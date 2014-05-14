import pygame
import pygame.locals as pl

import time
import rstore
import score
from scene import PlayScene, TitleScene
import globalobj
import const

def withsound(fn):
    """Decorator for a class method."""
    def wrapped(self, *args, **kwargs):
        if self.soundon:
            fn(self, *args, **kwargs)
        return None
    return wrapped

class JukeBox(object):
    """Game jukebox that handles music and sfx."""
    def __init__(self):
        try:
            pygame.mixer.init()
        except: 
            self.soundon = False
        else:
            self.soundon = True
        
        # mapping of file names to sound effects and music
        self.sfx = rstore.sfx
        self.music = rstore.music

        self.playing = None
    
    @withsound
    def play_music(self, name):
        pygame.mixer.music.load(self.music[name])
        # -1 means repeat
        pygame.mixer.music.play(-1)
        self.playing = name

    @withsound
    def play_music_if(self, name):
        """Play music if not already playing."""

        if self.playing != name:
            self.play_music(name)
    
    @withsound
    def stop_music(self):
        pygame.mixer.music.stop()
    
    @withsound
    def play_sfx(self, name):
        self.sfx[name].play()


class Game(object):
    def __init__(self):
        """Setup pygame, display, resource loading etc."""
        
        pygame.init()
        self.screen = pygame.display.set_mode(const.SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        # load images, fonts and sounds
        rstore.load_resources()

        # high scores
        score.load_high_scores()
        
        self.juke = JukeBox()

        self.juke.play_music('reawakening')

        pygame.mouse.set_cursor(*pygame.cursors.tri_left)

    def mainloop(self):
        
        # first scene of the game
        ascene = TitleScene(self)

        # initialize clock
        dt = self.clock.tick(const.FPS) / 1000.0

        while ascene != None:
            # get all events we are interested in.
            quitevent = False
            events = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quitevent = True
                if ((event.type == pl.MOUSEBUTTONDOWN) or 
                    (event.type == pl.MOUSEBUTTONUP)):
                    events.append(event)

            # scene specific updating based on events.
            ascene.process_input(events, dt)

            # update not based on events.
            ascene.update(dt)

            # draw to the screen.
            ascene.render(self.screen)

            # possible change to new scene.
            ascene = ascene.next

            # draw to the screen!
            pygame.display.flip()

            # delay for correct time here.
            dt = self.clock.tick(const.FPS) / 1000.0
                
            if quitevent:
                ascene = None
                pygame.quit()

if __name__ == "__main__":
    gm = Game()
    def get_game():
        return gm
    globalobj.get_game = get_game
    gm.mainloop()
