import pygame
import math
import random
import pathlib
import palettes
from vector import Vector2
import time

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

GAME_STATE_INTRO          = 0
GAME_STATE_IN_PROGRESS    = 1
GAME_STATE_LIFE_LOST      = 2
GAME_STATE_OVER           = 3

FILEPATH = pathlib.Path().cwd()

# direction consts for player movement
D_UP    = 0
D_DOWN  = 1
D_LEFT  = 2
D_RIGHT = 3


# ======================================================================
# setup pygame
# ======================================================================
# set mixer to 512 value to stop buffering causing sound delay
# this must be called before anything else using mixer.pre_init()
# setting frequency to 22050 seems to cure the SDL thread dump bug
# also calling pygame.init() after both mixer inits is recomended
# to further help remove sound delay problems.
# https://stackoverflow.com/questions/18273722/pygame-sound-delay/18513365
# pygame2 apparently does not require the mixer pre init()
# but keeping it seems to still cure the sdl bug 
#pygame.mixer.pre_init(22050, -16, 2, 512)
pygame.mixer.init()
pygame.init()
pygame.display.set_caption('Shmup1')
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()
      
#=======================================================================
# Score Partical class
#=======================================================================

class ScorePartical():
    
    def __init__(self, pos, angle, speed, image):
        
        self.pos = Vector2(pos.x, pos.y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0,0)     
        self.alpha = 255   
        self.acc.setFromAngle(angle)
        self.acc.mult(speed)
        self.image = image
        self.image.set_alpha(self.alpha)
        
    def update(self):
        
        self.vel.add(self.acc)
        self.pos.add(self.vel)
        self.alpha -= 0.2
        self.alpha = max(0,self.alpha)
        self.image.set_alpha(self.alpha)

        
    def draw(self):
        
        screen.blit(self.image, (self.pos.x, self.pos.y))
        
    def isOffScreen(self):
        
        return (self.pos.x < 0) or (self.pos.x > SCREEN_WIDTH) or (self.pos.y < 0) or (self.pos.y > SCREEN_HEIGHT)
        
    def isDead(self):
        
        return (self.alpha <= 0) or (self.isOffScreen())

#=======================================================================
# Partical class
#=======================================================================

class Partical():
    
    def __init__(self, pos, angle, speed, size, colour):
        
        self.pos = Vector2(pos.x, pos.y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0,0)     
        self.size = size
        self.alpha = 255   
        self.acc.setFromAngle(angle)
        self.acc.mult(speed)
        self.image = pygame.Surface([self.size, random.choice((2,4,12))]) # particals have random height
        self.image.fill(colour)
        self.image.set_alpha(self.alpha)
        
    def update(self):
        
        self.vel.add(self.acc)
        self.pos.add(self.vel)
        self.alpha -= 0.1 
        self.alpha = max(0,self.alpha)
        self.image.set_alpha(self.alpha)
        
        
    def draw(self):
        
        screen.blit(self.image, (self.pos.x, self.pos.y))
        
    def isOffScreen(self):
        
        return (self.pos.x < 0) or (self.pos.x > SCREEN_WIDTH) or (self.pos.y < 0) or (self.pos.y > SCREEN_HEIGHT)
        
    def isDead(self):
        
        return (self.alpha <= 0) or (self.isOffScreen())
    

#=======================================================================
# particle system class
#=======================================================================

class ParticleSystem():
    
    def __init__(self, x, y, mx = 40):
        
        self.pos = Vector2(x, y)
        self.particles = []
        self.max_particles = mx
        
    def killAll(self):
        
        self.particles = []
        
    def burstDirection(self, angle, spread, colour):
        
        self.killAll()
        for n in range(0, self.max_particles):
            if colour is None:
                c = palettes.PALETTE_PICO8[random.randint(1, 15)]
            else:
                c = colour
            # vary the angle a little bit
            angle = (angle + random.uniform(-spread, spread)) % 360
            speed = random.uniform(0.05, 2.0)
            size = random.randint(4, 64) # this is width of the partical
            p = Partical(self.pos, angle, speed, size, c)
            self.particles.append(p)
            
    def burstCircle(self, colour):
        
        self.killAll()
        step = 360 // self.max_particles
        for n in range(0, self.max_particles):
            if colour is None:
                c = palettes.PALETTE_PICO8[random.randint(1, 15)]
            else:
                c = colour
                
            angle = n * step
            speed = random.uniform(1.0, 5.0)
            size = random.randint(4, 64) # this is width of the partical
            
            p = Partical(self.pos, angle, speed, size, c)
            self.particles.append(p)
    
    def scoreBurst(self, scoreimage):
        
        self.killAll()
        step = 360 // self.max_particles
        for n in range(0, self.max_particles):
            if self.max_particles == 1:
                angle = random.randint(180, 360)
            else:
                angle = n * step
                
            speed = 0.5
            p = ScorePartical(self.pos, angle, speed, scoreimage)
            self.particles.append(p)
            
    def update(self):
        
        cp = [p for p in self.particles if not p.isDead()]
        self.particles = cp
        for p in self.particles:
            p.update()
            p.draw()
        
    def isDead(self):
        
        return len(self.particles) == 0
        

