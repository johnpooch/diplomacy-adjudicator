from adjudicator.decisions import Outcomes
from adjudicator.paradoxes import find_circular_movements


def process(state):
    """
    Processes all orders in a turn.
    """
    orders = state.orders
    pieces = state.pieces
    for order in orders:
        order.update_legal_decision()

    moves = [o for o in orders if o.is_move]
    supports = [o for o in orders if o.is_support]

    illegal_moves = [m for m in moves if m.legal_decision == Outcomes.ILLEGAL]
    # set illegal moves to fail.
    for m in illegal_moves:
        m.move_decision = Outcomes.FAILS

    unresolved_moves = [m for m in moves if m.move_decision == Outcomes.UNRESOLVED]
    unresolved_pieces = [p for p in pieces if p.dislodged_decision == Outcomes.UNRESOLVED]

    depth = 0
    while unresolved_moves or unresolved_pieces:
        if depth == 5:
            circular_movements = find_circular_movements(moves)
            for l in circular_movements:
                for move in l:
                    move.move_decision = Outcomes.MOVES

        for move in unresolved_moves:
            move.update_move_decision()

        unresolved_supports = [s for s in supports if s.support_decision == Outcomes.UNRESOLVED]
        for support in unresolved_supports:
            support.update_support_decision()

        for piece in unresolved_pieces:
            piece.update_dislodged_decision()

        unresolved_moves = [m for m in moves if m.move_decision == Outcomes.UNRESOLVED]
        unresolved_pieces = [p for p in pieces if p.dislodged_decision == Outcomes.UNRESOLVED]
        depth += 1
    return orders
