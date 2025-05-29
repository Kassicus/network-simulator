"""
Module for the Server Room scene.
Handles UI and logic for managing cables, switches, and patch panels.
"""

import pygame
import logging
from rack import Rack, RackMountable
from switch import Switch

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class ServerRoomScene:
    def __init__(self, screen, scene_manager=None):
        self.screen = screen
        self.scene_manager = scene_manager  # For scene switching
        self.bg_color = (30, 32, 38)
        self.title_color = (220, 220, 220)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        width, height = self.screen.get_size()
        # Place two racks side by side
        rack_width = 120
        rack_height = 400
        spacing = 80
        x1 = width // 2 - rack_width - spacing // 2
        x2 = width // 2 + spacing // 2
        y = height // 2 - rack_height // 2
        self.racks = [
            Rack(x1, y, rack_width, rack_height),
            Rack(x2, y, rack_width, rack_height)
        ]
        self.title = 'Server Room'
        self.selected_port = None  # (switch, port_index)
        self.hovered_port = None   # (switch, port_index)
        self.menu_open = False
        self.menu_pos = (0, 0)
        self.menu_rack = None
        self.menu_unit = None
        logging.info("ServerRoomScene initialized with 2 racks.")

    def draw(self):
        self.screen.fill(self.bg_color)
        # Draw title
        title_surf = self.title_font.render(self.title, True, self.title_color)
        self.screen.blit(title_surf, (24, 16))
        # Draw racks and collect all switches
        switches = []
        for rack in self.racks:
            rack.draw(self.screen)
            for device in rack.slots:
                if isinstance(device, Switch):
                    switches.append(device)
        # Draw cables (connections between ports)
        for switch in switches:
            for port_index, conn in enumerate(switch.get_connections()):
                if conn:
                    other_switch, other_port_index = conn
                    # Only draw if this is the 'lower' switch to avoid double-drawing
                    if id(switch) < id(other_switch):
                        start = switch.get_port_center(port_index)
                        end = other_switch.get_port_center(other_port_index)
                        self._draw_cable(start, end)
        # Draw port highlight for hovered/selected
        if self.hovered_port:
            switch, port_index = self.hovered_port
            switch.draw(self.screen, highlight_port=port_index)
        if self.selected_port:
            switch, port_index = self.selected_port
            switch.draw(self.screen, highlight_port=port_index)
        # Draw context menu if open
        if self.menu_open:
            self._draw_menu()
        pygame.display.flip()

    def _draw_cable(self, start, end):
        # Draw yellow cable with squares at each end
        color = (255, 255, 0)
        square_size = 16
        pygame.draw.line(self.screen, color, start, end, 4)
        for pt in [start, end]:
            rect = pygame.Rect(pt[0] - square_size//2, pt[1] - square_size//2, square_size, square_size)
            pygame.draw.rect(self.screen, color, rect)

    def _draw_menu(self):
        # Draws a context menu at self.menu_pos with all RackMountable subclasses
        font = pygame.font.SysFont('Arial', 24)
        items = RackMountable.registry
        menu_width = 220
        menu_item_height = 36
        menu_height = len(items) * menu_item_height
        x, y = self.menu_pos
        menu_rect = pygame.Rect(x, y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (40, 44, 52), menu_rect, border_radius=8)
        for idx, cls in enumerate(items):
            item_rect = pygame.Rect(x, y + idx * menu_item_height, menu_width, menu_item_height)
            pygame.draw.rect(self.screen, (60, 64, 72), item_rect, border_radius=4)
            label = font.render(cls.get_display_name(), True, (220, 220, 220))
            self.screen.blit(label, (x + 12, y + idx * menu_item_height + 6))
        self.menu_rect = menu_rect
        self.menu_item_height = menu_item_height
        self.menu_items = items

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                if self.scene_manager:
                    logging.info("Switching to desk scene.")
                    self.scene_manager.set_scene('desk')
            elif event.key == pygame.K_s:
                # Already in server room, do nothing
                pass
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_port = None
            for rack in self.racks:
                for device in rack.slots:
                    if isinstance(device, Switch):
                        for i, port_rect in enumerate(device.ports):
                            if port_rect.collidepoint(event.pos):
                                self.hovered_port = (device, i)
            for rack in self.racks:
                rack.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_open:
                # Check if click is inside menu
                if self.menu_rect.collidepoint(event.pos):
                    idx = (event.pos[1] - self.menu_rect.y) // self.menu_item_height
                    if 0 <= idx < len(self.menu_items):
                        cls = self.menu_items[idx]
                        # Add device to rack
                        if self.menu_rack and self.menu_unit is not None:
                            rack = self.menu_rack
                            unit = self.menu_unit
                            rack.slots[unit] = cls(rack.x, rack.y, rack.width, unit, rack.unit_height)
                            logging.info(f"Added {cls.get_display_name()} to rack at unit {unit+1}.")
                        self.menu_open = False
                        self.menu_rack = None
                        self.menu_unit = None
                        return
                # Click outside menu closes it
                self.menu_open = False
                self.menu_rack = None
                self.menu_unit = None
                return
            # Check if a port was clicked
            for rack in self.racks:
                for device in rack.slots:
                    if isinstance(device, Switch):
                        for i, port_rect in enumerate(device.ports):
                            if port_rect.collidepoint(event.pos):
                                if self.selected_port is None:
                                    self.selected_port = (device, i)
                                    logging.info(f"Selected port {i+1} on switch at rack unit {device.unit_index+1}.")
                                else:
                                    # Connect selected port to this port (if not same port)
                                    sel_device, sel_index = self.selected_port
                                    if (sel_device, sel_index) != (device, i):
                                        sel_device.set_connection(sel_index, device, i)
                                        device.set_connection(i, sel_device, sel_index)
                                        logging.info(f"Connected port {sel_index+1} on one switch to port {i+1} on another switch.")
                                    self.selected_port = None
                                return
            # Check for empty rack unit click to open menu
            for rack in self.racks:
                if rack.rect.collidepoint(event.pos):
                    rel_y = event.pos[1] - rack.y
                    unit = rel_y // rack.unit_height
                    if 0 <= unit < rack.units and rack.slots[unit] is None:
                        self.menu_open = True
                        self.menu_pos = event.pos
                        self.menu_rack = rack
                        self.menu_unit = unit
                        return
            for rack in self.racks:
                rack.handle_mouse_click(event.pos)
        return None

    def update(self, dt):
        pass  # For future use 