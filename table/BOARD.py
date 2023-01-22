import sys
sys.path.append('..')
import random
from table.DECK import Deck



class Community_Cards(Deck):
    def __init__(self,stack = set()):
        super().__init__(stack)
        self.stack = stack

    


class Hand(Deck):
    def __init__(self,stack = set()):
        super().__init__()
        self.stack = stack

    @staticmethod
    def _random(cards = None):
        deck = Deck().stack 
        if cards != None: deck |= cards.stack
        new = set(random.sample(list(deck), k = 2)) 
        return Deck(new)


# def appStarted(app):
#     app.board = board
#     for i, card in enumerate(app.board):
#         card.x += card.img.width*i + 10*i
#     app.timerDelay = 1


# def mouseDragged(app, event):
#     app.board.mouseDragged(app, event)


# def mousePressed(app, event):
#     app.board.mousePressed(app, event)


# def redrawAll(app, canvas):
#     canvas.create_rectangle(0, 0, app.width, app.height, fill='black')
#     app.board.draw(app, canvas)
