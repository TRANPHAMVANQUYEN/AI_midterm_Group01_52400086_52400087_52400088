import threading
import time
from pathlib import Path

import pygame

from sokoban_competitive.agents.agent_1 import Agent1
from sokoban_competitive.agents.agent_2 import Agent2
from sokoban_competitive.environment import CompetitiveEnvironment
from sokoban_single.models.action import Action


BACKGROUND = (235, 239, 242)
FLOOR = (250, 249, 242)
GRID = (214, 216, 212)
WALL = (87, 95, 99)
TEXT = (34, 42, 46)
BLUE = (49, 118, 194)
ORANGE = (222, 132, 54)
NEUTRAL_BOX = (154, 119, 75)
WHITE = (255, 255, 255)
ROUND_DELAY = 0.45


class CompetitiveGUI:
	def __init__(self, map_path: str | Path, max_rounds: int = 40):
		self.environment = CompetitiveEnvironment(map_path)
		self.agents = [Agent1(), Agent2()]
		self.state = self.environment.initial_state
		self.max_rounds = max(1, max_rounds)
		self.phase = "setup"
		self.last_actions = ["Waiting", "Waiting"]
		self.last_tick = time.perf_counter()
		self.pending = False
		self.turn_result = None
		self.return_to_menu = False

		pygame.init()
		pygame.display.set_caption("Competitive Sokoban")
		self.title_font = pygame.font.SysFont("arial", 30, bold=True)
		self.font = pygame.font.SysFont("arial", 20)
		self.small_font = pygame.font.SysFont("arial", 16)
		self.set_board_size()
		self.clock = pygame.time.Clock()

	def set_board_size(self):
		self.cell_size = min(58, 620 // self.environment.height, 760 // self.environment.width)
		self.cell_size = max(24, self.cell_size)
		self.board_x = 36
		self.board_y = 104
		self.board_width = self.environment.width * self.cell_size
		self.board_height = self.environment.height * self.cell_size
		self.panel_x = self.board_x + self.board_width + 34
		self.screen = pygame.display.set_mode(
			(self.panel_x + 320, max(620, self.board_y + self.board_height + 42))
		)

	def start_round_worker(self):
		if self.pending:
			return
		self.pending = True
		current_state = self.state

		def calculate_round():
			actions = [None, None]

			def ask_agent(index):
				try:
					actions[index] = self.agents[index].choose_action(
						self.environment, current_state, index, 1.0
					)
				except Exception:
					actions[index] = None

			workers = [
				threading.Thread(target=ask_agent, args=(index,), daemon=True)
				for index in range(2)
			]
			for worker in workers:
				worker.start()
			for worker in workers:
				worker.join(1.05)

			directions = [
				"Wait" if action is None else Action.to_string(action)
				for action in actions
			]
			next_state = self.environment.resolve_round(current_state, actions)
			self.turn_result = (next_state, directions)

		threading.Thread(target=calculate_round, daemon=True).start()

	def update(self):
		if self.turn_result is not None:
			self.state, self.last_actions = self.turn_result
			self.turn_result = None
			self.pending = False
			if self.state.round_number >= self.max_rounds:
				self.phase = "finished"

		if self.phase != "playing" or self.pending:
			return
		now = time.perf_counter()
		if now - self.last_tick >= ROUND_DELAY:
			self.last_tick = now
			self.start_round_worker()

	def restart(self):
		self.state = self.environment.initial_state
		self.last_actions = ["Waiting", "Waiting"]
		self.turn_result = None
		self.pending = False
		self.phase = "setup"

	def cell_rect(self, position):
		row, col = position
		return pygame.Rect(
			self.board_x + col * self.cell_size,
			self.board_y + row * self.cell_size,
			self.cell_size,
			self.cell_size,
		)

	def draw_text(self, text, font, position, color=TEXT):
		self.screen.blit(font.render(text, True, color), position)

	def draw_board(self):
		board_rect = pygame.Rect(
			self.board_x, self.board_y, self.board_width, self.board_height
		)
		pygame.draw.rect(self.screen, FLOOR, board_rect)

		for row in range(self.environment.height):
			for col in range(self.environment.width):
				position = (row, col)
				rect = self.cell_rect(position)
				if self.environment.is_wall(position):
					pygame.draw.rect(self.screen, WALL, rect.inflate(-2, -2))
				else:
					pygame.draw.rect(self.screen, GRID, rect, width=1)

		target_colors = (BLUE, ORANGE)
		for target in self.environment.targets:
			rect = self.cell_rect(target)
			pygame.draw.circle(self.screen, (205, 77, 72), rect.center, self.cell_size // 5)

		owners = dict(self.state.goal_owners)
		for box in self.state.boxes:
			rect = self.cell_rect(box).inflate(-10, -10)
			if box in owners:
				color = target_colors[owners[box]]
			else:
				color = NEUTRAL_BOX
			pygame.draw.rect(self.screen, color, rect, border_radius=3)
			pygame.draw.rect(self.screen, TEXT, rect, width=2, border_radius=3)

		for agent_index, position in enumerate(self.state.agent_positions):
			color = target_colors[agent_index]
			center = self.cell_rect(position).center
			pygame.draw.circle(self.screen, color, center, self.cell_size // 3)
			label = self.small_font.render(str(agent_index + 1), True, WHITE)
			self.screen.blit(label, label.get_rect(center=center))

	def draw_panel(self):
		score_one, score_two = self.environment.scores(self.state)
		self.draw_text("MATCH", self.title_font, (self.panel_x, 106))
		self.draw_text(
			f"Round  {self.state.round_number} / {self.max_rounds}",
			self.font,
			(self.panel_x, 158),
		)
		self.draw_text(f"Agent 1: {score_one}", self.font, (self.panel_x, 204), BLUE)
		self.draw_text(f"Agent 2: {score_two}", self.font, (self.panel_x, 236), ORANGE)
		self.draw_text("Last actions", self.font, (self.panel_x, 294))
		self.draw_text(f"Agent 1: {self.last_actions[0]}", self.small_font, (self.panel_x, 326))
		self.draw_text(f"Agent 2: {self.last_actions[1]}", self.small_font, (self.panel_x, 350))

		if self.phase == "setup":
			self.draw_text("SET ROUND LIMIT", self.font, (self.panel_x, 410))
			self.draw_text(f"{self.max_rounds} rounds", self.title_font, (self.panel_x, 444))
			self.draw_text("Up/Down: change by 1", self.small_font, (self.panel_x, 492))
			self.draw_text("Space: start", self.small_font, (self.panel_x, 516))
		elif self.phase == "playing":
			self.draw_text("Space: pause", self.small_font, (self.panel_x, 432))
			self.draw_text("R: restart", self.small_font, (self.panel_x, 456))
		elif self.phase == "paused":
			self.draw_text("PAUSED", self.title_font, (self.panel_x, 420))
			self.draw_text("Space: resume", self.small_font, (self.panel_x, 468))
		elif self.phase == "finished":
			self.draw_text("MATCH FINISHED", self.font, (self.panel_x, 418))
			if score_one > score_two:
				winner = "Agent 1 wins"
				color = BLUE
			elif score_two > score_one:
				winner = "Agent 2 wins"
				color = ORANGE
			else:
				winner = "Draw"
				color = TEXT
			self.draw_text(winner, self.title_font, (self.panel_x, 454), color)
			self.draw_text("R: new match", self.small_font, (self.panel_x, 504))
		self.draw_text("Esc: choose another map", self.small_font, (self.panel_x, 560))

	def draw(self):
		self.screen.fill(BACKGROUND)
		self.draw_text("Competitive Sokoban", self.title_font, (36, 34))
		self.draw_board()
		self.draw_panel()
		pygame.display.flip()

	def handle_event(self, event):
		if event.type == pygame.QUIT:
			self.running = False
			return
		if event.type != pygame.KEYDOWN:
			return True
		if event.key == pygame.K_ESCAPE:
			self.return_to_menu = True
			self.running = False
			return
		if event.key == pygame.K_SPACE:
			if self.phase in ("setup", "paused"):
				self.phase = "playing"
				self.last_tick = time.perf_counter()
			elif self.phase == "playing":
				self.phase = "paused"
			return

		if self.phase == "setup":
			if event.key == pygame.K_UP:
				self.max_rounds += 1
			elif event.key == pygame.K_DOWN:
				self.max_rounds = max(1, self.max_rounds - 1)
		elif self.phase == "playing":
			if event.key == pygame.K_r:
				self.restart()
		elif self.phase == "paused":
			if event.key == pygame.K_r:
				self.restart()
		elif self.phase == "finished" and event.key == pygame.K_r:
			self.restart()
		return True

	def run(self):
		self.running = True
		while self.running:
			for event in pygame.event.get():
				self.handle_event(event)
				if not self.running:
					break
			self.update()
			self.draw()
			self.clock.tick(60)
		return "menu" if self.return_to_menu else "quit"


if __name__ == "__main__":
	from sokoban_competitive.main import main

	main()
