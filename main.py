from random import randint

# Классы исключений
class GameException(Exception):
    pass
# BoardOutException: ошибка, происходящая, когда игрок попытается отметить точку за пределами игрового поля
class BoardOutException(GameException):
    def __str__(self):
        return 'Ошибка: отметка точки за пределами поля'
# DotUsedException: ошибка при повторном использовании точки, в которую уже стреляли
class DotUsedException(GameException):
    def __str__(self):
        return 'Ошибка: повторная отметка уже использованной точки'
# WrongShipException: ошибка при неверном размещении корабля
class WrongShipException(GameException):
    pass


# Класс для игровой доски
class Board:
    def __init__(self, size = 6, hid = False):
        self.size = size
        self.hid = hid

        self.counter = 0
        self.field = [["O"] * size for _ in range(size)]
        self.taken = []
        self.ships = []
    def __str__(self):
        res_board = ""
        res_board += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res_board += f'\n{i + 1} | ' + " | ".join(row) + " |"

        if self.hid:
            res_board = res_board.replace('■', 'O')

        return res_board

    def out_of_board(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out_of_board(d) or d in self.taken:
                raise WrongShipException
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.taken.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near_dots = [(-1,-1), (-1, 0), (-1,1),
                     (0,-1), (0, 0), (0,1),
                     (1,-1), (1, 0), (1,1)]
        for d in ship.dots:
            for dotx, doty in near_dots:
                cur = Dot(d.x + dotx, d.y + doty)
                if not(self.out_of_board(cur)) and cur not in self.taken:
                    if verb and self.field[cur.x][cur.y] != 'X':
                        self.field[cur.x][cur.y] = '.'
                    self.taken.append(cur)

    def shot(self, d):
        if self.out_of_board(d):
            raise BoardOutException

        if d in self.taken:
            raise DotUsedException

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.counter += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print("Вы попали в корабль!")
                    return True
        self.field[d.x][d.y] = '.'
        print('Мимо!')
        self.field[d.x][d.y] = 'T'
        return False

    def begin(self):
        self.taken = []





# Класс для кораблей
class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction == 0:
                cur_x += i
            elif self.direction == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

# Класс точек на игровом поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    # Проверка точек на равенство
    def __eq__(self, other):
         return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f'Точка {self.x}, {self.y}'


# Класс игрока
class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except GameException as e:
                print(e)


# Класс пользователя
class User(Player):
    def ask(self):
        while True:
            coords = input('Ваш ход: ').split()
            if len(coords) != 2:
                print('Введите 2 координаты!')

                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Некорректный ввод. Введите числа!')
                continue

            x,y = int(x), int(y)

            return Dot(x-1, y-1)


# Класс компьютера
class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0,5))
        print(f'Ход компьютера: {d.x+1} {d.y+1}')
        return d

# класс игры
class Game:
    def __init__(self, size=6):
        self.size = size
        user_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hid = True

        self.ai = AI(ai_board, user_board)
        self.user = User(user_board, ai_board)

    def generate_board(self):
        lenghts = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0

        for i in lenghts:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(i, Dot(randint(0, self.size),(randint(0, self.size))), randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipException:
                    pass
                
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.generate_board()
        return board

    def greet(self):
        print('-' * 20)
        print('Приветствуем вас в игре \'Морской бой\'!')
        print('Формат ввода: x, y')
        print('x - номер строки, y - номер столбца.')
        print('-' * 20)

    def loop(self):
        number = 0
        while True:
            print('-'*20)
            print('Доска пользователя:')
            print(self.user.player_board)
            print('-' * 20)
            print('Доска компьютера:')
            print(self.ai.player_board)
            if number % 2 == 0:
                print('Ходит пользователь!')
                move = self.user.move()
            else:
                print('Ходит компьютер!')
                move = self.ai.move()
            if move:
                number -= 1

            if self.ai.player_board.counter == 7:
                print('-' * 20)
                print('Пользователь выиграл!')
                break
            if self.user.player_board.counter == 7:
                print('-' * 20)
                print('Компьютер выиграл!')
                break
            number += 1


    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()