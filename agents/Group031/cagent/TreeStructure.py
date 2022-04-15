from numpy import sqrt, log


class Tree:
    def __init__(self, mv=None, par=None):
        self.visits = 0
        self.score = 0
        self.parent = par
        self.children = []
        self.move = mv

    def get_ucb_score(self, explore, multiplier, exploit):
        if self.visits:
            exploitation = multiplier * self.score / self.visits
            if explore:
                exploration = exploit * sqrt(log(self.parent.visits) / self.visits)
                return exploitation + exploration
            else:
                return exploitation
        else:
            return 100 * explore
