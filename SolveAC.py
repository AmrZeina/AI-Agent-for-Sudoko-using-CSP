import Environment as env
import copy
import ArcConsistency as ac  
import ACTree as tree 

def draw_tree(root):
    graph = tree.draw_tree(root)
    graph.render("ac3_tree", format="pdf", cleanup=True)

def enforceArcConsistency(csp):
    """
    This function:
    - Runs AC-3
    - Applies domain reductions to the board
    - Repeats AC-3 until no more changes can be made
    - Stops when the board is fully solved
    """

    # Step 1: Initialize domains
    domains = ac.initializeDomain(csp)
    revision = 0
    pruning = 0
    while True:
        print("\n===== Starting AC-3 iteration =====")
        # Make a copy to detect changes
        old_domains = copy.deepcopy(domains)
        # Run AC3 with logging
        success, root, revised, pruned = ac.AC3(csp)
        revision+=revised
        pruning += pruned
        if not success:
            print("AC-3 detected inconsistency! No solution possible.")
            return False, revision, pruning
        
        # Step 2: Update board with singleton domains
        updated = False
        for r in range(9):
            for c in range(9):
                if len(domains[(r, c)]) == 1:
                    val = next(iter(domains[(r, c)]))
                    if csp.board[r][c] == 0:
                        print(f"Assigning X({r},{c}) = {val} because its domain is singleton.")
                        csp.addNum(r, c, val)
                        updated = True

        # Step 3: Recompute domains after assignments
        domains = ac.initializeDomain(csp)

        # Step 4: If board solved → finish
        if csp.isFilled():
            print("\nBoard solved by repeated Arc Consistency!\n")
            draw_tree(root)
            return True,  revision, pruning

        # Step 5: Stop when domains no longer change
        if old_domains == domains and not updated:
            print("\nNo more domain changes detected. Arc consistency complete.\n")
            draw_tree(root)
            return True,  revision, pruning
