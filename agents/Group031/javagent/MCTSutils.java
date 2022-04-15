import java.util.*;

public abstract class MCTSutils
{
    private static Set<Move> neighbourIndices = null;
    private static final char emptyTile = '0';

    public static Character otherPlayer(Character player)
    {
        if (player == 'R')
        {
            return 'B';
        }

        else if (player == 'B')
        {
            return 'R';
        }

        return '0';
    }

    public static Set<Move> validMoves(HexBoard board)
    {
        Set<Move> moves = new HashSet<>();

        for (int i = 0; i < board.getBoardSize(); i++)
        {
            for (int j = 0; j < board.getBoardSize(); j++)
            {
                if (board.getBoard()[i][j] == emptyTile)
                {
                    moves.add(new Move(i, j));
                }
            }
        }

        return moves;
    }

    public static boolean boardHasWinner(HexBoard board)
    {
        return playerIsWinner(board, new Player('R')) || playerIsWinner(board, new Player('B'));
    }

    public static boolean playerIsWinner(HexBoard board, Player player)
    {
        List<Move> start = new ArrayList<>();
        List<Move> end = new ArrayList<>();

        Queue<Move> discovered = new LinkedList<>();

        int boardOffset = board.getBoardSize() - 1;

        if (player.getColour() == 'R')
        {
            for (int i = 0; i < board.getBoardSize(); i++)
            {
                if (board.getBoard()[0][i] == player.getColour())
                {
                    Move m = new Move(0, i);
                    start.add(m);
                    discovered.add(m);
                }

                if (board.getBoard()[boardOffset][i] == player.getColour())
                {
                    end.add(new Move(boardOffset, i));
                }
            }
        }

        else if (player.getColour() == 'B')
        {
            for (int i = 0; i < board.getBoardSize(); i++)
            {
                if (board.getBoard()[i][0] == player.getColour())
                {
                    Move m = new Move(i, 0);
                    start.add(m);
                    discovered.add(m);
                }

                if (board.getBoard()[i][boardOffset] == player.getColour())
                {
                    end.add(new Move(i, boardOffset));
                }
            }
        }

        if (start.size() > 0 && end.size() > 0)
        {
            Set<Move> explored = new HashSet<>();

            while (discovered.size() > 0)
            {
                Move move = discovered.poll();

                Set<Move> similarNeighbours = similarNeighbours(board, move, player);
                for (Move neighbour : similarNeighbours)
                {
                    if (!(discovered.contains(neighbour) || explored.contains(neighbour)))
                    {
                        discovered.add(neighbour);
                    }

                    if (player.getColour() == 'R' && neighbour.getRow() == boardOffset)
                    {
                        return true;
                    }

                    else if (player.getColour() == 'B' && neighbour.getCol() == boardOffset)
                    {
                        return true;
                    }
                }

                explored.add(move);
            }
        }

        return false;
    }

    private static Set<Move> similarNeighbours(HexBoard board, Move move, Player player)
    {
        if (neighbourIndices == null)
        {
            neighbourIndices = new HashSet<>();
            neighbourIndices.add(new Move(0, -1));
            neighbourIndices.add(new Move(1, -1));
            neighbourIndices.add(new Move(1, 0));
            neighbourIndices.add(new Move(0, 1));
            neighbourIndices.add(new Move(-1, 1));
            neighbourIndices.add(new Move(-1, 0));
        }

        Set<Move> similarNeighbours = new HashSet<>();

        for (Move neighbour : neighbourIndices)
        {
            if (neighbourOnBoard(move, neighbour, board.getBoardSize()) &&
            board.getBoard()[move.getRow() + neighbour.getRow()][move.getCol() + neighbour.getCol()] == player.getColour())
            {
                similarNeighbours.add(new Move(move.getRow() + neighbour.getRow(), move.getCol() + neighbour.getCol()));
            }
        }

        return similarNeighbours;
    }

    private static boolean neighbourOnBoard(Move move, Move neighbour, int boardSize)
    {
        int neighbourRow = move.getRow() + neighbour.getRow();
        int neighbourCol = move.getCol() + neighbour.getCol();

        return neighbourRow >= 0 && neighbourRow < boardSize && neighbourCol >= 0 && neighbourCol < boardSize;
    }
}
