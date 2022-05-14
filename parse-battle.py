# This file will take the initialized teams and battle log,
# then parse the battle log and glean SARSA tuples.

# You can set these to True for debugging purposes.

# Determines whether teams are printed at the start.
printTeams = False
# Determines if the turn-by-turn output is printed.
printTurnOutput = False

# Whether or not to actually update SAR.
updateSAR = False

# Whether SAR will store both the acting and defending pokemon, or just the defending pokemon.
doubleSAR = True

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

# a class we can use to store and act upon state-action values stored in SAR.txt.
# we don't store the pokemon using the move because it doesn't matter too much.
class SAR:
    def __init__(self):
        self.timesUsed = 0
        self.p1 = None
        self.p2 = None
        self.move = None
        self.value = None

    def fromSingleInput(self, p2, move, value):
        if doubleSAR:
            print("calling single input??")
        self.timesUsed = 1
        self.p2 = p2
        self.move = move
        # clean up the move name a bit, if necessary
        self.move = self.move.replace("-", "")
        self.move = self.move.lower()
        self.value = value
    
    def fromDoubleInput(self, p1, p2, move, value):
        if doubleSAR == False:
            print("calling double input??")
        self.timesUsed = 1
        self.p1 = p1
        self.p2 = p2
        self.move = move
        # clean up the move name a bit, if necessary
        self.move = self.move.replace("-", "")
        self.move = self.move.lower()
        self.value = value

    def fromString(self, initStr):
        split = initStr.split("|")
        self.timesUsed = int(split[0])
        if doubleSAR:
            self.p1 = split[1]
            self.p2 = split[2]
            self.move = split[3]
            # clean up the move name a bit, if necessary
            self.move = self.move.replace("-", "")
            self.move = self.move.lower()
            self.value = float(split[-1])
        else:
            self.p2 = split[1]
            self.move = split[2]
            # clean up the move name a bit, if necessary
            self.move = self.move.replace("-", "")
            self.move = self.move.lower()
            self.value = float(split[-1])

    # used to see if two SARs refer to the same entry
    def __eq__(self, other):
        if doubleSAR:
            return self.p1 == other.p1 and self.p2 == other.p2 and self.move == other.move
        else:
            return self.p2 == other.p2 and self.move == other.move

    def update(self, value):
        self.timesUsed = self.timesUsed + 1
        self.value = ((self.value * (self.timesUsed - 1)) + value) / self.timesUsed

    def toString(self):
        if doubleSAR:
            return str(self.timesUsed) + "|" + self.p1 + "|" + self.p2 + "|" + self.move + "|" + str(self.value)
        else:
            return str(self.timesUsed) + "|" + self.p2 + "|" + self.move + "|" + str(self.value)

