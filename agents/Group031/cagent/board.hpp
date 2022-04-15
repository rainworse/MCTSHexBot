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
    GameBoard(int boardSize);

    public:
    int size;
    board_tile **tiles;
};
