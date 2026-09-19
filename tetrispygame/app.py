import os
import random
import pygame

# Инициализация Pygame
pygame.init()

# Настройки игрового поля
ROW_COUNT = 20
COL_COUNT = 10
CELL_SIZE = 30
SCORE_PANEL_WIDTH = 180

# Размеры окна
WIDTH = COL_COUNT * CELL_SIZE + SCORE_PANEL_WIDTH
HEIGHT = ROW_COUNT * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Тетрис 2D")
clock = pygame.time.Clock()

# Путь к файлу с рекордом
HIGHSCORE_FILE = "highscore.txt"

# Цвета (RGB)
BLACK = (20, 20, 20)
GRID_COLOR = (40, 40, 40)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

SHAPE_COLORS = [
    (0, 255, 255),  # I - Бирюзовый
    (255, 255, 0),  # O - Желтый
    (128, 0, 128),  # T - Пурпурный
    (0, 255, 0),  # S - Зеленый
    (255, 0, 0),  # Z - Красный
    (0, 0, 255),  # J - Синий
    (255, 165, 0),  # L - Оранжевый
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]


def load_highscore():
    """Загрузка рекорда из файла."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except ValueError:
            return 0
    return 0


def save_highscore(score):
    """Сохранение рекорда в файл."""
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


class Piece:

    def __init__(self):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.matrix = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]
        self.x = COL_COUNT // 2 - len(self.matrix[0]) // 2
        self.y = 0

    def rotate(self):
        return [list(row) for row in zip(*self.matrix[::-1])]


class Tetris:

    def __init__(self):
        self.grid = [[None for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
        self.current_piece = Piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.highscore = load_highscore()

    def check_collision(self, matrix, offset_x, offset_y):
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                if val:
                    new_x = self.current_piece.x + c + offset_x
                    new_y = self.current_piece.y + r + offset_y
                    if (
                        new_x < 0
                        or new_x >= COL_COUNT
                        or new_y >= ROW_COUNT
                        or (new_y >= 0 and self.grid[new_y][new_x])
                    ):
                        return True
        return False

    def lock_piece(self):
        for r, row in enumerate(self.current_piece.matrix):
            for c, val in enumerate(row):
                if val:
                    py = self.current_piece.y + r
                    px = self.current_piece.x + c
                    if py >= 0:
                        self.grid[py][px] = self.current_piece.color

        self.clear_lines()
        self.current_piece = Piece()

        # Проверка на Game Over
        if self.check_collision(self.current_piece.matrix, 0, 0):
            self.game_over = True
            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = ROW_COUNT - len(new_grid)

        while len(new_grid) < ROW_COUNT:
            new_grid.insert(0, [None for _ in range(COL_COUNT)])

        self.grid = new_grid

        # Подсчет очков
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 700
        elif lines_cleared == 4:
            self.score += 1500

        # Динамическое обновление рекорда прямо во время игры
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def move(self, dx):
        if not self.check_collision(self.current_piece.matrix, dx, 0):
            self.current_piece.x += dx

    def drop(self):
        if not self.check_collision(self.current_piece.matrix, 0, 1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    def hard_drop(self):
        while not self.check_collision(self.current_piece.matrix, 0, 1):
            self.current_piece.y += 1
        self.lock_piece()

    def rotate_piece(self):
        rotated = self.current_piece.rotate()
        if not self.check_collision(rotated, 0, 0):
            self.current_piece.matrix = rotated

    def toggle_pause(self):
        self.paused = not self.paused

    def draw(self):
        screen.fill(BLACK)

        # Отрисовка сетки и зафиксированных блоков
        for r in range(ROW_COUNT):
            for c in range(COL_COUNT):
                rect = pygame.Rect(
                    c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)
                if self.grid[r][c]:
                    pygame.draw.rect(screen, self.grid[r][c], rect)

        # Отрисовка падающей фигуры
        p = self.current_piece
        for r, row in enumerate(p.matrix):
            for c, val in enumerate(row):
                if val:
                    rect = pygame.Rect(
                        (p.x + c) * CELL_SIZE,
                        (p.y + r) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, p.color, rect)

        # Отрисовка интерфейса (Счет и Рекорд)
        font = pygame.font.SysFont("Arial", 22)
        panel_x = COL_COUNT * CELL_SIZE + 15

        # Вывод текущего счета
        screen.blit(font.render("Текущий счет:", True, GRAY), (panel_x, 30))
        screen.blit(
            font.render(str(self.score), True, WHITE), (panel_x, 55)
        )

        # Вывод рекорда
        screen.blit(font.render("Рекорд:", True, GRAY), (panel_x, 110))
        screen.blit(
            font.render(str(self.highscore), True, (255, 215, 0)),
            (panel_x, 135),
        )

        # Оверлей паузы
        if self.paused:
            pause_font = pygame.font.SysFont("Arial", 36, bold=True)
            sub_font = pygame.font.SysFont("Arial", 18)

            # Затемнение игрового поля
            overlay = pygame.Surface(
                (COL_COUNT * CELL_SIZE, HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            p_text = pause_font.render("ПАУЗА", True, WHITE)
            s_text = sub_font.render("Нажмите ESC для продолжения", True, GRAY)

            screen.blit(p_text, (COL_COUNT * CELL_SIZE // 2 - 55, HEIGHT // 2 - 30))
            screen.blit(s_text, (COL_COUNT * CELL_SIZE // 2 - 110, HEIGHT // 2 + 15))

        # Сообщение Game Over
        if self.game_over:
            go_font = pygame.font.SysFont("Arial", 40, bold=True)
            go_text = go_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(go_text, (COL_COUNT * CELL_SIZE // 6, HEIGHT // 2 - 20))

        pygame.display.flip()


def main():
    game = Tetris()
    fall_time = 0
    fall_speed = 500  # Скорость падения фигуры (в мс)

    run = True
    while run:
        fall_time += clock.get_rawtime()
        clock.tick()

        # Падение происходит только если нет паузы и игра не окончена
        if fall_time >= fall_speed and not game.game_over and not game.paused:
            game.drop()
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not game.game_over:
                    game.toggle_pause()

                # Управление блокируется во время паузы или завершения игры
                if not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1)
                    elif event.key == pygame.K_DOWN:
                        game.drop()
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        game.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
