/**
 * Example random player AI.
 *
 * Pokemon Showdown - http://pokemonshowdown.com/
 *
 * @license MIT
 */

import { convertCompilerOptionsFromJson, ImportsNotUsedAsValues } from 'typescript';
import {ObjectReadWriteStream} from '../../lib/streams';
import {BattlePlayer} from '../battle-stream';
import {Dex, toID} from '../dex';
import {PRNG, PRNGSeed} from '../prng';
import {PythonShell} from 'python-shell';
import { Integer } from 'better-sqlite3';
import { type } from 'os';

export class ReinforcementLearningAI extends BattlePlayer {
	protected readonly move: number;
	protected readonly mega: number;
	protected readonly prng: PRNG;

	constructor(
		playerStream: ObjectReadWriteStream<string>,
		options: {move?: number, mega?: number, seed?: PRNG | PRNGSeed | null } = {},
		debug = false
	) {
		super(playerStream, debug);
		this.move = options.move || 1.0;
		this.mega = options.mega || 0;
		this.prng = options.seed && !Array.isArray(options.seed) ? options.seed : new PRNG(options.seed);
	}

	receiveError(error: Error) {
		// If we made an unavailable choice we will receive a followup request to
		// allow us the opportunity to correct our decision.
		if (error.message.startsWith('[Unavailable choice]')) return;
		console.log("ERROR!")
		throw error;
	}

	async receiveRequest(request: AnyObject) {
		console.log("Request Received...")
		if (request.wait) {
			// wait request
			// do nothing
		} else if (request.forceSwitch) {
			// console.log("We need to switch.")
			// switch request
			const pokemon = request.side.pokemon;
			const chosen: number[] = [];
			const choices = await request.forceSwitch.map((mustSwitch: AnyObject) => {
				if (!mustSwitch) return `pass`;

				const canSwitch = range(1, 6).filter(i => (
					pokemon[i - 1] &&
					// not active
					i > request.forceSwitch.length &&
					// not chosen for a simultaneous switch
					!chosen.includes(i) &&
					// not fainted
					!pokemon[i - 1].condition.endsWith(` fnt`)
				));

				if (!canSwitch.length) return `pass`;
				const target = this.chooseSwitch(
					request.active,
					canSwitch.map(slot => ({slot, pokemon: pokemon[slot - 1]}))
				);
				chosen.push(target);
				return `switch ${target}`;
			});

			this.choose(choices.join(`, `));
		} else if (request.active) {
			let done = false
			console.log("Let's make a move!");
			// move request
			let [canMegaEvo, canUltraBurst, canZMove, canDynamax] = [true, true, true, true];
			const pokemon = request.side.pokemon;
			const chosen: number[] = [];

			let learnedChoice = new Promise(function(myResolve, myReject) {
				// "Producing Code" (May take some time)
				console.log("inside learnedChoice...");
				const choices = request.active.map((active: AnyObject, i: number) => {
					if (pokemon[i].condition.endsWith(` fnt`)) {done = true; return `pass`};
					console.log("inside choices...");
					canMegaEvo = canMegaEvo && active.canMegaEvo;
					canUltraBurst = canUltraBurst && active.canUltraBurst;
					canZMove = canZMove && !!active.canZMove;
					canDynamax = canDynamax && !!active.canDynamax;
	
					// Determine whether we should change form if we do end up switching
					const change = (canMegaEvo || canUltraBurst || canDynamax) && this.prng.next() < this.mega;
					// If we've already dynamaxed or if we're planning on potentially dynamaxing
					// we need to use the maxMoves instead of our regular moves
	
					const useMaxMoves = (!active.canDynamax && active.maxMoves) || (change && canDynamax);
					const possibleMoves = useMaxMoves ? active.maxMoves.maxMoves : active.moves;
	
					let canMove = range(1, possibleMoves.length).filter(j => (
						// not disabled
						!possibleMoves[j - 1].disabled
						// NOTE: we don't actually check for whether we have PP or not because the
						// simulator will mark the move as disabled if there is zero PP and there are
						// situations where we actually need to use a move with 0 PP (Gen 1 Wrap).
					)).map(j => ({
						slot: j,
						move: possibleMoves[j - 1].move,
						target: possibleMoves[j - 1].target,
						zMove: false,
					}));
					if (canZMove) {
						canMove.push(...range(1, active.canZMove.length)
							.filter(j => active.canZMove[j - 1])
							.map(j => ({
								slot: j,
								move: active.canZMove[j - 1].move,
								target: active.canZMove[j - 1].target,
								zMove: true,
							})));
					}
	
					// Filter out adjacentAlly moves if we have no allies left, unless they're our
					// only possible move options.
					const hasAlly = pokemon.length > 1 && !pokemon[i ^ 1].condition.endsWith(` fnt`);
					const filtered = canMove.filter(m => m.target !== `adjacentAlly` || hasAlly);
					canMove = filtered.length ? filtered : canMove;
					console.log("further down...");
					const moves = canMove.map(m => {
						let move = `move ${m.slot}`;
						// NOTE: We don't generate all possible targeting combinations.
						if (request.active.length > 1) {
							if ([`normal`, `any`, `adjacentFoe`].includes(m.target)) {
								move += ` ${1 + Math.floor(this.prng.next() * 2)}`;
							}
							if (m.target === `adjacentAlly`) {
								move += ` -${(i ^ 1) + 1}`;
							}
							if (m.target === `adjacentAllyOrSelf`) {
								if (hasAlly) {
									move += ` -${1 + Math.floor(this.prng.next() * 2)}`;
								} else {
									move += ` -${i + 1}`;
								}
							}
						}
						if (m.zMove) move += ` zmove`;
						// done = true;
						console.log("move?? " + move + " ? " + m);
						return {choice: move, move: m};
					});
					console.log("done compiling moves");
					const canSwitch = range(1, 6).filter(j => (
						pokemon[j - 1] &&
						// not active
						!pokemon[j - 1].active &&
						// not chosen for a simultaneous switch
						!chosen.includes(j) &&
						// not fainted
						!pokemon[j - 1].condition.endsWith(` fnt`)
					));
					const switches = active.trapped ? [] : canSwitch;
					console.log("compiled?");
					if (switches.length && (!moves.length || this.prng.next() > this.move)) {
						console.log("special case?");
						const target = this.chooseSwitch(
							active,
							canSwitch.map(slot => ({slot, pokemon: pokemon[slot - 1]}))
						);
						chosen.push(target);
						done = true;
						return `switch ${target}`;
					} else if (moves.length) {
						console.log("about to declare move...");
						let move = new Promise(function(myResolve, myReject) {
							// "Producing Code" (May take some time)
							this.chooseMove(request, active, moves);
							  myResolve(move); // when successful
							  myReject("error!");  // when error
							});
							
							// "Consuming Code" (Must wait for a fulfilled Promise)
							move.then(
							  function(value) { /* code if successful */ 
									  console.log("chose move " + move);
									  done = true;
									  return move;
								},
							  function(error) { /* code if some error */ }
							);
					} else {
						console.log("looks like an error??");
						done = true;
						throw new Error(`${this.constructor.name} unable to make choice ${i}. request='${request}',` +
							` chosen='${chosen}', (mega=${canMegaEvo}, ultra=${canUltraBurst}, zmove=${canZMove},` +
							` dynamax='${canDynamax}')`);
					}
					console.log("down here??");
				});

				  myResolve(choices); // when successful
				  myReject("oof...");  // when error
				});
				
			// "Consuming Code" (Must wait for a fulfilled Promise)
			learnedChoice.then(
				function(value: AnyObject) { /* code if successful */ 
				console.log("made the choice of " + value);
				console.log("umpa " + value.join(`, `));
				this.choose(value.join(`, `));
				done = true;
			
			},
				function(error) { /* code if some error */ }
			);
			function waitForIt(){
				if (done == false) {
					console.log("waiting...")
					setTimeout(function(){waitForIt()},1000);
				} else {
					// go do that thing
					console.log("done");
				};
			}
			waitForIt()
			console.log("rock bottom...");
		} else {
			// team preview?
			// console.log("...team preview?");
			this.choose(this.chooseTeamPreview(request.side.pokemon));
		}
	}

