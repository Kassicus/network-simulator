"""
Module for the Server Room scene.
Handles UI and logic for managing cables, switches, and patch panels.
"""

import pygame
import logging
from rack import Rack, RackMountable
from switch import Switch
from patch_panel import PatchPanel8, PatchPanel16

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class ServerRoomScene:
    def __init__(self, screen, scene_manager=None):
        self.screen = screen
        self.scene_manager = scene_manager  # For scene switching
        self.bg_color = (30, 32, 38)
        self.title_color = (220, 220, 220)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        width, height = self.screen.get_size()
        # Place two racks side by side with new width and 12U
        rack_width = 240
        rack_height = 480
        spacing = 120
        x1 = width // 2 - rack_width - spacing // 2
        x2 = width // 2 + spacing // 2
        y = height // 2 - rack_height // 2
        self.racks = [
            Rack(x1, y, rack_width, rack_height, 12),
            Rack(x2, y, rack_width, rack_height, 12)
        ]
        self.title = 'Server Room'
        self.selected_port = None  # (device, port_index)
        self.hovered_port = None   # (device, port_index)
        self.menu_open = False
        self.menu_pos = (0, 0)
        self.menu_rack = None
        self.menu_unit = None
        self.cable_menu_open = False
        self.cable_menu_pos = (0, 0)
        self.cable_menu_cable = None  # (device1, port1, device2, port2)
        self.cable_hover = None  # (device1, port1, device2, port2)
        logging.info("ServerRoomScene initialized with 2 racks.")

    def draw(self):
        self.screen.fill(self.bg_color)
        # Draw title
        title_surf = self.title_font.render(self.title, True, self.title_color)
        self.screen.blit(title_surf, (24, 16))
        # Draw racks and collect all rack-mountable devices with ports
        devices = []
        cables = []
        for rack in self.racks:
            rack.draw(self.screen)
            for device in rack.slots:
                if isinstance(device, RackMountable) and hasattr(device, 'get_connections') and hasattr(device, 'get_port_center'):
                    devices.append(device)
        # Draw cables (connections between ports)
        for device in devices:
            for port_index, conn in enumerate(device.get_connections()):
                if conn:
                    other_device, other_port_index = conn
                    # Only draw if this is the 'lower' device to avoid double-drawing
                    if id(device) < id(other_device):
                        start = device.get_port_center(port_index)
                        end = other_device.get_port_center(other_port_index)
                        cable = (device, port_index, other_device, other_port_index)
                        highlight = (self.cable_hover == cable or self.cable_hover == (other_device, other_port_index, device, port_index))
                        self._draw_cable(start, end, highlight=highlight)
                        cables.append(cable)
        # Draw port highlight for hovered/selected
        if self.hovered_port:
            device, port_index = self.hovered_port
            device.draw(self.screen, highlight_port=port_index)
        if self.selected_port:
            device, port_index = self.selected_port
            device.draw(self.screen, highlight_port=port_index)
        # Draw context menu if open
        if self.menu_open:
            self._draw_menu()
        if self.cable_menu_open:
            self._draw_cable_menu()
        pygame.display.flip()

    def _draw_cable(self, start, end, highlight=False):
        # Draw yellow cable with squares at each end, highlight if needed
        color = (255, 255, 0) if not highlight else (255, 220, 40)
        square_size = 16
        width = 6 if highlight else 4
        pygame.draw.line(self.screen, color, start, end, width)
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

    def _draw_cable_menu(self):
        font = pygame.font.SysFont('Arial', 24)
        menu_width = 180
        menu_item_height = 36
        x, y = self.cable_menu_pos
        menu_rect = pygame.Rect(x, y, menu_width, menu_item_height)
        pygame.draw.rect(self.screen, (40, 44, 52), menu_rect, border_radius=8)
        item_rect = pygame.Rect(x, y, menu_width, menu_item_height)
        pygame.draw.rect(self.screen, (200, 60, 60), item_rect, border_radius=4)
        label = font.render("Remove Cable", True, (255, 255, 255))
        self.screen.blit(label, (x + 16, y + 6))
        self.cable_menu_rect = menu_rect

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
            self.cable_hover = None
            # Check for cable hover
            devices = []
            for rack in self.racks:
                for device in rack.slots:
                    if isinstance(device, RackMountable) and hasattr(device, 'get_connections') and hasattr(device, 'get_port_center'):
                        devices.append(device)
            for device in devices:
                for port_index, conn in enumerate(device.get_connections()):
                    if conn:
                        other_device, other_port_index = conn
                        if id(device) < id(other_device):
                            start = device.get_port_center(port_index)
                            end = other_device.get_port_center(other_port_index)
                            # Check if mouse is near the cable (line segment)
                            if self._point_near_line(event.pos, start, end, 12):
                                self.cable_hover = (device, port_index, other_device, other_port_index)
            for rack in self.racks:
                for device in rack.slots:
                    if isinstance(device, RackMountable) and hasattr(device, 'ports'):
                        for i, port_rect in enumerate(device.ports):
                            if port_rect.collidepoint(event.pos):
                                self.hovered_port = (device, i)
            for rack in self.racks:
                rack.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cable_menu_open:
                if self.cable_menu_rect.collidepoint(event.pos):
                    # Remove cable
                    d1, p1, d2, p2 = self.cable_menu_cable
                    d1.clear_connection(p1)
                    d2.clear_connection(p2)
                    logging.info(f"Cable removed between port {p1+1} and port {p2+1}.")
                    self.cable_menu_open = False
                    self.cable_menu_cable = None
                    return
                # Click outside menu closes it
                self.cable_menu_open = False
                self.cable_menu_cable = None
                return
            # Cable menu takes priority: check if a cable was clicked
            if self.cable_hover:
                self.cable_menu_open = True
                self.cable_menu_pos = event.pos
                self.cable_menu_cable = self.cable_hover
                # Do not open device menu if cable is hovered
                return
            if self.menu_open:
                # Check if click is inside menu
                if self.menu_rect.collidepoint(event.pos):
                    idx = (event.pos[1] - self.menu_rect.y) // self.menu_item_height
                    if 0 <= idx < len(self.menu_items):
                        cls = self.menu_items[idx]
                        # Only add device if enough space
                        if self.menu_rack and self.menu_unit is not None:
                            rack = self.menu_rack
                            unit = self.menu_unit
                            if rack.can_place_device(cls, unit):
                                rack.add_device(cls, unit)
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
            # Only open device menu if no cable is hovered
            if not self.cable_hover:
                # Check for empty rack unit click to open menu (only if enough space for at least one device)
                for rack in self.racks:
                    if rack.rect.collidepoint(event.pos):
                        rel_y = event.pos[1] - rack.y
                        unit = rel_y // rack.unit_height
                        if 0 <= unit < rack.units and rack.slots[unit] is None:
                            # Only open menu if at least one device can fit
                            for cls in RackMountable.registry:
                                if rack.can_place_device(cls, unit):
                                    self.menu_open = True
                                    self.menu_pos = event.pos
                                    self.menu_rack = rack
                                    self.menu_unit = unit
                                    return
            # Check if a port was clicked
            for rack in self.racks:
                for device in rack.slots:
                    if isinstance(device, RackMountable) and hasattr(device, 'ports'):
                        for i, port_rect in enumerate(device.ports):
                            if port_rect.collidepoint(event.pos):
                                if self.selected_port is None:
                                    self.selected_port = (device, i)
                                    logging.info(f"Selected port {i+1} on device at rack unit {device.unit_index+1}.")
                                else:
                                    # Connect selected port to this port (if not same port)
                                    sel_device, sel_index = self.selected_port
                                    # Only connect if both ports are not already connected
                                    if (sel_device, sel_index) != (device, i):
                                        if sel_device.get_connections()[sel_index] is None and device.get_connections()[i] is None:
                                            sel_device.set_connection(sel_index, device, i)
                                            device.set_connection(i, sel_device, sel_index)
                                            logging.info(f"Connected port {sel_index+1} on one device to port {i+1} on another device.")
                                        else:
                                            logging.warning(f"Cannot connect: one or both ports already connected.")
                                    self.selected_port = None
                                return
        return None

    def update(self, dt):
        pass  # For future use 

    def _point_near_line(self, point, start, end, threshold):
        # Utility: check if point is within threshold pixels of the line segment start-end
        import math
        x0, y0 = point
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:
            return math.hypot(x0 - x1, y0 - y1) <= threshold
        t = max(0, min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / float(dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(x0 - proj_x, y0 - proj_y) <= threshold 