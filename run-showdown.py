# Here we will attempt to run a Pokemon battle using the command line API.
# There are a number of advantages to this appraoch; for one, we can 
#   easily simulate battles as a "black box" and simply take 
#   into account the logged feedback afterwards.
# Additionally, Python is full of useful ML libraries that will greatly
#   increase the scope of what we can do in this project.

import os, sys, subprocess, time

if __name__ == "__main__":
    start = time.time()
    # Use this string to easily access the pokemon-showdown directory when executing commands.
    # Keep in mind the directory will reset after each os.system() call.
    sDir = "cd pokemon-showdown && "
    # Quick reference for running pokemon-showdown related commands.
    # A list of useful ones can be found here:
    # https://github.com/smogon/pokemon-showdown/blob/master/COMMANDLINE.md
    sNode = "node pokemon-showdown "

    # booleans that determine whether we clear persistent data from each run of this file.
    clearWinTally = True
    clearSARs = False
    clearCoverage = True
    clearTimer = True

    # set this to true if we're training.
    training = False

    # set this to true if two RL AI are battling.
    adversary = True

    # set this to true if you'd like to use a time limit on training.
    useTimeLimit = False
    # if the above is true, this is the time limit.
    timeLimit = 16525.014806747437

    # set to true if you'd like for the learning to stop after each round (often for debugging purposes).
    roundBreak = False

    # set to true if you'd like to see some more thorough output.
    printVerbose = False

    print("Building...")

    # Build the showdown project
    os.system(sDir + "node build")

    # clear the win tally, if that's what we want.
    if clearWinTally:
        print("clearing win tally...")
        f = open("Tally.txt", "w")
        f.write("0 0")
    
    # clear the existing SARs, if that's what we want.
    if clearSARs:
        print("clearing p1 SARs...")
        f = open("SAR.txt", "w")
        f.write("")

    # clear the existing coverage counts, if that's what we want.
    if clearCoverage:
        print("clearing coverage...")
        f = open("coverage.txt", "w")
        f.write("0 0")
        f = open("adversaryCoverage.txt", "w")
        f.write("0 0")
    # clear the existing timer, if that's what we want.
    if clearTimer:
        print("clearing timer...")
        f = open("time.txt", "w")
        f.write("")

    print("Finished building")

    if training:
        rounds = 5
    else:
        rounds = 1

    # set SYSOUT to be a file we can easily read.
    # sys.stdout = open("run-showdown-output", "w")
    for i in range(1000):
        curr = time.time()
        if useTimeLimit and ((curr - start) > timeLimit):
            print("time is up!")
            break
        print("ITERATION", (i + 1))
        print("time elapsed: ", curr - start)
        f = open("time.txt", "a")
        f.write(str(curr - start) + "\n")

        if printVerbose:
            print("Generating teams...")
        # Generate random generation 1 teams
        os.system(sDir + sNode + "generate-team gen1randombattle > genTeamP1.txt")
        os.system(sDir + sNode + "generate-team gen1randombattle > genTeamP2.txt")
        if printVerbose:
            print("Teams generated.")
            # print("p1's team is: ", p1Team)
            # print("p2's team is: ", p2Team)

        for j in range(rounds):
            curr = time.time()
            if useTimeLimit and ((curr - start) > timeLimit):
                print("Time is up!")
                break
            print("ROUND", (j + 1), "of iteration", (i + 1))
            # access the teams
            with open("pokemon-showdown/genTeamP1.txt") as f:
                p1Team = f.readlines()

            with open("pokemon-showdown/genTeamP2.txt") as f:
                p2Team = f.readlines()

            # members = 0
            # for member in p1Team.split("]"):
            #     members += 1
            #     print("member of team 1: " + member)
            # print("total members: ", members)

            # precompute the best available moves to use
            if printVerbose:
                print("precomputing best actions...")
            os.system("python3 precompute.py")
            os.system("python3 adversary-precompute.py")
            # simulate a battle with the generated teams
            if printVerbose:
                print("Starting battle...")
            if training:
                os.system(sDir + "node .sim-dist/examples/run-learning-battle")
            elif adversary:
                os.system(sDir + "node .sim-dist/examples/run-adversary-battle")
            else:
                os.system(sDir + "node .sim-dist/examples/run-battle")
            # parse the battle's results to learn
            if printVerbose:
                print("Parsing battle results...")
            os.system("python3 parse-battle.py")
            if roundBreak:
                print("press enter to continue...")
                input()

    print("done")
    # sys.stdout.close()