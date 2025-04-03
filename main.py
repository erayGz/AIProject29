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
