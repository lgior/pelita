# -*- coding: utf-8 -*-

import unittest
from pelita.datamodel import north, south, east, west, stop,\
        Wall, Free, Food,\
        TeamWins, BotMoves, create_CTFUniverse
from pelita.game_master import GameMaster, UniverseNoiser
from pelita.player import AbstractPlayer, SimpleTeam, TestPlayer
from pelita.viewer import AbstractViewer, DevNullViewer


class TestGameMaster(unittest.TestCase):

    def test_basics(self):
        test_layout = (
        """ ##################
            #0#.  .  # .     #
            #2#####    #####1#
            #     . #  .  .#3#
            ################## """)

        game_master = GameMaster(test_layout, 4, 200)

        class BrokenViewer(AbstractViewer):
            pass

        class BrokenPlayer(AbstractPlayer):
            pass

        self.assertRaises(TypeError, game_master.register_viewer, BrokenViewer())
#        self.assertRaises(TypeError, game_master.register_player, BrokenPlayer())
        self.assertRaises(IndexError, game_master.play)

    def test_team_names(self):
        test_layout = (
        """ ##################
            #0#.  .  # .     #
            #2#####    #####1#
            #     . #  .  .#3#
            ################## """)

        game_master = GameMaster(test_layout, 4, 200)

        team_1 = SimpleTeam(TestPlayer([]), TestPlayer([]))
        team_2 = SimpleTeam(TestPlayer([]), TestPlayer([]))

        game_master.register_team(team_1, team_name="team1")
        game_master.register_team(team_2, team_name="team2")

        game_master.set_initial()
        self.assertEqual(game_master.universe.teams[0].name, "team1")
        self.assertEqual(game_master.universe.teams[1].name, "team2")

        # check that all players know it, before the game started
        self.assertEqual(team_1._players[0].current_uni.teams[0].name, "team1")
        self.assertEqual(team_1._players[0].current_uni.teams[1].name, "team2")
        self.assertEqual(team_1._players[1].current_uni.teams[0].name, "team1")
        self.assertEqual(team_1._players[1].current_uni.teams[1].name, "team2")

        self.assertEqual(team_2._players[0].current_uni.teams[0].name, "team1")
        self.assertEqual(team_2._players[0].current_uni.teams[1].name, "team2")
        self.assertEqual(team_2._players[1].current_uni.teams[0].name, "team1")
        self.assertEqual(team_2._players[1].current_uni.teams[1].name, "team2")


