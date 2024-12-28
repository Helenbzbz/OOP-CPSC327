"""
Defines the piece class,
has attributes of color: Y/B/A/Z, its basic __str__
This follows Command pattern, as
it will have the following functions: 
    1. Check if can move
    2. Check if can build
    3. Move
    4. Build
    5. Enumerate all moves
    6. Enumerate all builds
    7. Calculate center score
    8. Reverse move
    9. Reverse build
"""

class Piece:
    def __init__(self, color, player):
        self.color = color
        self.col = None
        self.row = None
        self.player = player

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

    def __str__(self):
        return self.color
    
    def update_position(self, row, col):
        self.row = row
        self.col = col

    def check_if_can_move(self, direction, board):
        """
        Check if the piece can move in the given direction
        """
        row, col = self.direction_dic[direction]
        if self.row + row < 0 or self.row + row > 4 or self.col + col < 0 or self.col + col > 4:
            return False
        if board.grid[self.row + row][self.col + col].piece is not None:
            return False
        if board.grid[self.row + row][self.col + col].level - board.grid[self.row][self.col].level > 1:
            return False
        return True
    
    def check_if_can_build(self, direction, board):
        """
        Check if the piece can build in the given direction
        """
        row, col = self.direction_dic[direction]
        if self.row + row < 0 or self.row + row > 4 or self.col + col < 0 or self.col + col > 4:
            return False
        if board.grid[self.row + row][self.col + col].piece is not None:
            return False
        if board.grid[self.row + row][self.col + col].level == 4:
            return False
        return True

    def enumerate_all_moves(self, board):
        """
        Enumerate all possible moves for the piece
        """
        directions = []
        for direction in self.direction_dic.keys():
            if self.check_if_can_move(direction, board):
                directions.append(direction)
        return directions
    
    def enumerate_all_builds(self, board):
        """
        Enumerate all possible builds for the piece
        """
        directions = []
        for direction in self.direction_dic.keys():
            if self.check_if_can_build(direction, board):
                directions.append(direction)
        return directions

    def move(self, direction, board):
        """
        Execute the move
        """
        row, col = self.direction_dic[direction]
        board.grid[self.row][self.col].update(piece=None)
        self.update_position(self.row + row, self.col + col)
        board.grid[self.row][self.col].update(piece=self)
    
    def build(self, direction, board):
        """
        Execute the build
        """
        row, col = self.direction_dic[direction]
        board.grid[self.row + row][self.col + col].level += 1
    
    def calculate_center_score(self):
        """
        Calculate the center score for the piece
        """
        if self.row == 2 and self.col == 2:
            return 2
        elif self.row == 1 or self.row == 3 or self.col == 1 or self.col == 3:
            return 1
        else:
            return 0
    
    def reverse_move(self, direction, board):
        """
        Reverse the move
        """
        row, col = self.direction_dic[direction]
        board.grid[self.row][self.col].update(piece=None)
        self.update_position(self.row - row, self.col - col)
        board.grid[self.row][self.col].update(piece=self)
    
    def reverse_build(self, direction, board):
        """
        Reverse the build
        """
        row, col = self.direction_dic[direction]
        board.grid[self.row + row][self.col + col].level -= 1
