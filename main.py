import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

# Инициализация Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)  # Настройка звука (частота, битность, каналы, буфер)
mixer.init()  # Инициализация звука Pygame
pygame.init()  # Инициализация Pygame


# загрузка музыки и звуков
pygame.mixer.music.load('img/music.wav') # фоновая музыка
pygame.mixer.music.play(-1, 0.0, 5000) # бесконечное проигрывание

coin_fx = pygame.mixer.Sound('img/coin.wav')# звук подбора монеты
coin_fx.set_volume(0.5) #установка громкости

jump_fx = pygame.mixer.Sound('img/jump.wav')# звук прыжка
jump_fx.set_volume(0.5)#установка громкости
game_over_fx = pygame.mixer.Sound('img/game_over.wav')# звук проигрыша
game_over_fx.set_volume(0.5)#установка громкости

# Настройка экрана
clock = pygame.time.Clock()  # Создание объекта Clock для управления FPS
fps = 60  # Частота кадров в секунду

screen_width = 800  # Ширина экрана
screen_height = 800  # Высота экрана

screen = pygame.display.set_mode((screen_width, screen_height))  # Создание экрана
pygame.display.set_caption('Platformer')  # Установка заголовка окна

# ------------ Определение переменных для шрифтов ------------------#
font = pygame.font.SysFont('Bauhaus 93', 70)  # Шрифт для заголовков
font_score = pygame.font.SysFont('Bauhaus 93', 30)  # Шрифт для счета

# Переменные игры
tile_size = 40  # Размер тайла
main_menu = True  # Флаг, показывающий, что открыто главное меню
level = 0  #!!!  Уровень игры (заглушка)
max_levels = 4 #!!! максимальное кол-во уровней
score = 0 # добавили счет
game_over = 0# добавили игра

# Определение цветов
white = (255, 255, 255)  # Белый цвет
blue = (0, 0, 255)  # Синий цвет

# Загрузка изображений
sun_img = pygame.image.load('img/sun.png')  # Изображение солнца
bg_img = pygame.image.load('img/sky.png')  # Изображение фона
start_img = pygame.image.load('img/start_btn.png')  # Изображение кнопки старта
restart_img = pygame.image.load('img/restart_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')  # Изображение кнопки выхода






class World:
    """
    Класс для представления игрового мира.
    """

    def __init__(self, data):
        """
        Инициализация мира на основе данных.

        Параметры:
        data (list): Двумерный список, представляющий уровень игры.
        """
        self.tile_list = []  # Список тайлов в мире

        # Загрузка изображений тайлов
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        # Обход данных уровня и создание тайлов
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    # Создание тайла земли
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    # Создание тайла травы
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #извлечение противника
                if tile == 3:
                    blob = Enemy(col_count * tile_size,
                                 row_count * tile_size + 15)
                    blob_group.add(blob)
                #извечение тайла монеты
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2),
                                row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)

                # !!! -------- извечение тайла Перехода на следущей уровень (Выход на уровень) -----------!!!#
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count *
                                tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        """
        Отрисовка всех тайлов мира на экране.
        """
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Player:
    """
    Класс для представления игрока.
    """

    def __init__(self, x, y):
        """
        Инициализация игрока с заданными координатами.

        Параметры:
        x (int): Начальная координата X игрока.
        y (int): Начальная координата Y игрока.
        """
        self.reset(x, y)  # Сброс параметров игрока

    def update(self, world, game_over):
        """
        Обновление состояния игрока на основе ввода и проверка столкновений с тайлами.

        Параметры:
        world (World): Объект мира для проверки столкновений с тайлами.
        """
        dx = 0
        dy = 0
        walk_cooldown = 5  # Задержка между кадрами анимации


        if game_over == 0:# -----------------Если НЕ конец игры-----------------------#
            # Получение нажатых клавиш
            key = pygame.key.get_pressed()

            # Обработка нажатий клавиш для движения игрока
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Обработка прыжка
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play() # воспроизводим звук прыжка
                self.vel_y = -20
                self.jumped = True

            if not key[pygame.K_SPACE]:
                self.jumped = False

            # ------------------ переключение анимации --------------------- #
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Применение гравитации
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Проверка столкновений с тайлами
            self.in_air = True #чтобы не прыгал бесокечно
            for tile in world.tile_list:
                # Проверка столкновений по X
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Проверка столкновений по Y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Обновление координат игрока
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0
                self.in_air = False

            # !!! ------------ Если игрок столкнулся с выходом на следующий уровень --------------#
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # ----------------------------------------#
            # проверка на столкновение с противником
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()


        elif game_over == -1:# ----------------------если конец игры------------------#
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue,
                      (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5


        # Отрисовка игрока на экране
        screen.blit(self.image, self.rect)
        return game_over # !!! Возвращаем состояние игры


    def reset(self, x, y):
        """
        Сброс состояния игрока к начальным параметрам.

        Параметры:
        x (int): Начальная координата X игрока.
        y (int): Начальная координата Y игрока.
        """
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0

        #--------Добавлена загрузка кадров для анимации-------------#
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        # Загрузка изображений для анимации движения игрока
        img_right = pygame.image.load(f'img/guy1.png')
        img_right = pygame.transform.scale(img_right, (40, 80))
        img_left = pygame.transform.flip(img_right, True, False)
        self.images_right.append(img_right)
        self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()

        # Установка начальных координат и параметров игрока
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True



#------------Добавили класс противника-----------------#
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        #--------делаем патриулируйщего противника--------#
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(
            img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#Отрисовка текста
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
def get_data_from_file(file):
    """
    Функция для чтения уровня игры из файла и преобразования его в двумерный список.

    Параметры:
    file (file object): Объект файла с данными уровня.

    Возвращает:
    list: Двумерный список с данными уровня.
    """
    world_data = []
    for l in file:
        temp = []
        s_temp = l.strip().split(',')
        temp = [int(s) for s in s_temp]
        world_data.append(temp)
    return world_data


# ---------------перезапуск уровня--------------------#
def reset_level(level):
    player.reset(100, screen_height - 130)  # сбрасываем игрока в начальную позицию
    blob_group.empty()  # очищаем группу врагов (blob)
    coin_group.empty()  # очищаем группу монет
    exit_group.empty()  # очищаем группу выходов


    # загружаем данные уровня и создаем мир
    if path.exists(f'levels/level{level}.txt'): # цифру меняем на {level}
        pickle_in = open(f'levels/level{level}.txt', 'r')# цифру меняем на {level}
        # world_data = pickle.load(pickle_in)
        world_data = get_data_from_file(pickle_in)  # получаем данные мира из файла

    world = World(world_data)  # создаем мир на основе загруженных данных
    # создаем фиктивную монету для отображения счета
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world  # возвращаем объект мира
# -----------------------------------#




class Button:
    """
    Класс для представления кнопки в игре.

    Attributes:
    ----------
    image : pygame.Surface
        Изображение кнопки.
    rect : pygame.Rect
        Прямоугольник, ограничивающий кнопку.
    clicked : bool
        Флаг, указывающий, была ли нажата кнопка.
    """

    def __init__(self, x, y, image):
        """
        Инициализация кнопки.

        Parameters:
        -----------
        x : int
            Координата X кнопки на экране.
        y : int
            Координата Y кнопки на экране.
        image : pygame.Surface
            Изображение кнопки.
        """
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        """
        Отображение кнопки на экране и обработка нажатия.

        Returns:
        --------
        bool
            True, если кнопка была нажата, иначе False.
        """
        action = False

        # Получение текущей позиции курсора мыши
        pos = pygame.mouse.get_pos()

        # Проверка на наведение и нажатие кнопки
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Отрисовка кнопки на экране
        screen.blit(self.image, self.rect)

        return action


class Coin(pygame.sprite.Sprite):
    """
    Класс, представляющий монету в игре.
    Наследует методы и атрибуты от pygame.sprite.Sprite.
    """

    def __init__(self, x, y):
        """
        Инициализирует объект монеты с заданными координатами.

        Аргументы:
        x (int): Координата x центра монеты.
        y (int): Координата y центра монеты.
        """
        pygame.sprite.Sprite.__init__(self)  # Инициализация родительского класса
        img = pygame.image.load('img/coin.png')  # Загрузка изображения монеты
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))  # Масштабирование изображения
        self.rect = self.image.get_rect()  # Получение прямоугольника изображения
        self.rect.center = (x, y)  # Установка координат центра прямоугольника




