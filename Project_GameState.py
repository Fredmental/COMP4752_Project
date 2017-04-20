import sys, time, random, copy
from settings import *

# This handles the actual game aspect of checkers.
class GameState:
    def __init__(self, rows, cols):
        self.__rows  = rows         # number of rows in the board
        self.__cols = cols          # number of columns in the board
        self.__pieces = [0]*cols    # __pieces[c] = number of pieces in a column c
        self.__player = 0           # the current player to move, 0 = Player One, 1 = Player Two
        self.__board   = [[PLAYER_NONE]*cols for r in range(rows)]

        # Initializes all the variables that help with putting and moving pieces.
        self.selected_piece = (-1, -1) # Used for highlighting potential moves.
        self.red_piece_list = copy.deepcopy(STARTING_RED_POSITIONS) # All red pieces at bottom. # STARTING_RED_POSITIONS
        self.black_piece_list = copy.deepcopy(STARTING_BLACK_POSITIONS) # All black pieces at top. # STARTING_BLACK_POSITIONS

        # List of all kings on the board
        self.red_king_piece_list = [] ##copy.deepcopy(RED_CAN_BECOME_KING_KING_LIST_R)
        self.black_king_piece_list = [] # copy.deepcopy(BLACK_CAN_BECOME_KING_KING_LIST_B)
        
        self.red_piece_potential_move_list = [] # No potential red moves at init.
        self.black_piece_potential_move_list = [] # No potential black moves at init.
        self.black_pieces_to_remove_list = [] # Used to remove black pieces when a red piece does a jump.
        self.red_pieces_to_remove_list = [] # Used to remove red pieces when a black piece does a jump

        self.just_done_move = None # The move just finished,
        self.just_deleted = None # last deleted.
        # # print("GameState init completed")

    # These are getter functions used to get private variables such as self.__rows.
    def get(self, r, c):        return self.__board[r][c]   # piece type located at (r,c)
    def cols(self):             return self.__cols          # number of columns in board
    def rows(self):             return self.__rows          # number of rows in board
    def player_to_move(self):   return self.__player        # the player to move next
    def opponent(self, player): return (player + 1) % 2 # return the opponent's value

    # Check if a move is legal.
    def is_legal(self, move):
        # If the move is on tile with a red piece, then it's not legal.
        if move in self.red_piece_list:
            # # print("move is in red piece list")
            return False

        # If the move is on tile with a black piece, then it's not legal.
        if move in self.black_piece_list:
            # # print("move is in black piece list")
            return False

        # Check if the row position is within bounds.
        if (move[0] < 0 or move[0] >= BOARD_ROWS):
            # # print("row location is out of bounds")
            return False

        # Check if the column position is within bounds.
        if (move[1] < 0 or move[1] >= BOARD_COLS):
            # # print("column location is out of bounds")
            return False

        # Previously checks were false so tile must be legal.
        return True

    # This will execute a move when passed a new row/column location.
    def do_move(self, new_pos):
        # print("new_pos is ", new_pos)
        self.just_deleted = None
        # If the move is illegal, then return.
        # # print("new_pos is ", new_pos)
        if not self.is_legal(new_pos):
            self.__player = self.opponent(self.__player)
            print("DOING ILLEGAL MOVE")
            return

        # Used to determine the action direction the move took.
        action_taken = ( new_pos[0] - self.selected_piece[0],
                         new_pos[1] - self.selected_piece[1])

        self.just_done_move = (new_pos, self.selected_piece)

        # If positive row action, action_direction_row is 1.
        if action_taken[0] < 0:
            action_direction_row = -1
        else:
            action_direction_row = 1

        # If positive column action, action_direction_col is 1.
        if action_taken[1] < 0:
            action_direction_col = -1
        else:
            action_direction_col = 1

        # Used to remove a black piece off a board after a jump.
        action_direction = (action_direction_row, action_direction_col)

        # If the player is red then execute his move.
        if (self.__player == 0):
            # If a jump was executed, removed all elements jumped.
            for piece in self.black_pieces_to_remove_list:
                # If the piece's action to get there is the same as we used to get here
                # then remove it.
                if piece[1] == action_direction:
                    self.black_piece_list.remove(piece[0]) # Remove from board.
                    self.just_deleted = piece[0]
            self.black_pieces_to_remove_list = [] # Reinitialize list.

            # Grab index of selected tile.
            # # print("self.selected_piece is ", self.selected_piece)
            # # print("self.black_piece_list is ", self.red_piece_list)
            piece_index = self.red_piece_list.index(self.selected_piece)

            # If piece is a king, must update it's location in red_king_piece_list.
            if self.red_piece_list[piece_index] in self.red_king_piece_list:
                king_piece_index = self.red_king_piece_list.index(self.selected_piece)
                self.red_king_piece_list[king_piece_index] = new_pos

            # If piece is about to become a king, then add it to the list.
            if new_pos in RED_CAN_BECOME_KING:
                # We don't want duplicates.
                if new_pos not in self.red_king_piece_list:
                    self.red_king_piece_list.append(new_pos)
                
            self.red_piece_list[piece_index] = new_pos
            self.red_piece_potential_move_list = []

        # If the player is black then execute his move.
        if (self.__player == 1):
            print("player is 1")
            print("self.red_pieces_to_remove_list is ", self.red_pieces_to_remove_list)
            # If a jump was executed, removed all elements jumped.
            for piece in self.red_pieces_to_remove_list:
                # If the piece's action to get there is the same as we used to get here
                # then remove it.
                if piece[1] == action_direction:
                    self.red_piece_list.remove(piece[0]) # Remove from board.
                    self.just_deleted = piece[0]
            # MAYBE self.red_pieces_to_remove_list = [] # Reinitialize list.
            
            # Grab index of selected tile
            # # print("self.selected_piece is ", self.selected_piece)
            # # print("self.black_piece_list is ", self.black_piece_list)
            # print("black piece selected index is ", self.selected_piece) 
            piece_index = self.black_piece_list.index(self.selected_piece)

            # If piece is a king, must update it's location in red_king_piece_list.
            if self.black_piece_list[piece_index] in self.black_king_piece_list:
                king_piece_index = self.black_king_piece_list.index(self.selected_piece)
                self.black_king_piece_list[king_piece_index] = new_pos

            # If piece is about to become a king, then add it to the list.
            if new_pos in BLACK_CAN_BECOME_KING:
                # We don't want duplicates.
                if new_pos not in self.black_king_piece_list:
                    self.black_king_piece_list.append(new_pos)
            
            self.black_piece_list[piece_index] = new_pos
            self.black_piece_potential_move_list = []

        # Swap players so the next player gets the turn.
        self.__player = self.opponent(self.__player)
        # print("self.__player is ", self.__player)
        

    # Undo the last done move in the gamestate.
    def undo_move(self):
        # self.just_done_move = (new_pos, self.selected_piece)
        # If the player is red, undo the red move and pass it to black.
        if (self.__player == 0):
            # Remove the new postion piece and add the old position back in.
            piece_index = self.black_piece_list.index(self.just_done_move[0])
            self.black_piece_list[piece_index] = self.just_done_move[1]

            # If we deleted a piece then put it back in.
            if self.just_deleted != None:
                self.red_piece_list.append(self.just_deleted)

        # If the player is black, undo the red move and pass it to red.
        elif (self.__player == 1):
            # Remove the new postion piece and add the old position back in.
            piece_index = self.red_piece_list.index(self.just_done_move[0])
            self.red_piece_list[piece_index] = self.just_done_move[1]

            # If we deleted a piece then put it back in.
            if self.just_deleted != None:
                self.black_piece_list.append(self.just_deleted)

        # Give the opponent back his turn.
        self.__player = self.opponent(self.__player)

    
    # When a player selects a piece, this function will highlight all the potential moves around it.
    def highlight_potential_moves(self, tile):
        # We don't don't want multiple red/black potential pieces on board, so reinitialize.
        # # print("----------------------------------- HIGHLIGHT ----------------------------------- ")
        # # print("self.player is ", self.__player)
        self.red_piece_potential_move_list = [] 
        self.black_piece_potential_move_list = []
        self.red_pieces_to_remove_list = []
        self.black_pieces_to_remove_list = []
        self.red_pieces_to_remove_list = [] # Reinitialize list.
        self.just_done_move = None

        # Grab potential_moves depending on the player.
        # Red piece player
        if (self.__player == 0):
            # If the tile pressed isn't red, then return.
            # # print("hm - tile is ", tile)
            # # print("hm - self.red_piece_ is ", self.red_piece_list)
            if tile not in self.red_piece_list:
                # # print("Didn't click on red tile")
                return

            self.selected_piece = tile # Used to possibly move to this postion later.

            # Grab all legal actions and put it in the legal action list.
            action_list = []

            # If the tile is a king then grab all king actions, if not then grab usual red piece actions.
            if tile in self.red_king_piece_list:
                for action in LEGAL_KING_ACTIONS:
                    action_list.append(action)
            else:
                for action in LEGAL_RED_ACTIONS:
                    action_list.append(action)

            # Loop through all legal red actions to add them as potential moves.
            for action in action_list:
                # # print("-------- action")
                # The new postion of the piece.
                new_row = tile[0] + action[0]
                new_col = tile[1] + action[1]
                temp_piece = (new_row, new_col)

                # If the temp location is on a black piece, check if jump exists.
                if temp_piece in self.black_piece_list:
                    # The possible jump column will change depending on the action taken.
                    # possible jump row will remain the same.
                    possible_jump_row = temp_piece[0] + action[0]
                    possible_jump_col = temp_piece[1] + action[1]

                    # Where we'll be jumping to if the spot is legal.
                    possible_jump = (possible_jump_row, possible_jump_col)
                    if self.is_legal(possible_jump):
                        # It's now a potential move.
                        self.red_piece_potential_move_list.append(possible_jump)
                        
                        # We remove the jumped piece by using this list.
                        self.black_pieces_to_remove_list.append( (temp_piece, action))
                    continue
                else:
                    # The temp_piece is now added to list.
                    if self.is_legal(temp_piece):
                        self.red_piece_potential_move_list.append(temp_piece)

        # Black piece player
        if (self.__player == 1):
            # If the tile pressed isn't black, then return.
            if tile not in self.black_piece_list:
                # # print("Didn't click on black tile")
                return

            self.selected_piece = tile # Used to possibly move to this postion later.

            # Grab all legal actions and put it in the legal action list.
            action_list = []

            # If the tile is a king then grab all king actions, if not then grab usual red piece actions.
            if tile in self.black_king_piece_list:
                for action in LEGAL_KING_ACTIONS:
                    action_list.append(action)
            else:
                for action in LEGAL_BLACK_ACTIONS:
                    action_list.append(action)
            
            # Loop through all legal black actions to add them as potential moves.
            for action in action_list:
                # The new postion of the piece.
                new_row = tile[0] + action[0]
                new_col = tile[1] + action[1]
                temp_piece = (new_row, new_col)
                new_action = (action[0] + action[0], action[1] + action[1])

                # If the temp location is on a black piece, check if jump exists.
                if temp_piece in self.red_piece_list:
                    # The possible jump column will change depending on the action taken.
                    # possible jump row will remain the same.
                    possible_jump_row = temp_piece[0] + action[0]
                    possible_jump_col = temp_piece[1] + action[1]

                    # Where we'll be jumping to if the spot is legal.
                    possible_jump = (possible_jump_row, possible_jump_col)
                    if self.is_legal(possible_jump):
                        # It's now a potential move
                        self.black_piece_potential_move_list.append(possible_jump)

                        # We remove the jumped piece by using this list.
                        self.red_pieces_to_remove_list.append( (temp_piece, action))
                    continue
                else:
                    # The temp_piece is now added to list.
                    if self.is_legal(temp_piece):
                        self.black_piece_potential_move_list.append(temp_piece)


    def winner(self):
        if(len(self.black_piece_list) <= 6):
            # # print("P1 wins!")
            return PLAYER_ONE

        elif(len(self.red_piece_list) <= 6):
            # # print("P2 wins!")
            return PLAYER_TWO

        else: 
            return PLAYER_NONE

    # The Heuristic will be put in this function.
    def eval(self, player):
        # print("in eval")
        score = 0
        if(self.winner() == player):
            score = 1000000
            # # print("winning move")
            return score
        elif(self.winner() == ((player + 1) % 2)):
            score = -1000000
            # # print("losing move")
            return score
        else:
            if(player == PLAYER_ONE):
                score += ((len(self.red_piece_list) - len(self.black_piece_list)) * 100)
                score += ((len(self.red_king_piece_list) - len(self.black_king_piece_list)) * 25)

                ##for pieces in red_piece_list
            else:
                score += ((len(self.black_piece_list) - len(self.red_piece_list)) * 100)
                score += ((len(self.black_king_piece_list) - len(self.red_king_piece_list)) * 25)
            # # print("no one has won yet")
            return score


