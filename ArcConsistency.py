import Environment as env
from collections import deque

def get_row_neighbours(cell):
    r, c = cell
    return {(r, col) for col in range(env.N) if col != c}

def get_col_neighbours(cell):
    r, c = cell
    return {(row, c) for row in range(env.N) if row != r}

def get_square_neighbours(cell):
    r, c = cell
    neighbours = set()
    box_r, box_c = r // 3, c // 3
    for row in range(box_r * 3, box_r * 3 + 3):
        for col in range(box_c * 3, box_c * 3 + 3):
            if (row, col) != (r, c):
                neighbours.add((row, col))
    return neighbours

def get_neighbours(cell):
    """
    All neighbours (row + column + square)
    """
    neighbours = set()
    neighbours.update(get_row_neighbours(cell))
    neighbours.update(get_col_neighbours(cell))
    neighbours.update(get_square_neighbours(cell))
    return neighbours

def initializeDomain(csp):
    """
    Function that calculates domain for all empty cells
    """
    domains = {}
    board = csp.getBoard()
    for r in range(env.N):
        for c in range(env.N):
            if board[r][c] !=0: #already filled
                domains[(r,c)] = {board[r][c]}
            else: #empty
                domain = set(env.DOMAIN)
                domain -= set(csp.getRow(r))
                domain -= set(csp.getCol(c))
                domain -= set(csp.getSquare(r // 3, c // 3))
                domains [(r, c)] = domain

    return domains

def queueArcs(unassigned_cells):
    """
    Builds and returns a queue of all constraint arcs
    Each arc is ((r1, c1), (r2, c2))
    """
    ArcQ = deque()
    
    for Xi in unassigned_cells:  #Xi = (r1, c1)
        for Xj in get_neighbours(Xi):
            ArcQ.append((Xi, Xj))
    return ArcQ
    
def revise(Xi, Xj, D):
    revised = False
    pruned = 0

    domainXi = D[Xi]
    domainXj = D[Xj]
    domainXi_copy = domainXi.copy()

    print(f"Revising arc ({Xi}, {Xj})")
    print(f"Current domain of {Xi}: {sorted(list(domainXi))}")
    print(f"Domain of {Xj}: {sorted(list(domainXj))}")
    
    for val in domainXi_copy:
        compatible_exists = False
        for val_j in domainXj:
            if val != val_j:  #Different values
                compatible_exists = True
                break
        
        # If NO compatible values
        if not compatible_exists:
            #Remove val from Xi's domain
            domainXi.remove(val)
            revised = True
            pruned += 1

            print(f"Removed value {val} from {Xi} because no supporting value exists in {Xj}")

    print(f"Updated domain of {Xi}: {sorted(list(domainXi))}")
    print("-" * 40)
    return revised, pruned
    

def AC3(csp):
    unassigned_cells = csp.getAllUnassigned()
    domains = initializeDomain(csp)
    ArcQ = queueArcs(unassigned_cells)

    revision = 0
    pruning = 0

    #Tree Creation
    root = env.TreeNode(("START", None))
    last_node = root

    while ArcQ:
        Xi, Xj = ArcQ.popleft()

        # Building AC tree structure
        arc_node = env.TreeNode((Xi, Xj))
        last_node.add_child(arc_node)

        revised, pruned = revise(Xi, Xj, domains)
        revision += 1

        if revised:
            pruning += pruned
            if len(domains[Xi]) == 0:
                print(f"Inconsistent! Empty domain for {Xi}")
                arc_node.failed = True
                return False, root, revision, pruning

            for neighbour in get_neighbours(Xi):
                if neighbour != Xj:
                    child = env.TreeNode((neighbour, Xi))
                    arc_node.add_child(child)
                    ArcQ.append((neighbour, Xi))
    
    return True, root, revision, pruning