import unittest
from adjudicator.state import state
from adjudicator.order import Hold
from adjudicator.piece import Army
from adjudicator.territory import CoastalTerritory


class OrderTestCase(unittest.TestCase):
    def setUp(self):
        state.__init__()


class TestPiece(OrderTestCase):

    def test_piece(self):
        london = CoastalTerritory(1, "London", "England", [], [])
        wales = CoastalTerritory(2, "Wales", "England", [], [])

        army = Army("England", london)
        london_hold = Hold("England", london)
        wales_hold = Hold("England", wales)

        self.assertEqual(london_hold.piece, army)
        self.assertIsNone(wales_hold.piece)


class TestIsOrder(OrderTestCase):

    def test_hold(self):
        london = CoastalTerritory(1, "London", "England", [], [])
        Army("England", london)
        london_hold = Hold("England", london)

        self.assertTrue(london_hold.is_hold)
        self.assertFalse(london_hold.is_move)
        with self.assertRaises(AttributeError):
            london_hold.is_fake_class_name
