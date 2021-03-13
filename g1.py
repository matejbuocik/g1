# Import pygame and colors module
import pygame, colors
from pygame.locals import *

# Import random's randint function
from random import randint  



# Define constants for screen width and height
S_WIDTH = 800
S_HEIGHT = 600


# Define a player class by extending pygame.sprite.Sprite
# The surface drawn on the screen is now attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("player.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.vel = 10 # player's velocity
        self.cooldown = 400 # cooldown between shots
        self.last = pygame.time.get_ticks() # time of last shot

    def update(self, pressed_keys):
        # Move the sprite based on user keypress
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            self.rect.move_ip(0, -self.vel)
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            self.rect.move_ip(0, self.vel)
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.rect.move_ip(self.vel, 0)
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.rect.move_ip(-self.vel, 0)

        # Keep the player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > S_WIDTH:
            self.rect.right = S_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > S_HEIGHT:
            self.rect.bottom = S_HEIGHT

    def shoot(self):
        now = pygame.time.get_ticks() # time right now
        # If now - last is bigger than cooldown, the player can shoot
        if now - self.last >= self.cooldown:
            # Create a shot sprite
            # Set x and y of shot to start straight from the player's plane
            new_shot = Shot(self.rect.right, self.rect.midright) 
            # Add to sprite groups
            shots.add(new_shot)
            allSprites.add(new_shot)
            # Change last to now
            self.last = now


# Class of Shots
class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surf = pygame.Surface((15, 12)) # size of surf
        self.surf.fill(colors.BLACK)
        self.rect = self.surf.get_rect(left = x, midleft = y) # start straight from the plane
        self.vel = 15 # velocity of shot

    def update(self, infoscreen):
        self.rect.move_ip(self.vel, 0)
        if self.rect.left > S_WIDTH:
            self.kill()

        collidedWith = pygame.sprite.spritecollideany(self, enemies)
        # Check if collided with any enemy sprite
        # If True kill self and kill the enemy
        if collidedWith:
            self.kill() 
            collidedWith.kill()
            # Add 1 to infoscreen kill count
            infoscreen.killCount()


# Class of enemy rockets
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load('enemy.png').convert_alpha()
        # Starting position is randomly generated
        self.rect = self.surf.get_rect(
            center = (
                randint(S_WIDTH + 20, S_WIDTH + 100),
                randint(0, S_HEIGHT)
            )
        )
        # Velocity is randomly generated
        self.vel = randint(5,20)

    def update(self):
        self.rect.move_ip(-self.vel, 0)
        if self.rect.right < 0:
            self.kill()


# Class of random clouds
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load('cloud.png').convert_alpha()
        # Random beginning position
        self.rect = self.surf.get_rect(
            center = (
                randint(S_WIDTH+20, S_WIDTH+100), # behind the right end of screen
                randint(0, S_HEIGHT)
            )
        )
        # Clouds' velocity
        self.vel = 5
    
    def update(self):
        self.rect.move_ip(-self.vel, 0)
        if self.rect.right < 0:
            self.kill()