#=======================================================================
# particlesystemController class
#=======================================================================

class ParticleSystemController():
    
    def __init__(self):
        
        self.systems = []
        
    def spawn(self, x, y, mx):
        
        system = ParticleSystem(x, y, mx)
        self.systems.append(system)
        return system
        
    def spawnBurstDirection(self, x, y, angle, spread, max_particles = 20, colour=None):
        
        system = self.spawn(x, y, max_particles)
        system.burstDirection(angle, spread, colour)
        
    def spawnBurstCircle(self, x, y, max_particles = 20, colour=None):
        
        system = self.spawn(x, y, max_particles)
        system.burstCircle(colour)
        
    def spawnScoreBurst(self, x, y, scoreimage):
        
        system = self.spawn(x, y, 1)
        system.scoreBurst(scoreimage)
        
    def killAll(self):
        
        self.systems = []
    
    def update(self):
        
        cp = [ps for ps in self.systems if not ps.isDead()]
        self.systems = cp
        for s in self.systems:
            s.update()       


#=======================================================================
# Star class
#=======================================================================

class Star():
    
    def __init__(self, size, img):
        
        self.position = Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.velocity = Vector2(0.0, 1 + random.random() * 4.1)
        self.size     = size
        self.image    = img 
        self.rect     = self.image.get_rect()                   

    def reset(self):
        
        self.position.y = 0
        self.position.x = random.randint(0, SCREEN_WIDTH)
        self.velocity.y = 1 + random.random() * 6.1
        
    def update(self):
                
        self.velocity.y += 0.2
        self.position.add(self.velocity)
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        
    def draw(self):
        
        screen.blit(self.image, self.rect)


#=======================================================================
# Starfield class
#=======================================================================

class StarField():
    
    def __init__(self):
        
        self.stars = []
        self.max_stars = 20
        self.images = []
        
        for i in range(4):
            img = pygame.Surface((i + 1, i + 1))
            img.fill(palettes.COLOUR_PICO8_BLUE)
            self.images.append(img)
        
        for i in range(0, self.max_stars):
            size = random.randint(1,4)
            img  = self.images[size-1]
            star = Star(size, img)
            self.stars.append(star)
            
    def update(self):
        
        for star in self.stars:
            star.update()
            
            if star.position.y > SCREEN_HEIGHT:
                star.reset()
                
    def draw(self):
        
        for star in self.stars:
            star.draw()

# ======================================================================
# Sploder Enemy class
# ======================================================================

class EnemySploder():
    
    def __init__(self, x, y, score_value, score_image_index, game):
        
        speedy = 0.1
        
        self.pos   = Vector2(x, y)
        self.vel   = Vector2(random.randrange(-1, 1), 1 + random.random() * speedy)
        self.rect  = None
        self.image = None
        self.dead  = False
        self.game  = game
        self.score_value = score_value
        self.score_image_index = score_image_index

    def setImage(self, img):
    
        self.image = img
        self.rect  = self.image.get_rect()

    def update(self):
        
        self.pos.add(self.vel)
        
        # bounce off the walls
        if self.pos.x < 32 or self.pos.x > SCREEN_WIDTH - 72:
            self.vel.x *= -1
        
        # don't kill if we go off screen instead put enemy back to top
        if self.pos.y > SCREEN_HEIGHT or self.pos.x < -50 or self.pos.x > SCREEN_WIDTH:
            self.pos.x = random.randint(100, SCREEN_WIDTH-100)
            self.pos.y = -50
        
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        self.fire()
        
    def fire(self):
        
        if self.isOnscreen:
            x = random.random()
            if x > 0.99:
                vx = -4
                vy = 7
                game.enemyFire(self.pos.x + 16, self.pos.y, vx, vy, self)

    def isOnscreen(self):
        
        return self.pos.y > 0

    def isDead(self):
        
        return self.dead
        
    def draw(self):
        
        screen.blit(self.image, (self.pos.x, self.pos.y))

# ======================================================================
# enemy class
# ======================================================================

