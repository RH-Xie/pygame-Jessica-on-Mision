import pygame
import random
from pygame import font
from pygame import mixer
import csv
import button
import math
import os
path = os.getcwd()
print(path)
ROOT_PATH = path + "/"
TEXTURE_PATH = path + "/texture/"


mixer.init()
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jessica on Mission")

# set fps
clock = pygame.time.Clock()
fps = 60

# actions for player
moving_left = False
moving_right = False
grenade = False
grenade_thrown = False

# music and sounds

jump_fx = pygame.mixer.Sound(ROOT_PATH + "audio/jump.mp3")
jump_fx.set_volume(0.1)
shotgun_fx = pygame.mixer.Sound(ROOT_PATH + "audio/shotgun.mp3")
shotgun_fx.set_volume(0.1)
pistol_fx = pygame.mixer.Sound(ROOT_PATH + "audio/pistol.mp3")
pistol_fx.set_volume(0.1)
machinegun_fx = pygame.mixer.Sound(ROOT_PATH + "audio/machinegun.mp3")
machinegun_fx.set_volume(0.1)
launcher_fx = pygame.mixer.Sound(ROOT_PATH + "audio/launcher.mp3")
launcher_fx.set_volume(0.1)
explosion_fx = pygame.mixer.Sound(ROOT_PATH + "audio/explosion.mp3")
explosion_fx.set_volume(0.1)


# in-game attribute
HEAL_AMOUNT = 25

m_ammo = [15, 7, 4, 50]

# environment variable
GRAVITY = 0.75
SCROLL_THRESH = 150
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TITLE_TYPES = 21
MAX_LEVELS = 3
ENTER_COUNTER = 120 # forbid player from shooting while playing intro 
screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False
start_intro = False
all_complete = False

# background
pine1_img = pygame.image.load(TEXTURE_PATH + "bg/pine1.png").convert_alpha()
pine2_img = pygame.image.load(TEXTURE_PATH + "bg/pine2.png").convert_alpha()
mountain_img = pygame.image.load(TEXTURE_PATH + "bg/mountain.png").convert_alpha()
sky_img = pygame.image.load(TEXTURE_PATH + "bg/sky_cloud.png").convert_alpha()

# menu image
start_img = pygame.image.load(TEXTURE_PATH + "menu/start_button.png").convert_alpha()
exit_img = pygame.image.load(TEXTURE_PATH + "menu/exit_button.png").convert_alpha()
restart_img = pygame.image.load(TEXTURE_PATH + "menu/restart_button.png").convert_alpha()

# tiles
img_list = []
for x in range(TITLE_TYPES):
    img = pygame.image.load(TEXTURE_PATH + f"tiles/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    if x == 20:
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE * 2))
    img_list.append(img)
# Some image load ahead
bullet_img = pygame.image.load(TEXTURE_PATH + "items/bullet/bullet_normal.png").convert_alpha()
grenade_img = pygame.image.load(TEXTURE_PATH + "items/grenade/grenade_normal.png").convert_alpha()

