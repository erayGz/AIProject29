import tkinter as tk
from tkinter import messagebox, font
import time

# Global constants
WIN_THRESHOLD = 1200
INFINITY = float('inf')
MAX_DEPTH = 4  # search depth limit (N-ply lookahead)


# Game state class
class GameState:
    def __init__(self, number, human_score, computer_score, bank, turn, move=None):
        self.number = number
        self.human_score = human_score
        self.computer_score = computer_score
        self.bank = bank
        self.turn = turn  # "human" or "computer"
        self.move = move  # the move (factor) that led to this state

    def is_terminal(self):
        return self.number >= WIN_THRESHOLD

    def copy(self):
        return GameState(self.number, self.human_score, self.computer_score, self.bank, self.turn, self.move)

    def __repr__(self):
        return (f"GameState(number={self.number}, human_score={self.human_score}, "
                f"computer_score={self.computer_score}, bank={self.bank}, turn={self.turn})")


# Generate possible moves from the current state
def get_children(state):
    children = []
    for factor in [2, 3, 4]:
        new_state = state.copy()
        new_state.move = factor
        new_state.number *= factor
        # Update score based on even/odd result:
        if new_state.number % 2 == 0:
            score_change = -1
        else:
            score_change = 1
        # If number ends with 0 or 5, add 1 point to the bank
        if new_state.number % 10 == 0 or new_state.number % 10 == 5:
            new_state.bank += 1
        # Update the score for the current player
        if state.turn == 'human':
            new_state.human_score += score_change
        else:
            new_state.computer_score += score_change
        # If game ends, add bank points to the moving player
        if new_state.number >= WIN_THRESHOLD:
            if state.turn == 'human':
                new_state.human_score += new_state.bank
            else:
                new_state.computer_score += new_state.bank
            new_state.bank = 0
        else:
            # Switch turn after move
            new_state.turn = 'computer' if state.turn == 'human' else 'human'
        children.append(new_state)
    return children


# Heuristic evaluation function (from computer's perspective)
def evaluate(state):
    if state.is_terminal():
        if state.computer_score > state.human_score:
            return 1000
        elif state.human_score > state.computer_score:
            return -1000
        else:
            return 0
    return (state.computer_score - state.human_score) + 0.5 * state.bank


nodes_visited = 0


# Minimax algorithm
def minimax(state, depth, maximizingPlayer):
    global nodes_visited
    nodes_visited += 1
    if depth == 0 or state.is_terminal():
        return evaluate(state), None
    if maximizingPlayer:
        maxEval = -INFINITY
        best_move = None
        for child in get_children(state):
            eval_child, _ = minimax(child, depth - 1, False)
            if eval_child > maxEval:
                maxEval = eval_child
                best_move = child.move
        return maxEval, best_move
    else:
        minEval = INFINITY
        best_move = None
        for child in get_children(state):
            eval_child, _ = minimax(child, depth - 1, True)
            if eval_child < minEval:
                minEval = eval_child
                best_move = child.move
        return minEval, best_move


# Alpha-beta pruning algorithm
def alphabeta(state, depth, alpha, beta, maximizingPlayer):
    global nodes_visited
    nodes_visited += 1
    if depth == 0 or state.is_terminal():
        return evaluate(state), None
    if maximizingPlayer:
        maxEval = -INFINITY
        best_move = None
        for child in get_children(state):
            eval_child, _ = alphabeta(child, depth - 1, alpha, beta, False)
            if eval_child > maxEval:
                maxEval = eval_child
                best_move = child.move
            alpha = max(alpha, maxEval)
            if beta <= alpha:
                break
        return maxEval, best_move
    else:
        minEval = INFINITY
        best_move = None
        for child in get_children(state):
            eval_child, _ = alphabeta(child, depth - 1, alpha, beta, True)
            if eval_child < minEval:
                minEval = eval_child
                best_move = child.move
            beta = min(beta, minEval)
            if beta <= alpha:
                break
        return minEval, best_move


