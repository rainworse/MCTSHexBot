import socket
import sys
from random import choice
from time import sleep
from copy import deepcopy


class NaiveAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
        
        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []
        
        states = {
            1: NaiveAgent._connect,
            2: NaiveAgent._wait_start,
            3: NaiveAgent._make_move,
            4: NaiveAgent._wait_message,
            5: NaiveAgent._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """
        
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((NaiveAgent.HOST, NaiveAgent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            self._board = [ [0] * self._board_size for i in range(self._board_size)]
            for i in range(self._board_size):
                for j in range(self._board_size):
                    self._choices.append((i, j))

            self._colour = data[2]
            self.simulate_game()
            if (self._colour == "R"):
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """

        if (self._turn_count == 2 and choice([0, 1]) == 1):
            msg = "SWAP\n"
        else:
            move = choice(self._choices)
            msg = f"{move[0]},{move[1]}\n"
        
        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:

            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                self._choices.remove((int(x), int(y)))

            if (data[-1] == self._colour):
                return 3

        return 4

    def _close(self):
        """Closes the socket."""

        self._s.close()
        return 0

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        
        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"



    def simulate_game(self):

        currentTurn = self._colour
        simulationChoices = deepcopy(self._choices)
        simulationBoard = deepcopy(self._board)
        simulationEnd = False

        while (not simulationEnd and len(simulationChoices) > 0):
            move = choice(simulationChoices)
            simulationBoard[move[0]][move[1]] = currentTurn
            simulationChoices.remove((move[0], move[1]))
            simulationEnd = self.check_game_end(simulationBoard, move)

            if (simulationEnd):
                print ("Simulation winner: " + currentTurn)

            if (currentTurn == self._colour):
                currentTurn = self.opp_colour()

            else:
                currentTurn = self._colour



    def check_game_end(self, board, lastMove):

        moveColor = board[lastMove[0]][lastMove[1]]

        start = []
        end = []

        if (moveColor == "R"):
            start = [board[0][i] for i in range(len(board))]
            end = [board[len(board) - 1][i] for i in range(len(board))]

        else:
            start = [board[i][0] for i in range(len(board))]
            end = [board[i][len(board) - 1] for i in range(len(board))]

        if (moveColor in start and moveColor in end):
            startFound = False
            endFound = False

            if (moveColor == "R"):
                if (lastMove[0] == 0):
                    startFound = True
                elif (lastMove[0] == len(board) - 1):
                    endFound = True
            else:
                if (lastMove[1] == 0):
                    startFound = True
                elif (lastMove[1] == len(board) - 1):
                    endFound = True

            discovered = []
            explored = []

            discovered.append(lastMove)

            while (len(discovered) > 0):
                move = discovered.pop()
                neighbours = (self.similar_neighbours(board, move))

                for neighbourtile in neighbours:
                    if (moveColor == "R"):
                        if (neighbourtile[0] == 0):
                            if (endFound):
                                return True
                            else:
                                startFound = True
                        elif (neighbourtile[0] == len(board) - 1):
                            if (startFound):
                                return True
                            else:
                                endFound = True


                    elif (moveColor == "B"):
                        if (neighbourtile[1] == 0):
                            if (endFound):
                                return True
                            else:
                                startFound = True
                        elif (neighbourtile[1] == len(board) - 1):
                            if (startFound):
                                return True
                            else:
                                endFound = True


                    if neighbourtile not in discovered and neighbourtile not in explored:
                        discovered.append(neighbourtile)

                explored.append(move)

        return False



    def similar_neighbours(self, board, move):

        tileColor = board[move[0]][move[1]]
        similarNeighbours = []

        if (move[0] > 0):
            if (board[move[0] - 1][move[1]] == tileColor):
                similarNeighbours.append((move[0] - 1, move[1]))

            if (move[1] < len(board) - 1 and board[move[0] - 1][move[1] + 1] == tileColor):
                similarNeighbours.append((move[0] - 1, move[1] + 1))

        if (move[1] < len(board) - 1):
            if (board[move[0]][move[1] + 1] == tileColor):
                similarNeighbours.append((move[0], move[1] + 1))

        if (move[0] < len(board) - 1):
            if (board[move[0] + 1][move[1]] == tileColor):
                similarNeighbours.append((move[0] + 1, move[1]))

            if (move[1] > 0 and board[move[0] + 1][move[1] - 1] == tileColor):
                similarNeighbours.append((move[0] + 1, move[1] - 1))

        if (move[1] > 0):
            if (board[move[0]][move[1] - 1] == tileColor):
                similarNeighbours.append((move[0], move[1] - 1))

        return similarNeighbours



    def printBoard(self, board):

        b = ""
        for i in range (len(board)):
            s = ""
            for j in range(i):
                s += " "

            for j in range(len(board[i])):
                s += str(board[i][j])
                s += " "

            b += s
            b += "\n"

        return b



if (__name__ == "__main__"):
    agent = NaiveAgent()
    agent.run()
