import pygame
import random
import os




#    Bird class for the Flappy Bird game.
class Bird:


    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5


#        Initialize the bird.
    def __init__(self, x=200, y=350):

        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0

        # Improved bird images with better visuals
        self.IMGS = [
            pygame.Surface((50, 35), pygame.SRCALPHA),
            pygame.Surface((50, 35), pygame.SRCALPHA),
            pygame.Surface((50, 35), pygame.SRCALPHA)
        ]

        # Draw more detailed bird shapes
        for i, img in enumerate(self.IMGS):
            # Yellow body (main ellipse)
            pygame.draw.ellipse(img, (255, 255, 0), (0, 0, 50, 35))

            # Wing animation (different wing positions)
            wing_height = 15 - (i * 5)  # Makes the wing move up and down
            pygame.draw.ellipse(img, (240, 240, 0), (10, 20, 20, wing_height))

            # Details
            pygame.draw.circle(img, (255, 255, 255), (40, 15), 8)  # White eye background
            pygame.draw.circle(img, (0, 0, 0), (42, 15), 4)  # Black eye
            pygame.draw.circle(img, (255, 255, 255), (43, 13), 1)  # Eye highlight
            pygame.draw.polygon(img, (255, 69, 0), [(0, 17), (15, 12), (0, 7)])  # Orange beak

            # Add shading
            pygame.draw.ellipse(img, (220, 220, 0), (5, 5, 30, 25), 1)

        # Initialize the image to avoid NoneType error
        self.img = self.IMGS[0]


# Make the bird jump.
    def jump(self):

        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y


# Move the bird based on physics.
    def move(self):

        self.tick_count += 1

        # Calculate displacement
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # Terminal velocity
        if displacement >= 16:
            displacement = 16

        if displacement < 0:
            displacement -= 2

        # Update position
        self.y = self.y + displacement

        # Tilt bird
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL


# Draw the bird on the screen.
    def draw(self, win, rect):

        x, y, width, height = rect
        scale_factor_x = width / 600
        scale_factor_y = height / 800

        # Animation
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # Don't flap when nose diving
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate the image around the center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        # Scale the image for the display rectangle
        scaled_img = pygame.transform.scale(rotated_image,
                                            (int(rotated_image.get_width() * scale_factor_x),
                                             int(rotated_image.get_height() * scale_factor_y)))

        # Scale the position for the display rectangle
        scaled_x = int(x + (self.x * scale_factor_x))
        scaled_y = int(y + (self.y * scale_factor_y))

        # Add shadow for depth effect
        shadow_img = scaled_img.copy()
        shadow_img.fill((20, 20, 20, 100), None, pygame.BLEND_RGBA_MULT)
        win.blit(shadow_img, (scaled_x + 4, scaled_y + 4))

        # Draw the image
        win.blit(scaled_img, (scaled_x, scaled_y))


# Get the mask for collision detection.
    def get_mask(self):

        return pygame.mask.from_surface(self.img)




# Pipe class for the Flappy Bird game.
class Pipe:


    GAP = 200
    VEL = 5


# Initialize the pipe.
    def __init__(self, x):

        self.x = x
        self.height = 0
        self.gap = 200
        self.passed = False

        # Where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        # Create improved pipe surfaces
        self.PIPE_TOP = pygame.Surface((70, 500), pygame.SRCALPHA)
        self.PIPE_BOTTOM = pygame.Surface((70, 500), pygame.SRCALPHA)

        # Draw more detailed pipes
        self._draw_detailed_pipe(self.PIPE_TOP)
        self._draw_detailed_pipe(self.PIPE_BOTTOM, is_top=False)

        # Set the pipe position
        self.set_height()


