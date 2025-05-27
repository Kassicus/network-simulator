import pygame

class TitleScreenScene:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.bg_color = (24, 26, 32)
        self.title_color = (220, 220, 220)
        self.button_color = (40, 44, 52)
        self.button_hover_color = (60, 64, 72)
        self.button_text_color = (220, 220, 220)
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 36)
        self.title = 'Network Simulator'
        self.buttons = [
            {'label': 'Start Game', 'rect': pygame.Rect(self.WIDTH//2-120, self.HEIGHT//2, 240, 60)},
            {'label': 'Quit', 'rect': pygame.Rect(self.WIDTH//2-120, self.HEIGHT//2+80, 240, 60)}
        ]
        self.selected = None

    def draw(self):
        self.screen.fill(self.bg_color)
        # Draw title
        title_surf = self.title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.WIDTH//2, self.HEIGHT//2-120))
        self.screen.blit(title_surf, title_rect)
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            rect = button['rect']
            is_hovered = rect.collidepoint(mouse_pos)
            color = self.button_hover_color if is_hovered else self.button_color
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            # Draw button text
            text_surf = self.button_font.render(button['label'], True, self.button_text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, button in enumerate(self.buttons):
                if button['rect'].collidepoint(event.pos):
                    return button['label']
        return None 