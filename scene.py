import os

import pygame.locals as pl
from const import *
import board
import rstore

class Scene(object):
    """Abstract base class."""

    def __init__(self):
        # the next property is accessed every iteration of the main
        # loop, to get the scene.  When we want to change to a new
        # scene, we simply set self.next = LevelCompleteScene() (for
        # example).  This should be done in the update() method below.
        self.next = self

    def process_input(self, events, dt):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass


def _get_level(fname):
    """Return full path to level file."""

    my_path = os.path.abspath(os.path.dirname(__file__))
    level_path = os.path.normpath(os.path.join(my_path, 'level'))
    return os.path.join(level_path, fname)
    
class PlayScene(Scene):
    def __init__(self, game):
        super(PlayScene, self).__init__()

        self.game = game

        # for handling the board
        self._boardhandler = board.BoardHandler(board.GameBoard(_get_level('l1.txt')))

        # store clicked board cell
        self._clickcell = None

        self.game.juke.play_music('reawakening')

    def process_input(self, events, dt):

        for ev in events:
            if (ev.type == pl.MOUSEBUTTONDOWN):
                # did we click on board?
                if board.clicked_board(ev.pos):
                    self._clickcell = board.get_clicked_cell(ev.pos)
            elif (ev.type == pl.MOUSEBUTTONUP):
                if (board.get_clicked_cell(ev.pos) == self._clickcell):
                    self._boardhandler.handle_click(self._clickcell)
                    self._clickcell = None
        
    def update(self, dt):
        self._boardhandler.update(dt)

    def render(self, screen):
        # blit background
        screen.blit(rstore.images['bg'], (0, 0))
        #screen.fill(BLACK)
        # render the board surface and blit to screen
        self._boardhandler.draw()
        screen.blit(board.bsurf, (XOFF, YOFF))
        pass

class TitleScene(Scene):
    def __init__(self, game):
        super(TitleScene, self).__init__()
        self._game = game
    
    def process_input(self, events, dt):
        for e in events:
            if (e.type == pl.MOUSEBUTTONUP):
                self.next = PlayScene(self._game)