# Создание объекта игрока с начальными координатами
player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group() # добавили группу для противников
coin_group = pygame.sprite.Group() # создание группы для монеты (что-то вроде списка)
exit_group = pygame.sprite.Group() # !!! добавили группу для переходов (выходов) на следующий уровень

# создать фиктивную монету для показа счета
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Загрузка данных уровня и создание мира
if path.exists(f'levels/level{level}.txt'):  #!!! цифру меняем на {level} # Проверяем наличие файла с данными уровня
    pickle_in = open(f'levels/level{level}.txt', 'r') # !!!!цифру меняем на {level} # Открываем файл для чтения
    world_data = get_data_from_file(pickle_in)  # Получаем данные уровня из файла
    pickle_in.close()  # Закрываем файл

world = World(world_data)  # Создаем объект мира на основе полученных данных





# Создание кнопок для интерфейса
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)  # Кнопка "Старт"
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)  # Кнопка "Выход"
restart_button = Button(screen_width // 2 - 50,
                        screen_height // 2 + 100, restart_img)# --------кнопка перезапуска-----------------------#



# Основной цикл игры
run = True
while run:
    clock.tick(fps)  # Ограничение FPS

    screen.blit(bg_img, (0, 0))  # Отображение фона

    if main_menu:  # Если находимся в главном меню
        if exit_button.draw():  # Отрисовка кнопки выхода и проверка нажатия
            run = False  # Завершение игрового цикла при нажатии кнопки выхода
        if start_button.draw():  # Отрисовка кнопки старта и проверка нажатия
            main_menu = False  # Переход из главного меню в игровой режим
    else:  # Если находимся в игровом режиме
        world.draw()  # Отрисовка игрового мира
        # не конец игры?
        if game_over == 0:
            blob_group.update()

            # проверка на соприкосновение с монетой
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)# рендеринг противников
        coin_group.draw(screen) # отрисовка группы монет
        exit_group.draw(screen)  #!!!----- Отрисовка группы выходов -----


        game_over = player.update(world, game_over)# обновления игрока


        # если игрок погиб
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # !!! --------------- Если игрок завершил уровень ---------------------!!! #
        if game_over == 1:

            level += 1
            if level <= max_levels:
                #!!! Сброс уровня (даже если игрок только на него попал)
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', font, blue,
                          (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    # !!! Сброс уровня
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():  # Обработка событий Pygame
        if event.type == pygame.QUIT:  # Обработка события выхода из игры
            run = False  # Завершение игрового цикла
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                main_menu = True  # Возврат в главное меню

    pygame.display.update()  # Обновление экрана

pygame.quit()  # Завершение работы Pygame
