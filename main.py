import pygame
import sys
from game import Game

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Curse of Tus")

game = Game(screen)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:  
            game.handle_key_press(event.key)
            if event.key == pygame.K_LCTRL or event.key == pygame.K_l:  # Ctrl ou C pour dash
                game.player.dash(game.world)
    
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)