class Enemy():
    
    def __init__(self, x, y, score_value, score_image_index, game):
        
        speedx = 5
        speedy = 0.9
        
        self.pos         = Vector2(x, y)
        self.vel         = Vector2(-3 + random.random() * speedx, 3 + random.random() * speedy)
        self.rect        = None
        self.image       = None
        self.dead        = False
        self.game        = game
        self.score_value = score_value
        self.score_image_index = score_image_index

    def setImage(self, img):
    
        self.image = img
        self.rect  = self.image.get_rect()

    def update(self):
        
        self.pos.add(self.vel)
        
        # bounce off the walls
        if self.pos.x < 32 or self.pos.x > SCREEN_WIDTH - 72:
            self.vel.x *= -1
        
        # don't kill if we go off screen instead put enemy back to top
        if self.pos.y > SCREEN_HEIGHT or self.pos.x < -50 or self.pos.x > SCREEN_WIDTH:
            self.pos.x = random.randint(100, SCREEN_WIDTH-100)
            self.pos.y = random.randint(-600, -100)
        
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        self.fire()
        
    def fire(self):
        
        if self.isOnscreen:
            x = random.random()
            bullet_vx = 0
            bullet_vy = 7 + random.random()
            
            if x > 0.995:
                game.enemyFire(self.pos.x + 16, self.pos.y, bullet_vx, bullet_vy, self)

    def isOnscreen(self):
        
        return self.pos.y > 0

    def isDead(self):
        
        return self.dead
        
    def draw(self):
        
        screen.blit(self.image, (self.pos.x, self.pos.y))

# ======================================================================
# player class
# ======================================================================

class Player():
    
    def __init__(self):
        
        self.pos           = Vector2(SCREEN_WIDTH // 2 - 12, SCREEN_HEIGHT - 30)
        self.vel           = Vector2(0.0, 0.0)
        self.vel_target    = Vector2(0.0, 0.0)
        self.images        = []
        self.rect          = None
        self.speed         = 5.0
        self.gun_heat      = 0
        self.gun_heat_max  = 100
        self.gun_level     = 1
        self.gun_level_max = 3
        self.lives         = 3
        self.this_frame    = 0
        self.image_index   = 0
        
    def reset(self):
        
        self.lives      = 3
        self.gun_heat   = 0
        self.pos        = Vector2(SCREEN_WIDTH // 2 - 12, SCREEN_HEIGHT - 30)
        self.vel        = Vector2(0.0, 0.0)
        self.vel_target = Vector2(0.0, 0.0)
        
    def fire(self):
        
        self.gun_heat += 10
        
    def gunOverHeated(self):
        
        return self.gun_heat >= self.gun_heat_max
        
    def lostLife(self):
        
        self.lives -= 1
        
    def gunIsMax(self):
        
        return self.gun_level >= self.gun_level_max
        
    def addGunLevel(self):
        
        if not self.gunIsMax():
            self.gun_level += 1
        
    def setImage(self, image):
        
        self.images.append(image)
        self.rect = image.get_rect()
        
    def lerp(self, mn, mx, norm):
        
        return ((mx - mn) * norm + mn)
    
    def update(self):
        
        # lerp towards full speed
        self.vel.x = self.lerp(self.vel.x, self.vel_target.x, 0.4)
        self.vel.y = self.lerp(self.vel.y, self.vel_target.y, 0.4)
        
        self.pos.add(self.vel)
        self.constrain()
        
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        # cooldown gun each frame
        if self.gun_heat > 0:
            self.gun_heat -= 0.6
        
    def move(self, direction):
        
        if direction == D_UP:
            self.vel_target.y = -self.speed
        elif direction == D_DOWN:
            self.vel_target.y = self.speed
        elif direction == D_LEFT:
            self.vel_target.x = -self.speed            
        elif direction == D_RIGHT:
            self.vel_target.x = self.speed
            
    def constrain(self):
        
        if self.pos.x < 32:
            self.pos.x = 32
        elif self.pos.x > SCREEN_WIDTH-72:
            self.pos.x = SCREEN_WIDTH-72
            
        if self.pos.y > SCREEN_HEIGHT - 50:
            self.pos.y = SCREEN_HEIGHT - 50
        elif self.pos.y < SCREEN_HEIGHT - 200:
            self.pos.y = SCREEN_HEIGHT - 200

    def draw(self):
        
        self.this_frame += 1
        if self.this_frame > 4:
            self.this_frame = 0
            self.image_index += 1
            if self.image_index > len(self.images)-1:
                self.image_index = 0
            
        screen.blit(self.images[self.image_index], (self.pos.x, self.pos.y))
        
        
# ======================================================================
# bullet class
# ======================================================================

class PlayerBullet():
    
    def __init__(self, x, y):
        
        self.pos   = Vector2(x,y)
        self.vel   = Vector2(0,-40)
        self.dead  = False
        self.image = None
        self.rect = None
        
    def setImage(self, img):
        
        self.image = img
        self.rect = pygame.Rect(0,0,4,40) # hitbox is not full length of image
        
    def isDead(self):
        
        return self.dead or self.pos.y < -128
        
    def update(self):
        
        self.pos.add(self.vel)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
    def draw(self):
        
        screen.blit(self.image, (self.pos.x, self.pos.y))


class EnemyBullet():
    
    def __init__(self, x, y, vx, vy):
        
        self.pos = Vector2(x, y)
        self.vel = Vector2(vx, vy)
        self.size = 4
        
        self.image = pygame.Surface([self.size, self.size*3])
        self.image.fill(palettes.COLOUR_PICO8_WHITE)
        self.rect = self.image.get_rect()
        self.dead = False
        
    def setImage(self, image):
        
        self.image = image
        self.rect = self.image.get_rect()
        
    def isDead(self):
        
        return self.dead or self.pos.y > SCREEN_HEIGHT
        
    def update(self):
        
        self.pos.add(self.vel)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
    def draw(self):
        
        screen.blit(self.image, (self.pos.x, self.pos.y))
     
     
     
# ======================================================================
# powerup class - adds firepower to player etc.
# ======================================================================
        
class PowerUp():
    
    def __init__(self, x, y):
        
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 2)
        self.images = []
        self.rect = None
        self.dead = False
        
    def setImage(self, image):
        
        self.images.append(image)
        self.rect = image.get_rect()
        
    def isDead(self):
        
        return self.dead or self.pos.y > SCREEN_HEIGHT
        
    def update(self):
        
        self.pos.add(self.vel)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
    def draw(self):
        
        screen.blit(self.images[0], (self.pos.x, self.pos.y))

# ======================================================================
# token class - additional scoring opportunities
# ======================================================================
        
class Token():
    
    def __init__(self, x, y, value):
        
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 2)
        self.images = []
        self.rect = None
        self.dead = False
        self.value = value
        
    def setImage(self, image):
        
        self.images.append(image)
        self.rect = image.get_rect()
        
    def isDead(self):
        
        return self.dead or self.pos.y > SCREEN_HEIGHT
        
    def update(self):
        
        self.pos.add(self.vel)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
    def draw(self):
        
        screen.blit(self.images[0], (self.pos.x, self.pos.y))
        
        
