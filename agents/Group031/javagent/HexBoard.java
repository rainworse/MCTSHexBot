public class HexBoard
{
    private final int board_size;
    private char[][] board;

    public HexBoard(int board_size)
    {
        board = new char[board_size][board_size];
        this.board_size = board_size;
        newBoard();
    }

    public HexBoard(HexBoard hexBoard)
    {
        board_size = hexBoard.getBoardSize();
        board = new char[board_size][board_size];

        for (int i = 0; i < board_size; i++)
        {
            for (int j = 0; j < board_size; j++)
            {
                board[i][j] = hexBoard.getBoard()[i][j];
            }
        }
    }

    private void newBoard()
    {
        for (int i = 0; i < board_size; i++)
        {
            for (int j = 0; j < board_size; j++)
            {
                board[i][j] = '0';
            }
        }
    }

    public void moveMade(Move move, char colour)
    {
        board[move.getRow()][move.getCol()] = colour;
    }

    public char[][] getBoard()
    {
        return board;
    }

    public int getBoardSize()
    {
        return board_size;
    }

    @Override
    public String toString(){
        StringBuilder board = new StringBuilder();
        for(int i =0; i < this.board.length; i++) {
            String padding = new String(new char[i]).replace("\0", " ");
            board.append(padding);

            for(char cell : this.board[i]) {
                if (cell=='0') board.append("o ");
                else board.append(cell).append(" ");
            }

            board.append("\n");
        }
        return board.toString();
    }
}
