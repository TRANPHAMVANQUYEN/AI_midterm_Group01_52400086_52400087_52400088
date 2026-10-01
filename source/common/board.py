# Đọc file ma trận là bản đồ của trò chơi
from importlib.resources import path
import os
class Board:
    def __init__(self, map_path: str):
        self.map_path=map_path
        self.height=0
        self.width=0

        self.walls=set() # chứa tọa độ các ô tường
        self.target=set() # chứa tọa độ điểm đích

        self.initial_agent_pos =None
        self.initial_boxes_pos=set() # chứa tọa độ các ô hộp

        #lưu vị trí ban đầu
        self._load_map()
    def _load_map(self):
        if not os.path.exists(self.map_path):
            raise FileNotFoundError(f"Không tìm thấy file map: {self.map_path}")
        with open(self.map_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
            self.height=len(lines)
            self.width=max(len(line) for line in lines) if self.height>0 else 0
            for r, line in enumerate(lines):
                for c, char in enumerate(line):
                    pos = (r, c)
                    if char =='%':
                        self.walls.add(pos)
                    elif char =='A':
                        self.initial_agent_pos = pos
                    elif char =='B':
                        self.initial_boxes_pos.add(pos)
                    elif char =='D':
                        self.target.add(pos)
                    elif char =='C':
                        self.target.add(pos)
                        self.initial_boxes_pos.add(pos)
    def is_wall(self, pos: tuple[int, int]) -> bool:
        return pos in self.walls #kiểm tra xem vị trí có phải là tường không
    def is_target(self, pos: tuple[int, int]) -> bool:
        return pos in self.target #kiểm tra xem vị trí có phải là điểm đích không
                        