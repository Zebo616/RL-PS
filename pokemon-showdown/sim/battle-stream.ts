/**
 * Battle Stream
 * Pokemon Showdown - http://pokemonshowdown.com/
 *
 * Supports interacting with a PS battle in Stream format.
 *
 * This format is VERY NOT FINALIZED, please do not use it directly yet.
 *
 * @license MIT
 */

import {Streams, Utils} from '../lib';
import {Teams} from './teams';
import {Battle} from './battle';

/**
 * Like string.split(delimiter), but only recognizes the first `limit`
 * delimiters (default 1).
 *
 * `"1 2 3 4".split(" ", 2) => ["1", "2"]`
 *
 * `Utils.splitFirst("1 2 3 4", " ", 1) => ["1", "2 3 4"]`
 *
 * Returns an array of length exactly limit + 1.
 */
function splitFirst(str: string, delimiter: string, limit = 1) {
	const splitStr: string[] = [];
	while (splitStr.length < limit) {
		const delimiterIndex = str.indexOf(delimiter);
		if (delimiterIndex >= 0) {
			splitStr.push(str.slice(0, delimiterIndex));
			str = str.slice(delimiterIndex + delimiter.length);
		} else {
			splitStr.push(str);
			str = '';
		}
	}
	splitStr.push(str);
	return splitStr;
}

export class BattleStream extends Streams.ObjectReadWriteStream<string> {
	debug: boolean;
	noCatch: boolean;
	replay: boolean | 'spectator';
	keepAlive: boolean;
	battle: Battle | null;

	constructor(options: {
		debug?: boolean, noCatch?: boolean, keepAlive?: boolean, replay?: boolean | 'spectator',
	} = {}) {
		super();
		this.debug = !!options.debug;
		this.noCatch = !!options.noCatch;
		this.replay = options.replay || false;
		this.keepAlive = !!options.keepAlive;
		this.battle = null;
	}

	_write(chunk: string) {
		if (this.noCatch) {
			this._writeLines(chunk);
		} else {
			try {
				this._writeLines(chunk);
			} catch (err: any) {
				this.pushError(err, true);
				return;
			}
		}
		if (this.battle) this.battle.sendUpdates();
	}

	_writeLines(chunk: string) {
		for (const line of chunk.split('\n')) {
			if (line.startsWith('>')) {
				const [type, message] = splitFirst(line.slice(1), ' ');
				this._writeLine(type, message);
			}
		}
	}

	pushMessage(type: string, data: string) {
		if (this.replay) {
			if (type === 'update') {
				if (this.replay === 'spectator') {
					this.push(data.replace(/\n\|split\|p[1234]\n(?:[^\n]*)\n([^\n]*)/g, '\n$1'));
				} else {
					this.push(data.replace(/\n\|split\|p[1234]\n([^\n]*)\n(?:[^\n]*)/g, '\n$1'));
				}
			}
			return;
		}
		this.push(`${type}\n${data}`);
	}

