import pygame
import os
import re

#===============Constants===================
GAME_WIDTH = 900
GAME_HEIGHT = 600

OUTSIDE_SPAWN = (0, 260)
HOME_SPAWN    = (100, 300)

# Colors 
WHITE = (255,255,255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0,0,0)

# Game State
CHAPTER1 = "chapter1"
## Profile
PROFILE = "profile"
## Chapter I
OUTSIDE = "outside"
HOME = "home"
WISEMAN = "wiseman"
GATE = "gate"
## Chapter II
CHAPTER2 = "chapter2"
PORTAL1 = "portal1"
PORTAL2 = "portal2"
PORTAL3 = "portal3"

#================ Player =========================
class Player:
    def __init__(self, x, y, width, height, img_path, speed):
        self.img_path = img_path

        # Load idle sprites for all directions at a fixed render size.
        self.img_up = pygame.transform.scale(
            pygame.image.load(img_path + "north.png").convert_alpha(), (width, height)
        )
        self.img_down = pygame.transform.scale(
            pygame.image.load(img_path + "south.png").convert_alpha(), (width, height)
        )
        self.img_left = pygame.transform.scale(
            pygame.image.load(img_path + "west.png").convert_alpha(), (width, height)
        )
        self.img_right = pygame.transform.scale(
            pygame.image.load(img_path + "east.png").convert_alpha(), (width, height)
        )

        # Player Attributes
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed # pixel/second
        self.img = self.img_down
        self.last_dir = "down"
        self.anim_index = 0.0
        self.anim_fps = 10.0

        self.walk_frames = {
            "up": self._build_direction_sequence("north", self.img_up, width, height),
            "down": self._build_direction_sequence("south", self.img_down, width, height),
            "left": self._build_direction_sequence("left", self.img_left, width, height),
            "right": self._build_direction_sequence("right", self.img_right, width, height),
        }

    def _build_direction_sequence(self, token, idle_img, width, height):
        anim_dir = os.path.join(self.img_path, "animation")
        frames = [idle_img]
        if not os.path.isdir(anim_dir):
            return frames

        pattern = re.compile(rf"^walk_{re.escape(token)}(\d+)\.png$", re.IGNORECASE)
        matches = []
        for fn in os.listdir(anim_dir):
            m = pattern.match(fn)
            if m:
                matches.append((int(m.group(1)), fn))

        matches.sort(key=lambda item: item[0])
        for _, fn in matches:
            p = os.path.join(anim_dir, fn)
            frame = pygame.transform.scale(pygame.image.load(p).convert_alpha(), (width, height))
            frames.append(frame)
        return frames

    def move(self, dt, game_width, game_height):
        keys = pygame.key.get_pressed()
        dx = 0.0
        dy = 0.0
        move_dir = None

        # Move Up
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_k]) and self.rect.y >= 0:
            dy -= self.speed * dt
            move_dir = "up"

        # Move Down
        if (keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_j]) and self.rect.y <= game_height - self.rect.height:
            dy += self.speed * dt
            move_dir = "down"

        # Move Left
        if (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_h]) and self.rect.x >= 0:
            dx -= self.speed * dt
            move_dir = "left"

        # Move Right
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_l]) and self.rect.x <= game_width - self.rect.width:
            dx += self.speed * dt
            move_dir = "right"

        if dx == 0 and dy == 0:
            return

        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(game_width - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(game_height - self.rect.height, self.rect.y))

        if move_dir is not None:
            self.last_dir = move_dir
        frames = self.walk_frames.get(self.last_dir, [self.img_down])
        self.anim_index = (self.anim_index + self.anim_fps * dt) % len(frames)
        self.img = frames[int(self.anim_index)]

    def draw(self, surface):
        surface.blit(self.img, self.rect)

class Structure:
    def __init__(self, x, y, width, height, img_path, bg_img_path):
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (width, height))

        bg_img = pygame.image.load(bg_img_path)
        bg_img = pygame.transform.scale(bg_img, (GAME_WIDTH, GAME_HEIGHT))

        self.img = img
        self.bg = bg_img
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        surface.blit(self.img, self.rect)
