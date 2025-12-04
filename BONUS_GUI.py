# sudoku_gui.py
import sys
import io
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import time

# Project modules (assumed to exist in the same project)
import Environment as env
import Creation
import SolveAC as ACS
import Backtracking as BK

# ------------------ Utilities ------------------

class StdoutRedirector:
    """Capture print() output (used for AC-3 / solver logs)."""
    def __init__(self):
        self.buffer = io.StringIO()
        self._orig = None

    def __enter__(self):
        self._orig = sys.stdout
        sys.stdout = self.buffer
        return self

    def __exit__(self, exc_type, exc, tb):
        sys.stdout = self._orig
        if exc_type:
            traceback.print_exception(exc_type, exc, tb, file=self.buffer)

    def getvalue(self):
        return self.buffer.getvalue()


def board_to_text(board_obj):
    """Return 9-line string representation (0 for empty)."""
    b = board_obj.getBoard()
    return '\n'.join(''.join(str(x) for x in b[r]) for r in range(env.N))


def text_to_board(text):
    """Parse a 9-line representation into a new env.sudoku() object.
    Accepts contiguous digits or space-separated digits.
    Non-digits are treated as 0."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip() != '']
    if len(lines) < env.N:
        raise ValueError("Not enough lines for a 9x9 board.")
    g = env.sudoku()
    for r in range(env.N):
        line = lines[r]
        tokens = line.split()
        if len(tokens) == env.N:
            for c in range(env.N):
                ch = tokens[c]
                g.addNum(r, c, int(ch) if ch.isdigit() else 0)
        else:
            for c in range(env.N):
                g.addNum(r, c, int(line[c]) if c < len(line) and line[c].isdigit() else 0)
    return g


# ------------------ GUI ------------------

class SudokuGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku CSP Visualizer")
        self.geometry("980x720")
        self.minsize(900, 650)
        self.configure(bg="#f3f6fb")

        # Fonts & style
        self.header_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.cell_font = font.Font(family="Consolas", size=18, weight="bold")
        self.small_font = font.Font(family="Segoe UI", size=10)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.configure("Accent.TButton", foreground="white", background="#4b7bec")
        style.map("Accent.TButton", background=[("active", "#3a5db0"), ("!disabled", "#4b7bec")])

        # State
        self.cells = {}                      # (r,c) -> Entry widget
        self.original_board = None           # snapshot of original numbers
        self.last_assign_source = {}         # (r,c) -> "original"|"ac3"|"backtracking"|"user"
        self.current_board = env.sudoku()

        # Build UI
        self._build_header()
        self._build_controls()
        self._build_board()
        self._build_logs()

        # initialize
        self.reset_board_colors()
        self.refresh_grid_from_board(self.current_board)

    # ---------- UI pieces ----------
    def _build_header(self):
        header = tk.Canvas(self, height=70, bg="#ffffff", highlightthickness=0)
        header.pack(fill="x", padx=12, pady=(12, 4))
        w = 980
        for i, color in enumerate(["#eef4ff", "#e6f0ff", "#dfe9ff"]):
            header.create_rectangle(0, i * 23, w, (i + 1) * 23, fill=color, outline=color)
        header.create_text(20, 36, anchor="w", text="Sudoku CSP Visualizer", font=self.header_font, fill="#222")
        header.create_text(20, 52, anchor="w", text="Arc Consistency (AC-3) • Backtracking • Visual logs", font=self.small_font, fill="#555")

    def _build_controls(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=12, pady=(4, 8))

        left = ttk.Frame(frame); left.pack(side="left", anchor="n")
        ttk.Button(left, text="Generate Puzzle", command=self.on_generate, style="Accent.TButton").grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(left, text="Validate Input", command=self.on_validate).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(left, text="Solve using AC-3", command=self.on_ac3).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(left, text="Full Solve (AC3 + Backtracking)", command=self.on_full_solve).grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(left, text="Clear Board", command=self.on_clear).grid(row=0, column=4, padx=4, pady=4)

        right = ttk.Frame(frame); right.pack(side="right", anchor="n")
        ttk.Button(right, text="Load Puzzle", command=self.on_load).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(right, text="Save Puzzle", command=self.on_save).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(right, text="Exit", command=self.destroy).grid(row=0, column=2, padx=4, pady=4)

    def _build_board(self):
        board_frame = ttk.Frame(self, padding=8)
        board_frame.pack(side="left", padx=(12, 8), pady=6)

        self.grid_canvas = tk.Canvas(board_frame, width=450, height=450, bg="white", highlightthickness=0)
        self.grid_canvas.pack()

        cell_size = 50
        padding = 2
        self.cells = {}

        for r in range(env.N):
            for c in range(env.N):
                x = c * cell_size
                y = r * cell_size
                e = tk.Entry(self.grid_canvas, width=2, font=self.cell_font, justify="center", bd=0, relief="ridge")
                vcmd = (self.register(self._validate_entry), '%P', '%d')
                e.config(validate="key", validatecommand=vcmd)
                e.bind("<FocusOut>", self._on_cell_focusout)
                e.bind("<KeyRelease>", self._on_key_release)  # live feedback color while typing
                self.grid_canvas.create_window(x + cell_size/2, y + cell_size/2, window=e, width=cell_size-2*padding, height=cell_size-2*padding)
                self.cells[(r, c)] = e

        for i in range(env.N + 1):
            thickness = 3 if i % 3 == 0 else 1
            self.grid_canvas.create_line(0, i * cell_size, 9 * cell_size, i * cell_size, width=thickness, fill="#000")
            self.grid_canvas.create_line(i * cell_size, 0, i * cell_size, 9 * cell_size, width=thickness, fill="#000")

        legend = ttk.Frame(board_frame); legend.pack(pady=(8, 0))
        def make_legend(text, color):
            lbl = tk.Label(legend, text=text, bg=color, fg="#111", padx=10, pady=4)
            lbl.pack(side="left", padx=6)
        make_legend("Given", "#a9a9a9")
        make_legend("AC-3 assigned", "#c9f0d6")
        make_legend("Backtracking", "#d7f0ff")
        make_legend("User", "#fff8dc")
        make_legend("Invalid (conflict)", "#ffb3b3")

    def _build_logs(self):
        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=(0,12), pady=6)
        ttk.Label(right_frame, text="AC-3 & Solver Logs", font=self.small_font).pack(anchor="w", pady=(2,6))
        self.log_text = tk.Text(right_frame, width=48, height=28, wrap="word", bg="#111", fg="#dfeaff")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.insert("1.0", "Logs will appear here when you run AC-3 or the solver...\n")

    # ---------- Entry validation / events ----------
    def _validate_entry(self, P, action_type):
        if P == "":
            return True
        if len(P) > 1:
            return False
        return P.isdigit() and 1 <= int(P) <= 9

    def _on_key_release(self, event):
        # while typing, color cell as user (but do not write to model until focusout)
        widget = event.widget
        for (r, c), w in self.cells.items():
            if w is widget:
                w.config(bg="#fff8dc", fg="#111")
                break

    def _on_cell_focusout(self, event):
        widget = event.widget
        for (r, c), w in self.cells.items():
            if w is widget:
                txt = w.get().strip()
                val = int(txt) if txt.isdigit() else 0

                # before adding to board → check validity
                if val != 0 and not self.is_valid_move(r, c, val):
                    # highlight conflict and show message
                    w.config(bg="#ffb3b3")
                    messagebox.showwarning("Invalid Move", f"Placing {val} at row {r+1}, col {c+1} violates Sudoku constraints.")
                    # do NOT update model with invalid value
                    return

                # valid → update model and mark source
                self.current_board.addNum(r, c, val)
                self.last_assign_source[(r, c)] = "user"

                # update cell color based on source
                self._color_cell(r, c)
                break

    def is_valid_move(self, r, c, val):
        """Check row, column, and box constraints for user input."""
        if val == 0:
            return True  # empty is always valid

        b = self.current_board.getBoard()

        # Check row
        for j in range(env.N):
            if j != c and b[r][j] == val:
                return False

        # Check column
        for i in range(env.N):
            if i != r and b[i][c] == val:
                return False

        # Check 3x3 box
        br = (r // 3) * 3
        bc = (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i, j) != (r, c) and b[i][j] == val:
                    return False

        return True

    # ---------- Board <-> UI syncing ----------
    def reset_board_colors(self):
        self.last_assign_source = {(r, c): "user" for r in range(env.N) for c in range(env.N)}

    def refresh_grid_from_board(self, board_obj, mark_original=True):
        """Update GUI entries to match board_obj (env.sudoku())."""
        board = board_obj.getBoard()
        if mark_original and self.original_board is None:
            self.original_board = [[board[r][c] for c in range(env.N)] for r in range(env.N)]

        for r in range(env.N):
            for c in range(env.N):
                val = board[r][c]
                ent = self.cells[(r, c)]
                ent.delete(0, "end")
                if val != 0:
                    ent.insert(0, str(val))

                if self.original_board and self.original_board[r][c] != 0:
                    self.last_assign_source[(r, c)] = "original"
                elif val != 0 and self.last_assign_source.get((r, c)) is None:
                    self.last_assign_source[(r, c)] = "user"

                self._color_cell(r, c)

    def _color_cell(self, r, c):
        ent = self.cells[(r, c)]
        src = self.last_assign_source.get((r, c), "user")
        if src == "original":
            ent.config(bg="#a9a9a9", fg="#111", state="readonly")
        elif src == "ac3":
            ent.config(bg="#c9f0d6", fg="#062b12", state="normal")
        elif src == "backtracking":
            ent.config(bg="#d7f0ff", fg="#04223a", state="normal")
        elif self.current_board.getBoard()[r][c] == 0:
            ent.config(bg="white", fg="#111", state="normal")
        else:
            # user-entered valid cell
            ent.config(bg="#fff8dc", fg="#111", state="normal")

    # ---------- Actions ----------
    def on_generate(self):
        try:
            self.current_board = env.sudoku()
            Creation.generateRandom(self.current_board)
            self.original_board = [[self.current_board.getBoard()[r][c] for c in range(env.N)] for r in range(env.N)]
            for r in range(env.N):
                for c in range(env.N):
                    self.last_assign_source[(r, c)] = "original" if self.original_board[r][c] != 0 else "user"
            self.refresh_grid_from_board(self.current_board, mark_original=False)
            self.log("Generated a new puzzle (50 cells removed).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate puzzle:\n{e}")

    def on_clear(self):
        self.current_board = env.sudoku()
        self.original_board = None
        self.reset_board_colors()
        self.refresh_grid_from_board(self.current_board, mark_original=False)
        self.log("Cleared board.")

    def on_load(self):
        try:
            path = filedialog.askopenfilename(title="Load puzzle", filetypes=[("Text files","*.txt"),("All files","*.*")])
            if not path:
                return
            with open(path, "r") as f:
                data = f.read()
            self.current_board = text_to_board(data)
            self.original_board = [[self.current_board.getBoard()[r][c] for c in range(env.N)] for r in range(env.N)]
            for r in range(env.N):
                for c in range(env.N):
                    self.last_assign_source[(r, c)] = "original" if self.original_board[r][c] != 0 else "user"
            self.refresh_grid_from_board(self.current_board, mark_original=False)
            self.log(f"Loaded puzzle from {path}")
        except Exception as e:
            messagebox.showerror("Error loading file", str(e))

    def on_save(self):
        try:
            path = filedialog.asksaveasfilename(title="Save puzzle", defaultextension=".txt", filetypes=[("Text files","*.txt")])
            if not path:
                return
            text = board_to_text(self.current_board)
            with open(path, "w") as f:
                f.write(text)
            self.log(f"Saved puzzle to {path}")
        except Exception as e:
            messagebox.showerror("Error saving file", str(e))

    def on_validate(self):
        try:
            self._pull_entries_to_board()
            ok = Creation.validateInput(self.current_board)
            if ok:
                messagebox.showinfo("Validate", "Puzzle is solvable (backtracking found a solution).")
                self.log("Validate: puzzle is solvable (backtracking).")
            else:
                messagebox.showwarning("Validate", "Puzzle is NOT solvable.")
                self.log("Validate: puzzle is NOT solvable.")
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{e}")

    def _pull_entries_to_board(self):
        for r in range(env.N):
            for c in range(env.N):
                txt = self.cells[(r, c)].get().strip()
                val = int(txt) if txt.isdigit() else 0
                self.current_board.addNum(r, c, val)
                if self.original_board and self.original_board[r][c] != val:
                    self.last_assign_source[(r, c)] = "user"

    def on_ac3(self):
        try:
            self._pull_entries_to_board()
            with StdoutRedirector() as rd:
                start = time.time()
                success = ACS.enforceArcConsistency(self.current_board)
                elapsed = time.time() - start
            log = rd.getvalue().strip() or "(no output generated by AC-3)"
            self._append_log(log)
            if not success:
                messagebox.showerror("AC-3 Result", "AC-3 detected inconsistency (no solution possible). See logs.")
                self.log("AC-3: inconsistent (empty domain encountered).")
                return
            # mark new ac3 assignments
            for r in range(env.N):
                for c in range(env.N):
                    prev = self.original_board[r][c] if self.original_board else 0
                    val = self.current_board.getBoard()[r][c]
                    if prev == 0 and val != 0:
                        self.last_assign_source[(r, c)] = "ac3"
            self.refresh_grid_from_board(self.current_board, mark_original=False)
            messagebox.showinfo("AC-3 Complete", f"AC-3 finished in {elapsed:.2f} seconds. See logs.")
            self.log(f"AC-3 finished in {elapsed:.2f}s.")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error running AC-3", str(e))

    def on_full_solve(self):
        try:
            self._pull_entries_to_board()
            with StdoutRedirector() as rd:
                start = time.time()
                ac_success = ACS.enforceArcConsistency(self.current_board)
                solution = BK.backtrackingSearch(self.current_board, Randomize=False)
                elapsed = time.time() - start
            log = rd.getvalue().strip() or "(no output generated)"
            self._append_log(log)
            if not ac_success:
                messagebox.showerror("Result", "AC-3 detected inconsistency first; no solution.")
                self.log("AC-3 declared inconsistency; aborting full solve.")
                return
            if solution is None:
                messagebox.showwarning("Full Solve", "AC-3 completed but backtracking did not find a solution.")
                self.log("Full Solve: backtracking returned None.")
                self.refresh_grid_from_board(self.current_board, mark_original=False)
                return
            # apply solution and mark backtracking assignments
            for r in range(env.N):
                for c in range(env.N):
                    orig = self.original_board[r][c] if self.original_board else 0
                    current_val = self.current_board.getBoard()[r][c]
                    solved_val = solution.getBoard()[r][c]
                    if orig == 0 and solved_val != 0 and current_val != solved_val:
                        self.last_assign_source[(r, c)] = "backtracking"
                        self.current_board.addNum(r, c, solved_val)
            self.refresh_grid_from_board(self.current_board, mark_original=False)
            elapsed_msg = f"Full solve finished in {elapsed:.2f} seconds."
            messagebox.showinfo("Full Solve", "Solved! " + elapsed_msg)
            self.log("Full Solve: " + elapsed_msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Full Solve Error", str(e))

    # ---------- Logging ----------
    def log(self, text):
        self._append_log(text + "\n")

    def _append_log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")


if __name__ == "__main__":
    app = SudokuGUI()
    app.mainloop()
