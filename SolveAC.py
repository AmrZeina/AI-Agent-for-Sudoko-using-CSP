import Environment as env
import copy
import ArcConsistency as ac   


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
    while True:
        print("\n===== Starting AC-3 iteration =====")
        # Make a copy to detect changes
        old_domains = copy.deepcopy(domains)
        # Run AC3 with logging
        success = ac.AC3(csp)
        if not success:
            print("AC-3 detected inconsistency! No solution possible.")
            return False
        
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
            return True

        # Step 5: Stop when domains no longer change
        if old_domains == domains and not updated:
            print("\nNo more domain changes detected. Arc consistency complete.\n")
            return True
