import java.util.*;

public class MoveSearching implements Runnable
{
    private MCTSdata data;

    public MoveSearching(MCTSdata data)
    {
        this.data = data;
    }

    @Override
    public void run()
    {
        makeMCTSchoice();
    }

    public void makeMCTSchoice()
    {
        long start_time = System.currentTimeMillis();
        int time_limit = 6000;
        if (data.turn_count < 20)
        {
            time_limit = 10000;
        }

        if (data.turn_count > 60)
        {
            time_limit = 4000;
        }

        if (data.turn_count > 80)
        {
            time_limit = 2000;
        }


        while ((System.currentTimeMillis() - start_time) < time_limit)
        {
            searchMoves();
        }
    }

    private void searchMoves()
    {
        HexBoard simulationBoard = new HexBoard(data.board);
        Player player = new Player(data.colour);
        MCTStree node = selectMove(simulationBoard, player);
        node = expandMove(simulationBoard, player, node);
        Player winner = simulateGame(simulationBoard, player);
        backpropagate(node, winner);
    }

    private MCTStree selectMove(HexBoard board, Player player)
    {
        MCTStree node = data.rootTree;

        while (node.getChildren() != null && node.getChildren().size() > 0)
        {
            Map<Double, MCTStree> nodes = new HashMap<>();
            double maxVal = Double.NEGATIVE_INFINITY;
            double exploit = player.getColour() == data.colour ? 1.2 : 1.4;
            int multiplier = player.getColour() == data.colour ? 1 : -1;

            for (MCTStree tree : node.getChildren())
            {
                double ucb = tree.getUcbScore(true, multiplier, exploit);

                if (ucb >= maxVal)
                {
                    maxVal = ucb;
                    nodes.put(ucb, tree);
                }
            }

            node = nodes.get(maxVal);
            board.getBoard()[node.getMove().getRow()][node.getMove().getCol()] = player.getColour();
            player.setColour(MCTSutils.otherPlayer(player.getColour()));
        }

        return node;
    }

    private MCTStree expandMove(HexBoard board, Player player, MCTStree node)
    {
        Set<Move> moves = MCTSutils.validMoves(board);

        if (moves.size() == 0 || MCTSutils.boardHasWinner(board))
        {
            return node;
        }

        for (Move move : moves)
        {
            node.getChildren().add(new MCTStree(node, move));
        }

        Random random = new Random();
        MCTStree newNode = node.getChildren().get(random.nextInt(node.getChildren().size()));
        board.getBoard()[newNode.getMove().getRow()][newNode.getMove().getCol()] = player.getColour();
        player.setColour(MCTSutils.otherPlayer(player.getColour()));

        return newNode;
    }

    private Player simulateGame(HexBoard board, Player player)
    {
        List<Move> moves = new ArrayList<>(MCTSutils.validMoves(board));
        Collections.shuffle(moves);

        for (Move move : moves)
        {
            board.getBoard()[move.getRow()][move.getCol()] = player.getColour();
            player.setColour(MCTSutils.otherPlayer(player.getColour()));
        }

        if (MCTSutils.playerIsWinner(board, player))
        {
            return player;
        }

        return new Player(MCTSutils.otherPlayer(player.getColour()));
    }

    private void backpropagate(MCTStree node, Player player)
    {
        int flip = player.getColour() == data.colour ? 1 : -1;

        while (node != null)
        {
            node.incrementVisits();
            node.addScore(flip);
            //flip *= -1;
            node = node.getParent();
        }
    }
}