	_writeLine(type: string, message: string) {
		switch (type) {
		case 'start':
			const options = JSON.parse(message);
			options.send = (t: string, data: any) => {
				if (Array.isArray(data)) data = data.join("\n");
				this.pushMessage(t, data);
				if (t === 'end' && !this.keepAlive) this.pushEnd();
			};
			if (this.debug) options.debug = true;
			this.battle = new Battle(options);
			break;
		case 'player':
			const [slot, optionsText] = splitFirst(message, ' ');
			this.battle!.setPlayer(slot as SideID, JSON.parse(optionsText));
			break;
		case 'p1':
		case 'p2':
		case 'p3':
		case 'p4':
			if (message === 'undo') {
				this.battle!.undoChoice(type);
			} else {
				this.battle!.choose(type, message);
			}
			break;
		case 'forcewin':
		case 'forcetie':
			this.battle!.win(type === 'forcewin' ? message as SideID : null);
			if (message) {
				this.battle!.inputLog.push(`>forcewin ${message}`);
			} else {
				this.battle!.inputLog.push(`>forcetie`);
			}
			break;
		case 'forcelose':
			this.battle!.lose(message as SideID);
			this.battle!.inputLog.push(`>forcelose ${message}`);
			break;
		case 'reseed':
			const seed = message ? message.split(',').map(Number) as PRNGSeed : null;
			this.battle!.resetRNG(seed);
			// could go inside resetRNG, but this makes using it in `eval` slightly less buggy
			this.battle!.inputLog.push(`>reseed ${this.battle!.prng.seed.join(',')}`);
			break;
		case 'tiebreak':
			this.battle!.tiebreak();
			break;
		case 'chat-inputlogonly':
			this.battle!.inputLog.push(`>chat ${message}`);
			break;
		case 'chat':
			this.battle!.inputLog.push(`>chat ${message}`);
			this.battle!.add('chat', `${message}`);
			break;
		case 'eval':
			const battle = this.battle!;

			// n.b. this will usually but not always work - if you eval code that also affects the inputLog,
			// replaying the inputlog would double-play the change.
			battle.inputLog.push(`>${type} ${message}`);

			message = message.replace(/\f/g, '\n');
			battle.add('', '>>> ' + message.replace(/\n/g, '\n||'));
			try {
				/* eslint-disable no-eval, @typescript-eslint/no-unused-vars */
				const p1 = battle.sides[0];
				const p2 = battle.sides[1];
				const p3 = battle.sides[2];
				const p4 = battle.sides[3];
				const p1active = p1?.active[0];
				const p2active = p2?.active[0];
				const p3active = p3?.active[0];
				const p4active = p4?.active[0];
				const toID = battle.toID;
				const player = (input: string) => {
					input = toID(input);
					if (/^p[1-9]$/.test(input)) return battle.sides[parseInt(input.slice(1)) - 1];
					if (/^[1-9]$/.test(input)) return battle.sides[parseInt(input) - 1];
					for (const side of battle.sides) {
						if (toID(side.name) === input) return side;
					}
					return null;
				};
				const pokemon = (side: string | Side, input: string) => {
					if (typeof side === 'string') side = player(side)!;

					input = toID(input);
					if (/^[1-9]$/.test(input)) return side.pokemon[parseInt(input) - 1];
					return side.pokemon.find(p => p.baseSpecies.id === input || p.species.id === input);
				};
				let result = eval(message);
				/* eslint-enable no-eval, @typescript-eslint/no-unused-vars */

				if (result?.then) {
					result.then((unwrappedResult: any) => {
						unwrappedResult = Utils.visualize(unwrappedResult);
						battle.add('', 'Promise -> ' + unwrappedResult);
						battle.sendUpdates();
					}, (error: Error) => {
						battle.add('', '<<< error: ' + error.message);
						battle.sendUpdates();
					});
				} else {
					result = Utils.visualize(result);
					result = result.replace(/\n/g, '\n||');
					battle.add('', '<<< ' + result);
				}
			} catch (e: any) {
				battle.add('', '<<< error: ' + e.message);
			}
			break;
		case 'requestlog':
			this.push(`requesteddata\n${this.battle!.inputLog.join('\n')}`);
			break;
		case 'requestteam':
			message = message.trim();
			const slotNum = parseInt(message.slice(1)) - 1;
			if (isNaN(slotNum) || slotNum < 0) {
				throw new Error(`Team requested for slot ${message}, but that slot does not exist.`);
			}
			const side = this.battle!.sides[slotNum];
			const team = Teams.pack(side.team);
			this.push(`requesteddata\n${team}`);
			break;
		case 'version':
		case 'version-origin':
			break;
		default:
			throw new Error(`Unrecognized command ">${type} ${message}"`);
		}
	}

	_writeEnd() {
		// if battle already ended, we don't need to pushEnd.
		if (!this.atEOF) this.pushEnd();
		this._destroy();
	}

	_destroy() {
		if (this.battle) this.battle.destroy();
	}
}

/**
 * Splits a BattleStream into omniscient, spectator, p1, p2, p3 and p4
 * streams, for ease of consumption.
 */
