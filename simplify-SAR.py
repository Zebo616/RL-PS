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

# A SAR that only takes into account the move, times used, and value.
# This is mostly used for debug purposes.
class MoveSAR:
    def __init__(self):
        self.timesUsed = 0
        self.move = None
        self.value = None

    def fromInput(self, timesUsed, move, value):
        self.timesUsed = timesUsed
        self.move = move
        # clean up the move name a bit, if necessary
        self.move = self.move.replace("-", "")
        self.move = self.move.lower()
        self.value = value

    # used to see if two SARs refer to the same entry
    def __eq__(self, other):
        return self.move == other.move

    def update(self, value):
        self.timesUsed = self.timesUsed + 1
        self.value = ((self.value * (self.timesUsed - 1)) + value) / self.timesUsed

    # used to merge two occurences of the same move.
    def merge(self, additionalOccurences, averageValue):
        previousTotalValue = self.value * self.timesUsed
        additionalValue = averageValue * additionalOccurences
        self.timesUsed += additionalOccurences
        self.value = (previousTotalValue + additionalValue) / self.timesUsed

    def toString(self):
        return str(self.timesUsed) + "|" + self.move + "|" + str(self.value)

file = "V2FullDouble/"

if __name__ == "__main__":
    # initialize the matchup list
    matchups = open(file + "SAR.txt")
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

    # clear the previous entries
    f = open(file + "simplifiedSAR.txt", "w")
    f.write("")
    f.close()

    visitedMoves = []
    f = open(file + "simplifiedSAR.txt", "a")
    # for every move that occurs in the SARs, find every occurence of that move
    # and find the actual average value
    for i in range(len(SARs)):
        # see if we've seen this move before
        seen = False
        for seenEntry in visitedMoves:
            if seenEntry.move == SARs[i].move:
                seen = True
                break
        if seen:
            # we've seen this move before, so do nothing
            pass
        else:
            totalSAR = MoveSAR()
            totalSAR.fromInput(SARs[i].timesUsed, SARs[i].move, SARs[i].value)
            print("found new move", totalSAR.move, "from", SARs[i].move)
            # we haven't seen this move before, so tally up every occurence of this move
            for j in range(i + 1, len(SARs)):
                # print("comparing to move", SARs[j].toString())
                if totalSAR.move == SARs[j].move:
                    # print("merging occurences of", totalSAR.move, "and", SARs[j].move)
                    # merge these occurences
                    totalSAR.merge(SARs[j].timesUsed, SARs[j].value)
            # write this move to the output file
            visitedMoves.append(totalSAR)
    
    # sort the entries
    visitedMoves.sort(key=lambda x: x.value, reverse=True)

    # write the entries to the file
    for entry in visitedMoves:
        f.write(entry.toString() + "\n")

