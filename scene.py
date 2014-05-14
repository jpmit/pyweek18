import os

import pygame
import pygame.locals as pl

from const import *
import board
import hud
import cell
import rstore
import tutorial

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
        self._hud = hud.Hud(self._board)

        self.levnum = 0
        self.load_level()

        self.game.juke.play_music('reawakening')

    def load_level(self):
        # load the data onto the board
        fname = 'l{0}.txt'.format(self.levnum)
        self._board.setup_board(_get_level(fname))
        # update the HUD
        self._hud.set_data(self.levnum)
        # reset any game state
        self._isplayer = True
        # bullet sprites
        self._bullets = []
        # store clicked board cell
        self._clickcell = None
        # cell positions of any bits the tutorial wants to flash
        self._tutflash = []
        # load the relevant tutorial
        self._tutorial = tutorial.get_tutorial(self)

        self.next = self

    def pos_on_board(self, pos):
        return False

    def pos_on_hud(self, pos):
        return False

    def mouseup_board(self, pos):
        if (board.get_clicked_cell(pos) == self._clickcell):
            if self._tutorial.is_allowed(self._clickcell):
                self.handle_board_click(self._clickcell)
                self._clickcell = None

    def mousedown_board(self, pos):
        self._clickcell = board.get_clicked_cell(pos)
        pass

    def mouseover_board(self, pos):
        pass
    
    def mouseup_hud(self, pos):
        pass

    def mousedown_hud(self, pos):
        pass

    def mousedown_tutorial(self, pos):
        pass

    def mouseup_tutorial(self, pos):
        self._tutorial.try_advance()
        pass

    def mouseover_board(self, pos):
        pass

    def process_input(self, events, dt):

        # mouse position
        mpos = pygame.mouse.get_pos()

        # mouse clicks
        if board.pos_on_board(mpos):
            self.mouseover_board(mpos)
        elif hud.pos_on_hud(mpos):
            self.mouseover_hud(mpos)

        for ev in events:
            if (ev.type == pl.MOUSEBUTTONDOWN):
                if tutorial.pos_on_tutorial(ev.pos):
                    self.mousedown_tutorial(ev.pos)
                elif board.pos_on_board(ev.pos):
                    self.mousedown_board(ev.pos)
                elif hud.pos_on_hud(ev.pos):
                    self.mousedown_hud(ev.pos)
            elif (ev.type == pl.MOUSEBUTTONUP):
                if tutorial.pos_on_tutorial(ev.pos):
                    self.mouseup_tutorial(ev.pos)
                elif board.pos_on_board(ev.pos):
                    self.mouseup_board(ev.pos)
                elif hud.pos_on_hud(ev.pos):
                    self.mouseup_hud(ev.pos)

    def handle_board_click(self, pos):
        if not self._isplayer:
            return
        # can we move to this position
        if self._board.is_move_cell(pos):
            if self._board.is_goal_cell(pos):
                self.game.juke.play_sfx('goal')
            else:
                self.game.juke.play_sfx('click')
            self._board.make_move(pos)
            # update the hud
            self._hud.set_moves(self._board.nmoves)
            self._hud.set_saved(self._board.nsaved)
            self.finish_player_move()
        elif self._board.is_player_cell(pos):
            self.game.juke.play_sfx('click')
            self._board.set_selected(pos)
        else:
            pass
            #self.game.juke.play_sfx('error')

    def finish_player_move(self):
        """Called at the end of the player move"""
        self._isplayer = False
        # create bullets
        playercells = self._board.get_cells_by_type(cell.C_PLAYER)
        guncells = self._board.get_cells_by_type(cell.C_GUN)
        for g in guncells:
            p = [g.pos[0] * CSIZE + OUTLINE, g.pos[1] * CSIZE + OUTLINE]
            if self._board.can_hit(g):
                self._bullets.append(cell.BulletSprite(p, g.direction))
                # we hit the player
                self.game.juke.play_sfx('shoot')
        
    def finish_opponent_move(self):
        pass

    def handle_tutorial_cells(self):
        """Make the right bits flash for this stage of the tutorial."""
        # set any currently flashing bits to not flash
        for cpos in self._tutflash:
            c = self._board.get_cell(cpos)
            if c is not None:
                c.set_flash(False)
        self._tutflash = []
        # check if there are any new bits to flash
        allowed_pos = self._tutorial.get_allowed_cells()
        for cpos in allowed_pos:
            #if self._board.is_player_cell(cpos):
            self._tutflash.append(cpos)
            c = self._board.get_cell_or_move_cell(cpos)
            c.set_flash(True)
        
    def update(self, dt):

        for c in self._board.get_cells():
            c.update(dt)
        for c in self._board.get_move_cells():
            c.update(dt)
    
        if self._isplayer:
            self.update_player(dt)
        else:
            self.update_opponent(dt)

        # update tutorial
        if self._tutorial.changed:
            self.handle_tutorial_cells()
        self._tutorial.update(dt)
    
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
                    self._bullets.remove(b)
                    p.health -= 1
                    if (p.health == 0):
                        self._board.nlost += 1
                        self._hud.set_lost(self._board.nlost)
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
        board.draw_board(self._board, self._bullets)

        # render to the HUD surface
        self._hud.draw()

        # render to the tutorial surface
        tutorial.draw_tutorial(self._tutorial)

        # blit the board surface to the screen
        screen.blit(board.bsurf, (XOFF, YOFF))

        # blit the hud surface to the screen
        screen.blit(hud.hsurf, HUD_POS)

        # blit the tutorial surface to the screen
        screen.blit(tutorial.tsurf, TUT_POS)
        pass

class LevelCompleteScene(Scene):
    def __init__(self, pscene):
        super(LevelCompleteScene, self).__init__()

        self.pscene = pscene
        self.tpassed = 0

    def update(self, dt):
        self.tpassed += dt
        if self.tpassed > 1:
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
