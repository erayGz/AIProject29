import tkinter as tk
from tkinter import messagebox, font
import time

# Game constants
INF = float('inf')
MAX_DEPTH = 4  # N-ply lookahead

# Game state
class GameState:
   def __init__(self, number, human_score, computer_score, bank, turn, move=None):
       self.number = number
       self.human_score = human_score
       self.computer_score = computer_score
       self.bank = bank
       self.turn = turn  # "human" or "computer"
       self.move = move  # the move (factor) that led to this state

   def is_terminal(self):
       return self.number >= 1200

   def copy(self):
       return GameState(self.number, self.human_score, self.computer_score, self.bank, self.turn, self.move)

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

       # Bank +1 if number ends with 0 or 5
       if new_state.number % 10 == 0 or new_state.number % 10 == 5:
           new_state.bank += 1

       # Update the score
       if state.turn == 'human':
           new_state.human_score += score_change
       else:
           new_state.computer_score += score_change

       # If game ends, add bank points to the moving player
       if new_state.number >= 1200:
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

# Heuristic evaluation function
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

# Minimax
def minimax(state, depth, is_max):
   global nodes_visited
   nodes_visited += 1
   if depth == 0 or state.is_terminal():
       return evaluate(state), None
   if is_max:
       maxEval = -INF
       best_move = None
       for child in get_children(state):
           eval_child, _ = minimax(child, depth - 1, False)
           if eval_child > maxEval:
               maxEval = eval_child
               best_move = child.move
       return maxEval, best_move
   else:
       minEval = INF
       best_move = None
       for child in get_children(state):
           eval_child, _ = minimax(child, depth - 1, True)
           if eval_child < minEval:
               minEval = eval_child
               best_move = child.move
       return minEval, best_move

# Alpha-beta
def alphabeta(state, depth, alpha, beta, is_max):
   global nodes_visited
   nodes_visited += 1
   if depth == 0 or state.is_terminal():
       return evaluate(state), None
   if is_max:
       maxEval = -INF
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
       minEval = INF
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
   def __init__(self, starting_number, starting_player, algo):
       self.state = GameState(starting_number, 0, 0, 0, starting_player)
       self.algo = algo
       self.game_over = False
       self.computer_nodes = 0
       self.computer_time = 0
       self.computer_moves_log = []  # Log computer move stats

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
       if self.algo == 'minimax':
           _, best_move = minimax(self.state, MAX_DEPTH, True)
       else:
           _, best_move = alphabeta(self.state, MAX_DEPTH, -INF, INF, True)
       end_time = time.perf_counter()
       self.computer_time = end_time - start_time
       self.computer_nodes = nodes_visited
       if best_move is None:
           best_move = 2
       # Log computer move info
       self.computer_moves_log.append(f"Computer move: {self.computer_time:.6f} sec, nodes: {self.computer_nodes}")
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

   def get_computer_moves_log(self):
       return self.computer_moves_log

# GUI class
class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Two-Player Game - Minimax / Alpha-Beta")

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Starting Number (8-18):").grid(row=0, column=0, sticky="e")
        self.start_num_entry = tk.Entry(top_frame, width=5)
        self.start_num_entry.insert(0, "12")
        self.start_num_entry.grid(row=0, column=1, padx=5)

        tk.Label(top_frame, text="Who starts the game:").grid(row=1, column=0, sticky="e")
        self.who_starts_var = tk.StringVar(value="human")
        tk.Radiobutton(top_frame, text="Human", variable=self.who_starts_var, value="human").grid(row=1, column=1, sticky="w")
        tk.Radiobutton(top_frame, text="Computer", variable=self.who_starts_var, value="computer").grid(row=1, column=2, sticky="w")

        tk.Label(top_frame, text="Algorithm Selection:").grid(row=2, column=0, sticky="e")
        self.algo_var = tk.StringVar(value="minimax")
        tk.Radiobutton(top_frame, text="Minimax", variable=self.algo_var, value="minimax").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(top_frame, text="Alpha-Beta", variable=self.algo_var, value="alphabeta").grid(row=2, column=2, sticky="w")

        self.start_button = tk.Button(top_frame, text="Start Game", command=self.start_game)
        self.start_button.grid(row=3, column=0, columnspan=3, pady=5)

        # Main state text
        self.state_text = tk.Text(self.root, height=8, width=50, state="disabled")
        self.state_text.pack(pady=10)

        # Buttons for x2, x3, x4
        move_frame = tk.Frame(self.root)
        move_frame.pack(pady=5)
        self.x2_button = tk.Button(move_frame, text="x2", command=lambda: self.human_move(2), state="disabled")
        self.x2_button.pack(side="left", padx=5)
        self.x3_button = tk.Button(move_frame, text="x3", command=lambda: self.human_move(3), state="disabled")
        self.x3_button.pack(side="left", padx=5)
        self.x4_button = tk.Button(move_frame, text="x4", command=lambda: self.human_move(4), state="disabled")
        self.x4_button.pack(side="left", padx=5)

        self.new_game_button = tk.Button(self.root, text="New Game", command=self.new_game, state="disabled")
        self.new_game_button.pack(pady=5)

        # Computer move log
        self.computer_log_text = tk.Text(self.root, height=4, width=50, state="disabled")
        self.computer_log_text.pack(pady=10)

        self.game = None

    def start_game(self):
        try:
            start_num = int(self.start_num_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Starting number must be an integer.")
            return
        if start_num < 8 or start_num > 18:
            messagebox.showerror("Error", "Number must be between 8 and 18.")
            return
        who = self.who_starts_var.get()
        algo = self.algo_var.get()
        self.game = Game(start_num, who, algo)
        self.update_state_text()
        self.update_computer_log_text()
        self.enable_move_buttons(True)
        self.new_game_button.config(state="normal")
        if who == "computer":
            self.game.computer_move()
            self.update_state_text()
            self.update_computer_log_text()

    def human_move(self, factor):
        if not self.game or self.game.game_over:
            return
        self.game.human_move(factor)
        self.update_state_text()
        if not self.game.game_over:
            self.game.computer_move()
            self.update_state_text()
            self.update_computer_log_text()
        if self.game.game_over:
            self.enable_move_buttons(False)

    def new_game(self):
        self.game = None
        self.enable_move_buttons(False)
        self.new_game_button.config(state="disabled")
        self.state_text.config(state="normal")
        self.state_text.delete("1.0", tk.END)
        self.state_text.config(state="disabled")
        self.computer_log_text.config(state="normal")
        self.computer_log_text.delete("1.0", tk.END)
        self.computer_log_text.config(state="disabled")

    def update_state_text(self):
        if not self.game:
            return
        self.state_text.config(state="normal")
        self.state_text.delete("1.0", tk.END)
        self.state_text.insert(tk.END, self.game.get_state_description())
        self.state_text.config(state="disabled")

    def update_computer_log_text(self):
        if not self.game:
            return
        self.computer_log_text.config(state="normal")
        self.computer_log_text.delete("1.0", tk.END)
        for line in self.game.get_computer_moves_log():
            self.computer_log_text.insert(tk.END, line + "\n")
        self.computer_log_text.config(state="disabled")

    def enable_move_buttons(self, enable):
        state = "normal" if enable else "disabled"
        self.x2_button.config(state=state)
        self.x3_button.config(state=state)
        self.x4_button.config(state=state)

def run_game_interface():
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_game_interface()
