from copy import deepcopy
from random import choice, randint
from sys import exit

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BEIGE = (122, 117, 88)
RED = (237, 14, 55)
DARK_RED = (148, 12, 37)
GRAY = (79, 79, 79)
DARK_GRAY = (46, 46, 46)
GREEN = (46, 89, 48)
DARK_GREEN = (34, 66, 36)

# Цвет фона:
BOARD_BACKGROUND_COLOR = BEIGE

# Цвет яблока
APPLE_COLOR = RED
# Цвет границы яблока
BORDER_APPLE_COLOR = DARK_RED

# Цвет камня
STONE_COLOR = GRAY
# Цвет границы камня
BORDER_STONE_COLOR = DARK_GRAY

# Цвет змейки
SNAKE_COLOR = GREEN
# Цвет границы змейки
BORDER_SNAKE_COLOR = DARK_GREEN

# Координаты центра экрана
SCREEN_CENTER_X = SCREEN_WIDTH // 2
SCREEN_CENTER_Y = SCREEN_HEIGHT // 2

# Начальное значение позиции:
INITIAL_VALUE_POSITION = [SCREEN_CENTER_X, SCREEN_CENTER_Y]

# Толщина обводки
THICKNESS_OUTLINE = 2

# Количество камней
STONES_AMOUNT = 10
# Клетки, в которых не могут появиться камни (8 клеток вокруг змейки)
STONES_PROHIBITED_POSITIONS = [
    INITIAL_VALUE_POSITION,
    [SCREEN_CENTER_X + GRID_SIZE, SCREEN_CENTER_Y],
    [SCREEN_CENTER_X - GRID_SIZE, SCREEN_CENTER_Y],
    [SCREEN_CENTER_X, SCREEN_CENTER_Y + GRID_SIZE],
    [SCREEN_CENTER_X, SCREEN_CENTER_Y - GRID_SIZE],
    [SCREEN_CENTER_X + GRID_SIZE, SCREEN_CENTER_Y + GRID_SIZE],
    [SCREEN_CENTER_X - GRID_SIZE, SCREEN_CENTER_Y - GRID_SIZE],
    [SCREEN_CENTER_X + GRID_SIZE, SCREEN_CENTER_Y - GRID_SIZE],
    [SCREEN_CENTER_X - GRID_SIZE, SCREEN_CENTER_Y + GRID_SIZE]
]


screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(
            self,
            body_color=BOARD_BACKGROUND_COLOR,
    ):
        self.body_color = body_color
        self.position = INITIAL_VALUE_POSITION

    def draw(self):
        """Метод отрисовки объекта на экране."""
        raise NotImplementedError(f'{type(self).__name__} должен '
                                  'реализовывать свой метод отрисовывания '
                                  'на экране.')

    def draw_cell(self, position, body_color=None, border_color=None,
                  thickness_outline=THICKNESS_OUTLINE):
        """
        Метод для отрисовки одной клетки на экране.

        Связан с методом draw().
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(
            screen,
            border_color,
            rect,
            thickness_outline
        )


class InteractionObjects(GameObject):
    """
    Класс для создания объектов взаимодействия.

    С помощью этого класса создаются объекты,
    с которыми взаимодействует Змейка.
    """

    def __init__(self, body_color):
        super().__init__(body_color)

    def randomize_position(self, occupied_cells=None):
        """
        Метод для генерации случайных координат.

        Генерирует случайные координаты ОДНОЙ клетки объекта взаимодействия.
        """
        occupied_cells = occupied_cells or []
        is_in_occupied_cells = True
        while is_in_occupied_cells:
            self.position = [
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            ]
            if self.position not in occupied_cells:
                is_in_occupied_cells = False

    def draw(self, position=None, body_color=BEIGE, border_color=BEIGE,
             thickness_outline=THICKNESS_OUTLINE):
        """Метод для отрисовки объекта на экране."""
        position = position or self.position
        self.draw_cell(position, body_color, border_color, thickness_outline)


class Apple(InteractionObjects):
    """Класс для создания объекта Яблоко."""

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position(self.occupied_cells)

    def draw(
            self, body_color=APPLE_COLOR, border_color=BORDER_APPLE_COLOR
    ):
        """Метод для отрисовки яблока на экране."""
        self.draw_cell(self.position, body_color,
                       border_color)


class Stone(InteractionObjects):
    """Класс для создания объекта Камень."""

    def __init__(self, body_color=STONE_COLOR):
        super().__init__(body_color)
        # Генератору камней не нужно учитывать занятые позиции, поскольку
        # камни генерируются в приоритетном порядке после змейки, а со змейкой
        # они пересечься не могут.
        self.stones_coordinates = self.add_positions()

    def add_positions(self):
        """Метод для генерации камней."""
        stones_coordinates = []
        for _ in range(STONES_AMOUNT):
            # Бесконечный цикл для избежания появления камней друг на друге.
            while True:
                self.randomize_position(STONES_PROHIBITED_POSITIONS)
                if self.position in stones_coordinates:
                    continue
                stones_coordinates.append(self.position)
                break
        return stones_coordinates

    def draw(
            self,
            body_color=STONE_COLOR,
            border_color=BORDER_STONE_COLOR
    ):
        """Метод для отрисовки камней на экране."""
        for stone_coordinate in self.stones_coordinates:
            self.draw_cell(
                stone_coordinate,
                body_color,
                border_color
            )


class Snake(GameObject):
    """Класс для создания объекта Змейка."""

    def __init__(
            self,
            length=1,
            positions=None,
            direction=RIGHT,
            body_color=SNAKE_COLOR,
    ):
        super().__init__(body_color)
        self.length = length
        if positions is None:
            self.positions = [self.position]
        else:
            self.positions = positions
        self.direction = direction
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Метод для получения координат головы змейки."""
        return deepcopy(self.positions[0])

    def update_direction(self):
        """Метод, меняющий направление движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод, отвечающий за перемещение змейки по полю."""
        current_head_coordinates = self.get_head_position()
        moving = [offset * GRID_SIZE for offset in self.direction]
        current_head_coordinates[0] = ((current_head_coordinates[0]
                                        + moving[0]) % SCREEN_WIDTH)
        current_head_coordinates[1] = ((current_head_coordinates[1]
                                        + moving[1]) % SCREEN_HEIGHT)
        self.positions.insert(0, current_head_coordinates)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(
            self,
            body_color=SNAKE_COLOR,
            border_color=BORDER_SNAKE_COLOR
    ):
        """Метод для отрисовки змейки на экране."""
        self.draw_cell(
            self.get_head_position(),
            body_color,
            border_color
        )
        # Затирание последнего сегмента
        if self.last:
            self.draw_cell(self.last, BEIGE, BEIGE)

    def reset(self):
        """Метод, возвращающий змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([LEFT, RIGHT, UP, DOWN])


def handle_keys(game_object):
    """
    Функция обработки нажатий клавиш пользователем,
    отвечающих за смену направления змейки.
    """
    TURNS = {
        pg.K_UP: (UP, DOWN),
        pg.K_DOWN: (DOWN, UP),
        pg.K_LEFT: (LEFT, RIGHT),
        pg.K_RIGHT: (RIGHT, LEFT)
    }
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        elif event.type == pg.KEYDOWN and event.key in TURNS:
            new_direction, opposite = TURNS.get(event.key)
            if game_object.direction != opposite:
                game_object.next_direction = new_direction


def main():
    """Главная функция программы."""
    pg.init()
    speed = 4  # Скорость движения змейки
    snake = Snake()
    stones = Stone()
    apple = Apple()
    apple.occupied_cells = snake.positions + stones.stones_coordinates
    screen.fill(BOARD_BACKGROUND_COLOR)
    points_count = 0  # Переменная для подсчёта количества съеденных яблок

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        snake_current_head_coordinates = snake.get_head_position()

        if snake_current_head_coordinates == apple.position:
            snake.length += 1
            points_count += 1
            apple.randomize_position([
                *snake.positions,
                *stones.stones_coordinates
            ])
            if points_count % 4 == 0:
                speed += 1

        first_condition = snake_current_head_coordinates in snake.positions[1:]
        second_condition = (snake_current_head_coordinates
                            in stones.stones_coordinates)
        if first_condition or second_condition:
            points_count = 0
            # Метод гарантирует появление змейки в середине экрана.
            # После сброса игры учтено, что камни и яблоки не могут появиться
            # в середине экрана (там же, где и змейка).
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            # Избегаем появления яблока в клетке появления Змейки.
            apple.randomize_position([
                *snake.positions,
                *stones.stones_coordinates,
                *INITIAL_VALUE_POSITION
            ])
        stones.draw()
        snake.draw()
        apple.draw()
        pg.display.update()
        clock.tick(speed)


if __name__ == '__main__':
    main()
