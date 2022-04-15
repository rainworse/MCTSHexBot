import socket
from time import time
from TreeStructure import Tree
from numpy import zeros
from random import choice, shuffle, uniform
from copy import deepcopy
from ctypes import *


# Returns the char representation of the colour opposite to the provided one.
def opp_colour(color):
    if color == "R":
        return "B"
    elif color == "B":
        return "R"
    else:
        return "None"


# check if move is within the board
def within_bounds(move, board_size):
    return 0 <= move[0] < board_size and 0 <= move[1] < board_size


# get swap moves
def get_swap_moves():
    f = open('./agents/Group031/swap_moves.txt', "r")
    swap_moves_dict = dict()
    for x in f:
        if "#" not in x and x != '':
            swap_move = x.split()
            if swap_move[0] in swap_moves_dict:
                swap_moves_dict[swap_move[0]].append((int(swap_move[1][1]) - 1, int(ord(swap_move[1][0])) - 97))
            else:
                swap_moves_dict[swap_move[0]] = []
                swap_moves_dict[swap_move[0]].append((int(swap_move[1][1]) - 1, int(ord(swap_move[1][0])) - 97))
    f.close()
    return swap_moves_dict


class MCTSAgent:
    HOST = "127.0.0.1"
    PORT = 1234
    PLAYERS = {"None": 0, "B": 1, "R": 2}
    TIME_LIMIT_S = 5 * 60
    NEIGHBOURS = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]

    def __init__(self):
        self.game_tree = Tree()
        self._turn_count = 1
        self._colour = "None"
        self._board_size = 0
        self.prev_move = (0, 0)
        self.time_taken_s = 0
        self.mcts_calls = 0

    # check if should swap or not here
    def swap_logic(self):
        swap_moves = get_swap_moves()
        if self.prev_move in swap_moves[str(self._board_size) + 'x' + str(self._board_size)]:
            return True
        return False

    # time allowed to find a turn
    def choose_turn_time(self):
        # return (self.TIME_LIMIT_S - self.time_taken_s) / (len(self.valid_moves(self._board)) / 2 + 1) * 0.9
        return 0.2

    # randomly choose value from weights
    def select_rand_pos(self, weights, summa):
        rnd = uniform(0, summa)
        for i in range(self._board_size):
            weight = weights[int(i / self._board_size * len(weights))]
            if rnd < weight:
                return i
            rnd -= weight
        return self._board_size - 1

    # choose how to start the game based on weighing
    def make_first_move(self):
        x_weights = [0, 0, 0, 30, 30, 30, 30, 30, 0, 0, 0]
        y_weights = [100, 50, 30, 10, 0, 0, 0, 10, 30, 50, 100]

        sum_x = 0
        sum_y = 0
        for i in range(self._board_size):
            sum_x += x_weights[int(i / self._board_size * len(x_weights))]
            sum_y += y_weights[int(i / self._board_size * len(y_weights))]

        return self.select_rand_pos(x_weights, sum_x), self.select_rand_pos(y_weights, sum_y)

    # check if nearby tiles are occupied by player
    def similar_neighbours(self, board, move, player_color):
        similar = []

        for n in self.NEIGHBOURS:
            n_move = (move[0] + n[0], move[1] + n[1])
            if within_bounds(n_move, self._board_size) and board[n_move] == player_color:
                similar.append(n_move)
        return similar

    # check if 'player' is winner on 'board'
    def player_is_winner(self, board, player):
        start = []
        end = []
        player_color = self.PLAYERS[player]
        color_offset = 0
        board_offset = self._board_size - 1

        if player == "R":
            start = [board[0, i] for i in range(self._board_size)]
            end = [board[board_offset, i] for i in range(self._board_size)]
            color_offset = 0
        elif player == "B":
            start = [board[i, 0] for i in range(self._board_size)]
            end = [board[i, board_offset] for i in range(self._board_size)]
            color_offset = 1

        if player_color in start and player_color in end:
            discovered = []
            explored = []

            for i in range(self._board_size):
                if start[i] == player_color:
                    move = (0, i)
                    if player == "B":
                        move = tuple(reversed(move))
                    discovered.append(move)

            while len(discovered):
                move = discovered.pop()
                neighbours = self.similar_neighbours(board, move, player_color)

                for nb_tile in neighbours:
                    if nb_tile[color_offset] == board_offset:
                        return True
                    if nb_tile not in discovered and nb_tile not in explored:
                        discovered.append(nb_tile)
                explored.append(move)

        return False

    # check if winner exists
    def board_has_winner(self, board):

        return self._clib.player_is_winner(self._board, self._board_size, self._colour) or \
               self._clib.player_is_winner(self._board, self._board_size, opp_colour(self._colour))

    # return a set of empty board spaces
    def valid_moves(self, board):
        return [(x, y) for x in range(self._board_size) for y in range(self._board_size) if not board[x, y]]

    # go down until we find an unexplored node
    def select_move(self, board, player):
        node = self.game_tree

        # down a level if possible
        while len(node.children):
            nodes = []
            max_val = float('-inf')
            multiplier = 1 if player == self._colour else -1
            exploit = 1.2 if player == self._colour else 1.4
            for node in node.children:
                ucb = node.get_ucb_score(True, multiplier, exploit)
                if ucb >= max_val:
                    max_val = ucb
                    nodes.append([ucb, node])

            node = choice([t[1] for t in nodes if t[0] == max_val])
            board[node.move] = self.PLAYERS[player]
            player = opp_colour(player)
        return node, player

    # add all possible moves to node from current position
    def expand_move(self, node, board, player):
        moves = self.valid_moves(board)

        # break if game over
        if not len(moves) or self.board_has_winner(board):
            return node, opp_colour(player)

        for move in moves:
            node.children.append(Tree(move, node))

        # choose a random move to explore
        node = choice(node.children)
        board[node.move] = self.PLAYERS[player]
        return node, player

    # simulate a game until the end
    def simulate_game(self, board, player):
        moves = self.valid_moves(board)
        shuffle(moves)

        # fill in moves until game won, swapping between players
        while len(moves):
            player = opp_colour(player)
            board[moves.pop()] = self.PLAYERS[player]

        if self.player_is_winner(board, player):
            return player
        return opp_colour(player)

    # save info back up the tree
    def backpropagate(self, node, winner):
        flip = 1 if winner == self._colour else -1
        while node is not None:
            node.visits += 1
            node.score += flip
            flip *= -1
            node = node.parent

    # run a single iteration of MCTS
    def search_moves(self):
        player = self._colour
        fake_board = deepcopy(self._board)

        node, player = self.select_move(fake_board, player)
        node, player = self.expand_move(node, fake_board, player)
        winner = self.simulate_game(fake_board, player)
        self.backpropagate(node, winner)

    # pick move with highest score
    def best_move(self):
        # clear out data for next turn
        self.game_tree = sorted(self.game_tree.children, key=lambda c: c.get_ucb_score(False, 1, 0))[-1]
        self.game_tree.parent = None

    # runs several iterations of MCTS to choose the best move
    def make_mcts_choice(self, time_allowed, start_time):
        # search while have time
        times_searched = 0
        # while times_searched < 50:
        while not times_searched or time() - start_time < time_allowed:
            self.search_moves()
            times_searched += 1
            if len(self.game_tree.children) == 1:
                break

        # select best move from search results
        self.best_move()
        return self.game_tree.move

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """

        states = {
            1: MCTSAgent._connect,
            2: MCTSAgent._wait_start,
            3: MCTSAgent._make_move,
            4: MCTSAgent._wait_message,
            5: MCTSAgent._close
        }

        # noinspection PyArgumentList
        res = states[1](self)
        while res:
            # noinspection PyArgumentList
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((MCTSAgent.HOST, MCTSAgent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if data[0] == "START":
            # init game with data from server
            self._board_size = int(data[1])
            self._board = zeros((self._board_size, self._board_size), dtype=int)
            self._colour = data[2]

            if self._colour == "R":
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        start_time = time()

        if self._turn_count == 2 and self.swap_logic():
            msg = "SWAP\n"
        else:
            # chose a move and send to server
            move = self.make_first_move() if self._turn_count == 1 else\
                self.make_mcts_choice(self.choose_turn_time(), start_time)
            msg = f"{move[0]},{move[1]}\n"

        self._s.sendall(bytes(msg, "utf-8"))

        self.time_taken_s += time() - start_time
        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if data[0] == "END" or data[-1] == "END":
            return 5
        else:

            if data[1] == "SWAP":
                self._colour = opp_colour(self._colour)
            else:
                # update game board
                x, y = data[1].split(",")
                self.prev_move = (int(x), int(y))
                self._board[self.prev_move] = self.PLAYERS[opp_colour(data[-1])]

            if data[-1] == self._colour:
                sel = [t for t in self.game_tree.children if t.move == self.prev_move]
                if len(sel):
                    self.game_tree = sel[0]
                    self.game_tree.parent = None
                else:
                    self.game_tree = Tree(self.prev_move)
                return 3

        return 4

    def _close(self):
        """Closes the socket."""

        self._s.close()
        return 0


if __name__ == "__main__":
    agent = MCTSAgent()
    agent.run()
