import pygame
import random
from game.utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ITEM_GOOD, ITEM_BAD, ITEM_SPECIAL,
    SCORES, create_placeholder_surface, GREEN, RED, GOLD
)


class Item:
    """Represents a falling item (cake, bomb, etc.)"""
    
    def __init__(self, item_type, speed_multiplier=1.0):
        from game.utils import SCALE_FACTOR
        
        self.type = item_type
        base_max_size = 100 if item_type != ITEM_SPECIAL else 120
        self.max_size = int(base_max_size * SCALE_FACTOR * 1.35)  # 1.35x multiplier
        
        # Scale speed so items fall at consistent rate regardless of screen size
        base_fall_speed = random.uniform(3, 6)
        self.base_speed = base_fall_speed * SCALE_FACTOR
        self.speed = self.base_speed * speed_multiplier
        self.score_value = SCORES[item_type]
        
        # Load actual images from assets
        try:
            if item_type == ITEM_GOOD:
                # Randomly select from good items
                good_items = ['good_cake.png', 'good_cupcake.png', 'good_gift.png', 
                             'good_balloon.png', 'good_candle.png']
                selected_item = random.choice(good_items)
                self.image = pygame.image.load(f'assets/images/{selected_item}').convert_alpha()
            elif item_type == ITEM_BAD:
                # Randomly select from bad items
                bad_items = ['bad_broken_cake.png', 'bad_rotten_balloon.png', 'bad_cracked_gift.png']
                selected_item = random.choice(bad_items)
                self.image = pygame.image.load(f'assets/images/{selected_item}').convert_alpha()
            else:  # SPECIAL
                self.image = pygame.image.load('assets/images/special_gold_cake.png').convert_alpha()
            
            # Scale while preserving aspect ratio
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            aspect_ratio = original_width / original_height
            
            # Fit within max_size while preserving aspect ratio
            if original_width > original_height:
                # Wider than tall
                new_width = self.max_size
                new_height = int(self.max_size / aspect_ratio)
            else:
                # Taller than wide
                new_height = self.max_size
                new_width = int(self.max_size * aspect_ratio)
            
            self.image = pygame.transform.smoothscale(self.image, (new_width, new_height))
            self.width = new_width
            self.height = new_height
            
        except Exception as e:
            # Fallback to placeholder if image not found
            self.width = self.max_size
            self.height = self.max_size
            if item_type == ITEM_GOOD:
                self.image = create_placeholder_surface(self.width, self.height, GREEN, shape="circle")
            elif item_type == ITEM_BAD:
                self.image = create_placeholder_surface(self.width, self.height, RED, shape="circle")
                x_mark = create_placeholder_surface(self.width, self.height, (0, 0, 0, 0), shape="x")
                self.image.blit(x_mark, (0, 0))
            else:  # SPECIAL
                self.image = create_placeholder_surface(self.width, self.height, GOLD, shape="circle")
                pygame.draw.circle(self.image, (255, 255, 200), (self.width // 2, self.height // 2), self.width // 3)
        
        # Set spawn position and rect
        self.x = random.randint(self.width, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.caught = False
        
    def update(self):
        """Update item position"""
        self.y += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
    def draw(self, screen):
        """Draw the item"""
        screen.blit(self.image, self.rect)
        
    def is_off_screen(self):
        """Check if item has fallen off screen"""
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Return collision rectangle"""
        return self.rect
    
    def is_good(self):
        """Check if this is a good item"""
        return self.type == ITEM_GOOD
    
    def is_bad(self):
        """Check if this is a bad item"""
        return self.type == ITEM_BAD
    
    def is_special(self):
        """Check if this is a special item"""
        return self.type == ITEM_SPECIAL
