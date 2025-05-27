"""
SceneManager module for managing game scenes and transitions.
"""

class SceneManager:
    def __init__(self, screen):
        """
        Initialize the SceneManager.
        :param screen: The main pygame display surface.
        """
        self.screen = screen
        self.scenes = {}
        self.current_scene_key = None

    def register_scene(self, key, scene):
        """
        Register a scene with a unique key.
        :param key: String identifier for the scene.
        :param scene: Scene object with draw() and handle_event() methods.
        """
        self.scenes[key] = scene

    def set_scene(self, key):
        """
        Set the active scene by key.
        :param key: String identifier for the scene to activate.
        """
        if key in self.scenes:
            self.current_scene_key = key
        else:
            raise ValueError(f"Scene '{key}' not registered.")

    def handle_event(self, event):
        """
        Pass an event to the current scene.
        """
        if self.current_scene_key:
            return self.scenes[self.current_scene_key].handle_event(event)
        return None

    def draw(self):
        """
        Draw the current scene.
        """
        if self.current_scene_key:
            self.scenes[self.current_scene_key].draw() 