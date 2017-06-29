
from swap.utils.scores import ScoreIterator


class History:

    def __init__(self, id_, gold, score_history):
        """
        Parameters
        ----------
        id_ : int
            Subject it
        gold : int
            Subject gold label 1, 0, or -1
        scores : list
            List of score history for subject [0.2, 0.1, ...]
        """
        self.id = id_
        self.gold = gold
        self.scores = score_history


class HistoryExport:

    def __init__(self, history):
        """
        Parameters
        ----------
        history : dict
            Mapping of Subject History to subject id
        """
        self.history = history

    def get(self, id_):
        return self.history[id_]

    def traces(self):

        def func(history):
            return (history.gold, history.scores)

        return ScoreIterator(self.history, func)

    def __iter__(self):

        def func(history):
            return (history.id, history.gold, history.scores)
        return ScoreIterator(self.history, func)
