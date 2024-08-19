import math
import numpy as np

class Geometry:
    def construct_rect(width, height, position, rotation):
        (x, y) = position
        dx = width / 2
        dy = height / 2
        sin = math.sin(math.radians(rotation))
        cos = math.cos(math.radians(rotation))
        return [
            (x + dx * cos + dy * sin, y + dx * sin - dy * cos),
            (x + dx * cos - dy * sin, y + dx * sin + dy * cos),
            (x - dx * cos - dy * sin, y - dx * sin + dy * cos),
            (x - dx * cos + dy * sin, y - dx * sin - dy * cos)
        ]

    def absolute_position(point, origin, rotation):
        (x, y) = point
        (x0, y0) = origin
        sin = math.sin(math.radians(rotation))
        cos = math.cos(math.radians(rotation))
        return (x0 + x * cos - y * sin, y0 + x * sin + y * cos)

    def relative_position(point, origin, rotation):
        (x, y) = point
        (x0, y0) = origin
        x -= x0
        y -= y0
        sin = math.sin(math.radians(rotation))
        cos = math.cos(math.radians(rotation))
        return (x * cos + y * sin, y * cos - x * sin)

    def normalize_angle(angle):
        return (angle + 180) % 360 - 180

class Viewport:
    _width = 0
    _height = 0
    _offsetx = 0
    _offsety = 0
    _scale = 1

    def __init__(self, size):
        (self._width, self._height) = size
        self._focus()
    
    def _focus(self):
        self._focusx = self._width / 2 + self._offsetx
        self._focusy = self._height / 2 + self._offsety

    def reset(self):
        self._offsetx = 0
        self._offsety = 0
        self._scale = 1
        self._focus()

    def move(self, dx, dy):
        self._offsetx += dx / self._scale
        self._offsety += dy / self._scale
        self._focus()

    def zoom(self, factor):
        self._scale *= factor
        self._focus()

    def transform_width(self, width):
        return width * self._scale

    def transform_point(self, p):
        (x, y) = p
        return (
            (x - self._focusx) * self._scale + self._focusx - self._offsetx,
            (y - self._focusy) * self._scale + self._focusy - self._offsety
        )

    def transform_rect(self, rect):
        trans_rect = [(0, 0), (0, 0), (0, 0), (0, 0)]
        for i in range(4):
            trans_rect[i] = self.transform_point(rect[i])
        return trans_rect

