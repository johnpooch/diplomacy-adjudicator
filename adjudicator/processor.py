from adjudicator.decisions import Outcomes
from adjudicator.paradoxes import find_circular_movements


def process_orders(orders):
    """
    Processes all orders in a turn.
    """
    for order in orders:
        order.update_legal_decision()

    moves = [o for o in orders if o.is_move]
    supports = [o for o in orders if o.is_support]

    illegal_moves = [m for m in moves if m.legal_decision == Outcomes.ILLEGAL]
    # set illegal moves to fail.
    for m in illegal_moves:
        m.move_decision = Outcomes.FAILS

    unresolved_moves = [m for m in moves if m.move_decision == Outcomes.UNRESOLVED]

    depth = 0
    while unresolved_moves:
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

        unresolved_moves = [m for m in moves if m.move_decision == Outcomes.UNRESOLVED]
        depth += 1
    return orders
