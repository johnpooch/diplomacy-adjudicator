from .base import Decision, Outcomes
from .attack_strength import AttackStrength


class Move(Decision):
    """
    For each piece ordered to move, the decision whether the move is
    successful.
    """
    def _resolve(self):

        piece = self.order.piece
        head_to_head = self.order.is_head_to_head()
        min_attack_strength, max_attack_strength = AttackStrength(self.order)()

        target_min_hold = self.order.target.hold_strength[0]
        target_max_hold = self.order.target.hold_strength[1]

        other_attacking_pieces = self.order.target.other_attacking_pieces(piece)
        other_pieces_max_prevent = max([p.order.prevent_strength_decision()[1] for p in other_attacking_pieces], default=0)
        other_pieces_min_prevent = min([p.order.prevent_strength_decision()[0] for p in other_attacking_pieces], default=0)

        print(self.order.source)
        l = [p.order.prevent_strength_decision()[1] for p in other_attacking_pieces]
        print(other_attacking_pieces)
        print(l)
        # print(other_pieces_max_prevent)
        # print(other_pieces_min_prevent)

        # succeeds if...
        if head_to_head:
            opposing_unit = self.order.target.piece
            opposing_max_defend = opposing_unit.order.max_defend_strength
            if min_attack_strength > opposing_max_defend:
                if other_attacking_pieces:
                    if min_attack_strength > other_pieces_max_prevent:
                        return Outcomes.MOVES
                else:
                    return Outcomes.MOVES

        else:
            if other_attacking_pieces:
                if min_attack_strength > target_max_hold:
                    if min_attack_strength > other_pieces_max_prevent:
                        return Outcomes.MOVES
            else:
                if min_attack_strength > target_min_hold:
                    return Outcomes.MOVES

        # fails if...
        if head_to_head:
            opposing_unit = self.order.target.piece
            opposing_min_defend = opposing_unit.order.min_defend_strength

            if max_attack_strength <= opposing_min_defend:
                return Outcomes.FAILS

        if max_attack_strength <= target_min_hold:
            return Outcomes.FAILS

        if other_attacking_pieces:
            if max_attack_strength <= other_pieces_min_prevent:
                return Outcomes.FAILS

        return Outcomes.UNRESOLVED