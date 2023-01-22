import sys
import os
sys.path.append('..')
from cmu_112_graphics import *
from game import Poker,AI
from agents import Screen,ActionType
from entities import Player
import gui
import math,time



def appStarted(app):
    app.screen = Screen.SPLASH
    app.buy_in = 100
    app.sb = 1
    app.bb = 2
    app.game = None
    app.action = None
    app.bet_size = 0
    app.btns = gui.game_buttons(app)
    
    app.menu_btns = gui.menu_buttons(app)
    app.running = False
    app.mx, app.my = 0,0
    
    app.slider = app.width * (3/16),app.height * (9/10)
    app.stats = False
    app.player = None
    app.gameover = False
    


def user_btns_moved(app,event):
    for btn in app.btns:
        btn.mouseHovered(app,event)
def game_btn_actions(app,event):
    current = app.game.players[app.game.current_player]
    pot = app.game.pot
    if app.fold_btn.clicked(app,event): 
        app.game.choose_action(ActionType.FOLD)
    if app.check_btn.clicked(app,event):
        if pot.amount_to_call != current.bet_size:
            app.showMessage('INVALID MOVE')
        else: app.game.choose_action(ActionType.CHECK)
    if app.call_btn.clicked(app,event):
        if pot.amount_to_call == 0:
            app.showMessage('INVALID MOVE')
        else: app.game.choose_action(ActionType.CALL)
    if app.bet_btn.clicked(app,event): 
        app.game.choose_action(ActionType.BET, app.bet_size)
    app.action = None
def mousePressed(app,event):
    if app.screen in {Screen.MULTI,Screen.AI}:
        game_btn_actions(app,event)
    elif app.screen == Screen.SPLASH:
        if app.multi_btn.clicked(app,event):
            app.screen = Screen.MULTI
            players = {i:Player(i, app.buy_in, f'Player{i+1}')
                                for i in range(6)}
            app.game = Poker(app.buy_in, app.sb, app.bb, players)
            app.running = True

        if app.vs_ai_btn.clicked(app,event):
            app.screen = Screen.AI
            player_name = app.getUserInput('Enter in your name:')
            players = {
                0: Player(0,app.buy_in,player_name), 
                1: AI(app.buy_in)}
            game = Poker(app.buy_in, app.sb, app.bb,players)
            app.player = players[0]
            app.game = game
            app.running = True
       
def mouseMoved(app,event):
    if app.screen in {Screen.AI, Screen.MULTI}:
        user_btns_moved(app,event)
def mouseDragged(app,event):
    if app.screen in {Screen.AI, Screen.MULTI} and app.running:
        app.bet_btn.text = f'bet: {app.bet_size}'
        gui.slider(app,event)

def keyPressed(app,event):
    if event.key == 'Escape':
        appStarted(app)
    if event.key == 'S':
        app.stats = not app.stats

def timerFired(app):
    if app.screen == Screen.MULTI and app.running:
        if app.game.hand_is_running():
            app.game.choose_action(app.action)
        else: 
            app.game.new_hand()
            
    elif app.screen == Screen.AI and app.running:
        current = app.game.current_player
        ai = app.game.players[1]
        pot = app.game.pot
        cc = app.game.community_cards
        if app.player.chips == 0:
                app.gameover = True 
        if app.game.hand_is_running():
             
            if current == 1:
                
                app.game.choose_action(*ai.decision(cc,pot))
                time.sleep(1)
            elif current == 0:
                app.game.choose_action(app.action)
                app.action = None
        else:
            app.game.new_hand()
        
            
        
        
def draw_game(app,canvas):
    gui.draw_board(app,canvas)
    gui.draw_players(app,canvas,app.game,app.game.players)
    gui.draw_pot(app,canvas,app.game.pot)
    gui.draw_community(app,canvas,app.game.community_cards)
    gui.draw_game_btns(app,canvas)
    gui.draw_slider(app,canvas)
    
def draw_game_over(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = 'black')
    canvas.create_text(app.width/2,app.height/2,
                        text = 'YOU LOST', 
                        font = f'Arial {int(app.height / 15)}', 
                        fill = 'white')
    canvas.create_text(app.width/2,app.height*(2/3),
                        text = 'press ESC to start over', 
                        font = f'Arial {int(app.height / 15)}', 
                        fill = 'white')
def redrawAll(app, canvas):
    
    if app.gameover:
        draw_game_over(app,canvas)
    else:
        canvas.create_rectangle(0,0,app.width,app.height, fill = 'black')
        canvas.create_text(app.width/2,app.height/2,
                        text = 'ENTER NAME', 
                        font = f'Arial {int(app.height / 15)}', 
                        fill = 'white')
        if app.screen in {Screen.AI, Screen.MULTI} and app.running:
            draw_game(app,canvas)
            
        elif app.screen == Screen.SPLASH:
            gui.draw_menu(app,canvas)
    
    
        
runApp(width=1000, height=600)


