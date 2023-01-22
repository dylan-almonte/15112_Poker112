import sys
import os
sys.path.append('..')
from game import PlayerState, ActionType, GamePhase, Player, Pot, Poker
from table.DECK import Deck, Card
from table.BOARD import Community_Cards, Hand
from cmu_112_graphics import *
from agents import Screen
import math


CARD_DIRECTORY = os.listdir('Poker_PNG')
CARD_IMG = {file[:-4]: file for file in CARD_DIRECTORY}

CARD_SCALE = 1/15
CHIP_SCALE = 1/25
CARD_WIDTH = 46
CARD_HEIGHT = 70


def draw_board(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill='black')
    canvas.create_oval(app.width * (1/5), app.height * (1/10),
                       app.width * (4/5), app.height * (7/10),
                       fill='green', outline='green')
    # draw_community(app,canvas,app.community_cards)


def draw_card(app, canvas, card, x, y):
    card.x, card.y = x, y
    card_scale = min(app.width, app.height)/10
    img_path = CARD_IMG[card.rank + card.suit]
    if card.display:
        img = Image.open(f'Poker_PNG/{img_path}')
    else:
        img = Image.open('Poker_PNG/flipped.png')
    aspect_ratio = img.width/img.height
    card.width, card.height = aspect_ratio*card_scale, card_scale
    img = img.resize((int(card.width), int(card.height)))

    canvas.create_image(card.x, card.y,
                        image=ImageTk.PhotoImage(img))


def draw_pot(app, canvas, pot: Pot):
    table_cx = (app.width / 2)
    table_cy = app.height * (2/5)
    img = Image.open('Poker_PNG/chips.png')
    size = min(app.height, app.width)/15
    ratio = img.width / img.height
    img = img.resize((int(ratio*size), int(size)))
    canvas.create_image(table_cx - size, table_cy * (7/8),
                        image=ImageTk.PhotoImage(img))

    canvas.create_text(table_cx + size, table_cy * (7/8),
                       text=f'total: {pot.total_prize} | to call: {pot.amount_to_call}', 
                       font=f'Arial {int(app.width/80)} bold',
                       fill='white')
    canvas.create_text(table_cx + size, table_cy * (13/16) ,
                        text = f'last winner {app.game.winners} | {app.game.winning_hand}', 
                        font = f'Arial {int(app.width / 80)}', 
                        fill = 'white')


def draw_community(app, canvas, community):
    table_cx = (app.width / 2)
    table_cy = app.height * (2/5)
    if len(community.stack) > 0:
        for i, card in enumerate(community):
            draw_card(app, canvas, card, table_cx +
                      card.width*(i-2), table_cy * 1.1)


def draw_hand(app, canvas, player, x, y):
    if len(player.hand) > 0:
        for i, card in enumerate(player.hand):
            if x < app.width/2:
                draw_card(app, canvas, card, x + card.width*(i-1), y)
            elif x > app.width/2:
                draw_card(app, canvas, card, x + card.width*(i), y)


def draw_players(app, canvas, game, players):
    table_cy = app.height * (2/5)
    table_width = app.width * (3/5)
    table_height = app.height * (6/10)
    table_left = app.width/5
    table_right = app.width * (4/5)
    if app.screen == Screen.AI:
        players[1].x, players[1].y = (
        table_left + table_width/4, table_cy - table_height * (7/16))
        players[0].x, players[0].y = (
        table_right - table_width/4, table_cy + table_height * (7/16))
    elif app.screen == Screen.MULTI:
        players[0].x, players[0].y = table_left,table_cy
        players[1].x, players[1].y = (
            table_left + table_width/4, table_cy - table_height * (7/16))
        players[2].x, players[2].y = (table_right - table_width/4
                                         ,table_cy - table_height * (7/16))
        players[3].x, players[3].y = (table_right,table_cy)
        players[4].x, players[4].y = (
            table_right - table_width/4, table_cy + table_height * (7/16))
        players[5].x, players[5].y = (table_left + table_width/4
                                         ,table_cy + table_height * (7/16))
    for player_id in players:
        player = players[player_id]
        draw_player(app, canvas, game, player, player.x, player.y)

    draw_player_bets(app, canvas, players)
    draw_player_hands(app, canvas, players)