# describes a single turn of battle for both players.
# player 1 can be accessed with "True", and player 2 with "False".
class BattleSAR:
    def __init__(self, initStr, p1p, p1h, p1mh, p2p, p2h, p2mh):
        # as we parese these should be set to either true or false by the end
        self.p1Fainted = None
        self.p2Fainted = None
        self.turnNumber = initStr.split("|")[0]
        # make sense of the turn output
        # first, let's figure out if anyone even moved this turn
        if printTurnOutput:
            print("INITSTR:", initStr)
            print("initial turn status:")
            print("p1's", p1p, "with", p1h, "/", p1mh, "HP")
            print("p2's", p2p, "with", p2h, "/", p2mh, "HP")
        self.p1Pokemon = p1p
        self.p2Pokemon = p2p
        movesThisTurn = initStr.split("|move|")
        # for move in movesThisTurn:
        #     print("a move occurred this turn:", move)
        if printTurnOutput:
            print("TOTAL MOVES THIS TURN:", (len(movesThisTurn) - 1))
        if len(movesThisTurn) == 1:
            if printTurnOutput:
                print("WOW! Nobody moved this turn.")
            self.p1DamageDealt = 0
            self.p2DamageDealt = 0
            self.p1MovedFirst = False
            self.p1Fainted = False
            self.p2Fainted = False
            self.p1MoveUsed = "NONE"
            self.p2MoveUsed = "NONE"
            self.p1DamageDealt = 0
            self.p1HPAfter = p1h
            self.p2DamageDealt = 0
            self.p2HPAfter = p2h
        else:
            # we know someone moved, so we need to figure out who moved first
            firstMover = movesThisTurn[1].split("a")[0].split("p")[1]
            if firstMover == "1":
                if printTurnOutput:
                    print("p1's", p1p, "moved first")
                self.p1MovedFirst = True
            elif firstMover == "2":
                if printTurnOutput:
                    print("p2's", p2p, "moved first")
                self.p1MovedFirst = False
            else:
                print("can't make sense of '", firstMover, "'")
                input()
            # now that we know who moved first, figure out the move used
            firstMoveUsed = movesThisTurn[1].split("|")[1]
            if self.p1MovedFirst:
                if printTurnOutput:
                    print(p1p, "used '", firstMoveUsed, "'")
                self.p1MoveUsed = firstMoveUsed
            else:
                if printTurnOutput:
                    print(p2p, "used '", firstMoveUsed, "'")
                self.p2MoveUsed = firstMoveUsed
            # figure out the damage dealt and calculate the fraction of HP drained as a result...
            # that is, if the move hit.
            if "|-damage" in movesThisTurn[1]:
                if printTurnOutput:
                    print("the move did damage")
                HPAfterAttack = movesThisTurn[1].split("|-damage")[1].split("|")[2].split("/")[0]
                if "fnt" in HPAfterAttack:
                    HPAfterAttack = HPAfterAttack.split(" ")[0]
                    if self.p1MovedFirst:
                        if printTurnOutput:
                            print("K.O. for p1")
                        self.p1Fainted = False
                        self.p2Fainted = True
                    else:
                        if printTurnOutput:
                            print("K.O. for p2")
                        self.p1Fainted = True
                        self.p2Fainted = False
                else:
                    if self.p1MovedFirst:
                        self.p2Fainted = False
                    else:
                        self.p1Fainted = False

            else:
                if printTurnOutput:
                    print("the move did no damage...")
                if self.p1MovedFirst:
                    HPAfterAttack = p2h
                    self.p2Fainted = False
                else:
                    HPAfterAttack = p1h
                    self.p1Fainted = False
            if self.p1MovedFirst:
                HPFractionLost = (int(p2h) - int(HPAfterAttack)) / int(p2mh)
                self.p1DamageDealt = HPFractionLost
                self.p2HPAfter = HPAfterAttack
            else:
                HPFractionLost = (int(p1h) - int(HPAfterAttack)) / int(p1mh)
                self.p2DamageDealt = HPFractionLost
                self.p1HPAfter = HPAfterAttack
            if printTurnOutput:
                print("enemy HP after the attack is '", HPAfterAttack,  "(", HPFractionLost, "of max HP )")
            # check if there was recoil from this attack
            if len(movesThisTurn[1].split("|-damage")) > 2:
                if printTurnOutput:
                    print("ouch! recoil")
                HPAfterAttack = movesThisTurn[1].split("|-damage")[2].split("|")[2].split("/")[0]
                if "fnt" in HPAfterAttack:
                    if printTurnOutput:
                        print("K.O. from recoil ;-;")
                    HPAfterAttack = HPAfterAttack.split(" ")[0]
                    if self.p1MovedFirst:
                        self.p1Fainted = True
                    else:
                        self.p2Fainted = True
            # do the same thing for the other move this turn, if there was one.
            if len(movesThisTurn) > 2:
                if printTurnOutput:
                    print("second move this turn...")
                    print(movesThisTurn[2])
                secondMoveUsed = movesThisTurn[2].split("|")[1]
                if self.p1MovedFirst:
                    if printTurnOutput:
                        print("p2's", p2p, "used '", secondMoveUsed, "'")
                    self.p2MoveUsed = secondMoveUsed
                else:
                    if printTurnOutput:
                        print(p1p, "used '", secondMoveUsed, "'")
                    self.p1MoveUsed = secondMoveUsed
                if "|-damage" in movesThisTurn[2]:
                    if printTurnOutput:
                        print("the move did damage")
                    HPAfterAttack = movesThisTurn[2].split("|-damage")[1].split("|")[2].split("/")[0]
                    if "fnt" in HPAfterAttack:
                        HPAfterAttack = HPAfterAttack.split(" ")[0]
                        if self.p1MovedFirst:
                            if printTurnOutput:
                                print("K.O. for p2")
                            self.p1Fainted = True
                            self.p2Fainted = False
                        else:
                            if printTurnOutput:
                                print("K.O. for p1")
                            self.p1Fainted = False
                            self.p2Fainted = True
                    else:
                        if self.p1MovedFirst:
                            self.p1Fainted = False
                        else:
                            self.p2Fainted = False
                else:
                    if printTurnOutput:
                        print("the move did no damage...")
                    if self.p1MovedFirst:
                        HPAfterAttack = p1h
                        self.p1Fainted = False
                    else:
                        HPAfterAttack = p2h
                        self.p2Fainted = False
                if self.p1MovedFirst:
                    HPFractionLost = (int(p1h) - int(HPAfterAttack)) / int(p1mh)
                    self.p2DamageDealt = HPFractionLost
                    self.p1HPAfter = HPAfterAttack
                else:
                    HPFractionLost = (int(p2h) - int(HPAfterAttack)) / int(p2mh)
                    self.p1DamageDealt = HPFractionLost
                    self.p2HPAfter = HPAfterAttack
                if printTurnOutput:
                    print("enemy HP after the attack is '", HPAfterAttack,  "(", HPFractionLost, "of max HP )")
                # check if there was recoil from this attack
                if len(movesThisTurn[2].split("|-damage")) > 2:
                    if printTurnOutput:
                        print("ouch! recoil")
                    HPAfterAttack = movesThisTurn[2].split("|-damage")[2].split("|")[2].split("/")[0]
                    if "fnt" in HPAfterAttack:
                        if printTurnOutput:
                            print("K.O. from recoil ;-;")
                        HPAfterAttack = HPAfterAttack.split(" ")[0]
                        if self.p1MovedFirst:
                            self.p2Fainted = True
                        else:
                            self.p1Fainted = True
            else:
                if printTurnOutput:
                    print("only one move this turn.")
                if self.p1MovedFirst:
                    self.p2DamageDealt = 0
                    self.p2MoveUsed = "NONE"
                    self.p1HPAfter = p1h
                    if self.p1Fainted is None:
                        self.p1Fainted = False
                else:
                    self.p1DamageDealt = 0
                    self.p1MoveUsed = "NONE"
                    self.p2HPAfter = p2h
                    if self.p2Fainted is None:
                        self.p2Fainted = False

        # do a final check for pokemon that have fainted due to other factors, like confusion
        # or using a move that kills them
        faints = initStr.split("|faint|")
        if len(faints) > 0:
            faints = faints[1:]
            if printTurnOutput:
                print("faints this turn: ", faints)
            for faint in faints:
                playerFainted = faint.split("a")[0].split("p")[1]
                if playerFainted == "1":
                    if printTurnOutput:
                        print("player 1 fainted")
                    self.p1Fainted = True
                elif playerFainted == "2":
                    if printTurnOutput:
                        print("player 2 fainted")
                    self.p2Fainted = True
                else:
                    print("Cant' make sense of fainted player '", playerFainted, "'")
                    input()
        if self.p1MoveUsed == "Explosion" or self.p1MoveUsed == "Self-Destruct":
            if printTurnOutput:
                print("p1 fainted from suicide move!")
                # input()
            self.p1Fainted = True
        if self.p2MoveUsed == "Explosion" or self.p2MoveUsed == "Self-Destruct":
            if printTurnOutput:
                print("p2 fainted from suicide move!")
                # input()
            self.p2Fainted = True

        # regardless of moves used, calculate net reward for both p1 and p2
        self.p1Reward = self.p1DamageDealt - self.p2DamageDealt
        self.p2Reward = self.p2DamageDealt - self.p1DamageDealt
        if self.p1Fainted:
            self.p1Reward -= 1
            self.p2Reward += 1
            if printTurnOutput:
                print("rewards adjusted because p1 fainted")
        if self.p2Fainted:
            self.p1Reward += 1
            self.p2Reward -= 1
            if printTurnOutput:
                print("rewards adjusted because p2 fainted")
        if printTurnOutput:
            print("p1's reward:", self.p1Reward)
            print("p2's reward:", self.p2Reward)

        if self.p1Fainted == None or self.p2Fainted == None:
            print("ERROR: didn't set p1Fainted or p2Fainted:", self.p1Fainted, " ", self.p2Fainted)
            print(p1p, "vs", p2p)
            print("")
            input()

        # if someone fainted, set their new pokemon
        if self.p1Fainted or self.p2Fainted:
            # get the switched out pokemon name and HP
            if printTurnOutput:
                print("someone fainted!")
            if len(initStr.split("win|")) > 1:
                # someone's won, so the knocked out pokemon was the last one!
                if printTurnOutput:
                    print("the battle is over!")
                self.newp1p = None
                self.newp1pHP = None
                self.newp1pMaxHP = None
                self.newp2p = None
                self.newp2pHP = None
                self.newp2pMaxHP = None
                with open("Tally.txt") as f:
                    wins = f.readlines()[0].split(" ")
                if printTurnOutput:
                    print("current wins:", wins)
                if initStr.split("win|")[1] == "Reinforcement Doer":
                    self.p1Fainted = False
                    if printTurnOutput:
                        print("RL wins!")
                    wins[0] = str(float(wins[0]) + 1)
                    self.winningPlayer = 1
                else:
                    self.p2Fainted = False
                    if printTurnOutput:
                        print("random wins...")
                    wins[1] = str(float(wins[1]) + 1)
                    self.winningPlayer = 2
                f = open("Tally.txt", "w")
                f.write(wins[0] + " " + wins[1])
            elif len(initStr.split("tie")) > 1:
                # someone's won, so the knocked out pokemon was the last one!
                print("a tie?!?")
                self.newp1p = None
                self.newp1pHP = None
                self.newp1pMaxHP = None
                self.newp2p = None
                self.newp2pHP = None
                self.newp2pMaxHP = None
                with open("Tally.txt") as f:
                    wins = f.readlines()[0].split(" ")
                if printTurnOutput:
                    print("current wins:", wins)
                wins[0] = str(float(wins[0]) + .5)
                wins[1] = str(float(wins[1]) + .5)
                self.winningPlayer = -1
                f = open("Tally.txt", "w")
                f.write(wins[0] + " " + wins[1])
            else:
                self.winningPlayer = -1
                switches = initStr.split("switch")
                switchStr = initStr.split("switch")[1]
                switchedToPokemon = switchStr.split(":")[1][1:].split("|")[1].split(",")[0]
                switchedToHP = switchStr.split("|")[3].split("/")[0]
                switchedToMaxHP = switchStr.split("|")[3].split("/")[1]
                if len(switches) > 2:
                    if printTurnOutput:
                        print("BOTH PLAYERS ARE SWITCHING!")
                    # both active pokemon fainted!?! bruh moment
                    # there should be two switch statements, so set them based on who moved first
                    firstSwitchedToPokemon = switchStr.split(":")[1][1:].split("|")[1].split(",")[0]
                    firstSwitchedToHP = switchStr.split("|")[3].split("/")[0]
                    firstSwitchedToMaxHP = switchStr.split("|")[3].split("/")[1]
                    secondSwitchedToPokemon = switches[2].split(":")[1][1:].split("|")[1].split(",")[0]
                    secondSwitchedToHP = switches[2].split("|")[3].split("/")[0]
                    secondSwitchedToMaxHP = switches[2].split("|")[3].split("/")[1]
                    firstPlayerSwitch = switchStr.split("a")[0].split("p")[1]
                    firstPlayerSwitch = switchStr.split("a")[0].split("p")[1]
                    if printTurnOutput:
                        print("the first player to switch is", firstPlayerSwitch)
                    if firstPlayerSwitch == "1":
                        # playerOne switched first
                        if printTurnOutput:
                            print("p1 switches first")
                            print("p1 switching into", firstSwitchedToPokemon)
                            print("p2 switching into", secondSwitchedToPokemon)
                        self.newp1p = firstSwitchedToPokemon
                        self.newp1pHP = firstSwitchedToHP
                        self.newp1pMaxHP = firstSwitchedToMaxHP
                        self.newp2p = secondSwitchedToPokemon
                        self.newp2pHP = secondSwitchedToHP
                        self.newp2pMaxHP = secondSwitchedToMaxHP
                    elif firstPlayerSwitch == "2":
                        # playerTwo switched first
                        if printTurnOutput:
                            print("p2 switches first")
                            print("p2 switching into", firstSwitchedToPokemon)
                            print("p1 switching into", secondSwitchedToPokemon)
                        self.newp1p = secondSwitchedToPokemon
                        self.newp1pHP = secondSwitchedToHP
                        self.newp1pMaxHP = secondSwitchedToMaxHP
                        self.newp2p = firstSwitchedToPokemon
                        self.newp2pHP = firstSwitchedToHP
                        self.newp2pMaxHP = firstSwitchedToMaxHP
                    else:
                        print("uhh idk who's switching first", firstPlayerSwitch)
                        input()
                    if printTurnOutput:
                        print("p1 set to", self.newp1p)
                        print("p2 set to", self.newp2p)
                else:
                    if self.p1Fainted:
                        if printTurnOutput:
                            print("p1 switching into", switchedToPokemon)
                        self.newp1p = switchedToPokemon
                        self.newp1pHP = switchedToHP
                        self.newp1pMaxHP = switchedToMaxHP
                    else:
                        self.newp1p = p1p
                        self.newp1pHP = self.p1HPAfter
                        self.newp1pMaxHP = p1mh
                    if self.p2Fainted:
                        if printTurnOutput:
                            print("p2 switching into", switchedToPokemon)
                        self.newp2p = switchedToPokemon
                        self.newp2pHP = switchedToHP
                        self.newp2pMaxHP = switchedToMaxHP
                    else:
                        self.newp2p = p2p
                        self.newp2pHP = self.p2HPAfter
                        self.newp2pMaxHP = p2mh

        else:
            self.winningPlayer = -1
            if printTurnOutput:
                print("nobody fainted this turn :)")
            self.newp1p = p1p
            self.newp1pHP = self.p1HPAfter
            self.newp1pMaxHP = p1mh
            self.newp2p = p2p
            self.newp2pHP = self.p2HPAfter
            self.newp2pMaxHP = p2mh
        
        # replace spaces in move names with dashes
        self.p1MoveUsed = self.p1MoveUsed.replace(" ", "-")
        self.p2MoveUsed = self.p2MoveUsed.replace(" ", "-")
        # print("self.p1MoveUsed: '", self.p1MoveUsed, "'")
        # print("self.p2MoveUsed: '", self.p2MoveUsed, "'")
    
    def toString(self):
        # print("BattleSAR toString")
        print("Turn", self.turnNumber)
        if self.p1MovedFirst:
            print("p1's", self.p1Pokemon, "used", self.p1MoveUsed, ", dealing", (self.p1DamageDealt * 100), "%")
            print("p2's", self.p2Pokemon, "used", self.p2MoveUsed, ", dealing", (self.p2DamageDealt * 100), "%")
        else:
            print("p2's", self.p2Pokemon, "used", self.p2MoveUsed, ", dealing", (self.p2DamageDealt * 100), "%")
            print("p1's", self.p1Pokemon, "used", self.p1MoveUsed, ", dealing", (self.p1DamageDealt * 100), "%")
        print("net p1 reward:", (self.p1Reward - self.p2Reward))
        print("net p2 reward:", (self.p2Reward - self.p1Reward))


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
        if printTurnOutput:
            print(initPokemon)
        self.firstP1Pokemon = initPokemon.split("switch")[1].split(":")[1][1:].split("|")[0]
        self.firstP1HP = initPokemon.split("switch")[1].split("/")[1].split("\n")[0]
        self.firstP2Pokemon = initPokemon.split("switch")[2].split(":")[1][1:].split("|")[0]
        self.firstP2HP = initPokemon.split("switch")[2].split("/")[1].split("\n")[0]
        if printTurnOutput:
            print("player 1's initial pokemon is:", self.firstP1Pokemon, "with HP = '", self.firstP1HP, "'")
            print("player 2's initial pokemon is:", self.firstP2Pokemon, "with HP = '", self.firstP2HP, "'")
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
            # print("PARSING TURN", turn)
            SAR = BattleSAR(turn, previousP1Pokemon, previousP1HP, previousP1MaxHP, \
            previousP2Pokemon, previousP2HP, previousP2MaxHP)
            self.turnList.append(SAR)
                # self.newp2p = switchedToPokemon
                # self.newp2pHP = switchedToHP
                # self.newp2pMaxHP = switchedToMaxHP
                # self.newp1p = p1p
                # self.newp1pHP = self.p1HPAfter
                # self.newp1pMaxHP = p1mh
            # Update variables
            previousP1Pokemon = SAR.newp1p
            previousP1HP = SAR.newp1pHP
            previousP1MaxHP = SAR.newp1pMaxHP
            previousP2Pokemon = SAR.newp2p
            previousP2HP = SAR.newp2pHP
            previousP2MaxHP = SAR.newp2pMaxHP
            # SAR.toString()
            # input()
    
    # updates "SAR.txt" to include updated state-action values.
    def updateMatchupValues(self):
        if updateSAR:
            # initialize the matchup list
            matchups = open("SAR.txt")
            matchupValues = matchups.readlines()
            matchups.close()
            # print(matchupValues)
            # turn these strings into SAR objects
            SARs = []
            for matchup in matchupValues:
                newSAR = SAR()
                if printTurnOutput:
                    print("making matchup from", matchup)
                newSAR.fromString(matchup)
                # print(newSAR.toString())
                SARs.append(newSAR)

            for turn in self.turnList:
                # initialize SARs for this turn
                turnSAR1 = SAR()
                if doubleSAR:
                    turnSAR1.fromDoubleInput(turn.p1Pokemon, turn.p2Pokemon, turn.p1MoveUsed, (turn.p1Reward))
                else:
                    turnSAR1.fromSingleInput(turn.p2Pokemon, turn.p1MoveUsed, (turn.p1Reward))
                turnSAR2 = SAR()
                if doubleSAR:
                    turnSAR2.fromDoubleInput(turn.p2Pokemon, turn.p1Pokemon, turn.p2MoveUsed, (turn.p2Reward))
                else:
                    turnSAR2.fromSingleInput(turn.p1Pokemon, turn.p2MoveUsed, (turn.p2Reward))
                found1 = False
                found2 = False
                # do a lookup for these SARs in SARs
                for aSAR in SARs:
                    if aSAR == turnSAR1:
                        if found1 == False:
                            # update this SAR with the new move info
                            aSAR.update(turnSAR1.value)
                            found1 = True
                        else:
                            print("duplicate entries!", aSAR.toString())
                    if aSAR == turnSAR2:
                        # update this SAR with the new move info
                        if found2 == False:
                            # update this SAR with the new move info
                            aSAR.update(turnSAR2.value)
                            found2 = True
                        else:
                            print("duplicate entries!", aSAR.toString())
                # check if we'll need to make new entries
                if found1 == False:
                    # make a new entry for SAR1
                    SARs.append(turnSAR1)
                if found2 == False:
                    # make a new entry for SAR2
                    SARs.append(turnSAR2)
            
            # put the new SAR entries into SAR.txt
            os.remove("SAR.txt")
            f = open("SAR.txt", "a")
            for newSAR in SARs:
                f.write(newSAR.toString() + "\n")
            
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

    parser.updateMatchupValues()

    # if printTurnOutput:
    #     parser.toString()