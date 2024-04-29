"""
Define the base player class here,
will be inherited by the 1 human and 2 computer player classes like a Template Pattern
The player will have a color, while/blue, and 2 pieces, A/B or Y/Z

All players will be derived from the Player class, which is Template Pattern
1. Human Players, ask for input regarding the move and build
2. Computer Players Random Version, have a generated move and build
3. Computer Players Heuristic Version, have a generated move and build
"""

from observer import Observer
import random

class Player:
    def __init__(self, color, show_score=False):
        self.color = color
        self.pieces = []
        self.observer = Observer()
        self.directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
        self.show_score = show_score

    def __str__(self):
        return f'{self.color} ({self.pieces[0]}{self.pieces[1]})'
    
    def _return_piece(self, color):
        """
        Return the piece object based on the color
        """
        for piece in self.pieces:
            if piece.color == color:
                return piece
    
    def check_if_own_piece(self, piece):
        """
        Check if the piece belongs to the player
        """
        if self.color == 'white':
            return piece in ['A', 'B']
        else:
            return piece in ['Y', 'Z']
    
    def can_player_move(self, board):
        """
        Check if the piece can move in the given direction
        """
        return self.pieces[0].enumerate_all_moves(board) or self.pieces[1].enumerate_all_moves(board)

    def player_turn(self, board, opponent, history, turn):
        """
        This is the move and build function for the player that will be implemented by the subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def _calculate_height_score(self, board):
        """
        Calculate the height score for the player
        """
        score = 0
        for piece in self.pieces:
            score += board.grid[piece.row][piece.col].level
        return score
    
    def _calculate_center_score(self):
        """
        Calculate the center score for the player
        """
        score = 0
        for piece in self.pieces:
            score += piece.calculate_center_score()
        return score
    
    def _calculate_distance_score(self, opponent):
        """
        Calculate the distance score for the player,
        Diagonal distance is considered as 1, we canculate the minimum distance between the player's piece and the opponent's pieces
        We sum up all the minimum distances for all the opponent's pieces
        """
        score = 0
        for opponent_piece in opponent.pieces:
            distance_list = []
            for piece in self.pieces:
                distance = max(abs(opponent_piece.row - piece.row), abs(opponent_piece.col - piece.col))
                distance_list.append(distance)
            score += min(distance_list)     
        return 8-score

    def calculate_move_score(self, board, opponent):
        """
        Calculate the move score for the player
        """
        height_score = self._calculate_height_score(board)
        center_score = self._calculate_center_score()
        distance_score = self._calculate_distance_score(opponent)
        return [f'{height_score, center_score, distance_score}', 2*height_score + 1*center_score + 1.5*distance_score]

class HumanPlayer(Player):
    """
    Human player class, ask for input regarding the move and build
    """
    def __init__(self, color, show_score=False):
        super().__init__(color, show_score=show_score)
        self.type = 'human'

    def player_turn(self, board, opponent, history, turn):
        valid_worker= False
        while not valid_worker:
            ## Takes input about which piece to move and if this is a valid piece
            move_piece = input("Select a worker to move\n")
            if move_piece not in ['A', 'B', 'Y', 'Z']:
                self.observer.update("Not a valid worker")
                continue
            if not self.check_if_own_piece(move_piece):
                self.observer.update("That is not your worker")
                continue
            move_piece = self._return_piece(move_piece)
            if move_piece.enumerate_all_moves(board) == []:
                self.observer.update("That worker cannot move")
                continue
            valid_worker = True
        
        valid_move = False
        while not valid_move:
            ## Takes input about which direction to move and check if it is valid
            move_direction = input("Select a direction to move (n, ne, e, se, s, sw, w, nw)\n")
            if move_direction not in self.directions:
                self.observer.update("Not a valid direction")
                continue
            if not move_piece.check_if_can_move(move_direction, board):
                self.observer.update(f"Cannot move {move_direction}")
                continue

            ## Execute the move
            move_piece.move(move_direction, board)
            valid_move = True

        valid_build = False
        while not valid_build:
            ## Takes input about which direction to build and check if it is valid
            build_direction = input("Select a direction to build (n, ne, e, se, s, sw, w, nw)\n")
            if build_direction not in self.directions:
                self.observer.update("Not a valid direction")
                continue
            if not move_piece.check_if_can_build(build_direction, board):
                self.observer.update(f"Cannot build {build_direction}")
                continue
            move_piece.build(build_direction, board)
            valid_build = True
        
        if self.show_score:
            self.observer.update(f"{move_piece},{move_direction},{build_direction} {self.calculate_move_score(board, opponent)[0]}")
        else:
            self.observer.update(f"{move_piece},{move_direction},{build_direction}")
        
        history.add_turn(turn, move_piece, move_direction, build_direction)

class RandomComputerPlayer(Player):
    """
    Random computer player class, have a randomly generated move and build
    """
    def __init__(self, color, show_score=False):
        super().__init__(color, show_score)
        self.type = 'random'

    def player_turn(self, board, opponent, history, turn):
        valid_move = False
        while not valid_move:
            ## Randomly select a piece to move
            move_piece = random.choice(self.pieces)
            if move_piece.enumerate_all_moves(board) == []:
                continue
            move_direction = random.choice(move_piece.enumerate_all_moves(board))
            move_piece.move(move_direction, board)
            valid_move = True

        valid_build = False
        while not valid_build:
            ## Randomly select a direction to build
            build_direction = random.choice(move_piece.enumerate_all_builds(board))
            move_piece.build(build_direction, board)
            valid_build = True

        if self.show_score:
            self.observer.update(f"{move_piece},{move_direction},{build_direction} {self.calculate_move_score(board, opponent)[0]}")
        else:
            self.observer.update(f"{move_piece},{move_direction},{build_direction}")

        history.add_turn(turn, move_piece, move_direction, build_direction)

class HeuristicComputerPlayer(Player):
    """
    Heuristic computer player class, have a generated move and build based on score calculation
    height_score: sum of heights of all pieces a player's pieces stand on
    center_score: center: 2, ring around center: 1, edge: 0
    distance_score: sum of minimum distance to opponent's pieces. Example: 8 - min(Z to A, Y to A) - min(Z to B, Y to B)
    move_score = 2*height_score + 1*center_score + 1.5*distance_score

    The Heuristic Computer Player will move the piece to a direction that maximizes the move_score

    If any move can place the piece on the third level, the player will ignore move score
    """
    def __init__(self, color, show_score=False):
        super().__init__(color, show_score)
        self.type = 'heuristic'
    
    def player_turn(self, board, opponent, history, turn):
        """
        The Heuristic Computer Player will move the piece to a direction
            1. Place it on the third level if possible
            2. that maximizes the move_score
        """
        ## Find if any pieces's any possible direction correspond to the third level
        for piece in self.pieces:
            for direction in piece.enumerate_all_moves(board):
                if board.grid[piece.row + piece.direction_dic[direction][0]][piece.col + piece.direction_dic[direction][1]].level == 3:
                    piece.move(direction, board)
        
        ## If no piece can be placed on the third level, then calculate the move score by moving and redoing the move
        move_scores = []
        for piece in self.pieces:
            for direction in piece.enumerate_all_moves(board):
                piece.move(direction, board)
                move_scores.append([piece, direction, self.calculate_move_score(board, opponent)[1]])
                piece.reverse_move(direction, board)
        
        ## Select the move with the highest score
        move_scores.sort(key=lambda x: x[2], reverse=True)
        piece, move_direction, _ = move_scores[0]
        piece.move(move_direction, board)
                    
        ## Randomly build in any direction
        build_direction = random.choice(piece.enumerate_all_builds(board))
        piece.build(build_direction, board)

        if self.show_score:
            self.observer.update(f"{piece},{move_direction},{build_direction} {self.calculate_move_score(board, opponent)[0]}")
        else:
            self.observer.update(f"{piece},{move_direction},{build_direction}")

        history.add_turn(turn, piece, move_direction, build_direction)

    