"""
Module for the Player Desk scene.
Handles UI and logic for the player's main computer and remote access.
"""

import pygame
from soggy_os import SoggyOS

class PlayerDeskScene:
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = (24, 26, 32)
        self.title_color = (220, 220, 220)
        self.monitor_color = (0, 0, 0)  # Black for terminal
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.term_font = pygame.font.SysFont('Consolas', 22)
        self.term_color = (0, 255, 0)  # Green text
        self.dir_color = (0, 128, 255) # Blue for directories
        self.file_color = (255, 255, 255) # White for files
        self.title = 'Desk'
        self._update_monitor_rect()
        # SoggyOS instance
        self.os = SoggyOS()
        self.input_buffer = ''
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500  # ms
        # Editor state
        self.editor_mode = False
        self.editor_path = None
        self.editor_content = ''
        self.editor_original_content = ''
        self.editor_log = []  # For audit logging
        self.editor_status = ''
        self.editor_command_buffer = ''
        self.editor_in_command_mode = False

    def _update_monitor_rect(self):
        width, height = self.screen.get_size()
        monitor_width = int(width * 0.7)
        monitor_height = int(height * 0.6)
        self.monitor_rect = pygame.Rect(
            (width - monitor_width) // 2,
            (height - monitor_height) // 2,
            monitor_width,
            monitor_height
        )

    def draw(self):
        self._update_monitor_rect()
        self.screen.fill(self.bg_color)
        # Draw title in upper left
        title_surf = self.title_font.render(self.title, True, self.title_color)
        self.screen.blit(title_surf, (24, 16))
        # Draw monitor rectangle
        pygame.draw.rect(self.screen, self.monitor_color, self.monitor_rect, border_radius=16)
        if self.editor_mode:
            # Draw editor overlay
            self._draw_editor()
        else:
            # Draw terminal output and prompt
            term_x = self.monitor_rect.x + 18
            term_y = self.monitor_rect.y + 18
            line_height = self.term_font.get_height() + 4
            max_lines = (self.monitor_rect.height - 36) // line_height - 1
            output_lines = self.os.get_output()[-max_lines:]
            for entry in output_lines:
                if isinstance(entry, dict) and 'ls' in entry:
                    # Render ls output as columns
                    names = entry['ls']
                    if not names:
                        term_y += line_height
                        continue
                    col_width = max(len(name) for name, _ in names) * 14 + 20  # Estimate width per col
                    cols = max(1, (self.monitor_rect.width - 36) // col_width)
                    for i in range(0, len(names), cols):
                        row = names[i:i+cols]
                        col_x = term_x
                        for name, typ in row:
                            if typ == 'dir':
                                color = self.dir_color
                            elif typ == 'file':
                                color = self.file_color
                            else:
                                color = self.term_color
                            name_surf = self.term_font.render(name, True, color)
                            self.screen.blit(name_surf, (col_x, term_y))
                            col_x += col_width
                        term_y += line_height
                else:
                    line_surf = self.term_font.render(str(entry), True, self.term_color)
                    self.screen.blit(line_surf, (term_x, term_y))
                    term_y += line_height
            # Draw prompt and input buffer
            prompt = self.os.get_prompt() + self.input_buffer
            if self.cursor_visible:
                prompt += '_'
            prompt_surf = self.term_font.render(prompt, True, self.term_color)
            self.screen.blit(prompt_surf, (term_x, term_y))
        pygame.display.flip()

    def _draw_editor(self):
        # Draw a simple text editor overlay
        pad = 24
        rect = self.monitor_rect.inflate(-pad, -pad)
        pygame.draw.rect(self.screen, (30, 30, 40), rect, border_radius=12)
        # Draw file path
        path_surf = self.term_font.render(f'Editing: {self.editor_path}', True, (200, 200, 255))
        self.screen.blit(path_surf, (rect.x + 8, rect.y + 8))
        # Draw status/info
        mode_str = 'COMMAND' if self.editor_in_command_mode else 'INSERT'
        status = f'-- {mode_str} -- {self.editor_status}'
        status_surf = self.term_font.render(status, True, (255, 180, 180))
        self.screen.blit(status_surf, (rect.x + 8, rect.y + rect.height - 32))
        # Draw content (multi-line)
        lines = self.editor_content.split('\n')
        line_height = self.term_font.get_height() + 2
        max_lines = (rect.height - 64) // line_height
        for i, line in enumerate(lines[-max_lines:]):
            line_surf = self.term_font.render(line, True, (220, 255, 220))
            self.screen.blit(line_surf, (rect.x + 8, rect.y + 40 + i * line_height))
        # Draw editor prompt
        if self.editor_in_command_mode:
            prompt = ':' + self.editor_command_buffer
            prompt_surf = self.term_font.render(prompt, True, (180, 255, 180))
            self.screen.blit(prompt_surf, (rect.x + 8, rect.y + rect.height - 56))
        else:
            prompt = '-- INSERT -- (ESC to enter command mode)'
            prompt_surf = self.term_font.render(prompt, True, (180, 255, 180))
            self.screen.blit(prompt_surf, (rect.x + 8, rect.y + rect.height - 56))

    def handle_event(self, event):
        if self.editor_mode:
            self._handle_editor_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Submit command
                prev_len = len(self.os.output)
                result = self.os.run_command(self.input_buffer)
                # Check for editor mode trigger
                if isinstance(result, dict) and 'editor' in result:
                    self.editor_mode = True
                    self.editor_path = result['editor']['path']
                    self.editor_content = result['editor']['content']
                    self.editor_original_content = self.editor_content
                    self.editor_status = ''
                    self.editor_log.append((pygame.time.get_ticks(), f"Opened editor for {self.editor_path}"))
                    # Remove the last output if it is the editor dict
                    if self.os.output and isinstance(self.os.output[-2], str) and self.os.output[-2].startswith(self.os.get_prompt().strip()):
                        self.os.output = self.os.output[:-2]
                    elif self.os.output and isinstance(self.os.output[-1], dict) and 'editor' in self.os.output[-1]:
                        self.os.output = self.os.output[:-1]
                self.input_buffer = ''
            elif event.key == pygame.K_BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
            elif event.key == pygame.K_TAB:
                pass  # Optionally implement tab completion
            elif event.key < 256:
                char = event.unicode
                if char.isprintable():
                    self.input_buffer += char
        elif event.type == pygame.USEREVENT:
            self.cursor_visible = not self.cursor_visible

    def _handle_editor_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.editor_in_command_mode:
                if event.key == pygame.K_RETURN:
                    cmd = self.editor_command_buffer.strip()
                    if cmd == 'wq':
                        self.os.files[self.editor_path] = self.editor_content
                        self.editor_log.append((pygame.time.get_ticks(), f"Saved {self.editor_path}"))
                        self.editor_mode = False
                        self.editor_path = None
                        self.editor_content = ''
                        self.editor_status = ''
                        self.editor_command_buffer = ''
                        self.editor_in_command_mode = False
                        # Remove the last output if it is the editor dict
                        if self.os.output and isinstance(self.os.output[-1], dict) and 'editor' in self.os.output[-1]:
                            self.os.output = self.os.output[:-1]
                    elif cmd == 'q!':
                        self.editor_log.append((pygame.time.get_ticks(), f"Discarded changes to {self.editor_path}"))
                        self.editor_mode = False
                        self.editor_path = None
                        self.editor_content = ''
                        self.editor_status = ''
                        self.editor_command_buffer = ''
                        self.editor_in_command_mode = False
                        # Remove the last output if it is the editor dict
                        if self.os.output and isinstance(self.os.output[-1], dict) and 'editor' in self.os.output[-1]:
                            self.os.output = self.os.output[:-1]
                    else:
                        self.editor_status = f'Unknown command: {cmd}'
                        self.editor_command_buffer = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.editor_command_buffer = self.editor_command_buffer[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.editor_in_command_mode = False
                    self.editor_command_buffer = ''
                elif event.key < 256:
                    char = event.unicode
                    if char.isprintable():
                        self.editor_command_buffer += char
            else:
                if event.key == pygame.K_ESCAPE:
                    self.editor_in_command_mode = True
                    self.editor_status = ''
                elif event.key == pygame.K_RETURN:
                    self.editor_content += '\n'
                elif event.key == pygame.K_BACKSPACE:
                    self.editor_content = self.editor_content[:-1]
                elif event.key < 256:
                    char = event.unicode
                    if char.isprintable():
                        self.editor_content += char
        elif event.type == pygame.USEREVENT:
            self.cursor_visible = not self.cursor_visible

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0 