import pygame

from const import *
import rstore
import util

# key is the level num
_TUTSTEPS = {0: [
    # can split the the text over as many lines as we want, it will be
    # formatted
    ["Click on the flashing bit.",
     [[1, 4]], 0],
    ["The white cells are possible moves for this bit.",
     [], 5],
    ["Each bit can move into one of its 8 neighbouring cells.",
     [], 5],
    ["As long as that cell isn't occupied.",
     [], 5],
    ["And as long as the move will leave the bit " 
      "with at least one neighbour on either the vertical or horizontal.",
     [], 5],
    ["Click on one of the white cells to move this bit.",
     [[1, 3], [2, 3], [2, 5]], 0],
    ["Try moving the bit that is on its own.",
     [[6, 4]], 0],
    ["There are no white cells, "
     "indicating no moves are possible.",
     [], 2]
]
}


# this makes a different since we are using alpha transparency
_FILL_COL = (224, 224, 224)

tsurf = pygame.Surface(TUT_SIZE)

def pos_on_tutorial(pos):
    # tsurf changes in size so we need current size
    tsize = tsurf.get_size()
    return (pos[0] > TUT_POS[0] and pos[0] < TUT_POS[0] + tsize[0]
            and pos[1] > TUT_POS[1] and pos[1] < TUT_POS[1] + tsize[1])

def draw_tutorial(tut):
    # this is a bit of a mess currently...
    global tsurf
    # only need to remake the surface if tutorial changed on last turn
    if tut.changed:
        if tut.step is None:
            tsurf = pygame.Surface((0, 0))
            return
        font = rstore.fonts['tutorial']
        tlines = util.wrap_multi_line(tut.step.text, font, 
                                      TUT_SIZE[0] - 2 * TUT_BORDER - 2* TUT_OFFSET)
        # height of each line
        char_height = font.size(tlines[0][0])[1]
        nlines = len(tlines)
        # make the main tutorial surface of the correct size
        height = nlines * char_height + 2 * TUT_BORDER + 2 * TUT_OFFSET + (nlines - 1) * TUT_LINE_PAD
        tsurf = pygame.Surface((TUT_SIZE[0], height))
        tsurf.fill(GREY1)
        # blit center surface so that we have a border
        midsurf = pygame.Surface((TUT_SIZE[0] - 2 * TUT_BORDER,
                                  height - 2 * TUT_BORDER))
        midsurf.fill(_FILL_COL)
        tsurf.blit(midsurf, (TUT_BORDER, TUT_BORDER))
        for i, line in enumerate(tlines):
            mt = rstore.fonts['tutorial'].render(line, True, GREY1)
            tsurf.blit(mt, (0 + TUT_BORDER + TUT_OFFSET, TUT_BORDER + TUT_OFFSET + (TUT_LINE_PAD + char_height) * i))

class Step(object):
    """A single step of the tutorial."""
    def __init__(self, text, toclick, ttot):
        self.text = text
        # we won't advance to the next step until one of the cells in
        # toclick list has been clicked.
        self.toclick = toclick
        # if we aren't waiting for a user click, we finish after a set
        # time.
        self.timeout = (ttot > 0)
        self.tleft = ttot
        self.finished = False

    def update(self, dt):
        return
#        if not self.timeout:
#            return
#
#        self.tleft -= dt
#        if (self.tleft <= 0):
#            self.finished = True

class Tutorial(object):
    def __init__(self, playscene):

        self._steps = []
        # the actual logic of the tutorial is a series of steps
        self.load_steps(playscene.levnum)

        self.changed = True
        if self.step:
            draw_tutorial(self)

    def load_steps(self, levelnum):
        stepdata = _TUTSTEPS.get(levelnum, [])
        for s in stepdata:
            self._steps.append(Step(text=s[0], toclick=s[1], ttot=s[2]))
        if self._steps:
            self.step = self._steps[0]
        else:
            self.step = None

    def is_finished(self):
        return not self._steps

    def is_allowed(self, cpos):
        """Is clicking on the cell allowed at this point in the tutorial?"""
        if self.step is None:
            return True
        
        # has the player clicked on one of the allowed cells?
        if (cpos in self.step.toclick):
            # mark step as finished
            self.step.finished = True
            return True
        return False
    
    def try_advance(self):
        """
        Advance to the next tutorial step if possible (i.e. we are not
        waiting for the user to click a certain cell.
        """
        if not self.step.toclick:
            self.step.finished = True

    def get_allowed_cells(self):
        """Return list of cells we are waiting for user to click on."""
        if self.step is None:
            return []
        return self.step.toclick

    def advance(self):
        self._steps.pop(0)
        if self._steps:
            self.step = self._steps[0]
        else:
            self.step = None

    def update(self, dt):
        self.changed = False
        if self.step:
            self.step.update(dt)
            if self.step.finished:
                self.changed = True
                self.advance()



def get_tutorial(playscene):
    return Tutorial(playscene)