# Game class to manage game state and moves
class Game:
    def __init__(self, starting_number, starting_player, algorithm):
        self.state = GameState(starting_number, 0, 0, 0, starting_player)
        self.algorithm = algorithm
        self.game_over = False
        self.computer_nodes = 0
        self.computer_time = 0

    def human_move(self, factor):
        if self.game_over or self.state.turn != 'human':
            return
        children = get_children(self.state)
        next_state = None
        for child in children:
            if child.move == factor:
                next_state = child
                break
        if next_state is None:
            return
        self.state = next_state
        self.check_game_over()

    def computer_move(self):
        if self.game_over or self.state.turn != 'computer':
            return
        global nodes_visited
        nodes_visited = 0
        start_time = time.perf_counter()  # high precision timing
        if self.algorithm == 'minimax':
            _, best_move = minimax(self.state, MAX_DEPTH, True)
        else:
            _, best_move = alphabeta(self.state, MAX_DEPTH, -INFINITY, INFINITY, True)
        end_time = time.perf_counter()
        self.computer_time = end_time - start_time
        self.computer_nodes = nodes_visited
        if best_move is None:
            best_move = 2  # default move (rarely reached)
        children = get_children(self.state)
        next_state = None
        for child in children:
            if child.move == best_move:
                next_state = child
                break
        if next_state is None:
            return
        self.state = next_state
        self.check_game_over()

    def check_game_over(self):
        if self.state.is_terminal():
            self.game_over = True

    def get_state_description(self):
        desc = f"Current Number: {self.state.number}\n"
        desc += f"Human Score: {self.state.human_score}\n"
        desc += f"Computer Score: {self.state.computer_score}\n"
        desc += f"Bank: {self.state.bank}\n"
        desc += f"Turn: {self.state.turn}\n"
        if self.game_over:
            if self.state.human_score > self.state.computer_score:
                result = "Human wins!"
            elif self.state.human_score < self.state.computer_score:
                result = "Computer wins!"
            else:
                result = "Draw!"
            desc += "Game Over!\n" + result
        return desc


