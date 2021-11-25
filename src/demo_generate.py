import os
import sys

if __name__ == "__main__":

    paths = sys.argv[1:3]
    rate = sys.argv[3]
    n_times = sys.argv[4]


    for i in range(1,int(n_times)+1):
        print( i, "time generating...")
        print( "using", paths[0], "(", rate,") &", paths[1], "(", 1-float(rate), ")")
        if "--note" in sys.argv:
            os.system("python3 GeneticAlgorithm_withNote.py " + paths[0] + " " + paths[1] + " " + rate)
        else:
            os.system("python3 GeneticAlgorithm\ copy.py " + paths[0] + " " + paths[1] + " " + rate)



    