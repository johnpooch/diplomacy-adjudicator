class State:

    def __init__(self):
        self.subscribers = set()

    def register(self, observer):
        self.subscribers.add(observer)

    @property
    def pieces(self):
        return [s for s in self.subscribers if s.__class__.__name__ == 'Piece']

    @property
    def territories(self):
        return [s for s in self.subscribers if s.__class__.__name__ == 'Territory']

    @property
    def named_coasts(self):
        return [s for s in self.subscribers if s.__class__.__name__ == 'NamedCoast']
