import pygame
import sys
from scene_title import TitleScreenScene
from scene_desk import PlayerDeskScene
from scene_server_room import ServerRoomScene
from scene_manager import SceneManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

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
scene_manager.register_scene('server_room', ServerRoomScene(screen, scene_manager))
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
                    logging.info("Switched to desk scene after title.")
                elif result == 'Quit':
                    running = False
            elif scene_manager.current_scene_key == 'desk':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    scene_manager.set_scene('server_room')
                    logging.info("Switched to server room scene from desk.")
            elif scene_manager.current_scene_key == 'server_room':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    scene_manager.set_scene('desk')
                    logging.info("Switched to desk scene from server room.")
    # Call update if the current scene has it
    current_scene = scene_manager.scenes.get(scene_manager.current_scene_key)
    if hasattr(current_scene, 'update'):
        current_scene.update(dt)
    scene_manager.draw()

pygame.quit()
sys.exit() 