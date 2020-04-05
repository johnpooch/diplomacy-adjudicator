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

    def test_kidnapping_an_army(self):
        """
        Germany promised England to support to dislodge the Russian fleet in
        Sweden and it promised Russia to support to dislodge the English army
        in Norway. Instead, the joking German orders a convoy.

        England:
        A Norway - Sweden

        Russia:
        F Sweden - Norway

        Germany:
        F Skagerrak Convoys A Norway - Sweden
        See issue 4.A.3.

        When the 1982/2000 rulebook is used (which I prefer), England has no
        intent to swap and it is just a head to head battle were both units
        will fail to move. When explicit adjacent convoying is used (DPTG), the
        English move is not a convoy and again it just a head to head battle
        were both units will fail to move. In all other interpretations, the
        army in Norway will be convoyed and swap its place with the fleet in
        Sweden.
        """
        pieces = [
            Army(Nations.ENGLAND, self.territories.NORWAY),
            Fleet(Nations.RUSSIA, self.territories.SKAGERRAK),
            Army(Nations.RUSSIA, self.territories.SWEDEN),
        ]
        orders = [
            Move(Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Convoy(Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.SWEDEN),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)

    def test_kidnapping_with_a_disrupted_convoy(self):
        """
        When kidnapping of armies is allowed, a move can be sabotaged by a
        fleet that is almost certainly dislodged.

        France:
        F Brest - English Channel
        A Picardy - Belgium
        A Burgundy Supports A Picardy - Belgium
        F Mid-Atlantic Ocean Supports F Brest - English Channel

        England:
        F English Channel Convoys A Picardy - Belgium

        See issue 4.A.3. If a convoy always takes precedence over a land route
        (choice a), the move from Picardy to Belgium fails. It tries to convoy
        and the convoy is disrupted.

        For choice b and c, there is no unit moving in opposite direction for
        the move of the army in Picardy. For this reason, the move for the army
        in Picardy is not by convoy and succeeds over land.

        When the 1982 or 2000 rules are used (choice d), then it is not the
        "intent" of the French army in Picardy to convoy. The move from Picardy
        to Belgium is just a successful move over land.

        When explicit adjacent convoying is used (DPTG, choice e), the order of
        the French army in Picardy is not a convoy order. So, it just ordered
        over land, and that move succeeds.

        This is an excellent example why the convoy route should not
        automatically have priority over the land route. It would just be
        annoying for the attacker and this situation is without fun. I prefer
        the 1982 rule with the 2000 clarification. According to these rules the
        move from Picardy succeeds.
        """
        pieces = [
            Fleet(Nations.FRANCE, self.territories.BREST),
            Army(Nations.FRANCE, self.territories.PICARDY),
            Army(Nations.FRANCE, self.territories.BURGUNDY),
            Fleet(Nations.FRANCE, self.territories.MID_ATLANTIC),
            Fleet(Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
        ]
        orders = [
            Move(Nations.FRANCE, self.territories.BREST, self.territories.ENGLISH_CHANNEL),
            Move(Nations.FRANCE, self.territories.PICARDY, self.territories.BELGIUM),
            Support(Nations.FRANCE, self.territories.BURGUNDY, self.territories.PICARDY, self.territories.BELGIUM),
            Support(Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.BREST, self.territories.ENGLISH_CHANNEL),
            Convoy(Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.PICARDY, self.territories.BELGIUM),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)

    def test_kidnapping_with_a_disrupted_convoy_and_opposite_move(self):
        """
        In the situation of the previous test case it was rather clear that the
        army didn't want to take the convoy. But what if there is an army
        moving in opposite direction?

        France:
        F Brest - English Channel
        A Picardy - Belgium
        A Burgundy Supports A Picardy - Belgium
        F Mid-Atlantic Ocean Supports F Brest - English Channel

        England:
        F English Channel Convoys A Picardy - Belgium
        A Belgium - Picardy

        See issue 4.A.3. If a convoy always takes precedence over a land route
        (choice a), the move from Picardy to Belgium fails. It tries to convoy
        and the convoy is disrupted.

        For choice b the convoy is also taken, because there is a unit in
        Belgium moving in opposite direction. This means that the convoy is
        disrupted and the move from Picardy to Belgium fails.

        For choice c the convoy is not taken. Although, the unit in Belgium is
        moving in opposite direction, the army will not take a disrupted
        convoy. So, the move from Picardy to Belgium succeeds.

        When the 1982 or 2000 rules are used (choice d), then it is not the
        "intent" of the French army in Picardy to convoy. The move from Picardy
        to Belgium is just a successful move over land.

        When explicit adjacent convoying is used (DPTG, choice e), the order of
        the French army in Picardy is not a convoy order. So, it just ordered
        over land, and that move succeeds.

        Again an excellent example why the convoy route should not
        automatically have priority over the land route. It would just be
        annoying for the attacker and this situation is without fun. I prefer
        the 1982 rule with the 2000 clarification. According to these rules the
        move from Picardy succeeds.
        """
        pieces = [
            Fleet(Nations.FRANCE, self.territories.BREST),
            Army(Nations.FRANCE, self.territories.PICARDY),
            Army(Nations.FRANCE, self.territories.BURGUNDY),
            Fleet(Nations.FRANCE, self.territories.MID_ATLANTIC),
            Fleet(Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
            Army(Nations.ENGLAND, self.territories.BELGIUM),
        ]
        orders = [
            Move(Nations.FRANCE, self.territories.BREST, self.territories.ENGLISH_CHANNEL),
            Move(Nations.FRANCE, self.territories.PICARDY, self.territories.BELGIUM),
            Support(Nations.FRANCE, self.territories.BURGUNDY, self.territories.PICARDY, self.territories.BELGIUM),
            Support(Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.BREST, self.territories.ENGLISH_CHANNEL),
            Convoy(Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.PICARDY, self.territories.BELGIUM),
            Move(Nations.ENGLAND, self.territories.BELGIUM, self.territories.PICARDY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[5].dislodged_decision, Outcomes.DISLODGED)

    def test_swapping_with_unintended_intent(self):
        """
        The intent is questionable.


        England:
        A Liverpool - Edinburgh
        F English Channel Convoys A Liverpool - Edinburgh

        Germany:
        A Edinburgh - Liverpool

        France:
        F Irish Sea Hold
        F North Sea Hold

        Russia:
        F Norwegian Sea Convoys A Liverpool - Edinburgh
        F North Atlantic Ocean Convoys A Liverpool - Edinburgh
        See issue 4.A.3.

        For choice a, b and c the English army in Liverpool will move by convoy
        and consequentially the two armies are swapped.

        For choice d, the 1982/2000 rulebook (which I prefer), the convoy
        depends on the "intent". England intended to convoy via the French
        fleets in the Irish Sea and the North Sea. However, the French did not
        order the convoy. The alternative route with the Russian fleets was
        unintended. The English fleet in the English Channel (with the convoy
        order) is not part of this alternative route with the Russian fleets.
        Since England still "intent" to convoy, the move from Liverpool to
        Edinburgh should be via convoy and the two armies are swapped.
        Although, you could argue that this is not really according to the
        clarification of the 2000 rulebook.

        When explicit adjacent convoying is used (DPTG, choice e), then the
        English army did not receive an order to move by convoy. So, it is just
        a head to head battle and both the army in Edinburgh and Liverpool will
        not move.
        """
        pieces = [
            Army(Nations.ENGLAND, self.territories.LIVERPOOL),
            Fleet(Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
            Army(Nations.GERMANY, self.territories.EDINBURGH),
            Fleet(Nations.FRANCE, self.territories.IRISH_SEA),
            Fleet(Nations.FRANCE, self.territories.NORTH_SEA),
            Fleet(Nations.RUSSIA, self.territories.NORWEGIAN_SEA),
            Fleet(Nations.RUSSIA, self.territories.NORTH_ATLANTIC),
        ]
        orders = [
            Move(Nations.ENGLAND, self.territories.LIVERPOOL, self.territories.EDINBURGH),
            Convoy(Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.LIVERPOOL, self.territories.EDINBURGH),
            Move(Nations.GERMANY, self.territories.EDINBURGH, self.territories.LIVERPOOL),
            Hold(Nations.FRANCE, self.territories.IRISH_SEA),
            Hold(Nations.FRANCE, self.territories.NORTH_SEA),
            Convoy(Nations.RUSSIA, self.territories.NORWEGIAN_SEA, self.territories.LIVERPOOL, self.territories.EDINBURGH),
            Convoy(Nations.RUSSIA, self.territories.NORTH_ATLANTIC, self.territories.LIVERPOOL, self.territories.EDINBURGH),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)

    def test_swapping_with_illegal_intent(self):
        """
        Can the intent made clear with an impossible order?

        England:
        F Skagerrak Convoys A Sweden - Norway
        F Norway - Sweden

        Russia:
        A Sweden - Norway
        F Gulf of Bothnia Convoys A Sweden - Norway
        See issue 4.A.3 and 4.E.1.

        If for issue 4.A.3 choice a, b or c has been taken, then the army in
        weden moves by convoy and swaps places with the fleet in Norway.

        However, if for issue 4.A.3 the 1982/2000 has been chosen (choice d),
        then the "intent" is important. The question is whether the fleet in
        the Gulf of Bothnia can express the intent. If the order for this fleet
        is considered illegal (see issue 4.E.1), then this order must be
        ignored and there is no intent to swap. In that case none of the units
        move.

        If explicit convoying is used (DPTG, choice e of issue 4.A.3) then the
        army in Sweden will take the land route and none of the units move.

        I prefer the 1982/2000 rule and that any orders that can't be valid are
        illegal. So, the order of the fleet in the Gulf of Bothnia is ignored
        and can not show the intent. There is no convoy, so no unit will move.
        """
        pieces = [
            Fleet(Nations.ENGLAND, self.territories.SKAGERRAK),
            Fleet(Nations.ENGLAND, self.territories.NORWAY),
            Army(Nations.RUSSIA, self.territories.SWEDEN),
            Fleet(Nations.RUSSIA, self.territories.GULF_OF_BOTHNIA),
        ]
        orders = [
            Convoy(Nations.ENGLAND, self.territories.SKAGERRAK, self.territories.SWEDEN, self.territories.NORWAY),
            Move(Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
            Convoy(Nations.RUSSIA, self.territories.GULF_OF_BOTHNIA, self.territories.SWEDEN, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)

    def test_explicit_convoy_that_isnt_there(self):
        """
        What to do when a unit is explicitly ordered to move via convoy and the
        convoy is not there?

        France:
        A Belgium - Holland via Convoy

        England:
        F North Sea - Helgoland Bight
        A Holland - Kiel

        The French army in Belgium intended to move convoyed with the English
        fleet in the North Sea. But the English changed their plans.

        See issue 4.A.3.

        If choice a, b or c has been taken, then the 'via Convoy' directive has
        no meaning and the army in Belgium will move to Holland.

        If the 1982/2000 rulebook is used (choice d, which I prefer), the "via
        Convoy" has meaning, but only when there is both a land route and a
        convoy route. Since there is no convoy the "via Convoy" directive
        should be ignored. And the move from Belgium to Holland succeeds.

        If explicit adjacent convoying is used (DPTG, choice e), then the unit
        can only go by convoy. Since there is no convoy, the move from Belgium
        to Holland fails.
        """
        pieces = [
            Army(Nations.FRANCE, self.territories.BELGIUM),
            Fleet(Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(Nations.ENGLAND, self.territories.HOLLAND),
        ]
        orders = [
            Move(Nations.FRANCE, self.territories.BELGIUM, self.territories.HOLLAND, via_convoy=True),
            Move(Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.HELGOLAND_BIGHT),
            Move(Nations.ENGLAND, self.territories.HOLLAND, self.territories.KIEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].path_decision(), Outcomes.NO_PATH)
        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)

    def test_swapped_or_dislodged(self):
        """
        The 1982 rulebook says that whether the move is over land or via convoy
        depends on the "intent" as shown by the totality of the orders written
        by the player governing the army (see issue 4.A.3). In this test case
        the English army in Norway will end in all cases in Sweden. But whether
        it is convoyed or not has effect on the Russian army. In case of convoy
        the Russian army ends in Norway and in case of a land route the Russian
        army is dislodged.

        England:
        A Norway - Sweden
        F Skagerrak Convoys A Norway - Sweden
        F Finland Supports A Norway - Sweden

        Russia:
        A Sweden - Norway
        See issue 4.A.3.

        For choice a, b and c the move of the army in Norway is by convoy and
        the armies in Norway and Sweden are swapped.

        If the 1982 rulebook is used with the clarification of the 2000
        rulebook (choice d, which I prefer), the intent of the English player
        is to convoy, since it ordered the fleet in Skagerrak to convoy.
        Therefore, the armies in Norway and Sweden are swapped.

        When explicit adjacent convoying is used (DTPG, choice e), then the
        unit in Norway did not receive an order to move by convoy and the land
        route should be considered. The Russian army in Sweden is dislodged.
        """
        pieces = [
            Army(Nations.ENGLAND, self.territories.NORWAY),
            Fleet(Nations.ENGLAND, self.territories.SKAGERRAK),
            Fleet(Nations.ENGLAND, self.territories.FINLAND),
            Army(Nations.RUSSIA, self.territories.SWEDEN),
        ]
        orders = [
            Move(Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Convoy(Nations.ENGLAND, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.SWEDEN),
            Support(Nations.ENGLAND, self.territories.FINLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)

    def test_swapped_or_head_to_head(self):
        """
        Can a dislodged unit have effect on the attackers area, when the
        attacker moved by convoy?

        England:
        A Norway - Sweden via Convoy
        F Denmark Supports A Norway - Sweden
        F Finland Supports A Norway - Sweden

        Germany:
        F Skagerrak Convoys A Norway - Sweden

        Russia:
        A Sweden - Norway
        F Barents Sea Supports A Sweden - Norway

        France:
        F Norwegian Sea - Norway
        F North Sea Supports F Norwegian Sea - Norway

        Since England ordered the army in Norway to move explicitly via convoy
        and the army in Sweden is moving in opposite direction, only the
        convoyed route should be considered regardless of the rulebook used.
        It is clear that the army in Norway will dislodge the Russian army in
        Sweden. Since the strength of three is in all cases the strongest
        force.

        The army in Sweden will not advance to Norway, because it can not beat
        the force in the Norwegian Sea. It will be dislodged by the army from
        Norway.

        The more interesting question is whether French fleet in the Norwegian
        Sea is bounced by the Russian army from Sweden. This depends on the
        interpretation of issue 4.A.7. If the rulebook is taken literally
        (choice a), then a dislodged unit can not bounce a unit in the area
        where the attacker came from. This would mean that the move of the
        fleet in the Norwegian Sea succeeds However, if choice b is taken
        (which I prefer), then a bounce is still possible, when there is no
        head to head battle. So, the fleet in the Norwegian Sea will fail to
        move.
        """
        pieces = [
            Army(Nations.ENGLAND, self.territories.NORWAY),
            Fleet(Nations.ENGLAND, self.territories.DENMARK),
            Fleet(Nations.ENGLAND, self.territories.FINLAND),
            Fleet(Nations.GERMANY, self.territories.SKAGERRAK),
            Army(Nations.RUSSIA, self.territories.SWEDEN),
            Fleet(Nations.RUSSIA, self.territories.BARRENTS_SEA),
            Fleet(Nations.FRANCE, self.territories.NORWEGIAN_SEA),
            Fleet(Nations.FRANCE, self.territories.NORTH_SEA),
        ]
        orders = [
            Move(Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN, via_convoy=True),
            Support(Nations.ENGLAND, self.territories.DENMARK, self.territories.NORWAY, self.territories.SWEDEN),
            Support(Nations.ENGLAND, self.territories.FINLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Convoy(Nations.GERMANY, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.SWEDEN),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
            Support(Nations.RUSSIA, self.territories.BARRENTS_SEA, self.territories.SWEDEN, self.territories.NORWAY),
            Move(Nations.FRANCE, self.territories.NORWEGIAN_SEA, self.territories.NORWAY),
            Support(Nations.FRANCE, self.territories.NORTH_SEA, self.territories.NORWEGIAN_SEA, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[4].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[5].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[6].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[7].support_decision, Outcomes.GIVEN)

    @unittest.skip('test_convoy_to_an_adjacent_place_with_paradox - convoy paradox')
    def test_convoy_to_an_adjacent_place_with_paradox(self):
        """
        In this case the convoy route is available when the land route is
        chosen and the convoy route is not available when the convoy route is
        chosen.

        England:
        F Norway Supports F North Sea - Skagerrak
        F North Sea - Skagerrak

        Russia:
        A Sweden - Norway
        F Skagerrak Convoys A Sweden - Norway
        F Barents Sea Supports A Sweden - Norway
        See issue 4.A.2 and 4.A.3.

        If for issue 4.A.3, choice b, c or e has been taken, then the move from
        Sweden to Norway is not a convoy and the English fleet in Norway is
        dislodged and the fleet in Skagerrak will not be dislodged.

        If choice a or d (1982/2000 rule) has been taken for issue 4.A.3, then
        the move from Sweden to Norway must be treated as a convoy. At that
        moment the situation becomes paradoxical. When the 'All Hold' rule is
        used, both the army in Sweden as the fleet in the North Sea will not
        advance. In all other paradox rules the English fleet in the North Sea
        will dislodge the Russian fleet in Skagerrak and the army in Sweden
        will not advance.

        I prefer the 1982 rule with the 2000 rulebook clarification concerning
        the convoy to adjacent places and I prefer the Szykman rule for paradox
        resolving. That means that according to these preferences the fleet in
        the North Sea will dislodge the Russian fleet in Skagerrak and the army
        in Sweden will not advance.
        """
        pieces = [
            Fleet(Nations.ENGLAND, self.territories.NORWAY),
            Fleet(Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(Nations.RUSSIA, self.territories.SWEDEN),
            Fleet(Nations.RUSSIA, self.territories.SKAGERRAK),
            Fleet(Nations.RUSSIA, self.territories.BARRENTS_SEA),
        ]
        orders = [
            Support(Nations.ENGLAND, self.territories.NORWAY, self.territories.NORTH_SEA, self.territories.SKAGERRAK),
            Move(Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.SKAGERRAK),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
            Convoy(Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.SWEDEN, self.territories.NORWAY),
            Support(Nations.RUSSIA,self.territories.BARRENTS_SEA, self.territories.SWEDEN, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)

    def test_swapping_two_units_with_two_convoys(self):
        """
        Of course, two armies can also swap by when they are both convoyed.

        England:
        A Liverpool - Edinburgh via Convoy
        F North Atlantic Ocean Convoys A Liverpool - Edinburgh
        F Norwegian Sea Convoys A Liverpool - Edinburgh

        Germany:
        A Edinburgh - Liverpool via Convoy
        F North Sea Convoys A Edinburgh - Liverpool
        F English Channel Convoys A Edinburgh - Liverpool
        F Irish Sea Convoys A Edinburgh - Liverpool

        The armies in Liverpool and Edinburgh are swapped.
        """
        pieces = [
            Army(Nations.ENGLAND, self.territories.LIVERPOOL),
            Fleet(Nations.ENGLAND, self.territories.NORTH_ATLANTIC),
            Fleet(Nations.ENGLAND, self.territories.NORWEGIAN_SEA),
        ]
        orders = [
            Support(Nations.ENGLAND, self.territories.NORWAY, self.territories.NORTH_SEA, self.territories.SKAGERRAK),
            Move(Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.SKAGERRAK),
            Move(Nations.RUSSIA, self.territories.SWEDEN, self.territories.NORWAY),
            Convoy(Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.SWEDEN, self.territories.NORWAY),
            Support(Nations.RUSSIA,self.territories.BARRENTS_SEA, self.territories.SWEDEN, self.territories.NORWAY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
