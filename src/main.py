import pygame
import sys
from scene_title import TitleScreenScene
from scene_desk import PlayerDeskScene
from scene_manager import SceneManager

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Network Simulator')

# Scene management
scene_manager = SceneManager(screen)
scene_manager.register_scene('title', TitleScreenScene(screen))
scene_manager.register_scene('desk', PlayerDeskScene(screen))
scene_manager.set_scene('title')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            result = scene_manager.handle_event(event)
            if scene_manager.current_scene_key == 'title':
                if result == 'Start Game':
                    scene_manager.set_scene('desk')
                elif result == 'Quit':
                    running = False
    scene_manager.draw()

pygame.quit()
sys.exit() 