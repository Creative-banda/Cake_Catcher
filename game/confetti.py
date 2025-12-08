import pygame
import random
import math


class ConfettiParticle:
    """Individual confetti particle with physics"""
    
    def __init__(self, x, y, particle_type="confetti"):
        self.x = x
        self.y = y
        self.type = particle_type
        
        if particle_type == "sparkle":
            # Small sparkle stars
            self.size = random.randint(3, 6)
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 5)
            self.vx = math.cos(math.radians(angle)) * speed
            self.vy = math.sin(math.radians(angle)) * speed - 2  # Slight upward bias
            self.gravity = 0.15
            self.lifetime = 40  # 1.3 seconds
            self.color = (255, 255, 200)  # Golden sparkle
            self.rotation = 0
            self.rotation_speed = 0
        else:
            # Confetti ribbons
            self.size = random.randint(6, 10)
            angle = random.uniform(-45, -135)  # Upward burst
            speed = random.uniform(4, 8)
            self.vx = math.cos(math.radians(angle)) * speed
            self.vy = math.sin(math.radians(angle)) * speed
            self.gravity = 0.25
            self.rotation = random.uniform(0, 360)
            self.rotation_speed = random.uniform(-12, 12)
            self.lifetime = 90  # 3 seconds
            
            # Vibrant but not overwhelming colors
            colors = [
                (255, 100, 180),  # Pink
                (100, 200, 255),  # Blue
                (255, 220, 100),  # Yellow
                (255, 150, 100),  # Orange
            ]
            self.color = random.choice(colors)
        
        self.alpha = 255
        
    def update(self):
        """Update particle physics"""
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
        self.lifetime -= 1
        max_lifetime = 40 if self.type == "sparkle" else 90
        self.alpha = int((self.lifetime / max_lifetime) * 255)
        
    def draw(self, screen):
        """Draw the confetti particle"""
        if self.lifetime > 0:
            if self.type == "sparkle":
                # Draw as a glowing star
                surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                # Draw cross for star effect
                center = self.size
                pygame.draw.line(surf, self.color, (center, 0), (center, self.size * 2), 2)
                pygame.draw.line(surf, self.color, (0, center), (self.size * 2, center), 2)
                surf.set_alpha(self.alpha)
                screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))
            else:
                # Draw rotated rectangle for confetti
                surf = pygame.Surface((self.size, self.size * 2), pygame.SRCALPHA)
                pygame.draw.rect(surf, self.color, (0, 0, self.size, self.size * 2))
                rotated = pygame.transform.rotate(surf, self.rotation)
                rotated.set_alpha(self.alpha)
                rect = rotated.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(rotated, rect)
    
    def is_alive(self):
        """Check if particle should still exist"""
        return self.lifetime > 0


class ConfettiSystem:
    """Manages all confetti particles and effects"""
    
    def __init__(self):
        self.particles = []
        self.flash_timer = 0
        self.flash_x = 0
        self.flash_y = 0
        
    def celebration_burst(self, x, y):
        """Create a balanced celebration effect at catch position"""
        # Add golden flash
        self.flash_timer = 15
        self.flash_x = x
        self.flash_y = y
        
        # Add sparkles (15 small stars)
        for _ in range(15):
            self.particles.append(ConfettiParticle(x, y, "sparkle"))
        
        # Add confetti ribbons (25 pieces)
        for _ in range(25):
            self.particles.append(ConfettiParticle(x, y, "confetti"))
        
    def update(self):
        """Update all particles and effects"""
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
    def draw(self, screen):
        """Draw all particles and effects"""
        # Draw golden flash
        if self.flash_timer > 0:
            alpha = int((self.flash_timer / 15) * 150)
            radius = 50 + (15 - self.flash_timer) * 3
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 215, 0), (radius, radius), radius)
            surf.set_alpha(alpha)
            screen.blit(surf, (int(self.flash_x) - radius, int(self.flash_y) - radius))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
    
    def is_active(self):
        return len(self.particles) > 0 or self.flash_timer > 0
