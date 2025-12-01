import Environment as env
from collections import deque

N=env.N
queue=deque()

#we need to find all arcs

#If Xi has a value v that Xj cannot support,
#remove v from Xi.
#repeat till no change occur

def findAllArcs(board):
    #row arcs
    for r in range (N):
        for c in range (N):
            arc=[(r,c),(r,c+1)]
            queue.append(arc)
    
    #column arcs
    for c in range (N):
        for r in range (N):
            arc=[(r,c),(r+1,c)]
            queue.append(arc)

    #square area arcs
    




    