# Draw a detailed pipe with gradients and highlights.
    def _draw_detailed_pipe(self, surface, is_top=True):

        width = 70
        height = 500

        # Main pipe body (darker green)
        base_color = (0, 150, 0)
        pygame.draw.rect(surface, base_color, (0, 0, width, height))

        # Lighter green side for 3D effect
        highlight_color = (50, 220, 50)
        pygame.draw.rect(surface, highlight_color, (0, 0, 5, height))

        # Darker green side for 3D effect
        shadow_color = (0, 100, 0)
        pygame.draw.rect(surface, shadow_color, (width - 5, 0, 5, height))

        # Pipe cap (thicker part at the end)
        cap_height = 40
        cap_color = (0, 180, 0)
        cap_width = 80
        cap_offset = (width - cap_width) // 2

        if is_top:
            cap_pos = (cap_offset, height - cap_height, cap_width, cap_height)
        else:
            cap_pos = (cap_offset, 0, cap_width, cap_height)

        # Draw the pipe cap
        pygame.draw.rect(surface, cap_color, cap_pos)

        # Add cap details (horizontal lines)
        for i in range(3):
            y_pos = height - cap_height + (10 * i) if is_top else (10 * i)
            pygame.draw.line(surface, shadow_color, (cap_offset, y_pos),
                             (cap_offset + cap_width, y_pos), 2)

        # Add vertical line details on the pipe body
        for i in range(0, width, 20):
            pygame.draw.line(surface, (0, 130, 0), (i, 0), (i, height), 1)


# Set the height of the pipe from the top of the screen.
    def set_height(self):

        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP


# Move the pipe based on velocity.
    def move(self):

        self.x -= self.VEL


# Draw both the top and bottom of the pipe.
    def draw(self, win, rect):

        x, y, width, height = rect
        scale_factor_x = width / 600
        scale_factor_y = height / 800

        # Scale the position for the display rectangle
        scaled_x = int(x + (self.x * scale_factor_x))
        scaled_top_y = int(y + (self.top * scale_factor_y))
        scaled_bottom_y = int(y + (self.bottom * scale_factor_y))

        # Scale the pipes for the display rectangle
        scaled_pipe_width = int(self.PIPE_TOP.get_width() * scale_factor_x)
        scaled_top_height = int(self.PIPE_TOP.get_height() * scale_factor_y)
        scaled_bottom_height = int(self.PIPE_BOTTOM.get_height() * scale_factor_y)

        # Create scaled pipes
        scaled_pipe_top = pygame.transform.scale(self.PIPE_TOP, (scaled_pipe_width, scaled_top_height))
        scaled_pipe_bottom = pygame.transform.scale(self.PIPE_BOTTOM, (scaled_pipe_width, scaled_bottom_height))

        # Add shadow for depth (slight offset)
        shadow_alpha = pygame.Surface((scaled_pipe_width, scaled_top_height), pygame.SRCALPHA)
        shadow_alpha.fill((0, 0, 0, 50))
        win.blit(shadow_alpha, (scaled_x + 5, scaled_top_y))

        shadow_alpha = pygame.Surface((scaled_pipe_width, scaled_bottom_height), pygame.SRCALPHA)
        shadow_alpha.fill((0, 0, 0, 50))
        win.blit(shadow_alpha, (scaled_x + 5, scaled_bottom_y))

        # Draw the pipes
        win.blit(scaled_pipe_top, (scaled_x, scaled_top_y))
        win.blit(scaled_pipe_bottom, (scaled_x, scaled_bottom_y))


# Check if the bird collides with the pipe.
    def collide(self, bird, rect):

        x, y, width, height = rect
        scale_factor_x = width / 600
        scale_factor_y = height / 800

        # Get masks for collision detection
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Offset for masks
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Check for collision
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # Return True if collision
        return b_point or t_point




# Base class for the Flappy Bird game.
class Base:


    VEL = 5
    WIDTH = 600
    IMG = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)


# Initialize the base.
    def __init__(self, y):

        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

        # Draw a more detailed and visually appealing base
        self._create_detailed_base()


