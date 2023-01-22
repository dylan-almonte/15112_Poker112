from enum import Enum, auto
from dataclasses import dataclass
class PlayerState(Enum):
    IN = auto()
    OUT = auto()
    SKIP = auto()
    ALL_IN = auto()
    TO_PLAY = auto()

class ActionType(Enum):
    IDLE = auto()
    ALL_IN = auto()
    CHECK = auto()
    CALL = auto()
    BET = auto()
    FOLD = auto()

@dataclass(frozen = True)
class Phase:
    new_cards: int
    next_phase: str

class Screen(Enum):
    SPLASH = auto()
    MULTI = auto()
    AI = auto()
    
class GamePhase(Enum):
    PREHAND = Phase(0,'PREFLOP')
    PREFLOP = Phase(0,'FLOP')
    FLOP = Phase(3,'TURN')
    TURN = Phase(1,'RIVER')
    RIVER = Phase(1,'SETTLE')
    SETTLE = Phase(0,'PREHAND')

    def new_cards(self):
        return self.value.new_cards
    def next_phase(self):
        return GamePhase[self.value.next_phase]
