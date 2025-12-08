import pygame
import math


class ComboEffect:
    """Animated combo visual effect"""
    
    def __init__(self, x, y, combo_count, font, scale_factor):
        self.x = x
        self.y = y
        self.combo = combo_count
        self.font = font
        self.scale_factor = scale_factor
        
        # Animation properties
        self.lifetime = 0
        self.max_lifetime = 1.2  # 1.2 seconds
        self.start_y = y
        self.move_distance = 80 * scale_factor
        
        # Color based on combo level
        if combo_count >= 10:
            self.color = (255, 23, 68)  # #FF1744 red neon
            self.stroke_color = (255, 255, 255)  # White
            self.stroke_width = int(5 * scale_factor)
            self.trigger_special = True
        elif combo_count >= 5:
            self.color = (255, 235, 59)  # #FFEB3B yellow
            self.stroke_color = (75, 0, 130)  # Purple
            self.stroke_width = int(4 * scale_factor)
            self.trigger_special = False
        else:  # 2-4
            self.color = (0, 230, 118)  # #00E676 green
            self.stroke_color = (0, 0, 0)  # Black
            self.stroke_width = int(3 * scale_factor)
            self.trigger_special = False
        
        self.text = f"{combo_count}x Combo!"
        self.alpha = 255
        self.scale = 1.0
        
    def update(self, dt):
        """Update animation - dt in seconds"""
        self.lifetime += dt
        
        if self.lifetime >= self.max_lifetime:
            return False  # Effect finished
        
        # Calculate animation progress (0.0 to 1.0)
        progress = self.lifetime / self.max_lifetime
        
        # Upward movement (eased)
        ease_out = 1 - (1 - progress) ** 2
        self.y = self.start_y - (self.move_distance * ease_out)
        
        # Scale animation: grow to 1.4 then back to 1.0
        if progress < 0.3:
            # First 30%: scale up
            self.scale = 1.0 + (progress / 0.3) * 0.4
        elif progress < 0.6:
            # Next 30%: scale back down
            t = (progress - 0.3) / 0.3
            self.scale = 1.4 - t * 0.4
        else:
            self.scale = 1.0
        
        # Fade out in last 40%
        if progress > 0.6:
            fade_progress = (progress - 0.6) / 0.4
            self.alpha = int(255 * (1 - fade_progress))
        else:
            self.alpha = 255
        
        return True  # Effect still active
    
    def draw(self, screen):
        """Draw the combo effect"""
        if self.alpha <= 0:
            return
        
        # Create scaled font
        scaled_size = int(self.font.get_height() * self.scale)
        try:
            scaled_font = pygame.font.Font(self.font, scaled_size)
        except:
            # Fallback if font scaling fails
            scaled_font = self.font
        
        # Get text surface
        text_surf = scaled_font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        
        # Draw stroke/outline
        if self.stroke_width > 0:
            for dx in range(-self.stroke_width, self.stroke_width + 1):
                for dy in range(-self.stroke_width, self.stroke_width + 1):
                    if dx*dx + dy*dy <= self.stroke_width*self.stroke_width:
                        outline_surf = scaled_font.render(self.text, True, self.stroke_color)
                        outline_surf.set_alpha(self.alpha)
                        outline_rect = outline_surf.get_rect(center=(int(self.x) + dx, int(self.y) + dy))
                        screen.blit(outline_surf, outline_rect)
        
        # Draw main text with alpha
        text_surf.set_alpha(self.alpha)
        screen.blit(text_surf, text_rect)
    
    def is_finished(self):
        """Check if animation is complete"""
        return self.lifetime >= self.max_lifetime
    
    def should_trigger_special(self):
        """Check if this combo level triggers special effects"""
        return self.trigger_special and self.lifetime < 0.1  # Only trigger once at start
