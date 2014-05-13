"""Resource store and loader."""

import os
import pygame

_my_path = os.path.abspath(os.path.dirname(__file__))
# paths to image, font and sound directories
_image_path = os.path.normpath(os.path.join(_my_path, 'image'))
_font_path = os.path.normpath(os.path.join(_my_path, 'font'))
_sound_path = os.path.normpath(os.path.join(_my_path, 'sound'))

images = {'bg': 'paper.png',
          'goal': 'goal.png',
          'arrowleft': 'arrowleft.png',
          'arrowdown': 'arrowdown.png',
          'arrowright': 'arrowright.png',
          'arrowup': 'arrowup.png'}

# value is name, size in pts
fonts = {'main': ('ShareTechMono-Regular.ttf', 30)}

sfx = {'click': 'click.ogg'}

music = {'reawakening': 'reawakening.ogg'}

def load_resources():
    global fonts, images, sfx, music

    for key, val in images.items():
        images[key] = pygame.image.load(os.path.join(_image_path, val)).convert_alpha()
    for key, val in fonts.items():
        fonts[key] = pygame.font.Font(os.path.join(_font_path, val[0]), val[1])
    for key, val in sfx.items():
        sfx[key] = pygame.mixer.Sound(os.path.join(_sound_path, val))
    for key, val in music.items():
        # all we need is the full path here
        music[key] = os.path.join(_sound_path, val)