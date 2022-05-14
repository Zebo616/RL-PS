doubleSAR = True
printTeams = False

# Whether to print terminal output.
printTurnOutput = False

# Stores information about a Pokemon.
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

# IMPORTANT:
# if you run this file directly, the file paths will be slightly different than if they are run
# in script.
# set the below boolean to "True" to run this file directly, and set it to "False" otherwise.
runningDirectly = False

if __name__ == "__main__":
    if runningDirectly == False:
        path = "pokemon-showdown/"
    else:
        path = ""
    
    # get the teams
    with open(path + "genTeamP1.txt") as f:
        p1Team = f.readlines()[0]

    with open(path + "genTeamP2.txt") as f:
        p2Team = f.readlines()[0]
    
    with open("coverage.txt") as f:
        coverages = f.readlines()[0].split(" ")
        if printTurnOutput:
            print("coverages:", coverages)
    
    coverages[0] = int(coverages[0])
    coverages[1] = int(coverages[1])

    # parse the teams into different Pokemon
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

f = open("pokemon-showdown/p1Preferences.txt", "w")
f.write("")
f.close()

# initialize the matchup list
matchups = open("SAR.txt")
matchupValues = matchups.readlines()
matchups.close()
# print(matchupValues)
# turn these strings into SAR objects
SARs = []
for matchup in matchupValues:
    newSAR = SAR()
    # if printTurnOutput:
    #     print("making matchup from", matchup)
    newSAR.fromString(matchup)
    # print(newSAR.toString())
    SARs.append(newSAR)

f = open("pokemon-showdown/p1Preferences.txt", "a")
# For each one of p1's Pokemon, find the best move it can use against each of p2's pokemon
for playerPokemon in p1:
    for enemyPokemon in p2:
        playerChoices = []
        if printTurnOutput:
            print("player's moves:", playerPokemon.moves)
        for moveIndex in range(len(playerPokemon.moves)):
            # create a SAR representing this matchup
            if printTurnOutput:
                print("considering move", playerPokemon.moves[moveIndex])
            playerSAR = SAR()
            if doubleSAR:
                playerSAR.fromDoubleInput(playerPokemon.name, enemyPokemon.name, playerPokemon.moves[moveIndex], 0)
            else:
                playerSAR.fromSingleInput(enemyPokemon.name, playerPokemon.moves[moveIndex], 0)
            foundMove = False
            # check if this SAR matches any of the situations we've encountered before
            for aSAR in SARs:
                if playerSAR == aSAR:
                    if printTurnOutput:
                        print("found a match!")
                    if foundMove == False:
                        coverages[0] += 1
                        foundMove = True
                    playerSAR = aSAR
            # print(playerSAR.toString())
            if foundMove == False:
                coverages[1] += 1

            playerChoices.append(playerSAR)
            # print("finished with that...")
        # finally, find the move with highest expected reward and write the index to preferences
        # input()
        bestIndex = 0
        bestReward = -999999
        currIndex = 1
        for choice in playerChoices:
            if printTurnOutput:
                print("choice is:", choice.p1, " ", choice.p2)
            if choice.value > bestReward:
                if printTurnOutput:
                    print("choice", currIndex, "has a value of", choice.value)
                bestIndex = currIndex
                bestReward = choice.value
            currIndex += 1
        f.write(playerPokemon.name + " " + enemyPokemon.name + " " + str(bestIndex) + "\n")
f.close()
coverages[0] = str(coverages[0])
coverages[1] = str(coverages[1])
# write the updated coverage information
f = open("coverage.txt", "w")
if printTurnOutput:
    print("writing", coverages[0], coverages[1])
f.write(coverages[0] + " " + coverages[1])
