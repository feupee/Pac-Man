import pygame
import config

from ghost import *
from collision import rectangles_collide


def load_sounds():
    sounds = {}

    for name,path in config.SOUND_PATHS.items():
        sounds[name] = pygame.mixer.Sound(path)

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

def draw_misc(
    screen,
    font,
    score_font,
    title_font,
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
        draw_text(
            'GAME   OVER',
            title_font,
            'red',
            center_x,
            message_y + 45,
            center=True
        )

    if game_won:
        draw_text(
            'VICTORY',
            title_font,
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
        
def player_hit_by_ghost(player_hitbox,ghosts,powerup,eaten_ghost):
    if not powerup:
        return any(rectangles_collide(player_hitbox,ghost.hitbox) and not ghost.dead for ghost in ghosts)

    return any(
        rectangles_collide(player_hitbox,ghost.hitbox) and eaten_ghost[index] and not ghost.dead
        for index, ghost in enumerate(ghosts)
    )


def eat_available_ghosts(player_hitbox,ghosts,ghost_state,eaten_ghost,score):
    ghost_names = ['blinky', 'inky', 'pinky', 'clyde']

    for index, ghost in enumerate(ghosts):
        if rectangles_collide(player_hitbox,ghost.hitbox) and not ghost.dead and not eaten_ghost[index]:
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
