import pygame
import json
import os

# Screen settings will be set dynamically based on display
SCREEN_WIDTH = 1920  # Default, will be updated at runtime
SCREEN_HEIGHT = 1080  # Default, will be updated at runtime
FPS = 30

# Scale factor for consistent sizing across different resolutions
# Based on 1920x1080 as reference resolution
SCALE_FACTOR = 1.0  # Will be updated at runtime
CUSTOM_FONT = None  # Will be set at runtime

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
BLUE = (100, 150, 255)
GOLD = (255, 215, 0)

# Game settings
GAME_DURATION = 60

# Item types
ITEM_GOOD = "GOOD"
ITEM_BAD = "BAD"
ITEM_SPECIAL = "SPECIAL"

# Item scores
SCORES = {
    ITEM_GOOD: 10,
    ITEM_BAD: -15,
    ITEM_SPECIAL: 50
}

# Spawn rates for regular items (no longer used for special)
SPAWN_RATES = {
    ITEM_GOOD: 0.7,
    ITEM_BAD: 0.3
}


def lerp(start, end, factor):
    """Linear interpolation for smooth movement"""
    return start + (end - start) * factor


def check_collision(rect1, rect2):
    """Check if two rectangles collide"""
    return rect1.colliderect(rect2)


class ScorePopup:
    """Visual feedback for score changes"""
    def __init__(self, x, y, score, color):
        self.x = x
        self.y = y
        self.score = score
        self.color = color
        self.lifetime = 60
        self.alpha = 255
        
    def update(self):
        self.y -= 2
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 60) * 255)
        
    def draw(self, screen, font):
        if self.lifetime > 0:
            text = f"{'+' if self.score > 0 else ''}{self.score}"
            surf = font.render(text, True, self.color)
            surf.set_alpha(self.alpha)
            screen.blit(surf, (self.x, self.y))
            
    def is_alive(self):
        return self.lifetime > 0


def create_placeholder_surface(width, height, color, shape="circle"):
    """Create placeholder surfaces for game objects"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    if shape == "circle":
        pygame.draw.circle(surface, color, (width // 2, height // 2), width // 2)
    elif shape == "rect":
        pygame.draw.rect(surface, color, (0, 0, width, height))
    elif shape == "x":
        pygame.draw.line(surface, color, (10, 10), (width - 10, height - 10), 5)
        pygame.draw.line(surface, color, (width - 10, 10), (10, height - 10), 5)
    return surface


# Leaderboard functions
def load_leaderboard():
    """Load leaderboard from scores.json"""
    if os.path.exists('scores.json'):
        try:
            with open('scores.json', 'r') as f:
                scores = json.load(f)
                return sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
        except:
            return []
    return []


def save_leaderboard(scores):
    """Save leaderboard to scores.json"""
    try:
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
        with open('scores.json', 'w') as f:
            json.dump(sorted_scores, f, indent=2)
    except Exception as e:
        print(f"Error saving leaderboard: {e}")


def qualifies_for_leaderboard(score):
    """Check if score qualifies for top 5"""
    leaderboard = load_leaderboard()
    if len(leaderboard) < 5:
        return True
    return score > leaderboard[-1]['score']


# Settings management functions
def load_settings():
    """Load settings from settings.json"""
    if os.path.exists('settings.json'):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_settings(settings):
    """Save settings to settings.json"""
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")


def get_last_player_name():
    """Get the last saved player name"""
    settings = load_settings()
    return settings.get('last_name', '')


def save_player_name(name):
    """Save player name to settings"""
    settings = load_settings()
    settings['last_name'] = name
    save_settings(settings)
