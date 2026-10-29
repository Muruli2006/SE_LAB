import pygame
import time
import json
import os
from game.maze import generate_maze, solve_bfs, CELL
from game.player import Player

FPS = 60
BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
PATH_COLOR = (255, 200, 50)
LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                valid_times = [float(t) for t in data if isinstance(t, (int, float))]
                valid_times.sort()
                return valid_times[:5]
    except Exception:
        pass
    return []

def save_leaderboard(times):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(times, f, indent=2)
    except Exception:
        pass

class GameEngine:
    def __init__(self):
        pygame.init()
        self.cols, self.rows = 15, 13
        self.width = 600
        self.height = 480
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Maze Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.hud_font = pygame.font.SysFont("monospace", 17)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.leaderboard = load_leaderboard()
        self.in_select_screen = True
        self.reset()

    def select_difficulty(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.width = self.cols * CELL
        self.height = self.rows * CELL + 60
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.in_select_screen = False
        self.reset()

    def reset(self):
        self.walls = generate_maze(self.cols, self.rows)
        self.player = Player(0, 0)
        self.exit_rect = pygame.Rect((self.cols-1)*CELL+5, (self.rows-1)*CELL+5, CELL-10, CELL-10)
        self.start_time = time.time()
        self.elapsed = 0
        self.won = False
        self.show_hint = False

    def handle_events(self):
        options = [
            ("Easy", 10, 8, 160),
            ("Medium", 15, 13, 240),
            ("Hard", 20, 18, 320)
        ]
        btn_w, btn_h = 260, 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.in_select_screen:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for _, c, r, y in options:
                        btn_rect = pygame.Rect(self.width // 2 - btn_w // 2, y, btn_w, btn_h)
                        if btn_rect.collidepoint(event.pos):
                            self.select_difficulty(c, r)
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_1, pygame.K_e):
                        self.select_difficulty(10, 8)
                    elif event.key in (pygame.K_2, pygame.K_m):
                        self.select_difficulty(15, 13)
                    elif event.key in (pygame.K_3, pygame.K_h):
                        self.select_difficulty(20, 18)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_h:
                        self.show_hint = not self.show_hint
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                        self.in_select_screen = True
                        self.width, self.height = 600, 480
                        self.screen = pygame.display.set_mode((self.width, self.height))
        return True

    def update(self):
        if self.in_select_screen or self.won:
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, self.rows, self.cols)
        self.elapsed = time.time() - self.start_time
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True
            completion_time = round(self.elapsed, 2)
            self.leaderboard.append(completion_time)
            self.leaderboard.sort()
            self.leaderboard = self.leaderboard[:5]
            save_leaderboard(self.leaderboard)

    def draw_select_screen(self):
        self.screen.fill((30, 30, 50))
        title = self.big_font.render("MAZE RUNNER", True, (255, 215, 0))
        sub = self.font.render("Select Difficulty Tier", True, (200, 200, 220))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 40))
        self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, 95))

        mx, my = pygame.mouse.get_pos()
        options = [
            ("Easy (10 x 8)", 10, 8, 160),
            ("Medium (15 x 13)", 15, 13, 240),
            ("Hard (20 x 18)", 20, 18, 320)
        ]
        btn_w, btn_h = 260, 50
        for label, c, r, y in options:
            btn_rect = pygame.Rect(self.width // 2 - btn_w // 2, y, btn_w, btn_h)
            is_hover = btn_rect.collidepoint(mx, my)
            btn_color = (60, 140, 230) if is_hover else (50, 60, 90)
            text_color = (255, 255, 255) if is_hover else (220, 220, 220)

            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 180, 255) if is_hover else (80, 90, 120), btn_rect, width=2, border_radius=8)

            txt_surf = self.font.render(label, True, text_color)
            self.screen.blit(txt_surf, (btn_rect.centerx - txt_surf.get_width() // 2, btn_rect.centery - txt_surf.get_height() // 2))

        hint_txt = self.hud_font.render("Click a button or press 1 (Easy), 2 (Medium), 3 (Hard)", True, (160, 160, 180))
        self.screen.blit(hint_txt, (self.width // 2 - hint_txt.get_width() // 2, 405))

    def draw_maze(self):
        wall_w = 3
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c*CELL, r*CELL
                w = self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen, WALL_COLOR, (x,y), (x+CELL,y), wall_w)
                if w[1]: pygame.draw.line(self.screen, WALL_COLOR, (x,y+CELL), (x+CELL,y+CELL), wall_w)
                if w[2]: pygame.draw.line(self.screen, WALL_COLOR, (x+CELL,y), (x+CELL,y+CELL), wall_w)
                if w[3]: pygame.draw.line(self.screen, WALL_COLOR, (x,y), (x,y+CELL), wall_w)

    def draw_hint(self):
        if not self.show_hint:
            return
        pr = max(0, min(self.rows - 1, int(self.player.rect.centery // CELL)))
        pc = max(0, min(self.cols - 1, int(self.player.rect.centerx // CELL)))
        path = solve_bfs(self.walls, (pr, pc), (self.rows - 1, self.cols - 1), self.rows, self.cols)
        for r, c in path:
            rect = pygame.Rect(c * CELL + 6, r * CELL + 6, CELL - 12, CELL - 12)
            pygame.draw.rect(self.screen, PATH_COLOR, rect, border_radius=4)

    def draw_fog(self):
        fog = pygame.Surface((self.width, self.rows * CELL), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 255))
        px, py = self.player.rect.center
        r_inner = int(3.0 * CELL)
        r_outer = int(3.5 * CELL)
        for r in range(r_outer, r_inner, -1):
            alpha = int(255 * (r - r_inner) / (r_outer - r_inner))
            pygame.draw.circle(fog, (0, 0, 0, alpha), (px, py), r)
        pygame.draw.circle(fog, (0, 0, 0, 0), (px, py), r_inner)
        self.screen.blit(fog, (0, 0))

    def draw(self):
        if self.in_select_screen:
            self.draw_select_screen()
            pygame.display.flip()
            return

        self.screen.fill(BG)
        self.draw_hint()
        self.draw_maze()
        pygame.draw.rect(self.screen, EXIT_COLOR, self.exit_rect, border_radius=4)
        ex_label = self.hud_font.render("EXIT", True, (20,80,20))
        self.screen.blit(ex_label, (self.exit_rect.x+2, self.exit_rect.y+4))
        self.player.draw(self.screen)
        self.draw_fog()

        hud = pygame.Rect(0, self.rows*CELL, self.width, 60)
        pygame.draw.rect(self.screen, (30,30,50), hud)
        time_surf = self.hud_font.render(f"Time: {self.elapsed:.1f}s   H=Hint  R=Reset  M=Menu", True, (200,200,200))
        self.screen.blit(time_surf, (10, self.rows*CELL+20))

        if self.won:
            overlay = pygame.Surface((self.width, self.rows*CELL), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            cy = (self.rows * CELL) // 2

            msg = self.big_font.render(f"Solved in {self.elapsed:.1f}s!", True, (80,240,80))
            self.screen.blit(msg, (self.width//2 - msg.get_width()//2, max(10, cy - 120)))

            lb_title = self.font.render("-- Top 5 Leaderboard --", True, (255,215,0))
            self.screen.blit(lb_title, (self.width//2 - lb_title.get_width()//2, max(50, cy - 70)))

            for i, score in enumerate(self.leaderboard):
                entry_str = f"{i+1}. {score:.2f}s"
                entry_surf = self.hud_font.render(entry_str, True, (240,240,240))
                self.screen.blit(entry_surf, (self.width//2 - entry_surf.get_width()//2, cy - 35 + i * 22))

            sub = self.hud_font.render("Press R for new maze or M for menu", True, (200,200,200))
            self.screen.blit(sub, (self.width//2 - sub.get_width()//2, min(self.rows * CELL - 25, cy + 95)))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()