# Creates a more detailed base with ground texture and grass
    def _create_detailed_base(self):

        # Base ground color (brown)
        pygame.draw.rect(self.IMG, (139, 69, 19), (0, 0, self.WIDTH, 150))

        # Add ground texture pattern
        for i in range(0, self.WIDTH, 30):
            # Vertical dirt lines
            pygame.draw.line(self.IMG, (120, 60, 15), (i, 0), (i, 150), 1)

        for j in range(0, 150, 20):
            # Horizontal dirt lines
            pygame.draw.line(self.IMG, (160, 82, 45), (0, j), (self.WIDTH, j), 1)

        # Add random small stones
        for _ in range(50):
            stone_x = random.randint(0, self.WIDTH)
            stone_y = random.randint(20, 140)
            stone_size = random.randint(2, 6)
            stone_color = (100 + random.randint(0, 50), 50 + random.randint(0, 30), 10 + random.randint(0, 20))
            pygame.draw.circle(self.IMG, stone_color, (stone_x, stone_y), stone_size)

        # Add grass on top
        for i in range(0, self.WIDTH, 5):
            grass_height = random.randint(5, 12)
            grass_color = (0, 160 + random.randint(0, 40), 0)
            pygame.draw.line(self.IMG, grass_color, (i, 0), (i, grass_height), 2)


# Move the base for scrolling effect.
    def move(self):

        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # If the base is off the screen, reset position
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH


# Draw the base.
    def draw(self, win, rect):

        x, y, width, height = rect
        scale_factor_x = width / 600
        scale_factor_y = height / 800

        # Scale the position for the display rectangle
        scaled_x1 = int(x + (self.x1 * scale_factor_x))
        scaled_x2 = int(x + (self.x2 * scale_factor_x))
        scaled_y = int(y + (self.y * scale_factor_y))

        # Scale the base for the display rectangle
        scaled_width = int(self.WIDTH * scale_factor_x)
        scaled_height = int(self.IMG.get_height() * scale_factor_y)

        # Create scaled bases
        scaled_img = pygame.transform.scale(self.IMG, (scaled_width, scaled_height))

        # Draw the bases
        win.blit(scaled_img, (scaled_x1, scaled_y))
        win.blit(scaled_img, (scaled_x2, scaled_y))




# Cloud class for visual enhancement in the background.
class Cloud:


# Initialize a cloud.
    def __init__(self, x, y, speed, size):

        self.x = x
        self.y = y
        self.speed = speed
        self.size = size

        # Create cloud surface
        self.width = int(100 * size)
        self.height = int(50 * size)
        self.cloud = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw cloud shape
        self._draw_cloud()


# Draw a fluffy cloud shape
    def _draw_cloud(self):

        # Cloud base color
        cloud_color = (250, 250, 250)

        # Draw multiple circles to create cloud shape
        positions = [
            (self.width * 0.3, self.height * 0.5, self.height * 0.5),
            (self.width * 0.5, self.height * 0.3, self.height * 0.6),
            (self.width * 0.7, self.height * 0.5, self.height * 0.5),
            (self.width * 0.5, self.height * 0.6, self.height * 0.4),
            (self.width * 0.2, self.height * 0.5, self.height * 0.3),
            (self.width * 0.8, self.height * 0.5, self.height * 0.3),
        ]

        for x, y, radius in positions:
            pygame.draw.circle(self.cloud, cloud_color, (int(x), int(y)), int(radius))


# Move cloud horizontally
    def move(self):

        self.x -= self.speed


# Draw the cloud.
    def draw(self, win, rect):

        x, y, width, height = rect
        scale_factor_x = width / 600
        scale_factor_y = height / 800

        # Scale position
        scaled_x = int(x + (self.x * scale_factor_x))
        scaled_y = int(y + (self.y * scale_factor_y))

        # Scale cloud
        scaled_width = int(self.width * scale_factor_x)
        scaled_height = int(self.height * scale_factor_y)
        scaled_cloud = pygame.transform.scale(self.cloud, (scaled_width, scaled_height))

        # Draw cloud
        win.blit(scaled_cloud, (scaled_x, scaled_y))