export function getPlayerStreams(stream: BattleStream) {
	const streams = {
		omniscient: new Streams.ObjectReadWriteStream({
			write(data: string) {
				void stream.write(data);
			},
			writeEnd() {
				return stream.writeEnd();
			},
		}),
		spectator: new Streams.ObjectReadStream<string>({
			read() {},
		}),
		p1: new Streams.ObjectReadWriteStream({
			write(data: string) {
				void stream.write(data.replace(/(^|\n)/g, `$1>p1 `));
			},
		}),
		p2: new Streams.ObjectReadWriteStream({
			write(data: string) {
				void stream.write(data.replace(/(^|\n)/g, `$1>p2 `));
			},
		}),
		p3: new Streams.ObjectReadWriteStream({
			write(data: string) {
				void stream.write(data.replace(/(^|\n)/g, `$1>p3 `));
			},
		}),
		p4: new Streams.ObjectReadWriteStream({
			write(data: string) {
				void stream.write(data.replace(/(^|\n)/g, `$1>p4 `));
			},
		}),
	};
	(async () => {
		for await (const chunk of stream) {
			const [type, data] = splitFirst(chunk, `\n`);
			switch (type) {
			case 'update':
				streams.omniscient.push(Battle.extractUpdateForSide(data, 'omniscient'));
				streams.spectator.push(Battle.extractUpdateForSide(data, 'spectator'));
				streams.p1.push(Battle.extractUpdateForSide(data, 'p1'));
				streams.p2.push(Battle.extractUpdateForSide(data, 'p2'));
				streams.p3.push(Battle.extractUpdateForSide(data, 'p3'));
				streams.p4.push(Battle.extractUpdateForSide(data, 'p4'));
				break;
			case 'sideupdate':
				const [side, sideData] = splitFirst(data, `\n`);
				streams[side as SideID].push(sideData);
				break;
			case 'end':
				// ignore
				break;
			}
		}
		for (const s of Object.values(streams)) {
			s.pushEnd();
		}
	})().catch(err => {
		for (const s of Object.values(streams)) {
			s.pushError(err, true);
		}
	});
	return streams;
}

export abstract class BattlePlayer {
	readonly stream: Streams.ObjectReadWriteStream<string>;
	readonly log: string[];
	readonly debug: boolean;
	p1p: string;
	p2p: string;
	preferences: string;

	constructor(playerStream: Streams.ObjectReadWriteStream<string>, debug = false) {
		this.stream = playerStream;
		this.log = [];
		this.debug = debug;
		this.p1p = "?";
		this.p2p = "?"
		this.preferences = "none";
	}

	async start() {
		for await (const chunk of this.stream) {
			this.receive(chunk);
		}
	}

	async specialStart(preferences: string) {
		this.preferences = preferences;
		// console.log("established player preferences.");
		for await (const chunk of this.stream) {
			this.receive(chunk);
		}
	}

	receive(chunk: string) {
		for (const line of chunk.split('\n')) {
			this.receiveLine(line);
		}
	}

	receiveLine(line: string) {
		if (this.debug) console.log(line);
		if (!line.startsWith('|')) return;
		// console.log("BATTLE PLAYER Received " + line);
		// Update the active pokemon of player one and player two
		if(line.includes("p1a: ")) {
			this.p1p = line.split("p1a: ")[1].split("|")[0];
		}
		if(line.includes("p2a: ")) {
			this.p2p = line.split("p2a: ")[1].split("|")[0];
		}
		const [cmd, rest] = splitFirst(line.slice(1), '|');
		if (cmd === 'request') {
			let JSONRest = JSON.parse(rest);
			// console.log("Rest before: " + JSONRest + " " + typeof JSONRest);
			// console.log("Player Name: ", JSONRest.side.name);
			if(JSONRest.side.name == "Reinforcement Doer" || JSONRest.side.name == "Reinforcement Adversary") {
				// give the request extra stuff
				return this.receiveCustomRequest(JSON.parse(rest), this.p1p, this.p2p);
			} else {
				// console.log("regular actor: '" + JSONRest.side.name + "'");
				// the learner doesn't need the extra stuff
				return this.receiveRequest(JSON.parse(rest));
			}
		}
		if (cmd === 'error') return this.receiveError(new Error(rest));
		this.log.push(line);
	}

	abstract receiveRequest(request: AnyObject): void;

	abstract receiveCustomRequest(request: AnyObject, p1p: string, p2p: string): void;

	receiveError(error: Error) {
		throw error;
	}

	choose(choice: string) {
		void this.stream.write(choice);
	}
}

export class BattleTextStream extends Streams.ReadWriteStream {
	readonly battleStream: BattleStream;
	currentMessage: string;

	constructor(options: {debug?: boolean}) {
		super();
		this.battleStream = new BattleStream(options);
		this.currentMessage = '';
		void this._listen();
	}

	async _listen() {
		for await (let message of this.battleStream) {
			if (!message.endsWith('\n')) message += '\n';
			this.push(message + '\n');
		}
		this.pushEnd();
	}

	_write(message: string | Buffer) {
		this.currentMessage += '' + message;
		const index = this.currentMessage.lastIndexOf('\n');
		if (index >= 0) {
			void this.battleStream.write(this.currentMessage.slice(0, index));
			this.currentMessage = this.currentMessage.slice(index + 1);
		}
	}

	_writeEnd() {
		return this.battleStream.writeEnd();
	}
}