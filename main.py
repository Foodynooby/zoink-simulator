# zoink simulator
# --- juggernaut freeplay from GD
# --- contains AI guidance

import random

import pygame

pygame.init()
pygame.mixer.init()
death_sound = pygame.mixer.Sound("assets/explode.mp3")
death_sound.set_volume(0.25)
pygame.mixer.music.load("assets/song.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
pygame.font.init()
tiny_text = pygame.font.SysFont("comicsansms", 20)
text = pygame.font.SysFont("comicsansms", 40)
big_text = pygame.font.SysFont("comicsansms", 70)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)
CYAN = (0, 255, 255)

# CONSTANTS
WIDTH = 1980
HEIGHT = 1080
SIZE = (WIDTH, HEIGHT)
gs = 5
# gamespeed (i like 16 but 3-5 is best for beginners)


# player (basic elements taken from collision project)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.y_vel = gs * 100
        self.image_original = pygame.image.load("assets/wave.png").convert_alpha()
        self.image_original = pygame.transform.scale_by(self.image_original, 0.8)
        self.image = self.image_original
        self.pos_x = float(x)  # custom x/y
        self.pos_y = float(y)

        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = pygame.Rect(0, 0, 12, 12)  # hitbox size
        self.hitbox.center = self.rect.center

        # rotation
        self.angle = 0.0  # current angle
        self.target_angle = 0.0  # angle to reach
        self.rotation_speed = 0.1  # easing factor

        # trail system
        self.trail_positions = []
        self.max_trail_length = 2000 / gs

    def update(self, dt, current_frame_scroll):
        # replaced self.y stuff with current frame scroll
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # stay on screen/what happens when u hit top/bottom
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos_y = float(self.rect.centery)
            self.flat()
        if self.rect.bottom > 1080:
            self.rect.bottom = 1080
            self.pos_y = float(self.rect.centery)
            self.flat()

        # --- TRAIL
        # set each segment to current x coord - frame scroll (compacted method!!)
        self.trail_positions = [
            (x - current_frame_scroll, y) for x, y in self.trail_positions
        ]
        self.trail_positions.append((self.rect.centerx, self.rect.centery))

        # remove the earliest position once it exceeds max
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)

        # --- HITBOX
        self.hitbox.center = (self.pos_x, self.pos_y)

        # --- ROTATION STUFF
        angle_diff = self.target_angle - self.angle
        self.angle += angle_diff * self.rotation_speed

        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=old_center)

    def draw_trail(self, surface):
        # wait until there are 2 points
        if len(self.trail_positions) < 2:
            return
        thickness = 15
        # top & bottom to connect
        top_points = []
        bottom_points = []
        for x, y in self.trail_positions:
            # add top point position
            top_points.append((x, y - thickness))
            # add bottom point position at the front for drawing the full shape
            bottom_points.insert(0, (x, y + thickness))
        # combine for a bunch of verticies and draw as polygon
        polygon_points = top_points + bottom_points
        pygame.draw.polygon(surface, CYAN, polygon_points)

    def up(self, dt):
        self.pos_y -= self.y_vel * dt
        self.target_angle = 45.0

    def down(self, dt):
        self.pos_y += self.y_vel * dt
        self.target_angle = -45.0

    def flat(self):
        self.target_angle = 0


