#include "board.hpp"

GameBoard::GameBoard(int boardSize)
{
    size = boardSize;
    tiles = new board_tile[size][size];
}
