from pygame import *
import random

level = 1

# GAMESPRITE CLASS

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, vx, vy, x=60, y=60, angle=0):
        super().__init__()

        self.original_image = transform.scale(image.load(player_image), (x, y))
        self.image = self.original_image

        self.angle = angle
        self.vx = vx
        self.vy = vy

        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

        self.width = x
        self.height = y

    def rotate(self, amount):
        self.angle += amount

        center = self.rect.center
        self.image = transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=center)
    
    def photo(self, img):
        center = self.rect.center
        self.original_image = transform.scale(image.load(img), (self.width, self.height))
        self.image = transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=center)
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# ASTEROID CLASS

class Asteroid(GameSprite):
    def start(self, do=None):
        self.vx = random.randint(1, level + 1)
        self.vy = random.randint(1, 2)

        if do == None:
            choice = random.randint(0, 1)

            if choice == 0:
                self.rect.x = random.choice([0, size[0]])
                self.rect.y = random.randint(5, size[1] - 5)
        
            if choice == 1:
                self.rect.y = random.choice([0, size[1]])
                self.rect.x = random.randint(5, size[0] - 5)
        
        else:
            self.rect.y = do[1]
            self.rect.x = do[0]
        
    def controls(self):
        global lived

        if self.rect.y >= size[1] - self.width // 2:
            self.start(do=(self.rect.x, 0))
        
        if self.rect.y <= self.width // 2:
            self.start(do=(self.rect.x, self.rect.y))

        if self.rect.x >= size[0] - self.height // 2:
            self.start(do=(0, self.rect.y))
        
        if self.rect.x <= self.height // 2:
            self.start(do=(self.rect.x, self.rect.y))

    def update(self):
        self.controls()
        self.rect.x += self.vx
        self.rect.y += self.vy

# PLAYER CLASS

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, vx, vy, x=60, y=60, angle=0):
        super().__init__(player_image, player_x, player_y, vx, vy, x, y, angle)

        self.normal_image = transform.scale(image.load(player_photo), (x, y))
        self.fire_image = transform.scale(image.load("feuer.jpeg"), (x, y))

    def set_photo(self, img):
        center = self.rect.center
        self.original_image = img
        self.image = transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=center)

    def start(self):
        self.rect.x = size[0] // 2
        self.rect.y = size[1] // 2
        self.speed = 4
    
    def controls(self):
        self.rect.x = min(max(self.rect.x, 5), size[0]-5)

    def move(self):
        keys = key.get_pressed()

        if keys[K_RIGHT]:
            self.rotate(5)
        
        if keys[K_LEFT]:
            self.rotate(-5)

        moving = False

        if keys[K_UP]:
            import math

            rad = math.radians(self.angle)

            self.vx = -math.sin(rad) * self.speed
            self.vy = -math.cos(rad) * self.speed

            self.rect.x += self.vx
            self.rect.y += self.vy
            moving = True

        if moving:
            self.set_photo(self.fire_image)
        else:
            self.set_photo(self.normal_image)
        
        if keys[K_a]:
            self.rotate(-5)
        
        if keys[K_d]:
            self.rotate(5)

 
    def update(self):
        self.move()
        self.controls()
    
    def fire(self):
        import math

        speed = 8

        rad = math.radians(self.angle)

        vx = -math.sin(rad) * speed
        vy = -math.cos(rad) * speed

        bullet = Bullet(bullet_photo, 0, 0, 0, 0, x=10, y=10)
        bullet.start(
            vx,
            vy,
            self.rect.centerx + vx * 4,
            self.rect.centery + vy * 4
        )
        bullets.add(bullet)


# BULLET CLASS

class Bullet(GameSprite):
    def start(self, vx, vy, x, y):
        self.vx = vx
        self.vy = vy
        self.rect.x = x
        self.rect.y = y
    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
       

# SETTINGS

# Window settings

caption = "Asteroiden-Ausweichen"
size = (600, 400)

# Photo settings

player_photo = "rocket.png"
asteroid_photo = "asteroid.png"
background_photo = "background.png"
bullet_photo = "bullet.png"

# Game-in settings

num_asteroids = 4
game = True

FPS = 30
clock = time.Clock()

lived = 0
min_live = 5

# Font settings

lose_show = False
win_show = False

font_size = 50

# Time settings

counter = 0
start = 0
wait_time = 3 # s

# Music settings

mixer.init()

mixer.music.load("space.mp3")
mixer.music.play()

# HILFSFUNKTIONEN

def update_asteroid_num():
    asteroids.empty()
    global free
    
    free = list(range(1, size[0]))

    for i in range(num_asteroids):
        asteroid = Asteroid(asteroid_photo, 0, 0, 0, 0)
        asteroid.start()
        asteroids.add(asteroid)

def LOSE():
    global lose_show, start, lived
    window.blit(lose, (size[0] // 2 - 100, size[1] // 2))
    if start == 0:
        start = counter

    if counter - start == wait_time * FPS:
        lose_show = False
        start = 0
        lived = 0

        update_asteroid_num()        
        player.start()

def events_control():
    global game

    for e in event.get():
        if e.type == QUIT:
            game = False

        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                player.fire()

def game_in_controls():
    global lose_show

    for asteroid in asteroids:
        small_rect = asteroid.rect.inflate(-20, -20)

        if small_rect.colliderect(player.rect):
            lose_show = True

def update_all():
    asteroids.update()
    bullets.update()
    player.update()

def draw_all():
    if lose_show:
        LOSE()
    asteroids.draw(window)
    bullets.draw(window)
    player.reset()

def main_controls():
    global win_show
    events_control()

    if not win_show and not lose_show:
        update_all()
        game_in_controls()
    
    hits = sprite.groupcollide(asteroids, bullets, False, True)

    for asteroid in hits:
        for bullet in hits[asteroid]:
            bullets.remove(bullet)
            bullet.kill()
        
        asteroid.start()

def main():
    global counter
    window.blit(background, (0, 0))
    main_controls()
    draw_all()

    display.update()
    clock.tick(FPS)

    counter += 1


# FENSTER ERSTELLEN

window = display.set_mode(size)
display.set_caption(caption)

# TEXTS

# Fonts

font.init()

font1 = font.Font(None, font_size)

# Labels
lose = font1.render("GAME OVER!", True, (255, 0, 0))

# SPRITES

# Asteroiden

asteroids = sprite.Group()

for i in range(num_asteroids):
    asteroid = Asteroid(asteroid_photo, 0, 0, 0, 0)
    asteroid.start()
    asteroids.add(asteroid)


# Bullets
bullets = sprite.Group()

# Player

player = Player(player_photo, 0, 0, 0, 0)
player.start()

# Background

background = transform.scale(
    image.load(background_photo),
    size
)

# GAME LOOP

while game:
    main()

# TODO 