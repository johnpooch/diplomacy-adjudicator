from adjudicator import illegal_messages
from .base import Decision, Outcomes
from adjudicator.piece import Army, Fleet
from adjudicator.territory import CoastalTerritory


class BasicLegalDecision(Decision):
    def __init__(self, order):
        super().__init__(order)
        self.illegal_message = None

    def _resolve(self):
        piece = self.order.source.piece
        if piece.nation != self.order.nation:
            self.illegal_message = illegal_messages.B001
            return Outcomes.ILLEGAL


class MoveLegal(BasicLegalDecision):
    """
    For each piece ordered to move, the decision whether the move is legal.
    """
    def _resolve(self):
        if super()._resolve() == Outcomes.ILLEGAL:
            return Outcomes.ILLEGAL
        piece = self.order.source.piece

        if self.order.target == self.order.source:
            self.illegal_message = illegal_messages.M002
            return Outcomes.ILLEGAL

        if not self.order.source.adjacent_to(self.order.target):
            if isinstance(piece, Fleet):
                self.illegal_message = illegal_messages.M004
                return Outcomes.ILLEGAL
            if not self.order.via_convoy:
                self.illegal_message = illegal_messages.M003
                return Outcomes.ILLEGAL

        if not piece.can_reach(self.order.target, self.order.target_coast):
            if isinstance(piece, Army):
                self.illegal_message = illegal_messages.M005
            else:
                if isinstance(self.order.target, CoastalTerritory):
                    self.illegal_message = illegal_messages.M007
                else:
                    self.illegal_message = illegal_messages.M006
            return Outcomes.ILLEGAL

        if isinstance(piece, Fleet):
            if self.order.source.adjacent_to(self.order.target) and self.order.target not in self.order.source.shared_coasts:
                self.illegal_message = illegal_messages.M007
                return Outcomes.ILLEGAL
        return Outcomes.LEGAL


class ConvoyLegal(BasicLegalDecision):
    """
    For each piece ordered to convoy, the decision whether the convoy is legal.
    """
    def _resolve(self):
        super()._resolve()
        if super()._resolve() == Outcomes.ILLEGAL:
            return Outcomes.ILLEGAL
        piece = self.order.source.piece

        if isinstance(self.order.aux.piece, Fleet):
            self.illegal_message = illegal_messages.C001
            return Outcomes.ILLEGAL
        return Outcomes.LEGAL


        # if not self.order.source.adjacent_to(self.order.target):
        #     if isinstance(self.order.source.piece, Fleet):
        #         self.illegal_message = illegal_messages.M004
        #         return ILLEGAL
        #     if not self.order.via_order:
        #         self.illegal_message = illegal_messages.M003
        #         return ILLEGAL
        #
        # if not self.order.source.piece.can_reach(self.order.target):
        #     if isinstance(self.order.source.piece, Army):
        #         self.illegal_message = illegal_messages.M004
        #     else:
        #         self.illegal_message = illegal_messages.M005
        #     return ILLEGAL
        # return LEGAL


class SupportLegal(BasicLegalDecision):
    """
    For each piece ordered to support, the decision whether the support is
    legal.
    """
    def _resolve(self):
        super()._resolve()
        if super()._resolve() == Outcomes.ILLEGAL:
            return Outcomes.ILLEGAL
        piece = self.order.source.piece

        if self.order.target == self.order.source:
            self.illegal_message = illegal_messages.S001
            return Outcomes.ILLEGAL

        if not piece.can_reach_support(self.order.target):
            self.illegal_message = illegal_messages.S002
            return Outcomes.ILLEGAL
        return Outcomes.LEGAL
