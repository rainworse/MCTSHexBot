import java.util.Objects;

public class Player
{
    private char colour;

    public Player(char p)
    {
        colour = p;
    }

    public char getColour()
    {
        return colour;
    }

    public void setColour(char p)
    {
        colour = p;
    }

    @Override
    public int hashCode()
    {
        return Objects.hash(colour);
    }

    @Override
    public boolean equals(Object obj)
    {
        if (obj instanceof Player)
        {
            Player other = (Player) obj;
            return colour == other.getColour();
        }

        return false;
    }
}
