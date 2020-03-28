from . import decisions
from .decisions import Outcomes


class Order:

    def __init__(self, nation, source):
        self.nation = nation
        self.source = source
        self.piece = None
        self.hold_support_orders = set()

    def __getattr__(self, name):
        """
        Adds the ability to ask an order what type it is using the syntax
        `order.is_<order_subclass>`.
        """
        subclasses = Order.__subclasses__()
        for s in subclasses:
            if name == 'is_' + s.__name__.lower():
                return isinstance(self, s)
        raise AttributeError(
            f'{self.__class__.__name__} has no attribute \'{name}\'.'
        )

    # TODO test
    def hold_support(self, *args):
        legal_decisions = [Outcomes.LEGAL]
        return [s for s in self.hold_support_orders if
                s.support_decision() in args and s.legal_decision() in legal_decisions]


class Hold(Order):
    pass


class Move(Order):
    def __init__(self, nation, source, target, target_coast=None, via_convoy=False):
        super().__init__(nation, source)
        self.target = target
        self.target_coast = target_coast
        self.via_convoy = via_convoy
        self.move_support_orders = set()
        self.legal_decision = decisions.MoveLegal(self)
        self.move_decision = decisions.Move(self)
        self.attack_strength_decision = decisions.AttackStrength(self)
        self.prevent_strength_decision = decisions.PreventStrength(self)
        self.path_decision = decisions.Path(self)

    # TODO test
    # TODO DRY
    def move_support(self, *args):
        legal_decisions = [Outcomes.LEGAL]
        return [s for s in self.move_support_orders if
                s.support_decision() in args and s.legal_decision() in legal_decisions]

    def is_head_to_head(self):
        """
        Determine whether the move is a head to head battle, i.e. the target
        piece is trying to move to this territory.

        Returns:
            * `bool`
        """
        opposing_piece = self.target.piece
        if opposing_piece:
            if opposing_piece.order.is_move:
                return opposing_piece.order.target == self
        return False


class Support(Order):
    def __init__(self, nation, source, aux, target):
        super().__init__(nation, source)
        self.aux = aux
        self.target = target
        self.legal_decision = decisions.SupportLegal(self)
        self.support_decision = decisions.Support(self)


class Convoy(Order):
    def __init__(self, nation, source, aux, target):
        super().__init__(nation, source)
        self.aux = aux
        self.target = target
        self.legal_decision = decisions.ConvoyLegal(self)
