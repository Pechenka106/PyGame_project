import pygame
import sys
import os


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    # try:
    image = image.convert_alpha()
    # except Exception as error:
    #     print(error)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Cell:  # общий класс клетки
    def __init__(self, x, y, screen, size):
        self.name = self.__class__.__name__
        self.x, self.y = x, y
        self.size = size
        self.screen = screen

    def __str__(self):  # удобное преобразование в строку
        return self.name

    def draw(self):
        pygame.draw.rect(self.screen, 'white', (self.x, self.y, self.size, self.size), 1)

    def set_size(self, size):  # установить новые размеры клетки
        self.size = size


class Road_cell(Cell):  # клетка дороги для мобов
    def __init__(self, x, y, screen, size):
        super().__init__(x, y, screen, size)

    def draw(self):
        pygame.draw.rect(self.screen, 'blue', (self.x, self.y, self.size, self.size), 5)


class Pass_cell(Cell):  # пустая клетка (декоративная)
    def __init__(self, x, y, screen, size):
        super().__init__(x, y, screen, size)


class Building_cell(Cell):  # клетка для стороительства башен
    def __init__(self, x, y, screen, size, tower=None):
        super().__init__(x, y, screen, size)
        self.tower = tower

    def set_tower(self, tower):  # установить башня в клетку
        self.tower = tower

    def draw(self): # отрисовка клетки и башни
        pygame.draw.rect(self.screen, 'green', (self.x, self.y, self.size, self.size), 5)


class Enemy(pygame.sprite.Sprite):  # класс враждебного моба
    def __init__(self, x, y, screen, width, height, health, image, damage=10, price=10, speed=1):
        super().__init__(entities, enemies)
        self.name = self.__class__.__name__
        self.pos = x, y
        self.screen = screen
        self.size = self.width, self.height = width, height
        self.health = health
        self.damage = damage
        self.speed = speed
        self.image = image
        self.price = price
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos[0], self.pos[1]
        self.path = None
        self.current_step = None
        self.step = None
        self.steps = None
        self.is_move = True
        self.set_path(enemy_path)


    def load_step(self, index):  # загрузка следующего направления движения из пути
        self.step = self.path[index]
        if self.step[0] < 0 or self.step[1] < 0:
            self.speed = abs(self.speed) * -1
        else:
            self.speed = abs(self.speed)

    def move(self):  # передвижение врага по пути из файла
        if self.is_move:
            if self.rect.x + self.rect.width + self.speed >= width:
                self.is_move = False
                self.explosion()
            elif self.rect.y + self.rect.height + self.speed >= height:
                self.is_move = False
                self.explosion()
            else:
                if self.step[0] == 0:
                    if abs(self.step[1]) <= self.steps and self.current_step == len(self.path) - 1:
                        self.is_move = False
                        self.explosion()
                    elif abs(self.step[1]) <= self.steps:
                        self.steps = 0
                        self.current_step += 1
                        self.load_step(self.current_step)
                    else:
                        self.pos = self.pos[0], self.pos[1] + self.speed
                        self.steps += abs(self.speed)
                        self.rect.x, self.rect.y = self.pos[0], self.pos[1]
                else:
                    if abs(self.step[0]) <= self.steps and self.current_step == len(self.path) - 1:
                        self.is_move = False
                        self.explosion()
                    elif abs(self.step[0]) <= self.steps:
                        self.steps = 0
                        self.current_step += 1
                        self.load_step(self.current_step)
                    else:
                        self.pos = self.pos[0] + self.speed, self.pos[1]
                        self.steps += abs(self.speed)
                        self.rect.x, self.rect.y = self.pos[0], self.pos[1]

    def explosion(self):  # суицидальный взрыв при подходу к замку наносящий урон
        global castle_health
        castle_health -= self.damage
        print(castle_health)
        self.health = 0
        self.kill()

    def check(self, cell1, cell2):  # проверка(враг не может выйти за пределы дороги)
        if self.speed > 0 and cell1.name == 'Road_cell':
            self.move()
        if self.speed < 0 and cell2.name == 'Road_cell':
            self.move()

    def set_path(self, path):  # задать путь
        self.path = path
        self.current_step = 0
        self.steps = 0
        self.load_step(0)

    def get_damage(self, damage):  # получение урона от башни
        if self.health - damage <= 0:
            self.health = 0
            self.is_move = False
            global gold
            gold += self.price
            self.kill()
        else:
            self.health -= damage
            # self.image.fill('blue')


