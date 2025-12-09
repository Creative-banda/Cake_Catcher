import pygame
import cv2
import sys
import random
from game.hand_tracker import HandTracker
from game.player import Player
from game.game_manager import GameManager
from game.sound_manager import SoundManager
from game.menu_animations import MenuAnimations
from game.end_screen import EndScreen
from game import utils
from game.utils import (
    FPS, BLACK, WHITE, GREEN, GOLD, 
    load_leaderboard, save_leaderboard,
    get_last_player_name, save_player_name
)


def convert_cv_to_pygame(cv_image):
    """Convert OpenCV image to Pygame surface"""
    import numpy as np
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    cv_image = np.transpose(cv_image, (1, 0, 2))
    return pygame.surfarray.make_surface(cv_image)


def draw_text_with_effects(surface, text, font, pos, color, stroke_color=None, stroke_width=0, shadow_offset=0, shadow_alpha=128):
    """Draw text with outline stroke and drop shadow for better readability"""
    x, y = pos
    
    # Draw drop shadow
    if shadow_offset > 0:
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_surf.set_alpha(shadow_alpha)
        surface.blit(shadow_surf, (x + shadow_offset, y + shadow_offset))
    
    # Draw stroke/outline
    if stroke_width > 0 and stroke_color:
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx*dx + dy*dy <= stroke_width*stroke_width:
                    outline_surf = font.render(text, True, stroke_color)
                    surface.blit(outline_surf, (x + dx, y + dy))
    
    # Draw main text
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (x, y))
    
    return text_surf.get_rect(topleft=pos)


class GameState:
    """Enum for game states"""
    START_MENU = 0
    NAME_ENTRY = 1
    COUNTDOWN = 2
    PLAYING = 3
    GAME_OVER = 4


