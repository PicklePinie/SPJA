import sys
from random import Random
import time
from utils import Cooldown

import pygame
from pygame.locals import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_SPACE, KEYDOWN, KEYUP

from utils import load_image

EVENT_SPAWN_ENEMY = pygame.USEREVENT

"""
Implement the following functionality into the game:

(1 point)
Periodically spawn an enemy at the top of the window (@Engine.spawn_enemy).                 
The starting X position of the enemy should be random (and within the window width).
The enemy will move down in every frame according to its speed and delta (@Enemy.update).

(1 point)
Store health for the player and draw it in every frame below the score (@Player).           

(2 points)
When the enemy hits the player, kill the enemy and decrease player health (@Enemy.update).
When the enemy moves out of the window, kill enemy an decrease player health.
When player health reaches zero, end the program.                                           
    + randomly select enemy image (enemy1-5.gif) (0.5 points)
    + assign different starting health and score to the enemy according to its image (0.5 points)

(3 points)
When the player presses space, create a missile at the location of the player (@Player.handle_keys).
The missile will move up in every frame (@Missile.update).
When the missile hits an enemy, decrease the enemy's health according to the missile's damage.
If this kills the enemy, remove the enemy and add its score to player.
Remove the missile after it hits an enemy or leaves the window.                            
    + add cooldown to the missile firing (e.g. you can only fire once every 100 ms) (0.5 points)
    + play a sound when an enemy explodes (0.5 points)
    + add an explosion animation to the game for 2 seconds when an enemy explodes (1 bonus point)


Use the delta time in update method for all movements and animations.

Documentation: https://www.pygame.org/docs/index.html
Cheatsheet:
    # (pseudo-)random numbers
    import random
    r = random.Random()
    r.random()              # random number between in range (0, 1)
    r.randint(3, 5)         # random number in range [3, 5]
    r.choice([1, 2, 3])     # randomly select item from collection

    X coordinate is increasing from left to right
    Y coordinate is increasing from top to bottom

    # sprite groups
    g = pygame.sprite.Group()   # group of sprites
    e = Enemy(...)              # create sprite
    g.add(e)                    # add sprite to group
    g.update(arg1, arg2, ...)   # call .update(arg1, arg2, ...) on all sprites in group
    e.kill()                    # automatically remove sprite from all groups

    img = load_image('images/...')  # load image
    rect = img.get_rect()           # get image rectangle
    rect.center = (50, 50)          # set image center to (50, 50)

    surface.blit(img, rect)         # draw `img` at position specified by rectangle `rect`

    for sprite in g:                # draw all sprites from group
        g.draw(surface)

    engine.screen                   # window screen
    engine.screen.get_width()       # window width
    engine.screen.get_height()      # window height

    def update(self, engine, delta):
        self.rect = self.rect.move(500 * delta, 0) # move rectangle in X axis by 500 * delta

    from utils import Cooldown
    cd = Cooldown(500)          # 500 ms cooldown
    cd.update(delta)            # update cooldown in every frame
    if cd.reset_if_ready():     # returns True if CD is ready and resets it if its ready

    def handle_keys(self, event):
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                pass

    # return all sprites from collection `items` that collide with `player`
    collisions = pygame.sprite.spritecollide(player, items, False)
    if collisions:
        for item in collisions: # remove all items that collided with `player`
            item.kill()
"""


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos


    def update(self, engine, delta):
        pass


    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Missile(GameObject):
    def __init__(self, player, pos, damage=20, speed=700):
        super().__init__(load_image('images/bullet.gif'), pos)

        self.player = player
        self.damage = damage
        self.speed = speed


    def update(self, engine, delta):
        if self.rect.bottom < 0:
            self.kill()
        else:
            self.rect = self.rect.move(0, self.speed * -delta)

        for enemy in engine.enemies:
            if enemy.is_exploding():
                continue
            if(
                self.rect.bottom > enemy.rect.top and self.rect.top < enemy.rect.bottom and
                self.rect.right > enemy.rect.left and self.rect.left < enemy.rect.right
            ):
                enemy.health -= 10
                self.kill()
            if enemy.health <1:
                engine.player.score += enemy.score
                enemy.explosion()


