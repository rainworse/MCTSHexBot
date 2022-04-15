#include <stdlib.h>
#include <time.h>
#include <utility>
#include <iostream>
#include <string>

/*
 * 2-bit struct to store if tile has been occupied or not.
 * Unoccupied:    0
 * Occupied by R: 1
 * Occupied by B: 2
 */

struct board_tile
{
    unsigned int occupied_by: 2;
};



class GameBoard
{
    public:
    GameBoard(int boardSize)
    {
        size = boardSize;
        tiles = new board_tile[boardSize][boardSize];
    }

    public:
    int size;
    board_tile **tiles;
};



extern "C"
{
    int swap()
    {
        srand(time(NULL));
        return rand() % 2;
    }

    void makeMove(int *x, int *y, int availableX[], int availableY[], 
		  int xamount, int yamount, int boardSize, wchar_t *board)
    {
        srand(time(NULL));
        *x = availableX[rand() % xamount];
        *y = availableY[rand() % xamount];

        GameBoard gameBoard(boardSize);
        std::cout << gameBoard.size << std::endl;
    }
}
