from .base import Decision, Outcomes
from .attack_strength import AttackStrength


class Support(Decision):
    """
    For each piece ordered to support, the decision whether the support is
    given or cut.
    """
    def _resolve(self):

        piece = self.order.piece


        target_piece = self.order.target.piece
        aux_piece = self.order.aux.piece
        aux_target = self.order.aux.piece.order.target

        source_attacking_pieces = self.order.source.other_attacking_pieces(target_piece)

        # succeeds if...
        if not self.order.source.attacking_pieces:
            return Outcomes.GIVEN

        # TODO clear this up!
        # if piece.sustains:
        if target_piece and aux_piece:
            # If the aux piece is moving to the right target.
            if aux_piece.order.is_move() and aux_target == self.order.target:
                # If no pieces (other than the target piece) have strength
                if all([p.order.attack_strength_decision.max_strength == 0 for p in source_attacking_pieces]):
                    return Outcomes.GIVEN

                # # NOTE not sure what this block is for.
                # if isinstance(target_piece.order, Convoy):
                #     convoying_order = target_piece.order
                #     if convoying_order.aux.piece:
                #         if all([p.order.attack_strength == 0
                #                 for p in self.order.source.other_attacking_pieces(convoying_order.aux.piece)]):
                #             return Outcomes.GIVEN


        if all([p.order.attack_strength_decision.max_strength == 0 for p in self.order.source.attacking_pieces]):
            return Outcomes.GIVEN

        # fails if...
        # If aux piece is not going to target of order
        if aux_piece:
            if aux_piece.order.is_move() \
                    and aux_piece.order.target != self.order.target \
                    and aux_piece.order.legal_decision == Outcomes.LEGAL:
                return Outcomes.CUT
            # If aux piece holds and support target is not same as aux
            else:
                 if self.order.target != self.order.aux:
                    return Outcomes.CUT

        if self.order.source.piece.dislodged:
            return Outcomes.CUT

        if target_piece and aux_piece:
            if aux_piece.order.is_move() and aux_piece == self.order.target:
                if target_piece.order.is_convoy:
                    convoying_order = target_piece.order
                    if convoying_order.aux.piece:
                        if any([p.order.min_attack_strength >= 1
                                for p in self.order.source.other_attacking_pieces(convoying_order.aux.piece)]):
                            return Outcomes.CUT
                else:
                    if any([p.order.attack_strength_decision.min_strength >= 1
                            for p in self.order.source.other_attacking_pieces(self.order.target.piece)]):
                        return Outcomes.CUT
        if self.order.source.attacking_pieces and \
                any([p.order.min_attack_strength >= 1
                     for p in self.order.source.attacking_pieces
                     if p.territory != self.order.aux.piece.order.target]):
            return Outcomes.CUT

