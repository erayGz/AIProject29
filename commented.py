        # Create a frame for the move buttons with a light grey background, horizontal and vertical padding.
        self.move_frame = tk.Frame(master, bg="#e6e6e6", padx=15, pady=15)
        # Pack (display) the move_frame with vertical padding of 10 pixels.
        self.move_frame.pack(pady=10)

        # Create a button for multiplying by 2:
        # - Parent widget: self.move_frame
        # - Text displayed: "×2"
        # - When clicked, it calls the human_move function with factor 2.
        # - Initial state is DISABLED (not clickable until game starts)
        # - Font is set to Helvetica 12pt, width 6 characters, background color light grey.
        self.btn2 = tk.Button(self.move_frame, text="×2", command=lambda: self.human_move(2), state=tk.DISABLED,
                              font=("Helvetica", 12), width=6, bg="#d9d9d9")
        # Pack the button to the left side with 10 pixels horizontal padding.
        self.btn2.pack(side=tk.LEFT, padx=10)

        # Create a button for multiplying by 3 with similar settings as btn2.
        self.btn3 = tk.Button(self.move_frame, text="×3", command=lambda: self.human_move(3), state=tk.DISABLED,
                              font=("Helvetica", 12), width=6, bg="#d9d9d9")
        # Pack the btn3 to the left side with 10 pixels horizontal padding.
        self.btn3.pack(side=tk.LEFT, padx=10)

        # Create a button for multiplying by 4 with similar settings.
        self.btn4 = tk.Button(self.move_frame, text="×4", command=lambda: self.human_move(4), state=tk.DISABLED,
                              font=("Helvetica", 12), width=6, bg="#d9d9d9")
        # Pack the btn4 to the left side with 10 pixels horizontal padding.
        self.btn4.pack(side=tk.LEFT, padx=10)

        # Create the "New Game" button:
        # - Parent widget: master (main window)
        # - Text: "New Game"
        # - Calls reset_game function when clicked
        # - Initially disabled; font set to Helvetica 12pt, background color light grey.
        self.new_game_button = tk.Button(master, text="New Game", command=self.reset_game, state=tk.DISABLED,
                                         font=("Helvetica", 12), bg="#cccccc")
        # Pack the New Game button with vertical padding of 5 pixels.
        self.new_game_button.pack(pady=5)

        # Create a Text widget for logging computer move statistics:
        # - Parent widget: master (main window)
        # - Height: 5 lines; Width: 50 characters
        # - Font set to Helvetica 12pt, background white, with a 2-pixel border and sunken relief (3D effect).
        self.log_text = tk.Text(master, height=5, width=50, font=("Helvetica", 12), bg="#ffffff", bd=2, relief="sunken")
        # Pack the log_text widget with vertical padding of 10 and horizontal padding of 20 pixels.
        self.log_text.pack(pady=10, padx=20)
        # Disable editing of the log_text widget (read-only).
        self.log_text.config(state=tk.DISABLED)

        # Initialize the game object to None since no game has started yet.
        self.game = None
        # Schedule the game_loop function to be called after 1000 milliseconds (1 second) repeatedly.
        self.master.after(1000, self.game_loop)

    # Function to start a new game
    def start_game(self):
        # Retrieve the starting number from the input widget.
        start_number = self.start_number_var.get()
        # Check if the starting number is within the allowed range (8-18).
        if start_number < 8 or start_number > 18:
            # If not, display an error message.
            messagebox.showerror("Error", "Starting number must be between 8 and 18.")
            return
        # Get the starting player choice (human or computer) from the radio buttons.
        starting_player = self.start_player_var.get()
        # Get the algorithm choice (minimax or alphabeta) from the radio buttons.
        algorithm = self.algorithm_var.get()
        # Create a new game instance with the chosen starting number, player, and algorithm.
        self.game = Game(start_number, starting_player, algorithm)
        # Update the state text widget to reflect the new game state.
        self.update_state_text()
        # Disable the start button to prevent restarting during a game.
        self.start_button.config(state=tk.DISABLED)
        # Disable the entry widget for the starting number.
        self.start_number_entry.config(state=tk.DISABLED)
        # Disable all radiobuttons in the settings frame to lock the choices.
        for child in self.settings_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=tk.DISABLED)
        # Enable the New Game button now that a game has started.
        self.new_game_button.config(state=tk.NORMAL)
        # Update the state of the move buttons (enable if it's human's turn).
        self.update_move_buttons()
        # If it is the computer's turn, schedule the computer_turn function to run after 500 milliseconds.
        if self.game.state.turn == 'computer':
            self.master.after(500, self.computer_turn)

    # Function to update the state display text widget with the current game state.
    def update_state_text(self):
        # Enable editing temporarily to update the text.
        self.state_text.config(state=tk.NORMAL)
        # Clear the current text.
        self.state_text.delete(1.0, tk.END)
        # If a game is in progress, insert the current state description.
        if self.game:
            self.state_text.insert(tk.END, self.game.get_state_description())
        # Disable editing again.
        self.state_text.config(state=tk.DISABLED)

    # Function to enable or disable the move buttons based on game state.
    def update_move_buttons(self):
        # If the game exists, is not over, and it's the human's turn...
        if self.game and not self.game.game_over and self.game.state.turn == 'human':
            # Enable the multiply-by-2, 3, and 4 buttons.
            self.btn2.config(state=tk.NORMAL)
            self.btn3.config(state=tk.NORMAL)
            self.btn4.config(state=tk.NORMAL)
        else:
            # Otherwise, disable these buttons.
            self.btn2.config(state=tk.DISABLED)
            self.btn3.config(state=tk.DISABLED)
            self.btn4.config(state=tk.DISABLED)

    # Function that processes a human move when a move button is clicked.
    def human_move(self, factor):
        # Check that a game exists, it's human's turn, and the game is not over.
        if self.game and self.game.state.turn == 'human' and not self.game.game_over:
            # Apply the human move with the given multiplication factor.
            self.game.human_move(factor)
            # Update the state text to reflect the move.
            self.update_state_text()
            # Update the move buttons (enable/disable based on new state).
            self.update_move_buttons()
            # If the game is still running and it's now the computer's turn, schedule a computer move after 500ms.
            if not self.game.game_over and self.game.state.turn == 'computer':
                self.master.after(500, self.computer_turn)

    # Function to process the computer's turn.
    def computer_turn(self):
        # Ensure a game exists, it's the computer's turn, and the game is not over.
        if self.game and self.game.state.turn == 'computer' and not self.game.game_over:
            # Let the game logic process the computer move.
            self.game.computer_move()
            # Update the state display after the move.
            self.update_state_text()
            # Log computer move statistics (time taken, nodes visited).
            self.log_computer_stats()
            # Update the move buttons based on the new state.
            self.update_move_buttons()

    # Function to log statistics of the computer's move in the log_text widget.
    def log_computer_stats(self):
        # Enable editing of the log_text widget.
        self.log_text.config(state=tk.NORMAL)
        # Insert a line with the computer move time and number of nodes visited.
        self.log_text.insert(tk.END,
                             f"Computer move: {self.game.computer_time:.6f} sec, nodes visited: {self.game.computer_nodes}\n")
        # Disable editing again.
        self.log_text.config(state=tk.DISABLED)

    # Function to reset the game and GUI to initial state for a new game.
    def reset_game(self):
        # Set the game object to None to indicate no active game.
        self.game = None
        # Enable and clear the state text widget.
        self.state_text.config(state=tk.NORMAL)
        self.state_text.delete(1.0, tk.END)
        self.state_text.config(state=tk.DISABLED)
        # Enable and clear the log_text widget.
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        # Re-enable the start button.
        self.start_button.config(state=tk.NORMAL)
        # Re-enable the starting number entry.
        self.start_number_entry.config(state=tk.NORMAL)
        # Enable all radiobuttons in the settings frame.
        for child in self.settings_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=tk.NORMAL)
        # Disable the New Game button since no game is active.
        self.new_game_button.config(state=tk.DISABLED)
        # Disable the move buttons.
        self.btn2.config(state=tk.DISABLED)
        self.btn3.config(state=tk.DISABLED)
        self.btn4.config(state=tk.DISABLED)

    # Game loop function that periodically checks the game state.
    def game_loop(self):
        # If a game exists...
        if self.game:
            # And if the game is over, update the move buttons to disable them.
            if self.game.game_over:
                self.update_move_buttons()
        # Schedule this game_loop function to run again after 1000 milliseconds (1 second).
        self.master.after(1000, self.game_loop)


# The following code block runs when the script is executed directly.
if __name__ == "__main__":
    # Create the main Tkinter window.
    root = tk.Tk()
    # Create an instance of the GameGUI class with the main window as its parent.
    gui = GameGUI(root)
    # Start the Tkinter main event loop.
    root.mainloop()
