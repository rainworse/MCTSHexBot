import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;

public class MCTStree
{
    private int visits = 0;
    private int score = 0;
    private MCTStree parent = null;
    private List<MCTStree> children = new ArrayList<>();
    private Move move = null;

    public MCTStree()
    {

    }

    public MCTStree(MCTStree parent, Move move)
    {
        this.parent = parent;
        this.move = move;
    }

    public int getVisits()
    {
        return visits;
    }

    public void setVisits(int visits)
    {
        this.visits = visits;
    }

    public int getScore()
    {
        return score;
    }

    public void setScore(int score)
    {
        this.score = score;
    }

    public MCTStree getParent()
    {
        return parent;
    }

    public void setParent(MCTStree parent)
    {
        this.parent = parent;
    }

    public void setChildren(List<MCTStree> children)
    {
        this.children = children;
    }

    public List<MCTStree> getChildren()
    {
        return children;
    }

    public void removeChild(MCTStree child)
    {
        if (children.remove(child))
        {
            for (MCTStree tree : children)
            {
                tree.removeChild(child);
            }
        }
    }

    public Move getMove()
    {
        return move;
    }

    public void setAsRoot()
    {
        parent = null;
    }

    public void incrementVisits()
    {
        visits++;
    }

    public void addScore(int score)
    {
        this.score += score;
    }

    public double getUcbScore(boolean explore, int multiplier, double exploit)
    {
        if (visits > 0)
        {
            double exploitation = multiplier * ((double) score) / ((double) visits);

            if (explore)
            {
                double exploration = exploit * Math.sqrt(Math.log(parent.getVisits()) / visits);
                return exploration + exploitation;
            }

            return exploitation;
        }

        if (explore)
        {
            return 100.0;
        }

        return -100.0;
    }

    @Override
    public int hashCode()
    {
        return Objects.hash(visits, score, parent, children, move);
    }

    @Override
    public boolean equals(Object obj)
    {
        if (obj instanceof MCTStree)
        {
            MCTStree other = (MCTStree) obj;
            return (move != null && other.getMove() != null && move.equals(other.getMove())) &&
                    visits == other.getVisits() && score == other.getScore();
        }

        return false;
    }
}