def draw_start_screen(screen, font_large, font_medium, font_small, blink_timer, menu_background=None, menu_animations=None):
    """Draw start menu with leaderboard and styled text"""
    if menu_background:
        screen.blit(menu_background, (0, 0))
    else:
        screen.fill(BLACK)
    
    # Draw falling items FIRST (background layer)
    if menu_animations:
        for item in menu_animations.falling_items:
            item.draw(screen)
    
    scale = utils.SCALE_FACTOR
    
    # Title
    title_color = (255, 204, 0)
    title_stroke = (75, 0, 130)
    title_x = utils.SCREEN_WIDTH // 2 - font_large.size("CAKE CATCHER")[0] // 2
    title_y = int(100 * scale)
    draw_text_with_effects(
        screen, "CAKE CATCHER", font_large, 
        (title_x, title_y),
        title_color,
        stroke_color=title_stroke,
        stroke_width=int(6 * scale),
        shadow_offset=int(4 * scale),
        shadow_alpha=90
    )
    
    # Draw sparkles AFTER title (foreground layer)
    if menu_animations:
        for sparkle in menu_animations.sparkles:
            sparkle.draw(screen)
    
    # "TOP SCORES" label
    label_color = (255, 255, 255)
    label_stroke = (199, 21, 133)
    label_x = utils.SCREEN_WIDTH // 2 - font_medium.size("TOP SCORES")[0] // 2
    label_y = int(220 * scale)
    draw_text_with_effects(
        screen, "TOP SCORES", font_medium,
        (label_x, label_y),
        label_color,
        stroke_color=label_stroke,
        stroke_width=int(4 * scale),
        shadow_offset=int(3 * scale),
        shadow_alpha=77
    )
    
    # Leaderboard table setup
    table_start_y = int(290 * scale)
    row_height = int(50 * scale)
    
    # Column headers - yellow with purple outline
    header_y = table_start_y
    header_text = "#    NAME                      SCORE"
    header_x = utils.SCREEN_WIDTH // 2 - font_small.size(header_text)[0] // 2
    
    # Draw header with birthday theme colors
    draw_text_with_effects(
        screen, header_text, font_small,
        (header_x, header_y),
        (255, 217, 61),  # #FFD93D bright yellow
        stroke_color=(75, 0, 130),  # #4B0082 purple
        stroke_width=int(4 * scale),
        shadow_offset=int(2 * scale),
        shadow_alpha=90
    )
    
    # Horizontal line below header
    line_y = header_y + int(35 * scale)
    line_start_x = utils.SCREEN_WIDTH // 2 - int(300 * scale)
    line_end_x = utils.SCREEN_WIDTH // 2 + int(300 * scale)
    pygame.draw.line(screen, (100, 100, 100), (line_start_x, line_y), (line_end_x, line_y), 2)
    
    # Leaderboard entries - 3 column table
    leaderboard = load_leaderboard()
    
    # Define column positions
    rank_x = utils.SCREEN_WIDTH // 2 - int(250 * scale)
    name_x = rank_x + int(40 * scale)
    score_x = utils.SCREEN_WIDTH // 2 + int(250 * scale)  # Right-aligned
    
    entry_start_y = line_y + int(30 * scale)  # Increased spacing from header line
    
    for i, entry in enumerate(leaderboard):
        y_pos = entry_start_y + i * row_height
        
        # Special colors for top 3
        if i == 0:  # 1st place - gold
            rank_color = (255, 215, 0)
            name_color = (255, 235, 150)
            score_color_custom = (255, 223, 100)
        elif i == 1:  # 2nd place - silver
            rank_color = (192, 192, 192)
            name_color = (230, 230, 230)
            score_color_custom = (180, 220, 255)
        elif i == 2:  # 3rd place - bronze
            rank_color = (205, 127, 50)
            name_color = (255, 240, 220)
            score_color_custom = (150, 200, 220)
        else:  # 4th and 5th - standard colors
            rank_color = (255, 79, 163)  # #FF4FA3 pink
            name_color = (255, 255, 255)  # white
            score_color_custom = (108, 231, 255)  # #6CE7FF cyan
        
        # Rank number - pink with black outline (or special color)
        rank_text = f"{i+1}."
        draw_text_with_effects(
            screen, rank_text, font_small,
            (rank_x, y_pos),
            rank_color,
            stroke_color=(0, 0, 0),
            stroke_width=int(3 * scale),
            shadow_offset=int(2 * scale),
            shadow_alpha=64
        )
        
        # Player name - white with navy outline (or special color)
        name_text = entry['name'][:15]
        draw_text_with_effects(
            screen, name_text, font_small,
            (name_x, y_pos),
            name_color,
            stroke_color=(0, 51, 102),  # #003366 navy blue
            stroke_width=int(3 * scale),
            shadow_offset=int(2 * scale),
            shadow_alpha=64
        )
        
        # Score - cyan with dark teal outline (or special color)
        score_text = str(entry['score'])
        score_width = font_small.size(score_text)[0]
        draw_text_with_effects(
            screen, score_text, font_small,
            (score_x - score_width, y_pos),
            score_color_custom,
            stroke_color=(0, 91, 99),  # #005B63 dark teal
            stroke_width=int(3 * scale),
            shadow_offset=int(2 * scale),
            shadow_alpha=64
        )
    
    # Horizontal line below table (with extra spacing for text clearance)
    table_end_y = entry_start_y + len(leaderboard) * row_height + int(45 * scale)
    pygame.draw.line(screen, (100, 100, 100), (line_start_x, table_end_y), (line_end_x, table_end_y), 2)
    
    # Last player info below table - light yellow with gray outline
    saved_name = get_last_player_name()
    if saved_name:
        try:
            small_font = pygame.font.Font(utils.CUSTOM_FONT, int(24 * scale))
        except:
            small_font = pygame.font.Font(None, int(24 * scale))
        
        last_player_y = table_end_y + int(30 * scale)
        hint_text = f"Last Player: {saved_name}  |  Press N to change"
        
        # Draw with styled text
        hint_x = utils.SCREEN_WIDTH // 2 - small_font.size(hint_text)[0] // 2
        
        # Shadow
        shadow_surf = small_font.render(hint_text, True, (0, 0, 0))
        shadow_surf.set_alpha(90)
        screen.blit(shadow_surf, (hint_x + 1, last_player_y + 1))
        
        # Outline
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx + dy*dy <= 4:
                    outline = small_font.render(hint_text, True, (68, 68, 68))  # #444444
                    screen.blit(outline, (hint_x + dx, last_player_y + dy))
        
        # Main text
        hint_surf = small_font.render(hint_text, True, (255, 226, 138))  # #FFE28A light yellow
        screen.blit(hint_surf, (hint_x, last_player_y))
    
    # Instructions - always visible with pulse animation
    instruction_color = (255, 255, 255)
    instruction_stroke = (0, 150, 136)
    instruction_text = "Press SPACE to Start"
    
    # Get pulse scale
    pulse_scale = menu_animations.get_pulse_scale() if menu_animations else 1.0
    
    # Create scaled font for pulse effect
    base_size = int(36 * scale)
    pulsed_size = int(base_size * pulse_scale)
    try:
        pulsed_font = pygame.font.Font(utils.CUSTOM_FONT, pulsed_size)
    except:
        pulsed_font = pygame.font.Font(None, pulsed_size)
    
    instruction_x = utils.SCREEN_WIDTH // 2 - pulsed_font.size(instruction_text)[0] // 2
    instruction_y = utils.SCREEN_HEIGHT - int(120 * scale)
    draw_text_with_effects(
        screen, instruction_text, pulsed_font,
        (instruction_x, instruction_y),
        instruction_color,
        stroke_color=instruction_stroke,
        stroke_width=int(3 * scale),
        shadow_offset=int(2 * scale),
        shadow_alpha=64
    )


