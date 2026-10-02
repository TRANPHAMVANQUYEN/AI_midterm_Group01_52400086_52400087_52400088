import argparse
from pathlib import Path

import pygame

from sokoban_competitive.gui_competitive import CompetitiveGUI


MAP_FOLDER = Path(__file__).parent / "maps"
BACKGROUND = (235, 239, 242)
TEXT = (34, 42, 46)
BLUE = (49, 118, 194)
WHITE = (255, 255, 255)


def choose_map(map_paths, selected_index):
	pygame.display.set_caption("Competitive Sokoban - Choose Map")
	screen_width = 640
	screen_height = max(420, 210 + len(map_paths) * 58)
	screen = pygame.display.set_mode((screen_width, screen_height))
	clock = pygame.time.Clock()
	title_font = pygame.font.SysFont("arial", 32, bold=True)
	font = pygame.font.SysFont("arial", 22)
	small_font = pygame.font.SysFont("arial", 17)
	map_rects = [
		pygame.Rect(150, 150 + index * 58, 340, 46)
		for index in range(len(map_paths))
	]

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					selected_index = (selected_index - 1) % len(map_paths)
				elif event.key == pygame.K_DOWN:
					selected_index = (selected_index + 1) % len(map_paths)
				elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
					return map_paths[selected_index], selected_index
				elif event.key == pygame.K_ESCAPE:
					return None
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				for index, rect in enumerate(map_rects):
					if rect.collidepoint(event.pos):
						return map_paths[index], index

		screen.fill(BACKGROUND)
		title = title_font.render("Choose a map", True, TEXT)
		screen.blit(title, title.get_rect(center=(screen_width // 2, 72)))
		for index, (map_path, rect) in enumerate(zip(map_paths, map_rects)):
			color = BLUE if index == selected_index else TEXT
			pygame.draw.rect(screen, WHITE, rect)
			pygame.draw.rect(screen, color, rect, width=2)
			label = font.render(map_path.stem, True, color)
			screen.blit(label, label.get_rect(center=rect.center))
		instruction = small_font.render(
			"Click a map to open; Up/Down then Enter also works; Esc to quit",
			True,
			TEXT,
		)
		screen.blit(instruction, instruction.get_rect(center=(screen_width // 2, screen_height - 42)))
		pygame.display.flip()
		clock.tick(60)


def main():
	parser = argparse.ArgumentParser(description="Two-agent competitive Sokoban")
	parser.add_argument("--map", help="Select this map when the menu opens")
	parser.add_argument("--steps", type=int, default=40, help="Starting round limit")
	arguments = parser.parse_args()
	map_paths = sorted(MAP_FOLDER.glob("*.txt"))
	if arguments.map:
		requested_map = Path(arguments.map).resolve()
		matching_index = next(
			(
				index
				for index, map_path in enumerate(map_paths)
				if map_path.resolve() == requested_map
			),
			None,
		)
		if matching_index is None:
			map_paths.insert(0, requested_map)
			selected_index = 0
		else:
			selected_index = matching_index
	else:
		selected_index = 0

	if not map_paths:
		raise FileNotFoundError(f"No map files found in {MAP_FOLDER}")

	pygame.init()
	try:
		while True:
			selection = choose_map(map_paths, selected_index)
			if selection is None:
				break
			map_path, selected_index = selection
			result = CompetitiveGUI(map_path, max(1, arguments.steps)).run()
			if result == "quit":
				break
	finally:
		pygame.quit()


if __name__ == "__main__":
	main()
