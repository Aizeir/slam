import pygame as pg
from pygame.math import Vector2 as vec2
pg.init()
pg.display.set_caption("SLAM")


W,H = 600,600
cm = 2
Wcm, Hcm = W/cm,H/cm

class Sim:
    def __init__(self):
        self.display = pg.display.set_mode((W,H))
        self.clock = pg.time.Clock()
        self.rects = [pg.FRect(r) for r in ((50,50,300,20),(200,500,300,30),(100,50,50,400),(500,200,20,300))]

        self.robot = Robot(self, (300,300))

    def update(self):
        for e in pg.event.get():
            if e.type==pg.QUIT:
                pg.quit()
                raise SystemExit()
        self.dt = self.clock.tick() / 1000
        self.robot.update()

    def draw(self):
        self.display.fill("black")
        for r in self.rects:
            pg.draw.rect(self.display, 'gray',r)
        self.robot.draw()


def colliderect(pr, r, angle):
    for a,b in [r.bottomright-vec2(r.bottomleft),r.topright-vec2(r.topleft), r.bottomleft-vec2(r.topleft),r.bottomright-vec2(r.topright)]:
        for pv in [pr.bottomright-vec2(pr.bottomleft),pr.topright-vec2(pr.topleft), pr.bottomleft-vec2(pr.topleft),pr.bottomright-vec2(pr.topright)]:
            pv = pv.rotate(angle)

robot_size = vec2(20,20)*cm
robot_speed = 30 # en cm/s
robot_turn_speed = 50 # en deg/s

class Robot:
    def __init__(self, sim, pos):
        self.sim = sim
        self.rect = pg.FRect(pos, robot_size)

        # mvt polaire
        self.moving = 0
        self.angle = 0
        self.speed = vec2()



        # dessin
        self.chassis = pg.Surface(robot_size).convert_alpha() # pr les rotation
        self.chassis.fill('red')


    def update(self):
        k = pg.key.get_pressed()
        self.moving = k[pg.K_UP] - k[pg.K_DOWN]
        self.angle += (k[pg.K_RIGHT] - k[pg.K_LEFT]) * self.sim.dt * robot_turn_speed * (not self.moving)
        self.speed = robot_speed*cm*vec2(0,-1).rotate(self.angle)*self.moving
        self.mvt_collision()

    def mvt_collision(self):
        self.rect.x += self.speed.x * self.sim.dt
        for r in self.sim.rects:
            if r.colliderect(self.rect):
                if self.speed.x > 0: self.rect.right = r.x
                else: self.rect.x = r.right

        self.rect.y += self.speed.y * self.sim.dt
        for r in self.sim.rects:
            if r.colliderect(self.rect):
                if self.speed.y > 0: self.rect.bottom = r.y
                else: self.rect.y = r.bottom


    def draw(self):
        # chassis (on anticipe les rotations)
        chassis = pg.transform.rotate(self.chassis,-self.angle)
        self.sim.display.blit(chassis, chassis.get_rect(center=self.rect.center))

        # chassis prédit



s = Sim()
while True:
    s.update()
    s.draw()
    pg.display.flip()