class Car:
    _length = 100
    _axle_distance = 80
    _width = 60
    _acceleration = 1000 # pixels / second^2
    _friction = 5.0      # loss of velocity / second
    _turn_speed = 60     # degrees / second
    
    _x = 0
    _y = 0
    _v = 0
    _theta = 0
    _alpha = 0
    _direction = 0       # forward / backward

    _draw_guides = False
    _c = (0, 0)          # circle center
    _r = 0               # circle radius

    def __init__(self, x, y, angle):
        self._x = x
        self._y = y
        self._theta = angle

    def get_position(self):
        return (self._x, self._y)

    def get_orientation(self):
        return self._theta

    def get_wheel_position(self):
        return self._alpha

    def get_speed(self):
        return self._v

    def turn_wheel(self, direction, dt):
        if direction > 0:
            self._alpha += self._turn_speed * dt
        elif direction < 0:
            self._alpha -= self._turn_speed * dt

        if self._alpha > 30:
            self._alpha = 30
        if self._alpha < -30:
            self._alpha = -30

    def move(self, pedal, dt):
        # Distance travelled
        self._v += pedal * self._acceleration * dt
        self._v -= self._v * self._friction * dt
        s = self._v * dt

        # If wheels are straight
        if self._alpha == 0:
            self._r = 0
            (self._x, self._y) = Geometry.absolute_position((0, s), (self._x, self._y), self._theta)
        
        # If wheels are turned
        else:
            # Compute the turning circle
            self._r = self._axle_distance / (2 * math.sin(math.radians(abs(self._alpha))))
            t0 = Geometry.absolute_position((0, self._axle_distance/2), (self._x, self._y), self._theta)
            if self._alpha > 0:
                self._c = Geometry.absolute_position((0, self._r), t0, self._theta + self._alpha + 90)
            else:
                self._c = Geometry.absolute_position((0, self._r), t0, self._theta + self._alpha - 90)
            
            # Move along the circle arc
            beta = (180 * s) / (math.pi * self._r) # rotational distance travelled
            if self._alpha > 0: # destination point on the arc
                t1 = Geometry.absolute_position((self._r * (math.cos(math.radians(beta)) - 1), self._r * math.sin(math.radians(beta))),
                    t0, self._theta + self._alpha) 
            else:
                t1 = Geometry.absolute_position((self._r * (1 - math.cos(math.radians(beta))), self._r * math.sin(math.radians(beta))),
                    t0, self._theta + self._alpha)
            
            # New body position
            angle = math.radians(180 - self._alpha)
            sin = math.sin(angle)
            cos = math.cos(angle)
            (self._x, self._y) = Geometry.absolute_position((self._axle_distance/2 * cos, self._axle_distance/2 * sin), t1, self._theta + self._alpha + 90)

            # New body angle
            if self._alpha > 0:
                self._theta += beta
            else:
                self._theta -= beta
    
    def render(self, surface, viewport):
        if self._draw_guides:
            if self._r > 0 and self._r < 1000:
                (cx, cy) = self._c
                gfxdraw.circle(surface, round(cx), round(cy), round(self._r), (0, 0, 128))

        body = Geometry.construct_rect(0.7 * self._width, self._length, (self._x, self._y), self._theta)
        cabin = Geometry.construct_rect(0.5 * self._width, 0.5 * self._length,
            Geometry.absolute_position((0, -0.1 * self._length), (self._x, self._y), self._theta), self._theta)
        axle_front = Geometry.construct_rect(self._width, self._length / 20,
            Geometry.absolute_position((0, 0.5 * self._axle_distance), (self._x, self._y), self._theta), self._theta)
        axle_rear = Geometry.construct_rect(self._width, self._length / 20,
            Geometry.absolute_position((0, -0.5 * self._axle_distance), (self._x, self._y), self._theta), self._theta)
        tire_fl = Geometry.construct_rect(self._length / 10, 0.2 * self._length,
            Geometry.absolute_position((-self._width / 2, 0.5 * self._axle_distance), (self._x, self._y), self._theta), self._theta + self._alpha)
        tire_fr = Geometry.construct_rect(self._length / 10, 0.2 * self._length,
            Geometry.absolute_position((self._width / 2, 0.5 * self._axle_distance), (self._x, self._y), self._theta), self._theta + self._alpha)
        tire_rl = Geometry.construct_rect(self._length / 10, 0.2 * self._length,
            Geometry.absolute_position((-self._width / 2, -0.5 * self._axle_distance), (self._x, self._y), self._theta), self._theta)
        tire_rr = Geometry.construct_rect(self._length / 10, 0.2 * self._length,
            Geometry.absolute_position((self._width / 2, -0.5 * self._axle_distance), (self._x, self._y), self._theta), self._theta)
        
        body = viewport.transform_rect(body)
        cabin = viewport.transform_rect(cabin)
        axle_front = viewport.transform_rect(axle_front)
        axle_rear = viewport.transform_rect(axle_rear)
        tire_fl = viewport.transform_rect(tire_fl)
        tire_fr = viewport.transform_rect(tire_fr)
        tire_rl = viewport.transform_rect(tire_rl)
        tire_rr = viewport.transform_rect(tire_rr)

        pygame.draw.polygon(surface, "gray20", axle_front, 0)
        pygame.draw.polygon(surface, "gray20", axle_rear, 0)
        pygame.draw.polygon(surface, "black", tire_fl, 0)
        pygame.draw.polygon(surface, "black", tire_fr, 0)
        pygame.draw.polygon(surface, "black", tire_rl, 0)
        pygame.draw.polygon(surface, "black", tire_rr, 0)
        gfxdraw.aapolygon(surface, body, (128, 0, 0))
        gfxdraw.filled_polygon(surface, body, (128, 0, 0))
        gfxdraw.aapolygon(surface, cabin, (64, 0, 0))
        gfxdraw.filled_polygon(surface, cabin, (64, 0, 0))

