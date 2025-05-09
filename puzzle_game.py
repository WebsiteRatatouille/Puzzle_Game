import pygame
import sys
import random
import numpy as np
from collections import deque
import heapq
import time
from solver import solve_bfs, solve_astar, is_solvable
import subprocess

pygame.init()

WINDOW_SIZE = 600
GRID_SIZE = 3
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
DARK_GRAY = (180, 180, 180)
BLUE = (70, 130, 180)
RED = (200, 60, 60)
GREEN = (100, 180, 120)
YELLOW = (220, 200, 80)
BG_GRAD1 = (235, 240, 245)
BG_GRAD2 = (210, 220, 230)
MAX_SEARCH_TIME = 1.0

# Màu cho từng số (đơn giản: trắng, ô trống xám)
TILE_COLORS = [GRAY] + [WHITE]*8

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 160))
pygame.display.set_caption('8-Puzzle Game')

FONT = pygame.font.SysFont('arial', 48, bold=True)
BUTTON_FONT = pygame.font.SysFont('arial', 24, bold=False)
SMALL_FONT = pygame.font.SysFont('arial', 28, bold=True)

# Vẽ nền gradient
def draw_gradient():
    for y in range(WINDOW_SIZE + 120):
        color = [BG_GRAD1[i] + (BG_GRAD2[i] - BG_GRAD1[i]) * y // (WINDOW_SIZE + 120) for i in range(3)]
        pygame.draw.line(screen, color, (0, y), (WINDOW_SIZE, y))

class PuzzleState:
    def __init__(self, board, parent=None, move=None, depth=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.cost = self.calculate_manhattan()
        self.hash = hash(self.board.tobytes())
    def __hash__(self):
        return self.hash
    def __eq__(self, other):
        return np.array_equal(self.board, other.board)
    def calculate_manhattan(self):
        cost = 0
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                val = self.board[i, j]
                if val != 0:
                    x_goal = (val - 1) // GRID_SIZE
                    y_goal = (val - 1) % GRID_SIZE
                    cost += abs(x_goal - i) + abs(y_goal - j)
        return cost
    def __lt__(self, other):
        return (self.cost + self.depth) < (other.cost + other.depth)
    def get_blank_pos(self):
        pos = np.argwhere(self.board == 0)[0]
        return tuple(pos)
    def get_possible_moves(self):
        moves = []
        x, y = self.get_blank_pos()
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                moves.append((nx, ny))
        return moves
    def get_new_state(self, new_pos):
        new_board = self.board.copy()
        x, y = self.get_blank_pos()
        nx, ny = new_pos
        new_board[x, y], new_board[nx, ny] = new_board[nx, ny], new_board[x, y]
        return PuzzleState(new_board, self, (nx, ny), self.depth + 1)

def get_solution_path(state):
    path = []
    while state.parent is not None:
        path.append(state.move)
        state = state.parent
    return path[::-1]

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
    def draw(self, surface, mouse_pos):
        color = DARK_GRAY if self.rect.collidepoint(mouse_pos) else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        text_surf = BUTTON_FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Game:
    def __init__(self):
        self.reset_game()
        self.algorithm = "A*"
        self.solution = None
        self.current_step = 0
        self.message = ""
        self.message_time = 0
        # Căn đều 3 nút ở dưới
        btn_w, btn_h = 150, 48
        gap = (WINDOW_SIZE - btn_w*3)//4
        y_btn = WINDOW_SIZE + 30
        self.buttons = [
            Button((gap, y_btn, btn_w, btn_h), "Reset"),
            Button((2*gap+btn_w, y_btn, btn_w, btn_h), "Switch Algorithm"),
            Button((3*gap+2*btn_w, y_btn, btn_w, btn_h), "Hint"),
            Button((WINDOW_SIZE - 170, WINDOW_SIZE + 100, 150, 42), "Switch to 4x4")
        ]
    def reset_game(self):
        self.board = np.arange(1, 9).tolist() + [0]
        while True:
            random.shuffle(self.board)
            arr = np.array(self.board).reshape((3, 3))
            if is_solvable(arr):
                self.board = arr
                break
        self.solution = None
        self.current_step = 0
        self.message = ""
    def draw(self):
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        # Vẽ lưới
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                val = self.board[i, j]
                rect = pygame.Rect(j*CELL_SIZE+12, i*CELL_SIZE+12, CELL_SIZE-24, CELL_SIZE-24)
                color = TILE_COLORS[val]
                pygame.draw.rect(screen, color, rect, border_radius=8)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
                if val != 0:
                    text = FONT.render(str(val), True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
        # Vẽ các nút
        for btn in self.buttons:
            btn.draw(screen, mouse_pos)
        # Hiển thị thuật toán
        algo_text = SMALL_FONT.render(f"Algorithm: {self.algorithm}", True, BLACK)
        screen.blit(algo_text, (30, WINDOW_SIZE+90))
        # Hiển thị thông báo
        if self.message:
            box_w, box_h = 500, 60
            box_x = (WINDOW_SIZE - box_w) // 2
            box_y = 20
            notif_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            color = (60, 180, 90) if "Completed" in self.message else (200, 0, 0)
            border_color = (0, 120, 40) if "Completed" in self.message else (150, 0, 0)
            pygame.draw.rect(screen, color, notif_rect, border_radius=16)
            pygame.draw.rect(screen, border_color, notif_rect, 4, border_radius=16)
            notif_font = pygame.font.SysFont('arial', 32, bold=True)
            notif_text = notif_font.render(self.message, True, WHITE)
            notif_text_rect = notif_text.get_rect(center=notif_rect.center)
            screen.blit(notif_text, notif_text_rect)
        pygame.display.flip()
    def handle_click(self, pos):
        for idx, btn in enumerate(self.buttons):
            if btn.is_clicked(pos):
                if idx == 0:
                    self.reset_game()
                elif idx == 1:
                    self.algorithm = "BFS" if self.algorithm == "A*" else "A*"
                    self.message = ""
                    self.message_time = 0
                elif idx == 2:
                    self.get_hint()
                    
                elif idx == 3:
                    pygame.quit()
                    subprocess.Popen(["python", "play.py"])
                    sys.exit()
                return
        # Di chuyển ô
        if pos[1] < WINDOW_SIZE:
            row, col = (pos[1]-12)//CELL_SIZE, (pos[0]-12)//CELL_SIZE
            if 0 <= row < 3 and 0 <= col < 3:
                self.move_tile(row, col)
    def move_tile(self, row, col):
        blank = tuple(np.argwhere(self.board == 0)[0])
        if (abs(row-blank[0]) == 1 and col == blank[1]) or (abs(col-blank[1]) == 1 and row == blank[0]):
            self.board[blank], self.board[row, col] = self.board[row, col], self.board[blank]
            self.solution = None
            self.current_step = 0
            if self.is_solved():
                self.show_congratulations()
    def get_hint(self):
        current_state = PuzzleState(self.board.copy())
        if self.algorithm == "A*":
            self.solution = solve_astar(current_state)
        else:
            self.solution = solve_bfs(current_state)
        self.current_step = 0
        if not self.solution:
            self.message = "Solution not found!"
            self.message_time = pygame.time.get_ticks()
            return
        if self.current_step < len(self.solution):
            next_move = self.solution[self.current_step]
            blank = tuple(np.argwhere(self.board == 0)[0])
            self.board[blank], self.board[next_move] = self.board[next_move], self.board[blank]
            self.current_step += 1
            if self.is_solved():
                self.show_congratulations()
    def is_solved(self):
        return np.array_equal(self.board, np.array([[1,2,3],[4,5,6],[7,8,0]]))
    def show_congratulations(self):
        self.message = "Completed the puzzle!"
        self.message_time = pygame.time.get_ticks()

def main():
    game = Game()
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
        # Ẩn thông báo sau 2 giây
        if game.message and pygame.time.get_ticks() - game.message_time > 2000:
            game.message = ""
        game.draw()
        clock.tick(60)

if __name__ == "__main__":
    main() 