heal_box_img = pygame.image.load(TEXTURE_PATH + "items/collectible/heal_box.png").convert_alpha()
ammo_box_img = pygame.image.load(TEXTURE_PATH + "items/collectible/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load(TEXTURE_PATH + "items/collectible/grenade_box.png").convert_alpha()
item_boxes = {
    "Health"    :   heal_box_img,
    "Ammo"      :   ammo_box_img,
    "Grenade"   :   grenade_box_img
}

bg = (28,28,28)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
HEAVY_GREY = (108, 108, 108)
MID_GREY = (118, 118, 118)
LIGHT_GREY = (128, 128, 128)
GREEN = (0, 255, 0)
DARK_YELLOW = (215, 175, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54, 100)

font = pygame.font.SysFont("Futura", 30)
win_font = pygame.font.SysFont("Futura", 60)

def load_image(path, num, scale):
    animation_list = []
    frame_index = 0
    for i in range(num):
        img = pygame.image.load(path + f"{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        animation_list.append(img)
    image = animation_list[frame_index]
    image_rect = image.get_rect()
    return animation_list, frame_index, image, image_rect

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(bg)
    for x in range(5):
        screen.blit(sky_img, (x * sky_img.get_width() - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, (x * mountain_img.get_width() - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, (x * pine1_img.get_width() - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, (x * pine2_img.get_width() - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

class Aimer(pygame.sprite.Sprite) :
    def __init__(self, pos, scale, type = 0):
        pygame.sprite.Sprite.__init__(self)
        if(type == 0):
            self.image = pygame.image.load(TEXTURE_PATH + "player/aimer/aimer_single.png").convert_alpha()
        else:
            self.image = pygame.image.load(TEXTURE_PATH + "player/aimer/aimer_single.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos
        self.draw()
        
    def draw(self):
        screen.blit(self.image, self.rect)
        
        

class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.face = 1

        self.jump = False
        self.vy = 0
        self.in_air = True

        self.alive = True
        self.health = 100
        self.max_health = self.health

        self.allow_shoot = False
        self.allow_melee = False
        self.shoot_cooldown = 0
        self.melee_cooldown = 0
        self.animation_frame = 0
        self.start_ammo = ammo
        self.ammo = m_ammo[0]
        self.shotgun_ammo = m_ammo[1]
        self.launcher_ammo = m_ammo[2]
        self.machinegun_ammo = m_ammo[3]
        self.ammo_type = "pistol"
        self.type = 0

        self.grenades = grenades
        
        # For enemy and npc soldiers
        self.flip = False
        self.update_time = pygame.time.get_ticks()
        self.animation_list, self.frame_index, self.image, self.rect = load_image(TEXTURE_PATH + f"{self.char_type}/idle/", 2, scale)
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        # Animations
        self.melee_animation, self.melee_frame_index, self.melee_image, self.melee_image_rect = load_image(TEXTURE_PATH + f"{self.char_type}/melee/knife/melee", 5, scale)
        self.run_animation, self.run_frame_index, self.run_image, self.run_image_rect = load_image(TEXTURE_PATH + f"{self.char_type}/run/", 5, scale)
        self.aimer = Aimer(self.rect, 1.0, 0)

        self.dismish = 150
        self.death_animation = []
        self.death_frame_index = 0
        for i in range(5):
            img = pygame.image.load(TEXTURE_PATH + f"{self.char_type}/death/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.death_animation.append(img)
        self.death_image = self.death_animation[self.death_frame_index]
        self.death_image_rect = self.death_image.get_rect()
    def update(self):
        self.update_animation()
        self.check_alive()
        self.aimer.update()
        if self.flip == True :
            flip_direction = -1
        else:
            flip_direction = 1
        self.melee_image_rect.centerx = self.rect.centerx + flip_direction * (self.width // 3)
        self.melee_image_rect.centery = self.rect.centery
        self.melee()
        if self.shoot_cooldown > 0 :
            self.shoot_cooldown -= 1
        if self.melee_cooldown > 0 :
            self.melee_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        # more suitable for collision check
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vy = -11
            self.jump = False
            self.in_air = True

        self.vy += GRAVITY
        if self.vy > 10: 
            self.vy
        dy += self.vy

        # collider for x and y axis
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                if self.vy < 0:
                    self.vy = 0
                    # dy down to zero, no more space to up
                    # dy = tile[1].bottom - self.rect.top
                    dy = 0
                elif self.vy >= 0:
                    self.vy = 0
                    self.in_air = False
                    # dy = tile[1].top - self.rect.bottom
                    dy = 0
        # drown
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        
        # tp
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # out of map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
            

        self.rect.x += dx
        self.rect.y += dy
        
        # scrolling
        if self.char_type == "player":
            if ((self.rect.right > SCREEN_WIDTH - SCROLL_THRESH - 200 and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx))):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def update_animation(self):
        pos = pygame.mouse.get_pos()
        if (pos[0] - self.rect.centerx > 0):
            self.face = 1
            self.flip = False
        else:
            self.face = -1
            self.flip = True
        ANIMATION_COOLDOWN = 100
        if self.alive == True:
            if not moving_left and not moving_right:
                self.image = self.animation_list[self.frame_index]
                if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                    self.frame_index += 1
                    self.update_time = pygame.time.get_ticks()
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0

            elif moving_left or moving_right:
                self.image = self.run_animation[self.run_frame_index]
                if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                    self.run_frame_index += 1
                    self.update_time = pygame.time.get_ticks()
                if self.run_frame_index >= len(self.run_animation):
                    self.run_frame_index = 0
        else:
            self.image = self.death_animation[self.death_frame_index]
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.death_frame_index += 1
                self.update_time = pygame.time.get_ticks()
            if self.death_frame_index >= len(self.death_animation):
                self.death_frame_index = len(self.death_animation) - 1
                if self.dismish > 0:
                    self.dismish -= 1
                else:
                    self.kill()



    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        # Show collide box:
        # pygame.draw.rect(screen, RED, self.rect, 1)

    def shoot(self):
        if self.ammo_type == "shotgun":
            current_ammo = self.shotgun_ammo
        elif self.ammo_type == "pistol":
            current_ammo = self.ammo
        elif self.ammo_type == "launcher":
            current_ammo = self.launcher_ammo
        elif self.ammo_type == "machinegun":
            current_ammo = self.machinegun_ammo
        pos = pygame.mouse.get_pos()
        if self.shoot_cooldown == 0 and self.allow_shoot:
            if self.ammo_type == "pistol" and self.ammo > 0:
                self.shoot_cooldown = 20
                self.ammo -= 1
                bullet = PlayerBullet(self.rect.centerx, self.rect.centery, self.face, pos, self.ammo_type)
                bullet_group.add(bullet)

            elif self.ammo_type == "shotgun" and self.shotgun_ammo > 0:
                self.shoot_cooldown = 20
                self.shotgun_ammo -= 1
                bullet = PlayerBullet(self.rect.centerx, self.rect.centery, self.face, pos, self.ammo_type)
                bullet_group.add(bullet)

            elif self.ammo_type == "machinegun" and self.machinegun_ammo > 0:
                self.shoot_cooldown = 5
                self.machinegun_ammo -= 1
                bullet = PlayerBullet(self.rect.centerx, self.rect.centery, self.face, pos, self.ammo_type)
                bullet_group.add(bullet)

            elif self.ammo_type == "launcher" and self.launcher_ammo > 0:
                self.shoot_cooldown = 20
                self.launcher_ammo -= 1
                bullet = PlayerBullet(self.rect.centerx, self.rect.centery, self.face, pos, self.ammo_type)
                bullet_group.add(bullet)
            m_ammo[0] = self.ammo
            m_ammo[1] = self.shotgun_ammo
            m_ammo[2] = self.launcher_ammo
            m_ammo[3] = self.machinegun_ammo
            self.allow_shoot = False

    def switch_weapon(self):
        if(self.type >= 3):
            self.type = 0
        else:
            self.type += 1
        type_list = ["pistol", "shotgun","launcher","machinegun"]
        self.ammo_type = type_list[self.type]
                            

    def melee(self):
        if(self.melee_frame_index >= 5):
            self.melee_frame_index = 0
            self.melee_cooldown = 20
            self.allow_melee = False
            
        
        if self.melee_cooldown == 0 and self.allow_melee:
            screen.blit(pygame.transform.flip(self.melee_animation[self.melee_frame_index], self.flip, False), self.melee_image_rect)
            if(self.animation_frame != 0):
                self.animation_frame -= 1
            else:
                
                self.melee_frame_index += 1
                self.animation_frame = 4
            for enemy in enemy_group:
                if abs(self.melee_image_rect.centerx - enemy.rect.centerx) < TILE_SIZE and \
                    abs(self.melee_image_rect.centery - enemy.rect.centery) < TILE_SIZE:
                    enemy.health -= 60


    def check_alive(self):
        if self.health <= 0 :
            self.health = 0
            self.speed = 0
            self.alive = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.dismish = 200

        self.jump = False
        self.vy = 0
        self.in_air = True

        self.alive = True
        self.health = 100
        self.max_health = self.health

        self.allow_shoot = False
        self.shoot_cooldown = 0
        self.start_ammo = ammo
        self.ammo = ammo

        self.grenades = grenades
        
        # For enemy 
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 400, 20)
        self.reaction_time = 30

        self.flip = False
        self.animation_cooldown = 10
        self.animation_cooldown_death = 10
        self.update_time = pygame.time.get_ticks()
        self.animation_list, self.frame_index, self.image, self.rect = load_image(TEXTURE_PATH + f"{self.char_type}/idle/", 5, scale)
        self.run_animation_list, self.run_frame_index, self.run_image, self.run_rect = load_image(TEXTURE_PATH + f"{self.char_type}/run/", 6, scale)
        self.death_animation_list, self.death_frame_index, self.death_image, self.death_rect = load_image(TEXTURE_PATH + f"{self.char_type}/death/", 8, scale)
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0 :
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # more suitable for collision check
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vy = -11
            self.jump = False
            self.in_air = True

        self.vy += GRAVITY
        if self.vy > 10: 
            self.vy
        dy += self.vy

        # collider for x and y axis
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                if self.vy < 0:
                    self.vy = 0
                    # dy down to zero, no more space to up
                    # dy = tile[1].bottom - self.rect.top
                    dy = 0
                elif self.vy >= 0:
                    self.vy = 0
                    self.in_air = False
                    # dy = tile[1].top - self.rect.bottom
                    dy = 0
        # drown
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        
        # tp
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # out of map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
            

        self.rect.x += dx
        self.rect.y += dy
        
        # scrolling
        if self.char_type == "player":
            if ((self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx))):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.idling = True
                self.idling_counter = 120
            # engage with player while in vision, thus stop to fire
            if self.vision.colliderect(player.rect):
                if(self.reaction_time > 0):
                    self.reaction_time -= 1
                else:
                    self.idling_counter -= 1
                    self.idling = True
                    self.allow_shoot = True
                    self.shoot()
            else:
                self.reaction_time = 30
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                        ai_moving_left = not ai_moving_right
                    else:
                        ai_moving_left = True
                        ai_moving_right = not ai_moving_left
                    self.idling
                    self.move(ai_moving_left, ai_moving_right)
                    self.move_counter += 1
                    # vision update
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # vision collidebox
                    # pygame.draw.rect(screen, RED, self.vision)
                    if self.move_counter >= TILE_SIZE:
                        self.direction *= -1
                        self.move_counter = 0
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100


        if self.alive == True:
            if self.idling:
                self.image = self.animation_list[self.frame_index]
                if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                    self.frame_index += 1
                    self.update_time = pygame.time.get_ticks()
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0

            else :
                if(self.animation_cooldown > 0):
                    self.animation_cooldown -= 1
                else:
                    self.image = self.run_animation_list[self.run_frame_index]
                    self.run_frame_index += 1
                    if self.run_frame_index >= len(self.run_animation_list):
                        self.run_frame_index = 0
                    self.animation_cooldown = 10
        else:
            self.image = self.death_animation_list[self.death_frame_index]
            if self.death_frame_index == len(self.death_animation_list) - 1:
                if self.dismish > 0:
                    self.dismish -= 1
                else:
                    self.kill()
            else:
                if self.animation_cooldown_death == 0:
                    self.death_frame_index += 1
                    self.animation_cooldown_death = 10
                else:
                    self.animation_cooldown_death -= 1

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        # Show collide box:
        # pygame.draw.rect(screen, RED, self.rect, 1)

    def shoot(self):

        pos = pygame.mouse.get_pos()
        if self.shoot_cooldown == 0 and self.allow_shoot and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = EnemyBullet(self.rect.centerx + self.direction * 0.75 * (self.rect.size[0]), self.rect.centery, self.direction)
            bullet_group.add(bullet)

            self.ammo -= 1

    def check_alive(self):
        if self.health <= 0 :
            self.health = 0
            self.speed = 0
            self.alive = False


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Player("player", x * TILE_SIZE, y * TILE_SIZE, 0.7, 3, 10, 5)
                        player.ammo = m_ammo[0]
                        player.shotgun_ammo = m_ammo[1]
                        player.launcher_ammo = m_ammo[2]
                        player.machinegun_ammo = m_ammo[3]
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Enemy("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.6, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # move when scrolling
        self.rect.x += screen_scroll
        # Collision check
        if pygame.sprite.collide_rect(self, player):
            retain_or_not = False
            if self.item_type == "Health":
                if player.health + HEAL_AMOUNT >= player.max_health:
                    player.health = player.max_health
                else:
                    player.health += HEAL_AMOUNT
                    retain_or_not = True
            elif self.item_type == "Ammo":
                player.ammo += 7
                player.shotgun_ammo += 4
                player.machinegun_ammo += 20
                player.launcher_ammo += 1
                m_ammo[0] = player.ammo
                m_ammo[1] = player.shotgun_ammo
                m_ammo[2] = player.launcher_ammo
                m_ammo[3] = player.machinegun_ammo
            elif self.item_type == "Grenade":
                player.grenades += 3
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, self.x + 144 , self.y + 14))
        pygame.draw.rect(screen, HEAVY_GREY, (self.x, self.y, self.x + 140 , self.y + 10))
        if(ratio >= 0.6):
            pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
        elif(ratio < 0.6 and ratio >= 0.4):
            pygame.draw.rect(screen, DARK_YELLOW, (self.x, self.y, 150 * ratio, 20))
        elif(ratio < 0.4):
            pygame.draw.rect(screen, RED, (self.x, self.y, 150 * ratio, 20))

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 12
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        # check whether bullets go out of or not
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # collide check for blocks
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # collide check whether entity is dead
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                self.kill()
                player.health -= 5


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, face, pos, ammo_type):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 30
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.face = face
        self.pos = pos
        self.vy = 0
        self.distance = abs(math.dist((x,y), pos))
        self.ammo_type = ammo_type
        if(ammo_type == "pistol"):
            pistol_fx.play()
        if(ammo_type == "machinegun"):
            machinegun_fx.play()
        if(ammo_type == "shotgun"):
            self.speed = 20
            self.shotgun_accuracy = 0.10
            shotgun_fx.play()
            for i in range(0,4):
                if i % 2 == 0:
                    order = i
                else:
                    order = i * (-1)
                sub_bullet = PlayerBullet(x, y, face, (pos[0] + self.shotgun_accuracy * self.distance * order, pos[1] + self.shotgun_accuracy * self.distance * order ), "none")
                bullet_group.add(sub_bullet)
        if(ammo_type == "launcher"):
            self.speed = 14
            launcher_fx.play()
        
        if pos[1] - y > 0:
            self.below = True
        else:
            self.below = False
        if pos[1] - y != 0 or pos[0] - x != 0:
            self.theta = abs(math.atan((pos[1] - y) / (pos[0] - x)))
        else:
            self.theta = 0

    def update(self):
        self.vy += GRAVITY * 0.05
        self.rect.x += (self.face * self.speed * math.cos(self.theta))
        if(self.ammo_type == "launcher"):
            if self.below :
                self.rect.y += (self.speed * math.sin(self.theta)) + self.vy * self.speed
            else:
                self.rect.y -= (self.speed * math.sin(self.theta) ) - self.vy * self.speed
            # check whether bullets go out of or not
            if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()
        else:

            if self.below :
                self.rect.y += (self.speed * math.sin(self.theta))
            else:
                self.rect.y -= (self.speed * math.sin(self.theta))
            # check whether bullets go out of or not
            if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()
        # collide check for blocks
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                if(self.ammo_type == "launcher"):
                    explosion = Explosion(self.rect.x,self.rect.y, 0.7)
                    explosion_group.add(explosion)
                    for enemy in enemy_group:
                        if abs(explosion.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                            abs(explosion.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                            enemy.health -= 110


        # collide check whether entity is dead
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    self.kill()
                    if(self.ammo_type == "launcher"):
                        explosion = Explosion(self.rect.x,self.rect.y, 0.7)
                        explosion_group.add(explosion)
                        for enemy in enemy_group:
                            if abs(explosion.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                                abs(explosion.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                                enemy.health -= 110
                    if(self.ammo_type == "shotgun" or "none"):
                        for enemy in enemy_group:
                            if enemy.rect.colliderect(self.rect):
                                enemy.health -= 25
                    if(self.ammo_type == "pistol"):
                        for enemy in enemy_group:
                            if enemy.rect.colliderect(self.rect):
                                enemy.health -= 50
                    if(self.ammo_type == "machinegun"):
                        for enemy in enemy_group:
                            if enemy.rect.colliderect(self.rect):
                                enemy.health -= 45




class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.max_vy = -10
        self.vy = self.max_vy
        self.speed = 7
        self.scale = 0.7

        self.image = pygame.transform.scale(grenade_img, (int(grenade_img.get_width() * self.scale), int(grenade_img.get_height() * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.height = self.image.get_height()
        self.width = self.image.get_width()
    def update(self):
        self.vy += GRAVITY
        dy = self.vy
        dx = self.direction * self.speed

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                if self.vy < 0:
                    self.vy = 0
                    dy = tile[1].bottom - self.rect.top
                    self.speed -= 6
                elif self.vy >= 0:
                    self.max_vy *= 0.3
                    self.vy = self.max_vy
                    if(self.speed > 0):
                        self.speed -= 1
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown for explosion
        self.timer -= 1
        if(self.timer <= 0):
            self.kill()
            explosion = Explosion(self.rect.x,self.rect.y, 0.8)
            explosion_group.add(explosion)

            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 110
            
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(TEXTURE_PATH + f"items/grenade/explosion{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
        explosion_fx.play()

    def update(self):
        
       self.rect.x += screen_scroll
       # how fast it shows
       EXPLOSION_SPEED = 4
       self.counter += 1

       if self.counter >= EXPLOSION_SPEED:
           self.counter = 0
           self.frame_index += 1
           if self.frame_index >= len(self.images):
               self.kill()
           else:
               self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1:
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        if self.direction == 2:
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete = True

        return fade_complete

intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

start_btn = button.Button(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 150, start_img, 3 )
exit_btn = button.Button(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 50, exit_img, 3 )
restart_btn = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 300, restart_img, 3 )

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()




world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(ROOT_PATH + f"level{level}_data.csv", newline = "") as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
enter_counter = ENTER_COUNTER
music_counter = 0
while run:
    clock.tick(fps)
    if start_game == False:
        # before entering game
        if(music_counter == 0):
            pygame.mixer.music.load(ROOT_PATH + "audio/Synthetech.mp3")
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1, 0.0, 5000)
            music_counter += 1
        screen.fill(bg)
        if start_btn.draw(screen):
            start_game = True
            start_intro = True
        if exit_btn.draw(screen):
            run = False
    else:
        if enter_counter > 0:
            pygame.mixer.music.load(ROOT_PATH + "audio/bg_LastReunion.mp3")
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1, 0.0, 5000)
            enter_counter -= 1
        draw_bg()
        world.draw()

        draw_text(f"AMMO: ", font, WHITE, 10, 35)
        if(player.type == 0) :
            ammo = player.ammo
        if(player.type == 1) :
            ammo = player.shotgun_ammo
        if(player.type == 2) :
            ammo = player.launcher_ammo
        if(player.type == 3) :
            ammo = player.machinegun_ammo
        if (ammo > 0):
            for x in range(ammo):
                screen.blit(bullet_img, (90 + (x * 10), 35))
        draw_text(f"GRENADE: ", font, WHITE, 10, 60)

        type_list = ["pistol", "shotgun","launcher","machinegun"]
        draw_text(f"WEAPON: " + player.ammo_type, font, WHITE, 10, 85)
        for x in range(player.grenades):
            icon_grenade_img = pygame.transform.scale(grenade_img, (int(grenade_img.get_width() * 0.8), int(grenade_img.get_height() * 0.8)))
            screen.blit(icon_grenade_img, (135 + (x * 25), 50))
        health_bar.draw(player.health)

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        bullet_group.update()
        bullet_group.draw(screen)
        grenade_group.update()
        grenade_group.draw(screen)
        explosion_group.update()
        explosion_group.draw(screen)
        item_box_group.update()
        item_box_group.draw(screen)
        decoration_group.update()
        decoration_group.draw(screen)
        water_group.update()
        water_group.draw(screen)
        exit_group.update()
        exit_group.draw(screen)

        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            if player.allow_shoot:
                player.shoot()
            # either shoot or throw
            elif grenade and grenade_thrown == False and player.grenades > 0:
                if player.flip:
                    m_direction = -1
                else:
                    m_direction = 1
                grenade = Grenade(player.rect.centerx + (player.rect.size[0] * 0.6 * m_direction), player.rect.top , m_direction)
                grenade_group.add(grenade)
                player.grenades -= 1
                grenade_thrown = True
            screen_scroll, level_complete = player.move(moving_left ,moving_right)
            bg_scroll -= screen_scroll

            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0 
                world_data = reset_level()
                if level > MAX_LEVELS:
                    level -= 1
                    all_complete = True
                with open(ROOT_PATH + f"level{level}_data.csv", newline = "") as csvfile:
                    reader = csv.reader(csvfile, delimiter = ',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)
            if all_complete:
                draw_text("You Win", win_font, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
                if restart_btn.draw(screen):
                    all_complete = False
                    # distance from start point, reset when restart
                    bg_scroll = 0
                    world_data = reset_level()
                    level = 0
                    with open(ROOT_PATH + f"level{level}_data.csv", newline = "") as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_btn.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    # distance from start point, reset when restart
                    bg_scroll = 0
                    world_data = reset_level()

                    with open(ROOT_PATH + f"level{level}_data.csv", newline = "") as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
    for event in pygame.event.get():
        # check quit
        if event.type == pygame.QUIT:
            run = False
        # keyboard input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_g:
                grenade = True
            if event.key == pygame.K_f:
                player.allow_melee = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_fx.play()
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_g:
                grenade = False
                grenade_thrown = False
            if event.key == pygame.K_q:
                player.switch_weapon()
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = False
        # mouse

        if pygame.mouse.get_pressed()[0] == 1 and enter_counter == 0:
            player.allow_shoot = True
        else:
            player.allow_shoot = False
    pygame.display.update()
pygame.quit()