class Goal:
    _length = 120
    _width = 80

    _x = 0
    _y = 0
    _angle = 0

    def __init__(self, x, y, angle):
        self._x = x
        self._y = y
        self._angle = angle

    def position(self):
        return (self._x, self._y)

    def angle(self):
        return self._angle
    
    def render(self, surface, viewport, filled = False):
        frame = Geometry.construct_rect(self._width, self._length, (self._x, self._y), self._angle)
        fill = Geometry.construct_rect(self._width - 6, self._length - 6, (self._x, self._y), self._angle)

        frame = viewport.transform_rect(frame)
        fill = viewport.transform_rect(fill)

        gfxdraw.filled_polygon(surface, frame, (64, 96, 64))
        if filled:
            gfxdraw.filled_polygon(surface, fill, (64, 192, 64))
        else:
            gfxdraw.filled_polygon(surface, fill, (190, 190, 190))
        pygame.draw.line(surface, (64, 96, 64),
            viewport.transform_point((self._x - 10, self._y + 10)),
            viewport.transform_point((self._x + 10, self._y - 10)),
            round(viewport.transform_width(4)))
        pygame.draw.line(surface, (64, 96, 64),
            viewport.transform_point((self._x - 10, self._y - 10)),
            viewport.transform_point((self._x + 10, self._y + 10)),
            round(viewport.transform_width(4)))