class Tower(pygame.sprite.Sprite):  # класс башни
    def __init__(self, x, y, screen, size, health, image, damage=50, radius=200, reload=1000, price=500, level=1,
                 is_splash=False, splash_radius=75):
        super().__init__(towers, entities)
        self.name = self.__class__.__name__
        self.pos = x, y
        self.screen = screen
        self.health = health
        self.size = size
        self.price = price
        self.damage = damage
        self.radius = radius
        self.reload = reload
        self.level = level
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos[0], self.pos[1]
        self.radius = radius
        self.focus = None
        self.is_splash = is_splash
        self.splash_radius = splash_radius

    def fire(self):  # выстрел по захваченой цели
        if self.focus != None and self.focus.health != 0 and pygame.sprite.collide_circle(self.focus, self):
            if self.is_splash:
                self.focus.radius = self.splash_radius
                for enemy in enemies:
                    if pygame.sprite.collide_circle(enemy, self.focus):
                        enemy.get_damage(self.damage)
            else:
                self.focus.get_damage(self.damage)
        else:
            self.focus_enemy()

    def focus_enemy(self):  # захват цели (при убийстве прошлой)
        for enemy in enemies:
            if pygame.sprite.collide_circle(enemy, self):
                self.focus = enemy
                self.fire()
                break


class Board:  # класс поля
    def __init__(self, screen, height=10, width=10, cell_size=80):
        self.screen = screen
        self.hieght = height
        self.width = width
        self.cell_size = cell_size
        self.board = [[Pass_cell(self.cell_size * i, self.cell_size * h, self.screen, self.cell_size)
                       for h in range(width)] for i in range(height)]
        self.spis = ['white', 'red', 'blue']
        self.n = 11

    def set_cell_size(self, cell_size):  # установить новый размер клетки
        self.cell_size = cell_size
        for h in range(self.hieght):
            for i in range(self.width):
                self.board[h][i].set_size(self.cell_size)

    def render(self):  # отрисовка поля, клеток и башен на нём
        for i in range(self.hieght):
            for g in range(self.width):
                self.board[i][g].draw()

    def set_cell(self, x, y, cell):  # заменить одну клетку на другую
        self.board[y][x] = cell

    def get_cell(self, pos):  # проверка на какую клетку нажали
        cell_x = pos[0] // self.cell_size
        cell_y = pos[1] // self.cell_size
        if cell_y < 0 or cell_y >= self.width or cell_x < 0 or cell_x >= self.hieght:
            print('error')
            return Pass_cell(0, 0, None, 80)
        return self.board[cell_x][cell_y], (cell_x, cell_y)

    def get_click(self, mouse_pos, tower_price=500):  # проверка на какую клетку нажали и установка башни
        # (пока только одного типа)
        cell, pos = self.get_cell(mouse_pos)
        if cell and cell.name == 'Building_cell':
            global gold
            if cell.tower == None:
                if gold >= tower_price:
                    cell.set_tower(Tower(pos[0] * self.cell_size + 10, pos[1] * self.cell_size + 10, self.screen,
                                         60, 100, load_image('car.jpg'), 50, 200, 1000, tower_price, True, 200))
                    gold -= tower_price
                    towers_reload[cell.tower] = pygame.USEREVENT + self.n
                    pygame.time.set_timer(towers_reload[cell.tower], cell.tower.reload)
                    self.n += 1
                else:
                    print(f'вам не хватает {tower_price - gold} золота')
            else:
                pygame.time.set_timer(towers_reload[cell.tower], 0)
                del towers_reload[cell.tower]
                gold += cell.tower.price // 2
                cell.tower.kill()
                cell.set_tower(None)
            return cell
        elif cell != None:
            return cell