class BackgroundScroller():
    
    def __init__(self, game):
        
        self.scroller_init_offy = -5112
        self.scroller_curr_offy = -5112
        self.scroller_image = game.scroller_image
    
    def update(self):
        
        pass
    
    def draw(self):
        
        self.scroller_curr_offy += 8
        
        if self.scroller_curr_offy > 0: 
            screen.blit(self.scroller_image,(0,self.scroller_init_offy - self.scroller_curr_offy))
            
        if self.scroller_curr_offy > SCREEN_HEIGHT:
            self.scroller_curr_offy = self.scroller_init_offy
            
        screen.blit(self.scroller_image,(0,self.scroller_curr_offy))
        
        
# ======================================================================
# intro screen class
# ======================================================================

class ScreenIntro():
    
    def __init__(self, game):
        
        self.game         = game
        self.title        = self.game.font_title.render('SHMUP1', 0,  palettes.COLOUR_PICO8_ORANGE)
        self.footer_text  = 'shoot enemies...collect bonus tokens and gun powerups! ... arrow keys to move, Z to fire. spacebar to start game.'
        self.footer       = self.game.font_small.render(self.footer_text, 0,  palettes.COLOUR_PICO8_LAVENDER)
        self.footer_xoff  = SCREEN_WIDTH # (SCREEN_WIDTH - self.footer.get_width()) // 2
        self.footer_width = self.footer.get_width()
        self.title_xoff   = (SCREEN_WIDTH - self.title.get_width()) // 2
        self.subheading   = 'THE RETRO SHOOTER'
        self.letters_xoff = (SCREEN_WIDTH - (len(self.subheading) * 26)) // 2
        self.angle        = 0
        self.letters      = []
       
        for char in list(self.subheading):
            self.letters.append(self.game.font_small.render(char, 0,  palettes.COLOUR_PICO8_RED))
        
    def draw(self):
        
        x              = self.letters_xoff
        wave_phase     = 0
        wave_phase_step = 360 / len(self.letters)
        wave_height    = 40
        wave_speed     = 0.3
        letter_spacing = 26

        for c in self.letters:
            
            y = math.sin(math.radians(self.angle + wave_phase)) * wave_height
            self.angle += wave_speed
            wave_phase += wave_phase_step
            screen.blit(c, (x, 400 + y))
            x += letter_spacing
            
        screen.blit(self.title, (self.title_xoff, y + 150))
        
        
        self.footer_xoff -= 3
        if self.footer_xoff < -self.footer_width:
            self.footer_xoff = SCREEN_WIDTH
            
        screen.blit(self.footer, (self.footer_xoff, 740))
        
        for i in range(1,4):
            y = math.sin(math.radians(self.angle / 2)) * 40
            x = math.cos(math.radians(self.angle / 2)) * 40
            screen.blit(self.game.enemy_images[i], (x + (100 * i) + 50,  y + 560))
            
            
# ======================================================================
# game over screen class
# ======================================================================

