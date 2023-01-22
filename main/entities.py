import sys
import os
sys.path.append('..')
from agents import GamePhase, PlayerState, ActionType
from table.BOARD import Community_Cards, Hand
from table.DECK import Deck
from evaluator import eval




  


class Player:
    def __init__(self, position: int, chips: int = 0, name=None):
        self.name = name
        self.chips = chips
        self.bet_size = 0

        self.state = PlayerState.IN
        self.hand = Deck(set())
        self.seat = position
        self.x = 0
        self.y = 0
        self.pos = position
        self.has_played = False
    def choose_action(self, action: ActionType):
        pass


class Pot:
    def __init__(self,players: dict[Player]):
        self.total = 0
        self.raised = 0
        self.players = players
        # dictionary containing player index as the key and the chips as
        
    @property
    def amount_to_call(self):
        return max(player.bet_size for player in self.players.values())
    @property
    def total_prize(self):
        return sum(player.bet_size for player in self.players.values()) + self.total

    def _action(self, p_id: int, amount: int):
        self.players[p_id].bet_size += amount
        self.players[p_id].chips -= amount
        

    def collect_bets(self):
        self.total += sum(player.bet_size for player in self.players.values()) 
        for player in self.players.values(): player.bet_size = 0

    
    
    def _reward(self, p_id, amount):
        self.players[p_id].chips += amount
        self.total = 0

    



class Table:
    def __init__(self, players: dict[Player], pot: Pot):
        self.players: set[Player] = set(players.values())
        self.total_table_chips: int = sum(p.chips for p in self.players)

        self.pot = pot

        self.dealer = Deck()
        self.community = Community_Cards()
    
    @property
    def _active(self):
        return [p for p in self.players 
                if p.state not in {PlayerState.SKIP, PlayerState.OUT}]
    
    def _rotate(self):
        for p in self._active: p.pos = (p.pos + 1) % len(self._active)

    def everyone_played(self):
        return len(self.active_players) > 1
    
  
