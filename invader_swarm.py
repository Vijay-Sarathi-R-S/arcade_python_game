import arcade
import random
import os
import sys
import json
import math
from pathlib import Path

# Helper to make assets work in both normal run and PyInstaller exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Invader Swarm - Enhanced"

PLAYER_SPEED = 5
ALIEN_SPEED_BASE = 1.2
ALIEN_DROP_DISTANCE_BASE = 25
BULLET_SPEED = 7
ALIEN_BULLET_SPEED = 4
PLAYER_BULLET_W = 5
PLAYER_BULLET_H = 15
ALIEN_BULLET_W = 6
ALIEN_BULLET_H = 16

# Target sizes for sprites (will auto-scale)
TARGET_SIZES = {
    'player': (50, 40),
    'enemy': (40, 30),
    'drifter': (20, 15),
    'boss': (80, 80),
    'powerup': (30, 30)
}

# Power-up constants
POWERUP_TYPES = ["shield", "extralife", "spread", "nuke", "rapidfire"]
POWERUP_COLORS = {
    "shield": arcade.color.BLUE,
    "extralife": arcade.color.GREEN,
    "spread": arcade.color.ORANGE,
    "nuke": arcade.color.RED,
    "rapidfire": arcade.color.YELLOW
}

class SmartSprite(arcade.Sprite):
    """Sprite that auto-scales to target size"""
    def __init__(self, path, target_size, fallback_color=None, fallback_size=None):
        try:
            full_path = resource_path(path)
            super().__init__(full_path)
            # Auto-scale to target size
            if self.width > 0 and self.height > 0:
                scale_x = target_size[0] / self.width
                scale_y = target_size[1] / self.height
                self.scale = min(scale_x, scale_y)
        except Exception as e:
            if fallback_color and fallback_size:
                # Create fallback texture
                texture = arcade.make_soft_circle_texture(
                    max(fallback_size), 
                    fallback_color
                )
                super().__init__()
                self.texture = texture
                self.scale = fallback_size[0] / texture.width
            else:
                raise e

class Particle:
    def __init__(self, x, y, dx, dy, color, lifetime):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy -= 0.2
        self.age += 1
    
    def draw(self):
        alpha = int(255 * (1 - self.age / self.lifetime))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        arcade.draw_circle_filled(self.x, self.y, 2, color)

class PowerUp(arcade.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        # Try to load image, fallback to colored circle
        try:
            path = f"assets/images/powerups/{power_type}.png"
            full_path = resource_path(path)
            self.texture = arcade.load_texture(full_path)
            # Auto-scale powerup
            if self.width > 0 and self.height > 0:
                scale = 30 / max(self.width, self.height)
                self.scale = scale
        except:
            self.texture = arcade.make_soft_circle_texture(30, POWERUP_COLORS[power_type])
        
        self.center_x = x
        self.center_y = y
        self.change_y = -2
        self.angle_speed = 2
        
    def update(self, delta_time=1/60):
        self.center_y += self.change_y
        self.angle += self.angle_speed

class Boss(arcade.Sprite):
    def __init__(self, wave):
        print(f"1. Starting Boss init for wave {wave}")

        path = "assets/images/bosses/boss.png"
        full_path = resource_path(path)

        # Proper Sprite init (IMPORTANT FIX)
        super().__init__(full_path, scale=1)


        print("2. Sprite parent init OK")

        # Scale boss
        target_size = TARGET_SIZES['boss'][0] + (wave * 5)
        if self.width > 0 and self.height > 0:
            scale = target_size / max(self.width, self.height)
            self.scale = scale

        # Attributes
        self.wave = wave
        self.health = 50 + wave * 10
        self.max_health = self.health
        self.change_x = 2
        self.shoot_timer = 0
        self.shoot_delay = 30
        self.pattern = 0

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT - 100

        print("3. Boss init complete")
        print(f"4. Boss has draw method? {hasattr(self, 'draw')}")

        
    def draw(self):
        arcade.Sprite.draw(self)

    def update(self):
        self.center_x += self.change_x
        if self.center_x < 100 or self.center_x > SCREEN_WIDTH - 100:
            self.change_x *= -1
        
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot_timer = 0
            self.pattern = (self.pattern + 1) % 3
            return True
        return False
    
    def draw_health_bar(self):
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT - 40
        
        # Draw background bar
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width, bar_y, bar_y + bar_height,
            arcade.color.GRAY
        )
        # Draw health
        health_width = (self.health / self.max_health) * bar_width
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + health_width, bar_y, bar_y + bar_height,
            arcade.color.RED
        )
        # Draw outline
        arcade.draw_lrbt_rectangle_outline(
            bar_x, bar_x + bar_width, bar_y, bar_y + bar_height,
            arcade.color.WHITE, 2
        )

