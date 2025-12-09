import pygame
from game.utils import SCREEN_WIDTH, SCREEN_HEIGHT, lerp, create_placeholder_surface, BLUE


class Player:
    """Represents the plate that catches items"""
    
    def __init__(self):
        # Import SCREEN_HEIGHT at runtime to get updated value
        from game.utils import SCREEN_WIDTH, SCREEN_HEIGHT
        
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100  # Position from bottom
        self.target_x = self.x
        
        # Load plate image from assets
        try:
            from game.utils import SCALE_FACTOR
            
            self.image = pygame.image.load('assets/images/plate.png').convert_alpha()
            
            # Scale while preserving aspect ratio (plate original: 1124x222)
            # Target width for plate scaled by screen resolution with 1.35x multiplier
            base_target_width = 150
            target_width = int(base_target_width * SCALE_FACTOR * 1.35)  # 1.35x multiplier
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            aspect_ratio = original_width / original_height
            
            new_width = target_width
            new_height = int(target_width / aspect_ratio) * 1.35
            
            self.image = pygame.transform.smoothscale(self.image, (new_width, new_height))
            self.width = new_width
            self.height = new_height
        except:
            # Fallback to placeholder if image not found
            self.width = 120
            self.height = 30
            self.image = create_placeholder_surface(self.width, self.height, BLUE, shape="rect")
            pygame.draw.rect(self.image, (80, 120, 200), (5, 5, self.width - 10, self.height - 10))
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update_target(self, normalized_x):
        """Update target position based on hand tracking (0.0-1.0)"""
        from game.utils import SCREEN_WIDTH
        self.target_x = normalized_x * SCREEN_WIDTH
        self.target_x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.target_x))
        
    def update(self):
        """Smooth movement towards target position"""
        self.x = lerp(self.x, self.target_x, 0.2)
        self.rect.x = int(self.x - self.width // 2)
        self.rect.y = self.y
        
    def draw(self, screen):
        """Draw the plate"""
        screen.blit(self.image, self.rect)
        
    def get_rect(self):
        """Return collision rectangle"""
        return self.rect
