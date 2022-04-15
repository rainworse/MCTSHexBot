import java.net.*;
import java.util.*;
import java.io.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

class MCTSJavagent
{
    public static String HOST = "127.0.0.1";
    public static int PORT = 1234;

    private Socket s;
    private PrintWriter out;
    private BufferedReader in;

    MCTSdata data = new MCTSdata();

    private void Connect() throws UnknownHostException, IOException
    {
        s = new Socket(HOST, PORT);
        out = new PrintWriter(s.getOutputStream(), true);
        in = new BufferedReader(new InputStreamReader(s.getInputStream()));
    }

    private String getMessage() throws IOException
    {
        return in.readLine();
    }

    private void sendMessage(String msg)
    {
        out.print(msg); out.flush();
    }

    private void closeConnection() throws IOException
    {
        s.close();
        out.close();
        in.close();
    }

    public void run()
    {
        // connect to the engine
        try
        {
            Connect();
        }

        catch (UnknownHostException e)
        {
            System.out.println("ERROR: Host not found.");
            return;
        }

        catch (IOException e)
        {
            System.out.println("ERROR: Could not establish I/O.");
            return;
        }

        while (true)
        {
            // receive messages
            try
            {
                String msg = getMessage();
                boolean res = interpretMessage(msg);

                if (res == false)
                {
                    break;
                }
            }

            catch (IOException e)
            {
                System.out.println("ERROR: Could not establish I/O.");
                return;
            }
        }

        try
        {
            closeConnection();
        }

        catch (IOException e)
        {
            System.out.println("ERROR: Connection was already closed.");
        }
    }

    private boolean interpretMessage(String s)
    {
        data.turn_count++;
        String[] msg = s.strip().split(";");
        switch (msg[0])
        {
            case "START":
                data.initializeData(Integer.parseInt(msg[1]), msg[2].charAt(0));
                if (data.colour == 'R')
                {
                    makeMove();
                }

                break;

            case "CHANGE":
                if (msg[3].equals("END")) return false;
                if (msg[1].equals("SWAP"))
                {
                    data.colour = MCTSutils.otherPlayer(data.colour);

                    if (msg[3].charAt(0) == data.colour)
                    {
                        makeMove();
                    }
                }

                else if (msg[3].charAt(0) == data.colour)
                {
                    String[] coordinates = msg[1].split(",");
                    data.board.getBoard()[Integer.parseInt(coordinates[0])][Integer.parseInt(coordinates[1])] = MCTSutils.otherPlayer(data.colour);
                    Move opponentMove = new Move(Integer.parseInt(coordinates[0]), Integer.parseInt(coordinates[1]));
                    data.prev_move = opponentMove;
                    int i = 0;
                    while(i < data.rootTree.getChildren().size())
                    {
                        if (data.rootTree.getChildren().get(i).getMove().equals(opponentMove))
                        {
                            data.rootTree = data.rootTree.getChildren().get(i);
                            data.rootTree.setAsRoot();
                            break;
                        }
                        i++;
                    }

                    makeMove();
                }

                else if (msg[3].charAt(0) == MCTSutils.otherPlayer(data.colour))
                {
                    String[] coordinates = msg[1].split(",");
                    data.board.getBoard()[Integer.parseInt(coordinates[0])][Integer.parseInt(coordinates[1])] = data.colour;
                    data.prev_move = new Move(Integer.parseInt(coordinates[0]), Integer.parseInt(coordinates[1]));
                }
                break;

            default:
                return false;
        }

        return true;
    }

    private void makeMove()
    {
        if (data.turn_count == 2 && doSwap())
        {
            sendMessage("SWAP\n");
            return;
        }

        if (data.rootTree.getChildren().size() > 0)
        {
            int threads = Runtime.getRuntime().availableProcessors();

            int childPartitionSize = data.rootTree.getChildren().size() / threads;
            List<MCTSdata> threadData = new ArrayList<>();
            for (int i = 0; i < threads; i++)
            {
                MCTSdata tdata = new MCTSdata();
                tdata.turn_count = data.turn_count;
                threadData.add(tdata);
                tdata.initializeData(data.board_size, data.colour);
                List<MCTStree> newChildren = new ArrayList<>();
                for (int j = childPartitionSize * i; j < childPartitionSize * (i + 1); j++)
                {
                    MCTStree child = data.rootTree.getChildren().get(j);
                    child.setParent(tdata.rootTree);
                    newChildren.add(child);
                }
            }

            ExecutorService es = Executors.newCachedThreadPool();
            for (int i = 0; i < threads; i++)
            {
                es.execute(new MoveSearching(threadData.get(i)));
            }

            es.shutdown();
            try
            {
                es.awaitTermination(15, TimeUnit.SECONDS);
            }

            catch (InterruptedException e) {}

            for (MCTSdata tdata : threadData)
            {
                for (MCTStree child : tdata.rootTree.getChildren())
                {
                    child.setParent(data.rootTree);
                }

                data.rootTree.setVisits(data.rootTree.getVisits() + tdata.rootTree.getVisits());
                data.rootTree.setScore(data.rootTree.getScore() + tdata.rootTree.getScore());
            }

            data.rootTree = bestMove(data.rootTree);
            data.rootTree.setAsRoot();
        }

        else
        {
            MoveSearching search = new MoveSearching(data);
            search.makeMCTSchoice();
            data.rootTree = bestMove(data.rootTree);
            data.rootTree.setAsRoot();
        }

        String msg = "" + data.rootTree.getMove().getRow() + "," + data.rootTree.getMove().getCol() + "\n";
        sendMessage(msg);
    }

    private MCTStree bestMove(MCTStree node)
    {
        Map<Double, MCTStree> moves = new HashMap<>();
        double maxVal = Double.NEGATIVE_INFINITY;

        for (MCTStree child : node.getChildren())
        {
            double ucb = child.getUcbScore(false, 1, 0);

            if (ucb > maxVal)
            {
                maxVal = ucb;
                moves.put(ucb, child);
            }
        }

        return moves.get(maxVal);
    }

    private boolean doSwap()
    {
        Set<String> swapMoves = getSwapMoves();
        String prevMove = data.board_size + "x" + data.board_size + " " + moveIntToChar(data.prev_move.getRow()) + (data.prev_move.getCol() + 1);

        return swapMoves.contains(prevMove);
    }

    private Set<String> getSwapMoves()
    {
        Set<String> swapMoves = new HashSet<>();
        try
        {
            BufferedReader br = new BufferedReader(new FileReader("./agents/Group031/swap_moves.txt"));
            String line = br.readLine();

            while (line != null)
            {
                swapMoves.add(line);
                line = br.readLine();
            }

        }

        catch (FileNotFoundException e) {}
        catch (IOException e) {}

        return swapMoves;
    }

    private char moveIntToChar(int moveInt)
    {
        char c = ' ';

        switch (moveInt)
        {
            case 0:
                c = 'a';
                break;

            case 1:
                c = 'b';
                break;

            case 2:
                c = 'c';
                break;

            case 3:
                c = 'd';
                break;

            case 4:
                c = 'e';
                break;

            case 5:
                c = 'f';
                break;

            case 6:
                c = 'g';
                break;

            case 7:
                c = 'h';
                break;

            case 8:
                c = 'i';
                break;

            case 9:
                c = 'j';
                break;

            case 10:
                c = 'k';
                break;

            default:
                break;
        }

        return c;
    }



    public static void main(String args[])
    {
        MCTSJavagent agent = new MCTSJavagent();
        agent.run();
    }
}