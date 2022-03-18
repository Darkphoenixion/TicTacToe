import pygame as pg

import sys
# import random

FPS = 30
TILE_SIZE = 128
SQUARE_GRID_SIZE = 3
LINE_SIZE = 32
WINDOWS_SIZE = (SQUARE_GRID_SIZE * TILE_SIZE, (SQUARE_GRID_SIZE * TILE_SIZE) + LINE_SIZE)

BLOCK_COLOR = (240, 240, 240)

P1 = "P1"
P2 = "P2"


class Circle:
    @classmethod
    def draw(cls, surface: pg.Surface):
        pg.draw.circle(surface, (10, 10, 10), surface.get_rect().center, TILE_SIZE / 4, 5)


class Cross:
    @classmethod
    def draw(cls, surface: pg.Surface):
        _start = (surface.get_rect().centerx - TILE_SIZE // 4, surface.get_rect().centery - TILE_SIZE // 4)
        _end = (surface.get_rect().centerx + TILE_SIZE // 4, surface.get_rect().centery + TILE_SIZE // 4)
        pg.draw.line(surface, (10, 10, 10), _start, _end, 8)

        _start = (surface.get_rect().centerx + TILE_SIZE // 4, surface.get_rect().centery - TILE_SIZE // 4)
        _end = (surface.get_rect().centerx - TILE_SIZE // 4, surface.get_rect().centery + TILE_SIZE // 4)
        pg.draw.line(surface, (10, 10, 10), _start, _end, 8)


class Case(pg.sprite.Sprite):
    def __init__(self, pos: tuple):
        super().__init__()
        self._pos = pos

        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLOCK_COLOR)
        _pos = pg.math.Vector2(pos)
        self.rect = self.image.get_rect(topleft=_pos * TILE_SIZE)

        self._is_free = True
        self._symbol = None

    @property
    def is_free(self):
        return self._is_free

    @property
    def pos(self):
        return self._pos

    @property
    def symbol(self) -> Cross | Circle:
        return self._symbol

    @symbol.setter
    def symbol(self, s: Cross | Circle):
        if self._is_free:
            self._symbol = s
            self._is_free = False

    def update(self):
        if not self._is_free:
            if isinstance(self._symbol, Cross | Circle):
                self._symbol.draw(self.image)


class Player:
    def __init__(self, name: str, symbol: Cross | Circle):
        self.__name = name
        self.__symbol = symbol
        self.__score = 0

    @property
    def name(self) -> str:
        return self.__name

    @property
    def symbol(self) -> Cross | Circle:
        return self.__symbol

    @property
    def score(self) -> int:
        return self.__score

    @score.setter
    def score(self, value: int):
        self.__score = value


def display(value):
    font = pg.font.Font(None, 28)
    render_surface = font.render(str(value), True, (10, 10, 10))
    return render_surface


class Game:
    pg.init()
    window = pg.display.set_mode(WINDOWS_SIZE)
    clock = pg.time.Clock()

    player_symbol = {
        P1: Cross,
        P2: Circle
    }

    player_1 = Player(P1, Cross())
    player_2 = Player(P2, Circle())

    pg.display.set_caption("Tic Tac Toe")

    def __init__(self):
        self.run_game = True
        self.pause = False
        self.main_surface = pg.Surface((SQUARE_GRID_SIZE * TILE_SIZE, SQUARE_GRID_SIZE * TILE_SIZE))
        self.mouse_is_pressed = False
        self.case_group = pg.sprite.Group()
        self.grid_game = {(x, y): None for x in range(SQUARE_GRID_SIZE) for y in range(SQUARE_GRID_SIZE)}

        self.create_grid_game()

        self.actual_player = Game.player_1
        self.winner = None
        self.draw = False

    def retry(self):
        self.grid_game = {(x, y): None for x in range(SQUARE_GRID_SIZE) for y in range(SQUARE_GRID_SIZE)}
        self.case_group.empty()
        self.create_grid_game()
        self.winner = None
        self.draw = False
        self.run_game = True

    def draw_grid(self):
        for _var in range(1, SQUARE_GRID_SIZE):
            # horizontals lines
            pg.draw.line(self.main_surface, (10, 10, 10), (8, _var * TILE_SIZE),
                         (SQUARE_GRID_SIZE * TILE_SIZE - 8, _var * TILE_SIZE), 5)
            # verticals lines
            pg.draw.line(self.main_surface, (10, 10, 10), (_var * TILE_SIZE, 8),
                         (_var * TILE_SIZE, SQUARE_GRID_SIZE * TILE_SIZE - 8), 5)

    def create_grid_game(self):
        for x in range(SQUARE_GRID_SIZE):
            for y in range(SQUARE_GRID_SIZE):
                self.case_group.add(Case((x, y)))

    def mouse_input(self):
        mouse_pos = tuple(pg.math.Vector2(pg.mouse.get_pos()) // TILE_SIZE)
        mouse_left, mouse_wheel, mouse_right = pg.mouse.get_pressed(3)
        if mouse_left and not self.mouse_is_pressed:
            self.mouse_is_pressed = True
            self.check_case(mouse_pos)
            self.actual_player = Game.player_turn(self.actual_player)
            self.winner = Game.check_game_grid(self.grid_game)
        elif not mouse_left and self.mouse_is_pressed:
            self.mouse_is_pressed = False

    def check_case(self, pos):
        if self.mouse_is_pressed:
            for case in self.case_group.sprites():
                if case.rect.collidepoint(pg.mouse.get_pos()) and case.is_free:
                    case.symbol = self.actual_player.symbol
                    self.grid_game[pos] = self.actual_player

    def display_text(self):
        if not self.winner and self.draw:
            text = f"Draw! r = Retry"
        elif not self.winner:
            text = f"Player {self.actual_player.name} turn"
        else:
            text = f"Player {self.winner.name} win! r = Retry"
        text_surface = display(text)
        x_text = Game.window.get_width() - text_surface.get_width() - 8
        Game.window.blit(text_surface, (x_text, Game.window.get_height() - (LINE_SIZE - 6)))

    @staticmethod
    def check_quit_game():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

    @staticmethod
    def input() -> bool:
        keys = pg.key.get_pressed()
        return keys[pg.K_r]

    @staticmethod
    def check_game_grid(grid: dict) -> Player:
        h = Game.check_horizontal(grid)
        v = Game.check_vertical(grid)
        d = Game.check_diagonal(grid)
        if h:
            return h
        elif v:
            return v
        elif d:
            return d

    @staticmethod
    def check_horizontal(grid: dict) -> Player:
        for y in range(SQUARE_GRID_SIZE):
            _lst = []
            for x in range(SQUARE_GRID_SIZE):
                _lst.append(grid[(x, y)])

            winner = Game.check_winner(_lst)
            if winner:
                return winner

    @staticmethod
    def check_vertical(grid: dict) -> Player:
        for x in range(SQUARE_GRID_SIZE):
            _lst = []
            for y in range(SQUARE_GRID_SIZE):
                _lst.append(grid[(x, y)])

            winner = Game.check_winner(_lst)
            if winner:
                return winner

    @staticmethod
    def check_diagonal(grid: dict) -> Player:
        _lst = []
        # premiere diagonale
        for c in range(SQUARE_GRID_SIZE):
            _lst.append(grid[(c, c)])

        winner = Game.check_winner(_lst)
        if winner:
            return winner

        _lst = []
        # seconde diagonale
        x = SQUARE_GRID_SIZE
        for y in range(SQUARE_GRID_SIZE):
            x -= 1
            _lst.append(grid[(x, y)])

        winner = Game.check_winner(_lst)
        if winner:
            return winner

    @staticmethod
    def check_winner(lst: list) -> Player:
        if lst.count(Game.player_1) >= SQUARE_GRID_SIZE:
            return Game.player_1
        elif lst.count(Game.player_2) >= SQUARE_GRID_SIZE:
            return Game.player_2

    @staticmethod
    def grid_is_full(grid: dict) -> bool:
        return list(grid.values()).count(None) == 0

    @staticmethod
    def player_turn(player: Player) -> Player:
        if player.name == P1:
            return Game.player_2
        elif player.name == P2:
            return Game.player_1

    @staticmethod
    def display_scoring():
        text = f"{P1} : {Game.player_1.score} | {P2} : {Game.player_2.score}"
        Game.window.blit(display(text), (8, Game.window.get_height() - (LINE_SIZE - 6)))

    @staticmethod
    def scoring(player: Player):
        player.score = (player.score + 1) % 99

    def run_party(self):

        self.main_surface.fill(BLOCK_COLOR)

        self.case_group.update()
        self.case_group.draw(self.main_surface)

        self.draw_grid()

        self.mouse_input()

        self.draw = Game.grid_is_full(self.grid_game) and not self.winner

    def restart(self):
        if Game.input():
            self.retry()

    def run(self):
        while True:
            Game.check_quit_game()
            Game.clock.tick(FPS)

            Game.window.fill("Dark Grey")

            if self.run_game:
                if self.winner:
                    self.run_game = False
                    Game.scoring(self.winner)
                elif self.draw:
                    self.run_game = False
                self.run_party()
            else:
                # en attente de recommencer
                self.restart()

            Game.window.blit(self.main_surface, (0, 0))

            self.display_text()
            Game.display_scoring()
            pg.display.flip()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    game = Game()
    game.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