class Slope(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__()

        # segment coordinates
        self.start_p = [float(start_x), float(start_y)]
        self.end_p = [float(end_x), float(end_y)]

        self.rect = pygame.Rect(
            int(start_x), int(min(start_y, end_y)), int(abs(end_x - start_x)), HEIGHT
        )

    def update(self, dt, current_frame_scroll):
        """
        shift segments to the left by
        how much the player moved forward that frame
        to create the player moving forward effect
        """
        self.start_p[0] -= current_frame_scroll
        self.end_p[0] -= current_frame_scroll
        self.rect.x = int(self.start_p[0])

        # if segments go past the screen delete them so it wont lag
        if self.end_p[0] < 0:
            self.kill()

    def draw_tunnel(self, surface, gap_size):
        pygame.draw.line(
            surface,
            WHITE,
            (int(self.start_p[0]), int(self.start_p[1])),
            (int(self.end_p[0]), int(self.end_p[1])),
            6,
        )

        # floor line; shifted straight down by gap_size
        floor_start = (int(self.start_p[0]), int(self.start_p[1] + gap_size))
        floor_end = (int(self.end_p[0]), int(self.end_p[1] + gap_size))
        pygame.draw.line(surface, WHITE, floor_start, floor_end, 6)


def main():
    # Creating the Screen
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Zoink Simulator")

    # Variables
    done = False
    clock = pygame.time.Clock()
    # game state + timers
    state = "START"
    time = 0
    current = 0.0
    best = 0.0
    noclip = False
    invalid_run = False
    primed = False
    death_time = 0
    # starting position for slopes
    last_x = float(WIDTH)
    last_y = 540.0
    # sprite groups
    everything = pygame.sprite.Group()
    slopes = pygame.sprite.Group()

    wave = Player(580, 650)
    everything.add(wave)

    gap_size = 200
    segment_width = 100

    # ------------ MAIN GAME LOOP
    while not done:
        # delta time system to decrease delay & make consistent regardless of lag
        dt = clock.tick(300) / 1000.0
        current_frame_scroll = (gs * 100) * dt
        if current > best:
            best = current
        # ------ MAIN EVENT LISTENER
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # change how it works based on game state
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    noclip = not noclip
                    invalid_run = True
                if state == "START" and event.key in (
                    pygame.K_SPACE,
                    pygame.K_w,
                    pygame.K_UP,
                ):
                    state = "PLAYING"
                    time = pygame.time.get_ticks()
                    noclip = False
                    invalid_run = False
                    primed = False
                elif state == "DEAD" and event.key in (
                    pygame.K_SPACE,
                    pygame.K_w,
                    pygame.K_UP,
                ):
                    if pygame.time.get_ticks() - death_time >= 200:
                        slopes.empty()
                        everything.empty()
                        wave = Player(580, 540)
                        everything.add(wave)
                        noclip = False
                        invalid_run = False
                        primed = False

                        # retrigger
                        last_x = float(WIDTH)
                        last_y = 540.0
                        while last_x < WIDTH * 2:
                            direction = random.choice([-1, 1])
                            next_x = last_x + segment_width
                            next_y = last_y + (direction * segment_width)

                            # avoid top and bottom
                            if next_y < 80:
                                direction = 1
                                next_y = last_y + (direction * segment_width)
                            elif next_y > (HEIGHT - gap_size - 80):
                                direction = -1
                                next_y = last_y + (direction * segment_width)

                            segment = Slope(last_x, last_y, next_x, next_y)
                            everything.add(segment)
                            slopes.add(segment)

                            last_x, last_y = next_x, next_y

                        state = "PLAYING"
                        time = pygame.time.get_ticks()
                elif event.key == pygame.K_r:
                    state = "DEAD"

            # handling mouse clicks inside respective states
            if event.type == pygame.MOUSEBUTTONDOWN and state in ("START", "DEAD"):
                if state == "START":
                    state = "PLAYING"
                    time = pygame.time.get_ticks()
                    noclip = False
                    invalid_run = False
                    primed = False
                elif state == "DEAD":
                    # wait 0.2s since death and then allow for restart
                    if pygame.time.get_ticks() - death_time >= 200:
                        slopes.empty()
                        everything.empty()
                        wave = Player(580, 650)
                        everything.add(wave)

                        # reset cheat status
                        noclip = False
                        invalid_run = False
                        primed = False

                        last_x = float(WIDTH)
                        last_y = 540.0
                        while last_x < WIDTH * 2:
                            direction = random.choice([-1, 1])
                            next_x = last_x + segment_width
                            next_y = last_y + (direction * segment_width)

                            # avoid top and bottom
                            if next_y < 80:
                                direction = 1
                                next_y = last_y + (direction * segment_width)
                            elif next_y > (HEIGHT - gap_size - 80):
                                direction = -1
                                next_y = last_y + (direction * segment_width)

                            segment = Slope(last_x, last_y, next_x, next_y)
                            everything.add(segment)
                            slopes.add(segment)
                            last_x, last_y = next_x, next_y

                        # start playing and start timer
                        state = "PLAYING"
                        time = pygame.time.get_ticks()

        # ------ GAME LOGIC
        if state == "PLAYING":
            current = (pygame.time.get_ticks() - time) / 1000.0

            # invalidate run timer if theyre cheatin
            if invalid_run:
                current = 0.0

            # --- input handling
            keys = pygame.key.get_pressed()
            input_active = (
                keys[pygame.K_SPACE]
                or keys[pygame.K_UP]
                or keys[pygame.K_w]
                or pygame.mouse.get_pressed()[0]
            )

            # disable first input
            if not input_active:
                primed = True

            # wave goes up/down
            if input_active and primed:
                wave.up(dt)
            else:
                wave.down(dt)

            # --- endless horizontal generation!!! fear
            last_x -= current_frame_scroll
            # end of track moves on-screen, generate new piece
            if last_x < WIDTH + segment_width:
                direction = random.choice([-1, 1])
                next_x = last_x + segment_width
                next_y = last_y + (direction * segment_width)

                # avoid top and bottom blah blah blah
                if next_y < 80:
                    direction = 1
                    next_y = last_y + (direction * segment_width)
                elif next_y > (HEIGHT - gap_size - 80):
                    direction = -1
                    next_y = last_y + (direction * segment_width)

                segment = Slope(last_x, last_y, next_x, next_y)
                everything.add(segment)
                slopes.add(segment)

                last_x, last_y = next_x, next_y

            everything.update(dt, current_frame_scroll)

            # --- COLLISION!!
            if not noclip:
                # list of slopes for the beginning extension
                slope_list = list(slopes)

                for slope_num, slope in enumerate(slope_list):
                    # check collision against the top slope
                    hit_ceiling = wave.hitbox.clipline(slope.start_p, slope.end_p)

                    # check collision against the bottom slope
                    floor_start = (slope.start_p[0], slope.start_p[1] + gap_size)
                    floor_end = (slope.end_p[0], slope.end_p[1] + gap_size)
                    hit_floor = wave.hitbox.clipline(floor_start, floor_end)

                    hit_top_extension = False
                    hit_bottom_extension = False

                    # entrance extension collision only on very first slope
                    if slope_num == 0:
                        dx = slope.end_p[0] - slope.start_p[0]
                        dy = slope.end_p[1] - slope.start_p[1]
                        EXTEND = 500

                        top_extension = (
                            slope.start_p[0] - EXTEND,
                            slope.start_p[1] - abs(dy) * (EXTEND / abs(dx)),
                        )

                        bottom_extension = (
                            floor_start[0] - EXTEND,
                            floor_start[1] + abs(dy) * (EXTEND / abs(dx)),
                        )

                        # create collision between coord -> slope starting point
                        hit_top_extension = wave.hitbox.clipline(
                            top_extension,
                            slope.start_p,
                        )

                        hit_bottom_extension = wave.hitbox.clipline(
                            bottom_extension,
                            floor_start,
                        )

                    # kill the player, play sound effect on collision
                    if (
                        hit_ceiling
                        or hit_floor
                        or hit_top_extension
                        or hit_bottom_extension
                    ):
                        if state == "PLAYING":
                            death_sound.play()
                            state = "DEAD"
                            death_time = pygame.time.get_ticks()

        # ------ DRAWING TO SCREEN
        screen.fill(BLACK)

        if state == "PLAYING" or state == "DEAD":
            # pause but keep rendered
            wave.draw_trail(screen)
            screen.blit(wave.image, wave.rect)

            for slope in slopes:
                slope.draw_tunnel(screen, gap_size)

            slope_list = list(slopes)

            if len(slope_list) > 0:
                first = slope_list[0]

                dx = first.end_p[0] - first.start_p[0]
                dy = first.end_p[1] - first.start_p[1]

                EXTEND = 500

                # top extension always goes upward
                top_extension = (
                    first.start_p[0] - EXTEND,
                    first.start_p[1] - abs(dy) * (EXTEND / abs(dx)),
                )

                pygame.draw.line(
                    screen,
                    WHITE,
                    top_extension,
                    first.start_p,
                    6,
                )

                # bottom extension always goes downward
                floor_start = (
                    first.start_p[0],
                    first.start_p[1] + gap_size,
                )

                bottom_extension = (
                    floor_start[0] - EXTEND,
                    floor_start[1] + abs(dy) * (EXTEND / abs(dx)),
                )

                pygame.draw.line(
                    screen,
                    WHITE,
                    bottom_extension,
                    floor_start,
                    6,
                )

            # mid-attempt HUD
            if invalid_run:
                time_text = text.render("practice mode", True, GREEN)
            else:
                time_text = text.render(f"{current:.2f}s", True, WHITE)
                best_top = tiny_text.render(f"{best:.2f}s", True, GREY)
            screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 30))
            screen.blit(best_top, (WIDTH // 2 - best_top.get_width() // 2, 90))

            # noclip indicator
            if noclip:
                noclip_text_surface = text.render("noclip", True, (255, 255, 255))
                noclip_text_surface = noclip_text_surface.convert_alpha()
                noclip_text_surface.set_alpha(100)
                screen.blit(noclip_text_surface, (20, 0))

        # starting screen
        if state == "START":
            title_text = big_text.render("zoink simulator", True, CYAN)
            tut_text = text.render("press up/space/W/click", True, WHITE)
            noclip_text = tiny_text.render("press N for noclip", True, GREEN)
            screen.blit(
                title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3)
            )
            screen.blit(tut_text, (WIDTH // 2 - tut_text.get_width() // 2, HEIGHT // 2))
            screen.blit(
                noclip_text, (WIDTH // 2 - noclip_text.get_width() // 2, HEIGHT // 1.7)
            )

        # death screen
        elif state == "DEAD":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            died_text = big_text.render("u died", True, RED)
            current_text = text.render(f"your time: {current:.2f}s", True, WHITE)
            best_text = text.render(f"best: {best:.2f}s", True, GREEN)
            retry_text = text.render("space to retry or R to reset", True, WHITE)

            screen.blit(
                died_text, (WIDTH // 2 - died_text.get_width() // 2, HEIGHT // 3)
            )
            screen.blit(
                current_text,
                (WIDTH // 2 - current_text.get_width() // 2, HEIGHT // 3 + 100),
            )
            screen.blit(
                best_text, (WIDTH // 2 - best_text.get_width() // 2, HEIGHT // 2)
            )
            screen.blit(
                retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 80)
            )

        # Update screen
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
# python3 main.py
