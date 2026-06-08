import copy
import math

import pygame

import config
from board import boards, rotacionar_board_180
from ghost import Ghost, calculate_ghost_speeds, get_targets
from pacman import Pacman
from leaderboard import add_score, load_leaderboard
from start_screen import draw_leaderboard_screen, draw_start_screen

def load_sounds():
    sounds = {}

    for name,path in config.SOUND_PATHS.items():
        try:
            sounds[name] = pygame.mixer.Sound(path)
            print(f'Som carregado: {name} -> {path}')
        except (FileNotFoundError,pygame.error) as error:
            sounds[name] = None
            print(f'Erro ao carregar o som: {name} -> {path}')
            print(error)

    return sounds


def play_sound(sounds,name):
    sound = sounds.get(name)

    if sound:
        sound.play()

def load_scaled_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size)


def load_font(path, size, fallback_path=None):
    """Carrega uma fonte personalizada e usa uma alternativa quando necessário."""
    for candidate in (path, fallback_path):
        if candidate:
            try:
                return pygame.font.Font(candidate, size)
            except (FileNotFoundError, OSError):
                pass

    return pygame.font.Font(None, size)


def load_player_images():
    return [
        load_scaled_image(path, config.PLAYER_SPRITE_SIZE)
        for path in config.PLAYER_IMAGE_PATHS
    ]


def load_ghost_images():
    ghost_images = {}

    for name, paths in config.GHOST_IMAGE_PATHS.items():
        if name in ('spooked', 'dead'):
            ghost_images[name] = [
                load_scaled_image(path, config.GHOST_SPRITE_SIZE)
                for path in paths
            ]
        else:
            ghost_images[name] = {
                direction: [
                    load_scaled_image(path, config.GHOST_SPRITE_SIZE)
                    for path in direction_paths
                ]
                for direction, direction_paths in paths.items()
            }

    return ghost_images


def create_initial_ghost_state():
    return {
        name: {
            'x': values['x'],
            'y': values['y'],
            'direction': values['direction'],
            'dead': False,
        }
        for name, values in config.GHOST_STARTS.items()
    }


