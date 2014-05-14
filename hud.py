import pygame
import pygame.locals as pl
import rstore
import score

from const import *

# this makes a different since we are using alpha transparency
_FILL_COL = (224, 224, 224)

# transparent surface to blit to
hsurf = pygame.Surface(HUD_SIZE, pl.SRCALPHA, 32)
#hsurf.set_colorkey(_FILL_COL)

def pos_on_hud(pos):
    return (pos[0] > HUD_POS[0] and pos[0] < HUD_POS[0] + HUD_SIZE[0] 
            and pos[1] > HUD_POS[1] and pos[1] < HUD_POS[1] + HUD_SIZE[1])

# color of all text on HUD
_HUDCOL = BLACK
# x offset for text
_X_OFF = 20

class Hud(object):
    def __init__(self, board):
        self._board = board
        self.smallfont = rstore.fonts['hudsmall']
        self.largefont = rstore.fonts['hudlarge']
        self.set_data(0)

        self.besttxt = self.smallfont.render('Best', True, _HUDCOL)

    def set_data(self, lnum):
        self.set_text(lnum)

    def set_text(self, lnum):
        self.set_level(lnum)
        self.set_moves(0)
        self.set_saved(0)
        self.set_lost(0)
        self.set_high_score(score.scores[lnum])

    def draw(self):
        #hsurf.fill(_FILL_COL)
        hsurf.blit(rstore.images['hud'], (0, 0))
        hsurf.blit(self.levtxt, (_X_OFF, 0))
        hsurf.blit(self.movtxt, (_X_OFF, 120))
        hsurf.blit(self.savetxt, (_X_OFF, 150))
        hsurf.blit(self.losttxt, (_X_OFF, 180))
        hsurf.blit(self.besttxt, (_X_OFF, 220))
        hsurf.blit(self.scoretxt, (_X_OFF, 240))
        pass

    def set_high_score(self, sc):
        s0 = score.get_score_string(sc[0])
        s1 = score.get_score_string(sc[1])
            
        self.scoretxt = self.smallfont.render('Saved: {0} Moves: {1}'.format(s0, s1),
                                              True, _HUDCOL)

    def set_level(self, level):
        self.levtxt = self.largefont.render('Level {0}'.format(level),
                                            True, _HUDCOL)

    def set_moves(self, moves):
        self.movtxt = self.smallfont.render('Moves: {0}'.format(moves),
                                            True, _HUDCOL)

    def set_lost(self, lost):
        self.losttxt = self.smallfont.render('Bits lost: {0}/8'.format(lost),
                                             True, _HUDCOL)

    def set_saved(self, saved):
        self.savetxt = self.smallfont.render('Bits saved: {0}/8'.format(saved),
                                             True, _HUDCOL)
