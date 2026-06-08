import copy
import math
import pygame
import config

from board import *
from ghost import *
from pacman import Pacman
from leaderboard import add_score, load_leaderboard
from start_screen import draw_leaderboard_screen, draw_start_screen
from bonus import BonusFruit
from game import *
from collision import create_hitbox

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

    bonus = BonusFruit(
        config.BONUS_START_X,
        config.BONUS_START_Y,
        config.BONUS_MIN_X,
        config.BONUS_MAX_X
    )

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
    release_counter = 0
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
                            release_counter = 0
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
                        release_counter = 0
                        eaten_ghost = [False, False, False, False]
                        score = 0
                        bonus.reset()
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
                        release_counter = 0

                        bonus.reset()

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

        if not startup_active:
            bonus.draw(board_surface)
            player.draw(board_surface,counter)

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
            title_font,
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
            release_counter += 1
            bonus.update()
            player.move(turns_allowed)
            move_ghosts(ghosts,ghost_state,release_counter)

        if moving:
            previous_score = score
            previous_powerup = powerup
            previous_power_counter = power_counter

            score,powerup,power_counter,eaten_ghost = player.check_pellet_collisions(
                level,score,powerup,power_counter,eaten_ghost
            )

            current_player_hitbox = create_hitbox(
                player.center_x,
                player.center_y,
                40,
                40
            )

            score += bonus.collect_if_colliding(current_player_hitbox)

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

            if player_hit_by_ghost(current_player_hitbox,ghosts,powerup,eaten_ghost):
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
                    release_counter = 0
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
                score = eat_available_ghosts(current_player_hitbox,ghosts,ghost_state,eaten_ghost,score)

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