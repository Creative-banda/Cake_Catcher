import pygame
import random
from game.item import Item
from game.confetti import ConfettiSystem
from game.combo_effect import ComboEffect
from game.utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GAME_DURATION,
    ITEM_GOOD, ITEM_BAD, ITEM_SPECIAL, SPAWN_RATES, ScorePopup,
    WHITE, RED, GREEN, GOLD, lerp
)


class GameManager:
    """Manages game state, scoring, spawning, and difficulty"""
    
    def __init__(self, sound_manager=None):
        from game.utils import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR, CUSTOM_FONT
        
        self.sound_manager = sound_manager
        self.score = 0
        self.items = []
        self.popups = []
        self.start_time = pygame.time.get_ticks()
        self.spawn_timer = 0
        self.difficulty_level = 1
        self.speed_multiplier = 1.0
        self.game_over = False
        
        # Fair spawn system for special items
        self.next_special_spawn_time = random.uniform(20, 30)
        self.special_spawned_this_interval = False
        self.special_missed = False
        self.special_items_spawned = 0
        
        # Combo system with timer
        self.combo_count = 0
        self.combo_timer = 0  # Time in seconds
        self.combo_max_time = 4.0  # 4 second window
        self.combo_effect = None  # Active visual effect
        self.last_frame_time = pygame.time.get_ticks()
        
        # Fonts - using custom font with scaled sizes
        try:
            if hasattr(CUSTOM_FONT, '__call__'):
                font_path = None
            else:
                font_path = CUSTOM_FONT
            self.font_large = pygame.font.Font(font_path, int(72 * SCALE_FACTOR))
            self.font_medium = pygame.font.Font(font_path, int(48 * SCALE_FACTOR))
            self.font_small = pygame.font.Font(font_path, int(36 * SCALE_FACTOR))
            self.font_tiny = pygame.font.Font(font_path, int(28 * SCALE_FACTOR))
        except:
            # Fallback to default font if custom font fails
            self.font_large = pygame.font.Font(None, int(72 * SCALE_FACTOR))
            self.font_medium = pygame.font.Font(None, int(48 * SCALE_FACTOR))
            self.font_small = pygame.font.Font(None, int(36 * SCALE_FACTOR))
            self.font_tiny = pygame.font.Font(None, int(28 * SCALE_FACTOR))
        
        # Animated confetti system
        self.confetti_system = ConfettiSystem()
        
    def get_elapsed_time(self):
        """Get elapsed game time in seconds"""
        return (pygame.time.get_ticks() - self.start_time) / 1000
    
    def get_remaining_time(self):
        """Get remaining game time"""
        remaining = GAME_DURATION - self.get_elapsed_time()
        return max(0, remaining)
    
    def get_difficulty_params(self):
        """Get speed multiplier and spawn interval based on elapsed time with smooth interpolation"""
        elapsed = self.get_elapsed_time()
        
        # Define difficulty stages: (time_threshold, speed, spawn_interval_seconds)
        stages = [
            (0, 1.3, 2.0),    # 0-10s: spawn every 2s, faster start
            (10, 1.5, 1.7),   # 10-30s: spawn every 1.7 seconds
            (30, 1.8, 1.4),   # 30-45s: spawn every 1.4 seconds
            (45, 2.1, 1.1)    # 45-60s: spawn every 1.1 seconds
        ]
        
        # Find current and next stage
        current_stage = stages[0]
        next_stage = stages[1]
        
        for i in range(len(stages) - 1):
            if elapsed >= stages[i][0] and (i == len(stages) - 2 or elapsed < stages[i + 1][0]):
                current_stage = stages[i]
                next_stage = stages[i + 1] if i < len(stages) - 1 else stages[i]
                break
        
        # Interpolate between current and next stage
        if current_stage == next_stage:
            return current_stage[1], current_stage[2]
        
        # Calculate interpolation factor
        time_range = next_stage[0] - current_stage[0]
        time_into_range = elapsed - current_stage[0]
        factor = min(1.0, time_into_range / time_range) if time_range > 0 else 0
        
        # Lerp speed and spawn interval
        speed = lerp(current_stage[1], next_stage[1], factor)
        spawn_interval = lerp(current_stage[2], next_stage[2], factor)
        
        return speed, spawn_interval
    
    def update(self, player):
        """Update game state"""
        if self.game_over:
            return
        
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_frame_time) / 1000.0  # Convert to seconds
        self.last_frame_time = current_time
            
        # Check if time is up
        if self.get_remaining_time() <= 0:
            self.game_over = True
            return
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0  # Reset combo when timer expires
                self.combo_timer = 0
        
        # Update combo effect animation
        if self.combo_effect:
            if not self.combo_effect.update(dt):
                self.combo_effect = None  # Remove finished effect
        
        # Get current difficulty parameters
        self.speed_multiplier, spawn_interval_seconds = self.get_difficulty_params()
        spawn_interval_frames = int(spawn_interval_seconds * 30)  # Convert to frames
        
        # Check for special item spawn timing
        elapsed = self.get_elapsed_time()
        if elapsed >= self.next_special_spawn_time and not self.special_spawned_this_interval:
            self.spawn_item(force_special=True)
            self.special_spawned_this_interval = True
            self.special_items_spawned += 1
        
        # Spawn regular items
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_interval_frames:
            self.spawn_timer = 0
            self.spawn_item()
        
        # Update items
        for item in self.items[:]:
            item.update(dt)
            
            # Check collision with player
            if not item.caught and item.get_rect().colliderect(player.get_rect()):
                item.caught = True
                self.handle_catch(item, player)
            
            # Check if special item was missed
            if item.is_special() and item.is_off_screen() and not item.caught:
                self.special_missed = True
                # Schedule retry in 10 seconds
                self.next_special_spawn_time = elapsed + 10
                self.special_spawned_this_interval = False
            
            # Remove items that are off screen
            if item.is_off_screen():
                self.items.remove(item)
        
        # Reset special spawn for next interval if this one completed
        if self.special_spawned_this_interval and elapsed >= self.next_special_spawn_time + 10:
            self.next_special_spawn_time = elapsed + random.uniform(20, 30)
            self.special_spawned_this_interval = False
        
        # Update popups
        for popup in self.popups[:]:
            popup.update()
            if not popup.is_alive():
                self.popups.remove(popup)
        
        # Update confetti system
        self.confetti_system.update()
    
    def spawn_item(self, force_special=False):
        """Spawn a random item or force spawn special"""
        if force_special:
            item_type = ITEM_SPECIAL
        else:
            rand = random.random()
            if rand < SPAWN_RATES[ITEM_GOOD]:
                item_type = ITEM_GOOD
            else:
                item_type = ITEM_BAD
        
        item = Item(item_type, self.speed_multiplier)
        self.items.append(item)
    
    def handle_catch(self, item, player):
        """Handle item being caught"""
        from game.utils import SCALE_FACTOR
        
        self.score += item.score_value
        
        # Play catch sound
        if self.sound_manager:
            if item.is_special():
                self.sound_manager.play('special_catch')
            elif item.is_good():
                self.sound_manager.play('good_catch')
            elif item.is_bad():
                self.sound_manager.play('bad_catch')
        
        # Timer-based combo system - both good items AND special items count for combo
        if item.is_good() or item.is_special():
            # Reset timer to 4 seconds on good catch
            self.combo_timer = self.combo_max_time
            prev_combo = self.combo_count
            self.combo_count += 1
            
            # Play combo sound when combo increases
            if self.sound_manager and self.combo_count >= 2:
                self.sound_manager.play('combo')
            
            # Trigger animated combo effect (only if combo >= 2)
            if self.combo_count >= 2:
                # Spawn effect at plate position, replacing previous one
                self.combo_effect = ComboEffect(
                    player.rect.centerx,
                    player.rect.top - 20,
                    self.combo_count,
                    self.font_medium,
                    SCALE_FACTOR
                )
                
                # Check for special effects (combo 10+)
                if self.combo_effect.should_trigger_special():
                    # Small screen shake and confetti
                    self.confetti_system.celebration_burst(player.rect.centerx, player.rect.centery)
                    if self.sound_manager:
                        self.sound_manager.play('confetti')
            
            # Milestone bonuses
            if self.combo_count == 5:
                bonus = 10
                self.score += bonus
                bonus_popup = ScorePopup(item.rect.centerx, item.rect.centery - 40, bonus, GOLD)
                self.popups.append(bonus_popup)
                if self.sound_manager:
                    self.sound_manager.play('combo_5x')
            elif self.combo_count == 10:
                bonus = 30
                self.score += bonus
                bonus_popup = ScorePopup(item.rect.centerx, item.rect.centery - 40, bonus, GOLD)
                self.popups.append(bonus_popup)
                if self.sound_manager:
                    self.sound_manager.play('combo_10x')
                
        elif item.is_bad():
            # Reset combo on bad catch
            if self.combo_count > 0 and self.sound_manager:
                self.sound_manager.play('combo_break')
            self.combo_count = 0
            self.combo_timer = 0
            self.combo_effect = None  # Clear visual
        
        # Create score popup
        color = GREEN if item.score_value > 0 else RED
        if item.is_special():
            color = GOLD
            # Trigger elegant celebration at catch position
            self.confetti_system.celebration_burst(item.rect.centerx, item.rect.centery)
            if self.sound_manager:
                self.sound_manager.play('confetti')
        
        popup = ScorePopup(
            item.rect.centerx,
            item.rect.centery,
            item.score_value,
            color
        )
        self.popups.append(popup)
        
        # Remove caught item
        if item in self.items:
            self.items.remove(item)
    
    def draw(self, screen):
        """Draw all game elements"""
        # Draw items directly on screen
        for item in self.items:
            item.draw(screen)
        
        # Draw popups
        for popup in self.popups:
            popup.draw(screen, self.font_small)
        
        # Draw combo effect
        if self.combo_effect:
            self.combo_effect.draw(screen)
        
        # Draw UI
        self.draw_ui(screen)
        
        # Draw animated confetti particles
        self.confetti_system.draw(screen)
    
    def draw_ui(self, screen):
        """Draw score and timer with styled text"""
        from game.utils import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR
        
        # Helper function for drawing text with effects
        def draw_text_styled(text, font, x, y, color, stroke_color, stroke_width):
            # Shadow
            shadow_surf = font.render(text, True, (0, 0, 0))
            shadow_surf.set_alpha(100)
            screen.blit(shadow_surf, (x + 2, y + 2))
            
            # Stroke
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx*dx + dy*dy <= stroke_width*stroke_width:
                        outline = font.render(text, True, stroke_color)
                        screen.blit(outline, (x + dx, y + dy))
            
            # Main text
            text_surf = font.render(text, True, color)
            screen.blit(text_surf, (x, y))
        
        scale = SCALE_FACTOR
        
        # Score - white with navy stroke
        score_text = f"Score: {self.score}"
        draw_text_styled(
            score_text, self.font_medium,
            20, 20,
            (255, 255, 255),  # White
            (0, 51, 102),  # Navy blue
            int(3 * scale)
        )
        
        # Timer - white/red with dark stroke
        remaining = int(self.get_remaining_time())
        timer_color = (255, 80, 80) if remaining <= 10 else (255, 255, 255)
        timer_stroke = (100, 0, 0) if remaining <= 10 else (0, 51, 102)
        timer_text = f"Time: {remaining}s"
        timer_x = SCREEN_WIDTH - self.font_medium.size(timer_text)[0] - 20
        draw_text_styled(
            timer_text, self.font_medium,
            timer_x, 20,
            timer_color,
            timer_stroke,
            int(3 * scale)
        )
        
        # Combo counter with timer bar - only show when combo >= 2
        if self.combo_count >= 2 and self.combo_timer > 0:
            combo_y = int(80 * scale)
            
            # Combo text
            combo_text = f"{self.combo_count}x Combo"
            draw_text_styled(
                combo_text, self.font_tiny,
                20, combo_y,
                (255, 215, 0),  # Gold
                (75, 0, 130),  # Purple
                int(2 * scale)
            )
            
            # Timer bar underneath
            bar_width = 150 * scale
            bar_height = 6 * scale
            bar_x = 20
            bar_y = combo_y + int(35 * scale)
            
            # Background bar
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar (decreases as timer runs out)
            progress = self.combo_timer / self.combo_max_time
            progress_width = bar_width * progress
            
            # Color based on urgency
            if progress > 0.5:
                bar_color = (0, 230, 118)  # Green
            elif progress > 0.25:
                bar_color = (255, 235, 59)  # Yellow
            else:
                bar_color = (255, 80, 80)  # Red
            
            pygame.draw.rect(screen, bar_color,
                           (bar_x, bar_y, progress_width, bar_height))
    
    def draw_game_over(self, screen):
        """Draw game over screen with styled text"""
        from game.utils import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR
        
        def draw_text_styled(text, font, center_x, center_y, color, stroke_color, stroke_width):
            # Get text dimensions
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(center_x, center_y))
            
            # Shadow
            shadow_surf = font.render(text, True, (0, 0, 0))
            shadow_surf.set_alpha(120)
            shadow_rect = shadow_surf.get_rect(center=(center_x + 3, center_y + 3))
            screen.blit(shadow_surf, shadow_rect)
            
            # Stroke - draw relative to final position
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx*dx + dy*dy <= stroke_width*stroke_width:
                        outline = font.render(text, True, stroke_color)
                        outline_rect = outline.get_rect(center=(center_x + dx, center_y + dy))
                        screen.blit(outline, outline_rect)
            
            # Main text
            screen.blit(text_surf, text_rect)
        
        scale = SCALE_FACTOR
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Game Over text - red with dark stroke
        draw_text_styled(
            "GAME OVER", self.font_large,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(100 * scale),
            (255, 80, 80),  # Red
            (100, 0, 0),  # Dark red
            int(5 * scale)
        )
        
        # Final Score - white with navy stroke
        score_text = f"Final Score: {self.score}"
        draw_text_styled(
            score_text, self.font_medium,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            (255, 255, 255),  # White
            (0, 51, 102),  # Navy
            int(3 * scale)
        )
        
        # Restart instruction - green with teal stroke
        draw_text_styled(
            "Press R to Restart", self.font_small,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(100 * scale),
            (100, 255, 100),  # Green
            (0, 150, 136),  # Teal
            int(3 * scale)
        )
    
    def reset(self):
        """Reset game state"""
        self.score = 0
        self.items = []
        self.popups = []
        self.start_time = pygame.time.get_ticks()
        self.spawn_timer = 0
        self.difficulty_level = 1
        self.speed_multiplier = 1.0
        self.game_over = False
        self.confetti_system = ConfettiSystem()
        
        # Reset fair spawn
        self.next_special_spawn_time = random.uniform(20, 30)
        self.special_spawned_this_interval = False
        self.special_missed = False
        self.special_items_spawned = 0
        
        # Reset combo
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_effect = None
        self.last_frame_time = pygame.time.get_ticks()
