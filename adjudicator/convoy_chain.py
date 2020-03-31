from adjudicator.decisions import Outcomes


class ConvoyChain:
    """
    Represents a chain of one or more fleet paths which are attempting to
    convoy an army from a source to a destination.
    """

    def __init__(self, fleets):
        self.fleets = fleets
        self.result = UNRESOLVED
