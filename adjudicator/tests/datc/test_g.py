import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestConvoyingToAdjacentPlaces(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_two_units_can_swap_places_by_convoy(self):
        """
        The only way to swap two units, is by convoy.

        England:
        A Norway - Sweden
        F Skagerrak Convoys A Norway - Sweden

        Russia:
        A Sweden - Norway

        In most interpretation of the rules, the units in Norway and Sweden
        will be swapped. However, if explicit adjacent convoying is used (see
        issue 4.A.3), then it is just a head to head battle.

        I prefer the 2000 rules, so the units are swapped.
        """
        pieces = [
            Army(Nations.ENGLAND, self.territories.NORWAY),
            Fleet(Nations.ENGLAND, self.territories.SKAGERRAK),
            Army(Nations.RUSSIA, self.territories.SWEDEN),
        ]
        orders = [
            Move(Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN, via_convoy=True),
            Convoy(Nations.ENGLAND, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.SWEDEN),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
