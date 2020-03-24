def process_orders(orders):
    """
    Processes all orders in a turn.
    """
    for order in orders:
        order.legal_decision()

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