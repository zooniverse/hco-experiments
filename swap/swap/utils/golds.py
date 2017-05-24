
import swap.db.classifications as db
import swap.db.controversial as cv


class GoldGetter:

    def __init__(self):
        self.reset()

    def _getter(func):
        def wrapper(self, *args, **kwargs):
            getter = func(self, *args, **kwargs)
            self.getters.append(getter)
            self._golds = None
            return getter
        return wrapper

    @_getter
    def all(self):
        return lambda: db.getAllGolds()

    @_getter
    def random(self, size):
        return lambda: db.getRandomGoldSample(size)

    @_getter
    def subjects(self, subject_ids):
        return lambda: db.getExpertGold(subject_ids)

    @_getter
    def controversial(self, size):
        def f():
            subjects = cv.get_controversial(size)
            return db.getExpertGold(subjects)
        return f

    @_getter
    def consensus(self, size):
        def f():
            consensus = cv.get_consensus(size)
            return db.getExpertGold(consensus)
        return f

    # @_getter
    # def extreme_min(self, n_controv, max_consensus):
    #     def f():
    #         controv = cv.get_controversial(n_controv)
    #         consensus = cv.get_max_consensus(max_consensus)

    #         return db.getExpertGold(controv + consensus)
    #     return f

    # @_getter
    # def extremes(self, n_controv, n_consensus):
    #     def f():
    #         controv = cv.get_controversial(n_controv)
    #         consensus = cv.get_consensus(n_consensus)

    #         return db.getExpertGold(controv + consensus)
    #     return f

    def reset(self):
        self.getters = []
        self._golds = None

    @property
    def golds(self):
        if self._golds is None:
            if len(self.getters) == 0:
                self.all()

            golds = {}
            for getter in self.getters:
                golds.update(getter())

            self._golds = golds
        return self._golds

    def __iter__(self):
        return self.golds
