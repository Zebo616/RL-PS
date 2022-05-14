import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import numpy as np

file1 = "V2FullDouble"
file2 = "V2Single"

if __name__ == "__main__":
    f = open(file1 + "/time.txt")
    times1 = f.readlines()
    f.close()
    f = open(file2 + "/time.txt")
    times2 = f.readlines()
    f.close()

    x1 = []
    Dtimes1 = []
    previous = 0

    for i in range(len(times1)):
        times1[i] = float(times1[i][:-2])
        Dtimes1.append(times1[i] - previous)
        x1.append(i)
        previous = times1[i]

    x2 = []
    Dtimes2 = []
    previous = 0
    
    for i in range(len(times2)):
        times2[i] = float(times2[i][:-2])
        Dtimes2.append(times2[i] - previous)
        x2.append(i)
        previous = times2[i]

    for i in range(len(times1)):
        if i == len(times1) or i == len(times2):
            break
        print("difference in training time is:", times2[i] - times1[i])

    plt.plot(x2, Dtimes2, label = file2)
    plt.plot(x1, Dtimes1, label = file1)

    # plt.plot(x2, times2, label = file2)
    # plt.plot(x1, times1, label = file1)

    # naming the x axis
    plt.xlabel('iteration number')
    # naming the y axis
    plt.ylabel('time')

    # giving a title to my graph
    plt.title('Training Time, Per Timestep')

    plt.legend(loc='center left', bbox_to_anchor=(1, 0))

    plt.tight_layout()
  
    # function to show the plot
    plt.show()
