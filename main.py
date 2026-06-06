import copy
import math

import pygame

import config
from board import boards, rotacionar_board_180
from ghost import Ghost, calculate_ghost_speeds, get_targets
from pacman import Pacman


def load_scaled_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size)


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


def draw_misc(screen, font, score, powerup, lives, game_over, game_won, player_images):
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], config.LIFE_SPRITE_SIZE), (650 + i * 40, 915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))


def draw_board(screen, level, flicker):
    num1 = (config.HEIGHT - config.BOARD_BOTTOM_MARGIN) // config.BOARD_ROWS
    num2 = config.WIDTH // config.BOARD_COLUMNS
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


def create_ghosts(screen, level, targets, speeds, ghost_images, ghost_state, powerup, eaten_ghost, counter):
    common_arguments = {
        'screen': screen,
        'level': level,
        'powerup': powerup,
        'eaten_ghost': eaten_ghost,
        'spooked_images': ghost_images['spooked'],
        'dead_images': ghost_images['dead'],
        'counter': counter,
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


def main():
    pygame.init()

    screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT])
    timer = pygame.time.Clock()
    font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE)

    player_images = load_player_images()
    ghost_images = load_ghost_images()

    level = copy.deepcopy(boards)
    #level = rotacionar_board_180(copy.deepcopy(boards)) 
    player = Pacman(player_images)
    ghost_state = create_initial_ghost_state()

    counter = 0
    flicker = False
    # R, L, U, D
    turns_allowed = [False, False, False, False]
    direction_command = config.PLAYER_START_DIRECTION
    score = 0
    powerup = False
    power_counter = 0
    eaten_ghost = [False, False, False, False]
    targets = [(player.x_pos, player.y_pos)] * 4
    moving = False
    startup_counter = 0
    lives = config.INITIAL_LIVES
    game_over = False
    game_won = False

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
        if powerup and power_counter < config.POWERUP_DURATION:
            power_counter += 1
        elif powerup and power_counter >= config.POWERUP_DURATION:
            power_counter = 0
            powerup = False
            eaten_ghost = [False, False, False, False]
        if startup_counter < config.STARTUP_DELAY and not game_over and not game_won:
            moving = False
            startup_counter += 1
        else:
            moving = True

        screen.fill('black')
        draw_board(screen, level, flicker)

        dead_flags = [
            ghost_state['blinky']['dead'],
            ghost_state['inky']['dead'],
            ghost_state['pinky']['dead'],
            ghost_state['clyde']['dead'],
        ]
        ghost_speeds = calculate_ghost_speeds(powerup, eaten_ghost, dead_flags)
        game_won = has_player_won(level)

        player_circle = pygame.draw.circle(screen, 'black', (player.center_x, player.center_y), 20, 2)
        player.draw(screen, counter)
        ghosts = create_ghosts(
            screen,
            level,
            targets,
            ghost_speeds,
            ghost_images,
            ghost_state,
            powerup,
            eaten_ghost,
            counter
        )
        blinky, inky, pinky, clyde = ghosts

        draw_misc(screen, font, score, powerup, lives, game_over, game_won, player_images)
        targets = get_targets(player.x_pos, player.y_pos, powerup, eaten_ghost, blinky, inky, pinky, clyde)

        turns_allowed = player.check_position(level)
        if moving:
            player.move(turns_allowed)
            move_ghosts(ghosts, ghost_state)

        score, powerup, power_counter, eaten_ghost = player.check_pellet_collisions(
            level, score, powerup, power_counter, eaten_ghost
        )

        if player_hit_by_ghost(player_circle, ghosts, powerup, eaten_ghost):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0
                direction_command = config.PLAYER_START_DIRECTION
                ghost_state = reset_round(player)
                eaten_ghost = [False, False, False, False]
            else:
                game_over = True
                moving = False
                startup_counter = 0
        elif powerup:
            score = eat_available_ghosts(player_circle, ghosts, ghost_state, eaten_ghost, score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
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

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT and direction_command == 0:
                    direction_command = player.direction
                if event.key == pygame.K_LEFT and direction_command == 1:
                    direction_command = player.direction
                if event.key == pygame.K_UP and direction_command == 2:
                    direction_command = player.direction
                if event.key == pygame.K_DOWN and direction_command == 3:
                    direction_command = player.direction

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

        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
