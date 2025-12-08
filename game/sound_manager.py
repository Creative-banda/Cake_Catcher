import pygame
import os


class SoundManager:
    """Manages all game sounds and music"""
    
    def __init__(self):
        """Initialize pygame mixer and load all sounds"""
        pygame.mixer.init()
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Load all sound effects
        sound_files = {
            'menu_press': 'space_press.mp3',
            'typing': 'typing_sound.mp3',
            'countdown': 'count_down_beep.mp3',
            'go': 'whoosh.mp3',
            'good_catch': 'ding.mp3',
            'bad_catch': 'splat.mp3',
            'special_catch': 'magical_sparkle.mp3',
            'combo': 'combo.mp3',
            'combo_5x': 'milestone_5x.mp3',
            'combo_10x': 'milestone_10x.mp3',
            'combo_break': 'combo_break.mp3',
            'confetti': 'confetti-pop.mp3'
        }
        
        # Load each sound
        for name, filename in sound_files.items():
            try:
                path = os.path.join('assets', 'sounds', filename)
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Warning: Could not load sound {filename}: {e}")
                self.sounds[name] = None
        
        # Set volume levels for different sound types
        self._set_volumes()
        
        # Music state
        self.music_enabled = True
        self.sfx_enabled = True
        
    def _set_volumes(self):
        """Set appropriate volumes for different sounds"""
        # Menu sounds - subtle
        if self.sounds['menu_press']:
            self.sounds['menu_press'].set_volume(0.3)
        if self.sounds['typing']:
            self.sounds['typing'].set_volume(0.2)
        
        # Countdown - prominent
        if self.sounds['countdown']:
            self.sounds['countdown'].set_volume(0.6)
        if self.sounds['go']:
            self.sounds['go'].set_volume(0.7)
        
        # Catching sounds - clear and satisfying
        if self.sounds['good_catch']:
            self.sounds['good_catch'].set_volume(1)  # Increased from 0.4
        if self.sounds['bad_catch']:
            self.sounds['bad_catch'].set_volume(0.5)
        if self.sounds['special_catch']:
            self.sounds['special_catch'].set_volume(1)
        
        # Combo sounds - celebratory and noticeable
        if self.sounds['combo']:
            self.sounds['combo'].set_volume(1)  # Increased from 0.3
        if self.sounds['combo_5x']:
            self.sounds['combo_5x'].set_volume(1)  # Increased from 0.5
        if self.sounds['combo_10x']:
            self.sounds['combo_10x'].set_volume(1)  # Increased from 0.6
        if self.sounds['combo_break']:
            self.sounds['combo_break'].set_volume(1)
        
        # Effects
        if self.sounds['confetti']:
            self.sounds['confetti'].set_volume(1)
    
    def play(self, sound_name):
        """Play a sound effect"""
        if not self.sfx_enabled:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
    
    def play_music(self, music_file, loops=-1, volume=0.3):
        """Play background music"""
        if not self.music_enabled:
            return
        
        try:
            path = os.path.join('assets', 'sounds', music_file)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"Error playing music {music_file}: {e}")
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except:
            pass
    
    def pause_music(self):
        """Pause background music"""
        try:
            pygame.mixer.music.pause()
        except:
            pass
    
    def unpause_music(self):
        """Unpause background music"""
        try:
            pygame.mixer.music.unpause()
        except:
            pass
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
    
    def toggle_sfx(self):
        """Toggle sound effects on/off"""
        self.sfx_enabled = not self.sfx_enabled