	protected chooseTeamPreview(team: AnyObject[]): string {
		return `default`;
	}

	protected async chooseMove(request: AnyObject, active: AnyObject, moves: {choice: string, move: AnyObject}[], choices): string {
		console.log("CHOOSING A MOVE")
		// If the only move we can use is mirror move, this will prevent an infinite loop
		if(moves.length == 1) {
			return "move 1";
		}
		// Send the current active pokemon as a .txt file to the decider
		let currentPokemon = request.side.pokemon[0].details;
		// console.log("this pokemon is: " + currentPokemon);
		const fs = require("fs");
		fs.writeFileSync("learnerCurrentPokemon.txt", currentPokemon, function(err){
			if(err){
			  return console.log("error");
			}
		})
		// compile all of the available moves
		let availableMoves: string = "";
		for (const {choice, move} of moves) {
			// console.log("move choice: " + choice);
			const id = toID(move.move);
			// console.log("move id: " + id);
			if(id != "Mirror Move") {
				availableMoves += id + " ";
			}
		}
		fs.writeFileSync("availableMoves.txt", availableMoves, function(err){
			if(err){
			  return console.log("error");
			}
		})
		var deciderPath = '../decide.py';
		console.log("shelling");
		let myPromise = new Promise(function(myResolve, myReject) {
			// "Producing Code" (May take some time)
			let move = PythonShell.run(deciderPath, null, function(
				err,
				results
			) {
				if (err) {
				console.log("uh oh");
				}
				// rest of your Code
				console.log("done?")
				// results is an array consisting of messages collected during execution
				console.log('results: %j', results);
				// console.log("asdf: " + (typeof results))
				console.log("results[-1]", results[results.length - 1]);
				let goodIndex = results[results.length - 1].indexOf("~");
				console.log("goodIndex is ", goodIndex);
				let greatIndex = results[results.length - 1].charAt(goodIndex + 2);
				console.log("decided on move " + greatIndex);
				// this.finishMoveChoice("move " + greatIndex);
			  myResolve("move " + move); // when successful
			  myReject("shell error");  // when error
			});
			
			// "Consuming Code" (Must wait for a fulfilled Promise)
			myPromise.then(
			  function(value) { return value },
			  function(error) { /* code if some error */ }
			);
		});
		console.log("learning?");
		// let moveChosen = this.prng.sample(moves).choice;
		// return moveChosen
	}
	protected chooseSwitch(active: AnyObject | undefined, switches: {slot: number, pokemon: AnyObject}[]): number {
		return this.prng.sample(switches).slot;
	}
}

// Creates an array of numbers progressing from start up to and including end
function range(start: number, end?: number, step = 1) {
	if (end === undefined) {
		end = start;
		start = 0;
	}
	const result = [];
	for (; start <= end; start += step) {
		result.push(start);
	}
	return result;
}
