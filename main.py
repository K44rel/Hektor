from sprites import *
from os import path
import time

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.bg = pg.image.load("background.png").convert()
        self.island = pg.image.load("maintower.png").convert_alpha()
        self.startscreen = pg.image.load("startscreen.png")
        self.goscreen = pg.image.load("GameOver.png")
        pg.display.set_caption(TITLE)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.clock = pg.time.Clock()
        self.running = True
        self.load_data()
        self.towerhp = TOWERHP
        self.mobfreq = MOBFREQ
        self.level = STARTLEVEL
    
    def load_data(self):
        self.dir = path.dirname(__file__)
        self.spritesheet = Spritesheet("spritesheet.png")
        with open(path.join(self.dir, HS_FILE), "r") as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
    
    def new(self, score, towerhp):
        self.score = score
        self.towerhp = towerhp
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.islands = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        self.plates = pg.sprite.Group()
        self.collisions = pg.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.mobs)
        self.all_sprites.add(self.bullets)
        self.all_sprites.add(self.islands)
        self.all_sprites.add(self.clouds)
        self.all_sprites.add(self.collisions)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        for plate in PLATE_LIST:
            plate = Plate(self,*plate)
            self.all_sprites.add(plate)
            self.plates.add(plate)
        self.mob_timer = 0
        self.island_timer = 0
        self.cloud_timer = 0
        self.run()
    
    def run(self):
        self.clock.tick(FPS)
        self.playing = True
        self.start_time = time.time()
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
    
    def update(self):
        self.all_sprites.update()
        now = pg.time.get_ticks()
        self.g_time = time.time() - self.start_time

        if self.g_time >= LVLLEN:
            self.level += 1
            self.mobfreq -= SPAWNSPEED
            self.new(self.score, self.towerhp)

        if now - self.mob_timer > 3 * self.mobfreq + random.choice([-0.5 * self.mobfreq, -0.25 * self.mobfreq, 0, 0.25 * self.mobfreq, 0.5 * self.mobfreq]):
            self.mob_timer = now
            Mob(self)

        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.playing = False

        if self.player.pos.y > HEIGHT:
            self.playing = False
        
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                if self.player.pos.y < hits[0].rect.bottom:
                    self.player.pos.y = hits[0].rect.top + 1
                    self.player.vel.y = 0

        if now - self.island_timer > 5000 + random.randint(-2500, 2500):
            if len(self.islands) < 15:
                self.island_timer = now
                Island(self)

        if now - self.cloud_timer > 5000 + random.randint(-2500, 2500):
            if len(self.clouds) < 15:
                self.cloud_timer = now
                Cloud(self)

        if self.towerhp <= 0:
            self.playing = False


    
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.player.jump()
                elif event.key == pg.K_SPACE:
                    self.shoot()
                    
    def shoot(self):
        Bullet(self, self.player.rect.centerx, self.player.rect.centery)
    
    def draw(self):
        self.screen.blit(self.bg, [0, 0])
        self.screen.blit(self.island, [0,0])
        self.all_sprites.draw(self.screen)
        self.draw_text("Score: " + str(self.score), 10, WHITE, 73, 22)
        self.draw_text("Level: " + str(self.level), 10, WHITE, 73, 52)
        self.draw_text("Level time: " + str(LVLLEN - int(self.g_time)), 10, WHITE, 73, 82)
        self.draw_text("Tower HP: " + str(self.towerhp), 10, WHITE,635, 42)
        pg.display.flip()
    
    def show_start_screen(self):
        self.screen.blit(self.startscreen, [0, 0])
        self.draw_text(str(self.highscore), 40, BLACK, 1165, 320)
        pg.display.flip()
        self.wait_for_key(pg.K_n)

    def show_go_screen(self):
        self.screen.blit(self.goscreen, [0, 0])
        self.draw_text(str(self.score), 30, BLACK, 460, 173)
        self.draw_text(str(self.level), 30, BLACK, 900, 165)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HI-SCORE!", 25, BLACK, 857, 230)
            self.draw_text(str(self.highscore), 30, BLACK, 910, 262)
            with open(path.join(self.dir, HS_FILE), "w") as f:
                f.write(str(self.score))
        else:
            self.draw_text(str(self.highscore), 30, BLACK, 910, 262)
        pg.display.flip()
        self.mobfreq = MOBFREQ
        self.wait_for_key(pg.K_n)

    def wait_for_key(self, key):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == key:
                        waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new(0, 100)
    g.run()
    g.show_go_screen()
    
pg.quit()