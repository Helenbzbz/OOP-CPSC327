"""
Requirements
1. 5x5 board (Singleton Pattern to ensure only one board (DONE)
2. 2 human players: 
    a. A, B, Y, Z; else print 'Not a valid worker' (DONE)
    b. If entered opponent worker, print 'That is not your worker' (DONE)
    c. n, ne, e, se, s, sw, w, nw; else print 'Not a valid direction' (DONE)
    d. If invalid direction, 'Cannot move <direction>' (DONE)
    --> Repeat prompt until valid input
    e. Print the mover, move direction, and build direction (DONE)
    
3. Check if game has eneded, if a player is on the third level (DONE)
4. Check if current player can move through enumerating all possible moves (DONE)
5. If game ended, print the winner, if a worker can't move, print 'That worker cannot move' (DONE)
--> Observer Pattern will contains the above 3 requirements

6. 2 Random Computer Players (DONE)
7. 2 Heuristic Players (DONE)
8. Undo/Redo Functions --> memento pattern

--> All players will be derived from the Player class, which is Template Pattern (DONE)
"""

from board import Board
from player import HumanPlayer, RandomComputerPlayer, HeuristicComputerPlayer 
from piece import Piece
from observer import Observer
from history import History

import argparse

class Game():
    """
    Play the entire game. Initializes Board, Players, and Pieces
    """
    def __init__(self, player1_name = 'white', player2_name = 'blue', player1_type = 'human', player2_type = 'human', show_score=False, undo_redo=False):
        self.observer = Observer()
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

    def main_loop(self):
        """
        Main game loop, will continue until the game is over
        """
        while self.continue_game:
            self.observer.update(self.game_board)

            ## if current_player.show_score, then add score to the update message
            opponent = self.player2 if self.current_player == self.player1 else self.player1
            if self.current_player.show_score:
                score, _ = self.current_player.calculate_move_score(self.game_board, opponent)
                self.observer.update(f"Turn: {self.turn}, {self.current_player}, "+score)
            else: 
                self.observer.update(f"Turn: {self.turn}, {self.current_player}")
            

            self.check_game_end()
            ## Reset the game if the game is over and prompt the user
            if not self.continue_game:
                reset = input("Play again?\n")
                if reset == 'yes':
                    self.game_board = Board()
                    self._initialize_pieces()
                    self.turn = 1
                    self.continue_game = True
                    self.current_player = self.player1
                else:
                    break
            
            ## Check undo/redo
            if self.undo_redo:
                undo_redo = input("undo, redo, or next\n")
                if undo_redo == 'undo' and self.turn > 1:
                    self.history.undo(self.game_board, self.turn-1)
                    self.turn -= 1
                    self._switch_player()
                    continue
                elif undo_redo == 'redo' and self.turn <= len(self.history.history):
                    self.history.redo(self.game_board, self.turn)
                    self.turn += 1
                    self._switch_player()
                    continue
                elif undo_redo == 'next':
                    self.history.delete_from_turn(self.turn)
                    self._player_turn(opponent)
            else:
                self._player_turn(opponent)
    
    def _player_turn(self, opponent):
        ## if this player is heuristic, then calculate the move and build
        if self.current_player.type == 'heuristic':
            self.current_player.player_turn(self.game_board, opponent, self.history, self.turn)
        else:
            self.current_player.player_turn(self.game_board, opponent, self.history, self.turn)
        self.turn += 1
        self._switch_player()

    def _switch_player(self):
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
            self.observer.update(f"{self.current_player.color} cannot move")
            self.continue_game = False

        winner = self.game_board.check_winner()
        if winner is not None:
            self.observer.update(f"{winner.color} has won")
            self.continue_game = False

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
    game = Game(player1_type=args.player1, 
                player2_type=args.player2, 
                undo_redo=args.undo_redo, 
                show_score=args.show_score)
    game.main_loop()
