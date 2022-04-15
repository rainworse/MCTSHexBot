import java.util.Objects;

public class Move
{
    private final int r;
    private final int c;

    public Move(int r, int c)
    {
        this.r = r;
        this.c = c;
    }

    public int getRow()
    {
        return r;
    }

    public int getCol()
    {
        return c;
    }

    @Override
    public int hashCode() {
        return Objects.hash(r, c);
    }

    @Override
    public boolean equals(Object obj)
    {
        if (obj instanceof Move)
        {
            Move other = (Move) obj;

            return r == other.getRow() && c == other.getCol();
        }

        return false;
    }
}
