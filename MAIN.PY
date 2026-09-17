import pygame
import random
import asyncio
import os
import sys

# Window settings
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 30

# Stack / Combo constants (unchanged from original)
STACK_LIMIT = 10
COMBO_SIZE  = 3

# Enemy types (unchanged)
ENEMY_TYPES = ["Scizor", "Magneton", "Voltorb", "Gloom"]

# Colours
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GRAY   = (150, 150, 150)
GRAY90 = (220, 220, 220)
CYAN   = (  0, 255, 255)

# Helper: load and scale image
def load_image(path, size):
    """Load an image relative to the script directory, scale it."""
    base = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(base, path)
    img  = pygame.image.load(full).convert_alpha()
    return pygame.transform.smoothscale(img, size)


# Game States
STATE_START    = "start"
STATE_GAME     = "game"
STATE_GAMEOVER = "gameover"


class ShootingGame:

    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_tiny  = pygame.font.SysFont("Arial",  9, bold=True)

        # Load shared assets
        self.bg_img         = load_image("background.png",   (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.start_bg_img   = load_image("gamestart_bg.png", (500, 300))
        self.gameover_bg    = load_image("gameover_bg.png",  (400, 220))
        self.player_img     = load_image("player.png",  (60, 60))
        self.bullet_img     = load_image("bullet.png",  (10, 20))
        self.enemy_imgs = {
            "Scizor":   load_image("enemy1.png", (40, 40)),
            "Magneton": load_image("enemy2.png", (40, 40)),
            "Voltorb":  load_image("enemy3.png", (40, 40)),
            "Gloom":    load_image("enemy4.png", (40, 40)),
        }

        # Timers (original: spawn every 2000ms, physics every 50ms)
        self.SPAWN_DELAY  = 2000
        self.FRAME_DELAY  = 50

        self.state = STATE_START
        self._reset_game()

    def _reset_game(self):
        # Player position (original: WINDOW_WIDTH//2, WINDOW_HEIGHT-60)
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT - 60

        self.bullets  = []   # each: [x, y]
        self.enemies  = []   # each: [x, y, etype]

        self.vertical_stack = []   # list of etype strings
        self.combo_stack    = []   # list of etype strings

        self.score     = 0
        self.game_over = False

        self._last_update = pygame.time.get_ticks()
        self._last_spawn  = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()

        if self.state == STATE_GAME:
            # Physics at original 50ms rate
            if now - self._last_update >= self.FRAME_DELAY:
                self._last_update = now
                self._physics_step()

            # Spawn enemy every 2000ms (original: root.after(2000,...))
            if now - self._last_spawn >= self.SPAWN_DELAY:
                self._last_spawn = now
                self._spawn_enemy()

    def _physics_step(self):
        # Move bullets up 15px (original)
        for b in self.bullets[:]:
            b[1] -= 15
            if b[1] < 0:
                self.bullets.remove(b)

        # Move enemies down 5px (original)
        for e in self.enemies[:]:
            e[1] += 5
            ex, ey = e[0], e[1]
            px, py = self.player_x, self.player_y

            # Collision with player (original: 40px threshold)
            if abs(px - ex) < 40 and abs(py - ey) < 40:
                self.state = STATE_GAMEOVER
                return

            # Enemy past bottom
            if ey > WINDOW_HEIGHT:
                self.enemies.remove(e)

        # Bullet-enemy collision (original: 30px threshold)
        for b in self.bullets[:]:
            bx, by = b[0], b[1]
            for e in self.enemies[:]:
                ex, ey, etype = e[0], e[1], e[2]
                if abs(bx - ex) < 30 and abs(by - ey) < 30:
                    self._add_to_stack(etype)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if e in self.enemies:
                        self.enemies.remove(e)
                    break

    def _spawn_enemy(self):
        etype = random.choice(ENEMY_TYPES)
        x     = random.randint(50, WINDOW_WIDTH - 50)
        self.enemies.append([x, 0, etype])

    def _add_to_stack(self, etype):
        """Stack/combo logic identical to original add_to_stack."""
        if len(self.vertical_stack) >= STACK_LIMIT:
            self.state = STATE_GAMEOVER
            return

        self.vertical_stack.append(etype)

        if len(self.vertical_stack) >= COMBO_SIZE:
            last_three = self.vertical_stack[-3:]
            if last_three.count(last_three[0]) == 3:
                self.vertical_stack = self.vertical_stack[:-3]
                self.combo_stack.append(last_three[0])
                self.score += 1

    def handle_event(self, event):
        if self.state == STATE_START:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start button centred at (260,160) on 500x300 popup
                ox = (WINDOW_WIDTH  - 500) // 2
                oy = (WINDOW_HEIGHT - 300) // 2
                bx = ox + 260 - 55
                by = oy + 160 - 15
                mx, my = event.pos
                if bx <= mx <= bx + 110 and by <= my <= by + 30:
                    self._last_spawn  = pygame.time.get_ticks()
                    self._last_update = pygame.time.get_ticks()
                    self._spawn_enemy()
                    self.state = STATE_GAME

        elif self.state == STATE_GAME:
            if event.type == pygame.KEYDOWN:
                # Left/right movement (original: 20px steps, boundary checks)
                if event.key == pygame.K_LEFT:
                    if self.player_x > 30:
                        self.player_x -= 20
                elif event.key == pygame.K_RIGHT:
                    if self.player_x < WINDOW_WIDTH - 30:
                        self.player_x += 20
                elif event.key == pygame.K_SPACE:
                    self.bullets.append([self.player_x, self.player_y - 30])

        elif self.state == STATE_GAMEOVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Restart button on game-over popup (400x220, centred)
                ox = (WINDOW_WIDTH  - 400) // 2
                oy = (WINDOW_HEIGHT - 220) // 2
                bx = ox + 200 - 55
                by = oy + 170 - 15
                mx, my = event.pos
                if bx <= mx <= bx + 110 and by <= my <= by + 30:
                    self._reset_game()
                    self._spawn_enemy()
                    self.state = STATE_GAME

    def draw(self):
        if self.state == STATE_START:
            self._draw_start()
        elif self.state == STATE_GAME:
            self._draw_game()
        elif self.state == STATE_GAMEOVER:
            self._draw_gameover()

    def _draw_start(self):
        """Start screen - mirrors original show_start_window."""
        self.screen.fill(BLACK)
        ox = (WINDOW_WIDTH  - 500) // 2
        oy = (WINDOW_HEIGHT - 300) // 2
        self.screen.blit(self.start_bg_img, (ox, oy))

        # Welcome text (original: 250,110 relative to popup)
        txt = self.font_big.render("Welcome to the DSA Shooting Game!", True, WHITE)
        self.screen.blit(txt, (ox + 250 - txt.get_width() // 2,
                               oy + 110 - txt.get_height() // 2))

        # Start Game button (original: 260,160 relative to popup)
        bx = ox + 260 - 55
        by = oy + 160 - 15
        pygame.draw.rect(self.screen, GRAY90, (bx, by, 110, 30), border_radius=5)
        pygame.draw.rect(self.screen, GRAY,   (bx, by, 110, 30), 2, border_radius=5)
        btn_txt = self.font_med.render("Start Game", True, BLACK)
        self.screen.blit(btn_txt, (bx + 55 - btn_txt.get_width()  // 2,
                                   by + 15 - btn_txt.get_height() // 2))

        # Controls hint
        hint = self.font_small.render("Arrow Keys: Move   |   SPACE: Shoot", True, GRAY90)
        self.screen.blit(hint, (ox + 250 - hint.get_width() // 2, oy + 210))

    def _draw_game(self):
        """Main game screen."""
        self.screen.blit(self.bg_img, (0, 0))

        # Left vertical stack border (original rect: 10,75 -> 50,530)
        pygame.draw.rect(self.screen, GRAY90, (10, 75, 40, 455))
        pygame.draw.rect(self.screen, GRAY,   (10, 75, 40, 455), 3)

        # Vertical stack (original: x=30, y starts 100, step 45)
        for i, etype in enumerate(self.vertical_stack):
            img = self.enemy_imgs[etype]
            self.screen.blit(img, (30 - 20, 100 + i * 45 - 20))

        # Combo stack (original: x=WINDOW_WIDTH-50, y starts 100, step 45)
        cx = WINDOW_WIDTH - 50
        if self.combo_stack:
            ch = 70 + len(self.combo_stack) * 45 - 78
            pygame.draw.rect(self.screen, WHITE, (cx - 25, 78, 50, ch), 2)

        # "Combo Points: N" label (original: at cx, 70)
        cp_txt = self.font_tiny.render("Combo Points: " + str(len(self.combo_stack)), True, WHITE)
        self.screen.blit(cp_txt, (cx - cp_txt.get_width() // 2,
                                  70 - cp_txt.get_height() // 2))

        for i, etype in enumerate(self.combo_stack):
            img = self.enemy_imgs[etype]
            self.screen.blit(img, (cx - 20, 100 + i * 45 - 20))

        # Bullets
        for b in self.bullets:
            self.screen.blit(self.bullet_img, (b[0] - 5, b[1] - 10))

        # Enemies
        for e in self.enemies:
            img = self.enemy_imgs[e[2]]
            self.screen.blit(img, (e[0] - 20, e[1] - 20))

        # Player
        self.screen.blit(self.player_img, (self.player_x - 30, self.player_y - 30))

        # Score
        score_txt = self.font_med.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(score_txt, (WINDOW_WIDTH // 2 - score_txt.get_width() // 2, 10))

    def _draw_gameover(self):
        """Game-over screen - mirrors original end_game popup."""
        self.screen.blit(self.bg_img, (0, 0))

        # Dim overlay
        dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        self.screen.blit(dim, (0, 0))

        # gameover_bg.png popup (400x220, centred)
        ox = (WINDOW_WIDTH  - 400) // 2
        oy = (WINDOW_HEIGHT - 220) // 2
        self.screen.blit(self.gameover_bg, (ox, oy))

        # "Game Over! Score: N" (original font Arial 14)
        go_txt = self.font_big.render("Game Over!  Score: " + str(self.score), True, WHITE)
        self.screen.blit(go_txt, (ox + 200 - go_txt.get_width() // 2,
                                  oy + 35 - go_txt.get_height() // 2))

        # Combo stack string (original: ', '.join(...) or "No combo collected")
        combo_string = ", ".join(self.combo_stack) if self.combo_stack else "No combo collected"
        if len(combo_string) > 32:
            combo_string = combo_string[:32] + "..."
        cs_txt = self.font_small.render("Combo Stack: [" + combo_string + "]", True, CYAN)
        self.screen.blit(cs_txt, (ox + 200 - cs_txt.get_width() // 2,
                                  oy + 85 - cs_txt.get_height() // 2))

        # Total combos
        cc_txt = self.font_small.render("Total Combos: " + str(len(self.combo_stack)), True, WHITE)
        self.screen.blit(cc_txt, (ox + 200 - cc_txt.get_width() // 2,
                                  oy + 115 - cc_txt.get_height() // 2))

        # Restart button
        bx = ox + 200 - 55
        by = oy + 170 - 15
        pygame.draw.rect(self.screen, GRAY90, (bx, by, 110, 30), border_radius=5)
        pygame.draw.rect(self.screen, GRAY,   (bx, by, 110, 30), 2, border_radius=5)
        rb_txt = self.font_med.render("Restart", True, BLACK)
        self.screen.blit(rb_txt, (bx + 55 - rb_txt.get_width()  // 2,
                                  by + 15 - rb_txt.get_height() // 2))


# Async entry point (required by Pygbag)
async def main():
    pygame.init()
    pygame.display.set_caption("DSA Combo Shooting Game")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Set window icon (skip gracefully if unsupported in browser)
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "22.ico")
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except Exception:
        pass

    game  = ShootingGame(screen)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update()
        game.draw()
        pygame.display.flip()

        # Yield to browser event loop (REQUIRED for Pygbag)
        await asyncio.sleep(0)

        clock.tick(FPS)


if __name__ == "__main__":
    asyncio.run(main())
