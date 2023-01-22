import time
import math
import sys
sys.path.append('..')
from table.CARD import Card
from table.DECK import Deck
from table.BOARD import Community_Cards, Hand
from evaluator.lookup_table import LOOKUP
import itertools as it
import random as rd



def five(cc):

    if Deck.is_flush(cc):
        return LOOKUP.flush[Deck.prime_prod(cc)]
    return LOOKUP.unique[Deck.prime_prod(cc)]


def seven(h_cc):
    return min(five(deck) for deck in it.combinations(h_cc, 5))



def win_percent(h1,cards = Deck(set()), n = 1000):
    score = 0
    for _ in range(n):
        h2 = Hand._random(h1 + cards)
        cc = Deck._random(h1 + h2 + cards)
        hand1 = seven(h1 + cc + cards)
        hand2 = seven(h2 + cc + cards)
        if hand1 < hand2:  score += 1
        
    return score / n



