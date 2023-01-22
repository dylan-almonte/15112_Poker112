import sys
import os
sys.path.append('..')
from agents import GamePhase, PlayerState, ActionType
from table.BOARD import Community_Cards, Hand
from evaluator import eval
from table.DECK import Deck
from entities import Player,Pot,Table
import time

'''
resources used:

'''


class Poker:
    def __init__(self, buy_in, small_blind, big_blind, players):
        self.buy_in = buy_in
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.dealer = Deck()
        self.community_cards = Community_Cards()
        
        self.players = players
        self.pot = Pot(self.players)
        self.table = Table(self.players, self.pot)
        self.winners = ''
        self.winning_hand = ''
        self.sb = 0
        self.bb = 0
        self.btn = 0
        self.current_player = 0

        self.action = None
        self.action_amt = 0
        self.phase = GamePhase.PREHAND
        self.phase_gen = None
        self.isRunning = True

        self.phase_runner = {
            GamePhase.PREHAND: self.prehand,
            GamePhase.PREFLOP: lambda: self.betting_round(GamePhase.PREFLOP),
            GamePhase.FLOP: lambda: self.betting_round(GamePhase.FLOP),
            GamePhase.TURN: lambda: self.betting_round(GamePhase.TURN),
            GamePhase.RIVER: lambda: self.betting_round(GamePhase.RIVER),
            GamePhase.SETTLE: self.settle,
        }
    def collect_bets(self):
        self.pot.total += sum(player.bet_size for player in self.player_iter())

    def settle(self):
        active = {p.pos : p for p in self.table._active}
        

        self.current_player = next(self.player_iter(self.btn + 1,
                    filter_status=(PlayerState.OUT, PlayerState.SKIP))).pos
        if len(self.community_cards) < 5:
            self.dealer.deal_to(self.community_cards,
                                5 - len(self.community_cards))
        player_ranks = {}
        hands = {}
        for p_id, player in active.items():
            player_ranks[p_id] = eval.seven(
                player.hand + self.community_cards)
            hands[p_id] = str(player.hand + self.community_cards)


        best = min(player_ranks.values())
        winners = {p_id for p_id, rank in player_ranks.items()
                   if rank == best}
        self.winners = ' '.join([self.players[i].name for i in winners])
        self.winning_hand = ' '.join([hands[i] for i in winners])
        prize = self.pot.total_prize // (len(winners))
        for p_id in winners:
            self.players[p_id].chips += prize
        leftover = self.pot.total_prize - (prize * len(winners))
        if leftover:
            for player in active.values():
                if player in winners:
                    player.chips += leftover
                    break

    def prehand(self):
        
        for player in self.player_iter(pos=0):
            if player.chips == 0:
                player.state = PlayerState.SKIP
            else:
                player.state = PlayerState.TO_PLAY

        active = list(self.player_iter(self.btn + 1,
                    filter_status=(PlayerState.OUT, PlayerState.SKIP)))

        if len(active) <= 1:
            self.isRunning = False
            return

        self.btn = active[0].pos
        self.sb = active[1].pos

        if len(active) == 2:
            self.sb = self.btn

        self.bb = next(self.player_iter(self.sb + 1,
                    filter_status=(PlayerState.OUT, PlayerState.SKIP))).pos
        self.dealer = Deck()
        self.pot = Pot(self.players)
        self.community_cards = Community_Cards(set())

        self.declare_action(self.sb, self.small_blind)
        self.declare_action(self.bb, self.big_blind)

        for player in active:
            player.hand = Deck(set())
            self.dealer.deal_to(player.hand, 2)

        self.current_player = next(self.player_iter(self.bb + 1,
                    filter_status=(PlayerState.OUT, PlayerState.SKIP))).pos

    def declare_action(self, player_id, amount=0):
        amount = min(self.players[player_id].chips, amount)

        if amount == self.players[player_id].chips:
            self.players[player_id].state = PlayerState.ALL_IN
        else:
            self.players[player_id].state = PlayerState.IN

        self.pot._action(player_id,amount)

    
    def take_action(self, action, raised_to=0):
        curr = self.players[self.current_player]
        if action == ActionType.ALL_IN:
            action = ActionType.BET
            raised_to = curr.chips + curr.bet_size

        if action == ActionType.CHECK:
            pass
        elif action == ActionType.CALL:
            if curr.chips < self.pot.amount_to_call:
                self.declare_action(self.current_player,
                curr.chips)
            else: self.declare_action(self.current_player,
                self.pot.amount_to_call)
        elif action == ActionType.BET:
            self.declare_action(self.current_player, 
                raised_to + self.pot.amount_to_call)
        elif action == ActionType.FOLD:
            curr.state = PlayerState.OUT

    def betting_round(self, phase: GamePhase):
     
        self.dealer.deal_to(self.community_cards, phase.new_cards())

        self.current_player = self.btn + 1

        if phase == GamePhase.PREFLOP:
            self.current_player = self.bb + 1

        player_q = [player.pos for player in self.player_iter(self.current_player,
                 find_status=(PlayerState.TO_PLAY, PlayerState.IN))]

        while not self.hand_is_over():
            if not len(player_q):
                break
            self.current_player = player_q.pop(0)

            yield self
            if self.action != None:
                self.take_action(self.action, self.action_amt)
                if self.action is ActionType.BET:
                    player_q = [player.pos for player in 
                    self.player_iter(self.current_player,
                    find_status=(PlayerState.TO_PLAY, PlayerState.IN))][1:]
                

        self.pot.collect_bets()

    def player_iter(self, pos=None,
                    find_status=set(PlayerState), filter_status=set()):
        if pos == None:
            pos = self.current_player
        num = len(self.players)
        start, stop, step = pos, pos + num, 1
        for i in range(start, stop, step):
            if (
                self.players[i % num].state not in filter_status
                and self.players[i % num].state in find_status
            ):
                yield self.players[i % num]

    def hand_is_running(self):
        return self.phase != GamePhase.PREHAND

    def hand_is_over(self):
        count = 0

        for player in self.player_iter(
                find_status=(PlayerState.TO_PLAY, PlayerState.IN)):
            if player.state == PlayerState.TO_PLAY:
                return False
            if player.state == PlayerState.IN:
                count += 1
            if count > 1:
                return False
        return True

    def hand_iter(self):
        while self.hand_is_running():
            if self.hand_is_over():
                self.phase = GamePhase.SETTLE
            phase = self.phase_runner[self.phase]()
            self.phase = self.phase.next_phase()
            if phase:

                yield from phase

  

    def new_hand(self):
        self.phase = GamePhase.PREHAND
        self.phase_runner[self.phase]()

        if not self.isRunning:
            return

        self.phase = self.phase.next_phase()
        self.phase_gen = self.hand_iter()
        try:
            next(self.phase_gen)
        except StopIteration:
            pass

    def choose_action(self, action: ActionType, amount=0):
        self.action = action
        self.action_amt = amount
        if action != None:
            try:
                next(self.phase_gen)
            except StopIteration:
                pass



class AI(Player):
    def __init__(self, chips: int):
        super().__init__(1, chips,'AI')
        
        

    def decision(self, cc, pot: Pot):
        w_percent = eval.win_percent(self.hand,
                            cards = cc)
        ev = (w_percent * pot.total_prize) - ((1 - w_percent) * pot.amount_to_call)
        print(f'{w_percent} * {pot.total_prize} - {1-w_percent} * {pot.amount_to_call}')
        print(f'ev:{str(ev)[:5]} | {self.hand} + {cc}')
        
        if ev < 0.2 or w_percent < 0.3:
            print('ai folded')
            return ActionType.FOLD,0
        elif ev > 1.5:
    
            raised = (pot.total_prize // 2)
            print(f'ai raised to ${raised}')
            return ActionType.BET,raised
        else:
            print('ai called/checked')
            return ActionType.CALL,0
        
        


