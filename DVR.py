import sys
import time
import math
import threading
from _thread import *
import numpy as np
from queue import Queue

lock = threading.Lock()
star_lock = threading.Lock()

no_of_routers = 0
router_list = []
dist = []
next_hop = []
queue_list = []
neighbours = []
router_dict = {}
star = []

def ReadFile(filename):

    global no_of_routers
    global router_list
    global dist
    global router_dict
    global queue_list
    global neighbours
    global next_hop

    try:
        f = open(filename, "r")
        print("File opened successfully")

        no_of_routers = int(f.readline())
        print("Number of Routers : " + str(no_of_routers))

        router_list = f.readline().strip().split(" ")

        # initializing matrices which represent min distance
        dist = np.zeros((no_of_routers, no_of_routers))
        next_hop = np.zeros((no_of_routers, no_of_routers)).astype("int")

        for i in range(no_of_routers): 
            for j in range(no_of_routers):
                if i == j:
                    dist[i, j] = 0
                    next_hop[i, j] = i
                else:
                    dist[i, j] = math.inf
                    next_hop[i, j] = no_of_routers

        # list of queues of routers
        queue_list = [Queue() for router in range(no_of_routers)]

        # list of every router's list of neighbours
        neighbours = [[] for router in range(no_of_routers)]

        # creating router dictionary i.e router A is stored as 0, B is stored as 1 etc.
        for i, r in enumerate(router_list):
            router_dict[r] = i

        line = f.readline().strip()
        while line != 'EOF':
            data = line.split(" ")

            # initialize distance vectors using file data i.e for A B 5 both A and B router's tables are updated
            dist[router_dict[data[0]], router_dict[data[1]]] = int(data[2])  
            dist[router_dict[data[1]], router_dict[data[0]]] = int(data[2])

            # initialize next hop values
            next_hop[router_dict[data[0]], router_dict[data[1]]] = router_dict[data[1]]
            next_hop[router_dict[data[1]], router_dict[data[0]]] = router_dict[data[0]]

            # assign router pairs as neighbours of each other
            neighbours[router_dict[data[0]]].append(router_dict[data[1]])
            neighbours[router_dict[data[1]]].append(router_dict[data[0]])

            line = f.readline().strip()

        f.close()

    except IOError:
        print("Error opening file " + filename)


def add_queue(index, router_no):

    global queue_list
    global dist

    lock.acquire()
    # router number and distance list of that router from other routers are added to the queue
    queue_list[index].put((router_no, dist[router_no, :]))
    lock.release()


def queuing(index):

    for i in neighbours[index]:
        add_queue(index, i)


def print_table():

    global star
    global next_hop

    for i in range(no_of_routers):

        print("Router " + router_list[i] + ":")

        for j in range(no_of_routers):

            if (i, j) in star:
                print("*", end="")
            if next_hop[i, j] < no_of_routers:
                print("dist(" + router_list[j] + ") = " + str(dist[i][j]))
            else:
                print("dist(" + router_list[j] + ") = inf")

        print()


def Bellman_Ford(index):
    
    global queue_list
    global dist
    global star
    queue_data = []

    while not queue_list[index].empty():
        queue_data.append(queue_list[index].get())

    for r in range(no_of_routers):
        
        if index != r:
            for data in queue_data:  
                
                # bellman ford equation
                if dist[index][r] > dist[index][data[0]] + data[1][r]:
                    dist[index][r] = dist[index][data[0]] + data[1][r]
                    next_hop[index, r] = data[0]
                    star_lock.acquire()
                    star.append((index, r))
                    star_lock.release()

try:
    filename = sys.argv[1]
except:
    print("Error: too few arguments")

ReadFile(filename)

for itr in range(no_of_routers):
    
    all_threads = []
    print("Iteration = " + str(itr) + ":")
    print_table()
    star = []
    time.sleep(2)
    
    for i in range(no_of_routers):
        # queue new data to corresponding neighbours of routers
        x = threading.Thread(target=queuing, args=(i,))
        all_threads.append(x)
        x.start()

    for x in all_threads:
        x.join()

    all_threads = []

    for i in range(no_of_routers):
        # start thread to Bellman_Ford distances using queue data
        x = threading.Thread(target=Bellman_Ford, args=(i,))
        all_threads.append(x)
        x.start()