class InvaderSwarm(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.game_over = False
        self.paused = False
        self.screen_shake = 0
        self.high_scores = self.load_high_scores()
        
        # Initialize sound system for MP3
        self.sounds = {}
        self.load_sounds()
        
        self.restart()

    def load_sounds(self):
        """Load MP3 sound files"""
        sound_files = {
            'shoot': 'assets/sounds/shoot.mp3',
            'explosion': 'assets/sounds/explosion.mp3',
            'powerup': 'assets/sounds/powerup.mp3',
            'boss': 'assets/sounds/boss.mp3',
            'gameover': 'assets/sounds/gameover.mp3'
        }
        
        for name, file_path in sound_files.items():
            try:
                full_path = resource_path(file_path)
                if os.path.exists(full_path):
                    self.sounds[name] = arcade.load_sound(full_path)
                    print(f"Loaded sound: {name}")
                else:
                    print(f"Sound file not found: {full_path}")
            except Exception as e:
                print(f"Could not load {name}: {e}")

    def play_sound(self, name, volume=0.5):
        """Play sound with error handling"""
        if name in self.sounds and self.sounds[name]:
            try:
                arcade.play_sound(self.sounds[name], volume)
            except:
                pass

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except:
            return [0, 0, 0, 0, 0]

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def restart(self):
        self.aliens = arcade.SpriteList()
        self.drifters = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.powerups = arcade.SpriteList()
        self.boss_list = arcade.SpriteList()
        self.boss = None
        self.particles = []
        
        self.player_bullets = []
        self.alien_bullets = []
        
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.kills = 0
        self.kills_since_powerup = 0
        self.alien_direction = 1
        
        # Player stats
        self.shield_active = False
        self.shield_duration = 0
        self.spread_shot = False
        self.spread_duration = 0
        self.rapid_fire = False
        self.rapid_timer = 0
        self.score_multiplier = 1
        self.multiplier_timer = 0
        
        # Background
        self.background = None
        self.load_background()
        
        self.setup_player()
        self.setup_aliens()

        self.shoot_cooldown = 0
        self.alien_shoot_timer = 0
        self.alien_shoot_delay = 90

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.fire_pressed = False
        self.game_over = False
        self.boss_wave = False

    def load_background(self):
        """Load random background with flexible sizing"""
        bg_files = [
            "assets/images/backgrounds/background1.png",
            "assets/images/backgrounds/background2.png"
        ]
        bg_file = random.choice(bg_files)
        try:
            full_path = resource_path(bg_file)
            if os.path.exists(full_path):
                self.background = arcade.load_texture(full_path)
                print(f"Loaded background: {bg_file}")
            else:
                print(f"Background not found: {bg_file}")
                self.background = None
        except Exception as e:
            print(f"Failed to load background: {e}")
            self.background = None

    def setup_player(self):
        """Setup player with auto-scaling"""
        try:
            self.player = SmartSprite(
                "assets/images/player/ship.png",
                TARGET_SIZES['player'],
                arcade.color.CYAN,
                TARGET_SIZES['player']
            )
            print("Player loaded and scaled")
        except Exception as e:
            print(f"Failed to load ship.png: {e}")
            self.player = arcade.SpriteSolidColor(
                TARGET_SIZES['player'][0],
                TARGET_SIZES['player'][1],
                arcade.color.CYAN
            )

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 60
        self.player_list.append(self.player)

    def setup_aliens(self):
        """Setup aliens with flexible sizing"""
        self.aliens = arcade.SpriteList()
        self.drifters = arcade.SpriteList()
        
        # Boss wave every 5 waves
        if self.wave % 5 == 0:
            boss = Boss(self.wave)
            self.boss_list.append(boss)
            self.boss = boss
            self.boss_wave = True
            self.play_sound('boss', 0.3)
            return
        
        self.boss_wave = False
        self.boss = None
        
        # Progressive difficulty
        rows = min(5, 3 + self.wave // 2)
        cols = min(11, 8 + self.wave // 3)
        
        enemy_types = ["green", "red", "extra", "alien"]
        for row in range(rows):
            enemy_type = enemy_types[row % len(enemy_types)]
            for col in range(cols):
                try:
                    # Try to load specific enemy sprite
                    path = f"assets/images/enemies/{enemy_type}.png"
                    alien = SmartSprite(
                        path,
                        TARGET_SIZES['enemy'],
                        arcade.color.LIME,
                        TARGET_SIZES['enemy']
                    )
                except:
                    # Fallback to colored rectangle
                    alien = arcade.SpriteSolidColor(
                        TARGET_SIZES['enemy'][0],
                        TARGET_SIZES['enemy'][1],
                        arcade.color.LIME
                    )

                alien.alien_type = enemy_type
                alien.center_x = 40 + col * 65
                alien.center_y = SCREEN_HEIGHT - 80 - row * 35
                
                # Different speeds for different alien types
                if alien.alien_type == "red":
                    alien.change_x_mult = 1.2
                elif alien.alien_type == "extra":
                    alien.change_x_mult = 0.8
                else:
                    alien.change_x_mult = 1.0
                    
                self.aliens.append(alien)

    def create_explosion(self, x, y, color=arcade.color.ORANGE):
        """Create particle explosion effect"""
        for _ in range(20):
            dx = random.uniform(-3, 3)
            dy = random.uniform(-3, 3)
            self.particles.append(Particle(x, y, dx, dy, color, 30))

    def spawn_powerup(self, x, y):
        """Spawn random power-up"""
        if random.random() < 0.2:
            power_type = random.choice(POWERUP_TYPES)
            self.powerups.append(PowerUp(x, y, power_type))

    def shoot(self):
        """Player shooting with spread shot support"""
        if self.spread_shot:
            # Spread shot - 3 bullets
            self.player_bullets.append([self.player.center_x, self.player.center_y + 20])
            self.player_bullets.append([self.player.center_x - 15, self.player.center_y + 20])
            self.player_bullets.append([self.player.center_x + 15, self.player.center_y + 20])
        else:
            self.player_bullets.append([self.player.center_x, self.player.center_y + 20])
        self.play_sound('shoot', 0.2)

    def shoot_alien(self):
        """Alien shooting with patterns"""
        if not self.aliens or self.boss_wave:
            return
        shooter = random.choice(self.aliens)
        
        if shooter.alien_type == "red":
            # Red aliens shoot faster in bursts
            for offset in [-10, 0, 10]:
                self.alien_bullets.append([shooter.center_x + offset, shooter.center_y - 15])
        else:
            self.alien_bullets.append([shooter.center_x, shooter.center_y - 15])

    def handle_alien_death(self, alien):
        """Handle alien destruction with rewards"""
        # First check if the alien is still in the list
        if alien not in self.aliens:
            return
            
        self.create_explosion(alien.center_x, alien.center_y)
        self.play_sound('explosion', 0.3)
        
        # Store alien properties before removal
        alien_type = alien.alien_type
        alien_x = alien.center_x
        alien_y = alien.center_y
        
        # Remove the alien
        self.aliens.remove(alien)
        
        if alien_type == "extra":
            self.score += 50 * self.wave * self.score_multiplier
            self.spawn_powerup(alien_x, alien_y)
            
        elif alien_type == "alien":
            self.spawn_powerup(alien_x, alien_y)
            # Create 2 drifters
            for _ in range(2):
                try:
                    drifter = SmartSprite(
                        "assets/images/enemies/alien.png",
                        TARGET_SIZES['drifter'],
                        arcade.color.MAGENTA,
                        TARGET_SIZES['drifter']
                    )
                except:
                    drifter = arcade.SpriteSolidColor(
                        TARGET_SIZES['drifter'][0],
                        TARGET_SIZES['drifter'][1],
                        arcade.color.MAGENTA
                    )
                
                drifter.alien_type = "drifter"
                drifter.center_x = alien_x + random.uniform(-20, 20)
                drifter.center_y = alien_y + random.uniform(-10, 10)
                drifter.change_x = random.uniform(-1.5, 1.5)
                drifter.change_y = random.uniform(-1.0, -0.5)
                drifter.is_drifter = True
                self.drifters.append(drifter)
                
        elif alien_type in ["green", "red"]:
            if random.random() < 0.1:
                self.spawn_powerup(alien_x, alien_y)

    def handle_drifter_death(self, drifter):
        """Handle drifter destruction"""
        if drifter not in self.drifters:
            return
            
        self.score += 5 * self.wave * self.score_multiplier
        self.create_explosion(drifter.center_x, drifter.center_y, arcade.color.PURPLE)
        self.drifters.remove(drifter)

    def activate_powerup(self, powerup):
        """Activate power-up effects"""
        self.play_sound('powerup', 0.4)
        power_type = powerup.power_type
        
        if power_type == "shield":
            self.shield_active = True
            self.shield_duration = 600
        elif power_type == "extralife":
            self.lives += 1
        elif power_type == "spread":
            self.spread_shot = True
            self.spread_duration = 600
        elif power_type == "nuke":
            # Destroy all enemies
            for alien in self.aliens:
                self.create_explosion(alien.center_x, alien.center_y)
            self.aliens = arcade.SpriteList()
            for drifter in self.drifters:
                self.create_explosion(drifter.center_x, drifter.center_y)
            self.drifters = arcade.SpriteList()
            self.score += 100 * self.wave * self.score_multiplier
        elif power_type == "rapidfire":
            self.rapid_fire = True
            self.rapid_timer = 600
        
        if powerup in self.powerups:
            self.powerups.remove(powerup)

    def rect_collides_sprite(self, rect_cx, rect_cy, rect_w, rect_h, sprite):
        """Rectangle-sprite collision detection"""
        left = rect_cx - rect_w / 2
        right = rect_cx + rect_w / 2
        bottom = rect_cy - rect_h / 2
        top = rect_cy + rect_h / 2
        return (left < sprite.right and right > sprite.left and
                bottom < sprite.top and top > sprite.bottom)

    def on_draw(self):
        """Render the game"""
        # Screen shake effect
        if self.screen_shake > 0:
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
            self.screen_shake -= 1
        else:
            shake_x = shake_y = 0
            
        self.clear()

        # Draw background (stretched to fit screen)
        if self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.XYWH(shake_x, shake_y, SCREEN_WIDTH, SCREEN_HEIGHT)
            )

        # Draw game objects
        self.aliens.draw()
        self.drifters.draw()
        self.powerups.draw()
        self.player_list.draw()
        
        if self.boss_list:
            self.boss_list.draw()
            for boss in self.boss_list:
                boss.draw_health_bar()

        # Draw bullets
        for bx, by in self.player_bullets:
            arcade.draw_lrbt_rectangle_filled(
                bx - PLAYER_BULLET_W/2,
                bx + PLAYER_BULLET_W/2,
                by - PLAYER_BULLET_H/2,
                by + PLAYER_BULLET_H/2,
                arcade.color.WHITE_SMOKE
            )

        for bx, by in self.alien_bullets:
            arcade.draw_lrbt_rectangle_filled(
                bx - ALIEN_BULLET_W/2,
                bx + ALIEN_BULLET_W/2,
                by - ALIEN_BULLET_H/2,
                by + ALIEN_BULLET_H/2,
                arcade.color.RED
            )

        # Draw particles
        for particle in self.particles:
            particle.draw()

        # Draw shield effect
        if self.shield_active:
            arcade.draw_circle_outline(
                self.player.center_x, self.player.center_y,
                35, arcade.color.BLUE, 2
            )

        # Draw UI
        self.draw_ui()
        
        # Game over screen
        if self.game_over:
            self.draw_game_over()

    def draw_ui(self):
        """Draw user interface"""
        # Score and stats
        arcade.draw_text(
            f"Score: {self.score}   Lives: {self.lives}   Wave: {self.wave}   x{self.score_multiplier}",
            10, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 16
        )

        # Active power-ups
        y_offset = SCREEN_HEIGHT - 60
        if self.rapid_fire:
            arcade.draw_text(f"RAPID FIRE: {self.rapid_timer//60}s",
                           10, y_offset, arcade.color.YELLOW, 14)
            y_offset -= 20
        if self.spread_shot:
            arcade.draw_text(f"SPREAD SHOT: {self.spread_duration//60}s",
                           10, y_offset, arcade.color.ORANGE, 14)
            y_offset -= 20
        if self.shield_active:
            arcade.draw_text(f"SHIELD: {self.shield_duration//60}s",
                           10, y_offset, arcade.color.BLUE, 14)

        # High scores
        arcade.draw_text("HIGH SCORES", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30,
                       arcade.color.WHITE, 14)
        for i, score in enumerate(self.high_scores[:5]):
            if score > 0:
                color = arcade.color.YELLOW if score == self.high_scores[0] else arcade.color.WHITE
                arcade.draw_text(f"{i+1}. {score}", SCREEN_WIDTH - 150,
                               SCREEN_HEIGHT - 50 - i * 20, color, 12)

        # Pause text
        if self.paused:
            arcade.draw_text("PAUSED", SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                           arcade.color.WHITE, 40, anchor_x="center")
            arcade.draw_text("Press P to Resume", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50,
                           arcade.color.WHITE, 20, anchor_x="center")

    def draw_game_over(self):
        """Draw game over screen"""
        # Draw semi-transparent overlay
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 200)
        )
        arcade.draw_text("GAME OVER", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50,
                       arcade.color.RED, 40, anchor_x="center")
        arcade.draw_text(f"Final Score: {self.score}   Wave: {self.wave}",
                       SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                       arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Press R to Restart",
                       SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50,
                       arcade.color.GREEN, 20, anchor_x="center")
        arcade.draw_text("Press ESC to Quit",
                       SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80,
                       arcade.color.RED, 16, anchor_x="center")

    def on_update(self, delta_time):
        """Update game logic"""
        if self.game_over or self.paused:
            return

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

        # Update particles
        self.particles = [p for p in self.particles if p.age < p.lifetime]
        for particle in self.particles:
            particle.update()

        # Update power-ups
        self.powerups.update()
        for powerup in self.powerups:
            if powerup.center_y < 0:
                self.powerups.remove(powerup)

        # Player movement
        self.player.change_x = 0
        self.player.change_y = 0
        if self.left_pressed: 
            self.player.change_x = -PLAYER_SPEED
        if self.right_pressed: 
            self.player.change_x = PLAYER_SPEED
        if self.up_pressed: 
            self.player.change_y = PLAYER_SPEED
        if self.down_pressed: 
            self.player.change_y = -PLAYER_SPEED
        self.player.update()

        # Keep player on screen
        self.player.center_x = max(25, min(SCREEN_WIDTH - 25, self.player.center_x))
        self.player.center_y = max(50, min(SCREEN_HEIGHT - 50, self.player.center_y))

        # Shooting
        if self.fire_pressed and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = 8 if self.rapid_fire else 25
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)

        # Power-up timers
        if self.rapid_fire:
            self.rapid_timer -= 1
            if self.rapid_timer <= 0:
                self.rapid_fire = False
        
        if self.spread_shot:
            self.spread_duration -= 1
            if self.spread_duration <= 0:
                self.spread_shot = False
        
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False

        # Score multiplier
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.score_multiplier = 1

        # Boss battle
        if self.boss:
            self.update_boss()

        # Regular alien movement
        if not self.boss_wave:
            self.update_aliens()

        # Move bullets
        for bullet in self.player_bullets[:]:
            bullet[1] += BULLET_SPEED
        
        for bullet in self.alien_bullets[:]:
            bullet[1] -= ALIEN_BULLET_SPEED

        # Handle collisions
        self.handle_collisions()

        # Check wave completion
        self.check_wave_completion()

        # Remove off-screen objects
        self.cleanup_offscreen()

        # Check game over
        if self.lives <= 0:
            self.game_over = True
            self.play_sound('gameover', 0.5)
            # Update high scores
            self.high_scores.append(self.score)
            self.high_scores.sort(reverse=True)
            self.high_scores = self.high_scores[:5]
            self.save_high_scores()

    def update_boss(self):
        """Update boss logic"""
        if self.boss.update():
            # Boss shooting patterns
            if self.boss.pattern == 0:
                # Single shot
                self.alien_bullets.append([self.boss.center_x, self.boss.center_y - 30])
            elif self.boss.pattern == 1:
                # Spread shot
                for angle in range(-45, 46, 15):
                    rad = math.radians(angle)
                    bullet = [self.boss.center_x + math.sin(rad) * 30, 
                             self.boss.center_y - 30 + math.cos(rad) * 10]
                    self.alien_bullets.append(bullet)
            elif self.boss.pattern == 2:
                # Triple shot
                for offset in [-20, 0, 20]:
                    self.alien_bullets.append([self.boss.center_x + offset, 
                                              self.boss.center_y - 30])

    def update_aliens(self):
        """Update regular alien movement"""
        self.aliens.update()
        self.drifters.update()

        edge_hit = False
        current_speed = ALIEN_SPEED_BASE + (self.wave - 1) * 0.3
        
        for alien in self.aliens:
            alien.change_x = current_speed * self.alien_direction * getattr(alien, 'change_x_mult', 1.0)
            if (self.alien_direction > 0 and alien.right >= SCREEN_WIDTH) or \
               (self.alien_direction < 0 and alien.left <= 0):
                edge_hit = True

        if edge_hit:
            self.alien_direction *= -1
            drop_dist = ALIEN_DROP_DISTANCE_BASE + (self.wave - 1) * 2
            for alien in self.aliens:
                alien.center_y -= drop_dist

        # Alien shooting
        if self.aliens:
            self.alien_shoot_delay = max(40, 100 - (self.wave - 1) * 8)
            self.alien_shoot_timer += 1
            if self.alien_shoot_timer >= self.alien_shoot_delay:
                self.shoot_alien()
                self.alien_shoot_timer = 0

    def handle_collisions(self):
        """Handle all collision detection"""
        # Player bullets vs enemies
        bullets_to_remove = set()
        aliens_to_remove = set()
        drifters_to_remove = set()
        
        for bullet in self.player_bullets[:]:
            bullet_removed = False
            
            # Check aliens
            for alien in self.aliens:
                if self.rect_collides_sprite(bullet[0], bullet[1],
                                            PLAYER_BULLET_W, PLAYER_BULLET_H, alien):
                    bullets_to_remove.add(tuple(bullet))
                    aliens_to_remove.add(alien)
                    bullet_removed = True
                    break
            
            # Check drifters if bullet wasn't removed
            if not bullet_removed:
                for drifter in self.drifters:
                    if self.rect_collides_sprite(bullet[0], bullet[1],
                                                PLAYER_BULLET_W, PLAYER_BULLET_H, drifter):
                        bullets_to_remove.add(tuple(bullet))
                        drifters_to_remove.add(drifter)
                        break

        # Process hits
        for bullet in bullets_to_remove:
            bullet_list = [b for b in self.player_bullets if tuple(b) == bullet]
            for b in bullet_list:
                if b in self.player_bullets:
                    self.player_bullets.remove(b)
        
        for alien in aliens_to_remove:
            self.handle_alien_death(alien)
            self.kills += 1
            self.kills_since_powerup += 1
            self.score += 10 * self.wave * self.score_multiplier
            
            # Update score multiplier
            self.score_multiplier = min(4, 1 + self.kills_since_powerup // 10)
            self.multiplier_timer = 180
            
            # Rapid fire power-up
            if self.kills % 20 == 0:
                self.rapid_fire = True
                self.rapid_timer = 300
        
        for drifter in drifters_to_remove:
            self.handle_drifter_death(drifter)
            self.kills += 1
            self.kills_since_powerup += 1
            self.score += 10 * self.wave * self.score_multiplier
            
            # Update score multiplier
            self.score_multiplier = min(4, 1 + self.kills_since_powerup // 10)
            self.multiplier_timer = 180

        # Power-up collisions
        for powerup in self.powerups:
            if arcade.check_for_collision(powerup, self.player):
                self.activate_powerup(powerup)
                break

        # Enemy bullets vs player
        for bullet in self.alien_bullets[:]:
            if self.rect_collides_sprite(bullet[0], bullet[1],
                                        ALIEN_BULLET_W, ALIEN_BULLET_H, self.player):
                if bullet in self.alien_bullets:
                    self.alien_bullets.remove(bullet)
                if not self.shield_active:
                    self.lives -= 1
                    self.screen_shake = 10
                    self.create_explosion(self.player.center_x, self.player.center_y, arcade.color.RED)
                    self.play_sound('explosion', 0.3)
                else:
                    self.create_explosion(bullet[0], bullet[1], arcade.color.BLUE)
                break

        # Player collision with enemies
        if not self.shield_active:
            hit_list = arcade.check_for_collision_with_list(self.player, self.aliens)
            for alien in hit_list:
                if alien in self.aliens:
                    self.handle_alien_death(alien)
                    self.lives -= 1
                    self.screen_shake = 10
                
            drifter_hit_list = arcade.check_for_collision_with_list(self.player, self.drifters)
            for drifter in drifter_hit_list:
                if drifter in self.drifters:
                    self.handle_drifter_death(drifter)
                    self.lives -= 1
                    self.screen_shake = 10

        # Boss collision with player bullets
        if self.boss:
            for bullet in self.player_bullets[:]:
                if self.rect_collides_sprite(bullet[0], bullet[1],
                                            PLAYER_BULLET_W, PLAYER_BULLET_H, self.boss):
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)
                    self.boss.health -= 1
                    self.create_explosion(bullet[0], bullet[1], arcade.color.RED)
                    
                    if self.boss.health <= 0:
                        self.create_explosion(self.boss.center_x, self.boss.center_y, arcade.color.GOLD)
                        self.score += 500 * self.wave * self.score_multiplier
                        self.boss = None
                        self.boss_wave = False
                        self.wave += 1
                        self.setup_aliens()
                    break

    def check_wave_completion(self):
        """Check if wave is cleared"""
        # Check if aliens reached bottom
        for alien in self.aliens:
            if alien.bottom <= 50:
                self.game_over = True
                self.play_sound('gameover', 0.5)
                break

        # Check if wave is cleared
        if len(self.aliens) == 0 and not self.boss_wave:
            self.wave += 1
            self.setup_aliens()
            # Reset alien direction
            self.alien_direction = 1

    def cleanup_offscreen(self):
        """Remove off-screen objects"""
        # Remove off-screen player bullets
        self.player_bullets = [bullet for bullet in self.player_bullets 
                              if bullet[1] < SCREEN_HEIGHT + 50]
        
        # Remove off-screen alien bullets
        self.alien_bullets = [bullet for bullet in self.alien_bullets 
                             if bullet[1] > -50]
        
        # Remove off-screen drifters
        for drifter in self.drifters[:]:
            if (drifter.center_y < -50 or drifter.center_x < -50 or 
                drifter.center_x > SCREEN_WIDTH + 50):
                self.drifters.remove(drifter)

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.SPACE:
            self.fire_pressed = True
        elif key == arcade.key.P:
            if not self.game_over:
                self.paused = not self.paused
        elif key == arcade.key.R:
            if self.game_over:
                self.restart()
        elif key == arcade.key.ESCAPE:
            if self.game_over:
                arcade.close_window()
            else:
                self.game_over = True

    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.SPACE:
            self.fire_pressed = False

def main():
    """Main function"""
    window = InvaderSwarm()
    arcade.run()

if __name__ == "__main__":
    main()