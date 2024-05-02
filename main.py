"""
1. Display the board as a grid of buttons (DONE)
    - The buildings and workers. (DONE)
    - The levels of the building should be shown visually and the worker should be shown standing on the building. (DONE)
2. Include buttons corresponding to next/undo/redo if enabled.  (DONE)
3. Human players should be able to select a worker to move by clicking on one of their spaces. (DONE)
4. Only allow the player to click on a worker that has legal moves. (DONE)
5. Available moves and builds should be highlighted visually on the board. (DONE)
6. The user should select their move and build by clicking on the highlighted spaces. (DONE)
7. If enabled the heuristic board score should be shown somewhere in the GUI and updated each turn. (DONE)
8. The winner of the game should be indicated visually in the GUI. (DONE)
9. GUI presents option to play again and resets everything properly. (DONE)
"""

"""
References:
The img folder contains the images for the pieces and the buildings, which were taken from the following link:
https://github.com/tjl0005/Santorini-Boardgame/tree/main/GUI%20Version/assets
"""

from board import Board
from player import HumanPlayer, RandomComputerPlayer, HeuristicComputerPlayer 
from piece import Piece
from history import History

import tkinter as tk
from tkinter import messagebox

import argparse

class SantoriniGUI():
    """
    GUI for the game
    """
    def __init__(self, game):
        ## Do not allow the user to resize the window
        self.game = game
        self.root = tk.Tk()
        self.root.resizable(False, False) 
        self.root.title("Santorini")
        self.root.geometry("525x650")
        self.loop()
        self.root.mainloop()

    def loop(self):
        """
        Part 1. Display Turn, Player, and Score, if enabled on top of the board
        Part 2. Add Next, Undo, Redo buttons if enabled
        Part 3. Board
        Each tile is a label with img/l0.png, img/l1.png, img/l2.png, img/l3.png, img/l4.png
        """

        ## Destroy everything
        for widget in self.root.winfo_children():
            widget.destroy()

        ## Display the turn, player, and score
        self._display_turn_player_score()

        ## Add Next, Undo, Redo buttons if enabled
        if self.game.undo_redo:
            text = f"Click Next to continue"
            hint_next = tk.Label(self.root, text=text, font=("Arial", 20))
            hint_next.grid(row=8, column=0, columnspan=5)
            next_button = tk.Button(self.root, text="Next", command = self._next_clicked)
            next_button.grid(row=1, column=1)

            ## Check if undo is possible
            if self.game.turn > 1:
                undo_button = tk.Button(self.root, text="Undo", command = self._undo_clicked)
            else:
                undo_button = tk.Button(self.root, text="Undo", state='disabled')
            undo_button.grid(row=1, column=2)
            
            ## Check if redo is possible
            if self.game.turn <= len(self.game.history.history):
                redo_button = tk.Button(self.root, text="Redo", command = self._redo_clicked)
            else:
                redo_button = tk.Button(self.root, text="Redo", state='disabled')
            redo_button.grid(row=1, column=3)

        else:
            text = "Undo/Redo is disabled"
            undo_redo = tk.Label(self.root, text=text, font=("Arial", 20))
            undo_redo.grid(row=1, column=1, columnspan=3)

        ## Show previous moves
        if self.game.turn > 1:
            prev_piece, prev_move, prev_build = self.game.history.history[self.game.turn-1]
            prev_piece = prev_piece.color
            text = f"Previous Moves: {prev_piece}, {prev_move}, {prev_build}"
            opponent = self.game.player2 if self.game.current_player == self.game.player1 else self.game.player1
            if opponent.show_score:
                score = opponent.calculate_move_score(self.game.game_board, self.game.current_player)[0]
                text += f", Score: {score}"
            prev_moves = tk.Label(self.root, text=text, font=("Arial", 20))
            prev_moves.grid(row=9, column=0, columnspan=5)

        self._refresh_board()
        self._print_piece()
        ## If current player is a human player, then display the board, wait for action
        if not self.game.undo_redo:
            if self.game.current_player.type == 'human':
                self._create_piece_button()
            else:
                self._computer_turn()

        ## Check if the game has ended
        message = self.game.check_game_end()
        if message is not None:
            reset = messagebox.askquestion("Game Over", message + " Do you want to play again?")
            if reset == 'yes':
                self.game.reset_game()
                self.loop()
            else:
                self.root.destroy()
    
    def _computer_turn(self):
        """
        Computer turn, calculate the move and build
        """
        self._refresh_board()
        opponent = self.game.player2 if self.game.current_player == self.game.player1 else self.game.player1
        piece, move_direction = self.game.current_player.player_move(self.game.game_board, opponent)
        build_direction = self.game.current_player.player_build(self.game.game_board, piece)
        self.game.history.add_turn(self.game.turn, piece, move_direction, build_direction)
        self.game.turn += 1
        self.game.switch_player()
        self.loop()

    def _refresh_board(self):
        """
        Refresh the board
        """
        self._destroy_board()
        for row in self.game.game_board.grid:
            for tile in row:
                self._create_tile_for_background(tile)
    
    def _create_piece_button(self):
        """
        create all buttons for the pieces
        """
        self._refresh_board()
        for piece in self.game.pieces_dict.values():
            self._create_piece(piece, piece.row, piece.col)

        self._destroy_text()
        text = "Select the piece to move"
        select_piece = tk.Label(self.root, text=text, font=("Arial", 20))
        select_piece.grid(row=8, column=0, columnspan=5)

    def _refresh_board_for_action(self, piece, action):
        """
        Refresh the board after a piece is selected to make all direction not possible for move 'img/no.png' 
        Make all the possible moves clickable with img/l{level}.png
        """
        self._destroy_board()

        if action == 'move':
            directions = piece.enumerate_all_moves(self.game.game_board)
        elif action == 'build':
            directions = piece.enumerate_all_builds(self.game.game_board)

        for row in self.game.game_board.grid:
            for tile in row:
                ## if tile is in the possible move, then create a clickable tile ## resize to 100x100
                if (tile.row - piece.row, tile.col - piece.col) in [self.game.direction_dic[direction] for direction in directions]:
                    img = tk.PhotoImage(file=f"img/l{tile.level}.png")
                    img.config(width=95, height=95)
                    direction = self.game.reverse_direction_dic[(tile.row - piece.row, tile.col - piece.col)]

                    if action == 'move':
                        command = lambda d=direction, p=piece: self._move_clicked(p, d)
                    elif action == 'build':
                        command = lambda d=direction, p=piece: self._build_clicked(p, d)

                    button = tk.Button(self.root, image=img, command = command)
                    button.image = img
                    button.grid(row=tile.row+2, column=tile.col)
                else:
                    img = tk.PhotoImage(file="img/no.png")
                    img.config(width=100, height=100)
                    label = tk.Label(self.root, image=img)
                    label.image = img
                    label.grid(row=tile.row+2, column=tile.col)
                
        self._print_piece()
        
        ## Display Text for the player to select the move
        self._destroy_text()
        text = f"Select the {action} for {piece.color}"
        select_move = tk.Label(self.root, text=text, font=("Arial", 20))
        select_move.grid(row=8, column=0, columnspan=5)

    def _print_piece(self):
        """
        Print the piece on the board
        """
        for row in self.game.game_board.grid:
            for tile in row:
                if tile.piece is not None:
                    text = tile.piece.color
                    color = tile.piece.player.color
                    button = tk.Label(self.root, text=text, bg=color)
                    button.config(width=5, height=2, font=("Arial", 20, "bold"))
                    button.grid(row=tile.row+2, column=tile.col)
        
    def _destroy_board(self):
        """
        Destroy everything from row 2 and row 7
        """
        for widget in self.root.winfo_children():
            if int(widget.grid_info()['row']) >= 2 and int(widget.grid_info()['row']) <= 7:
                widget.destroy()
    
    def _destroy_text(self):
        """
        Destroy everything from row 8
        """
        for widget in self.root.winfo_children():
            if int(widget.grid_info()['row']) == 8:
                widget.destroy()

    def _create_tile_for_background(self, tile):
        """
        Create a tile on the board, all tile as labels with img/l{level}.png
        ## Size of the image is 100x100, placed at corresponding row and column
        """
        img = tk.PhotoImage(file=f"img/l{tile.level}.png")
        img.config(width=100, height=100)
        label = tk.Label(self.root, image=img)
        label.image = img
        label.grid(row=tile.row+2, column=tile.col)
         
    def _create_piece(self, piece, row, col):
        """
        Create a piece as a circle button with corresponding name: A, B, Y, Z
        Make the piece a clicable button if it is the current player's turn
        Makes button/label circle with radius 25
        """
        text = piece.color
        color = piece.player.color
        ## Only makes the piece clickable if it is the current player's turn + the piece can move
        if self.game.current_player == piece.player and piece.enumerate_all_moves(self.game.game_board):
            button = tk.Button(self.root, text=text, bg=color, highlightbackground=color,
                               command=lambda p=piece: self._piece_clicked(p))
        else:
            button = tk.Label(self.root, text=text, bg=color, highlightbackground=color)
        button.config(width=5, height=2, font=("Arial", 20, "bold"))
        button.grid(row=row+2, column=col)

    def _display_turn_player_score(self):
        """
        Display the turn, player, and score on top of the board
        """
        opponent = self.game.player2 if self.game.current_player == self.game.player1 else self.game.player1
        text = f"Turn: {self.game.turn}, {self.game.current_player}, Score: "

        if self.game.current_player.show_score:
            score, _ = self.game.current_player.calculate_move_score(self.game.game_board, opponent)
        else: 
            score = "N/A"
        turn_player_score = tk.Label(self.root, text=text+score, font=("Arial", 20))
        turn_player_score.grid(row=0, column=0, columnspan=5)
    
    def _piece_clicked(self, piece):
        """
        When the piece is clicked, highlight all the possible move
        """
        self._refresh_board_for_action(piece, 'move')
        self.game.history.add_piece(self.game.turn, piece)

    def _move_clicked(self, piece, direction):
        """
        When the move is clicked, highlight all the possible build
        """
        piece.move(direction, self.game.game_board)
        self._refresh_board_for_action(piece, 'build')
        self.game.history.add_move(self.game.turn, direction)
    
    def _build_clicked(self, piece, direction):
        """
        When the build is clicked, update the board and refresh the board
        """
        piece.build(direction, self.game.game_board)
        self.game.history.add_build(self.game.turn, direction)
        self.game.switch_player()
        self.game.turn += 1
        self.loop()

    def _undo_clicked(self):
        """
        Undo the move
        """
        self.game.history.undo(self.game.game_board, self.game.turn-1)
        self.game.turn -= 1
        self.game.switch_player()
        print(self.game.turn, self.game.history.history)
        self.loop()

    def _redo_clicked(self):
        """
        Redo the move
        """
        self.game.history.redo(self.game.game_board, self.game.turn)
        print(self.game.turn, self.game.history.history)
        self.game.switch_player()
        self.game.turn += 1
        self.loop()
    
    def _next_clicked(self):
        """
        Next move
        """
        if self.game.current_player.type == 'human':
            self._create_piece_button()
        else:
            self._computer_turn()
        self.game.history.delete_from_turn(self.game.turn)


