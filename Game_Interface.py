# game interface

import tkinter as tk
from tkinter import messagebox

# Création de la fenêtre
root = tk.Tk()
root.title("Jeu de Multiplication")
root.attributes("-fullscreen", True)  # Plein écran
root.configure(bg="#EAEDED")  # Fond inspiré de l'image

# Variables globales
number_var = tk.IntVar(value=0)
player_score = 0
bank = 0

def start_game():
    global player_score, bank
    player_score = 0
    bank = 0
    selected_number = number_var.get()
    if selected_number == 0:
        messagebox.showwarning("Avertissement", "Veuillez choisir un nombre entre 8 et 18.")
    else:
        game_label.config(text=f"{selected_number}")
        update_scoreboard()

def update_number(value):
    number_var.set(value)

def multiply(factor):
    global player_score, bank
    current_number = number_var.get()
    new_number = current_number * factor
    number_var.set(new_number)
    update_score(new_number)
    game_label.config(text=f"{new_number}")
    if new_number >= 1200:
        end_game()

def update_score(number):
    global player_score, bank
    if number % 2 == 0:
        player_score -= 1
    else:
        player_score += 1
    if number % 5 == 0:
        bank += 1
    update_scoreboard()

def update_scoreboard():
    score_label.config(text=f"Score: {player_score}")
    bank_label.config(text=f"Banque: {bank}")

def end_game():
    global player_score
    player_score += bank
    messagebox.showinfo("Fin de la partie", f"Jeu terminé! Score final: {player_score}")
    root.quit()

# Conteneur principal
game_frame = tk.Frame(root, bg="#D6DBDF")
game_frame.pack(fill=tk.BOTH, expand=True)

# Sélection du nombre de départ
number_frame = tk.Frame(game_frame, bg="#D6DBDF")
number_frame.pack(pady=20)
for num in range(8, 19):
    if num in [8, 11, 14, 17]:
        bg_color = "#D5DBDB"  # Beige
    elif num in [9, 12, 15, 18]:
        bg_color = "#F1C40F"  # Jaune
    else:
        bg_color = "#5D6D7E"  # Bleu plus clair

    btn = tk.Button(number_frame, text=str(num), font=("Arial", 20, "bold"), width=4, height=2, bg=bg_color, fg="black", command=lambda n=num: update_number(n))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Zone de jeu
game_label = tk.Label(game_frame, text="0", font=("Arial", 60, "bold"), bg="#D6DBDF", fg="#2C3E50")
game_label.pack(pady=15)

# Bouton Start (en bleu)
start_button = tk.Button(game_frame, text="START GAME", font=("Arial", 24, "bold"), bg="#3498db", fg="white", width=20, height=2, command=start_game)
start_button.pack(pady=20)

# Boutons de multiplication (de plus en plus foncé)
multiplication_frame = tk.Frame(game_frame, bg="#D6DBDF")
multiplication_frame.pack()
for factor, color in zip([2, 3, 4], ["#A3E4D7", "#58D68D", "#28B463"]):
    btn = tk.Button(multiplication_frame, text=f"x{factor}", font=("Arial", 20, "bold"), width=6, height=2, bg=color, fg="black", command=lambda f=factor: multiply(f))
    btn.pack(side=tk.LEFT, padx=20, pady=10)

# Affichage des scores (en bleu foncé)
score_label = tk.Label(game_frame, text="Score: 0", font=("Arial", 22, "bold"), bg="#D6DBDF", fg="#2C3E50")
score_label.pack(pady=15)

# Affichage de la banque (en vert)
bank_label = tk.Label(game_frame, text="Banque: 0", font=("Arial", 22, "bold"), bg="#D6DBDF", fg="#28B463")
bank_label.pack(pady=10)

# Quitter avec Échap
def exit_fullscreen(event):
    root.attributes('-fullscreen', False)
root.bind("<Escape>", exit_fullscreen)

root.mainloop()