def load_level(file_level, file_settings):  # загрузка уровня и настроек игры из файлов
    with open(file_level, 'r')as Map:
        level_map = [line for line in Map]
    return level_map


def generate_level(level_map, cell_size, screen):  # генерация карты
    list_entities = []
    for y in range(len(level_map)):
        lst = []
        for x in range(len(level_map[y])):
            if level_map[y][x] == '.':
                lst.append(Pass_cell(x * cell_size, y * cell_size, screen, cell_size))
            elif level_map[y][x] == '0':
                lst.append(Building_cell(x * cell_size, y * cell_size, screen, cell_size))
            elif level_map[y][x] == '#':
                lst.append(Road_cell(x * cell_size, y * cell_size, screen, cell_size))
            elif level_map[y][x] == '@':
                lst.append(Road_cell(x * cell_size, y * cell_size, screen, cell_size))
                spawn_pos = (x, y)
        list_entities.append(lst)
    return list_entities, spawn_pos


def load_path(name):  # загрузка пути врага
    if os.path.isfile(name):
        file = open(name).readlines()
        path = []
        try:
            for string in file:
                path.append([int(i) for i in string.split(' ')])
            return path
        except Exception:
            print('Неверный формат файла:', name)


def find_key(dictionary, needle):  # найти башню которая перезарядилась
    for key in dictionary.keys():
        if dictionary[key] == needle:
            return key


def terminate():  # закрытие программы
    pygame.quit()
    sys.exit()


# константы используемые объектами или функциями
castle_health = 100
gold = 1000
entities = pygame.sprite.Group()
enemies = pygame.sprite.Group()
towers = pygame.sprite.Group()
towers_reload = {}
enemy_path = load_path('data/enemy_path.txt')
size = width, height = 1280, 720


def main():
    # создание окна
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('First board')

    # создания поля
    my_board = Board(screen, 16, 9)
    my_board.set_cell_size(80)

    # загрузка карты
    lvl = load_level('data/map.map', 'data/settings.txt')
    level, start_pos = generate_level(lvl, 80, screen)
    for x in range(len(level)):
        for y in range(len(level[x])):
            my_board.set_cell(x, y, level[x][y])

    # стандартные таймеры событий
    spawn_enemy = pygame.USEREVENT + 1
    my_event = pygame.USEREVENT + 2
    pygame.time.set_timer(my_event, 10)
    pygame.time.set_timer(spawn_enemy, 1000)

    enemy_image = load_image('image.jpg')
    vrag = (start_pos[0] * 80 + 20, start_pos[1] * 80 + 20, screen, 40, 40, 200, enemy_image)
    vrag_haste = (start_pos[0] * 80 + 20, start_pos[1] * 80 + 20, screen, 40, 40, 100, enemy_image, 10, 10, 2)

    running = True
    while running:
            screen.fill((0, 0, 0))
            if castle_health <= 0:
                terminate()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # выход из игры
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # проверка на какую вклетку нажали,
                    # если строительная то ставиться башня
                    print(my_board.get_click(event.pos, 500))
                if event.type == my_event:  # проверка выходит ли враг за дорогу
                    for enemy in enemies:
                        cell1 = my_board.get_click((enemy.pos[0] + enemy.size[0], enemy.pos[1] + enemy.size[1]))
                        cell2 = my_board.get_click((enemy.pos[0] + enemy.speed, enemy.pos[1] + enemy.speed))
                        enemy.check(cell1, cell2)
                if event.type == spawn_enemy:  # создание врага раз в заданое кол-во секунд (сейчас 2) секунды
                    Enemy(*vrag[:])
                    Enemy(*vrag_haste[:])
                if event.type in towers_reload.values():  # выстрел башни по окондании перезрядки
                    find_key(towers_reload, event.type).fire()
            # отрисовка
            my_board.render()
            entities.update()
            entities.draw(screen)
            pygame.display.flip()
    terminate()


if __name__ == '__main__':
    main()
