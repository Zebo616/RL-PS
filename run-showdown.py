# Here we will attempt to run a Pokemon battle using the command line API.
# There are a number of advantages to this appraoch; for one, we can 
#   easily simulate battles as a "black box" and simply take 
#   into account the logged feedback afterwards.
# Additionally, Python is full of useful ML libraries that will greatly
#   increase the scope of what we can do in this project.

import os, sys, subprocess

if __name__ == "__main__":
    # Use this string to easily access the pokemon-showdown directory when executing commands.
    # Keep in mind the directory will reset after each os.system() call.
    sDir = "cd pokemon-showdown && "
    # Quick reference for running pokemon-showdown related commands.
    # A list of useful ones can be found here:
    # https://github.com/smogon/pokemon-showdown/blob/master/COMMANDLINE.md
    sNode = "node pokemon-showdown "

    # set SYSOUT to be a file we can easily read.
    # sys.stdout = open("run-showdown-output", "w")

    print("Building...")

    # Build the showdown project
    os.system(sDir + "node build")
    print("Finished building")

    print("Generating teams...")
    # Generate random generation 1 teams
    os.system(sDir + sNode + "generate-team gen1randombattle > genTeamP1.txt")
    os.system(sDir + sNode + "generate-team gen1randombattle > genTeamP2.txt")
    print("Teams generated.")

    # access the teams
    with open("pokemon-showdown/genTeamP1.txt") as f:
        p1Team = f.readlines()

    with open("pokemon-showdown/genTeamP2.txt") as f:
        p2Team = f.readlines()
    
    print("p1's team is: ", p1Team)
    print("p2's team is: ", p2Team)

    # members = 0
    # for member in p1Team.split("]"):
    #     members += 1
    #     print("member of team 1: " + member)
    # print("total members: ", members)

    print("Starting battle...")
    # simulate a battle with the generated teams
    os.system(sDir + "node .sim-dist/examples/run-battle")

    print("done")
    # sys.stdout.close()