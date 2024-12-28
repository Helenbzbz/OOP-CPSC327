"""
Define the board class here, which is composed of 25 Tile objects
The tile will be defined under singleton pattern, so that only one board is created
Each tile object will have col index, row index, level, and if there is a player
"""

class Tile:
    def __init__(self, row, col, level=0, piece=None):
        self.row = row
        self.col = col
        self.level = level
        self.piece = piece
        self.clickable = False

    def __str__(self):
        piece = self.piece if self.piece else ' '
        return f"{self.level}{piece}"

    def update(self, level=None, piece=None):
        if level is not None:
            self.level = level
        if piece is not None:
            self.piece = piece
        if piece is None:
            self.piece = None

class Board:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Board, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        self.grid = [[Tile(row, col) for col in range(5)] for row in range(5)]
    
    def check_winner(self):
        """
        Check if there is a winner
        """
        for row in self.grid:
            for tile in row:
                if tile.level == 3 and tile.piece is not None:
                    return tile.piece.player
        return None
    

    