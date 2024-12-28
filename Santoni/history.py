"""
Define a history class here, which will keep track of the moves made by the players
then we can use the piece.reverse_build, piece.reserve_move, piece.build, piece.move to redo/undo

The history class will have a dictionary of the moves made by the players, where the key will be the turn number
"""

class History:
    def __init__(self):
        self.history = {}
    
    def add_turn(self, turn, piece, move, build):
        self.history[turn] = [piece, move, build]

    def add_piece(self, turn, piece):
        self.history[turn] = [piece]

    def add_move(self, turn, move):
        self.history[turn].append(move)

    def add_build(self, turn, build):
        self.history[turn].append(build)
    
    def undo(self, board, turn):
        if turn in self.history:
            piece, move, build = self.history[turn]
            piece.reverse_build(build, board)
            piece.reverse_move(move, board)
    
    def redo(self, board, turn):
        if turn in self.history:
            piece, move, build = self.history[turn]
            piece.move(move, board)
            piece.build(build, board)

    def delete_from_turn(self, turn):
        if self.history:
            max_turn = max(self.history.keys())
            for i in range(turn, max_turn+1):
                del self.history[i]




