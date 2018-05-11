'''
GROUP NAME:
    algorizma
WRITTEN BY:
    Hasitha Dias: 789929
    Rishab Garg: 796799
LAST MODIFIED DATE:
    11/05/2018
'''

import Board as bd
import Alpha_Beta as search
import copy
import sys
import time
import Node as nd

class Player:
    # used when considering machine learning
    # def get_data(self):
    #     df = pd.DataFrame()
    #     df['our_moves'] = self.our_pred_moves
    #     df['opp_moves'] = self.opp_pred_moves
    #     df['total_time'] = self.time
    #     df['depth'] = self.depths
    #     return df

    def __init__(self, colour):
        # used when considering machine learning
        # self.total_actual_moves=[]
        # self.our_pred_moves=[]
        # self.opp_pred_moves=[]
        # self.depths=[]

        self.board = bd.Board()
        self.player_position = []
        self.place_turns = 0
        self.move_turns = -1
        self.time = []

        #initial feature weightings obtained as best combination of features after implementing machine learning
        self.init_features = [17,7,2,12]
        self.previous_time = 0
        self.total_time = 0

        #starts at lower depth, to make sure program doesn;t get stuck initially
        self.depth = 2


        if (colour == "white"):
            self.player = "W"
            self.opponent = "B"
        else:
            self.player = "B"
            self.opponent = "W"

        self.ab = search.Alpha_Beta(self.player,self.opponent,self.init_features)

    def action(self, turns):
        """
        This function is called by referee. Calls necessary function to return a best/valid move place(for placing).

        :param turns: current turn of player
        :return: best/valid move/place or None if no available moves
        """
        start_time = time.time()
        self.board.turns = turns  # the current number of turn excluding the turn which we will take now.

        #changing from 'placing' phase to 'moving'
        if (self.board.phase == "placing" and self.place_turns != 0 and turns == 0):
            self.board.phase = 'moving'

        #check if placing phase to call function
        if (self.board.phase == 'placing'):
            # make sure this placing turn is counted one is counted
            self.place_turns += 1
            move_action = self._alpha_beta(turns)
            if (turns == 23):
                self.board.phase = "moving"
            self.previous_time = time.time() - start_time
            self.total_time += time.time() - start_time
            return move_action

        # shrinks if board shrinks on this turn
        if (self.board.phase == 'moving'):
            if (turns == 128 or turns == 192):
                self.board._shrink_board()
                self.player_list_update()

            #finds best/valid move
            moved_piece_direction = self._alpha_beta(turns)

            # shrinks if shrink is due for next turn
            if (turns == 127 or turns == 191):
                self.board._shrink_board()
                self.player_list_update()

            self.previous_time = time.time() - start_time
            self.total_time += time.time() - start_time
            return moved_piece_direction



    def check_feature(self,feature):
        """
        Sets new configuration of feature weights in Alpha-Beta class.

        :param feature: configuration of feature weights
        """
        self.ab.set_feature(feature)
        return None

    # used when considering machine learning
    # def _get_depth_moving(self):
    #     (our_position, opp_position, _) = self.board._get_positions(self.player,self.opponent)
    #     li = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    #     our_player_moves=0
    #     other_player_moves=0
    #     for (x,y) in our_position:
    #         for (dx,dy) in li:
    #             if(self.board._within_board(x+dx,y+dy) and self.board.board[y+dy][x+dx]==self.player):
    #                 our_player_moves += 1
    #             if (self.board._within_board(x + dx, y + dy) and self.board.board[y + dy][x + dx] == self.opponent):
    #                 other_player_moves += 1
    #
    #     return (our_player_moves,other_player_moves)


    def _alpha_beta(self, turns):
        """
        Calls necessary Alpha-Beta function from Alpha-Beta class depending on current phase after choosing
        best depth depending on performance and also choosing strategy depending on current state of game.

        :param turns: current turn of player
        :return: best/valid move/place or None if no available moves
        """
        # has newBoard which is current board of game
        new_board = copy.deepcopy(self.board)

        features = self.ab.get_feature()
        player_positions, opponent_positions, centre = self.board._get_positions(self.player,self.opponent)

        #changes strategy from attack to deffense depending on the clustering of black pieces and distance
        #   from dense white cluster to small black cluster
        if self.board.attack_strategy(player_positions,opponent_positions,self.player,self.opponent)>75:
            features[2] = 3
            features[3] = 7
        else:
            features[2] = 7
            features[3] = 3
        self.ab.set_feature(features)


        try:
            if (((110-self.total_time)/self.previous_time)<(192-turns)):
                self.depth = 2
            else:
                self.depth = 3
            if turns>192:
                if (((119-self.total_time)/self.previous_time)<(212-turns)):
                    self.depth = 5
                else:
                    self.depth = 4


        except:
            self.depth = 2

        alpha = -sys.maxsize
        beta = sys.maxsize
        root = nd.Node(new_board, None)

        if (self.board.phase == "placing"):
            #depth is fixed for placing as it chooses to occupy centre with array build in board.
            max_depth = 2
            (score, branch) = self.ab._alpha_beta_place(root, max_depth, True, alpha, beta)
        else:
            #changing depth depending on performance
            max_depth=self.depth
            (score, branch) = self.ab._alpha_beta_util(root, max_depth, True, alpha, beta)

            # used when considering machine learning
            # self.time.append((time.time() - start_time))
            # self.our_pred_moves.append(our_move)
            # self.opp_pred_moves.append(opp_move)
            # self.depths.append(max_depth)

        # returns None as move if there are no available moves
        if branch==None:
            return None
        else:
            self.board.board = copy.deepcopy(branch.board.board)

        return branch.move

    def update(self, action):
        """
        This function is called by referee. Updates the player's game state/board depending on the opponent's turn.

        :param action: move/place done by opponent
        """

        #no update if opponent forfeited their turn
        if (action == None):
            return

        #only places the action if still in placing phase
        if (self.board.phase == "placing"):
            (x0, y0) = action
            self.board.board[y0][x0] = self.opponent
            self.board._eliminate_about((x0, y0))
            self.player_list_update()
            return

        # does a move if the action is in placing phase
        ((x0, y0), (x1, y1)) = action

        self.board.board[y0][x0] = "-"
        self.board.board[y1][x1] = self.opponent
        self.board._eliminate_about((x1, y1))
        self.player_list_update()

    def player_list_update(self):
        """
        This function is called to update the list of all player positions depending on the current state of the board.

        """
        self.player_position_temp = []
        for (x, y) in self.player_position:

            if (self.board.board[y][x] == self.player):
                self.player_position_temp.append((x, y))
        self.player_position = self.player_position_temp