class Enemy(GameObject):
    def __init__(self,  image, pos, player, health=100, score=10, speed=100):
        super().__init__(image, pos)

        self.health = health
        self.score = score
        self.speed = speed
        self.player = player
        self.booms = []
        self.explosion_frame = -1

    def is_exploding(self):
        return self.explosion_frame >= 0


    def explosion(self):
        self.explosion_frame = 0
        if self.rect.top < engine.screen.get_height():
            pygame.mixer.music.load('sound/explosion.wav')
            pygame.mixer.music.play(0)
            spritesheet = pygame.image.load('images/explosion_anim.jpg').convert()

            i = 0
            while i < 193:
                j = 0
                while j < 193:
                   # print(str(i) + "," + str(j))
                    self.booms.append(spritesheet.subsurface(pygame.Rect(j, i, 64, 64)))
                    j += 64
                i += 64


    def update(self, engine, delta):
        if self.explosion_frame >= len(self.booms):
            self.kill()
            self.explosion_frame = -1
            return

        if self.explosion_frame >= 0:
            self.image = self.booms[self.explosion_frame]
            self.explosion_frame += 1
            return
        #print(self.explosion_frame)

        if self.rect.top <= engine.screen.get_height():
            self.rect = self.rect.move(0, self.speed * delta)

        if not self.is_exploding():
            if self.rect.top > engine.screen.get_height() or (
                self.rect.bottom > self.player.rect.top + 5 and self.rect.top < self.player.rect.bottom and
                self.rect.right > self.player.rect.left and self.rect.left < self.player.rect.right
            ):
                self.player.health -= 1
                self.explosion()

        if self.player.health < 1:
            engine.end()


class Player(GameObject):
    def __init__(self, engine, pos):
        super().__init__(load_image('images/plane.gif'), pos)

        self.image_straight = self.image
        self.image_left = load_image('images/plane_turning_right_1.gif')
        self.image_right = load_image('images/plane_turning_left_1.gif')

        self.engine = engine
        self.speed = [0, 0]  # [x, y]
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.health = 3 ####
        self.cd = Cooldown(100)


    def handle_keys(self, event):
        speed_value = 500
        arrows = (K_RIGHT, K_LEFT, K_UP, K_DOWN)

        if event.type == KEYDOWN:
            if event.key == K_SPACE and self.cd.ready :
                missile = Missile(self, self.rect.center)
                engine.missiles.add(missile)
                self.cd.reset()

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.speed[0] = speed_value
                self.image = self.image_right
            elif event.key == K_LEFT:
                self.speed[0] = -speed_value
                self.image = self.image_left
            elif event.key == K_UP:
                self.speed[1] = -speed_value
            elif event.key == K_DOWN:
                self.speed[1] = speed_value
        elif event.type == KEYUP:
            if event.key in arrows:
                self.speed = [0, 0]
                self.image = self.image_straight


    def update(self, engine, delta):
        self.cd.update(delta)
        x, y = self.speed
        rect = self.rect
        self.rect = self.rect.move(x * delta, y * delta)
        if (self.rect.left <= 0 or
                self.rect.right >= engine.screen.get_width() or
                self.rect.top <= 0 or
                self.rect.bottom >= engine.screen.get_height()):
            self.rect = rect


    def draw(self, surface):
        super().draw(surface)
        self.draw_status(surface)


    def draw_status(self, screen):
        if pygame.font:
            # draw score
            score = self.font.render('Score: {}'.format(self.score), 1,
                                    (255, 0, 0))
            scorepos = score.get_rect(centerx=screen.get_width() / 2)
            screen.blit(score, scorepos)

            """
            draw health of the player                                 
            """

            health = self.font.render('Health: {}'.format(self.health), 1, (0,255,0))
            healthpos = health.get_rect(centerx = screen.get_width() /2, centery = 35 )
            screen.blit(health, healthpos)


class Engine:
    def __init__(self, width=640, height=480):
        pygame.init()

        pygame.display.set_caption('SPJA invaders')
        pygame.key.set_repeat(100, 30)
        pygame.time.set_timer(EVENT_SPAWN_ENEMY, 3000)

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.clock = pygame.time.Clock()

        self.player = Player(self, (self.width / 2, self.height - 20))
        self.enemies = pygame.sprite.Group()
        self.missiles = pygame.sprite.Group()
        self.random = Random()

        self.spawn_enemy()

    def main_loop(self):
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        while True:
            self.handle_keys()
            self.update()
            self.draw()

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == EVENT_SPAWN_ENEMY:
                self.spawn_enemy()
            else:
                self.player.handle_keys(event)

    def update(self):
        delta = self.clock.tick(60) / 1000
        self.enemies.update(self, delta)
        self.missiles.update(self, delta)
        self.player.update(self, delta)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for missile in self.missiles:
            missile.draw(self.screen)



        self.player.draw(self.screen)

        pygame.display.flip()

    def spawn_enemy(self):
        """
         spawn an enemy and add him to enemies group
        """
        enemy_attributes_choices = [
            {"img_id":"1", "hp":100, "score": 10},
            {"img_id":"2", "hp":90, "score": 9},
            {"img_id":"3", "hp":150, "score": 15},
            {"img_id":"4", "hp":170, "score": 20},
            {"img_id":"5", "hp":60, "score": 6}]
        r = Random()
        enemy_attributes = r.choice(enemy_attributes_choices)
        image = load_image('images/enemy' + enemy_attributes["img_id"] + '.gif')
        pos = (r.randint(10,self.width-10),20)
        enemy = Enemy(image, pos, self.player, enemy_attributes["hp"], enemy_attributes["score"])
        self.enemies.add(enemy)

    def end(self):
        print("GAME OVER")
        exit(0)


if __name__ == '__main__':
    engine = Engine()
    engine.main_loop()
