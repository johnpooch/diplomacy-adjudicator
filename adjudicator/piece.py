from adjudicator.decisions import Outcomes


class Piece:

    is_army = False
    is_fleet = False

    def __init__(self, nation, territory):
        self.nation = nation
        self.territory = territory
        self.order = None
        self.dislodged_decision = Outcomes.UNRESOLVED
        self.dislodged_by = None

    # TODO test
    def __str__(self):
        return f'{self.__class__.__name__} {self.territory}'

    # TODO test
    def __repr__(self):
        return f'{self.__class__.__name__} {self.territory}'

    def moves(self):
        pass

    def set_dislodged_decision(self, outcome, dislodged_by=None):
        self.dislodged_decision = outcome
        self.dislodged_by = dislodged_by
        return self.dislodged_decision

    def update_dislodged_decision(self):
        attacking_pieces = list(self.territory.attacking_pieces)

        # sustains if...
        if not attacking_pieces:
            return self.set_dislodged_decision(Outcomes.SUSTAINS)
        if self.order.is_move:
            # cannot be dislodged if successfully moved
            if self.order.move_decision == Outcomes.MOVES:
                return self.set_dislodged_decision(Outcomes.SUSTAINS)
        # TODO this is messy
        if [p for p in attacking_pieces if p.order.move_decision == Outcomes.FAILS] \
                and all([p.order.move_decision == Outcomes.FAILS for p in attacking_pieces]):
            return self.set_dislodged_decision(Outcomes.SUSTAINS)

        # dislodged if...
        if self.order.is_move:
            if self.order.move_decision == Outcomes.FAILS and \
                    any([p for p in attacking_pieces if p.order.move_decision == Outcomes.MOVES]):
                piece = [p for p in attacking_pieces if p.order.move_decision == Outcomes.MOVES][0]
                return self.set_dislodged_decision(Outcomes.DISLODGED, piece)
        else:
            if any([p.order.move_decision == Outcomes.MOVES for p in attacking_pieces]):
                piece = [p for p in attacking_pieces
                         if p.order.move_decision == Outcomes.MOVES][0]
                return self.set_dislodged_decision(Outcomes.DISLODGED, piece)


class Army(Piece):

    is_army = True

    def can_reach(self, target, *args):
        """
        Determines whether the army can reach the given territory, regardless
        of whether the necessary convoying fleets exist or not.

        * Args:
            * `target` - `territory`

        Returns:
            * `bool`
        """

        if self.territory.is_coastal and target.is_coastal:
            return True

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    def can_reach_support(self, target):
        """
        Determines whether the army can reach the given territory in the
        context of providing support. Cannot provide support through a convoy.

        * Args:
            * `target` - `territory`

        Returns:
            * `bool`
        """
        return self.territory.adjacent_to(target) and \
               target.accessible_by_piece_type(self)

    # TODO move to decisions


class Fleet(Piece):

    is_fleet = True

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

    def can_reach_support(self, target):
        """
        Determines whether the fleet can reach the given territory in the
        context of providing support. In this context the fleet does not need
        to be able to reach the target named coast.

        * Args:
            * `target` - `territory`

        Returns:
            * `bool`
        """
        if self.territory.is_complex:
            return target in self.named_coast.neighbours

        if self.territory.is_coastal and target.is_coastal:
            return target in self.territory.shared_coasts

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)
