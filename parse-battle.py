# This file will take the initialized teams and battle log,
# then parse the battle log and glean SARSA tuples.

# You can set these to True for debugging purposes.

# Determines whether teams are printed at the start.
printTeams = False
# Determines if the turn-by-turn output is printed.
printTurnOutput = True

import os, sys, subprocess

# A class that parses and stores attributes of a Generation 1 competitve pokemon.
# Since we can assume generation one, we can ignore EVs, IVs, abilities, and held items.
# This allows us to greatly simplify the model which we train in.
class Gen1Pokemon:
    def __init__(self, initStr):
        self.name = initStr.split("|||")[0]
        self.level = initStr.split("|")[-2]
        self.moves = initStr.split("||")[1].split("|")[2].split(",")
    
    def toString(self):
        # print("Pokemon toString")
        print("Name: ", self.name)
        print("Level: ", self.level)
        print("Moves: ", self.moves)
        print("")

# describes a single turn of battle for both players.
# player 1 can be accessed with "True", and player 2 with "False".
class BattleSAR:
    def __init__(self, initStr, p1p, p1h, p1mh, p2p, p2h, p2mh):
        self.turnNumber = initStr.split("|")[0]
        # make sense of the turn output
        # first, let's figure out who moved first
        print("initial turn status:")
        print(p1p, "with", p1h, "/", p1mh, "HP")
        print(p2p, "with", p2h, "/", p2mh, "HP")
        firstMover = initStr.split("move")[1].split(" ")[1].split("|")[0]
        if firstMover == p1p:
            print(p1p, "moved first")
            self.p1MovedFirst = True
        elif firstMover == p2p:
            print(p2p, "moved first")
            self.p1MovedFirst = False
        else:
            print("can't make sense of", firstMover)
            input()
        # now that we know who moved first, figure out the move used
        firstMoveUsed = initStr.split("move")[1].split("|")[2]
        if self.p1MovedFirst:
            print(p1p, "used", firstMoveUsed, "'")
        else:
            print(p2p, "used '", firstMoveUsed, "'")
        # figure out the damage dealt and calculate the fraction of HP drained as a result...
        # that is, if the move hit.
        if "miss" in initStr.split("move")[1]:
            print("the attack missed!")
            if self.p1MovedFirst:
                HPAfterAttack = p2h
            else:
                HPAfterAttack = p1h
        else:
            HPAfterAttack = initStr.split("damage")[1].split("|")[2].split("/")[0]
            print("enemy HP after the attack is '", HPAfterAttack, "'")
            HPFractionLost
    
    def toString(self):
        # print("BattleSAR toString")
        print("Turn", self.turnNumber)


# A class that can read the battle log generated.
# Reference battleOutput for the specific format of the output generated.
# This class will be used to store the sequential states encountered in the battle,
# as well as the actions taken and the reward.
class BattleParser:
    def __init__(self, initStr):
        # initialize the turn list
        self.turnList = []
        # get the initial pokemon sent out
        initPokemon = initStr.split("|turn|")[0].split("start")[1]
        print(initPokemon)
        self.firstP1Pokemon = initPokemon.split("switch")[1].split(" ")[1].split("|")[0]
        self.firstP1HP = initPokemon.split("switch")[1].split("/")[1].split("\n")[0]
        self.firstP2Pokemon = initPokemon.split("switch")[2].split(" ")[1].split("|")[0]
        self.firstP2HP = initPokemon.split("switch")[2].split("/")[1].split("\n")[0]
        print("player 1's initial pokemon is:", self.firstP1Pokemon, "with HP ='", self.firstP1HP, "'")
        print("player 2's initial pokemon is:", self.firstP2Pokemon, "with HP ='", self.firstP2HP, "'")
        # initialize each turn as a BattleSAR object
        battleOutputTurns = initStr.split("|turn|")
        del battleOutputTurns[0]
        previousP1Pokemon = self.firstP1Pokemon
        previousP1HP = self.firstP1HP
        previousP1MaxHP = self.firstP1HP
        previousP2Pokemon = self.firstP2Pokemon
        previousP2HP = self.firstP2HP
        previousP2MaxHP = self.firstP2HP
        for turn in battleOutputTurns:
            print(turn)
            SAR = BattleSAR(turn, previousP1Pokemon, previousP1HP, previousP1MaxHP, \
            previousP2Pokemon, previousP2HP, previousP2MaxHP)
            self.turnList.append(SAR)
    
    def toString(self):
        print("BattleParser toString")
        for turn in self.turnList:
            turn.toString()

if __name__ == "__main__":
    # access the teams
    with open("pokemon-showdown/genTeamP1.txt") as f:
        p1Team = f.readlines()[0]
    with open("pokemon-showdown/genTeamP2.txt") as f:
        p2Team = f.readlines()[0]
    # print("p1's team is: ", p1Team)
    # print("p2's team is: ", p2Team)
    # print("Here's the battle output: ", battleOutput)

    # convert the raw strings into lists.
    p1Pokemon = p1Team.split("]")
    p2Pokemon = p2Team.split("]")

    p1 = []
    p2 = []

    # convert each pokemon on each team into a Gen1Pokemon object.
    for pokemon in p1Pokemon:
        # print("parsing ", pokemon)
        newPokemon = Gen1Pokemon(pokemon)
        p1.append(newPokemon)
    
    for pokemon in p2Pokemon:
        # print("parsing ", pokemon)
        newPokemon = Gen1Pokemon(pokemon)
        p2.append(newPokemon)
    
    if printTeams:
        print("Player one's team:")
        for pokemon in p1:
            pokemon.toString()

        print("Player two's team:")
        for pokemon in p2:
            pokemon.toString()

    # access the battle log
    with open("pokemon-showdown/battleOutput.txt") as f:
        battleOutput = ''.join(f.readlines())

    # split up the battle output into turns
    parser = BattleParser(battleOutput)

    if printTurnOutput:
        parser.toString()