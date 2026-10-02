import sys
import threading
import time

import pygame

from common.board import Board
from sokoban_single.algorithms.a_star import AStar
from sokoban_single.algorithms.ucs import UCS
from sokoban_single.models.action import Action
from sokoban_single.models.problem import SokobanProblem

# ---------- layout ----------
GRID_SIZE = 20                  # 20 x 20 cells
CELL = 30                       # cell size (px)
MARGIN = 20
INFO_HEIGHT = 140
BOARD_PX = GRID_SIZE * CELL
WIN_W = BOARD_PX + 2 * MARGIN
WIN_H = MARGIN + BOARD_PX + INFO_HEIGHT + MARGIN

# ---------- colors ----------
BG_COLOR = (232, 238, 245)
BOARD_BG = (255, 255, 255)
GRID_COLOR = (205, 210, 218)
TEXT_COLOR = (30, 35, 45)
BORDER_COLOR = (150, 158, 170)
WALL_COLOR = (95, 105, 120)
BOX_COLOR = (214, 160, 70)
BOX_EDGE = (90, 60, 20)
TARGET_COLOR = (215, 70, 70)
DONE_COLOR = (40, 160, 80)      # border of a box that is on a target
AGENT_COLOR = (50, 120, 230)

# ---------- settings ----------
FPS = 60
STEP_DELAY = 0.3                # seconds between two steps while playing
PATH_LINES = 3                  # lines of the path shown in the info panel
DEFAULT_MAP = "maps/example_map.txt"
ALGORITHMS = [("UCS", UCS), ("A*", AStar)]


