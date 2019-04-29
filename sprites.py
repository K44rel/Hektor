from settings import *
import pygame as pg
import random
vec = pg.math.Vector2


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image
        

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self.layer = 1
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.walk_frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "R"
        
    def load_images(self):
        self.walk_frames_l = [self.game.spritesheet.get_image(0, 0, 32, 32),
                              self.game.spritesheet.get_image(0, 32, 32, 32)]
        for frame in self.walk_frames_l:
            frame.set_colorkey(WHITE)
        self.walk_frames_r = [self.game.spritesheet.get_image(32, 0, 32, 32),
                              self.game.spritesheet.get_image(32, 32, 32, 32)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(WHITE)


    def jump(self):
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1
        if hits:
            self.vel.y = -8

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        
        self.rect.midbottom = self.pos
        
    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                    self.direction = "R"
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.direction = "L"


class Island(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = random.randint(3,4)
        self.game = game
        self.groups = game.all_sprites, game.islands
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_images()
        self.image = self.islands[random.randint(0,1)]
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-40, WIDTH + 40])
        self.rect.y = random.randint(340,HEIGHT - 64)
        self.vel = 1
        if self.rect.centerx > WIDTH:
            self.vel *= -1

    def load_images(self):
        self.islands = [self.game.spritesheet.get_image(0, 72, 32, 32),
                       self.game.spritesheet.get_image(64, 72, 64, 58)]
        for island in self.islands:
            island.set_colorkey(WHITE)

    def update(self):
        self.rect.x += self.vel
        if self.rect.centerx > WIDTH + 41 or self.rect.centerx < -40:
            self.kill()


class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = random.randint(3,4)
        self.game = game
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_images()
        self.image = self.clouds[random.randint(0,1)]
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-40, WIDTH + 40])
        self.rect.y = random.randint(20,HEIGHT - 128)
        self.vel = 1
        if self.rect.centerx > WIDTH:
            self.vel *= -1

    def load_images(self):
        self.clouds = [self.game.spritesheet.get_image(128, 0, 64, 64).convert(),
                       self.game.spritesheet.get_image(192, 0, 64, 64).convert()]
        for cloud in self.clouds:
            cloud.set_colorkey(BLACK)

    def update(self):
        self.rect.x += self.vel
        if self.rect.centerx > WIDTH + 41 or self.rect.centerx < -40:
            self.kill()


class Plate(pg.sprite.Sprite):
    def __init__(self, game,x, y):
        self._layer = 5
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.image = self.game.spritesheet.get_image(128, 64, 128, 32).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.groups = game.all_sprites, game.mobs
        self._layer = 1
        pg.sprite.Sprite.__init__(self, self.groups)
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.fly_frames_r[0]
        self.rect = self.image.get_rect()
        self.vx = random.randrange(1, 4)
        self.side = random.randint(1,2)
        if self.side == 1:
            self.rect.centerx = WIDTH + 100
            self.vx *= -1
        else:
            self.rect.centerx = -100
        self.rect.y = random.randint(100, 330)
        self.startpos = self.rect.centerx


    def load_images(self):
        self.fly_frames_l = [self.game.spritesheet.get_image(64, 0, 32, 32),
                              self.game.spritesheet.get_image(64, 32, 32, 32)]
        for frame in self.fly_frames_l:
            frame.set_colorkey(WHITE)
        self.fly_frames_r = [self.game.spritesheet.get_image(96, 0, 32, 32),
                              self.game.spritesheet.get_image(96, 32, 32, 32)]
        for frame in self.fly_frames_r:
            frame.set_colorkey(WHITE)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 300:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.fly_frames_l)
            if self.vx > 0:
                self.image = self.fly_frames_r[self.current_frame]
                self.direction = "R"
            else:
                self.image = self.fly_frames_l[self.current_frame]
                self.direction = "L"

    def update(self):
        self.animate()
        if self.startpos == WIDTH + 100:
            if self.rect.centerx  <= 695:
                self.game.towerhp -= 10
                Collison(self.game,self.rect.centerx + 25,self.rect.centery, "L")
                self.kill()
        if self.startpos == -100:
            if self.rect.centerx >= 570:
                self.game.towerhp -= 10
                Collison(self.game, self.rect.centerx - 30, self.rect.centery, "R")
                self.kill()
        bullet_hits = pg.sprite.groupcollide(self.game.bullets, self.game.mobs, True, True)
        if bullet_hits:
            self.game.score += 10
        self.rect.x += self.vx


class Collison(pg.sprite.Sprite):
    def __init__(self, game, x, y, s):
        self.direction = s
        self.game = game
        self.groups = game.all_sprites, game.collisions
        self._layer = 2
        pg.sprite.Sprite.__init__(self, self.groups)
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.collideframes_r[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def load_images(self):
        self.collideframes_l = [self.game.spritesheet.get_image(0, 192, 64, 64),
                             self.game.spritesheet.get_image(64, 192, 64, 64),
                             self.game.spritesheet.get_image(128, 192, 64, 64),
                             self.game.spritesheet.get_image(192, 192, 64, 64)]
        for frame in self.collideframes_l:
            frame.set_colorkey(WHITE)
        self.collideframes_r = [self.game.spritesheet.get_image(192, 256, 64, 64),
                             self.game.spritesheet.get_image(128, 256, 64, 64),
                             self.game.spritesheet.get_image(64, 256, 64, 64),
                             self.game.spritesheet.get_image(0, 256, 64, 64)]
        for frame in self.collideframes_r:
            frame.set_colorkey(WHITE)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 100:
            if self.current_frame == 3:
                self.kill()
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % 4
            if self.direction == "R":
                self.image = self.collideframes_r[self.current_frame]
            else:
                self.image = self.collideframes_l[self.current_frame]

    def update(self):
        self.animate()

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        player = game.player
        if player.direction == "R":
            self.speedx = 10
            self.image = self.game.spritesheet.get_image(16, 64, 8, 8)
            self.image.set_colorkey(WHITE)
            self.rect = self.image.get_rect()
            self.rect.bottom = y + random.randint(-5,5)
            self.rect.centerx = x
        elif player.direction == "L":
            self.speedx = -10
            self.image = self.game.spritesheet.get_image(0, 64, 8, 8)
            self.image.set_colorkey(WHITE)
            self.rect = self.image.get_rect()
            self.rect.bottom = y + random.randint(-5,5)
            self.rect.centerx = x
            
    def update(self):
        self.rect.x += self.speedx
        if self.rect.centerx > WIDTH or self.rect.centerx < 0:
            self.kill()
