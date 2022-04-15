#!/usr/bin/python3

import socket
from random import choice
from time import sleep
from copy import deepcopy
from ctypes import *


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

        self.clib = cdll.LoadLibrary('./agents/Group031/cagent.so')

        self._board_size = 0
        self._board = ""
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
            for i in range(self._board_size):
                for j in range(self._board_size):
                    self._choices.append((i, j))
                if (i == self._board_size - 1):
                    self._board += "00000000000"
                else:
                    self._board += "00000000000,"
                    
            self._colour = data[2]

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
        
        msg = ""
        if (self._turn_count == 2):
            swap = self.clib.swap;
            if (swap() == 1):
                msg = "SWAP\n"

        else:
            xmove = c_int(0)
            ymove = c_int(0)

            availablexmoves = [x[0] for x in self._choices]
            availableymoves = [y[1] for y in self._choices]

            self.clib.makeMove(byref(xmove), byref(ymove), (c_int * len(availablexmoves))(*availablexmoves), (c_int * len(availableymoves))(*availableymoves), c_int(len(availablexmoves)), c_int(len(availableymoves)), c_int(self._board_size), c_wchar_p(self._board))

            msg = f"{xmove.value},{ymove.value}\n"

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
                self._board = data[2]

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


if (__name__ == "__main__"):
    agent = NaiveAgent()
    agent.run()
