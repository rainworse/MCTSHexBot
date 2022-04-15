public class MCTSdata
{
    public MCTStree rootTree;
    public HexBoard board;
    public Move prev_move;
    public int turn_count;
    public int board_size;
    public int mcts_calls;
    public char colour;

    public MCTSdata()
    {
        rootTree = new MCTStree();
        board = null;
        prev_move = null;
        turn_count = 0;
        colour = '0';
        board_size = 0;
        mcts_calls = 0;
    }

    public void initializeData(int board_size, char colour)
    {
        this.board_size = board_size;
        this.colour = colour;

        board = new HexBoard(board_size);
    }
}
