/**
 * Battle Stream Example
 * Pokemon Showdown - http://pokemonshowdown.com/
 *
 * Example of how to create AIs battling against each other.
 * Run this using `node build && node .sim-dist/examples/run-battle`.
 *
 * @license MIT
 * @author Guangcong Luo <guangcongluo@gmail.com>
 */

import {BattleStream, getPlayerStreams, Teams} from '..';
import {RandomPlayerAI} from '../tools/random-player-ai';
import {ReinforcementLearningAI} from '../tools/applied-reinforcement-learning-ai';
import { readFileSync, writeFileSync, appendFileSync } from 'fs';

/*********************************************************************
 * Run AI
 *********************************************************************/

const streams = getPlayerStreams(new BattleStream());
const team1 = readFileSync('./genTeamP1.txt', 'utf-8');
const team2 = readFileSync('./genTeamP2.txt', 'utf-8');

const spec = {
	formatid: "gen1randombattle",
};
const p1spec = {
	name: "Reinforcement Doer",
	team: team1,
};
const p2spec = {
	name: "Random Actor",
	team: team2,
};

const p1 = new ReinforcementLearningAI(streams.p1);
const p2 = new RandomPlayerAI(streams.p2);

// console.log("p1 is " + p1.constructor.name);
// console.log("p2 is " + p2.constructor.name);
const fs = require("fs");
fs.readFile('p1Preferences.txt', 'utf8', (err, data) => {
	if (err) {
	  console.error(err);
	  return;
	}
	if(p1spec.name == "Reinforcement Doer") {
		void p1.specialStart(data);
	} else {
		void p1.start();
	}
	void p2.start();
  });

// override the log file from a previous run
writeFileSync('./battleOutput.txt', "");

void (async () => {
	for await (const chunk of streams.omniscient) {
		// console.log(chunk);
		appendFileSync('./battleOutput.txt', chunk);
	}
})();

void streams.omniscient.write(`>start ${JSON.stringify(spec)}
>player p1 ${JSON.stringify(p1spec)}
>player p2 ${JSON.stringify(p2spec)}`);
