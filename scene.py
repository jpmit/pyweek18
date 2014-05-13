import os

import pygame
import pygame.locals as pl

from const import *
import board
import cell
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
        self._board = board.GameBoard()
        self.levnum = 0
        self.load_level()

    def load_level(self):
        print self.levnum
        fname = 'l{0}.txt'.format(self.levnum)
        self._board.load_board(_get_level(fname))
        # is it the player's move at the moment?
        self._isplayer = True
        # bullet sprites
        self._bullets = []
        # store clicked board cell
        self._clickcell = None

        self.game.juke.play_music('reawakening')

        self.next = self

    def process_input(self, events, dt):

        for ev in events:
            if (ev.type == pl.MOUSEBUTTONDOWN):
                # did we click on board?
                if board.clicked_board(ev.pos):
                    self._clickcell = board.get_clicked_cell(ev.pos)
            elif (ev.type == pl.MOUSEBUTTONUP):
                if (board.get_clicked_cell(ev.pos) == self._clickcell):
                    self.handle_board_click(self._clickcell)
                    self._clickcell = None

    def handle_board_click(self, pos):
        if not self._isplayer:
            return
        # can we move to this position
        if self._board.is_move_cell(pos):
            self.game.juke.play_sfx('click')
            self._board.make_move(pos)
            self.finish_player_move()
        else:
            if self._board.is_player_cell(pos):
                self.game.juke.play_sfx('click')
                self._board.set_selected(pos)

    def finish_player_move(self):
        """Called at the end of the player move"""
        self._isplayer = False
        # create bullets
        playercells = self._board.get_cells_by_type(cell.C_PLAYER)
        guncells = self._board.get_cells_by_type(cell.C_GUN)
        for g in guncells:
            p = [g.pos[0] * CSIZE + OUTLINE, g.pos[1] * CSIZE + OUTLINE]
            if self._board.can_hit(g):
                self._bullets.append(cell.BulletSprite(p))
        
    def finish_opponent_move(self):
        pass
        
    def update(self, dt):

        for c in self._board.get_cells():
            c.update(dt)
        for c in self._board.get_move_cells():
            c.update(dt)
    
        if self._isplayer:
            self.update_player(dt)
        else:
            self.update_opponent(dt)
    
    def update_player(self, dt):
        if not self._board.can_move():
            print 'FINISHED!'
            self.next = LevelCompleteScene(self)
            # change scene here
            pass
        else:
            pass

    def update_opponent(self, dt):
        # advance bullets
        playercells = self._board.get_cells_by_type(cell.C_PLAYER)
        for b in list(self._bullets):
            b.update(dt)
            # remove if off screen
            if not board.brect.colliderect(b):
                self._bullets.remove(b)
            # check for collision with player
            for p in playercells:
                if pygame.sprite.collide_rect(b, p):
                    # we hit the player
                    self._bullets.remove(b)
                    p.health -= 1
                    if (p.health == 0):
                        self._board.remove_cell(p.pos)
                
        # check if all bullets are gone, and if so give player control
        # back
        if not self._bullets:
            self._isplayer = True
            self.finish_opponent_move()

    def render(self, screen):
        # blit background
        screen.blit(rstore.images['bg'], (0, 0))

        # render to the board surface
        if SHOWGRID:
            board.bsurf.blit(board.gridsurf, (0, 0))
        else:
            board.bsurf.fill(_FILL_COL)
        # goal cells
        for c in self._board.get_goal_cells():
            board.bsurf.blit(c.image, c.rect)
        # player / enemy cells
        for c in self._board.get_cells():
            board.bsurf.blit(c.image, c.rect)
        # move cells
        for c in self._board.get_move_cells():
            board.bsurf.blit(c.image, c.rect)            
        # enemy 'bullets'
        for b in self._bullets:
            board.bsurf.blit(b.image, b.rect)

        # blit the board surface to the screen
        screen.blit(board.bsurf, (XOFF, YOFF))
        pass

class LevelCompleteScene(Scene):
    def __init__(self, pscene):
        super(LevelCompleteScene, self).__init__()

        self.pscene = pscene
        self.tpassed = 0

    def update(self, dt):
        self.tpassed += dt
        if self.tpassed > 3:
            print 'level up'
            self.pscene.levnum += 1
            self.pscene.load_level()
            self.next = self.pscene

class TitleScene(Scene):
    def __init__(self, game):
        super(TitleScene, self).__init__()
        self._game = game
    
    def process_input(self, events, dt):
        for e in events:
            if (e.type == pl.MOUSEBUTTONUP):
                self.next = PlayScene(self._game)
