# Based on https://realpython.com/pygame-a-primer/

# Import pygame and colors module
import pygame, colors
# Import sys module for exiting game
import sys
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
        self.surf = playerSprite
        self.rect = self.surf.get_rect()
        self.vel = 10 # player's velocity
        self.cooldown = 400 # cooldown between shots
        self.last = pygame.time.get_ticks() # time of last shot
        self.lives = 3 # player's lives
        self.kills = 0 # player's kills

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
            new_shot = Shot(self.rect.midright) 
            # Add to sprite groups
            shots.add(new_shot)
            allSprites.add(new_shot)
            # Change last to now
            self.last = now

    # Update player's and on-screen kills
    def killCount(self):
        self.kills += 1
        screenInfo.killCount(self.kills)

    # Update player's and on-screen lives
    def lifeCount(self):
        self.lives -= 1
        screenInfo.lifeCount(self.lives)


# Class of Shots
class Shot(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.Surface((15, 12)) # size of surf
        self.surf.fill(colors.BLACK)
        self.rect = self.surf.get_rect(midright = pos) # start straight from the plane
        self.vel = 15 # velocity of shot

    def update(self):
        self.rect.move_ip(self.vel, 0)
        if self.rect.left > S_WIDTH:
            self.kill()

        collidedWith = pygame.sprite.spritecollideany(self, enemies)
        # Check if collided with any enemy sprite
        # If True kill self and kill the enemy
        if collidedWith:
            self.kill() 
            collidedWith.kill()
            # Add 1 to player's kill count
            player.killCount()
            # Make a BOOM
            newExplosion = Explosion(self.rect.midright)
            explosions.add(newExplosion)
            allSprites.add(newExplosion)
            # Play boom1 sound
            boomSound1.play()


# Class for Explosions
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.sprites = boomSprites
        # Starting sprite
        self.sprite = 0
        self.surf = self.sprites[self.sprite]
        self.rect = self.surf.get_rect(center = pos)
        # Velocity of spreading
        self.vel = 1

    def update(self):
        # Make a boom
        self.sprite += self.vel
        if self.sprite >= len(self.sprites) - 1:
            self.kill()
        self.surf = self.sprites[int(self.sprite)]
        self.rect = self.surf.get_rect(center = self.pos)


# Class of enemy rockets
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = enemySprite
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
        self.surf = cloudSprite
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


# Class of flying bonuses
class Bonus(pygame.sprite.Sprite):
    pass

# Class for on-screen information
class ScreenInfo:
    def __init__(self):
        super().__init__()
        self.font = font
        self.start_time = pygame.time.get_ticks() # Start of the game time
        self.stopwatch = 0 # Time since the start of the game

        # Create surface for timer in the beginning
        self.surf0 = self.font.render(str(self.stopwatch), True, colors.WHITE) # Text surface, antialiasing True
        self.rect0 = self.surf0.get_rect(bottomleft = (10, S_HEIGHT - 10))

        # Create surface for kills in the beginning
        self.surf1 = self.font.render(str(player.kills), True, colors.RED) # Text surface, antialiasing True
        self.rect1 = self.surf1.get_rect(bottomright = (S_WIDTH - 10, S_HEIGHT - 10))

        # Create surface for lives in the beginning
        self.heartSurf = heartSprite
        self.heartRects = []
        # Create corresponding rectangles
        for i in range(player.lives):
            self.heartRects.append( self.heartSurf.get_rect(right = S_WIDTH - 100 - i * (heartSpriteWidth + 10), bottom = S_HEIGHT - 20 ) )

        # All sprites and rects for rendering purposes (lazy coder)
        self.all = [(self.surf0, self.rect0), (self.surf1, self.rect1)]

    def timer(self):
        time = int((pygame.time.get_ticks() - self.start_time) / 1000) # time in whole seconds
        if time % 1 == 0: # Update time every second
            self.stopwatch = time
            # Timer surface
            self.surf0 = self.font.render(str(self.stopwatch), True, colors.WHITE) # Text surface, antialiasing True
            self.rect0 = self.surf0.get_rect(bottomleft = (10, S_HEIGHT - 10))
            self.all[0] = (self.surf0, self.rect0)

    def killCount(self, kills): # Update on-screen kill count
        # Kill count surface
        self.surf1 = self.font.render(str(kills), True, colors.RED) # Text surface, antialiasing True
        self.rect1 = self.surf1.get_rect(bottomright = (S_WIDTH - 10, S_HEIGHT - 10))
        self.all[1] = (self.surf1, self.rect1)
    
    def lifeCount(self, lives): # Update on-screen lives count
        # if player's lives are smaller than on-screen lives, then remove them from screen
        if lives < len(self.heartRects):
            self.heartRects.pop(-1)
        # if player's lives are bigger than on-screen, then add them
        else:
            # How many lives to add
            for i in range(lives - len(self.heartRects)):
                # Make a rectangle 
                rect = self.heartSurf.get_rect(
                    right = S_WIDTH - 100 - len(self.heartRects) * (heartSpriteWidth + 10) - i * (heartSpriteWidth + 10), 
                    bottom = S_HEIGHT - 20 
                )
                # Add it to heartRects (show it on screen)
                self.heartRects.append(rect)

    # Reset life count when starting new game
    def lifeCountReset(self):
        for i in range(player.lives):
            self.heartRects.append( self.heartSurf.get_rect(right = S_WIDTH - 100 - i * (heartSpriteWidth + 10), bottom = S_HEIGHT - 20 ) )



# Main menu loop
def menu():
    # Texts and their rects
    t1 = font.render('PLAY', True, colors.WHITE)
    t11 = font.render('PLAY', True, colors.RED)
    activet1 = t1

    t2 = font.render('QUIT', True, colors.WHITE)
    t22 = font.render('QUIT', True, colors.RED)
    activet2 = t2

    r1 = t1.get_rect(center = (S_WIDTH//2, S_HEIGHT//2 - 50))
    r2 = t2.get_rect(center = (S_WIDTH//2, S_HEIGHT//2 + 50))

    mousePos = (0,0)
    mouseClicked = False

    # Used to play button sound only once
    playSound1 = True
    playSound2 = True

    # Menu loop
    runMenu = True
    while runMenu:
        # Reset mouse clicked
        mouseClicked = False

        # Event check
        for event in pygame.event.get():
            e = eventCheck(event)

            if e == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEMOTION:
                mousePos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                mousePos = event.pos
                mouseClicked = True
            
        # Start button
        if r1.collidepoint(mousePos):
            # Change color
            activet1 = t11
            # Play button sound only once
            if playSound1:
                buttonSound.play()
                playSound1 = False
            # If clicked, run the game
            if mouseClicked:
                runMenu = False
                startSound.play()
        else:
            activet1 = t1
            # Reset playsound
            playSound1 = True
        # Quit button
        if r2.collidepoint(mousePos):
            # Change color
            activet2 = t22
            # Play button sound only once
            if playSound2:
                buttonSound.play()
                playSound2 = False
            # If clicked, exit
            if mouseClicked:
                pygame.quit()
                sys.exit()
        else:
            activet2 = t2
            # Reset playsound
            playSound2 = True

        # Update enemies and clouds 
        clouds.update()
        enemies.update()

        # Fill the screen
        screen.fill(colors.SKY)

        # Render enemies and clouds
        for entity in allSprites:
            screen.blit(entity.surf, entity.rect)

        # Render text
        screen.blit(activet1, r1)
        screen.blit(activet2, r2)

        # Update display
        pygame.display.update()
        # Tick the clock
        FPSCLOCK.tick(FPS)


# Event checking function
def eventCheck(event):
    # Check for QUIT event. If QUIT, then set running to False
    if event.type == QUIT:
        return QUIT
    # Check for KEYDOWN
    elif event.type == KEYDOWN:
        # ESCAPE pressed. If True, set running to False
        if event.key == K_ESCAPE:
            return QUIT
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


# Initialize pygame
pygame.init()


# Create the screen object
# The size is determined by constants - S_WIDTH and S_HEIGHT
screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))

# Set screen caption
pygame.display.set_caption('g1')


# Sprite image loading
# player plane
playerSprite = pygame.image.load("things/player.png").convert_alpha()
# enemy rocket
enemySprite = pygame.image.load('things/enemy.png').convert_alpha()
# cloud
cloudSprite = pygame.image.load('things/cloud.png').convert_alpha()
# animation of explosion
boomSprites = (
            pygame.image.load('things/boom/boom0.png').convert_alpha(),
            pygame.image.load('things/boom/boom1.png').convert_alpha(),
            pygame.image.load('things/boom/boom2.0.png').convert_alpha(),
            pygame.image.load('things/boom/boom2.5.png').convert_alpha(),
            pygame.image.load('things/boom/boom3.png').convert_alpha(),
            pygame.image.load('things/boom/boom4.0.png').convert_alpha(),
            pygame.image.load('things/boom/boom4.5.png').convert_alpha(),
            pygame.image.load('things/boom/boom5.png').convert_alpha(),
            pygame.image.load('things/boom/boom6.0.png').convert_alpha(),
            pygame.image.load('things/boom/boom6.5.png').convert_alpha(),
            pygame.image.load('things/boom/boom7.0.png').convert_alpha(),
            pygame.image.load('things/boom/boom7.5.png').convert_alpha(),
            pygame.image.load('things/boom/boom8.png').convert_alpha(),
            pygame.image.load('things/boom/boom9.png').convert_alpha(),
            pygame.image.load('things/boom/boom10.png').convert_alpha(),
            pygame.image.load('things/boom/boom11.png').convert_alpha(),
            pygame.image.load('things/boom/boom12.png').convert_alpha()
)
# boom rocket sound effect
boomSound1 = pygame.mixer.Sound('things/boom/boom.ogg')
boomSound1.set_volume(.7) # lower the volume a bit
# boom plane sound effect
boomSound2 = pygame.mixer.Sound('things/boom/boom2.ogg')
# lives hearts
heartSprite = pygame.image.load('things/heart.png').convert_alpha()
# Width of heartSprite (used for rendering on screen in ScreenInfo)
heartSpriteWidth = heartSprite.get_width()
# Plane sound
pygame.mixer.music.load('things/plane.ogg')
pygame.mixer.music.set_volume(.5)
# Load font
font = pygame.font.Font('freesansbold.ttf', 55) # New font object
# Start sound
startSound = pygame.mixer.Sound('things/start.ogg')
# Button sound effect
buttonSound = pygame.mixer.Sound('things/button.ogg')


# Create a custom event for adding new enemies
# Set a timer for creating enemies
# Can be set outside the mainloop
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
# Event for adding clouds
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1000)


# Instantiate player. Right now, this is just a rectangle
player = Player()

# Instantiate screen info
screenInfo = ScreenInfo()


# Create groups to hold enemy sprites, cloud sprites and all sprites
# - enemies is used for collision detection and position updates
# - shots is used for collision detection and position updates
# - clouds is used for position updates
# - explosions is used for position updates
# - allSprites is used for rendering
enemies = pygame.sprite.Group()
shots = pygame.sprite.Group()
allSprites = pygame.sprite.Group()
clouds = pygame.sprite.Group()
explosions = pygame.sprite.Group()


# Setup the clock
FPSCLOCK = pygame.time.Clock()
# Set FPS
FPS = 40


# Play the music
pygame.mixer.music.play(-1)

# The Game
def main():
    # Run the menu
    menu()

    # Clear all sprites
    # Add player to allSprites
    allSprites.empty()
    enemies.empty()
    clouds.empty()
    allSprites.add(player)

    # Variable to keep the main loop running
    running = True

    # Reset all stats
    screenInfo.start_time = pygame.time.get_ticks()
    player.lives = 3
    player.kills = 0
    screenInfo.killCount(player.kills)
    screenInfo.lifeCountReset()
    player.rect.midleft = (0, S_HEIGHT//2)

    # Main game loop 
    while running:
        # for loop through the event queue
        for event in pygame.event.get():
            # Check the event
            e = eventCheck(event)
            if e == QUIT:
                running = False

        # Get the set of keys pressed and check for user input
        # Update the player sprite based on user keypress
        keys = pygame.key.get_pressed()
        player.update(keys)
        
        # Update the position of enemies, shots, clouds and explosions
        enemies.update()
        shots.update()
        clouds.update()
        explosions.update()

        # Run the timer
        screenInfo.timer()

        # Fill the screen with sky blue
        screen.fill(colors.SKY)

        # Draw the screen information, use screenInfo's all tuple
        for s, r in screenInfo.all:
            # blit each surface on it's rect
            screen.blit(s, r)
        # Draw hearts
        for r in screenInfo.heartRects:
            screen.blit(screenInfo.heartSurf, r)

        # Draw all sprites
        for entity in allSprites:
            screen.blit(entity.surf, entity.rect)

        # Check if any enemies have collided with the player
        collidedWith = pygame.sprite.spritecollideany(player, enemies)
        if collidedWith:
            # Update player's lives
            player.lifeCount()
            # Kill the enemy
            collidedWith.kill()
            # If player has zero lives, quit the game
            if player.lives == 0:
                running = False

            # Make a BOOM
            newExplosion = Explosion(player.rect.center) # explosion in the center of the player
            explosions.add(newExplosion)
            allSprites.add(newExplosion)
            # play boom2 sound
            boomSound2.play()

        # Update the display
        pygame.display.update()  

        # Tick the clock
        # Ensure the program mantains a constant FPS
        FPSCLOCK.tick(FPS)

    # Start again
    main()

# Run the game
main()
# Deinitialize the pygame
pygame.quit()
# Exit
sys.exit()