def draw_name_entry_screen(screen, font_large, font_medium, font_small, name_input, blink_timer):
    """Draw name entry screen"""
    overlay = pygame.Surface((utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    scale = utils.SCALE_FACTOR
    
    # Title
    title_text = "Enter Your Name"
    title_x = utils.SCREEN_WIDTH // 2 - font_large.size(title_text)[0] // 2
    title_y = utils.SCREEN_HEIGHT // 2 - int(150 * scale)
    draw_text_with_effects(
        screen, title_text, font_large,
        (title_x, title_y),
        (255, 204, 0),
        stroke_color=(75, 0, 130),
        stroke_width=int(5 * scale),
        shadow_offset=int(3 * scale),
        shadow_alpha=100
    )
    
    # Input box
    input_box = pygame.Rect(utils.SCREEN_WIDTH // 2 - 200, utils.SCREEN_HEIGHT // 2, 400, 60)
    pygame.draw.rect(screen, WHITE, input_box, 3)
    
    # Display name with blinking cursor
    cursor = "|" if blink_timer % 40 < 20 else ""
    name_surface = font_medium.render(name_input + cursor, True, WHITE)
    name_rect = name_surface.get_rect(center=(utils.SCREEN_WIDTH // 2, utils.SCREEN_HEIGHT // 2 + 30))
    screen.blit(name_surface, name_rect)
    
    # Instructions
    inst1_text = "ENTER - Confirm | BACKSPACE - Delete"
    inst1_x = utils.SCREEN_WIDTH // 2 - font_small.size(inst1_text)[0] // 2
    inst1_y = utils.SCREEN_HEIGHT // 2 + int(100 * scale)
    draw_text_with_effects(
        screen, inst1_text, font_small,
        (inst1_x, inst1_y),
        GREEN,
        stroke_color=(0, 100, 0),
        stroke_width=int(2 * scale),
        shadow_offset=int(1 * scale),
        shadow_alpha=80
    )


def draw_welcome_message(screen, font_large, font_medium, welcome_text, elapsed_time, background=None):
    """Draw welcome message with fade animation"""
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)
    
    # Animation timing: 0.3s fade in, 1.2s hold, 0.3s fade out = 1.8s total
    fade_in_duration = 0.3
    hold_duration = 1.2
    fade_out_duration = 0.3
    
    # Calculate alpha based on elapsed time
    if elapsed_time < fade_in_duration:
        # Fade in
        alpha = int((elapsed_time / fade_in_duration) * 255)
    elif elapsed_time < fade_in_duration + hold_duration:
        # Hold
        alpha = 255
    else:
        # Fade out
        fade_out_progress = elapsed_time - (fade_in_duration + hold_duration)
        alpha = int((1 - fade_out_progress / fade_out_duration) * 255)
    
    alpha = max(0, min(255, alpha))
    
    # Get text dimensions
    text_surf = font_medium.render(welcome_text, True, (255, 215, 0))
    text_rect = text_surf.get_rect(center=(utils.SCREEN_WIDTH // 2, utils.SCREEN_HEIGHT // 2))
    
    scale = utils.SCALE_FACTOR
    stroke_width = int(4 * scale)
    
    # Draw shadow
    shadow_surf = font_medium.render(welcome_text, True, (0, 0, 0))
    shadow_surf.set_alpha(int(alpha * 0.6))
    shadow_rect = shadow_surf.get_rect(center=(utils.SCREEN_WIDTH // 2 + 3, utils.SCREEN_HEIGHT // 2 + 3))
    screen.blit(shadow_surf, shadow_rect)
    
    # Draw stroke (purple)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx*dx + dy*dy <= stroke_width*stroke_width:
                outline = font_medium.render(welcome_text, True, (75, 0, 130))
                outline.set_alpha(alpha)
                outline_rect = outline.get_rect(center=(utils.SCREEN_WIDTH // 2 + dx, utils.SCREEN_HEIGHT // 2 + dy))
                screen.blit(outline, outline_rect)
    
    # Draw main text
    text_surf.set_alpha(alpha)
    screen.blit(text_surf, text_rect)


def draw_countdown_screen(screen, font_large, font_medium, countdown_number, countdown_timer, welcome_text=""):
    """Draw countdown animation with welcome message overlay"""
    overlay = pygame.Surface((utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Draw welcome message above countdown
    if welcome_text:
        # Calculate alpha for welcome message based on countdown progress
        # Full alpha at start, fade during "1", fade out during "GO"
        if countdown_timer < 2.0:  # During 3 and 2
            welcome_alpha = 255
        elif countdown_timer < 3.0:  # During 1
            welcome_alpha = 150
        else:  # During GO
            fade_progress = (countdown_timer - 3.0) / 1.0
            welcome_alpha = int(150 * (1 - fade_progress))
        
        welcome_alpha = max(0, min(255, welcome_alpha))
        
        scale = utils.SCALE_FACTOR
        stroke_width = int(3 * scale)
        
        # Position 15% higher than center
        welcome_y = utils.SCREEN_HEIGHT // 2 - int(utils.SCREEN_HEIGHT * 0.15)
        
        # Draw shadow
        shadow_surf = font_medium.render(welcome_text, True, (0, 0, 0))
        shadow_surf.set_alpha(int(welcome_alpha * 0.6))
        shadow_rect = shadow_surf.get_rect(center=(utils.SCREEN_WIDTH // 2 + 3, welcome_y + 3))
        screen.blit(shadow_surf, shadow_rect)
        
        # Draw stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx*dx + dy*dy <= stroke_width*stroke_width:
                    outline = font_medium.render(welcome_text, True, (75, 0, 130))
                    outline.set_alpha(welcome_alpha)
                    outline_rect = outline.get_rect(center=(utils.SCREEN_WIDTH // 2 + dx, welcome_y + dy))
                    screen.blit(outline, outline_rect)
        
        # Draw main text
        text_surf = font_medium.render(welcome_text, True, (255, 215, 0))
        text_surf.set_alpha(welcome_alpha)
        text_rect = text_surf.get_rect(center=(utils.SCREEN_WIDTH // 2, welcome_y))
        screen.blit(text_surf, text_rect)
    
    # Draw countdown number (existing animation)
    anim_progress = countdown_timer % 1.0  # Each number lasts 1 second
    scale_factor = 1.0 + (1 - anim_progress) * 0.3
    alpha = int(255 * anim_progress)
    
    if countdown_number > 0:
        text = str(countdown_number)
    else:
        text = "🎂 GO! 🎂"
    
    scaled_size = int(font_large.get_height() * scale_factor)
    try:
        scaled_font = pygame.font.Font(utils.CUSTOM_FONT, scaled_size)
    except:
        scaled_font = pygame.font.Font(None, scaled_size)
    
    text_surf = scaled_font.render(text, True, (255, 215, 0))
    text_surf.set_alpha(alpha)
    text_rect = text_surf.get_rect(center=(utils.SCREEN_WIDTH // 2, utils.SCREEN_HEIGHT // 2))
    screen.blit(text_surf, text_rect)


def main():
    pygame.init()
    
    display_info = pygame.display.Info()
    SCREEN_WIDTH = display_info.current_w
    SCREEN_HEIGHT = display_info.current_h
    
    REFERENCE_WIDTH = 1920
    REFERENCE_HEIGHT = 1080
    scale_width = SCREEN_WIDTH / REFERENCE_WIDTH
    scale_height = SCREEN_HEIGHT / REFERENCE_HEIGHT
    SCALE_FACTOR = min(scale_width, scale_height)
    
    utils.SCREEN_WIDTH = SCREEN_WIDTH
    utils.SCREEN_HEIGHT = SCREEN_HEIGHT
    utils.SCALE_FACTOR = SCALE_FACTOR
    
    try:
        font_path = 'assets/fonts/Quantum Profit.ttf'
        # Test if the font can be loaded
        test_font = pygame.font.Font(font_path, 24)
        utils.CUSTOM_FONT = font_path
    except Exception as e:
        utils.CUSTOM_FONT = None
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption("Cake Catcher - Hand Tracking Game")
    clock = pygame.time.Clock()
    
    # Load fonts
    try:
        font_path = utils.CUSTOM_FONT
        font_large = pygame.font.Font(font_path, int(90 * SCALE_FACTOR))
        font_medium = pygame.font.Font(font_path, int(50 * SCALE_FACTOR))
        font_small = pygame.font.Font(font_path, int(36 * SCALE_FACTOR))
    except:
        font_large = pygame.font.Font(None, int(90 * SCALE_FACTOR))
        font_medium = pygame.font.Font(None, int(50 * SCALE_FACTOR))
        font_small = pygame.font.Font(None, int(36 * SCALE_FACTOR))
    
    # Initialize components
    hand_tracker = HandTracker()
    sound_manager = SoundManager()
    menu_animations = MenuAnimations(SCREEN_WIDTH, SCREEN_HEIGHT)
    player = None
    game_manager = None
    
    # Load backgrounds
    try:
        background = pygame.image.load('assets/images/background_party_2.png').convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = None
    
    try:
        menu_background = pygame.image.load('assets/images/menu_background.png').convert()
        menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        menu_background = None
    
    # Game state
    game_state = GameState.START_MENU
    show_webcam = True
    blink_timer = 0
    
    # End screen
    end_screen = None
    game_over_delay_timer = 0
    game_over_delay_duration = 1.0  # 1 second delay before showing end screen
    
    # Start menu music
    sound_manager.play_music('main_menu_background_music.mp3', loops=-1, volume=0.25)
    
    # Name entry
    name_input = get_last_player_name()
    player_name = ""
    
    # Welcome messages
    welcome_messages = [
        "Happy Birthday energy, {NAME}! Let’s make this round sweet!",
        "Ready for the party, {NAME}? Time to catch some cake!",
        "Let’s see those birthday reflexes, {NAME}!",
        "Catch fast, {NAME}! The cake won't wait forever!",
        "Party mode engaged, {NAME}! Don’t miss the treats!",
        "It’s all fun today, {NAME}! Make this one count!",
        "Show those skills, {NAME}! The celebration is watching!",
        "No pressure, {NAME}... but the cake depends on you.",
        "Grab the goodies and dodge the disasters, {NAME}!",
        "Alright {NAME} — grab cake like it’s your birthday!"
    ]
    welcome_text = ""
    
    # Countdown
    countdown_timer = 0
    countdown_start_time = 0
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_w:
                    show_webcam = not show_webcam
                
                # Start menu
                if game_state == GameState.START_MENU:
                    if event.key == pygame.K_SPACE:
                        sound_manager.play('menu_press')
                        game_state = GameState.NAME_ENTRY
                        name_input = get_last_player_name()
                    elif event.key == pygame.K_n:
                        sound_manager.play('menu_press')
                        game_state = GameState.NAME_ENTRY
                        name_input = ""
                
                # Name entry
                elif game_state == GameState.NAME_ENTRY:
                    if event.key == pygame.K_RETURN:
                        player_name = name_input if len(name_input) > 0 else "Player"
                        save_player_name(player_name)
                        sound_manager.play('menu_press')
                        # Select random welcome message and start countdown
                        welcome_text = random.choice(welcome_messages).replace("{NAME}", player_name)
                        countdown_start_time = pygame.time.get_ticks()
                        game_state = GameState.COUNTDOWN
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    elif event.unicode.isprintable() and len(name_input) < 15:
                        sound_manager.play('typing')
                        name_input += event.unicode.upper()
                
                # Game over
                elif game_state == GameState.GAME_OVER:
                    if end_screen:
                        # Handle end screen input
                        keys_pressed = {event.key: True}
                        action = end_screen.handle_input(keys_pressed)
                        
                        if action == "play_again":
                            # Start new game with same player
                            sound_manager.play('menu_press')
                            welcome_text = random.choice(welcome_messages).replace("{NAME}", player_name)
                            countdown_start_time = pygame.time.get_ticks()
                            game_state = GameState.COUNTDOWN
                            end_screen = None
                        elif action == "change_name":
                            # Go to name entry
                            sound_manager.play('menu_press')
                            sound_manager.stop_music()
                            sound_manager.play_music('main_menu_background_music.mp3', loops=-1, volume=0.25)
                            game_state = GameState.NAME_ENTRY
                            name_input = ""
                            end_screen = None
                        elif action == "main_menu":
                            # Return to menu
                            sound_manager.play('menu_press')
                            sound_manager.stop_music()
                            sound_manager.play_music('main_menu_background_music.mp3', loops=-1, volume=0.25)
                            game_state = GameState.START_MENU
                            end_screen = None
        
        # Get hand position
        hand_x, webcam_frame = hand_tracker.get_hand_position()
        
        # State logic
        if game_state == GameState.START_MENU:
            blink_timer += 1
            # Update menu animations
            current_time = pygame.time.get_ticks()
            dt = (current_time - (getattr(main, '_last_menu_time', current_time))) / 1000.0
            main._last_menu_time = current_time
            menu_animations.update(dt)
            draw_start_screen(screen, font_large, font_medium, font_small, blink_timer, menu_background, menu_animations)
        
        elif game_state == GameState.NAME_ENTRY:
            blink_timer += 1
            if menu_background:
                screen.blit(menu_background, (0, 0))
            else:
                screen.fill(BLACK)
            draw_name_entry_screen(screen, font_large, font_medium, font_small, name_input, blink_timer)
        
        elif game_state == GameState.COUNTDOWN:
            # 3 second countdown with welcome message overlay (1 second per number)
            countdown_timer = (pygame.time.get_ticks() - countdown_start_time) / 1000.0
            
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            
            # Determine which number is currently showing
            current_number = 0
            if countdown_timer < 1.0:
                current_number = 3
            elif countdown_timer < 2.0:
                current_number = 2
            elif countdown_timer < 3.0:
                current_number = 1
            
            # Play beep once at the start of each number
            # Use a small time window at the beginning of each second
            if countdown_timer < 0.05:  # First frame of "3"
                sound_manager.play('countdown')
            elif 1.0 <= countdown_timer < 1.05:  # First frame of "2"
                sound_manager.play('countdown')
            elif 2.0 <= countdown_timer < 2.05:  # First frame of "1"
                sound_manager.play('countdown')
            elif 3.0 <= countdown_timer < 3.05:  # GO sound
                sound_manager.play('go')
                # Switch to gameplay music
                sound_manager.stop_music()
                sound_manager.play_music('background_music.mp3', loops=-1, volume=0.20)
            
            if countdown_timer < 1.0:
                draw_countdown_screen(screen, font_large, font_medium, 3, countdown_timer, welcome_text)
            elif countdown_timer < 2.0:
                draw_countdown_screen(screen, font_large, font_medium, 2, countdown_timer, welcome_text)
            elif countdown_timer < 3.0:
                draw_countdown_screen(screen, font_large, font_medium, 1, countdown_timer, welcome_text)
            else:
                # Start game
                player = Player()
                game_manager = GameManager(sound_manager)
                game_state = GameState.PLAYING
        
        elif game_state == GameState.PLAYING:
            if hand_x is not None:
                player.update_target(hand_x)
            player.update()
            
            game_manager.update(player)
            
            if game_manager.game_over:
                # Save score with player name
                leaderboard = load_leaderboard()
                leaderboard.append({"name": player_name, "score": game_manager.score})
                save_leaderboard(leaderboard)
                
                # Start delay timer before showing end screen
                game_over_delay_timer = 0
                game_state = GameState.GAME_OVER
            
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            
            player.draw(screen)
            game_manager.draw(screen)
        
        elif game_state == GameState.GAME_OVER:
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            
            player.draw(screen)
            game_manager.draw(screen)
            
            # Handle delay before showing end screen
            current_time = pygame.time.get_ticks()
            dt = (current_time - (getattr(main, '_last_end_time', current_time))) / 1000.0
            main._last_end_time = current_time
            
            if end_screen is None:
                game_over_delay_timer += dt
                if game_over_delay_timer >= game_over_delay_duration:
                    # Create end screen after delay
                    end_screen = EndScreen(game_manager.score, player_name, sound_manager)
            else:
                # Update and draw end screen
                end_screen.update(dt)
                end_screen.draw(screen)
        
        # Draw webcam preview
        if show_webcam and webcam_frame is not None:
            try:
                webcam_surface = convert_cv_to_pygame(webcam_frame)
                screen.blit(webcam_surface, (10, SCREEN_HEIGHT - 130))
            except:
                pass
        
        # Draw help text
        if game_state == GameState.PLAYING:
            try:
                help_font = pygame.font.Font(utils.CUSTOM_FONT, int(20 * SCALE_FACTOR))
            except:
                help_font = pygame.font.Font(None, int(20 * SCALE_FACTOR))
            
            help_text = "W: Webcam | ESC: Quit"
            help_color = (180, 180, 180)
            help_x = SCREEN_WIDTH - help_font.size(help_text)[0] - 10
            help_y = SCREEN_HEIGHT - 30
            draw_text_with_effects(
                screen, help_text, help_font,
                (help_x, help_y),
                help_color,
                stroke_color=(50, 50, 50),
                stroke_width=1,
                shadow_offset=1,
                shadow_alpha=100
            )
        
        pygame.display.flip()
        clock.tick(FPS)
    
    hand_tracker.release()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