# GUI using tkinter with enhanced visuals
class GameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Two-Player Game - Minimax / Alpha-Beta")
        master.configure(bg="#e6e6e6")

        # Header label
        self.header = tk.Label(master, text="Two-Player Game - Minimax / Alpha-Beta", font=("Helvetica", 20, "bold"),
                               bg="#e6e6e6", fg="#333333")
        self.header.pack(pady=(10, 5))

        # Settings frame
        self.settings_frame = tk.Frame(master, bg="#e6e6e6", padx=15, pady=15, bd=2, relief="groove")
        self.settings_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(self.settings_frame, text="Starting Number (8-18):", font=("Helvetica", 12), bg="#e6e6e6").grid(row=0,
                                                                                                                 column=0,
                                                                                                                 sticky='w',
                                                                                                                 padx=5,
                                                                                                                 pady=5)
        self.start_number_var = tk.IntVar(value=8)
        self.start_number_entry = tk.Entry(self.settings_frame, textvariable=self.start_number_var, width=5,
                                           font=("Helvetica", 12))
        self.start_number_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.settings_frame, text="Who starts the game:", font=("Helvetica", 12), bg="#e6e6e6").grid(row=1,
                                                                                                              column=0,
                                                                                                              sticky='w',
                                                                                                              padx=5,
                                                                                                              pady=5)
        self.start_player_var = tk.StringVar(value="human")
        tk.Radiobutton(self.settings_frame, text="Human", variable=self.start_player_var, value="human",
                       font=("Helvetica", 12), bg="#e6e6e6").grid(row=1, column=1, padx=5, pady=5)
        tk.Radiobutton(self.settings_frame, text="Computer", variable=self.start_player_var, value="computer",
                       font=("Helvetica", 12), bg="#e6e6e6").grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self.settings_frame, text="Algorithm Selection:", font=("Helvetica", 12), bg="#e6e6e6").grid(row=2,
                                                                                                              column=0,
                                                                                                              sticky='w',
                                                                                                              padx=5,
                                                                                                              pady=5)
        self.algorithm_var = tk.StringVar(value="minimax")
        tk.Radiobutton(self.settings_frame, text="Minimax", variable=self.algorithm_var, value="minimax",
                       font=("Helvetica", 12), bg="#e6e6e6").grid(row=2, column=1, padx=5, pady=5)
        tk.Radiobutton(self.settings_frame, text="Alpha-Beta", variable=self.algorithm_var, value="alphabeta",
                       font=("Helvetica", 12), bg="#e6e6e6").grid(row=2, column=2, padx=5, pady=5)

        self.start_button = tk.Button(self.settings_frame, text="Start Game", command=self.start_game,
                                      font=("Helvetica", 12), bg="#cccccc")
        self.start_button.grid(row=3, column=0, columnspan=3, pady=10)

        # State display
        self.state_text = tk.Text(master, height=10, width=50, font=("Helvetica", 12), bg="#ffffff", bd=2,
                                  relief="sunken")
        self.state_text.pack(pady=10, padx=20)
        self.state_text.config(state=tk.DISABLED)

        # Move buttons frame
        self.move_frame = tk.Frame(master, bg="#e6e6e6", padx=15, pady=15)
        self.move_frame.pack(pady=10)
        self.btn2 = tk.Button(self.move_frame, text="×2", command=lambda: self.human_move(2), state=tk.DISABLED,
                              font=("Helvetica", 12), width=6, bg="#d9d9d9")
        self.btn2.pack(side=tk.LEFT, padx=10)
        self.btn3 = tk.Button(self.move_frame, text="×3", command=lambda: self.human_move(3), state=tk.DISABLED,
                              font=("Helvetica", 12), width=6, bg="#d9d9d9")
        self.btn3.pack(side=tk.LEFT, padx=10)
        self.btn4 = tk.Button(self.move_frame, text="×4", command=lambda: self.human_move(4), state=tk.DISABLED,
                              font=("Helvetica", 12), width=6, bg="#d9d9d9")
        self.btn4.pack(side=tk.LEFT, padx=10)

        # New game button
        self.new_game_button = tk.Button(master, text="New Game", command=self.reset_game, state=tk.DISABLED,
                                         font=("Helvetica", 12), bg="#cccccc")
        self.new_game_button.pack(pady=5)

        # Log text for computer move statistics
        self.log_text = tk.Text(master, height=5, width=50, font=("Helvetica", 12), bg="#ffffff", bd=2, relief="sunken")
        self.log_text.pack(pady=10, padx=20)
        self.log_text.config(state=tk.DISABLED)

        self.game = None
        self.master.after(1000, self.game_loop)

    def start_game(self):
        start_number = self.start_number_var.get()
        if start_number < 8 or start_number > 18:
            messagebox.showerror("Error", "Starting number must be between 8 and 18.")
            return
        starting_player = self.start_player_var.get()
        algorithm = self.algorithm_var.get()
        self.game = Game(start_number, starting_player, algorithm)
        self.update_state_text()
        self.start_button.config(state=tk.DISABLED)
        self.start_number_entry.config(state=tk.DISABLED)
        for child in self.settings_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=tk.DISABLED)
        self.new_game_button.config(state=tk.NORMAL)
        self.update_move_buttons()
        if self.game.state.turn == 'computer':
            self.master.after(500, self.computer_turn)

    def update_state_text(self):
        self.state_text.config(state=tk.NORMAL)
        self.state_text.delete(1.0, tk.END)
        if self.game:
            self.state_text.insert(tk.END, self.game.get_state_description())
        self.state_text.config(state=tk.DISABLED)

    def update_move_buttons(self):
        if self.game and not self.game.game_over and self.game.state.turn == 'human':
            self.btn2.config(state=tk.NORMAL)
            self.btn3.config(state=tk.NORMAL)
            self.btn4.config(state=tk.NORMAL)
        else:
            self.btn2.config(state=tk.DISABLED)
            self.btn3.config(state=tk.DISABLED)
            self.btn4.config(state=tk.DISABLED)

    def human_move(self, factor):
        if self.game and self.game.state.turn == 'human' and not self.game.game_over:
            self.game.human_move(factor)
            self.update_state_text()
            self.update_move_buttons()
            if not self.game.game_over and self.game.state.turn == 'computer':
                self.master.after(500, self.computer_turn)

    def computer_turn(self):
        if self.game and self.game.state.turn == 'computer' and not self.game.game_over:
            self.game.computer_move()
            self.update_state_text()
            self.log_computer_stats()
            self.update_move_buttons()

    def log_computer_stats(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END,
                             f"Computer move: {self.game.computer_time:.6f} sec, nodes visited: {self.game.computer_nodes}\n")
        self.log_text.config(state=tk.DISABLED)

    def reset_game(self):
        self.game = None
        self.state_text.config(state=tk.NORMAL)
        self.state_text.delete(1.0, tk.END)
        self.state_text.config(state=tk.DISABLED)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.start_number_entry.config(state=tk.NORMAL)
        for child in self.settings_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=tk.NORMAL)
        self.new_game_button.config(state=tk.DISABLED)
        self.btn2.config(state=tk.DISABLED)
        self.btn3.config(state=tk.DISABLED)
        self.btn4.config(state=tk.DISABLED)

    def game_loop(self):
        if self.game:
            if self.game.game_over:
                self.update_move_buttons()
        self.master.after(1000, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()
