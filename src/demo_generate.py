import os
import sys
import time

if __name__ == "__main__":

    paths = sys.argv[1:3]
    rate = sys.argv[3]
    n_times = sys.argv[4]


    for i in range(1,int(n_times)+1):
        print( i, "/", n_times, ": generating...")
        print( "using", paths[0], "(", rate,") &", paths[1], "(", 1-float(rate), ")")
        start_time = time.time()
        if "--note" in sys.argv:
            print(" GA with notes")
            os.system("python3 GeneticAlgorithm_withNote.py " + paths[0] + " " + paths[1] + " " + rate)
        else:
            print(" GA with elements")
            os.system("python3 GeneticAlgorithm\ copy.py " + paths[0] + " " + paths[1] + " " + rate)
        print("--- %s seconds ---" % (time.time() - start_time))
        print("done.")


    