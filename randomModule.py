from random import randint


class Board:
    def __init__(self, board=None):
        self.board = [['-' for _ in range(8)] for _ in range(8)]
        for square in [(0, 0), (7, 0), (7, 7), (0, 7)]:
            x, y = square
            self.board[y][x] = 'X'
        self.n_shrinks = 0

        # tracking progress through game phases
        self.turns = 0
        self.phase = 'placing'
        self.pieces = {'W': 0, 'B': 0}

    _DISPLAY = {'B': '@', 'W': 'O', 'X': 'X', '-': '-', ' ': ' '}

    def __str__(self):
        """String representation of the current game state."""
        displayboard = [[Board._DISPLAY[p] for p in row] for row in self.board]
        board = '\n'.join(' '.join(row) for row in displayboard)
        if self.playing():
            progress = f'{self.turns} turns into the {self.phase} phase'
        else:
            progress = 'game over!'
        return f'{board}\n{progress}'

    def playing(self):
        """:return: True iff the game is still in progress"""
        return self.phase == 'placing' or self.phase == 'moving'

    def _within_board(self, x, y):
        """
        Check if a given pair of coordinates is 'on the board'.

        :param x: column value
        :param y: row value
        :return: True iff the coordinate is on the board
        """
        for coord in [y, x]:
            if coord < 0 or coord > 7:
                return False
        if self.board[y][x] == ' ':
            return False
        return True

    def _shrink_board(self):
        """
        Shrink the board, eliminating all pieces along the outermost layer,
        and replacing the corners.

        This method can be called up to two times only.
        """
        s = self.n_shrinks  # number of shrinks so far, or 's' for short
        # Remove edges
        for i in range(s, 8 - s):
            for square in [(i, s), (s, i), (i, 7 - s), (7 - s, i)]:
                x, y = square
                piece = self.board[y][x]
                if piece in self.pieces:
                    self.pieces[piece] -= 1
                self.board[y][x] = ' '

        # we have now shrunk the board once more!
        self.n_shrinks = s = s + 1

        # replace the corners (and perform corner elimination)
        for corner in [(s, s), (s, 7 - s), (7 - s, 7 - s), (7 - s, s)]:
            x, y = corner
            piece = self.board[y][x]
            if piece in self.pieces:
                self.pieces[piece] -= 1
            self.board[y][x] = 'X'
            self._eliminate_about(corner)

    def _targets(self, piece):
        """
        Which pieces can a piece of this type eliminate?

        :param piece: the type of piece ('B', 'W', or 'X')
        :return: the set of piece types that a piece of this type can eliminate
        """
        if piece == 'B':
            return {'W'}
        elif piece == 'W':
            return {'B'}
        elif piece == 'X':
            return {'B', 'W'}
        return set()

    def _eliminate_about(self, square):
        """
        A piece has entered this square: look around to eliminate adjacent
        (surrounded) enemy pieces, then possibly eliminate this piece too.

        :param square: the square to look around
        """
        x, y = square
        piece = self.board[y][x]
        targets = self._targets(piece)

        # Check if piece in square eliminates other pieces
        for dx, dy in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_x, target_y = x + dx, y + dy
            targetval = None
            if self._within_board(target_x, target_y):
                targetval = self.board[target_y][target_x]
            if targetval in targets:
                if self._surrounded(target_x, target_y, -dx, -dy):
                    self.board[target_y][target_x] = '-'
                    self.pieces[targetval] -= 1

        # Check if the current piece is surrounded and should be eliminated
        if piece in self.pieces:
            if self._surrounded(x, y, 1, 0) or self._surrounded(x, y, 0, 1):
                self.board[y][x] = '-'
                self.pieces[piece] -= 1

    def _surrounded(self, x, y, dx, dy):
        """
        Check if piece on (x, y) is surrounded on (x + dx, y + dy) and
        (x - dx, y - dy).

        :param x: column of the square to be checked
        :param y: row of the square to be checked
        :param dx: 1 if adjacent cols are to be checked (dy should be 0)
        :param dy: 1 if adjacent rows are to be checked (dx should be 0)
        :return: True iff the square is surrounded
        """
        xa, ya = x + dx, y + dy
        firstval = None
        if self._within_board(xa, ya):
            firstval = self.board[ya][xa]

        xb, yb = x - dx, y - dy
        secondval = None
        if self._within_board(xb, yb):
            secondval = self.board[yb][xb]

        # If both adjacent squares have enemies then this piece is surrounded!
        piece = self.board[y][x]
        enemies = self._enemies(piece)
        return (firstval in enemies and secondval in enemies)

    def _enemies(self, piece):
        """
        Which pieces can eliminate a piece of this type?

        :param piece: the type of piece ('B', 'W', or 'X')
        :return: set of piece types that can eliminate a piece of this type
        """
        if piece == 'B':
            return {'W', 'X'}
        elif piece == 'W':
            return {'B', 'X'}
        return set()

    def _get_all_pieces(self, piece):
        # returns all the pieces of the board of type piece
        pieces = []
        for i in range(8):
            for j in range(8):
                if (self.board[j][i] == piece):
                    pieces.append((i, j))
        return pieces