# Check if cloud is off screen and should be removed
    def is_off_screen(self, width):

        return self.x + self.width < 0




# Background class to manage sky gradients, clouds and other visual elements.
class Background:


# Initialize background
    def __init__(self, width, height):

        self.width = width
        self.height = height
        self.clouds = []
        self.cloud_spawn_timer = 0

        # Create sky gradient
        self.sky = self._create_sky_gradient()

        # Add initial clouds
        for _ in range(4):
            self._add_random_cloud()


# Create a gradient sky background
    def _create_sky_gradient(self):

        sky = pygame.Surface((self.width, self.height))

        # Sky colors (from top to bottom)
        top_color = (100, 180, 255)  # Lighter blue at top
        bottom_color = (135, 206, 250)  # Darker blue at bottom

        # Create gradient
        for y in range(self.height):
            # Calculate color for this row
            r = int(top_color[0] * (1 - y / self.height) + bottom_color[0] * (y / self.height))
            g = int(top_color[1] * (1 - y / self.height) + bottom_color[1] * (y / self.height))
            b = int(top_color[2] * (1 - y / self.height) + bottom_color[2] * (y / self.height))

            # Draw horizontal line with this color
            pygame.draw.line(sky, (r, g, b), (0, y), (self.width, y))

        return sky


# Add a cloud with random properties
    def _add_random_cloud(self):

        x = self.width + random.randint(0, 100)
        y = random.randint(50, 300)
        speed = random.uniform(0.2, 0.8)
        size = random.uniform(0.5, 1.5)
        self.clouds.append(Cloud(x, y, speed, size))


# Update background elements
    def update(self):

        # Update cloud timer
        self.cloud_spawn_timer += 1

        # Add new cloud occasionally
        if self.cloud_spawn_timer > 120:  # Every ~2 seconds
            self._add_random_cloud()
            self.cloud_spawn_timer = 0

        # Move clouds and remove if off-screen
        clouds_to_remove = []
        for cloud in self.clouds:
            cloud.move()
            if cloud.is_off_screen(self.width):
                clouds_to_remove.append(cloud)

        for cloud in clouds_to_remove:
            self.clouds.remove(cloud)


# Draw background elements.
    def draw(self, win, rect):

        x, y, width, height = rect

        # Draw sky
        scaled_sky = pygame.transform.scale(self.sky, (width, height))
        win.blit(scaled_sky, (x, y))

        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(win, rect)




# Main game class for Flappy Bird.
class FlappyBird:


# Initialize the game.
    def __init__(self):

        # Game elements
        self.bird = Bird(230, 350)
        self.base = Base(730)
        self.pipes = [Pipe(700)]
        self.score = 0
        self.clock = pygame.time.Clock()
        self.background = Background(600, 800)

        # Font for improved text rendering
        pygame.font.init()  # Make sure font module is initialized
        self.score_font = None
        try:
            self.score_font = pygame.font.Font(None, 50)  # Default font
        except:
            self.score_font = pygame.font.SysFont("Arial", 50)

        self.message_font = None
        try:
            self.message_font = pygame.font.Font(None, 36)
        except:
            self.message_font = pygame.font.SysFont("Arial", 36)

        # Game state
        self.active = True
        self.passed_pipe = False

        # Animation effects
        self.score_animation = 0

        # Sound effects (Demo)
        # try:
        #     pygame.mixer.init()
        #     self.jump_sound = pygame.mixer.Sound("sound/jump.wav")
        #     self.score_sound = pygame.mixer.Sound("sound/score.wav")
        #     self.hit_sound = pygame.mixer.Sound("sound/hit.wav")
        # except:
        #     self.jump_sound = None
        #     self.score_sound = None
        #     self.hit_sound = None


