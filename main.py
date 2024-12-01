import arcade
import pathlib
from pyglet.gl import GL_NEAREST
from random import choice, randint
from enum import Enum
from sys import exit
import random
from arcade import Sound

DEBUG = False
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
WINDOW_TITLE = "Jungle Dash"
BACKGROUND_COLOR = (179, 235, 242)
ASSETS_PATH = pathlib.Path(__file__).resolve().parent / "assets"
GROUND_WIDTH = 500
LEVEL_WIDTH_PIXELS = GROUND_WIDTH * ((SCREEN_WIDTH * 4) // GROUND_WIDTH)
ALL_TEXTURES = [
    "monkey",
]
PLAYER_SPEED = 3.0
MAX_CLOUDS = 4
CLOUD_YPOS_MIN = 300
CLOUD_YPOS_MAX = 340
CLOUD_SPEED = -0.4
SPAWN_DISTANCE = SCREEN_WIDTH
BANANA_IMAGE = 'banana.png'
SPECIAL_BANANA_IMAGE = 'special-banana.png'
SHIELD_BANANA_IMAGE = 'shield-banana.png'
BANANA_COLLECTION_SOUND = Sound(":resources:sounds/coin5.wav")
SPECIAL_BANANA_COLLECTION_SOUND = Sound(ASSETS_PATH / "special-banana-collection-sound.wav")
SHIELD_BANANA_COLLECTION_SOUND = Sound(ASSETS_PATH / "shield-banana-collection-sound.wav")
CACTUS_COLLISION_SOUND = Sound(ASSETS_PATH / "cactus-collision-sound.wav")
GAME_OVER_SOUND = Sound(ASSETS_PATH / "game-over-sound.wav")

MonkeyStates = Enum("MonkeyStates", "IDLING RUNNING JUMPING CRASHING SURFING")
GameStates = Enum("GameStates", "PLAYING GAMEOVER")

class JungleDash(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.monkey_state = MonkeyStates.IDLING
        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.set_mouse_visible(True)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.floating_platform_list = arcade.SpriteList()
        self.bananas_list = arcade.SpriteList()
        self.special_bananas_list = arcade.SpriteList()
        self.shield_bananas_list = arcade.SpriteList()
        self.bananas = arcade.SpriteList()
        self.obstacles_list = arcade.SpriteList()

    def setup(self):
        # Reset sprite lists
        self.bananas_list = arcade.SpriteList()
        self.special_bananas_list = arcade.SpriteList()
        self.shield_bananas_list = arcade.SpriteList()
        self.bananas = arcade.SpriteList()
        self.obstacles_list = arcade.SpriteList()
        self.floating_platform_list = arcade.SpriteList()

        self.elapsed_time = 0.0
        self.score = 0
        self.health = 200
        self.health_x = 100
        self.textures = {
            tex: arcade.load_texture(ASSETS_PATH / f"{tex}.png") for tex in ALL_TEXTURES
        }
        self.game_state = GameStates.PLAYING

        # Scene setup

        # Clear sprite lists to ensure a fresh start
        self.scene = arcade.Scene()  # Reset the scene

        # Clouds Setup
        self.clouds_list = arcade.SpriteList()
        for i in range(MAX_CLOUDS):
            cloud_sprite = arcade.Sprite(ASSETS_PATH / "cloud.png")
            cloud_sprite.left = randint(0, SCREEN_WIDTH)
            cloud_sprite.top = randint(CLOUD_YPOS_MIN, CLOUD_YPOS_MAX)
            self.clouds_list.append(cloud_sprite)

        # Horizon setup
        self.horizon_list = arcade.SpriteList()
        for col in range(LEVEL_WIDTH_PIXELS // GROUND_WIDTH):
            horizon_sprite = arcade.Sprite(ASSETS_PATH / f"horizon.png")
            horizon_sprite.left = GROUND_WIDTH * (col - 1)
            horizon_sprite.bottom = 0
            self.horizon_list.append(horizon_sprite)
        self.scene.add_sprite_list("horizon", False, self.horizon_list)

        # Monkey setup
        self.player_sprite_running = [ASSETS_PATH / "monkey.png", ASSETS_PATH / "monkey2.png"]
        self.player_sprite_jumping = ASSETS_PATH / "monkey-jumping.png"
        self.player_sprite_surfing = ASSETS_PATH / "monkey-surfing.png"
        self.player_sprite = arcade.Sprite(self.player_sprite_running[0])
        self.player_sprite.center_x = 200
        self.player_sprite.center_y = 120
        self.player_sprite.texture = self.textures["monkey"]
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)
        self.monkey_state = MonkeyStates.RUNNING
        self.monkey_frame_count = 0
        self.monkey_frame = 0

        # Obstacles setup
        self.obstacles_list = arcade.SpriteList()
        self.add_obstacles(self.player_sprite.center_x + SPAWN_DISTANCE, LEVEL_WIDTH_PIXELS)
        self.scene.add_sprite_list("obstacles", True, self.obstacles_list)

        # Birds setup
        self.birds_list = arcade.SpriteList()
        self.bird_flying = [ASSETS_PATH / f"bird.png", ASSETS_PATH / f"bird2.png"]
        self.add_birds(self.player_sprite.center_x + SPAWN_DISTANCE, LEVEL_WIDTH_PIXELS)
        self.scene.add_sprite_list("birds", True, self.birds_list)

        # Render monkey in front of obstacles
        self.scene.add_sprite("player", self.player_sprite)

        # Bananas setup
        self.bananas_list = arcade.SpriteList()
        self.special_bananas_list = arcade.SpriteList()
        self.shield_bananas_list = arcade.SpriteList()
        self.bananas = arcade.SpriteList()
        self.add_bananas(self.player_sprite.center_x + SPAWN_DISTANCE, LEVEL_WIDTH_PIXELS)
        self.scene.add_sprite_list("bananas", True, self.bananas_list)
        self.scene.add_sprite_list("special_bananas", True, self.special_bananas_list)
        self.scene.add_sprite_list("shield_bananas", True, self.shield_bananas_list)

        # Heart graphic setup
        self.heart = arcade.load_texture(ASSETS_PATH / "heart.png")

        # Timer setup
        self.timer_text = arcade.Text(text="00:00:00", start_x=SCREEN_WIDTH - 200, start_y=SCREEN_HEIGHT - 85, color=arcade.color.BLACK, font_size=20)
        
        self.special_banana_timer = 0.0
        self.special_banana_active = False
        self.shield_banana_timer = 0.0
        self.shield_banana_active = False
        self.floating_platform_broken = False
        
        # Physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, self.horizon_list, gravity_constant=0.4
        )

        # Floating platforms setup
        self.floating_platform_list = arcade.SpriteList()
        self.add_floating_platforms_with_bananas(self.player_sprite.center_x + SPAWN_DISTANCE, LEVEL_WIDTH_PIXELS)
        self.scene.add_sprite_list("floating_platforms", False, self.floating_platform_list)

        # Add bananas to the scene
        self.scene.add_sprite_list("bananas", True, self.bananas_list)
        self.scene.add_sprite_list("special_bananas", True, self.special_bananas_list)
        self.scene.add_sprite_list("shield_bananas", True, self.shield_bananas_list)
        # self.scene.add_sprite_list("obstacles", True, self.obstacles_list)
        # self.scene.add_sprite_list("floating_platforms", False, self.floating_platform_list)
        
    def add_bananas(self, xmin, xmax):
        xpos = xmin
        while xpos < xmax:
            banana_variant= random.choices([BANANA_IMAGE, SPECIAL_BANANA_IMAGE, SHIELD_BANANA_IMAGE], weights=[0.6, 0.2, 0.2])[0]
            if banana_variant == BANANA_IMAGE:
                banana_sprite = arcade.Sprite(ASSETS_PATH / banana_variant)
                banana_sprite.left = xpos
                banana_sprite.bottom = 30
                xpos += banana_sprite.width + randint(200, 300)
                while banana_sprite.collides_with_list(self.obstacles_list):
                    banana_sprite.left = banana_sprite.left - 175
                self.bananas_list.append(banana_sprite)
                self.bananas.append(banana_sprite)
            elif banana_variant == SPECIAL_BANANA_IMAGE:
                special_banana_sprite = arcade.Sprite(ASSETS_PATH / banana_variant)
                special_banana_sprite.left = xpos
                special_banana_sprite.bottom = 30
                xpos += special_banana_sprite.width + randint(200, 300)
                while special_banana_sprite.collides_with_list(self.obstacles_list):
                    special_banana_sprite.left = special_banana_sprite.left - 175
                self.special_bananas_list.append(special_banana_sprite)
                self.bananas.append(special_banana_sprite)
            elif banana_variant == SHIELD_BANANA_IMAGE:
                shield_banana_sprite = arcade.Sprite(ASSETS_PATH / banana_variant)
                shield_banana_sprite.left = xpos
                shield_banana_sprite.bottom = 30
                xpos += shield_banana_sprite.width + randint(200, 300)
                while shield_banana_sprite.collides_with_list(self.obstacles_list):
                    shield_banana_sprite.left = shield_banana_sprite.left - 200
                self.shield_bananas_list.append(shield_banana_sprite)
                self.bananas.append(shield_banana_sprite)

    def add_obstacles(self, xmin, xmax):
        xpos = xmin
        while xpos < xmax:
            variant = choice(["1", "2", "3"])
            obstacle_sprite = arcade.Sprite(ASSETS_PATH / f"jungle-plant-{variant}.png")
            obstacle_sprite.left = xpos
            obstacle_sprite.bottom = 30     
            
            # No overlap with bananas
            while obstacle_sprite.collides_with_list(self.bananas_list):
                obstacle_sprite.left += 50
            xpos += obstacle_sprite.width + randint(300, 400)
            self.obstacles_list.append(obstacle_sprite)

    def add_birds(self, xmin, xmax):
        xpos = xmin
        while xpos < xmax:
            bird_sprite = arcade.Sprite(self.bird_flying[0])
            bird_sprite.left = xpos
            bird_sprite.bottom = randint(300, 400)
            bird_sprite.bird_frame_count = 0
            bird_sprite.bird_frame = 0
            
            # No overlap with floating platforms
            if self.floating_platform_list and any(
                platform.left < bird_sprite.right and platform.right > bird_sprite.left
                for platform in self.floating_platform_list
            ):
                xpos += randint(500, 700)
                continue
            xpos += bird_sprite.width + randint(500, 600)
            self.birds_list.append(bird_sprite)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and self.monkey_state != MonkeyStates.JUMPING:
            self.monkey_state = MonkeyStates.JUMPING
            self.physics_engine.jump(6)
        elif key == arcade.key.UP and self.monkey_state == MonkeyStates.SURFING:
            print('surfing')
            self.player_sprite.change_y = 2
        elif key == arcade.key.DOWN and self.monkey_state == MonkeyStates.SURFING:
            print('surfing')
            self.player_sprite.change_y = -2
        elif key == arcade.key.ESCAPE:
            exit()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.monkey_state = MonkeyStates.RUNNING
            self.player_sprite.hit_box = self.textures["monkey"].hit_box_points
            if self.player_sprite.center_y < 44:
                self.player_sprite.center_y = 44
        if self.game_state == GameStates.GAMEOVER:
            self.setup()

    def calculate_player_speed(self, base_speed, elapsed_time, scaling_factor=0.1):
        return base_speed + (scaling_factor * elapsed_time)

    def add_floating_platforms_with_bananas(self, xmin, xmax):
        xpos = xmin
        while xpos < xmax:
            platform = arcade.Sprite(ASSETS_PATH / "platform.png", scale=0.5)
            platform.left = xpos
            platform.bottom = randint(200, 300)
            platform.is_broken = False
            
            # No overlap with birds
            if any(bird.left < platform.right and bird.right > platform.left for bird in self.birds_list):
                xpos += randint(300, 500)
                continue
            
            # Add bananas on the platform
            num_bananas = randint(1, 2)
            for i in range(num_bananas):
                banana_sprite = arcade.Sprite(ASSETS_PATH / BANANA_IMAGE)
                banana_sprite.center_x = platform.left + i * 150 + 80
                banana_sprite.bottom = platform.top + 10
                self.bananas_list.append(banana_sprite)
            xpos += platform.width + randint(300, 500)
            self.floating_platform_list.append(platform)

    def on_update(self, delta_time):
        if self.game_state == GameStates.GAMEOVER:
            self.player_sprite.change_x = 0
            self.player_sprite.texture = self.textures["monkey"]
            return

        global PLAYER_SPEED
        PLAYER_SPEED = self.calculate_player_speed(2.0, self.elapsed_time, scaling_factor=0.025)

        if self.monkey_state == MonkeyStates.JUMPING or self.monkey_state == MonkeyStates.SURFING:
            if self.monkey_state == MonkeyStates.JUMPING:
                self.player_sprite.texture = arcade.load_texture(self.player_sprite_jumping)
            elif self.monkey_state == MonkeyStates.SURFING:
                self.player_sprite.texture = arcade.load_texture(self.player_sprite_surfing)

            # Check if monkey collides with a floating platform
            for platform in self.floating_platform_list:
                if (
                    self.player_sprite.collides_with_sprite(platform)
                    and self.player_sprite.center_y < platform.center_y
                    and self.player_sprite.change_y > 0
                    and platform.is_broken == False
                ):
                    platform.texture = arcade.load_texture(ASSETS_PATH / 'broken-platform.png')
                    self.player_sprite.top = platform.bottom
                    self.player_sprite.change_y = 0
                    platform.is_broken = True
                    break
                if (
                    self.player_sprite.collides_with_sprite(platform)
                    and self.player_sprite.center_y < platform.center_y
                    and self.player_sprite.change_y > 0
                    and platform.is_broken == True
                ):
                    print('here')
                    platform.remove_from_sprite_lists()
                    break

        elif self.monkey_state == MonkeyStates.RUNNING:
            self.monkey_frame_count += 1
            if self.monkey_frame_count >= 10:
                self.monkey_frame_count = 0
                self.monkey_frame = (self.monkey_frame + 1) % len(self.player_sprite_running)
                self.player_sprite.texture = arcade.load_texture(self.player_sprite_running[self.monkey_frame])

        # Ensure that monkey dosen't go off screen
        if self.player_sprite.top > SCREEN_HEIGHT:
            self.player_sprite.top = SCREEN_HEIGHT

        self.player_sprite.update()
        self.player_list.update()
        self.physics_engine.update()

        # Check if monkey lands on a floating platform
        platforms_hit = self.player_sprite.collides_with_list(self.floating_platform_list)
        if platforms_hit:
            platform = platforms_hit[0]
            if self.player_sprite.center_y > platform.top:
                self.player_sprite.bottom = platform.top
                self.player_sprite.change_y = 0
                self.monkey_state = MonkeyStates.RUNNING
        else:
            self.physics_engine.gravity_constant = 0.4

        last_platform_x = max((platform.right for platform in self.floating_platform_list), default=0)
        if last_platform_x < self.player_sprite.center_x + SPAWN_DISTANCE:
            self.add_floating_platforms_with_bananas(last_platform_x + SPAWN_DISTANCE, last_platform_x + 2 * SPAWN_DISTANCE)

        # Bird animation
        for bird in self.birds_list:
            bird.bird_frame_count += 1
            if bird.bird_frame_count >= 10:
                bird.bird_frame_count = 0
                bird.bird_frame = (bird.bird_frame + 1) % len(self.bird_flying)
                bird.texture = arcade.load_texture(self.bird_flying[bird.bird_frame])

        # Update horizon and camera with new PLAYER_SPEED
        self.player_sprite.change_x = PLAYER_SPEED
        self.camera_sprites.move((self.player_sprite.left - 30, 0))

        # Handle timer
        self.elapsed_time += delta_time
        minutes = int(self.elapsed_time) / 60
        seconds = int(self.elapsed_time) % 60
        milliseconds = int((self.elapsed_time - seconds) * 100)
        self.timer_text.text = f"Timer: {int(minutes)}:{seconds}:{milliseconds}"

        # Move clouds
        for cloud in self.clouds_list:
            cloud.center_x += CLOUD_SPEED
            if cloud.right < 0:
                cloud.left = SCREEN_WIDTH + randint(0, SCREEN_WIDTH // 2)
                cloud.top = randint(CLOUD_YPOS_MIN, CLOUD_YPOS_MAX)

        # Check for collisions with bananas, special bananas, and shield bananas
        for special_banana in self.special_bananas_list:
            if self.player_sprite.collides_with_sprite(special_banana):
                arcade.play_sound(SPECIAL_BANANA_COLLECTION_SOUND, 1.0, -1, False)
                self.special_banana_active = True
                self.special_banana_timer = 5.0
                special_banana.remove_from_sprite_lists()

        for shield_banana in self.shield_bananas_list:
            if self.player_sprite.collides_with_sprite(shield_banana):
                arcade.play_sound(SHIELD_BANANA_COLLECTION_SOUND, 1.0, -1, False)
                self.shield_banana_active = True
                self.shield_banana_timer = 5.0
                shield_banana.remove_from_sprite_lists()

        for banana in self.bananas_list:
            if self.player_sprite.collides_with_sprite(banana):
                arcade.play_sound(BANANA_COLLECTION_SOUND, 1.0, -1, False)
                if self.special_banana_active:
                    self.score += 20
                    if self.health < 200:
                        self.health += 12 
                        self.health_x += 6
                else:
                    self.score += 10
                    if self.health < 200:
                        self.health += 6 
                        self.health_x += 3
                banana.remove_from_sprite_lists()
        
        if self.special_banana_active and not self.shield_banana_active:
            self.player_sprite_running = [ASSETS_PATH / "special-monkey.png", ASSETS_PATH / "special-monkey2.png"]
            self.player_sprite_jumping = ASSETS_PATH / "special-monkey-jumping.png"
            self.player_sprite_surfing = ASSETS_PATH / "special-monkey-surfing.png"
            self.monkey_state = MonkeyStates.SURFING
            self.physics_engine.gravity_constant = 0
            self.special_banana_timer -= delta_time 
            if self.special_banana_timer <= 0:
                self.special_banana_active = False 
                self.physics_engine.gravity_constant = 0.4 
                self.monkey_state = MonkeyStates.RUNNING      
        elif self.shield_banana_active and not self.special_banana_active:
            self.player_sprite_running = [ASSETS_PATH / "shield-monkey.png", ASSETS_PATH / "shield-monkey2.png"]
            self.player_sprite_jumping = ASSETS_PATH / "shield-monkey-jumping.png"
            self.shield_banana_timer -= delta_time
            if self.shield_banana_timer <= 0:
                self.shield_banana_active = False
        elif self.shield_banana_active and self.special_banana_active:
            self.player_sprite_running = [ASSETS_PATH / "special-shield-monkey.png", ASSETS_PATH / "special-shield-monkey2.png"]
            self.player_sprite_jumping = ASSETS_PATH / "special-shield-monkey-jumping.png"
            self.player_sprite_surfing = ASSETS_PATH / "special-shield-monkey-surfing.png"
            self.monkey_state = MonkeyStates.SURFING
            self.physics_engine.gravity_constant = 0
            self.shield_banana_timer -= delta_time
            self.special_banana_timer -= delta_time
            if self.shield_banana_timer <= 0:
                self.shield_banana_active = False
            if self.special_banana_timer <= 0:
                self.special_banana_active = False
                self.monkey_state = MonkeyStates.RUNNING
                self.physics_engine.gravity_constant = 0.4
        else:
            self.player_sprite_running = [ASSETS_PATH / "monkey.png", ASSETS_PATH / "monkey2.png"]
            self.player_sprite_jumping = ASSETS_PATH / "monkey-jumping.png"

        # Spawn new bananas relative to the monkey
        last_banana_x = max(banana.right for banana in self.bananas_list)
        if last_banana_x < self.player_sprite.center_x + SPAWN_DISTANCE:
            self.add_bananas(last_banana_x + SPAWN_DISTANCE, last_banana_x + 2 * SPAWN_DISTANCE)

        # Check for collisions with obstacles
        collisions = self.player_sprite.collides_with_list(self.obstacles_list)
        for collision in collisions:
            if not self.shield_banana_active:
                arcade.play_sound(CACTUS_COLLISION_SOUND,1.0,-1,False)
                self.monkey_state = MonkeyStates.CRASHING
                collision.remove_from_sprite_lists()
                self.health -= 40  # Decrease health on collision with obstacle
                self.health_x -= 20
                if self.health <= 0:
                    self.game_state = GameStates.GAMEOVER  # End game if health is gone
                self.monkey_state = MonkeyStates.RUNNING
            self.monkey_state = MonkeyStates.RUNNING

        # Spawn new obstacles relative to the monkey
        last_obstacle_x = max(obstacle.right for obstacle in self.obstacles_list)
        if last_obstacle_x < self.player_sprite.center_x + SPAWN_DISTANCE:
            self.add_obstacles(last_obstacle_x + SPAWN_DISTANCE, last_obstacle_x + 2 * SPAWN_DISTANCE)

        # Check for collisions with birds
        collisions = self.player_sprite.collides_with_list(self.birds_list)
        for collision in collisions:
            if not self.shield_banana_active:
                arcade.play_sound(CACTUS_COLLISION_SOUND,1.0,-1,False)
                self.monkey_state = MonkeyStates.CRASHING
                collision.remove_from_sprite_lists()
                self.health -= 40 
                self.health_x -= 20
                if self.health <= 0:
                    self.game_state = GameStates.GAMEOVER 
                self.monkey_state = MonkeyStates.RUNNING
            self.monkey_state = MonkeyStates.RUNNING
	
        # Check if bird list is empty and add birds if necessary
        if len(self.birds_list) == 0:
            self.add_birds(self.player_sprite.center_x + SPAWN_DISTANCE, self.player_sprite.center_x + 2 * SPAWN_DISTANCE)

        # Spawn new birds relative to the monkey
        last_bird_x = max((bird.right for bird in self.birds_list), default=0)
        if last_bird_x < self.player_sprite.center_x + SPAWN_DISTANCE or len(self.birds_list) < 3:
            self.add_birds(last_bird_x + SPAWN_DISTANCE, last_bird_x + 2 * SPAWN_DISTANCE)
        
        for bird in self.birds_list:
            if bird.right < 0:
                bird.left = max(self.player_sprite.center_x + SPAWN_DISTANCE, bird.left + SCREEN_WIDTH)

        # Continuous horizon handling
        first_horizon_segment = self.horizon_list[0]       
        if first_horizon_segment.right < self.camera_sprites.goal_position[0]:
            last_horizon_segment = self.horizon_list[-1]
            first_horizon_segment.left = last_horizon_segment.right
            self.horizon_list.pop(0)
            self.horizon_list.append(first_horizon_segment)

        # Set textures based on the state
        self.player_sprite.change_x = PLAYER_SPEED
        self.camera_sprites.move((self.player_sprite.left - 30, 0))

        if self.game_state == GameStates.GAMEOVER:
            arcade.play_sound(GAME_OVER_SOUND, 1.0, -1, False)

        # Continuous spawning of floating platforms
        last_platform_x = max((platform.right for platform in self.floating_platform_list), default=0)
        if last_platform_x < self.player_sprite.center_x + SPAWN_DISTANCE:
            self.add_floating_platforms_with_bananas(last_platform_x + SPAWN_DISTANCE, last_platform_x + 2 * SPAWN_DISTANCE)

    def on_draw(self):
        arcade.start_render()
        self.camera_gui.use()
        self.clouds_list.draw(filter=GL_NEAREST)
        self.camera_sprites.use()
        self.scene.draw(filter=GL_NEAREST)
        self.camera_gui.use()
        self.timer_text.draw()
        self.bananas_list.draw()
        
        arcade.draw_texture_rectangle(28, SCREEN_HEIGHT - 30, self.heart.width, self.heart.height, self.heart)

        # Draw score
        arcade.draw_text(f"Score: {self.score:05}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, arcade.color.BLACK, 20)

        # Draw health bar
        arcade.draw_rectangle_filled(self.health_x + 50, SCREEN_HEIGHT - 30, self.health, 20, arcade.color.GREEN)
        arcade.draw_rectangle_outline(150, SCREEN_HEIGHT - 30, 200, 20, arcade.color.BLACK, 2)

        # Draw Game Over text if health reaches zero
        if self.game_state == GameStates.GAMEOVER:
            arcade.draw_text("G A M E   O V E R", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, arcade.color.BLACK, 30, anchor_x="center")
            arcade.draw_text("press the space bar to restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, arcade.color.BLACK, 15, anchor_x="center")
            arcade.draw_rectangle_filled(self.health_x + 50, SCREEN_HEIGHT - 30, self.health, 20, (179, 235, 242))
        else:
            arcade.draw_rectangle_filled(self.health_x + 50, SCREEN_HEIGHT - 30, self.health, 20, arcade.color.GREEN)

def main():
    window = JungleDash(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    window.setup()
    arcade.run()

main()