class Player:

    def __init__(self, colour):

        self.player = colour
        self.board = Board()
        self.player_position = []
        self.place_turns = 0
        self.move_turns = -1

        if (colour == "white"):
            self.player = "W"
            self.opponent = "B"
        else:
            self.player = "B"
            self.opponent = "W"

    def action(self, turns):
        self.board.turns = turns  # the current number of turn excluding the turn which we will take now.
        if (self.board.phase == "placing" and self.place_turns != 0 and turns == 0):
            self.board.phase = 'moving'

        if (self.board.phase == 'placing'):
            # make sure this placing turn is counted one is counted
            self.place_turns += 1
            move_action = self._place()

            if (turns == 23):
                self.board.phase = "moving"

            return move_action

        if (self.board.phase == 'moving'):
            if (turns == 128 or turns == 192):
                self.board._shrink_board();

                self.player_list_update()

            # count this as your turn and then shrink

            moved_piece_direction = self._move()

            # ready for next turn
            if (turns == 127 or turns == 191):
                self.board._shrink_board();

                self.player_list_update()

            return moved_piece_direction

    def _move(self):
        # random move, with each move either kill opponent or check if you get kill by opponent

        piece = self.player

        length = len(self.player_position)
        i = 0
        while (i < length):

            (x, y) = self.player_position[i]
            new_move = self._best_move(x, y)
            i += 1
            if (not (new_move == ())):
                return ((x, y), new_move)
        return ()

    def _best_move(self, x, y):
        lis=[(-1, 0), (1, 0), (0, 1), (0, -1)]
        t=1
        while(t<50):
            t+=1
            i = randint(0,len(lis)-1)
            dx,dy =lis[i]

            if (self.board._within_board(x + dx, y + dy) and self.board.board[y + dy][x + dx] == '-'):
                self.board.board[y][x] = '-'
                self.board.board[y + dy][x + dx] = self.player
                self.board._eliminate_about((x + dx, y + dy))

                self.player_position.append((x + dx, y + dy))
                self.player_position.remove((x, y))

                return (x + dx, y + dy)
        return ()

    def _place(self):
        # create random place

        piece = self.player
        while (1 == 1):
            x = randint(0, 7)
            y = randint(0, 7)
            if not (piece == 'W' and y > 5 or piece == 'B' and y < 2) and (self.board.board[y][x] == '-'):
                break

        # validate place itself

        # if that was all okay... we can carry out the place action!
        self.board.board[y][x] = piece
        self.board.pieces[piece] += 1
        self.board._eliminate_about((x, y))
        if (self.board.board[y][x] == piece):
            self.player_position.append((x, y))

        return (x, y)

    def update(self, action):
        # oppenent player has taken this action and hence update the board

        if (action == ()):
            return
        if (self.board.phase == "placing"):
            (x0, y0) = action
            self.board.board[y0][x0] = self.opponent
            self.board._eliminate_about((x0, y0))
            self.player_list_update()
            return
        ((x0, y0), (x1, y1)) = action

        self.board.board[y0][x0] = "-"

        self.board.board[y1][x1] = self.opponent

        self.board._eliminate_about((x1, y1))
        self.player_list_update()

    def player_list_update(self):

        self.player_position_temp = []
        for (x, y) in self.player_position:

            if (self.board.board[y][x] == self.player):
                self.player_position_temp.append((x, y))
        self.player_position=self.player_position_temp








