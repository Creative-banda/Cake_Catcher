import pygame
import random
import math


class MenuParticle:
    """Single particle for menu animations"""
    def __init__(self, x, y, particle_type="sparkle"):
        self.x = x
        self.y = y
        self.type = particle_type
        self.lifetime = 0
        self.max_lifetime = random.uniform(2.0, 3.0)  # Longer lifetime
        self.size = random.randint(6, 10) if particle_type == "sparkle" else random.randint(12, 20)  # Smaller sparkles
        self.velocity_y = random.uniform(1.0, 2.0) if particle_type == "falling" else 0
        self.velocity_x = random.uniform(-0.5, 0.5) if particle_type == "falling" else 0
        self.alpha = 0
        self.color = self._get_color()
        self.bob_offset = random.uniform(0, math.pi * 2)  # Random phase for bobbing
        
    def _get_color(self):
        """Get particle color based on type"""
        if self.type == "sparkle":
            colors = [
                (255, 50, 220),   # Hot magenta/pink
                (50, 255, 255),   # Bright cyan
                (255, 255, 50),   # Neon yellow
                (50, 255, 50)     # Bright green
            ]
            return random.choice(colors)
        else:  # falling confetti
            colors = [
                (255, 0, 200),    # Magenta
                (0, 255, 255),    # Cyan
                (255, 200, 0),    # Gold
                (255, 100, 0)     # Orange
            ]
            return random.choice(colors)
    
    def update(self, dt):
        """Update particle state"""
        self.lifetime += dt
        
        # Fade in/out
        progress = self.lifetime / self.max_lifetime
        if progress < 0.2:
            self.alpha = int((progress / 0.2) * 255)
        elif progress > 0.8:
            self.alpha = int((1 - (progress - 0.8) / 0.2) * 255)
        else:
            self.alpha = 255
        
        # Movement for falling particles
        if self.type == "falling":
            self.y += self.velocity_y
            self.x += self.velocity_x
        
        return self.lifetime < self.max_lifetime
    
    def draw(self, screen):
        """Draw particle with beautiful gradient effect"""
        if self.alpha <= 0:
            return
        
        if self.type == "sparkle":
            # Draw sparkle as a star with gradient
            self._draw_star_sparkle(screen)
        else:
            # Draw confetti as gradient circle
            self._draw_gradient_confetti(screen)
    
    def _draw_star_sparkle(self, screen):
        """Draw a star-shaped sparkle with glow"""
        # Create surface for the star
        size = self.size * 3
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Draw soft outer glow
        for i in range(3, 0, -1):
            radius = self.size * i * 0.5
            alpha = int(self.alpha * 0.15 * (4 - i))
            color = (*self.color, alpha)
            pygame.draw.circle(surf, color, (center, center), int(radius))
        
        # Draw star shape (4 points)
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            if i % 2 == 0:
                r = self.size * 0.8
            else:
                r = self.size * 0.3
            x = center + int(r * math.cos(angle))
            y = center + int(r * math.sin(angle))
            points.append((x, y))
        
        # Draw filled star with alpha
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.polygon(surf, color_with_alpha, points)
        
        # Add bright center dot
        center_color = (255, 255, 255, self.alpha)
        pygame.draw.circle(surf, center_color, (center, center), max(2, self.size // 4))
        
        screen.blit(surf, (self.x - center, self.y - center))
    
    def _draw_gradient_confetti(self, screen):
        """Draw confetti with radial gradient"""
        size = self.size * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Create radial gradient effect
        for i in range(self.size, 0, -1):
            # Calculate gradient alpha
            ratio = i / self.size
            alpha = int(self.alpha * ratio)
            
            # Lighten color toward center
            r = min(255, int(self.color[0] * (0.7 + 0.3 * (1 - ratio))))
            g = min(255, int(self.color[1] * (0.7 + 0.3 * (1 - ratio))))
            b = min(255, int(self.color[2] * (0.7 + 0.3 * (1 - ratio))))
            
            color = (r, g, b, alpha)
            pygame.draw.circle(surf, color, (center, center), i)
        
        screen.blit(surf, (self.x - center, self.y - center))


class MenuAnimations:
    """Manages all menu animations and effects"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Particle pools
        self.sparkles = []
        self.falling_items = []
        self.max_sparkles = 8   # Reduced from 25
        self.max_falling = 12   # Keep confetti count
        
        # Timing
        self.sparkle_spawn_timer = 0
        self.sparkle_spawn_interval = 0.5  # Slower (was 0.2)
        self.falling_spawn_timer = 0
        self.falling_spawn_interval = 1.5  # Keep same
        
        # Pulse animation for "Press SPACE"
        self.pulse_time = 0
        
        # Balloon bobbing
        self.bob_time = 0
    
    def update(self, dt):
        """Update all animations"""
        # Update timers
        self.sparkle_spawn_timer += dt
        self.falling_spawn_timer += dt
        self.pulse_time += dt
        self.bob_time += dt
        
        # Spawn sparkles
        if self.sparkle_spawn_timer >= self.sparkle_spawn_interval and len(self.sparkles) < self.max_sparkles:
            self.spawn_sparkle()
            self.sparkle_spawn_timer = 0
        
        # Spawn falling items
        if self.falling_spawn_timer >= self.falling_spawn_interval and len(self.falling_items) < self.max_falling:
            self.spawn_falling_item()
            self.falling_spawn_timer = 0
        
        # Update particles
        self.sparkles = [p for p in self.sparkles if p.update(dt)]
        self.falling_items = [p for p in self.falling_items if p.update(dt) and p.y < self.screen_height + 50]
    
    def spawn_sparkle(self):
        """Spawn a sparkle particle on the sides, avoiding the title area"""
        # Spawn on left or right side only, not near center title
        if random.random() < 0.5:
            # Left side
            x = random.randint(50, self.screen_width // 3)
        else:
            # Right side
            x = random.randint(2 * self.screen_width // 3, self.screen_width - 50)
        
        # Vertical position - anywhere on screen
        y = random.randint(100, self.screen_height - 100)
        
        self.sparkles.append(MenuParticle(x, y, "sparkle"))
    
    def spawn_falling_item(self):
        """Spawn a falling confetti/party item"""
        x = random.randint(0, self.screen_width)
        y = -20
        self.falling_items.append(MenuParticle(x, y, "falling"))
    
    def get_pulse_scale(self):
        """Get pulse scale for button animation (1.0 to 1.1)"""
        # Smooth pulse using cosine wave for breathing effect
        cycle_duration = 1.5
        progress = (self.pulse_time % cycle_duration) / cycle_duration
        # Use cosine for smooth in-out easing
        scale = 1.0 + 0.05 * (1 - math.cos(progress * math.pi * 2))
        return scale
    
    def get_bob_offset(self, index=0):
        """Get vertical bobbing offset for floating elements"""
        # Each element has slightly different phase for variety
        phase = self.bob_time + (index * 0.5)
        return math.sin(phase) * 15  # 15 pixel amplitude
    
    def draw(self, screen):
        """Draw all menu animations"""
        # Draw falling items first (background layer)
        for item in self.falling_items:
            item.draw(screen)
        
        # Draw sparkles on top
        for sparkle in self.sparkles:
            sparkle.draw(screen)
    
    def reset(self):
        """Reset all animations"""
        self.sparkles.clear()
        self.falling_items.clear()
        self.pulse_time = 0
        self.bob_time = 0