class game_gui:

    def __init__(self, map_path: str = DEFAULT_MAP):
        self.board = Board(map_path)
        self.problem = SokobanProblem(self.board)

        pygame.init()
        pygame.display.set_caption("Sokoban")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("timesnewroman", 20)
        self.big_font = pygame.font.SysFont("timesnewroman", 32)

        self.board_rect = pygame.Rect(MARGIN, MARGIN, BOARD_PX, BOARD_PX)
        self.info_rect = pygame.Rect(MARGIN, self.board_rect.bottom, BOARD_PX + 1, INFO_HEIGHT)
        self.buttons = []
        for i in range(len(ALGORITHMS)):
            rect = pygame.Rect(0, 0, 320, 60)
            rect.center = (self.board_rect.centerx, self.board_rect.centery - 40 + i * 90)
            self.buttons.append(rect)

        self.mode = "menu"          # menu | solving | play
        self.message = ""
        self.algo_name = "-"
        self.stats = ""
        self.action_names = []      # ["North", "East", ...]
        self.states = []            # state after every step
        self.index = 0
        self.playing = False
        self.last_tick = time.perf_counter()
        self._result = None

    def start_solve(self, i: int):
        self.algo_name, solver_cls = ALGORITHMS[i]
        self.mode = "solving"
        self.message = ""
        self._result = None
        threading.Thread(target=self._solve, args=(solver_cls,), daemon=True).start()

    def _solve(self, solver_cls):
        solver = solver_cls()
        self._result = (solver, solver.solve(self.problem))

    def _finish_solve(self):
        solver, path = self._result
        if path is None:
            self.mode = "menu"
            self.message = f"{self.algo_name}: no solution found"
            return
        self.states = [self.problem.initial_state]
        for direction in path:
            for nxt, action, _ in self.problem.get_successors(self.states[-1]):
                if action == direction:
                    self.states.append(nxt)
                    break
        self.action_names = [Action.to_string(d) for d in path]
        self.index = 0
        self.playing = False
        self.stats = (f"Cost: {len(path)}   Expanded: {solver.nodes_expanded}   "
                      f"Time: {solver.execution_time:.2f}s")
        print(f"{self.algo_name} - Actions:", ", ".join(self.action_names))
        print("Total cost:", len(path))
        self.mode = "play"

    @property
    def total_steps(self) -> int:
        return len(self.states) - 1

    def toggle_play(self):
        if self.index == self.total_steps:      # finished: replay from the start
            self.index = 0
        self.playing = not self.playing
        self.last_tick = time.perf_counter()

    def step_next(self):
        self.playing = False
        self.index = min(self.index + 1, self.total_steps)

    def step_prev(self):
        self.playing = False
        self.index = max(self.index - 1, 0)

    def update(self):
        if self.mode == "solving" and self._result is not None:
            self._finish_solve()
        elif self.mode == "play" and self.playing:
            now = time.perf_counter()
            if now - self.last_tick >= STEP_DELAY:
                self.last_tick = now
                self.index += 1
                if self.index >= self.total_steps:
                    self.index = self.total_steps
                    self.playing = False

    def cell_rect(self, pos) -> pygame.Rect:
        """Grid cell of a map position (row, col); the map is centered in the grid."""
        off_r = (GRID_SIZE - self.board.height) // 2
        off_c = (GRID_SIZE - self.board.width) // 2
        return pygame.Rect(self.board_rect.x + (pos[1] + off_c) * CELL,
                           self.board_rect.y + (pos[0] + off_r) * CELL, CELL, CELL)

    def draw_grid(self):
        pygame.draw.rect(self.screen, BOARD_BG, self.board_rect)
        x0, y0 = self.board_rect.topleft
        for i in range(GRID_SIZE + 1):
            d = i * CELL
            pygame.draw.line(self.screen, GRID_COLOR, (x0 + d, y0), (x0 + d, y0 + BOARD_PX))
            pygame.draw.line(self.screen, GRID_COLOR, (x0, y0 + d), (x0 + BOARD_PX, y0 + d))

    def draw_map(self):
        state = self.states[self.index]
        for pos in self.board.walls:
            pygame.draw.rect(self.screen, WALL_COLOR, self.cell_rect(pos).inflate(-2, -2))
        for pos in self.board.target:
            pygame.draw.circle(self.screen, TARGET_COLOR, self.cell_rect(pos).center, CELL // 6)
        for pos in state.boxes_pos:
            rect = self.cell_rect(pos).inflate(-8, -8)
            pygame.draw.rect(self.screen, BOX_COLOR, rect)
            pygame.draw.rect(self.screen, BOX_EDGE, rect, width=2)
            if pos in self.board.target:
                pygame.draw.rect(self.screen, DONE_COLOR, rect, width=3)
        pygame.draw.circle(self.screen, AGENT_COLOR,
                           self.cell_rect(state.agent_pos).center, CELL // 2 - 5)

    def draw_center_text(self, text, font, center):
        label = font.render(text, True, TEXT_COLOR)
        self.screen.blit(label, label.get_rect(center=center))

    def draw_menu(self):
        cx, cy = self.board_rect.center
        self.draw_center_text("Choose an algorithm", self.big_font, (cx, cy - 130))
        for i, (rect, (name, _)) in enumerate(zip(self.buttons, ALGORITHMS)):
            pygame.draw.rect(self.screen, BOARD_BG, rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, rect, width=2)
            self.draw_center_text(f"{i + 1}. {name}", self.big_font, rect.center)
        if self.message:
            self.draw_center_text(self.message, self.font, (cx, cy + 140))

    def path_lines(self) -> list[str]:
        """Actions done so far, wrapped to the panel width; only the last lines are kept."""
        done = self.action_names[:self.index]
        if not done:
            return ["Path: (no move yet)"]
        words = ["Path:"] + [n + "," for n in done[:-1]] + [done[-1]]
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if self.font.size(test)[0] <= self.info_rect.width - 20:
                cur = test
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        if len(lines) > PATH_LINES:
            lines = lines[-PATH_LINES:]
            lines[0] = "... " + lines[0]
        return lines

    def draw_info(self):
        pygame.draw.rect(self.screen, BORDER_COLOR, self.info_rect, width=1)
        x, y = self.info_rect.x + 10, self.info_rect.y + 6

        if self.mode == "menu":
            rows = ["Press 1 / 2 or click a button to choose an algorithm"]
        elif self.mode == "solving":
            rows = [f"Algorithm: {self.algo_name}", "Solving, please wait..."]
        else:
            if self.index == self.total_steps and self.index > 0:
                status = "Done"
            else:
                status = "Playing" if self.playing else "Paused"
            rows = [f"Algorithm: {self.algo_name}   Actions: {self.index} / {self.total_steps}   [{status}]",
                    self.stats,
                    "Space: play/pause   Left/Right: step   Esc: menu"] + self.path_lines()

        for row in rows:
            self.screen.blit(self.font.render(row, True, TEXT_COLOR), (x, y))
            y += 22

    def handle_event(self, event):
        if self.mode == "menu":
            if event.type == pygame.KEYDOWN:
                i = event.key - pygame.K_1
                if 0 <= i < len(ALGORITHMS):
                    self.start_solve(i)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.buttons):
                    if rect.collidepoint(event.pos):
                        self.start_solve(i)
        elif self.mode == "play" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle_play()
            elif event.key == pygame.K_RIGHT:
                self.step_next()
            elif event.key == pygame.K_LEFT:
                self.step_prev()
            elif event.key == pygame.K_ESCAPE:
                self.mode = "menu"
                self.playing = False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)
            self.update()

            self.screen.fill(BG_COLOR)
            self.draw_grid()
            if self.mode == "menu":
                self.draw_menu()
            elif self.mode == "solving":
                self.draw_center_text(f"Solving with {self.algo_name}...", self.big_font,
                                      self.board_rect.center)
            else:
                self.draw_map()
            self.draw_info()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    # python -m sokoban_single.ui.game_gui [map_path]
    game_gui(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MAP).run()