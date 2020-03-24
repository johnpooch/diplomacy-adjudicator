from .base import Decision, Outcomes
from .attack_strength import AttackStrength
from adjudicator.order import Convoy, Move


class Support(Decision):
    """
    For each piece ordered to support, the decision whether the support is
    given or cut.
    """
    def _resolve(self):

        piece = self.order.piece

        target_min_hold = self.order.target.hold_strength[0]
        target_max_hold = self.order.target.hold_strength[1]

        other_attacking_pieces = self.order.target.other_attacking_pieces(piece)
        other_pieces_max_prevent = max([p.order.prevent_strength[1] for p in other_attacking_pieces], default=0)
        other_pieces_min_prevent = min([p.order.prevent_strength[0] for p in other_attacking_pieces], default=0)

        # succeeds if...
        if not self.order.source.attacking_pieces:
            return Outcomes.GIVEN

        # TODO clear this up!
        if piece.sustains:
            if self.order.target.piece and self.order.aux.piece:
                if isinstance(self.order.aux.piece.order, Move) and \
                        self.order.aux.piece.order.target == self.order.target:
                    if isinstance(self.order.target.piece.order, Convoy):
                        convoying_order = self.order.target.piece.order
                        if convoying_order.aux.piece:
                            if all([p.order.attack_strength == 0
                                    for p in self.order.source.other_attacking_pieces(convoying_order.aux.piece)]):
                                return Outcomes.GIVEN
                    else:
                        if all([p.order.max_attack_strength == 0
                                for p in self.order.source.other_attacking_pieces
                                    (self.order.target.piece)]):
                            return Outcomes.GIVEN

            if all([p.order.max_attack_strength == 0
                    for p in self.order.source.attacking_pieces]):
                return Outcomes.GIVEN

        # fails if...
        # If aux piece is not going to target of command
        if self.order.aux.piece:
            if isinstance(self.order.aux.piece.command.is_move, Move) \
                    and self.order.aux.piece.command.target != self.order.target \
                    and not self.order.aux.piece.command.illegal:
                return Outcomes.CUT
        # If aux piece holds and support target is not same as aux
        if not self.order.aux.piece.command.is_move and self.order.target != self.order.aux:
            return Outcomes.CUT

        if self.order.source.piece.dislodged:
            return Outcomes.CUT
        if self.order.target.occupied() and self.order.aux.occupied():
            if self.order.aux.piece.command.is_move and \
                    self.order.aux.piece.command.target == self.order.target:
                if self.order.target.piece.command.is_convoy:
                    convoying_command = self.order.target.piece.command
                    if convoying_command.aux.occupied():
                        if any([p.command.min_attack_strength >= 1
                                for p in self.order.source.other_attacking_pieces(convoying_command.aux.piece)]):
                            return Outcomes.CUT
                else:
                    if any([p.command.min_attack_strength >= 1
                            for p in self.order.source.other_attacking_pieces(self.order.target.piece)]):
                        return Outcomes.CUT
        if self.order.source.attacking_pieces and \
                any([p.command.min_attack_strength >= 1
                     for p in self.order.source.attacking_pieces
                     if p.territory != self.order.aux.piece.command.target]):
            return Outcomes.CUT

