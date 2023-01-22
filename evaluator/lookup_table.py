import sys
sys.path.append('..')


import table.DECK
from table.CARD import Card

import itertools

import sys
sys.path.append('..')
# rank distribution of hand rankings
# MAX_STRAIGHT_FLUSH = 10
# MAX_FOUR_OF_A_KIND = 166
# MAX_FULL_HOUSE = 322
# MAX_FLUSH = 1599
# MAX_STRAIGHT = 1609
# MAX_THREE_OF_A_KIND = 2467
# MAX_TWO_PAIR = 3325
# MAX_PAIR = 6185
# MAX_HIGH_CARD = 7462


def prime_prod_from_bits(bits):
    product = 1
    for rank in Card.RANKS:
        # if the ith bit is set
        if bits & (1 << (Card.RANKS[rank]-2)):
            product *= Card.PRIMES[rank]
    return product


class Lookup_Table:

    def __init__(self):
        # create dictionaries
        self.flush: dict = {}
        self.unique: dict = {}
        self.FLUSH()
        self.multiples()

    def FLUSH(self):
        """
        Straight flushes and flushes.

        Lookup is done on 13 bit integer (2^13 > 7462):
        xxxbbbbb bbbbbbbb => integer hand index

        """

        # straight flushes in rank order
        straight_flushes = {
            7936:   1,  # int('0b1111100000000', 2), # royal flush
            3968:   2,  # int('0b111110000000', 2),
            1984:   3,  # int('0b11111000000', 2),
            992:    4,  # int('0b1111100000', 2),
            496:    5,  # int('0b111110000', 2),
            248:    6,  # int('0b11111000', 2),
            124:    7,  # int('0b1111100', 2),
            62:     8,  # int('0b111110', 2),
            31:     9,  # int('0b11111', 2),
            4111:   10, # int('0b1000000001111', 2) # 5 high
        }

        # now we'll dynamically generate all the other
        # flushes (including straight flushes)
        flushes = set()
        flush = int("0b11111", 2)

        for _ in range(1286):  

            xbits = (flush | (flush - 1)) + 1
            flush = xbits | ((((xbits & -xbits) // (flush & -flush)) >> 1) - 1)

            if flush not in straight_flushes:
                flushes.add(flush)

        flushes = sorted(flushes)
        
       
        for straight_flush, rank in straight_flushes.items():
            prime_product = prime_prod_from_bits(straight_flush)
            self.flush[prime_product] = rank
            

        rank = 323
        for flush in flushes:
            prime_product = prime_prod_from_bits(flush)
            self.flush[prime_product] = rank
            rank += 1

        self.straight_highcards(straight_flushes, flushes)

    def straight_highcards(self, straights, highcards):
        rank = 1600

        for straight in straights:
            prime_product = prime_prod_from_bits(straight)
            self.unique[prime_product] = rank
            rank += 1

        rank = 6186
        for high_card in highcards:
            prime_product = prime_prod_from_bits(high_card)
            self.unique[prime_product] = rank
            rank += 1

    def multiples(self):
        ranks = Card.RANK_STRS
        # 1) Four of a Kind
        rank = 166
        for r in ranks:
            for k in ranks:
                if r is not k:
                    product = Card.PRIMES[r] ** 4 * Card.PRIMES[k]
                    self.unique[product] = rank
                    rank -= 1
                
            

        # 2) Full House
        rank = 322
        for r in ranks:
            for k in ranks:
                if r is not k:
                    product = Card.PRIMES[r] ** 3 * Card.PRIMES[k] ** 2
                    self.unique[product] = rank
                    rank -= 1

        # 3) Three of a Kind
        rank = 2467

        # pick three of one rank
        for r in ranks:
            for kickers in itertools.combinations(ranks, 2):
                if r not in kickers:
                    card1, card2 = kickers
                    product = (
                        Card.PRIMES[r] ** 3 *
                        Card.PRIMES[card1] * Card.PRIMES[card2]
                    )
                    self.unique[product] = rank
                    rank -= 1

        # 4) Two Pair
        rank = 3325
        for two_pair in itertools.combinations(ranks, 2):
            pair1, pair2 = two_pair
            for kicker in ranks:
                if kicker not in two_pair:
                    product = (
                        Card.PRIMES[pair1] ** 2
                        * Card.PRIMES[pair2] ** 2
                        * Card.PRIMES[kicker]
                    )
                    self.unique[product] = rank
                    rank -= 1
                    
       
        # 5) Pair
        rank = 6185

        # choose a pair
        for r in ranks:
            for kickers in itertools.combinations(ranks, 3):
                if r not in kickers:
                    kicker1, kicker2, kicker3 = kickers
                    product = (
                        Card.PRIMES[r] ** 2
                        * Card.PRIMES[kicker1]
                        * Card.PRIMES[kicker2]
                        * Card.PRIMES[kicker3]
                    )
                    
                    self.unique[product] = rank
                    rank -= 1
   
    def _combine(self):
        self.five = self.flush | self.unique
    
    @staticmethod
    def prime_to_rank(num):
        n = num
        ranks = []
        if not num:
            return ranks
        while n % 2 == 0:
            ranks.append(Card.PRIME_RANK[2])
            n /= 2
        for i in range(3,int(n**0.5)+1,2):
            while n % i == 0:
                ranks.append(Card.PRIME_RANK[i] )
                n /= i
        if n > 2: ranks.append(Card.PRIME_RANK[n])
        return ' '.join(ranks[::-1])
    
    


LOOKUP = Lookup_Table()
