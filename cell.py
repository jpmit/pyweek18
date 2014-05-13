import pygame

import rstore
from const import *

# cell types
C_PLAYER = 'player'
C_GUN = 'gun'
C_GOAL = 'goal'
C_MOVE = 'move'

# directions for the gun
D_UP = 'up'
D_LEFT = 'left'
D_RIGHT = 'right'
D_DOWN = 'down'

class BulletSprite(object):
    _SPEED = 500
    def __init__(self, pos):
        self.image = pygame.Surface((CSIZE - 2 * OUTLINE, CSIZE - 2 * OUTLINE))
        self.image.fill(OTHERCOL)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
    def update(self, dt):
        self.rect.x += self._SPEED * dt

class CellSprite(object):
    """Base class, a sprite that is confined to a cell"""
    def __init__(self, pos):
        # pos is cell index
        self.pos = pos
        self.image = pygame.Surface((CSIZE - 2 * OUTLINE, CSIZE - 2 * OUTLINE))

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.pos[0] * CSIZE + OUTLINE, 
                             self.pos[1] * CSIZE + OUTLINE)

    def update(self, dt):
        pass

class GunCellSprite(CellSprite):
    def __init__(self, pos, **kwargs):
        super(GunCellSprite, self).__init__(pos)
        self.ctype = C_GUN
        self.direction = kwargs['direction']
        self.image = rstore.images['arrow' + self.direction]

class GoalCellSprite(CellSprite):
    def __init__(self, pos):
        super(GoalCellSprite, self).__init__(pos)
        self.ctype = C_GOAL
        self.image.fill(GCOL)
#        self.image = rstore.images['goal']

class PlayerCellSprite(CellSprite):
    def __init__(self, pos, **kwargs):
        super(PlayerCellSprite, self).__init__(pos)
        self.ctype = C_PLAYER
        self.health = kwargs['health']
        # can be selected (clicked on)
        self.selected = False
        # image for when cell selected and when cell not selected
        self.set_image()
    
    def set_image(self):
        # draw the health value to the middle of the 
        txt = rstore.fonts['main'].render(str(self.health), True, WHITE)
        # need different colors here for the different numbers!

        if self.selected:
            self.image.fill(YELLOW)
            pygame.draw.rect(self.image, pygame.Color(PCOL[self.health]), 
                             (OUTLINE, OUTLINE, CSIZE - 4 * OUTLINE, CSIZE - 4 * OUTLINE))
            self.image.set_alpha(128)
        else:
            self.image.fill(pygame.Color(PCOL[self.health]))
            self.image.set_alpha(255)

        self.image.blit(txt, (0, 0))
    
    def update(self, dt):
        self.set_image()

class PlayerMoveCellSprite(CellSprite):
    def __init__(self, pos):
        super(PlayerMoveCellSprite, self).__init__(pos)
        self.ctype = C_MOVE
        self.image.fill(MOVCOL)


# mapping of cell type to class object
CMAP = {C_PLAYER: PlayerCellSprite,
        C_GUN: GunCellSprite,
        C_GOAL: GoalCellSprite,
        C_MOVE: PlayerMoveCellSprite}


# mapping of input symbol in text file to cell type and any other
# parameters needed in constructor.
IMAP = {'E': (C_GOAL, {}),
        # wasd are guns shooting in the expected directions
        'W': (C_GUN, {'direction': D_UP}),
        'A': (C_GUN, {'direction': D_LEFT}),
        'S': (C_GUN, {'direction': D_DOWN}),
        'D': (C_GUN, {'direction': D_RIGHT}),
        '1': (C_PLAYER, {'health': 1}),
        '2': (C_PLAYER, {'health': 2}),
        '3': (C_PLAYER, {'health': 3}),
        '4': (C_PLAYER, {'health': 4}),
        '5': (C_PLAYER, {'health': 5})}
