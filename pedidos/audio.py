from pygame import mixer
import pygame
from time import sleep
pygame.init()
mixer.init()
mixer.music.load("som.wav") # Music file can only be MP3
mixer.music.play()
# Then start a infinite loop
while True:
	sleep(3)
	break