class Game():
    """
    Play the entire game. Initializes Board, Players, and Pieces
    """
    def __init__(self, player1_name = 'white', player2_name = 'blue', 
                 player1_type = 'human', player2_type = 'human', 
                 show_score=False, undo_redo=False):
        self.continue_game = True
        self.undo_redo = undo_redo
        self.history = History()

        ## Initialize the players based on the player type
        if player1_type == 'human':
            self.player1 = HumanPlayer(player1_name, show_score=show_score)
        elif player1_type == 'random':
            self.player1 = RandomComputerPlayer(player1_name, show_score=show_score)
        elif player1_type == 'heuristic':
            self.player1 = HeuristicComputerPlayer(player1_name, show_score=show_score)
        
        if player2_type == 'human':
            self.player2 = HumanPlayer(player2_name, show_score=show_score)
        elif player2_type == 'random':
            self.player2 = RandomComputerPlayer(player2_name, show_score=show_score)
        elif player2_type == 'heuristic':
            self.player2 = HeuristicComputerPlayer(player2_name, show_score=show_score)

        self.current_player = self.player1
        self.game_board = Board()
        self._initialize_pieces()
        self.turn = 1

        self.direction_dic = {
                'n': (-1, 0),
                'ne': (-1, 1),
                'e': (0, 1),
                'se': (1, 1),
                's': (1, 0),
                'sw': (1, -1),
                'w': (0, -1),
                'nw': (-1, -1)
        }

        self.pieces_dict = {
            'A': self.player1.pieces[0],
            'B': self.player1.pieces[1],
            'Y': self.player2.pieces[0],
            'Z': self.player2.pieces[1]
        }

        self.reverse_direction_dic = {
            (-1, 0): 'n',
            (-1, 1): 'ne',
            (0, 1): 'e',
            (1, 1): 'se',
            (1, 0): 's',
            (1, -1): 'sw',
            (0, -1): 'w',
            (-1, -1): 'nw'
        }

    def _initialize_pieces(self):
        """
        Initialize the pieces for each player and place them on the board by default
        """
        self.player1.pieces = [Piece('A', self.player1), Piece('B', self.player1)]
        self.player2.pieces = [Piece('Y', self.player2), Piece('Z', self.player2)]

        # Place the workers on the board
        self.game_board.grid[1][1].update(piece=self.player2.pieces[0])
        self.game_board.grid[1][3].update(piece=self.player1.pieces[1])
        self.game_board.grid[3][1].update(piece=self.player1.pieces[0])
        self.game_board.grid[3][3].update(piece=self.player2.pieces[1])

        ## Update the pieces with their current position
        self.player1.pieces[0].update_position(3, 1)
        self.player1.pieces[1].update_position(1, 3)
        self.player2.pieces[0].update_position(1, 1)
        self.player2.pieces[1].update_position(3, 3)
    

    def switch_player(self):
        """
        Switch the current player
        """
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def check_game_end(self):
        """
        Check if the game has ended.
        """
        if not self.current_player.can_player_move(self.game_board):
            self.continue_game = False
            opponent = self.player2 if self.current_player == self.player1 else self.player1
            message =  f"{self.current_player} cannot move, {opponent} wins!"
            return message
  
        winner = self.game_board.check_winner()
        if winner is not None:
            self.continue_game = False
            message = f"{winner} wins!"
            return message

        return None
        
    def reset_game(self):
        """
        Reset the game
        """
        self.game_board = Board()
        self._initialize_pieces()
        self.turn = 1
        self.continue_game = True
        self.current_player = self.player1

def parse_args():
    """
    Parse the arguments for the game
    """
    parser = argparse.ArgumentParser(description='Play Santorini')
    parser.add_argument('player1', type=str, default='human', 
                        choices = ['human', 'random', 'heuristic'],
                        help='Type of player 1')
    parser.add_argument('player2', type=str, default='human', 
                        choices = ['human', 'random', 'heuristic'],
                        help='Type of player 2')
    parser.add_argument('undo_redo', type = str, default='off',
                        choices = ['on', 'off'],
                        help='enable undo/redo')
    parser.add_argument('show_score', type = str, default='off',
                        choices = ['on', 'off'],
                        help='enable score display')
    
    args = parser.parse_args()

    ## Convert the strings to boolean
    args.undo_redo = True if args.undo_redo == 'on' else False
    args.show_score = True if args.show_score == 'on' else False

    return args

if __name__ == '__main__':
    args = parse_args()
    game = Game(player1_type = args.player1, 
                player2_type = args.player2, 
                undo_redo = args.undo_redo, 
                show_score= args.show_score)
    
    gui = SantoriniGUI(game)
