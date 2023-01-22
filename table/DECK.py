import sys
sys.path.append('..')
import math
import random
from table.CARD import Card



class Deck:
    def __init__(self, stack=None):
        if stack == None:
            self.stack = {Card(r+s) for r in Card.RANKS for s in Card.SUITS}
        else:
            self.stack = stack
        # self.shuffle()

    def __len__(self):
        return len(self.stack)

    def __repr__(self):
        string = sorted([c.name for c in self.stack])
        return ' '.join(reversed(string))

    def __iter__(self):
        self.index = 0
        self.cards = list(self.stack)
        return self

    def __next__(self):
        if self.index < len(self.stack):
            card = self.cards[self.index]
            
            self.index += 1
            return card
            
        else:
            raise StopIteration

    # def __getitem__(self,card):
    #     if isinstance(card,Card): return self.stack[card]

    def deal_to(self, other, amt=1):
        if isinstance(amt, int) and isinstance(other, Deck):
            
            cards = list(self.stack)
            random.shuffle(cards)
            other.stack.update(cards[:amt])
            self.stack = (cards[amt:])

    @property
    def binary_str(self):
        string = Card.ID
        for card in self.stack:
            string += f'{card.binary_str}\n'
        string += '=== +--------+--------+--------+--------+'
        return string

    def __add__(self, other):
        if isinstance(other, Deck):
            return Deck(set(list(self.stack)+list(other.stack)))

    @staticmethod
    def _random(cards_sofar):
        deck = list(Deck().stack | cards_sofar.stack)
        new = set(random.sample(deck, k= 9-len(cards_sofar)))
        return Deck(new)

    @property
    def prime_product(self):
        return math.prod(card.prime for card in self.stack)

    @staticmethod
    def prime_prod(cards):
        return math.prod(card.prime for card in cards)

    @staticmethod
    def is_flush(cards):
        flsh = 0xF00
        for c in cards:
            flsh &= c.bit
        return flsh

    @staticmethod
    def bit(cards):
        bit = 0
        for card in cards:
            bit |= card.bit
        return bit

    def show_cards(self):
        for card in self:
            card.display = True

    def hide_cards(self):
        for card in self:
            card.display = False

    def flip_cards(self):
        for card in self:
            card.flip()