def draw_misc(
    screen,
    font,
    score_font,
    score,
    high_score,
    powerup,
    lives,
    game_over,
    game_won,
    ready,
    player_images
):
    center_x = screen.get_width() // 2

    def draw_text(text, selected_font, color, x, y, center=False):
        # False mantém o aspecto pixelado da fonte.
        text_surface = selected_font.render(str(text), False, color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        screen.blit(text_surface, text_rect)

    def format_score(value):
        # Mostra pelo menos dois dígitos.
        return f'{value:02d}'

    # Interface superior inspirada no arcade original.
    title_y = 18
    value_y = 48

    draw_text(
        '1UP',
        score_font,
        config.WHITE,
        center_x - 280,
        title_y,
        center=True
    )

    draw_text(
        'HIGH SCORE',
        score_font,
        config.WHITE,
        center_x,
        title_y,
        center=True
    )

    draw_text(
        '2UP',
        score_font,
        config.WHITE,
        center_x + 280,
        title_y,
        center=True
    )

    draw_text(
        format_score(score),
        score_font,
        config.WHITE,
        center_x - 280,
        value_y,
        center=True
    )

    draw_text(
        format_score(high_score),
        score_font,
        config.WHITE,
        center_x,
        value_y,
        center=True
    )

    draw_text(
        '00',
        score_font,
        config.WHITE,
        center_x + 280,
        value_y,
        center=True
    )

    if powerup:
        pygame.draw.circle(
            screen,
            'blue',
            (center_x + 350, value_y),
            7
        )

    # Interface inferior.
    footer_top = config.TOP_UI_HEIGHT + config.BOARD_HEIGHT

    life_width = config.LIFE_SPRITE_SIZE[0]
    life_height = config.LIFE_SPRITE_SIZE[1]

    life_sprite_y = (
        footer_top
        + (config.BOTTOM_UI_HEIGHT - life_height) // 2
    )

    life_sprite = pygame.transform.scale(
        player_images[0],
        config.LIFE_SPRITE_SIZE
    )

    for index in range(lives):
        screen.blit(
            life_sprite,
            (
                20 + index * (life_width + 10),
                life_sprite_y
            )
        )

    # Mensagens sobrepostas ao centro do tabuleiro.
    message_width = 680
    message_height = 130

    message_x = (screen.get_width() - message_width) // 2
    message_y = (
        config.TOP_UI_HEIGHT
        + (config.BOARD_HEIGHT - message_height) // 2
    )

    if game_over:
        pygame.draw.rect(
            screen,
            'white',
            [message_x, message_y, message_width, message_height],
            0,
            10
        )

        pygame.draw.rect(
            screen,
            'dark gray',
            [
                message_x + 10,
                message_y + 10,
                message_width - 20,
                message_height - 20
            ],
            0,
            10
        )

        draw_text(
            'GAME OVER',
            font,
            'red',
            center_x,
            message_y + 45,
            center=True
        )

        draw_text(
            'PRESS SPACE FOR MENU',
            font,
            config.WHITE,
            center_x,
            message_y + 88,
            center=True
        )

    if game_won:
        pygame.draw.rect(
            screen,
            'white',
            [message_x, message_y, message_width, message_height],
            0,
            10
        )

        pygame.draw.rect(
            screen,
            'dark gray',
            [
                message_x + 10,
                message_y + 10,
                message_width - 20,
                message_height - 20
            ],
            0,
            10
        )

        draw_text(
            'VICTORY',
            font,
            'green',
            center_x,
            message_y + 45,
            center=True
        )

        draw_text(
            'PRESS SPACE FOR MENU',
            font,
            config.WHITE,
            center_x,
            message_y + 88,
            center=True
        )

    if ready:
        draw_text(
            'READY!',
            score_font,
            'yellow',
            center_x,
            config.TOP_UI_HEIGHT + config.BOARD_HEIGHT // 2 + 60,
            center=True
        )


def draw_board(screen, level, flicker):
    num1 = config.CELL_HEIGHT
    num2 = config.CELL_WIDTH
    pi = math.pi

    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, config.BOARD_COLOR, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, config.BOARD_COLOR, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, config.BOARD_COLOR,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, pi / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, config.BOARD_COLOR,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                                pi / 2, pi, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, config.BOARD_COLOR,
                                [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                                pi, 3 * pi / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, config.BOARD_COLOR,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                                3 * pi / 2, 2 * pi, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)


def create_ghosts(screen, level, targets, speeds, ghost_images, ghost_state, powerup, eaten_ghost, counter, visible=True):
    common_arguments = {
        'screen': screen,
        'level': level,
        'powerup': powerup,
        'eaten_ghost': eaten_ghost,
        'spooked_images': ghost_images['spooked'],
        'dead_images': ghost_images['dead'],
        'counter': counter,
        'visible': visible,
    }

    blinky = Ghost(
        ghost_state['blinky']['x'], ghost_state['blinky']['y'], targets[0], speeds[0], ghost_images['blinky'],
        ghost_state['blinky']['direction'], ghost_state['blinky']['dead'], False, 0, **common_arguments
    )

    inky = Ghost(
        ghost_state['inky']['x'], ghost_state['inky']['y'], targets[1], speeds[1], ghost_images['inky'],
        ghost_state['inky']['direction'], ghost_state['inky']['dead'], False, 1, **common_arguments
    )
    pinky = Ghost(
        ghost_state['pinky']['x'], ghost_state['pinky']['y'], targets[2], speeds[2], ghost_images['pinky'],
        ghost_state['pinky']['direction'], ghost_state['pinky']['dead'], False, 2, **common_arguments
    )

    clyde = Ghost(
        ghost_state['clyde']['x'], ghost_state['clyde']['y'], targets[3], speeds[3], ghost_images['clyde'],
        ghost_state['clyde']['direction'], ghost_state['clyde']['dead'], False, 3, **common_arguments
    )

    return [blinky, inky, pinky, clyde]


def move_ghosts(ghosts, ghost_state):
    blinky, inky, pinky, clyde = ghosts

    if not blinky.dead and not blinky.in_box:
        blinky_values = blinky.move_blinky()
    else:
        blinky_values = blinky.move_clyde()

    if not pinky.dead and not pinky.in_box:
        pinky_values = pinky.move_pinky()
    else:
        pinky_values = pinky.move_clyde()

    if not inky.dead and not inky.in_box:
        inky_values = inky.move_inky()
    else:
        inky_values = inky.move_clyde()

    clyde_values = clyde.move_clyde()

    for name, values in (
        ('blinky', blinky_values),
        ('inky', inky_values),
        ('pinky', pinky_values),
        ('clyde', clyde_values),
    ):
        ghost_state[name]['x'], ghost_state[name]['y'], ghost_state[name]['direction'] = values


def player_hit_by_ghost(player_circle, ghosts, powerup, eaten_ghost):
    if not powerup:
        return any(player_circle.colliderect(ghost.rect) and not ghost.dead for ghost in ghosts)

    return any(
        player_circle.colliderect(ghost.rect) and eaten_ghost[index] and not ghost.dead
        for index, ghost in enumerate(ghosts)
    )


def eat_available_ghosts(player_circle, ghosts, ghost_state, eaten_ghost, score):
    ghost_names = ['blinky', 'inky', 'pinky', 'clyde']

    for index, ghost in enumerate(ghosts):
        if player_circle.colliderect(ghost.rect) and not ghost.dead and not eaten_ghost[index]:
            ghost_state[ghost_names[index]]['dead'] = True
            eaten_ghost[index] = True
            score += (2 ** eaten_ghost.count(True)) * 100

    return score


def reset_round(player):
    player.reset_position()
    return create_initial_ghost_state()


def has_player_won(level):
    for row in level:
        if 1 in row or 2 in row:
            return False
    return True



def calculate_initial_display_size():
    """Calcula uma janela visível que caiba no monitor sem alterar a lógica do jogo."""
    display_info = pygame.display.Info()
    max_width = int(display_info.current_w * config.DISPLAY_MAX_USAGE)
    max_height = int(display_info.current_h * config.DISPLAY_MAX_USAGE)

    scale = min(
        max_width / config.WINDOW_WIDTH,
        max_height / config.WINDOW_HEIGHT,
        1.0,
    )

    return (
        max(1, int(config.WINDOW_WIDTH * scale)),
        max(1, int(config.WINDOW_HEIGHT * scale)),
    )


def present_frame(screen, game_surface):
    """Redimensiona o quadro inteiro preservando sua proporção e o estilo pixelado."""
    screen_width, screen_height = screen.get_size()
    logical_width, logical_height = game_surface.get_size()

    scale = min(
        screen_width / logical_width,
        screen_height / logical_height,
    )

    scaled_size = (
        max(1, int(logical_width * scale)),
        max(1, int(logical_height * scale)),
    )

    scaled_frame = pygame.transform.scale(game_surface, scaled_size)
    frame_x = (screen_width - scaled_size[0]) // 2
    frame_y = (screen_height - scaled_size[1]) // 2

    screen.fill('black')
    screen.blit(scaled_frame, (frame_x, frame_y))
    pygame.display.flip()

def main():
    pygame.mixer.pre_init(44100,-16,2,512)
    pygame.init()

    display_size = calculate_initial_display_size()
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE)
    game_surface = pygame.Surface([config.WINDOW_WIDTH, config.WINDOW_HEIGHT])
    board_surface = pygame.Surface([config.BOARD_WIDTH, config.BOARD_HEIGHT])
    pygame.display.set_caption('Pac-Man')
    timer = pygame.time.Clock()
    font = load_font(config.FONT_PATH, config.FONT_SIZE)
    title_font = load_font(config.FONT_PATH_MENU, config.MENU_TITLE_FONT_SIZE, config.FONT_PATH)
    subtitle_font = load_font(config.FONT_PATH_MENU, 33)
    menu_font = load_font(config.FONT_PATH_MENU, config.MENU_TEXT_FONT_SIZE, config.FONT_PATH)
    score_font = load_font(config.FONT_PATH_MENU, 22, config.FONT_PATH)

    game_state = 'menu'

    player_images = load_player_images()
    ghost_images = load_ghost_images()
    sounds = load_sounds()

    powerup_channel = pygame.mixer.Channel(1)

    if sounds['start_game']:
        sounds['start_game'].set_volume(0.10)

    if sounds['power_up']:
        sounds['power_up'].set_volume(0.05)

    if sounds['eating']:
        sounds['eating'].set_volume(0.08)

    level = copy.deepcopy(boards)
    #level = rotacionar_board_180(copy.deepcopy(boards)) 
    player = Pacman(player_images)
    ghost_state = create_initial_ghost_state()

    counter = 0
    flicker = False
    # R, L, U, D
    turns_allowed = [False, False, False, False]
    direction_command = config.PLAYER_START_DIRECTION
    powerup = False
    power_counter = 0
    eaten_ghost = [False, False, False, False]
    targets = [(player.x_pos, player.y_pos)] * 4
    moving = False
    startup_counter = 0
    lives = config.INITIAL_LIVES
    game_over = False
    game_won = False
    player_name = config.PLAYER_DEFAULT_NAME
    name_buffer = player_name
    editing_name = False

    leaderboard = load_leaderboard()

    if leaderboard:
        high_score = leaderboard[0]['score']
    else:
        high_score = 0

    score_registered = False
    score = 0
    death_counter = 0

    run = True
    while run:
        timer.tick(config.FPS)

        if counter < 19:
            counter += 1
            if counter > 3:
                flicker = False
        else:
            counter = 0
            flicker = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == 'leaderboard':
                        game_state = 'menu'

                    elif game_state == 'menu' and editing_name:
                        name_buffer = player_name
                        editing_name = False

                    else:
                        run = False

                    continue

                if game_state == 'menu':
                    if editing_name:
                        if event.key == pygame.K_RETURN:
                            player_name = (
                                name_buffer.strip()
                                or config.PLAYER_DEFAULT_NAME
                            )

                            name_buffer = player_name
                            editing_name = False

                        elif event.key == pygame.K_BACKSPACE:
                            name_buffer = name_buffer[:-1]

                        else:
                            typed_character = event.unicode.upper()

                            valid_character = (
                                typed_character
                                in config.PLAYER_NAME_ALLOWED_CHARACTERS
                            )

                            has_available_space = (
                                len(name_buffer)
                                < config.PLAYER_NAME_MAX_LENGTH
                            )

                            if valid_character and has_available_space:
                                name_buffer += typed_character

                    else:
                        if event.key in (pygame.K_1,pygame.K_KP1):
                            name_buffer = player_name
                            editing_name = True

                        elif event.key in (pygame.K_2,pygame.K_KP2):
                            game_state = 'leaderboard'

                        elif event.key in (pygame.K_RETURN,pygame.K_SPACE):
                            game_state = 'playing'
                            startup_counter = 0
                            score_registered = False
                            play_sound(sounds,'start_game')

                elif game_state == 'leaderboard':
                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_BACKSPACE
                    ):
                        game_state = 'menu'

                elif game_state == 'playing':
                    if event.key == pygame.K_RIGHT:
                        direction_command = 0
                    if event.key == pygame.K_LEFT:
                        direction_command = 1
                    if event.key == pygame.K_UP:
                        direction_command = 2
                    if event.key == pygame.K_DOWN:
                        direction_command = 3
                    if event.key == pygame.K_SPACE and (game_over or game_won):
                        powerup = False
                        power_counter = 0
                        startup_counter = 0
                        direction_command = config.PLAYER_START_DIRECTION
                        ghost_state = reset_round(player)
                        eaten_ghost = [False, False, False, False]
                        score = 0
                        lives = config.INITIAL_LIVES
                        level = copy.deepcopy(boards)
                        game_over = False
                        game_won = False
                        score_registered = False
                        game_state = 'menu'

                    if event.key == pygame.K_r:
                        lives = config.INITIAL_LIVES
                        score = 0
                        level = copy.deepcopy(boards)

                        startup_counter = 0
                        powerup = False
                        power_counter = 0
                        eaten_ghost = [False, False, False, False]

                        direction_command = config.PLAYER_START_DIRECTION
                        ghost_state = reset_round(player)

                        game_over = False
                        game_won = False

                        score_registered = False

            if event.type == pygame.KEYUP and game_state == 'playing':
                if event.key == pygame.K_RIGHT and direction_command == 0:
                    direction_command = player.direction
                if event.key == pygame.K_LEFT and direction_command == 1:
                    direction_command = player.direction
                if event.key == pygame.K_UP and direction_command == 2:
                    direction_command = player.direction
                if event.key == pygame.K_DOWN and direction_command == 3:
                    direction_command = player.direction

        if not run:
            break


        if score > high_score:
            high_score = score


        if game_state == 'menu':
            draw_start_screen(
                game_surface,
                title_font,
                subtitle_font,
                menu_font,
                score_font,
                player_images,
                ghost_images,
                counter,
                player_name,
                name_buffer,
                editing_name
            )

            present_frame(screen,game_surface)
            continue

        if game_state == 'leaderboard':
            draw_leaderboard_screen(
                game_surface,
                title_font,
                menu_font,
                leaderboard
            )

            present_frame(screen,game_surface)
            continue

        if powerup and power_counter < config.POWERUP_DURATION:
            power_counter += 1
        elif powerup and power_counter >= config.POWERUP_DURATION:
            power_counter = 0
            powerup = False
            eaten_ghost = [False, False, False, False]

        startup_active = startup_counter < config.STARTUP_DELAY and not game_over and not game_won

        if startup_active:
            moving = False
            startup_counter += 1
        elif game_over or game_won:
            moving = False
        else:
            moving = True

        game_surface.fill('black')
        board_surface.fill('black')
        draw_board(board_surface, level, flicker)

        dead_flags = [
            ghost_state['blinky']['dead'],
            ghost_state['inky']['dead'],
            ghost_state['pinky']['dead'],
            ghost_state['clyde']['dead'],
        ]
        ghost_speeds = calculate_ghost_speeds(powerup, eaten_ghost, dead_flags)
        game_won = has_player_won(level)

        player_circle = pygame.Rect(player.center_x - 20, player.center_y - 20, 40, 40)

        if not startup_active:
            player.draw(board_surface, counter)

        ghosts = create_ghosts(
            board_surface,
            level,
            targets,
            ghost_speeds,
            ghost_images,
            ghost_state,
            powerup,
            eaten_ghost,
            counter,
            visible=not startup_active
        )
        blinky, inky, pinky, clyde = ghosts

        game_surface.blit(board_surface, (0, config.TOP_UI_HEIGHT))
        draw_misc(
            game_surface,
            font,
            score_font,
            score,
            high_score,
            powerup,
            lives,
            game_over,
            game_won,
            startup_active,
            player_images
        )
        targets = get_targets(player.x_pos, player.y_pos, powerup, eaten_ghost, blinky, inky, pinky, clyde)

        turns_allowed = player.check_position(level)
        if moving:
            player.move(turns_allowed)
            move_ghosts(ghosts, ghost_state)

        if moving:
            previous_score = score
            previous_powerup = powerup
            previous_power_counter = power_counter

            score,powerup,power_counter,eaten_ghost = player.check_pellet_collisions(
                level,score,powerup,power_counter,eaten_ghost
            )

            collected_powerup = (
                powerup
                and (
                    not previous_powerup
                    or power_counter < previous_power_counter
                )
            )

            if collected_powerup and sounds['power_up']:
                powerup_channel.play(sounds['power_up'])
            elif score > previous_score:
                play_sound(sounds,'eating')

            if player_hit_by_ghost(player_circle, ghosts, powerup, eaten_ghost):
                if lives > 0:
                    lives -= 1
                    startup_counter = 0
                    powerup = False
                    power_counter = 0
                    play_sound(sounds,'death')
                    if death_counter < config.DEATH_ANIMATION_DURATION:
                        death_counter += 1
                    elif death_counter >= config.DEATH_ANIMATION_DURATION:
                        death_counter = 0
                    ghost_state = reset_round(player)
                    eaten_ghost = [False, False, False, False]
                    direction_command = config.PLAYER_START_DIRECTION
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
                    play_sound(sounds,'death')
                    if death_counter < config.DEATH_ANIMATION_DURATION:
                        death_counter += 1
                    elif death_counter >= config.DEATH_ANIMATION_DURATION:
                        death_counter = 0
            elif powerup:
                score = eat_available_ghosts(player_circle, ghosts, ghost_state, eaten_ghost, score)

        if score > high_score: 
            high_score = score

        if (game_over or game_won) and not score_registered:
            leaderboard = add_score(
                leaderboard,
                player_name,
                score
            )

            score_registered = True
    
        if direction_command == 0 and turns_allowed[0]:
            player.direction = 0
        if direction_command == 1 and turns_allowed[1]:
            player.direction = 1
        if direction_command == 2 and turns_allowed[2]:
            player.direction = 2
        if direction_command == 3 and turns_allowed[3]:
            player.direction = 3

        player.apply_tunnel_wrap()

        for name, ghost in zip(['blinky', 'inky', 'pinky', 'clyde'], ghosts):
            if ghost.in_box and ghost_state[name]['dead']:
                ghost_state[name]['dead'] = False

        present_frame(screen, game_surface)

    pygame.quit()


if __name__ == '__main__':
    main()