# Class for on-screen information
class ScreenInfo:
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font('freesansbold.ttf', 55) # New font object
        self.start_time = pygame.time.get_ticks() # Start of the game time
        self.stopwatch = 0 # Time since the start
        self.kills = 0 # Kills
        self.updateKill = False # Update kill count on screen?
        self.updateTime = False # Update time on the screen?
        self.score = 0 # Score
        
        # Create surface for timer in the beginning
        self.surf0 = self.font.render(str(self.stopwatch), True, colors.WHITE) # Text surface, antialiasing True
        self.rect0 = self.surf0.get_rect(bottomleft = (10, S_HEIGHT - 10))

        # Create surface for kills in the beginning
        self.surf1 = self.font.render(str(self.kills), True, colors.RED) # Text surface, antialiasing True
        self.rect1 = self.surf1.get_rect(bottomright = (S_WIDTH - 10, S_HEIGHT - 10))

    def timer(self):
        time = int((pygame.time.get_ticks() - self.start_time) / 1000) # time in whole seconds
        if time % 1 == 0: # Update time every second
            self.stopwatch = time
            self.updateTime = True

    def killCount(self): # Update on-screen kill count
        self.kills += 1
        self.updateKill = True
    
    def update(self):
        self.timer()
        self.score = self.kills + .2 * self.stopwatch # Calculate the score

        # Timer surface
        if self.updateTime:
            self.surf0 = self.font.render(str(self.stopwatch), True, colors.WHITE) # Text surface, antialiasing True
            self.rect0 = self.surf0.get_rect(bottomleft = (10, S_HEIGHT - 10))
            self.updateTime = False

        # Kill count surface
        if self.updateKill:
            self.surf1 = self.font.render(str(self.kills), True, colors.RED) # Text surface, antialiasing True
            self.rect1 = self.surf1.get_rect(bottomright = (S_WIDTH - 10, S_HEIGHT - 10))
            self.updateKill = False

# Initialize pygame
pygame.init()

# Create the screen object
# The size is determined by constants - S_WIDTH and S_HEIGHT
screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))

# Create a custom event for adding new enemies
# Set a timer for creating enemies
# Can be set outside the mainloop
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
# Event for adding clouds
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1000)

# Set screen caption
pygame.display.set_caption('g1')

# Instantiate player. Right now, this is just a rectangle
player = Player()

# Instantiate screen info
screenInfo = ScreenInfo()

# Create groups to hold enemy sprites, cloud sprites and all sprites
# - enemies is used for collision detection and position updates
# - shots is used for collision detection and position updates
# - clouds is used for position updates
# - allSprites is used for rendering
enemies = pygame.sprite.Group()
shots = pygame.sprite.Group()
allSprites = pygame.sprite.Group()
clouds = pygame.sprite.Group()
allSprites.add(player)


# Variable to keep the main loop running
running = True

# Setup the clock
FPSCLOCK = pygame.time.Clock()
# Set FPS
FPS = 40

# Main loop 
while running:

    # for loop through the event queue
    for event in pygame.event.get():
        # Check for QUIT event. If QUIT, then set running to False
        if event.type == QUIT:
            running = False
        # Check for KEYDOWN
        elif event.type == KEYDOWN:
            # ESCAPE pressed. If True, set running to False
            if event.key == K_ESCAPE:
                running = False
            # SPACE pressed. If True, the player shoots
            elif event.key == K_SPACE:
                player.shoot()

        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create a new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            allSprites.add(new_enemy)

        # Add a new cloud?
        elif event.type == ADDCLOUD:
            # Create a new cloud and add it to sprite groups
            new_cloud = Cloud()
            clouds.add(new_cloud)
            allSprites.add(new_cloud)

    # Get the set of keys pressed and check for user input
    # Update the player sprite based on user keypress
    keys = pygame.key.get_pressed()
    player.update(keys)
    
    # Update the position of enemies, shots and clouds
    enemies.update()
    shots.update(screenInfo)
    clouds.update()

    # Update the info screen
    screenInfo.update()

    # Fill the screen with sky blue
    screen.fill(colors.SKY)

    # Draw the screen information
    screen.blit(screenInfo.surf0, screenInfo.rect0)
    screen.blit(screenInfo.surf1, screenInfo.rect1)

    # Draw all sprites
    for entity in allSprites:
        screen.blit(entity.surf, entity.rect)

    # Check if any enemies have collided with the player
    if pygame.sprite.spritecollideany(player, enemies):
        # If so, then remove the player and stop the loop
        player.kill()
        running = False

    # Update the display
    pygame.display.update()  

    # Tick the clock
    # Ensure the program mantains a constant FPS
    FPSCLOCK.tick(FPS)

# Deinitialize the pygame
pygame.quit()