def draw_player(app, canvas, game, player, x, y):
    pr = app.width / 25
    color = 'gray'
    highlight = 'black'
    player.hand.hide_cards()
    if player.state == PlayerState.TO_PLAY:
        highlight = 'white'
    elif player.state == PlayerState.OUT:
        color = 'gray20'
    
    if player.pos == game.current_player and app.screen == Screen.MULTI:
        player.hand.show_cards()
        highlight = 'yellow'
    elif app.screen == Screen.AI:
        if player.pos == 0:
            player.hand.show_cards()
        if player.pos == game.current_player:
            highlight = 'yellow'
    if app.stats:
        player.hand.show_cards()
    canvas.create_oval(x-pr, y-pr, x+pr, y+pr, fill=color, outline=highlight)

    if player.pos == game.btn:
        canvas.create_text(x, y,
                           text='BTN', font=f'Arial {int(pr/2)} bold')
    elif player.pos == game.sb:
        canvas.create_text(x, y,
                           text='SB', font=f'Arial {int(pr/2)} bold')
    elif player.pos == game.bb:
        canvas.create_text(x, y,
                           text='BB', font=f'Arial {int(pr/2)} bold')
    canvas.create_rectangle(x-pr, y+pr, x+pr, y+(pr*1.5), fill='black')
    canvas.create_text(x, y+(pr*1.25),
                       text=f'{player.name}: ${player.chips}', font=f'Arial {int(pr/4)} bold')


def draw_chips(app, canvas, player, x, y):
    img = Image.open('Poker_PNG/chips.png')
    size = min(app.height, app.width)/15
    ratio = img.width / img.height
    img = img.resize((int(ratio*size),
                      int(size)))
    if player.bet_size > 0:
        canvas.create_image(x, y,
                            image=ImageTk.PhotoImage(img))
        canvas.create_text(x, y+img.height/2,
                           text=f'{player.bet_size}', font=f'Arial {int(app.width/80)} bold',
                           fill='white')


def draw_player_bets(app, canvas, players):
    pr = app.width / 25
    table_height = app.height * (3/5)
    if app.screen == Screen.MULTI:
        draw_chips(app,canvas,players[0], players[0].x + pr * 1.75, players[0].y)

        draw_chips(app, canvas, players[1], players[1].x + pr * 1.75,
                players[1].y + table_height * (1/16))

        draw_chips(app,canvas,players[2], players[2].x - pr * 1.75,
                                        players[2].y + table_height * (1/16))

        draw_chips(app,canvas,players[3], players[3].x - pr * 1.75, players[3].y)

        draw_chips(app, canvas, players[4], players[4].x - pr * 1.75,
                players[4].y - table_height * (1/16))

        draw_chips(app,canvas,players[5], players[5].x + pr * 1.75,
                                        players[5].y - table_height * (1/16))
    if app.screen == Screen.AI:
        draw_chips(app, canvas, players[1], players[1].x + pr * 1.75,
                    players[1].y + table_height * (1/16))
        draw_chips(app, canvas, players[0], players[0].x - pr * 1.75,
                    players[0].y - table_height * (1/16))

def draw_player_hands(app, canvas, players):
    pr = app.width / 25
    table_cx = app.width/2
    for player_id in players:
        player = players[player_id]
        if player.x > table_cx:
            draw_hand(app, canvas, player, player.x + pr*2, player.y)
        elif player.x < table_cx:
            draw_hand(app, canvas, player, player.x - pr*2, player.y)

def menu_buttons(app):
    app.multi_btn = Button('white', 'multiplayer (pass and play)')
    app.vs_ai_btn = Button('white', '1v1 vs ai')
    return app.multi_btn,app.vs_ai_btn
def draw_menu(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = 'black')
    app.multi_btn.draw(app,canvas, app.width*(2/5), app.height/2)
    app.vs_ai_btn.draw(app,canvas, app.width*(3/5), app.height/2)
    draw_title(app, canvas)

def game_buttons(app):
    app.fold_btn = Button( 'red', 'fold')
    app.check_btn = Button( 'spring green', 'check')
    app.call_btn = Button( 'cyan', 'call')
    app.bet_btn = Button( 'cyan', f'bet: {app.bet_size}')
    return (app.fold_btn, app.check_btn, app.call_btn, app.bet_btn)

def draw_game_btns(app,canvas):
    x = app.width*(3/4)
    y = app.height*(9/10)
    for i,btn in enumerate(app.btns):
        btn.draw(app,canvas, app.width-x*((i+1)/5), y)