# This will later will be used to implement alphabeta.
class Player_AlphaBeta:
    def __init__(self, max_depth, time_limit):
        self.max_depth = max_depth      # set the max depth of search
        self.time_limit = time_limit    # set the time limit (in milliseconds)
        self.best_move = -1             # record the best move found so far
        self.reset()
        self.current_maxd = max_depth
        
        # # print('initailized player alpha beta')
        # Add more class variables here as necessary (you will probably need more)

    
    # Reset all appropriate values so alphabeta can be freshly called again.
    def reset(self):
        self.temp_best_move = -1
        self.best_move = -1
        self.best_move_val = -1000000
        self.alpha_beta_val = []

    def get_move(self, state):
        print("get_move ----------------")
        # reset the variables
        self.reset()
        # store the time that we started calculating this move, so we can tell how much time has passed
        self.time_start = time.clock()
        # store the player that we're deciding a move for and set it as a class variable
        self.player = state.player_to_move()
        # do your alpha beta (or ID-AB) search here
        ab_value = self.alpha_beta(state, 0, -1000000, 1000000, True)
        # return the best move computer by alpha_beta
        print("++++++++alpha beta value received")
        print("self.temp_best_just_done_move is ", self.temp_best_just_done_move)
        return self.temp_best_move # Return the best move.

    def is_terminal(self, state, depth):
        # print("in terminal")
        # print("depth is ", depth)
        # print("current_maxd is ", self.current_maxd)
        if (self.current_maxd > 0 and depth >= self.current_maxd):
            return True
        return state.winner() != PLAYER_NONE
    
    def alpha_beta(self, state, depth, alpha, beta, max_player):
        # If terminal then return the evaluation.
        if (self.is_terminal(state, depth)): 
            # print('its terminal')
            return state.eval(self.player)

        print("player is ", state.player_to_move())

        # Look for best move if red piece.
        if(state.player_to_move() == 0):
            for piece in state.red_piece_list:
                # print("state.red_piece_list is ", state.red_piece_list)
                state.highlight_potential_moves(piece)
                for move in state.red_piece_potential_move_list:
                    state.do_move(move)
                    val = self.alpha_beta(state, depth+1, alpha, beta, False)  
                    state.undo_move()  # Must implement this method.
                    if depth == 0: self.alpha_beta_val.append(val)
                    if max_player and val > alpha:
                        if depth == 0:
                            self.temp_best_move = move
                        alpha = val
                    elif not max_player and val < beta:
                        beta = val
                    if alpha >= beta:
                        break
            return alpha if max_player else beta

        # Look for best move if black piece.
        elif(state.player_to_move() == 1):
            for piece in state.black_piece_list:
                # print("black piece list is ", state.black_piece_list)
                state.highlight_potential_moves(piece)
                # print("state.black_piece_list is ", state.black_piece_list)
                for move in state.black_piece_potential_move_list:
                    state.do_move(move)
                    val = self.alpha_beta(state, depth+1, alpha, beta, False)  
                    state.undo_move()  # Must implement this method.
                    if depth == 0: self.alpha_beta_val.append(val)
                    if max_player and val > alpha:
                        if depth == 0:
                            self.temp_best_move = move
                            self.temp_best_selected_piece = state.selected_piece
                            self.temp_best_just_done_move = state.just_done_move
                            self.temp_red_pieces_to_remove_list = state.red_pieces_to_remove_list
                            alpha = val
                        elif not max_player and val < beta:
                            beta = val
                        if alpha >= beta:
                            break
            # print("alpha is ", alpha)
            return alpha if max_player else beta
    