class TestUniverseNoiser(unittest.TestCase):

    def test_a_star(self):
        test_layout = (
        """ ##################
            #0#.  .  # .     #
            #2#####    #####1#
            #     . #  .  .#3#
            ################## """)
        universe = create_CTFUniverse(test_layout, 4)
        noiser = UniverseNoiser(universe.copy())
        # just a simple smoke test
        self.assertEqual(14, len(noiser.a_star((1, 1), (3, 1))))

    def test_pos_within(self):
        test_layout = (
        """ ##################
            #0#.  .  # .     #
            #2#####    #####1#
            #     . #  .  .#3#
            ################## """)
        universe = create_CTFUniverse(test_layout, 4)
        noiser = UniverseNoiser(universe.copy())
        free = set(universe.maze.pos_of(Free))


        self.assertRaises(TypeError, noiser.pos_within, (0, 0))
        self.assertRaises(TypeError, noiser.pos_within, (6, 2))

        target = set([(1, 1), (1, 2), (1,3), (2, 3), (3, 3), (3, 3)])
        self.assertEqual(target, noiser.pos_within((1, 1)))
        # assuming a_star is working properly
        for pos in target:
            self.assertTrue(len(noiser.a_star((1, 1), pos)) < 5)
        for pos in free.difference(target):
            self.assertTrue(len(noiser.a_star((1, 1), pos)) >= 5)

    def test_uniform_noise(self):
        test_layout = (
        """ ##################
            # #.  .  # .     #
            # #####    ##### #
            #  0  . #  .  .#1#
            ################## """)
        universe = create_CTFUniverse(test_layout, 2)
        noiser = UniverseNoiser(universe.copy())

        position_bucket = dict(((i, 0)
            for i in [(1, 2), (7, 3), (1, 3), (3, 3), (6, 3),
                (2, 3), (4, 3), (1, 1), (5, 3)]))
        for i in range(100):
            new = noiser.uniform_noise(universe.copy(), 1)
            self.assertTrue(new.bots[0].noisy)
            position_bucket[new.bots[0].current_pos] += 1
        self.assertEqual(100, sum(position_bucket.itervalues()))
        # Since this is a randomized algorithm we need to be a bit lenient with
        # our tests. We check that each position was selected at least once and
        # check that it was selected a minimum of five times.
        for v in position_bucket.itervalues():
            self.assertTrue(v != 0)
            self.assertTrue(v >= 5, 'Testing randomized function, may fail sometimes.')

    def test_uniform_noise_4_bots(self):
        test_layout = (
        """ ##################
            # #. 2.  # .     #
            # #####    #####3#
            #  0  . #  .  .#1#
            ################## """)
        universe = create_CTFUniverse(test_layout, 4)
        noiser = UniverseNoiser(universe.copy())

        position_bucket_0 = dict(((i, 0)
            for i in [(1, 2), (7, 3), (1, 3), (3, 3), (6, 3),
                (2, 3), (4, 3), (1, 1), (5, 3)]))

        position_bucket_2 = dict(((i, 0)
            for i in [(7, 3), (8, 2), (7, 1), (8, 1), (6, 1), (3, 1), (5, 1),
                (4, 1), (7, 2)]))

        for i in range(100):
            new = noiser.uniform_noise(universe.copy(), 1)
            self.assertTrue(new.bots[0].noisy)
            self.assertTrue(new.bots[2].noisy)
            position_bucket_0[new.bots[0].current_pos] += 1
            position_bucket_2[new.bots[2].current_pos] += 1
        self.assertEqual(100, sum(position_bucket_0.itervalues()))
        self.assertEqual(100, sum(position_bucket_2.itervalues()))
        # Since this is a randomized algorithm we need to be a bit lenient with
        # our tests. We check that each position was selected at least once and
        # check that it was selected a minimum of five times.
        for v in position_bucket_0.itervalues():
            self.assertTrue(v != 0)
            self.assertTrue(v >= 5, 'Testing randomized function, may fail sometimes.')

        for v in position_bucket_2.itervalues():
            self.assertTrue(v != 0)
            self.assertTrue(v >= 5, 'Testing randomized function, may fail sometimes.')

    def test_uniform_noise_4_bots_no_noise(self):
        test_layout = (
        """ ##################
            # #.  .  # . 2   #
            # #####    #####3#
            #  0  . #  .  .#1#
            ################## """)
        universe = create_CTFUniverse(test_layout, 4)
        noiser = UniverseNoiser(universe.copy())

        position_bucket_0 = dict(((i, 0)
            for i in [(1, 2), (7, 3), (1, 3), (3, 3), (6, 3),
                (2, 3), (4, 3), (1, 1), (5, 3)]))

        bot_2_pos = (13, 1)
        position_bucket_2 = {bot_2_pos : 0}

        for i in range(100):
            new = noiser.uniform_noise(universe.copy(), 1)
            self.assertTrue(new.bots[0].noisy)
            self.assertFalse(new.bots[2].noisy)
            position_bucket_0[new.bots[0].current_pos] += 1
            position_bucket_2[new.bots[2].current_pos] += 1
        self.assertEqual(100, sum(position_bucket_0.itervalues()))
        self.assertEqual(100, sum(position_bucket_2.itervalues()))
        # Since this is a randomized algorithm we need to be a bit lenient with
        # our tests. We check that each position was selected at least once and
        # check that it was selected a minimum of five times.
        for v in position_bucket_0.itervalues():
            self.assertTrue(v != 0)
            self.assertTrue(v >= 5, 'Testing randomized function, may fail sometimes.')

        # bots should never have been noised
        self.assertEqual(100, position_bucket_2[bot_2_pos])

class TestAbstracts(unittest.TestCase):

    def test_AbstractViewer(self):
        av = AbstractViewer()
        self.assertRaises(NotImplementedError, av.observe, None, None, None, None)

    def test_AbstractPlayer(self):
        ap = AbstractPlayer()
        self.assertRaises(NotImplementedError, ap.get_move)

