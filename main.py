import math
import time
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


robot_size = vec2(20,20)*cm
robot_speed = 30 # en cm/s
robot_turn_speed = 50 # en deg/s
robot_wheel_rad = 4*cm
robot_diag = robot_size.magnitude() / 2

bit_num = 2*16
angle_quad = 360 / bit_num * 1.5

class Robot:
    def __init__(self, sim, pos):
        self.sim = sim
        self.rect = pg.FRect(pos, robot_size)

        # mvt polaire
        self.moving = 0
        self.angle = 0
        self.speed = vec2()
        self.wheel_angles = [0]*4

        # odométrie
        self.wheel_bits = [(0,0)]*4
        self.wheel_bits_old = [(0,0)]*4
        self.wheel_bits_change = [0]*4

        # dessin
        self.chassis = pg.Surface(robot_size).convert_alpha() # pr les rotation
        self.chassis.fill('red')


    def update(self):
        k = pg.key.get_pressed()

        # Movement
        self.moving = k[pg.K_UP] - k[pg.K_DOWN]
        self.speed = self.moving*robot_speed*cm*vec2(0,-1).rotate(self.angle) * self.sim.dt

        # Collision
        rect = self.rect.move(self.speed)
        for r in self.sim.rects:
            if r.colliderect(rect):
                self.speed = vec2()
                self.moving = False
                break
        else:
            self.rect = rect

        # Turn
        angle = (not self.moving)*(k[pg.K_RIGHT] - k[pg.K_LEFT]) * robot_turn_speed * self.sim.dt
        self.angle += angle

        # Wheel angles
        for i in range(4):
            distance_px = self.moving*self.speed.magnitude() + (-1,1,1,-1)[i]*rad(angle)*robot_diag
            self.wheel_angles[i] += deg(distance_px / robot_wheel_rad)

        # Measure
        self.odometry()

    def odometry(self):
        # Relever les bits mesurés
        self.wheel_bits_old = self.wheel_bits.copy()
        for i in range(4):
            bit = (self.wheel_angles[i]%360 // bit_num)%2
            bit2 = ((self.wheel_angles[i]+angle_quad)%360 // bit_num)%2
            self.wheel_bits[i] = (bit,bit2)

            # Bit changed
            if self.wheel_bits[i] != self.wheel_bits_old[i]:
                self.wheel_bits_change[i] = time.time_ns()
                self.wheel_states[i] = 

    def draw(self):
        # chassis (on anticipe les rotations)
        chassis = pg.transform.rotate(self.chassis,-self.angle)
        self.sim.display.blit(chassis, chassis.get_rect(center=self.rect.center))

        # chassis prédit
        debug([[int(a) for a in x] for x in self.wheel_bits])


debug_font = pg.font.Font(None,35)
def debug(info, y=16, x=16, surf=None, font=debug_font):
    surf = pg.display.get_surface()
    debug_surf = font.render(str(info),True,"white")
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pg.draw.rect(surf, "black", debug_rect.inflate(12,0))
    surf.blit(debug_surf, debug_rect.topleft)
def deg(r): return r * 180 / math.pi
def rad(d): return d * math.pi / 180

s = Sim()
while True:
    s.update()
    s.draw()
    pg.display.flip()