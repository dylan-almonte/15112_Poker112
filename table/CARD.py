
import os
import random

"""


    We represent Card objects as native Python 32-bit integers. 
    Most of the bits are used, and have a specific meaning. See below:

    .. table:: Card
        :align: center
        :widths: auto

        +--------+--------+--------+--------+
        |xxxbbbbb|bbbbbbbb|cdhsrrrr|xxpppppp|
        +--------+--------+--------+--------+


    - p = prime number of rank (in binary) (deuce=2, trey=3, four=5, ..., ace=41)
    - r = rank of card (in binary) (deuce=0, trey=1, four=2, five=3, ..., ace=12)
    - cdhs = suit of card (bit turned on based on suit of card)
    - b = bit turned on depending on rank of card (deuce=1st bit, trey=2nd bit, ...)
    - x = unused

    **Example**
        .. table::
            :align: center
            :widths: auto

            +---------------+--------+--------+--------+-------+
            Card             xxxAKQJT 98765432 CDHSrrrr xxPPPPPP
            +---------------+--------+--------+--------+-------+
            King of Diamonds 00001000 00000000 01001011 00100101
            5    of Spades   00000000 00001000 00010011 00000111
            Jack of Clubs    00000010 00000000 10001001 00011101
            +---------------+--------+--------+--------+-------+
            


    This representation allows for minimal memory overhead along with fast applications
    necessary for poker:

        - Make a unique prime product for each hand (by multiplying the prime bits)
        - Detect flushes (bitwise && for the suits)
        - Detect straights (shift and bitwise &&)

"""


class Card:
    RANK_STRS: tuple = ('2', '3', '4', '5', '6', '7', '8',
                        '9', 'T', 'J', 'Q', 'K', 'A')
    RANK_INTS: int = tuple(range(2, 15))
    PRIME_INTS: tuple = (2,3,5,7,11,13,17,19,23,29,31,37,41)
    PRIMES: dict = dict(zip(RANK_STRS, PRIME_INTS))
    PRIME_BITS: dict = dict(zip(RANK_INTS, PRIME_INTS))
    PRIME_RANK = dict(zip(PRIME_INTS, RANK_STRS))
    RANKS: dict = dict(zip(RANK_STRS, RANK_INTS))
    
    SUITS: dict = {"C": 1,  # spades
                   "D": 2,  # hearts
                   "H": 4,  # diamonds
                   "S": 8, }  # clubs
    
    ID = '''=== +--------+--------+--------+--------+
     xxxAKQJT 98765432 rrrrSHDC xxPPPPPP\n'''

    def __init__(self, name):
        self.display = True
        self.rank = name[0]
        self.suit = name[1]
        self.prime = Card.PRIMES[self.rank]
        self.x = 100
        self.y = 100
        self.width = 0
        self.height = 0
        self.name = name
    def __repr__(self):
        return self.name
    

    @property
    def bit(self):
        rank_bit = Card.RANKS[self.rank]
        prime = Card.PRIMES[self.rank]
        suit_bit = Card.SUITS[self.suit]

        bitrank = 1 << rank_bit << 14
        suit = suit_bit << 8
        rank = rank_bit << 12
        return bitrank | rank | suit | prime

    @property
    def binary_str(self):
        sBinary = "{0:b}".format(1 << 32 | self.bit)
        bit_str = ' '.join([sBinary[i:i+8] for i in range(1, len(sBinary), 8)])
        card_str = f'{self.rank}{self.suit}'
        if len(card_str) == 2:
            card_str += ' '
        string = f'{card_str}  {bit_str}'
        return string

    


    def __hash__(self):
        return hash((self.rank, self.suit, self.bit))
    def __eq__(self,other):
        return self.name == other.name
    def flip(self):
        self.display = not self.display
    
    @staticmethod
    def _random(n = 1):
        # returns a set of random cards 
        rank = random.choice(Card.RANK_STRS)
        suit = random.choice(list(Card.SUITS))
        return Card(rank + suit)
    @staticmethod
    def pretty_binary(b):
        sBinary = "{0:b}".format(1 << 32 | b)
        bit_str = ' '.join([sBinary[i:i+8] for i in range(1, len(sBinary), 8)])
        return f'{Card.ID}===  {bit_str}'
    