class TestGame(unittest.TestCase):

    def test_game(self):

        test_start = (
            """ ######
                #0 . #
                #.. 1#
                ###### """)

        number_bots = 2

        # The problem here is that the layout does not allow us to specify a
        # different inital position and current position. When testing universe
        # equality by comparing its string representation, this does not matter.
        # But if we want to compare using the __eq__ method, but specify the
        # target as ascii encoded maze/layout we need to convert the layout to a
        # CTFUniverse and then modify the initial positions. For this we define
        # a closure here to quickly generate a target universe to compare to.
        # Also we adapt the score, in case food has been eaten

        def create_TestUniverse(layout):
            initial_pos = [(1, 1), (4, 2)]
            universe = create_CTFUniverse(layout, number_bots)
            for i, pos in enumerate(initial_pos):
                universe.bots[i].initial_pos = pos
            if not universe.maze.has_at(Food, (1, 2)):
                universe.teams[1]._score_point()
            if not universe.maze.has_at(Food, (2, 2)):
                universe.teams[1]._score_point()
            if not universe.maze.has_at(Food, (3, 1)):
                universe.teams[0]._score_point()
            return universe


        gm = GameMaster(test_start, number_bots, 200)
        gm.register_team(SimpleTeam(TestPlayer([east, east, east, south, stop, east])))
        gm.register_team(SimpleTeam(TestPlayer([west, west, west, stop, west, west])))

        gm.register_viewer(DevNullViewer())

        gm.set_initial()
        gm.play_round(0)
        test_first_round = (
            """ ######
                # 0. #
                #..1 #
                ###### """)
        self.assertEqual(create_TestUniverse(test_first_round), gm.universe)

        gm.play_round(1)
        test_second_round = (
            """ ######
                # 0. #
                #.1  #
                ###### """)
        self.assertEqual(create_TestUniverse(test_second_round), gm.universe)

        gm.play_round(2)
        test_third_round = (
            """ ######
                #  . #
                #.0 1#
                ###### """)
        self.assertEqual(create_TestUniverse(test_third_round), gm.universe)

        gm.play_round(3)
        test_fourth_round = (
            """ ######
                #0 . #
                #. 1 #
                ###### """)
        self.assertEqual(create_TestUniverse(test_fourth_round), gm.universe)

        gm.play_round(4)
        test_fifth_round = (
            """ ######
                # 0. #
                #.1  #
                ###### """)
        self.assertEqual(create_TestUniverse(test_fifth_round), gm.universe)

        gm.play_round(5)
        test_sixth_round = (
            """ ######
                #  0 #
                #.1  #
                ###### """)
        self.assertEqual(create_TestUniverse(test_sixth_round), gm.universe)


        # now play the full game
        gm = GameMaster(test_start, number_bots, 200)
        gm.register_team(SimpleTeam(TestPlayer([east, east, east, south, stop, east])))
        gm.register_team(SimpleTeam(TestPlayer([west, west, west, stop, west, west])))
        gm.play()
        test_sixth_round = (
            """ ######
                #  0 #
                #.1  #
                ###### """)
        self.assertEqual(create_TestUniverse(test_sixth_round), gm.universe)

    def test_malicous_player(self):
        free_obj = Free()

        class MaliciousPlayer(AbstractPlayer):
            def _get_move(self, universe):
                universe.teams[0].score = 100
                universe.bots[0].current_pos = (2,2)
                universe.maze[0,0][0] = free_obj
                return (0,0)

            def get_move(self):
                pass

        test_layout = (
            """ ######
                #0 . #
                #.. 1#
                ###### """)
        gm = GameMaster(test_layout, 2, 200)

        original_universe = gm.universe.copy()

        test_self = self
        class TestMaliciousPlayer(AbstractPlayer):
            def get_move(self):
                # universe should not have been altered
                test_self.assertEqual(original_universe, gm.universe)
                return (0,0)

        gm.register_team(SimpleTeam(MaliciousPlayer()))
        gm.register_team(SimpleTeam(TestMaliciousPlayer()))

        gm.set_initial()
        gm.play_round(0)

        test_self.assertEqual(original_universe, gm.universe)


    def test_viewer_must_not_change_gm(self):
        free_obj = Free()

        class MeanViewer(AbstractViewer):
            def set_initial(self, universe):
                universe.teams[1].score = 50

            def observe(self, round_, turn, universe, events):
                universe.teams[0].score = 100
                universe.bots[0].current_pos = (4,4)
                universe.maze[0,0][0] = free_obj

                events.append(TeamWins(0))
                test_self.assertEqual(len(events), 2)

        test_start = (
            """ ######
                #0 . #
                #.. 1#
                ###### """)

        number_bots = 2

        gm = GameMaster(test_start, number_bots, 200)
        gm.register_team(SimpleTeam(TestPlayer([(0,0)])))
        gm.register_team(SimpleTeam(TestPlayer([(0,0)])))

        original_universe = gm.universe.copy()

        test_self = self
        class TestViewer(AbstractViewer):
            def observe(self, round_, turn, universe, events):
                # universe should not have been altered
                test_self.assertEqual(original_universe, gm.universe)

                # there should only be a botmoves event
                test_self.assertEqual(len(events), 1)
                test_self.assertEqual(len(events), 1)
                test_self.assertTrue(BotMoves in events)

        gm.register_viewer(MeanViewer())
        gm.register_viewer(TestViewer())

        gm.set_initial()
        gm.play_round(0)

        self.assertEqual(original_universe, gm.universe)


