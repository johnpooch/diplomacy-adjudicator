from adjudicator.decisions import Outcomes


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

    while unresolved_moves:
        for move in unresolved_moves:
            move.update_move_decision()

        unresolved_supports = [s for s in supports if s.support_decision == Outcomes.UNRESOLVED]
        for support in unresolved_supports:
            support.update_support_decision()

        unresolved_moves = [m for m in moves if m.move_decision == Outcomes.UNRESOLVED]

    return orders
    #
    # for order in orders:
    #     move_decision(order)


    # # resolve convoy orders first
    # unresolved_fleet_orders = [c for c in all_orders if c.piece.is_fleet]
    # self.__resolve_orders(unresolved_fleet_orders, convoys_only=True)
    #
    # # resolve all other orders
    # unresolved_orders = [c for c in all_orders if c.unresolved]
    # self.__resolve_orders(unresolved_orders)
    #
    # # TODO improve
    # # check all pieces dislodged decision
    # [c.piece.dislodged_decision() for c in all_orders if c.piece.unresolved]
    #
    # [c.save() for c in all_orders]
    # pass