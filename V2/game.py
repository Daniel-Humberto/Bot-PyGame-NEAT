import pygame
import random
import os



# Bird class for the Flappy Bird game.
class Bird:
    

    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5


    # Initialize the bird.
    def __init__(self, x=200, y=350):
        
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0

        # Load images
        self.IMGS = [
            pygame.Surface((50, 35), pygame.SRCALPHA),
            pygame.Surface((50, 35), pygame.SRCALPHA),
            pygame.Surface((50, 35), pygame.SRCALPHA)
        ]

        # Draw simple bird shapes on the surfaces
        for img in self.IMGS:
            pygame.draw.ellipse(img, (255, 255, 0), (0, 0, 50, 35))  # Yellow body
            pygame.draw.circle(img, (0, 0, 0), (40, 15), 5)  # Eye
            pygame.draw.polygon(img, (255, 0, 0), [(0, 17), (15, 10), (0, 3)])  # Beak

        # Initialize the image to avoid NoneType error
        self.img = self.IMGS[0]


    # Make the bird jump.
    def jump(self):
        """
        
        """
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

        # Create simple pipe surfaces
        self.PIPE_TOP = pygame.Surface((70, 500), pygame.SRCALPHA)
        self.PIPE_BOTTOM = pygame.Surface((70, 500), pygame.SRCALPHA)

        # Draw the pipes
        pygame.draw.rect(self.PIPE_TOP, (0, 255, 0), (0, 0, 70, 500))
        pygame.draw.rect(self.PIPE_BOTTOM, (0, 255, 0), (0, 0, 70, 500))

        # Set the pipe position
        self.set_height()


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

        # Draw the base
        pygame.draw.rect(self.IMG, (165, 42, 42), (0, 0, self.WIDTH, 150))
        for i in range(0, self.WIDTH, 30):
            pygame.draw.line(self.IMG, (139, 69, 19), (i, 0), (i, 10), 3)


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

        # Game state
        self.active = True
        self.passed_pipe = False


    # Update the game state.
    def update(self):
        if not self.active:
            return "dead"

        # Move the bird
        self.bird.move()

        # Check for ground collision
        if self.bird.y + self.bird.img.get_height() >= 730 or self.bird.y < 0:
            self.active = False
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
            self.pipes.append(Pipe(600))

        # Remove pipes that are off the screen
        for pipe in pipes_to_remove:
            self.pipes.remove(pipe)

        # Move the base
        self.base.move()

        return "alive"


    # Draw the game elements on the window.
    def draw(self, win, rect):
        x, y, width, height = rect

        # Draw background
        pygame.draw.rect(win, (135, 206, 235), (x, y, width, height))

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(win, rect)

        # Draw base
        self.base.draw(win, rect)

        # Draw bird
        self.bird.draw(win, rect)

        # Draw score
        if width > 200:  # Only draw score if the display is large enough
            font = pygame.font.SysFont("comicsans", int(30 * (width / 600)))
            text = font.render(str(self.score), 1, (255, 255, 255))
            win.blit(text, (x + width / 2 - text.get_width() / 2, y + 100))