import pygame
import sys
from scene_title import TitleScreenScene
from scene_desk import PlayerDeskScene
from scene_manager import SceneManager

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Network Simulator')

# Scene management
scene_manager = SceneManager(screen)
scene_manager.register_scene('title', TitleScreenScene(screen))
scene_manager.register_scene('desk', PlayerDeskScene(screen))
scene_manager.set_scene('title')

# Set up cursor blink timer
CURSOR_EVENT = pygame.USEREVENT
pygame.time.set_timer(CURSOR_EVENT, 500)

clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60)
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
    # Call update if the current scene has it
    current_scene = scene_manager.scenes.get(scene_manager.current_scene_key)
    if hasattr(current_scene, 'update'):
        current_scene.update(dt)
    scene_manager.draw()

pygame.quit()
sys.exit() 