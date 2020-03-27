from adjudicator.named_coast import NamedCoast
from adjudicator.order import Order, Move
from adjudicator.piece import Piece
from adjudicator.territory import CoastalTerritory, Territory


class State:

    def __init__(self):
        self.subscribers = set()

    def register(self, *observers):
        for observer in observers:
            self.subscribers.add(observer)
            self._update_territory_piece(observer)
            self._update_neighbours(observer)
            self._update_shared_coasts(observer)
            self._update_piece_order(observer)
            self._update_territory_named_coasts(observer)
            self._update_territory_attacking_pieces(observer)

    @property
    def pieces(self):
        return [s for s in self.subscribers if isinstance(s, Piece)]

    @property
    def territories(self):
        return [s for s in self.subscribers if isinstance(s, Territory)]

    @property
    def named_coasts(self):
        return [s for s in self.subscribers if isinstance(s, NamedCoast)]

    def _update_territory_piece(self, observer):
        """
        Update the piece attribute of all territories.
        """
        if isinstance(observer, Piece):
            for t in self.territories:
                if observer.territory == t:
                    t.piece = observer

    def _update_neighbours(self, observer):
        """
        Update the neighbours of all territories in the state .
        """
        if isinstance(observer, Territory):
            for t in self.territories:
                if t.id in observer.neighbour_ids:
                    observer.neighbours.add(t)
                    t.neighbours.add(observer)

    def _update_shared_coasts(self, observer):
        """
        Update the shared coasts of all coastal territories in the state.
        """
        if isinstance(observer, CoastalTerritory):
            for t in self.territories:
                if t.id in observer.shared_coast_ids:
                    observer.shared_coasts.add(t)
                    t.shared_coasts.add(observer)

    def _update_piece_order(self, observer):
        """
        Update the `order` attribute of the piece associated with the order.
        """
        if isinstance(observer, Order):
            for p in self.pieces:
                if p.territory == observer.source:
                    observer.piece = p
                    p.order = observer

    def _update_territory_named_coasts(self, observer):
        """
        Update the named coasts of all territories.
        """
        if isinstance(observer, NamedCoast):
            for t in self.territories:
                if observer.parent == t:
                    t.named_coasts.add(observer)

    def _update_territory_attacking_pieces(self, observer):
        """
        Update the attacking_pieces of the target the move order.
        """
        if isinstance(observer, Move) and observer.piece:
            for t in self.territories:
                if t == observer.target:
                    t.attacking_pieces.add(observer.piece)
