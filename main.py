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
        self.raycast = Raycast(self)

    def update(self):
        for e in pg.event.get():
            if e.type==pg.QUIT:
                pg.quit()
                raise SystemExit()
        self.dt = self.clock.tick() / 1000
        self.robot.update()

    def draw(self):
        self.display.fill("black")
        """for r in self.rects:
            pg.draw.rect(self.display, 'gray',r)
        self.robot.draw()"""
        self.raycast.draw()




robot_size = vec2(20,20)*cm
robot_speed = 50 # en cm/s
robot_turn_speed = 50 # en deg/s
robot_wheel_rad = 4*cm
robot_diag = robot_size.magnitude() / 2

bit_num = 2*1
bit_size = 360 / bit_num
angle_quad = 360 / bit_num * 1.5
bit_step = (2*math.pi*robot_wheel_rad) / bit_num

bit_direct = {
    (0,0): (0,1),
    (0,1): (1,1),
    (1,1): (1,0),
    (1,0): (0,0),
}

class Robot:
    def __init__(self, sim, pos):
        self.sim = sim
        self.rect = pg.FRect(pos, robot_size)
        self.init = self.rect.center

        # mvt polaire
        self.moving = 0
        self.angle = 0
        self.speed = vec2()
        self.wheel_angles = [0]*2
        self.old_angles = [0]*2

        # odométrie
        self.wheel_bits = [(0,0)]*2
        self.wheel_bits_time = [0]*2
        self.wheel_bits_old = [0, 0]
        self.wheel_last_dir = [0, 0]
        self.wheel_directions = [0, 0]
        self.wheel_2_last_dir = 0

        self.predicted_pos = self.rect.center
        self.predicted_angle = 0

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
        for i in range(2):
            distance_px = self.moving*self.speed.magnitude() + (1,-1,-1,1)[i]*rad(angle)*robot_diag
            self.wheel_angles[i] += deg(distance_px / robot_wheel_rad)

        # Measure
        self.odometry()

    def odometry(self):
        # Lecture des bits
        for i in range(2):
            angle = self.wheel_angles[i]
            bit, quad = math.floor(angle / bit_size) % 2, math.floor((angle-angle_quad) / bit_size) % 2
            if bit != self.wheel_bits_old[i]:
                self.wheel_directions[i] = self.wheel_last_dir[i] = (-1,1)[bit == quad]
            elif i == 0:
                self.wheel_directions[i] = 0
            self.wheel_bits_old[i] = bit


        # Robot movement
        if self.wheel_directions[0] == self.wheel_directions[1]:
            self.predicted_pos += vec2(0,-1).rotate(self.predicted_angle) * self.wheel_directions[0] * bit_step
            self.wheel_directions[1] = 0
        else:
            self.predicted_angle += deg(bit_step / robot_wheel_rad) * (-1,1)[self.wheel_directions[0]]
        self.predicted_angle = self.angle
        """
        t = time.time()
        dx = bit_step / (t - self.wheel_bits_time[i])
        ...
        self.wheel_bits_time[i] = t
        """

    def draw(self):
        # chassis (on anticipe les rotations)
        chassis = pg.transform.rotate(self.chassis,-self.angle)
        self.sim.display.blit(chassis, chassis.get_rect(center=self.rect.center))
        
        # chassis prédit
        chassis = pg.transform.rotate(self.chassis,-self.predicted_angle)
        chassis.set_alpha(100)
        self.sim.display.blit(chassis, chassis.get_rect(center=self.predicted_pos))


FOV = math.pi / 3
NUM_RAYS = 10
RANGE = 400*cm
SCALE = W / NUM_RAYS
SCREEN_DIST = W/2 / math.tan(FOV/2)
WALL_HEIGHT = 100

class Raycast:
    def __init__(self, sim):
        self.robot,self.sim = sim.robot,sim

    def draw(self):
        dir = vec2(0,-1).rotate(self.robot.angle)
        pos = self.robot.rect.center + dir * robot_size.y // 2
        #pg.draw.circle(self.sim.display, "white", pos, 6)
        rays = []
        for i in range(NUM_RAYS):
            angle = FOV * (i/(NUM_RAYS-1)-.5)
            ray_dir = dir.rotate(deg(angle))
            for x in range(0, RANGE+1, 1):
                point = pos + ray_dir * x
                for r in self.sim.rects:
                    if r.collidepoint(point):
                        rays.append(x)
                        break
                else: continue
                break
            else:
                rays.append(-1)
            pg.draw.line(self.sim.display, "red", pos, pos + ray_dir * x, 2)

        
        # Draw
        for i in range(NUM_RAYS):
            x = rays[i]
            if x == -1: continue
            last = -1 if i==0 else rays[i-1]
            next = -1 if i==NUM_RAYS-1 else rays[i+1]
            a,b = (last,x)[last==-1],(next,x)[next==-1]
            for y in range(math.ceil(SCALE)):
                new_x = a+(x-a)*(y/SCALE)**.5
                xcos = new_x * math.cos(angle)
                h = SCREEN_DIST / (xcos+.0001) * WALL_HEIGHT
                color = [255/(1 + (xcos/RANGE)**.5)]*2+[(y > SCALE/2)*255]
                pg.draw.rect(self.sim.display, color, (
                    i*SCALE+y, H/2-h/2,
                    1, h
                ))

    def update(self):
        pass

debug_font = pg.font.Font(None,35)
def debug(info, y=16, x=16, surf=None, font=debug_font):
    surf = pg.display.get_surface()
    debug_surf = font.render(str(info),True,"white")
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pg.draw.rect(surf, "black", debug_rect.inflate(12,0))
    surf.blit(debug_surf, debug_rect.topleft)
def deg(r): return r * 180 / math.pi
def rad(d): return d * math.pi / 180

def moy(f,a,b): return (f(a) + f(b)) / 2

s = Sim()
while True:
    s.update()
    s.draw()
    pg.display.flip()