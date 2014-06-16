import sys
from cx_Freeze import setup, Executable

setup(
    name = "Save all 8 bits",
    version = "0.1",
    description = "A puzzle game made for PyWeek18",
    executables = [Executable("run_game.py", base = "Win32GUI")]
)
