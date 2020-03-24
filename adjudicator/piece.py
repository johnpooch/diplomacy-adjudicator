from .state import state
from .order import Hold


class Piece:
    all_pieces = []

    def __init__(self, nation, territory):
        state.all_pieces.append(self)
        self.nation = nation
        self.territory = territory
        self._order = None

    # TODO test
    def __str__(self):
        return f'{self.__class__.__name__} {self.territory}'

    # TODO test
    def __repr__(self):
        return f'{self.__class__.__name__} {self.territory}'

    @property
    def order(self):
        """
        Gets the `Order` which is assigned to this piece.
        Returns:
            * `Order`
        """
        if not self._order:
            for o in state.all_orders:
                if o.source == self.territory:
                    self._order = o
            if not self._order:
                self._order = Hold(self.nation, self.territory)
        return self._order

    def moves(self):
        pass


class Army(Piece):

    def can_reach(self, target):
        """
        Determines whether the army can reach the given territory, regardless of whether the necessary conoying fleets exist or not.

        * Args `target` - `territory`
        Returns Bool
        """

        if self.territory.is_coastal and target.is_coastal:
            return True

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    # TODO move to decisions


class Fleet(Piece):

    def __init__(self, nation, territory, named_coast=None):
        super().__init__(nation, territory)  # DRY - do not repeat yourself
        self.named_coast = named_coast

    def can_reach(self, target, named_coast=None):
        """
        Determines whether the fleet can reach the given territory and named
        coast.

        Args:
            * `target` - `Territory`
            * `[named_coast]` - `NamedCoast`

        Returns:
            * `bool`
        """
        if target.is_complex and not named_coast:
            raise ValueError(
                'Must specify coast if target is complex territory.'
            )
        if named_coast:
            return self.territory in named_coast.neighbours

        if self.territory.is_complex:
            return target in self.named_coast.neighbours

        if self.territory.is_coastal and target.is_coastal:
            return target in self.territory.shared_coasts

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    # TODO move to decisions
