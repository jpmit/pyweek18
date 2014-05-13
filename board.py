import pygame
import pygame.locals as pl

from const import *
import globalobj
import cell

# board x and y dimensions (in pixels)
_BSIZE = (NX * CSIZE, NY * CSIZE)

# this makes a different since we are using alpha transparency
_FILL_COL = (224, 224, 224)

# grid surface to show grid lines
gridsurf = pygame.Surface((_BSIZE[0] + 1, _BSIZE[1] + 1))
gridsurf.fill(_FILL_COL)
# board surface
bsurf = pygame.Surface((_BSIZE[0] + 1, _BSIZE[1] + 1))
bsurf.set_colorkey(_FILL_COL)
brect = bsurf.get_rect()

def draw_grid(size):
    """size is (nx, ny) where nx is number of cells in x direction."""
    global gridsurf
    # total size of the grid in px
    pxsize = (size[0] * CSIZE, size[1] * CSIZE)
    for i in range(size[0] + 1):
        pygame.draw.line(gridsurf, GREY1, (i * CSIZE, 0), (i * CSIZE, pxsize[1]))
    for j in range(size[1] + 1):
        pygame.draw.line(gridsurf, GREY1, (0, j * CSIZE), (pxsize[0], j * CSIZE))

def clicked_board(pos):
    return (pos[0] > XOFF and pos[0] < _BSIZE[0] + XOFF 
            and pos[1] > YOFF and pos[1] < _BSIZE[1] + YOFF)

def get_clicked_cell(pos):
    return [(pos[0] - XOFF) / CSIZE, (pos[1] - YOFF) / CSIZE]

class BoardHandler(object):
    def __init__(self, board):
        self._board = board
        # is it the player's move at the moment?
        self._isplayer = True
        # bullet sprites
        self._bullets = []

    def handle_click(self, pos):
        if not self._isplayer:
            return
        c = self._board.get_cell(pos)
        if c:
            if (c.ctype == cell.C_MOVE or c.ctype == cell.C_PLAYER):
                globalobj.get_game().juke.play_sfx('click')
            if (c.ctype == cell.C_PLAYER):
                self._board.set_selected(pos)
            elif (c.ctype == cell.C_MOVE):
                self._board.make_move(pos)
                self.finish_player_move()

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
    
        if self._isplayer:
            self.update_player(dt)
        else:
            self.update_opponent(dt)
    
    def update_player(self, dt):
        if not self._board.can_move():
            print 'END!'
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
            if not brect.colliderect(b):
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

    def draw(self):
        if SHOWGRID:
            bsurf.blit(gridsurf, (0, 0))
        else:
            bsurf.fill(_FILL_COL)
        for c in self._board.get_cells():
            bsurf.blit(c.image, c.rect)
        for b in self._bullets:
            bsurf.blit(b.image, b.rect)

class GameBoard(object):
    """Stores the state and handles manipulation of this state only."""
    def __init__(self, fname):

        # dict keys are 'x-y' where x and y are cell indices
        self._cells = {}

        self.load_board(fname)
        # move this somewhere else?
        draw_grid(self._size)
        self.selected = None

    def load_board(self, fname):
        lines = open(fname, 'r').readlines()
        row = 0
        self._size = (len(lines[0]), len(lines))
        for line in lines:
            col = 0
            for c in line.strip():
                if c != 'X':
                    ctype, kw = cell.IMAP[c] 
                    self.add_cell([col, row], ctype, **kw)
                col += 1
            row += 1

    def can_hit(self, g):
        """Return true if gun cell can hit player, false otherwise."""
        direction = g.direction
        for p in self.get_cells_by_type(cell.C_PLAYER):
            if (direction == cell.D_UP):
                if (g.pos[0] == p.pos[0]) and (g.pos[1] > p.pos[1]):
                    return True
            elif (direction == cell.D_DOWN):
                if (g.pos[0] == p.pos[0]) and (g.pos[1] < p.pos[1]):
                    return True
            elif (direction == cell.D_LEFT):
                if (g.pos[1] == p.pos[1]) and (g.pos[0] > p.pos[0]):
                    return True
            elif (direction == cell.D_RIGHT):
                if (g.pos[1] == p.pos[1]) and (g.pos[0] < p.pos[0]):
                    return True
        return False
    
    def add_cell(self, pos, ctype, **kwargs):
        if kwargs:
            c = cell.CMAP[ctype](pos, **kwargs)
        else:
            c = cell.CMAP[ctype](pos)

        self._cells['{0}-{1}'.format(pos[0], pos[1])] = c

    def can_move(self):
        """Is a move possible?"""
        all_moves = []
        for c in self.get_cells_by_type(cell.C_PLAYER):
            movs = self.get_moves(c.pos)
            all_moves += movs
        if all_moves:
            return True
        return False

    def remove_cell(self, pos):
        k = '{0}-{1}'.format(pos[0], pos[1])
        if k in self._cells:
            del self._cells[k]

    def get_cell(self, pos):
        k = '{0}-{1}'.format(pos[0], pos[1])
        if k in self._cells:
            return self._cells[k]
        return None

    def is_ctype(self, pos, ctype):
        c = self.get_cell(pos)
        if c and (c.ctype == ctype):
            return True
        return False

    def get_cells(self):
        """Return list of cell objects."""
        return self._cells.values()
    
    def get_cells_by_type(self, ctype):
        cs = []
        for c in self.get_cells():
            if (c.ctype == ctype):
                cs.append(c)
        return cs

    def delete_moves(self):
        """Remove possible move cells from the board."""
        for c in self.get_cells():
            if (c.ctype == cell.C_MOVE):
                self.remove_cell(c.pos)
    
    def get_moves(self, pos):
        add_moves = []
        for x in [pos[0] - 1, pos[0], pos[0] + 1]:
            for y in [pos[1] - 1, pos[1], pos[1] + 1]:
                if (x >= 0) and (x < self._size[0]) and (y >= 0) and (y < self._size[1]):
                    c = self.get_cell([x, y])
                    if c and c.ctype != cell.C_GOAL:
                        continue
                    # check if possible move is adjacent to a player cell
                    for p in [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]:
                        if (self.is_ctype(p, cell.C_PLAYER) and p != pos):
                            add_moves.append([x, y])
                            break
        return add_moves

    def add_moves(self, sel):
        """Add any possible move cells to the board."""

        addpos = self.get_moves(sel)
        for pos in addpos:
            self.add_cell(pos, cell.C_MOVE)
    
    def make_move(self, pos):
        """Make a move to pos. From is given by self.selected."""
        # replace the cell at move to position with a player
        c = self.get_cell(self.selected)
        self.remove_cell(pos)
        self.add_cell(pos, cell.C_PLAYER, **{'health': c.health})
        self.remove_cell(self.selected)
        # get rid of the possible move cells that weren't selected
        self.delete_moves()
        self.selected = None

    def set_selected(self, pos):
        if self.selected:
            self.get_cell(self.selected).selected = False

        # delete any previous moves cells
        self.delete_moves()
            
        # if we clicked on the currently selected cell, unselect it
        if pos == self.selected:
            self.selected = None
        else:
            c = self.get_cell(pos)
            c.selected = True
            self.selected = pos
            # add new moves cells
            self.add_moves(self.selected)