def game_btns_moved(app, event):
    for btn in game_buttons(app):
        btn.mouseHovered(app, event)

class Button:
    def __init__(self, color, text):
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.x0 = 0
        self.x1 = 0
        self.y0 = 0
        self.y1 = 0
        
        self.r = 0
        self.color = color
        self.filled = 'black'
        self.text = text
        self.hovered = False

    def draw(self, app, canvas, x, y):
        self.x,self.y = x,y
        self.width = app.width/12
        self.height = app.height/10
        self.x0 = x - self.width/2
        self.x1 = x + self.width/2
        self.y0 = y - self.height/2
        self.y1 = y + self.height/2
        self.r = self.height / 2
        if self.hovered:
            self.draw_filled(app, canvas, self.color)

        else:
            self.draw_outlined(app, canvas, self.color)

    def mouseHovered(self, app, event):
        self.hovered = ((event.x > self.x0-self.r) and (event.x < self.x1+self.r) and
                        (event.y > self.y0) and (event.y < self.y1))

    def clicked(self, app, event):
        return ((event.x > self.x0) and (event.x < self.x1) and
                (event.y > self.y0) and (event.y < self.y1))

    def draw_filled(self, app, canvas, color):
        
        canvas.create_oval(self.x0-self.r, self.y-self.r,
                           self.x0+self.r, self.y+self.r,
                           fill=color, outline=color)
        canvas.create_oval(self.x1-self.r, self.y-self.r,
                           self.x1+self.r, self.y+self.r,
                           fill=color, outline=color)
        canvas.create_rectangle(self.x0, self.y0,
                                self.x1, self.y1,
                                fill=color, outline=color)

        self.draw_outlined(app, canvas, self.filled)

    def draw_outlined(self, app, canvas, color):
        canvas.create_arc(self.x0-self.r, self.y-self.r,
                          self.x0+self.r, self.y+self.r,
                          style='arc', start='90', extent=180,
                          outline=color)
        canvas.create_arc(self.x1-self.r, self.y-self.r,
                          self.x1+self.r, self.y+self.r,
                          style='arc', start='90', extent=-180,
                          outline=color)
        canvas.create_line(self.x0, self.y0, self.x1, self.y0,
                           fill=color)
        canvas.create_line(self.x0, self.y1, self.x1, self.y1,
                           fill=color)
        canvas.create_text(self.x, self.y,
                           text=self.text.upper(), font=f'Arial {int(self.width/10)}',
                           fill=color)

def draw_slider(app,canvas):
    x0 = app.width * (1/16)
    x1 = app.width * (5/16)
    y0 = app.height * (9/10)
    r = (x0-x1)//20
    canvas.create_line(x0,y0,x1,y0, fill = 'white')
    x,y = app.slider
    canvas.create_oval(x+r,y+r,x-r,y-r, fill = 'white')
def slider(app,event):
    x0 = app.width * (1/16)
    x1 = app.width * (5/16)
    y = app.height * (9/10)
    r = (x0-x1)//20
    chips = app.game.players[app.game.current_player].chips 
    if event.x > x0 and event.x < x1 and event.y > y+r and event.y < y-r:
        app.slider = event.x,y
        app.bet_size = math.ceil((event.x-x0)/(x1-x0) * chips)
    elif event.x < x0 and event.y > y+r and event.y < y-r:
        app.slider = x0,y
        app.bet_size = app.game.pot.amount_to_call * 2
    elif event.x > x0 and event.y > y+r and event.y < y-r:
        app.slider = x1,y
        app.bet_size = chips
    
    else: app.slider = (x0+x1)/2,y


def draw_title(app,canvas):
    x0 = app.width * (1/5)
    x1 = app.width * (4/5)
    y0 = app.height * (2/5)
    y1 = app.height * (1/5)
    size = app.height / 15
    canvas.create_line(x0,y0,x1,y0, fill = 'white')
    canvas.create_line(x0,y1,x1,y1, fill = 'white')
    canvas.create_text(app.width//2, app.height * (3/10), 
        text = 'WELCOME TO 112 POKER', font = f'Arial {int(size)}', fill = 'white')
    canvas.create_text(app.width//2, app.height * (7/10), 
        text = 'press esc anytime to leave to menu', font = f'Arial {int(size/3)}', 
        fill = 'white')
# def 