class ParkingSimulator:
    _surface = None
    _font = None
    _clock = None
    _visualize = False
    _use_dqn_image = False
    _viewport = None
    _run = False
    _fps = 0
    _dt = 0

    _car = None
    _goal = None
    _initial_state = None
    _goal_state = None
    _goal_tolerance = (0, 0, 0)
    
    _input_steering = 0
    _input_direction = 0
    _was_reset = False

    _output_text = ["" for i in range(10)]
    _dqn_image = None

    def __init__(self,
        initial_state, goal_state, goal_tolerance = (0, 0, 0),
        visualize = True, fps = 60, window_size = (1280, 720),
        use_dqn_image = False
    ):        
        if visualize and fps > 0:
            global pygame
            global gfxdraw
            import pygame
            from pygame import gfxdraw

            pygame.init()
            self._font = pygame.font.SysFont(None, 32)
            self._clock = pygame.time.Clock()

            pygame.display.set_caption('Car parking simulator')
            self._surface = pygame.display.set_mode(window_size)
            self._viewport = Viewport(window_size)
            self._visualize = True
        else:
            self._visualize = False
        
        if use_dqn_image:
            global Image
            global ImageDraw
            global np
            from PIL import Image, ImageDraw
            import numpy as np
        self._use_dqn_image = use_dqn_image

        self._fps = fps
        self._dt = 1.0 / fps

        (x0, y0, angle0) = self._initial_state = initial_state
        (x1, y1, angle1) = self._goal_state = goal_state
        self._car = Car(x0, y0, angle0)
        self._goal = Goal(x1, y1, angle1)
        self._goal_tolerance = goal_tolerance
        
        self._mouse_down = False
        self._mouse_pos = (0, 0)
        self._run = True

    def __del__(self):
        if self._visualize:
            pygame.quit()

    def reset(self):
        (x0, y0, angle0) = self._initial_state
        (x1, y1, angle1) = self._goal_state
        self._car = Car(x0, y0, angle0)
        self._goal = Goal(x1, y1, angle1)
        self._output_text = ["" for i in range(10)]
        self._was_reset = True

        if self._use_dqn_image:
            self._render_dqn_image()

    def was_reset(self):
        ret = self._was_reset
        self._was_reset = False
        return ret

    def stop(self):
        self._run = False

    def run(self, frames = 1, render_all_frames = True):
        for _ in range(frames):
            self._car.turn_wheel(self._input_steering, self._dt)
            self._car.move(self._input_direction, self._dt)
            if render_all_frames:
                self._process_input()
                self._render_dqn_image()
                self.render_frame()
        
        if not render_all_frames:
            self._process_input()
            self._render_dqn_image()
            self.render_frame()

        return self._run

    def get_state(self, egocentric = False):
        (x, y) = self._car.get_position()
        angle_car = self._car.get_orientation()
        v = self._car.get_speed()
        w = self._car.get_wheel_position()
        angle_goal = self._goal.angle()
        (x0, y0) = self._goal.position()
        if egocentric:
            (x, y) = Geometry.relative_position(self._goal.position(), self._car.get_position(), self._car.get_orientation())    
            a = Geometry.normalize_angle(Geometry.normalize_angle(angle_goal) - Geometry.normalize_angle(angle_car))
        else:
            (x, y) = (x - x0, y - y0)
            a = Geometry.normalize_angle(Geometry.normalize_angle(angle_car) - Geometry.normalize_angle(angle_goal))

        if abs(x) < 1:
            x = 0
        if abs(y) < 1:
            y = 0
        if abs(a) < 0.1:
            a = 0
        if abs(v) < 1:
            v = 0
        if abs(w) < 0.1:
            w = 0
        
        return (x, y, a, v, w)

    def goal_reached(self):
        (x, y, angle, _, _) = self.get_state()
        (tol_x, tol_y, tol_a) = self._goal_tolerance
        return abs(x) < tol_x and abs(y) < tol_y and abs(angle) < tol_a

    def list_actions():
        return [(0, 0), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1)]

    def execute_action(self, action):
        try:
            (direction, steering) = action
            is_discrete = False
            if direction > 1:
                direction = 1
            if direction < -1:
                direction = -1
            if steering > 1:
                steering = 1
            if steering < -1:
                steering = -1
        except:
            is_discrete = True

        if is_discrete:
            (self._input_direction, self._input_steering) = ParkingSimulator.list_actions()[action]
        else:
            self._input_direction = direction
            self._input_steering = steering
    
    def print(self, line, text):
        if line >= 0 and line < 10:
            self._output_text[line] = text

    def get_dqn_image(self):
        if self._dqn_image != None:
            return np.array(self._dqn_image) / 255
        else:
            return None

    def _process_input(self):
        if not self._visualize:
            return

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self._input_steering = 1
                if event.key == pygame.K_RIGHT:
                    self._input_steering = -1
                if event.key == pygame.K_UP:
                    self._input_direction = 1
                if event.key == pygame.K_DOWN:
                    self._input_direction = -1
                if event.key == pygame.K_RETURN:
                    self.reset()
                if event.key == pygame.K_ESCAPE:
                    self._run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self._input_steering = 0
                if event.key == pygame.K_RIGHT:
                    self._input_steering = 0
                if event.key == pygame.K_UP:
                    self._input_direction = 0
                if event.key == pygame.K_DOWN:
                    self._input_direction = 0
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == True:
                self._mouse_down = True
                self._mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP and pygame.mouse.get_pressed()[0] == False:
                self._mouse_down = False
            if event.type == pygame.MOUSEMOTION and self._mouse_down:
                (x0, y0) = self._mouse_pos
                (x1, y1) = pygame.mouse.get_pos()
                (dx, dy) = (x1 - x0, y1 - y0)
                self._mouse_pos = (x1, y1)
                self._viewport.move(-dx, dy)
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self._viewport.zoom(1.1)
                elif event.y < 0:
                    self._viewport.zoom(0.9)
            if event.type == pygame.QUIT:
                self._run = False

    def _print_info(self):
        line = 0
        if self._output_text[0] == "":
            (x, y) = self._car.get_position()
            orientation = self._car.get_orientation()
            (x, y, orientation, v, w) = self.get_state()
            text = self._font.render(
                "state: [" + str(round(x)) + ", " +
                str(round(y)) + ", " +
                str(round(orientation)) + ", " +
                str(round(v)) + ", " +
                str(round(w)) + "]", True, (0, 0, 0))
            self._surface.blit(text, (10, 10))
        
        while line < 10:
            if self._output_text[line] != "":
                text = self._font.render(self._output_text[line], True, (0, 0, 0))
                self._surface.blit(text, (10, 10 + 30 * line))
            line += 1

    def render_frame(self):
        if not self._visualize:
            return
        
        self._surface.fill("gray")
        self._goal.render(self._surface, self._viewport, self.goal_reached())
        self._car.render(self._surface, self._viewport)
        self._surface.blit(pygame.transform.flip(self._surface, False, True), dest = (0, 0))
        self._print_info()

        if self._dqn_image != None:
            img = self._dqn_image.convert("RGB")
            surface = pygame.image.fromstring(img.tobytes(), img.size, "RGB")
            self._surface.blit(surface, dest = (self._surface.get_width() - 100, 16))

        pygame.display.flip()
        self._clock.tick(self._fps)
    
    def _render_dqn_image(self):
        if not self._use_dqn_image:
            return

        self._dqn_image = Image.new("L", (84, 84), 0)
        draw = ImageDraw.Draw(self._dqn_image)

        # Draw the parking place.
        draw.polygon([(38, 40), (45, 40), (45, 44), (38, 44)], outline=255, fill=0)

        # Compute the car's position.
        (x, y, a, _, _) = self.get_state()
        x = round((x + 500) * 84/1000)
        y = round((500 - y) * 84/1000)

        # Draw the car.
        rect = Geometry.construct_rect(7, 4, (x, y), 360 - a)
        draw.polygon(rect, outline=255, fill=255)