# Update the game state.
    def update(self):

        if not self.active:
            return "dead"

        # Update background
        self.background.update()

        # Move the bird
        self.bird.move()

        # Check for ground collision
        if self.bird.y + self.bird.img.get_height() >= 730 or self.bird.y < 0:
            self.active = False
            # if self.hit_sound:
            #     self.hit_sound.play()
            return "dead"

        # Add a new pipe when needed
        pipe_ind = 0
        if len(self.pipes) > 1 and self.bird.x > self.pipes[0].x + self.pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        # Move the pipes
        add_pipe = False
        pipes_to_remove = []
        for pipe in self.pipes:
            # Check for collision
            if pipe.collide(self.bird, (0, 0, 600, 800)):
                self.active = False
                # if self.hit_sound:
                #     self.hit_sound.play()
                return "dead"

            # Check if pipe is off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                pipes_to_remove.append(pipe)

            # Check if bird passed the pipe
            if not pipe.passed and pipe.x < self.bird.x:
                pipe.passed = True
                add_pipe = True

            # Move the pipe
            pipe.move()

        # Add score and new pipe if bird passed a pipe
        if add_pipe:
            self.score += 1
            self.score_animation = 10  # Start score animation
            # if self.score_sound:
            #     self.score_sound.play()
            self.pipes.append(Pipe(600))

        # Remove pipes that are off the screen
        for pipe in pipes_to_remove:
            self.pipes.remove(pipe)

        # Decrease score animation counter
        if self.score_animation > 0:
            self.score_animation -= 1

        # Move the base
        self.base.move()

        return "alive"


# Draw the game elements on the window.
    def draw(self, win, rect):

        x, y, width, height = rect

        # Draw background with sky and clouds
        self.background.draw(win, rect)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(win, rect)

        # Draw base
        self.base.draw(win, rect)

        # Draw bird
        self.bird.draw(win, rect)

        # Draw score with improved visuals
        if width > 200:  # Only draw score if the display is large enough
            # Score text with shadow
            score_str = str(self.score)

            # Determine font size based on display size
            font_size = int(50 * (width / 600))
            if self.score_font:
                self.score_font = pygame.font.Font(None, font_size)
            else:
                self.score_font = pygame.font.SysFont("Arial", font_size)

            # Dynamic size for score animation effect
            size_boost = self.score_animation / 2
            animated_size = font_size + int(size_boost)

            if self.score_animation > 0:
                # Animated score when player scores a point
                score_font = pygame.font.Font(None, animated_size)
                score_text = score_font.render(score_str, True, (255, 215, 0))  # Gold color
            else:
                # Normal score display
                score_text = self.score_font.render(score_str, True, (255, 255, 255))

            # Add shadow for better visibility
            shadow_text = self.score_font.render(score_str, True, (0, 0, 0))
            shadow_offset = max(2, int(4 * (width / 600)))

            # Center position
            text_x = x + width / 2 - score_text.get_width() / 2
            text_y = y + 50

            # Draw shadow then text
            win.blit(shadow_text, (text_x + shadow_offset, text_y + shadow_offset))
            win.blit(score_text, (text_x, text_y))

        # Draw game over message if game is not active
        if not self.active and width > 200:
            # Game over text
            if self.message_font:
                game_over_text = self.message_font.render("Game Over", True, (200, 30, 30))
                restart_text = self.message_font.render("Press Space to Restart", True, (255, 255, 255))

                # Center position
                go_x = x + width / 2 - game_over_text.get_width() / 2
                go_y = y + height / 3

                restart_x = x + width / 2 - restart_text.get_width() / 2
                restart_y = go_y + 50

                # Draw text with shadow for better visibility
                shadow_go = self.message_font.render("Game Over", True, (0, 0, 0))
                shadow_restart = self.message_font.render("Press Space to Restart", True, (0, 0, 0))

                win.blit(shadow_go, (go_x + 2, go_y + 2))
                win.blit(game_over_text, (go_x, go_y))

                win.blit(shadow_restart, (restart_x + 2, restart_y + 2))
                win.blit(restart_text, (restart_x, restart_y))