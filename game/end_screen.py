import pygame
import random
import math
from game.utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR,
    load_leaderboard, WHITE, GOLD, GREEN
)
from game import utils
from game.confetti import ConfettiSystem


class FloatingBalloon:
    """Decorative floating balloon for background"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y
        self.float_offset = random.uniform(0, math.pi * 2)
        self.float_speed = random.uniform(0.5, 1.0)
        self.float_amplitude = random.uniform(20, 40)
        self.color = random.choice([
            (255, 100, 180),  # Pink
            (100, 200, 255),  # Blue  
            (255, 220, 100),  # Yellow
            (150, 255, 150),  # Green
        ])
        self.size = random.randint(30, 50)
        
    def update(self, dt):
        """Update balloon floating animation"""
        self.float_offset += self.float_speed * dt
        self.y = self.start_y + math.sin(self.float_offset) * self.float_amplitude
        
    def draw(self, screen):
        """Draw the balloon"""
        # Balloon body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Balloon highlight
        highlight_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, highlight_color, 
                         (int(self.x - self.size//3), int(self.y - self.size//3)), 
                         self.size//4)
        # String
        pygame.draw.line(screen, (200, 200, 200), 
                        (int(self.x), int(self.y + self.size)), 
                        (int(self.x), int(self.y + self.size + 60)), 3)


class SparkleTrail:
    """Sparkle trail animation around text"""
    
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.sparkles = []
        self.spawn_timer = 0
        
    def update(self, dt):
        """Update sparkle trail"""
        self.spawn_timer += dt
        
        # Spawn new sparkles
        if self.spawn_timer > 0.1:  # Every 0.1 seconds
            angle = random.uniform(0, math.pi * 2)
            x = self.center_x + math.cos(angle) * self.radius
            y = self.center_y + math.sin(angle) * self.radius
            self.sparkles.append({
                'x': x, 'y': y, 'life': 1.0, 'size': random.randint(3, 6)
            })
            self.spawn_timer = 0
            
        # Update existing sparkles
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= dt * 2  # 0.5 second lifetime
            if sparkle['life'] <= 0:
                self.sparkles.remove(sparkle)
                
    def draw(self, screen):
        """Draw sparkle trail"""
        for sparkle in self.sparkles:
            alpha = int(sparkle['life'] * 255)
            size = int(sparkle['size'] * sparkle['life'])
            if size > 0:
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color = (255, 255, 200, alpha)
                # Draw star shape
                center = size
                pygame.draw.line(surf, color, (center, 0), (center, size * 2), 2)
                pygame.draw.line(surf, color, (0, center), (size * 2, center), 2)
                screen.blit(surf, (int(sparkle['x']) - size, int(sparkle['y']) - size))


class EndScreen:
    """Polished animated end-game results screen"""
    
    def __init__(self, score, player_name, sound_manager=None):
        self.score = score
        self.player_name = player_name
        self.sound_manager = sound_manager
        
        # Animation state - add transition phase for smoother entry
        self.phase = "transition"  # transition -> fade_in -> score_reveal -> leaderboard_check -> buttons
        self.timer = 0
        self.overlay_alpha = 0
        self.score_scale = 0
        self.score_revealed = False
        self.leaderboard_checked = False
        self.buttons_shown = False
        
        # Transition effect - slide up from bottom
        self.transition_y_offset = SCREEN_HEIGHT  # Start off-screen
        self.target_y_offset = 0
        
        # Visual effects
        self.confetti_system = ConfettiSystem()
        self.balloons = []
        self.sparkle_trail = None
        self.glow_intensity = 0
        
        # Create floating balloons
        for _ in range(6):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(200, SCREEN_HEIGHT - 200)
            self.balloons.append(FloatingBalloon(x, y))
            
        # Leaderboard status
        self.leaderboard_position = None
        self.leaderboard_message = ""
        self.is_new_champion = False
        self.made_leaderboard = False
        
        # Button animations
        self.button_scales = [0, 0, 0]  # Play Again, Change Name, Main Menu
        self.button_hover = [False, False, False]
        
        # Load fonts with proper custom font handling
        try:
            # Use the custom font path if available
            if utils.CUSTOM_FONT and utils.CUSTOM_FONT is not None:
                self.font_huge = pygame.font.Font(utils.CUSTOM_FONT, int(120 * SCALE_FACTOR))
                self.font_large = pygame.font.Font(utils.CUSTOM_FONT, int(72 * SCALE_FACTOR))
                self.font_medium = pygame.font.Font(utils.CUSTOM_FONT, int(48 * SCALE_FACTOR))
                self.font_small = pygame.font.Font(utils.CUSTOM_FONT, int(36 * SCALE_FACTOR))
            else:
                raise Exception("No custom font available")
        except Exception as e:
            # Fallback to default font
            self.font_huge = pygame.font.Font(None, int(120 * SCALE_FACTOR))
            self.font_large = pygame.font.Font(None, int(72 * SCALE_FACTOR))
            self.font_medium = pygame.font.Font(None, int(48 * SCALE_FACTOR))
            self.font_small = pygame.font.Font(None, int(36 * SCALE_FACTOR))
            
    def check_leaderboard_status(self):
        """Check player's leaderboard position and set appropriate message"""
        leaderboard = load_leaderboard()
        
        # Add current score temporarily to check position
        temp_leaderboard = leaderboard + [{"name": self.player_name, "score": self.score}]
        temp_leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Find player's position
        for i, entry in enumerate(temp_leaderboard):
            if entry['name'] == self.player_name and entry['score'] == self.score:
                self.leaderboard_position = i + 1
                break
                
        # Set messages based on position
        if self.leaderboard_position == 1:
            self.leaderboard_message = "🎉 New Party Champion! 🎉"
            self.is_new_champion = True
            self.made_leaderboard = True
        elif self.leaderboard_position <= 5:
            self.leaderboard_message = "You made the leaderboard!"
            self.made_leaderboard = True
        else:
            # Find score needed for top 5
            if len(leaderboard) >= 5:
                score_needed = leaderboard[4]['score'] + 1
                self.leaderboard_message = f"Score to beat: {score_needed}"
            else:
                self.leaderboard_message = "You made the leaderboard!"
                self.made_leaderboard = True
                
    def update(self, dt, keys_pressed=None):
        """Update end screen animations"""
        self.timer += dt
        
        # Update balloons
        for balloon in self.balloons:
            balloon.update(dt)
            
        # Update confetti
        self.confetti_system.update()
        
        # Update sparkle trail
        if self.sparkle_trail:
            self.sparkle_trail.update(dt)
            
        # Phase management
        if self.phase == "transition":
            # Smooth transition - ease in from bottom (1.0 seconds)
            if self.timer < 1.0:
                # Ease-out cubic animation
                progress = self.timer / 1.0
                eased_progress = 1 - (1 - progress) ** 3
                self.transition_y_offset = SCREEN_HEIGHT * (1 - eased_progress)
                
                # Start fading overlay during transition
                self.overlay_alpha = min(200, progress * 200)
            else:
                self.transition_y_offset = 0
                self.overlay_alpha = 200
                self.phase = "fade_in"
                self.timer = 0
                
        elif self.phase == "fade_in":
            # Additional fade in for content (0.3 seconds)
            if self.timer >= 0.3:
                self.phase = "score_reveal"
                self.timer = 0
                
        elif self.phase == "score_reveal":
            # Animate score with squash/stretch (1.0 seconds)
            if not self.score_revealed:
                # Play celebration sound
                if self.sound_manager:
                    self.sound_manager.play('special_catch')
                self.score_revealed = True
                
                # Trigger confetti burst
                center_x = SCREEN_WIDTH // 2
                center_y = SCREEN_HEIGHT // 2 - int(50 * SCALE_FACTOR)
                self.confetti_system.celebration_burst(center_x, center_y)
                
                # Create sparkle trail around score
                self.sparkle_trail = SparkleTrail(center_x, center_y, 200 * SCALE_FACTOR)
                
            # Squash and stretch animation
            if self.timer < 0.3:
                # Squash phase
                progress = self.timer / 0.3
                self.score_scale = progress * 1.2  # Scale up to 1.2x
            elif self.timer < 0.6:
                # Stretch phase  
                progress = (self.timer - 0.3) / 0.3
                self.score_scale = 1.2 - (progress * 0.3)  # Scale down to 0.9x
            else:
                # Settle phase
                progress = min(1.0, (self.timer - 0.6) / 0.4)
                self.score_scale = 0.9 + (progress * 0.1)  # Scale to 1.0x
                
            # Glow effect
            self.glow_intensity = math.sin(self.timer * 8) * 0.3 + 0.7
            
            if self.timer >= 1.5:
                self.phase = "leaderboard_check"
                self.timer = 0
                
        elif self.phase == "leaderboard_check":
            # Check leaderboard and show status (1.0 seconds)
            if not self.leaderboard_checked:
                self.check_leaderboard_status()
                self.leaderboard_checked = True
                
                # Play appropriate sound
                if self.sound_manager:
                    if self.is_new_champion:
                        self.sound_manager.play('combo_10x')  # Special fanfare
                    elif self.made_leaderboard:
                        self.sound_manager.play('combo_5x')
                        
            if self.timer >= 1.0:
                self.phase = "buttons"
                self.timer = 0
                
        elif self.phase == "buttons":
            # Animate buttons with bounce-in (0.6 seconds total, staggered)
            for i in range(3):
                button_delay = i * 0.2
                if self.timer >= button_delay:
                    button_time = self.timer - button_delay
                    if button_time < 0.4:
                        # Bounce in animation
                        progress = button_time / 0.4
                        # Elastic ease-out
                        self.button_scales[i] = progress * (1.0 + 0.3 * math.sin(progress * math.pi * 3))
                    else:
                        self.button_scales[i] = 1.0
                        
            if self.timer >= 0.8:
                self.buttons_shown = True
                
    def draw_text_with_glow(self, screen, text, font, x, y, color, glow_color=None, glow_intensity=1.0):
        """Draw text with soft glow effect"""
        if glow_color is None:
            glow_color = (255, 255, 255)
            
        # Draw glow layers
        glow_size = int(8 * SCALE_FACTOR * glow_intensity)
        for i in range(glow_size, 0, -2):
            alpha = int((glow_size - i) / glow_size * 100 * glow_intensity)
            glow_surf = font.render(text, True, glow_color)
            glow_surf.set_alpha(alpha)
            
            # Draw glow in multiple directions
            for dx in range(-i, i + 1, 2):
                for dy in range(-i, i + 1, 2):
                    if dx*dx + dy*dy <= i*i:
                        screen.blit(glow_surf, (x + dx, y + dy))
                        
        # Draw main text
        text_surf = font.render(text, True, color)
        screen.blit(text_surf, (x, y))
        
    def draw(self, screen):
        """Draw the end screen"""
        # Semi-transparent overlay
        if self.overlay_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(int(self.overlay_alpha))
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
        # Create a surface for all content that will be offset during transition
        content_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Draw floating balloons on content surface
        for balloon in self.balloons:
            # Adjust balloon position for transition
            original_y = balloon.y
            balloon.y = original_y - self.transition_y_offset
            balloon.draw(content_surface)
            balloon.y = original_y  # Restore original position
            
        # Draw sparkle trail on content surface
        if self.sparkle_trail:
            # Adjust sparkle positions for transition
            original_center_y = self.sparkle_trail.center_y
            self.sparkle_trail.center_y = original_center_y - self.transition_y_offset
            for sparkle in self.sparkle_trail.sparkles:
                sparkle['y'] -= self.transition_y_offset
            self.sparkle_trail.draw(content_surface)
            # Restore original positions
            self.sparkle_trail.center_y = original_center_y
            for sparkle in self.sparkle_trail.sparkles:
                sparkle['y'] += self.transition_y_offset
            
        # Draw score with animation on content surface
        if self.score_scale > 0:
            score_text = f"Score: {self.score}"
            
            # Create scaled font with proper custom font handling
            scaled_size = int(self.font_huge.get_height() * self.score_scale)
            try:
                if utils.CUSTOM_FONT and utils.CUSTOM_FONT is not None:
                    scaled_font = pygame.font.Font(utils.CUSTOM_FONT, scaled_size)
                else:
                    scaled_font = pygame.font.Font(None, scaled_size)
            except:
                scaled_font = pygame.font.Font(None, scaled_size)
                
            # Center position (adjusted for transition)
            text_rect = scaled_font.size(score_text)
            x = SCREEN_WIDTH // 2 - text_rect[0] // 2
            y = SCREEN_HEIGHT // 2 - int(50 * SCALE_FACTOR) - text_rect[1] // 2 - self.transition_y_offset
            
            # Draw with glow on content surface
            self.draw_text_with_glow(
                content_surface, score_text, scaled_font, x, y,
                GOLD, (255, 255, 200), self.glow_intensity
            )
            
        # Draw leaderboard status message on content surface
        if self.leaderboard_checked and self.leaderboard_message:
            message_y = SCREEN_HEIGHT // 2 + int(50 * SCALE_FACTOR) - self.transition_y_offset
            text_rect = self.font_medium.size(self.leaderboard_message)
            x = SCREEN_WIDTH // 2 - text_rect[0] // 2
            
            # Special styling for champion
            if self.is_new_champion:
                # Draw crown above text
                crown_y = message_y - int(60 * SCALE_FACTOR)
                crown_text = "👑"
                crown_rect = self.font_large.size(crown_text)
                crown_x = SCREEN_WIDTH // 2 - crown_rect[0] // 2
                
                # Animate crown with gentle bounce
                bounce_offset = math.sin(self.timer * 4) * 5
                crown_surf = self.font_large.render(crown_text, True, GOLD)
                content_surface.blit(crown_surf, (crown_x, int(crown_y + bounce_offset)))
                
                color = GOLD
            elif self.made_leaderboard:
                color = GREEN
            else:
                color = WHITE
                
            self.draw_text_with_glow(
                content_surface, self.leaderboard_message, self.font_medium, x, message_y,
                color, (255, 255, 255), 0.5
            )
            
        # Draw buttons on content surface
        if self.buttons_shown:
            button_texts = ["Play Again (SPACE)", "Change Name (N)", "Main Menu (M)"]
            button_y = SCREEN_HEIGHT // 2 + int(150 * SCALE_FACTOR) - self.transition_y_offset
            button_spacing = int(80 * SCALE_FACTOR)
            
            for i, (text, scale) in enumerate(zip(button_texts, self.button_scales)):
                if scale > 0:
                    y = button_y + i * button_spacing
                    
                    # Create scaled font with proper custom font handling
                    scaled_size = int(self.font_small.get_height() * scale)
                    try:
                        if utils.CUSTOM_FONT and utils.CUSTOM_FONT is not None:
                            scaled_font = pygame.font.Font(utils.CUSTOM_FONT, scaled_size)
                        else:
                            scaled_font = pygame.font.Font(None, scaled_size)
                    except:
                        scaled_font = pygame.font.Font(None, scaled_size)
                        
                    text_rect = scaled_font.size(text)
                    x = SCREEN_WIDTH // 2 - text_rect[0] // 2
                    
                    # Button background
                    padding = int(20 * SCALE_FACTOR * scale)
                    bg_rect = pygame.Rect(x - padding, y - padding//2, 
                                        text_rect[0] + padding*2, text_rect[1] + padding)
                    
                    # Hover effect
                    bg_color = (50, 50, 100) if self.button_hover[i] else (30, 30, 60)
                    pygame.draw.rect(content_surface, bg_color, bg_rect, border_radius=int(10 * SCALE_FACTOR))
                    pygame.draw.rect(content_surface, WHITE, bg_rect, int(2 * SCALE_FACTOR), border_radius=int(10 * SCALE_FACTOR))
                    
                    # Button text
                    text_surf = scaled_font.render(text, True, WHITE)
                    content_surface.blit(text_surf, (x, y))
        
        # Apply fade-in effect during transition
        if self.phase == "transition":
            content_alpha = int(255 * (self.timer / 1.0))
            content_surface.set_alpha(content_alpha)
        else:
            content_surface.set_alpha(255)
            
        # Blit the content surface to the main screen
        screen.blit(content_surface, (0, 0))
                    
        # Draw confetti on main screen (not affected by transition)
        self.confetti_system.draw(screen)
        
    def handle_input(self, keys_pressed):
        """Handle input for buttons"""
        if not self.buttons_shown:
            return None
            
        if keys_pressed.get(pygame.K_SPACE):
            return "play_again"
        elif keys_pressed.get(pygame.K_n):
            return "change_name"  
        elif keys_pressed.get(pygame.K_m):
            return "main_menu"
            
        return None
        
    def is_complete(self):
        """Check if all animations are complete"""
        return self.buttons_shown