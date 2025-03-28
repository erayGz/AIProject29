import tkinter as tk
from tkinter import messagebox
import random

class NumberGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Game")

        # Set window size to 720x720
        window_width = 720
        window_height = 720

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate position to center the window
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)

        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        self.start_number = tk.IntVar()
        self.current_number = None
        self.bank = 0
        self.human_score = 0
        self.computer_score = 0
        self.is_human_turn = True  # Start with human turn
        self.max_depth = 3  # Max depth for Minimax

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Choose a number (8-18):").pack()
        self.entry = tk.Entry(self.root, textvariable=self.start_number)
        self.entry.pack()

        tk.Button(self.root, text="Start Game", command=self.start_game).pack()

        self.info_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.info_label.pack(pady=20)

        self.move_buttons = []
        for factor in [2, 3, 4]:
            btn = tk.Button(self.root, text=f"Multiply by {factor}", command=lambda f=factor: self.make_move(f))
            self.move_buttons.append(btn)
            btn.pack()

        self.reset_button = tk.Button(self.root, text="New Game", command=self.reset_game)
        self.reset_button.pack()

        self.toggle_buttons(False)

    def start_game(self):
        try:
            self.current_number = int(self.entry.get())
            if not (8 <= self.current_number <= 18):
                raise ValueError

            print(f"Game started with {self.current_number}")
            self.info_label.config(text=f"Game started with {self.current_number}")
            self.bank = 0
            self.human_score = 0
            self.computer_score = 0
            self.is_human_turn = True  # Human starts first
            self.toggle_buttons(True)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number between 8 and 18")

    def make_move(self, factor):
        if self.current_number is None or not self.is_human_turn:
            return

        print(f"Human chooses to multiply {self.current_number} by {factor}")
        self.current_number *= factor
        self.update_scores()

        if self.current_number >= 1200:
            self.end_game()
            return

        # Switch to computer turn AFTER a delay
        self.is_human_turn = False
        self.toggle_buttons(False)
        self.root.after(2000, self.computer_move)  # 1 sec delay before AI plays

    def update_scores(self):
        if self.current_number % 2 == 0:
            if self.is_human_turn:
                self.human_score -= 1
            else:
                self.computer_score -= 1
        else:
            if self.is_human_turn:
                self.human_score += 1
            else:
                self.computer_score += 1

        if self.current_number % 10 == 0 or self.current_number % 10 == 5:
            self.bank += 1

        self.info_label.config(text=f"Current number: {self.current_number}, Bank: {self.bank}\nHuman: {self.human_score}, Computer: {self.computer_score}")

    def computer_move(self):
        if self.current_number >= 1200:
            return  # Game already ended

        # Call Minimax or Alpha-Beta algorithm to make the computer's move
        best_move = self.alpha_beta(self.current_number, self.bank, self.human_score, self.computer_score, 0, True, -float('inf'), float('inf'))
        factor = best_move[0]
        print(f"Computer chooses to multiply {self.current_number} by {factor}")

        self.current_number *= factor
        self.update_scores()

        if self.current_number >= 1200:
            self.end_game()
            return

        # Switch back to human turn
        self.is_human_turn = True
        self.toggle_buttons(True)

    def alpha_beta(self, number, bank, human_score, computer_score, depth, maximizing_player, alpha, beta):
        if depth == self.max_depth or number >= 1200:
            return [None, self.evaluate(number, bank, human_score, computer_score)]

        if maximizing_player:
            max_eval = -float('inf')
            best_move = None
            for factor in [2, 3, 4]:
                new_number = number * factor
                new_human_score = human_score + (1 if new_number % 2 != 0 else -1)
                new_computer_score = computer_score + (1 if new_number % 2 != 0 else -1)
                new_bank = bank + (1 if new_number % 10 == 0 or new_number % 10 == 5 else 0)

                eval_result = self.alpha_beta(new_number, new_bank, new_human_score, new_computer_score, depth + 1, False, alpha, beta)
                eval_score = eval_result[1]

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = factor
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cut-off
            return [best_move, max_eval]
        else:
            min_eval = float('inf')
            best_move = None
            for factor in [2, 3, 4]:
                new_number = number * factor
                new_human_score = human_score + (1 if new_number % 2 != 0 else -1)
                new_computer_score = computer_score + (1 if new_number % 2 != 0 else -1)
                new_bank = bank + (1 if new_number % 10 == 0 or new_number % 10 == 5 else 0)

                eval_result = self.alpha_beta(new_number, new_bank, new_human_score, new_computer_score, depth + 1, True, alpha, beta)
                eval_score = eval_result[1]

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = factor
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cut-off
            return [best_move, min_eval]

    def evaluate(self, number, bank, human_score, computer_score):
        # A simple heuristic for evaluation:
        if number >= 1200:
            return computer_score - human_score  # If the game ends, return the score difference
        return computer_score - human_score  # You can improve this evaluation function

    def end_game(self):
        if self.is_human_turn:
            self.human_score += self.bank
        else:
            self.computer_score += self.bank

        result = "It's a draw!"
        if self.human_score > self.computer_score:
            result = "You win!"
        elif self.computer_score > self.human_score:
            result = "Computer wins!"

        messagebox.showinfo("Game Over", result)
        self.toggle_buttons(False)

    def reset_game(self):
        self.start_number.set(0)
        self.current_number = None
        self.bank = 0
        self.human_score = 0
        self.computer_score = 0
        self.is_human_turn = True
        self.info_label.config(text="")
        self.toggle_buttons(False)

    def toggle_buttons(self, state):
        for btn in self.move_buttons:
            btn.config(state="normal" if state else "disabled")


if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGame(root)
    root.mainloop()