class ScreenGameOver():
    
    def __init__(self, game):
        
        self.game  = game
        self.score = 0
        self.score_offsetx = 0 
        self.final_score_letters = []
        self.game_over_letters = []
        self.letter_spacing = 0

        self.game_over_letters   = self.makeLetters(self.game.font_title, 'GAME OVER!', palettes.COLOUR_PICO8_RED)
        self.final_score_letters = self.makeLetters(self.game.font_title, 'YOU SCORED', palettes.COLOUR_PICO8_YELLOW)

       
    def makeLetters(self, font, message, colour):
        
        r = []
        for char in list(message):
            r.append(font.render(char, 0, colour))
            
        return r
            
    def reset(self):
        
        self.letter_spacing = 0
        
    def setFinalScore(self):
        
        self.score = self.game.font_title.render(str(self.game.score), 0,  palettes.COLOUR_PICO8_YELLOW)
        self.score_offsetx = (SCREEN_WIDTH - self.score.get_width()) // 2
        self.reset()
        
    def draw(self):
        
        offset1 = 260 - (self.letter_spacing * 4)
        offset2 = 250 - (self.letter_spacing * 4)
        
        if self.letter_spacing < 50:
            self.letter_spacing += 1
        
        for x, letter_image in enumerate(self.game_over_letters):
            screen.blit(letter_image, (offset1 + (x * self.letter_spacing), 100))
            
        for x, letter_image in enumerate(self.final_score_letters):
            screen.blit(letter_image, (offset2 + (x * self.letter_spacing), 300))    
            
        screen.blit(self.score, (self.score_offsetx, 500))
        
        
# ======================================================================
# life lost screen class
# ======================================================================

class ScreenLifeLost():
    
    def __init__(self, game):
        
        self.game         = game

        self.subheading   = 'GOT YOU !!!'
        self.letters_xoff = (SCREEN_WIDTH - (len(self.subheading) * 26)) // 2
        self.angle        = 0
        self.letters      = []
       
        for char in list(self.subheading):
            self.letters.append(self.game.font_small.render(char, 0,  palettes.COLOUR_PICO8_PINK))
        
    def draw(self):
        
        x              = self.letters_xoff
        wave_phase     = 0
        wave_phase_step = 360 / len(self.letters)
        wave_height    = 40
        wave_speed     = 0.8
        letter_spacing = 26

        for c in self.letters:
            
            y = math.sin(math.radians(self.angle + wave_phase)) * wave_height
            self.angle += wave_speed
            wave_phase += wave_phase_step
            screen.blit(c, (x, 400 + y))
            x += letter_spacing


            
        
        
        


        
# ======================================================================
# game class
# ======================================================================


