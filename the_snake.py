from copy import deepcopy
from random import choice, randint

import pygame

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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (122, 117, 88)

# Цвет яблока
APPLE_COLOR = (237, 14, 55)
# Цвет границы яблока
BORDER_APPLE_COLOR = (148, 12, 37)

# Цвет камня
STONE_COLOR = (79, 79, 79)
# Цвет границы камня
BORDER_STONE_COLOR = (46, 46, 46)

# Цвет змейки
SNAKE_COLOR = (46, 89, 48)
# Цвет границы змейки
BORDER_SNAKE_COLOR = (34, 66, 36)

# Координаты центра экрана
SCREEN_CENTER_X = SCREEN_WIDTH // 2
SCREEN_CENTER_Y = SCREEN_HEIGHT // 2

# Толщина обводки
THICKNESS_OUTLINE = 2


# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        self.position = [SCREEN_CENTER_X, SCREEN_CENTER_Y]
        self.body_color = body_color

    def draw(self):
        """Метод отрисовывания объекта на экране."""
        pass


class InteractionObjects(GameObject):
    """
    Класс для создания объектов,
    с которыми взаимодействует Змейка.
    """

    def __init__(self, body_color):
        super().__init__(body_color)

    def randomize_position(self):
        """
        Метод для генерации случайных координат положения
        объекта взаимодействия.
        """
        return [
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        ]

    def draw(self, border_color, thickness_outline):
        """Метод для отрисовки объекта на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(
            screen,
            border_color,
            rect,
            thickness_outline
        )


class Apple(InteractionObjects):
    """Класс для создания объекта Яблоко."""

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.position = super().randomize_position()

    def draw(
            self, border_color=BORDER_APPLE_COLOR,
            thickness_outline=THICKNESS_OUTLINE
    ):
        """Метод для отрисовки яблока на экране."""
        super().draw(border_color, thickness_outline)


class Stone(InteractionObjects):
    """Класс для создания объекта Камень."""

    def __init__(self, body_color=STONE_COLOR):
        super().__init__(body_color)
        self.stones_coordinates = []
        ITERATION_NUMBER = 9
        for _ in range(ITERATION_NUMBER):
            self.stones_coordinates.append(super().randomize_position())

    def draw(
            self, border_color=BORDER_STONE_COLOR,
            thickness_outline=THICKNESS_OUTLINE
    ):
        """Метод для отрисовки камней на экране."""
        for stone_coordinate in self.stones_coordinates:
            self.position = stone_coordinate
            super().draw(border_color, thickness_outline)


class Snake(GameObject):
    """Класс для создания объекта Змейка."""

    def __init__(
            self,
            length=1,
            positions=[[SCREEN_CENTER_X, SCREEN_CENTER_Y]],
            direction=RIGHT,
            body_color=SNAKE_COLOR
    ):
        super().__init__(body_color)
        self.length = length
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
        if self.direction == LEFT:
            current_head_coordinates[0] = ((current_head_coordinates[0]
                                            - GRID_SIZE) % SCREEN_WIDTH)
        elif self.direction == RIGHT:
            current_head_coordinates[0] = ((current_head_coordinates[0]
                                           + GRID_SIZE) % SCREEN_WIDTH)
        elif self.direction == UP:
            current_head_coordinates[1] = ((current_head_coordinates[1]
                                           - GRID_SIZE) % SCREEN_HEIGHT)
        elif self.direction == DOWN:
            current_head_coordinates[1] = ((current_head_coordinates[1]
                                           + GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, current_head_coordinates)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Метод для отрисовки змейки на экране."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(
                screen,
                BORDER_SNAKE_COLOR,
                rect,
                THICKNESS_OUTLINE
            )

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(
            screen,
            BORDER_SNAKE_COLOR,
            head_rect,
            THICKNESS_OUTLINE
        )

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Метод, возвращающий змейку в начальное состояние."""
        self.length = 1
        self.positions = [[SCREEN_CENTER_X, SCREEN_CENTER_Y]]
        self.position = [SCREEN_CENTER_X, SCREEN_CENTER_Y]
        self.direction = choice([LEFT, RIGHT, UP, DOWN])


def handle_keys(game_object):
    """
    Функция обработки нажатий клавиш пользователем,
    отвечающих за смену направления змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Главная функция программы."""
    pygame.init()
    speed = 4  # Скорость движения змейки
    apple = Apple()
    snake = Snake()
    stones = Stone()
    screen.fill(BOARD_BACKGROUND_COLOR)
    points_count = 0  # Переменная для подсчёта количества съеденных яблок

    while True:
        handle_keys(snake)
        snake.update_direction()
        apple.randomize_position()
        snake.move()
        snake_current_head_coordinates = snake.get_head_position()
        if snake_current_head_coordinates == apple.position:
            snake.length += 1
            points_count += 1
            new_apple_coordinates = apple.randomize_position()
            while new_apple_coordinates in snake.positions:
                new_apple_coordinates = apple.randomize_position()
            apple.position = new_apple_coordinates
            if points_count % 4 == 0:
                speed += 1
        first_condition = snake_current_head_coordinates in snake.positions[1:]
        second_condition = (snake_current_head_coordinates
                            in stones.stones_coordinates)
        if first_condition or second_condition:
            points_count = 0
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        if snake_current_head_coordinates in stones.stones_coordinates:
            points_count = 0
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        stones.draw()
        snake.draw()
        apple.draw()
        pygame.display.update()
        clock.tick(speed)


if __name__ == '__main__':
    main()
