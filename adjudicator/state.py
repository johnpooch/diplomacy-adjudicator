import json

from adjudicator.convoy_chain import get_convoy_chains
from adjudicator.named_coast import NamedCoast
from adjudicator.order import Convoy, Order, Move, Retreat, Support
from adjudicator.piece import Piece
from adjudicator.territory import CoastalTerritory, Territory


class State:

    def __init__(self):
        self.subscribers = set()

    def register(self, *observers):
        """
        Objects need to registered in the following order:
        `Territory`, `NamedCoast`, `Piece`, `Order`.
        """
        for observer in observers:
            self.subscribers.add(observer)

            if isinstance(observer, Territory):
                self._update_neighbours(observer)

            if isinstance(observer, CoastalTerritory):
                self._update_shared_coasts(observer)

            if isinstance(observer, NamedCoast):
                self._update_territory_named_coasts(observer)

            if isinstance(observer, Piece):
                self._update_territory_piece(observer)

            if isinstance(observer, Order):
                self._update_piece_order(observer)

            if isinstance(observer, Move):
                self._update_territory_attacking_pieces(observer)


            if isinstance(observer, Retreat):
                self._update_territory_retreating_pieces(observer)

    def post_register_updates(self):
        self._update_order_move_support()
        self._update_order_hold_support()
        self._update_convoy_chains()

    @property
    def pieces(self):
        return [s for s in self.subscribers if isinstance(s, Piece)]

    @property
    def territories(self):
        return [s for s in self.subscribers if isinstance(s, Territory)]

    @property
    def named_coasts(self):
        return [s for s in self.subscribers if isinstance(s, NamedCoast)]

    @property
    def orders(self):
        return [s for s in self.subscribers if isinstance(s, Order)]

    @property
    def moves(self):
        return [s for s in self.subscribers if isinstance(s, Move)]

    @property
    def supports(self):
        return [s for s in self.subscribers if isinstance(s, Support)]

    @property
    def convoys(self):
        return [s for s in self.subscribers if isinstance(s, Convoy)]

    def _update_territory_piece(self, observer):
        """
        Update the piece attribute of all territories.
        """
        for t in self.territories:
            if observer.territory == t:
                t.piece = observer

    def _update_neighbours(self, observer):
        """
        Update the neighbours of all territories in the state .
        """
        for t in self.territories:
            if t.id in observer.neighbour_ids:
                observer.neighbours.add(t)
                t.neighbours.add(observer)

    def _update_shared_coasts(self, observer):
        """
        Update the shared coasts of all coastal territories in the state.
        """
        for t in self.territories:
            if t.id in observer.shared_coast_ids:
                observer.shared_coasts.add(t)
                t.shared_coasts.add(observer)

    def _update_piece_order(self, observer):
        """
        Update the `order` attribute of the piece associated with the order.
        """
        for p in self.pieces:
            if p.territory == observer.source:
                observer.piece = p
                p.order = observer

    def _update_territory_named_coasts(self, observer):
        """
        Update the named coasts of all territories.
        """
        for t in self.territories:
            if observer.parent == t:
                t.named_coasts.add(observer)

    def _update_territory_attacking_pieces(self, observer):
        """
        Update the attacking_pieces of the target the move order.
        """
        for t in self.territories:
            if t == observer.target:
                t.attacking_pieces.add(observer.piece)

    def _update_territory_retreating_pieces(self, observer):
        """
        Update the retreating_pieces of the target the retreat order.
        """
        for t in self.territories:
            if t == observer.target:
                t.retreating_pieces.add(observer.piece)

    def _update_order_move_support(self):
        for s in self.supports:
            for m in self.moves:
                if m.target == s.target and m.source == s.aux:
                    m.move_support_orders.add(s)

    def _update_order_hold_support(self):
        for s in self.supports:
            for o in self.orders:
                if o.source == s.target and o.source == s.aux:
                    o.hold_support_orders.add(s)

    def _update_convoy_chains(self):
        for move in [m for m in self.moves if m.via_convoy]:
            source = move.source
            target = move.target
            eligible_convoys = [c for c in self.convoys
                                if c.aux == source and c.target == target]
            move.convoy_chains = get_convoy_chains(source, target, eligible_convoys)


def validate_json(data):
    """
    """
    json_data = json.loads(data)
    try:
        phase = json_data['phase']
        pieces = json_data['pieces']
        territories = json_data['territories']
        orders = json_data['orders']
    except KeyError:
        raise ValueError(
            'Invalid game state - Must include "phase", "pieces", '
            '"territories", and "orders" as keys'
        )

    if phase not in ['order', 'retreat', 'build']:
        raise ValueError(
            'Invalid game state - "phase" must be one of "order", "retreat", or '
            '"build"'
        )
    # TODO dry
    if phase == 'order':
        for order in orders:
            if not order['type'] in ['hold', 'move', 'convoy', 'support']:
                raise ValueError(
                    'Invalid game state - during order phase, each order must be '
                    'one of "hold", "move", "support", or "convoy"'
                )
    if phase == 'retreat':
        for order in orders:
            if not order['type'] in ['retreat', 'disband']:
                raise ValueError(
                    'Invalid game state - during retreat phase, each order must be '
                    'one of "retreat" or "disband"'
                )
    if phase == 'build':
        for order in orders:
            if not order['type'] in ['retreat', 'disband']:
                raise ValueError(
                    'Invalid game state - during build phase, each order must be '
                    'one of "build" or "disband"'
                )



def json_to_state(json):
    pass
