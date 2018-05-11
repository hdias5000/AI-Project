'''
GROUP NAME:
    algorizma
WRITTEN BY:
    Hasitha Dias: 789929
    Rishab Garg: 796799
LAST MODIFIED DATE:
    11/05/2018
'''

class Node:
    def __init__(self, board, move):
        self.weight = 0
        self.move = move
        self.board = board
        self.pieces = {"W": self.fill_child("W"), "B": self.fill_child("B")}

    def fill_child(self, piece):
        """
        Finds all positions of given piece in the board.

        :param piece: piece value
        :return: list of positions of piece
        """
        piece_position = []
        for i in range(0, 8):
            for j in range(0, 8):
                if (self.board.board[j][i] == piece):
                    piece_position.append((i, j))
        return piece_position