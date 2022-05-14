doubleSAR = True
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
        self.value = value
    
    def fromDoubleInput(self, p2, move, value):
        if doubleSAR == False:
            print("calling double input??")
        self.timesUsed = 1
        self.p2 = p2
        self.move = move
        self.value = value

    def fromString(self, initStr):
        split = initStr.split(" ")
        self.timesUsed = int(split[0])
        if doubleSAR:
            self.p1 = split[1]
            self.p2 = split[2]
            self.move = split[3]
            self.value = float(split[-1])
        else:
            self.p2 = split[1]
            self.move = split[2]
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
            return str(self.timesUsed) + " " + self.p1 + " " + self.p2 + " " + self.move + " " + str(self.value)
        else:
            return str(self.timesUsed) + " " + self.p2 + " " + self.move + " " + str(self.value)

# IMPORTANT:
# if you run this file directly, the file paths will be slightly different than if they are run
# in script.
# set the below boolean to "True" to run this file directly, and set it to "False" otherwise.
runningDirectly = False

if __name__ == "__main__":
    if runningDirectly:
        path = "pokemon-showdown/"
    else:
        path = ""
    # Access the available moves
    with open(path + "availableMoves.txt") as f:
        rawMoves = f.readlines()
    # parse the moves into a list
    moves = ''.join(rawMoves).split(" ")
    if len(moves) == 0:
        print("no available moves!")
    else:
        del moves[-1]
        # Access the player and enemy pokemon
        with open(path + "learnerCurrentPokemon.txt") as f:
            currentPokemon = f.readlines()
        with open(path + "enemyCurrentPokemon.txt") as f:
            enemyPokemon = f.readlines()

        print(currentPokemon, "VS", enemyPokemon, "with", len(moves), "choices", moves)

        # retrieve the current SARs
        if runningDirectly:
            matchups = open("SAR.txt")
        else:
            print("opening indirectly")
            matchups = open("../SAR.txt")
        matchupValues = matchups.readlines()
        print(matchupValues)
        # turn these strings into SAR objects
        SARs = []
        for matchup in matchupValues:
            newSAR = SAR()
            print("making matchup from", matchup)
            newSAR.fromString(matchup)
            # print(newSAR.toString())
            SARs.append(newSAR)
        
        for aSAR in SARs:
            aSAR.toString()
        matchups.close()
        # create a SAR for each potential match
        playerSARs = []
        for move in moves:
            newSAR = SAR()
            newSAR.fromInput(enemyPokemon, move, 0)
            for aSAR in SARs:
                # check if this current SAR matches the situation we're in currently.
                if aSAR == newSAR:
                    # apply the value of the stored SAR to this SAR
                    print("match found!")
                    newSAR = aSAR
                    break
            # add the new SAR
            playerSARs.append(newSAR)

        bestIndex = 0
        bestValue = -999
        currIndex = 0
        for option in playerSARs:
            if option.value > bestValue:
                bestIndex = currIndex
                bestValue = option.value
            currIndex += 1
        print("best option is~", bestIndex, "with value", bestValue)