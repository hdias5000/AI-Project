'''
GROUP NAME:
    algorizma
WRITTEN BY:
    Hasitha Dias: 789929
    Rishab Garg: 796799
LAST MODIFIED DATE:
    11/05/2018
'''

class Board:
    def __init__(self):
        self.board = [['-' for _ in range(8)] for _ in range(8)]
        for square in [(0, 0), (7, 0), (7, 7), (0, 7)]:
            x, y = square
            self.board[y][x] = 'X'
        self.n_shrinks = 0
        #this contains the positional value for each position on the board
        self.centre_board = \
            [[None, -100, -100, -100, -100, -100, -100, None],
             [-100, -75, -50, -50, -50, -50, -75, -100],
             [-100, -50, 50, 50, 50, 50, -50, -100],
             [-100, -50, 50, 100, 100, 50, -50, -100],
             [-100, -50, 50, 100, 100, 50, -50, -100],
             [-100, -50, 50, 50, 50, 50, -50, -100],
             [-100, -75, -50, -50, -50, -50, -75, -100],
             [None, -100, -100, -100, -100, -100, -100, None]]
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

    def _get_positions(self,player,other_player):
        """
        Finds all the positions of each piece and also counts number of pieces in center.

        :param player: player valye
        :param other_player: opponent value
        :return: tuple containing list of player positions, opponent positions, count of total pieces in centre
        """
        our_position = []
        opp_position = []
        total_centre = 0
        # iterates through each element on the board
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[j][i] == player:
                    our_position.append((i,j))
                    if i in range(2,6) and j in range(2,6):
                        total_centre += 1
                if self.board[j][i] == other_player:
                    opp_position.append((i, j))
        return our_position, opp_position, total_centre

    def _get_our_pairs(self, our_pieces,our_player):
        """
        Finds out how close the player's pieces are.

        :param our_pieces: list of pieces of player
        :param our_player: player value
        :return: total number white pieces close to eachother
        """
        li = [(-1, 0), (1, 0), (0, 1), (0, -1),(1,1),(1,-1),(-1,1),(-1,-1)]
        total=0
        for (x,y) in our_pieces:
            for (dx,dy) in li:
                if self._within_board(x+dx,y+dy) and self.board[y+dy][x+dx] == our_player:
                    total += 1
        return total

    def _get_placing_stability(self, our_position, opp_position):
        """
        Finds total for pieces on current state depending on positional value.

        :param our_position: list of pieces of player
        :param opp_position: list of pieces of opponent
        :return: total score depending on positional values
        """
        score = 0
        for (x, y) in our_position:
            score += self.centre_board[y][x]
        for (x, y) in opp_position:
            score -= self.centre_board[y][x]
        return score

    def _placing_score(self,player):
        """
        Finds evaluation score for placing phase.

        :param player: player value
        :return: evaluation score for placing phase
        """
        place_rate = 100
        diff_score = 1000
        #we should more focus on that player should not be killed in placing phase and is in centre.
        other_player = "W"
        if player == "W":
            other_player = "B"

        (our_position, opp_position, centre_total) = self._get_positions(player, other_player)

        #gets score for each feature
        place_score =self._get_placing_stability(our_position, opp_position)
        diff_pieces = self.pieces[player] - self.pieces[other_player]

        return place_score*place_rate + diff_score*diff_pieces

    def attack_strategy(self, player_positions, opponent_positions, player, opponent):
        """
        Finds score for attacking strategy in moving phase.

        :param player_positions: pieces of player
        :param opponent_positions: pieces of opponent
        :param player: player value
        :param opponent: opponent value
        :return: attacking score for moving phase
        """
        li = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        total_dist = 0

        max_player_pos,max_player_count=((),-1)

        #find  player clusters
        for (px, py) in player_positions:
            current_player_count = 0
            for (dx, dy) in li:
                if (self._within_board(px + dx, py + dy) and self.board[py + dy][px + dx] == player):
                    current_player_count += 1
            if(current_player_count > max_player_count):
                (max_player_pos,max_player_count) = ((px,py),current_player_count)

        min_opponent_pos, min_opponent_count = ((), 100)

        #finds opponent clusters
        for (ox, oy) in opponent_positions:
            current_opponent_count = 0

            for (dx, dy) in li:
                if (self._within_board(ox + dx, oy + dy) and self.board[oy + dy][ox + dx] == opponent):
                    current_opponent_count+=1
            if (current_opponent_count < min_opponent_count):
                (min_opponent_pos, min_opponent_count) = ((ox, oy), current_opponent_count)

        #finds distance between max player cluster and min opponent cluster
        if(max_player_count - min_opponent_count >2):
            total_dist = abs((min_opponent_pos[1]-max_player_pos[1] )) + abs((min_opponent_pos[0]-max_player_pos[0] ))
        try:
            return 100 / total_dist
        except:
            return 0

    def _calculate_score(self, player, features):
        """
        Finds evaluation score for moving phase.

        :param player: player value
        :param features: weights for each feature
        :return: evaluation score for moving phase
        """
        other_player = "W"
        if (player == "W"):
            other_player = "B"

        center_rate = features[0]
        piece_diff_rate = features[1]
        defense_rate = features[2]
        attack_rate = features[3]

        #recieves scores for each feature in moving phase
        (our_position,opp_position,centre_total)=self._get_positions(player,other_player)
        diff_pieces = self.pieces[player] - self.pieces[other_player]
        defense_score= self._get_our_pairs(our_position,player)
        attack_score = self.attack_strategy(our_position, opp_position, player, other_player)

        return (center_rate*centre_total) + (diff_pieces*piece_diff_rate) +\
               (defense_rate*defense_score) + (attack_rate*attack_score)