import os
import sys
import pygame
from sokoban_single.ui.game_gui import game_gui

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Choose map")
font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

MAPS_DIR = "maps"
maps = [f for f in os.listdir(MAPS_DIR) if f.endswith(".txt")] if os.path.exists(MAPS_DIR) else []
DEFAULT_MAP = os.path.join(MAPS_DIR, maps[0]) if maps else "maps/example_map.txt"
font=pygame.font.SysFont("timesnewroman", 24)
text=font.render("Choose a map to solve:", True, (30, 35, 45))

def choose_map():
    running = True
    selected_map = DEFAULT_MAP
    
    # Tạo danh sách các rect nút bấm tương ứng từng file txt
    buttons = [pygame.Rect(250, 100 + i * 60, 300, 45) for i in range(len(maps))]

    while running:
        screen.fill((232, 238, 245))
        screen.blit(text, (250, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        selected_map = os.path.join(MAPS_DIR, maps[i])
                        running = False
            elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if idx < len(maps):
                    selected_map = os.path.join(MAPS_DIR, maps[idx])
                    running = False

        # Vẽ danh sách các file map
        for i, (rect, map_name) in enumerate(zip(buttons, maps)):
            pygame.draw.rect(screen, (255, 255, 255), rect)
            pygame.draw.rect(screen, (30, 35, 45), rect, 2)
            txt_surface = font.render(f"{i + 1}. {map_name}", True, (30, 35, 45))
            screen.blit(txt_surface, txt_surface.get_rect(center=rect.center))

        pygame.display.flip()
        clock.tick(30)

    return selected_map

def main():
    map_path = sys.argv[1] if len(sys.argv) > 1 else choose_map()
    game_gui(map_path).run()

if __name__ == "__main__":
    main()