class Game():

    def __init__(self):
        
        self.gamestate           = GAME_STATE_INTRO
        self.gamestate_delay     = 0
        self.fps                 = 50
        self.starfield           = StarField()
        self.player              = Player() 
        self.psc                 = ParticleSystemController()
        self.enemies             = [] # the live enemies
        self.enemy_images        = [] # the enemy images
        self.enemy_sounds        = [] # the enemy sounds
        self.enemy_bullets       = [] # live enemy bullets
        self.enemy_bullet_images = [] # enemy bullet images
        self.player_bullets      = [] # live player bullets
        self.powerups            = [] # live powerups
        self.tokens              = [] # live tokens
        self.token_images        = [] # token images
        self.token_sounds        = [] # token sounds
        self.score_images        = [] # score images for partical system
        self.powerup_images      = [] # powerup images
        self.enemy_image_count   = 4  # number of enemy images
        self.font_small          = None 
        self.font_title          = None       
        self.screen_edge         = None
        self.scroller_image      = None
        self.player_bullet_image = None
        self.player_life_image   = None
        self.sound_player_zap    = None
        self.sound_player_death  = None
        self.sound_gun_overheat  = None
        self.sound_enemy_dead    = []
        self.score               = 0
        
        # load the assets once the above are set
        self.loadAssets()
        self.screen_intro        = ScreenIntro(self)
        self.screen_life_lost    = ScreenLifeLost(self)
        self.screen_game_over    = ScreenGameOver(self)
        self.background_scroller = BackgroundScroller(self)


    def spaceBarPressed(self):
        
        if self.gamestate == GAME_STATE_INTRO:
            self.startGame()
            self.gamestate = GAME_STATE_IN_PROGRESS
        elif self.gamestate == GAME_STATE_OVER:
            self.gamestate = GAME_STATE_INTRO

    def startGame(self):
        
        self.score          = 0
        self.enemies        = []
        self.enemy_bullets  = []
        self.player_bullets = []
        self.powerups       = []
        self.tokens         = []
        self.psc.killAll() 
        self.player.reset()

    def resumeAfterLifeLost(self):
        
        self.player.gun_heat  = 0
        self.player.gun_level = 1
        self.enemies          = []
        self.enemy_bullets    = []
        self.player_bullets   = []
        self.powerups         = []
        self.tokens           = []
        self.psc.killAll() 


    def enemyFire(self, x, y, vx, vy, enemytype):
        
        if isinstance(enemytype, EnemySploder):
            
            self.enemy_sounds[1].play()
            self.addEnemyBullet(x, y, vx,  vy, 1)
            self.addEnemyBullet(x, y, 0,   vy, 2)
            self.addEnemyBullet(x, y, -vx, vy, 3)
            
        elif isinstance(enemytype, Enemy):
            
            self.addEnemyBullet(x, y, vx,  vy, 0)
    
    
    def addEnemyBullet(self, x, y, vx, vy, img_idx):
        
        eb = EnemyBullet(x, y, vx, vy)
        eb.setImage(self.enemy_bullet_images[img_idx])
        self.enemy_bullets.append(eb)
        
        
    def fire(self):
        
        if not self.player.gunOverHeated():
            
            # create a xpositions tuple of where to spawn player
            # bullets based on whether we are single/double/triple shotting
            centrex = self.player.pos.x + 18
            xpositions = ()
            
            if self.player.gun_level == 1:
                xpositions = (centrex,)                
            elif self.player.gun_level == 2:
                xpositions = (centrex-10, centrex + 10)
            else:
                xpositions = (centrex-16, centrex, centrex + 16)
                
            for x in xpositions:
                b = PlayerBullet(x, self.player.pos.y - 10)
                b.setImage(self.player_bullet_image)
                self.player_bullets.append(b)
    
            self.player.fire()
            self.sound_player_zap.play()
        else:
            self.sound_gun_overheat.play()
        
        
    def spawnEnemy(self):
        
        if len(self.enemies) < 6:
            x = random.random()
            
            if x < 0.9:
                score_image_index = random.randint(0, self.enemy_image_count-2) # excludes sploder image
                score_value       = 10 + (score_image_index * 10) # score now matches the partical score image
                e = Enemy(random.randint(100,SCREEN_WIDTH-100), random.randint(-600, -100), score_value, score_image_index, self)
                e.setImage(self.enemy_images[score_image_index]) 
            else:
                self.enemy_sounds[0].play()
                score_image_index = 3
                score_value = 40
                e = EnemySploder(random.randint(100,SCREEN_WIDTH-100), -50, score_value, score_image_index, self)
                e.setImage(self.enemy_images[self.enemy_image_count-1]) 
                
            self.enemies.append(e)
                
                
    def spawnPowerUp(self):

        if len(self.powerups) < 1 and not self.player.gunIsMax():
            if random.random() > 0.99:
                p = PowerUp(random.randint(100, SCREEN_WIDTH-100), 0)
                p.setImage(self.powerup_images[0]) 
                self.powerups.append(p)
        
    def spawnToken(self):
        
        if len(self.tokens) < 4:
            if random.random() > 0.9:
                
                # pick a random spawn position but if it is already in use by a token
                # don't waste time chosing another just don't spawn anything this frame
                spawnposition = random.choice((100,200,300,400,500))
                position_is_unused = True
                
                for t in self.tokens:
                    if t.pos.x == spawnposition:
                        position_is_unused = False
                        break
                        
                if position_is_unused:
                    token_value = 100
                    token_type = random.randint(0, len(self.token_images)-2)
                    t = Token(spawnposition, 0, token_value)
                    t.setImage(self.token_images[token_type]) 
                    self.tokens.append(t)
        
        
    def loadAssets(self):
        
        self.scroller_image = pygame.image.load(str(FILEPATH.joinpath('png' ,'c64_screen.png'))).convert()
        self.scroller_image.set_alpha(50)
        
        self.player_life_image = pygame.image.load(str(FILEPATH.joinpath('png' ,'heart.png'))).convert()
        
        # load token images
        self.token_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'token_1.png'))).convert())
        self.token_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'token_2.png'))).convert())
        
        for img in self.token_images:
            img.set_colorkey(palettes.COLOUR_PICO8_BLACK)
            
        # load powerup images
        self.powerup_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'powerup_1.png'))).convert())
        self.powerup_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'powerup_small.png'))).convert())
        self.powerup_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'powerup_large.png'))).convert())
        
        for img in self.powerup_images:
            img.set_colorkey(palettes.COLOUR_PICO8_BLACK)
        
        # load score images
        self.score_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'score_10.png'))).convert())
        self.score_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'score_20.png'))).convert())
        self.score_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'score_30.png'))).convert())
        self.score_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'score_40.png'))).convert())
        self.score_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'score_100.png'))).convert())
        
        
        # load player sounds
        self.sound_player_zap   = pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'player_zap.ogg')))
        self.sound_player_death = pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'player_death.ogg')))
        self.sound_gun_overheat = pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'player_gun_overheat.ogg')))
        
        # load enemy bullet images
        self.enemy_bullet_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'enemy_bullet_1.png'))).convert())
        self.enemy_bullet_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'enemy_bullet_2.png'))).convert())
        self.enemy_bullet_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'enemy_bullet_3.png'))).convert())
        self.enemy_bullet_images.append(pygame.image.load(str(FILEPATH.joinpath('png' ,'enemy_bullet_4.png'))).convert())
        
        # load enemy explosion sounds
        self.sound_enemy_dead.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'enemy_dead_1.ogg'))))
        self.sound_enemy_dead.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'enemy_dead_2.ogg'))))
        self.sound_enemy_dead.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'enemy_dead_3.ogg'))))
        self.sound_enemy_dead.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'enemy_dead_4.ogg'))))
        
        # load enemy spawn and shoot sounds
        self.enemy_sounds.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'enemy_spawn_1.ogg'))))
        self.enemy_sounds.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'enemy_zap_1.ogg'))))
         
        # load token sounds
        self.token_sounds.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'token_1.ogg'))))
        self.token_sounds.append(pygame.mixer.Sound(str(FILEPATH.joinpath('sounds' ,'powerup_1.ogg'))))
        
        
        self.player_bullet_image = pygame.image.load(str(FILEPATH.joinpath('png' ,'player_bullet_2.png'))).convert()

        # load font
        self.font_small = pygame.font.Font(str(FILEPATH.joinpath('assets' ,'PressStart2P.ttf')), 24)
        self.font_title = pygame.font.Font(str(FILEPATH.joinpath('assets' ,'PressStart2P.ttf')), 48)
        
        
        # load enemy images
        sheet = pygame.image.load(str(FILEPATH.joinpath('png' ,'enemies.png'))).convert()
        sheet.set_colorkey(palettes.COLOUR_PICO8_BLACK)
            
        offsetx        = 0
        sprite_width   = 40
        sprite_height  = 32
        sprite_spacing = 10
        
        for n in range(self.enemy_image_count):
            tup = (offsetx, 0, sprite_width, sprite_height)
            img = sheet.subsurface(tup)
            self.enemy_images.append(img)
            offsetx += sprite_width + sprite_spacing
            
        # load player images
        player_image = pygame.image.load(str(FILEPATH.joinpath('png' ,'player.png'))).convert()
        player_image.set_colorkey(palettes.COLOUR_PICO8_BLACK)
        self.player.setImage(player_image)
        player_image = pygame.image.load(str(FILEPATH.joinpath('png' ,'player_2.png'))).convert()
        player_image.set_colorkey(palettes.COLOUR_PICO8_BLACK)
        self.player.setImage(player_image)
        
        # load edge tile and make edge surfaces
        tile = pygame.image.load(str(FILEPATH.joinpath('png' ,'edge.png'))).convert()
        self.screen_edge = pygame.Surface((32, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT // 32):
            self.screen_edge.blit(tile, (0, i*32))

    def collideBulletsWithEnemies(self):
        
         for bullet in self.player_bullets:
            for enemy in self.enemies:
                # player ship fires dual shots, test to see if 1 shot
                # has already killed the enemy to prevent double scoring bug
                if not enemy.dead and bullet.rect.colliderect(enemy.rect):
                    bullet.dead = True
                    enemy.dead = True
                    self.psc.spawnBurstCircle(enemy.pos.x, enemy.pos.y, 10)
                    self.psc.spawnScoreBurst(enemy.pos.x, enemy.pos.y, self.score_images[enemy.score_image_index]) # unfinished!
                    self.sound_enemy_dead[random.randint(0,3)].play()
                    self.score += enemy.score_value       
        
    def collideBulletsWithPlayer(self):
        
         for bullet in self.enemy_bullets:
            if bullet.rect.colliderect(self.player.rect):
                bullet.dead = True
                self.psc.spawnBurstDirection(self.player.rect.x, self.player.rect.y, 270, 5, 60)
                self.sound_enemy_dead[random.randint(0,3)].play()
                self.player.lostLife()
                self.sound_player_death.play()
                self.gamestate = GAME_STATE_LIFE_LOST       

    def collidePlayerWithTokens(self):
        
        for token in self.tokens:
            if self.player.rect.colliderect(token.rect):
                token.dead = True
                self.score += token.value
                self.token_sounds[0].play()
                self.psc.spawnScoreBurst(token.rect.x, token.rect.y, self.score_images[4])
        
    def collidePlayerWithPowerups(self):
        
        for powerup in self.powerups:
            if self.player.rect.colliderect(powerup.rect):
                powerup.dead = True
                self.player.addGunLevel()
                self.token_sounds[1].play()
                self.psc.spawnScoreBurst(powerup.rect.x, powerup.rect.y, self.powerup_images[1])
                
    def doCollisions(self):
        
        self.collideBulletsWithEnemies()
        self.collideBulletsWithPlayer()
        self.collidePlayerWithTokens()
        self.collidePlayerWithPowerups()

    def clearTheDead(self):
        
        tmp = [e for e in self.enemies if not e.isDead()]
        self.enemies = tmp
        
        tmp = [b for b in self.enemy_bullets if not b.isDead()]
        self.enemy_bullets = tmp
        
        tmp = [b for b in self.player_bullets if not b.isDead()]
        self.player_bullets = tmp
        
        tmp = [token for token in self.tokens if not token.isDead()]
        self.tokens = tmp

        tmp = [powerup for powerup in self.powerups if not powerup.isDead()]
        self.powerups = tmp
    
    def drawArena(self):
        
        screen.blit(self.screen_edge, (0,0))
        screen.blit(self.screen_edge, (SCREEN_WIDTH-32,0))
        
        # draw score
        screen.blit(self.font_small.render(str(self.score), 0,  palettes.COLOUR_PICO8_RED), (202, 12))
        screen.blit(self.font_small.render(str(self.score), 0,  palettes.COLOUR_PICO8_YELLOW), (200, 10))
        
        # draw lives remaining
        for i in range(self.player.lives):
            screen.blit(self.player_life_image, [40 + (i * 36), 10, 8, 8])
        
        # this bar needs to be an object
        if self.player.gunOverHeated():
            pygame.draw.rect(screen, palettes.COLOUR_PICO8_ORANGE, [396, 12, 108, 16])
            
        pygame.draw.rect(screen, palettes.COLOUR_PICO8_LIGHTPEACH, [400, 16, 100, 8])
        pygame.draw.rect(screen, palettes.COLOUR_PICO8_RED       , [400, 16, self.player.gun_heat, 8])        
        
    def drawGame(self):
        
        self.doCollisions()
        self.clearTheDead()
        
        # draw back scroller
        self.background_scroller.draw()
        
        self.starfield.update()
        self.starfield.draw()
        
        self.psc.update()

        for b in self.player_bullets:
            b.update()
            b.draw()

        for e in self.enemies:
            e.update()
            e.draw()
            
        for b in self.enemy_bullets:
            b.update()
            b.draw()
            
        for t in self.tokens:
            t.update()
            t.draw()
            
        for p in self.powerups:
            p.update()
            p.draw()
            
        self.player.update()
        self.player.draw()
        self.drawArena()
    
        self.spawnEnemy()
        self.spawnToken()
        self.spawnPowerUp()
    
    def drawIntro(self):
        
        self.starfield.update()
        self.starfield.draw()
        self.background_scroller.draw()
        self.screen_intro.draw()
        
    def drawLifeLost(self):
        
        self.gamestate_delay += 1
        
        if self.gamestate_delay == 1:
            pass
        else:
            #self.starfield.update()
            #self.starfield.draw()
            self.psc.update()
            self.drawArena()
            self.screen_life_lost.draw()
            
        if self.gamestate_delay > self.fps * 4:
            self.gamestate_delay = 0
            self.resumeAfterLifeLost()
            if self.player.lives > 0:
                self.gamestate = GAME_STATE_IN_PROGRESS
            else:
                self.screen_game_over.setFinalScore()
                self.gamestate = GAME_STATE_OVER
        
    def drawGameOver(self):
        
        self.starfield.update()
        self.starfield.draw()
        self.background_scroller.draw()
        self.screen_game_over.draw()
        
        
    def run(self):
        
        done = False
        
        while not done:
   
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:  
                    done = True
                    
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_ESCAPE):
                        done = True
                    elif (event.key == pygame.K_SPACE):
                        self.spaceBarPressed()
                    elif (event.key == pygame.K_z):
                        self.fire()
                    elif (event.key == pygame.K_LEFT):
                        self.player.move(D_LEFT)
                    elif (event.key == pygame.K_RIGHT):
                        self.player.move(D_RIGHT)
                    elif (event.key == pygame.K_UP):
                        self.player.move(D_UP)
                    elif (event.key == pygame.K_DOWN):
                        self.player.move(D_DOWN)
                    elif (event.key == pygame.K_s):
                        pygame.image.save(screen, 'screenshot.png')
                        
                        
            screen.fill((0,0,0))
                        
            if self.gamestate == GAME_STATE_INTRO:
                
                 game.drawIntro()
                 
            elif self.gamestate == GAME_STATE_IN_PROGRESS:
                
                game.drawGame()
                
            elif self.gamestate == GAME_STATE_LIFE_LOST:
                
                game.drawLifeLost()
                
            elif self.gamestate == GAME_STATE_OVER:
                self.drawGameOver()
                 

            # ~ fps = str(int(clock.get_fps()))
            # ~ fps_text = self.font_small.render(fps, 0, (255,255,255))
            # ~ screen.blit(fps_text, (20, 540))

            
            clock.tick(self.fps)            
            pygame.display.flip()
            
        
game = Game()
game.run()
pygame.quit()

        
