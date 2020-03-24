class DefendStrength(Decision):
    """
    For each piece ordered to move in a head to head battle, the strength to
    defend its own territory from the other piece of the head to head battle. A
    decision that results in a value equal or greater than zero.
    """
    def __init__(self, move):
        self.move = move
        self.result = UNRESOLVED

    def _minimum(self):
        return 1 + len(self.move.move_support(GIVEN))

    def _maximum(self):
        return 1 + len(self.move.move_support(GIVEN, UNRESOLVED))
