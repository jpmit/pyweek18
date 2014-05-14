import pygame
import pygame.locals as pl
import rstore

from const import *

# this makes a different since we are using alpha transparency
_FILL_COL = (224, 224, 224)

# transparent surface to blit to
hsurf = pygame.Surface(HUD_SIZE, pl.SRCALPHA, 32)
#hsurf.set_colorkey(_FILL_COL)

def pos_on_hud(pos):
    return (pos[0] > HUD_POS[0] and pos[0] < HUD_POS[0] + HUD_SIZE[0] 
            and pos[1] > HUD_POS[1] and pos[1] < HUD_POS[1] + HUD_SIZE[1])


class Hud(object):
    def __init__(self, board):
        self._board = board
        self.smallfont = rstore.fonts['hudsmall']
        self.largefont = rstore.fonts['hudlarge']
        self.set_data(0)

        # get buttons

    def set_data(self, lnum):
        self.set_text(lnum)

    def set_text(self, lnum):
        self.set_level(lnum)
        self.set_moves(0)
        self.set_saved(0)
        self.set_lost(0)

    def draw(self):
        #hsurf.fill(_FILL_COL)
        hsurf.blit(rstore.images['hud'], (0, 0))
        hsurf.blit(self.levtxt, (0, 0))
        hsurf.blit(self.movtxt, (0, 100))
        hsurf.blit(self.savetxt, (0, 200))
        hsurf.blit(self.losttxt, (0, 250))
        pass

    def set_level(self, level):
        self.levtxt = self.largefont.render('Level {0}'.format(level),
                                            True, GREY1)

    def set_moves(self, moves):
        self.movtxt = self.smallfont.render('Moves: {0}'.format(moves),
                                            True, GREY1)

    def set_lost(self, lost):
        self.losttxt = self.smallfont.render('Bits lost: {0}/8'.format(lost),
                                             True, GREY1)

    def set_saved(self, saved):
        self.savetxt = self.smallfont.render('Bits saved: {0}/8'.format(saved),
                                             True, GREY1)
