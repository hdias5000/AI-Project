'''
GROUP NAME:
    algorizma
WRITTEN BY:
    Hasitha Dias: 789929
    Rishab Garg: 796799
LAST MODIFIED DATE:
    11/05/2018
'''

import sys
import copy
import Node as nd

class Alpha_Beta:
    def __init__(self, player, opponent, features):
        self.player = player
        self.opponent = opponent
        self.feature = features

    def set_feature(self,features):
        """
        Changes feature weights to new configuration

        :param features: feature weights for moving phase
        """
        self.feature = features

    def get_feature(self):
        """
        Returns feature weights.

        :return: feature weights
        """
        return self.feature

    def _alpha_beta_place(self, root, max_depth, is_maximizing_player, alpha, beta):
        """
        Does Alpha-Beta pruning MinMax for the placing phase.

        :param root: node that needs expanding depending on depth
        :param max_depth: how much deeper recursion has to go
        :param is_maximizing_player: whether it's opponent's move or player's move in MinMax
        :param alpha: upper value
        :param beta: lover value
        :return: best branch and its score/value
        """
        if max_depth == 0:
            root.weight = root.board._placing_score(self.player)
            return (root.weight, root)

        if is_maximizing_player:
            player = self.player
        else:
            player = self.opponent

        play_dict = {"W": (0, 6), "B": (2, 8)}
        #

        if is_maximizing_player:    #player's turn(MAX)
            best_val = -sys.maxsize
            best_branch = None

            for x in range(0, 8):
                lower, higher = play_dict[player]
                for y in range(lower, higher):
                    if (root.board.board[y][x] == "-"):

                        new_board = copy.deepcopy(root.board)

                        new_board.board[y][x] = player
                        new_board.pieces[player] += 1
                        new_board._eliminate_about((x, y))

                        move = (x, y)
                        branch = nd.Node(new_board, move)


                        (value, b_branch) = self._alpha_beta_place(branch, max_depth - 1,
                                                                   not is_maximizing_player, alpha, beta)
                        if (best_val < value):
                            best_branch = branch
                        best_val = max(best_val, value)
                        alpha = max(alpha, best_val)
                        if beta <= alpha:
                            break
            return (best_val, best_branch)
        else:       #opponent's turn (MIN)
            best_val = sys.maxsize
            best_branch = None

            for x in range(0, 8):
                lower, higher = play_dict[player]
                for y in range(lower, higher):
                    if (root.board.board[y][x] == "-"):

                        new_board = copy.deepcopy(root.board)
                        new_board.board[y][x] = player
                        new_board.pieces[player] += 1
                        new_board._eliminate_about((x, y))

                        move = (x, y)
                        branch = nd.Node(new_board, move)

                        (value, b_branch) = self._alpha_beta_place(branch, max_depth - 1,
                                                                   not is_maximizing_player, alpha, beta)
                        if (best_val > value):
                            best_branch = branch
                        best_val = min(best_val, value)
                        beta = min(beta, best_val)
                        if beta <= alpha:
                            break
            return (best_val, best_branch)

    def _alpha_beta_util(self, root, max_depth, is_maximizing_player, alpha, beta):
        """
        Does Alpha-Beta pruning MinMax for the moving phase.

        :param root: node that needs expanding depending on depth
        :param max_depth: how much deeper recursion has to go
        :param is_maximizing_player: whether it's opponent's move or player's move in MinMax
        :param alpha: upper value
        :param beta: lover value
        :return: best branch and its score/value
        """
        lis = [(-1, 0), (1, 0), (0, 1), (0, -1)]

        if max_depth == 0:
            root.weight = root.board._calculate_score(self.player,self.feature)

            return (root.weight, root)

        if is_maximizing_player:
            player = self.player
        else:
            player = self.opponent
        pieces = root.pieces[player]


        if is_maximizing_player:    #player's move(MAX)
            best_val = -sys.maxsize
            best_branch = None

            for (x, y) in pieces:
                for (dx, dy) in lis:
                    #move to immediate neighbouring positions
                    if (root.board._within_board(x + dx, y + dy) and root.board.board[y + dy][x + dx] == "-"):
                        new_board = copy.deepcopy(root.board)
                        new_board.board[y][x] = "-"
                        new_board.board[y + dy][x + dx] = player
                        new_board._eliminate_about((x + dx, y + dy))

                        move = ((x, y), (x + dx, y + dy))
                        branch = nd.Node(new_board, move)
                        (value, b_branch) = self._alpha_beta_util(branch, max_depth - 1,
                                                                  not is_maximizing_player, alpha, beta)

                        if (best_val < value):
                            best_branch = branch
                        best_val = max(best_val, value)
                        alpha = max(alpha, best_val)
                        if beta <= alpha:
                            break

                    #jump move over an occupied position
                    if (root.board._within_board(x + 2 * dx, y + 2 * dy) and root.board.board[y + 2 * dy][
                        x + 2 * dx] == "-" and (
                            root.board.board[y + dy][x + dx] == "W" or root.board.board[y + dy][x + dx] == "B")):
                        new_board = copy.deepcopy(root.board)
                        new_board.board[y][x] = "-"
                        new_board.board[y + 2 * dy][x + 2 * dx] = player
                        new_board._eliminate_about((x + 2*dx, y + 2*dy))

                        move = ((x, y), (x + 2 * dx, y + 2 * dy))

                        branch = nd.Node(new_board, move)
                        (value, b_branch) = self._alpha_beta_util(branch, max_depth - 1,
                                                                  not is_maximizing_player, alpha, beta)
                        if (best_val < value):
                            best_branch = branch
                        best_val = max(best_val, value)
                        alpha = max(alpha, best_val)
                        if beta <= alpha:
                            break

            return (best_val, best_branch)

        else:       #opponent's move(MIN)
            best_val = sys.maxsize
            best_branch = None

            for (x, y) in pieces:
                for (dx, dy) in lis:
                    # move to immediate neighbouring positions
                    if (root.board._within_board(x + dx, y + dy) and root.board.board[y + dy][x + dx] == "-"):
                        new_board = copy.deepcopy(root.board)
                        new_board.board[y][x] = "-"
                        new_board.board[y + dy][x + dx] = player
                        new_board._eliminate_about((x + dx, y + dy))

                        move = ((x, y), (x + dx, y + dy))

                        branch = nd.Node(new_board, move)
                        (value, b_branch) = self._alpha_beta_util(branch, max_depth - 1,
                                                                  not is_maximizing_player, alpha, beta)

                        if (best_val > value):
                            best_branch = branch
                        best_val = min(best_val, value)
                        beta = min(beta, best_val)
                        if beta <= alpha:
                            break

                    # jump move over an occupied position
                    if (root.board._within_board(x + 2 * dx, y + 2 * dy) and root.board.board[y + 2 * dy][
                        x + 2 * dx] == "-" and (
                            root.board.board[y + dy][x + dx] == "W" or root.board.board[y + dy][x + dx] == "B")):
                        new_board = copy.deepcopy(root.board)
                        new_board.board[y][x] = "-"
                        new_board.board[y + 2 * dy][x + 2 * dx] = player
                        new_board._eliminate_about((x + 2*dx, y + 2*dy))

                        move = ((x, y), (x + 2 * dx, y + 2 * dy))

                        branch = nd.Node(new_board, move)
                        (value, b_branch) = self._alpha_beta_util(branch, max_depth - 1,
                                                                  not is_maximizing_player, alpha, beta)
                        if (best_val > value):
                            best_branch = branch
                        best_val = min(best_val, value)
                        beta = min(beta, best_val)
                        if beta <= alpha:
                            break

            return (best_val, best_branch)
