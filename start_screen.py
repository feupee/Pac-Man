import pygame
import config

def draw_chase_animation(screen,player_images,ghost_images,counter,animation_y):
    ghost_names = ['blinky','pinky','inky','clyde']

    speed = 155
    sprite_spacing = 62
    ghost_distance = 90
    screen_margin = 70
    pause_duration = 0.35

    last_ghost_offset = ghost_distance + (len(ghost_names) - 1) * sprite_spacing

    travel_distance = (
        screen.get_width()
        + (screen_margin * 2)
        + last_ghost_offset
    )

    travel_duration = travel_distance / speed
    cycle_duration = (travel_duration * 2) + (pause_duration * 2)

    elapsed_time = pygame.time.get_ticks() / 1000
    cycle_time = elapsed_time % cycle_duration

    player_animation_frame = player_images[counter // 7]
    ghost_animation_frame = counter // 10

    # =========================
    # Fase 1:
    # Pac-Man foge dos fantasmas
    # da esquerda para a direita.
    # =========================
    if cycle_time < travel_duration:
        distance = cycle_time * speed
        player_x = -screen_margin + distance

        # Pac-Man olha para a direita.
        screen.blit(
            player_animation_frame,
            (int(player_x),animation_y)
        )

        for index,ghost_name in enumerate(ghost_names):
            ghost_x = (
                player_x
                - ghost_distance
                - index * sprite_spacing
            )

            ghost_frame = ghost_images[ghost_name][0][ghost_animation_frame]

            screen.blit(
                ghost_frame,
                (int(ghost_x),animation_y)
            )

        return

    # Pausa curta depois que todos saem da tela.
    reverse_start = travel_duration + pause_duration

    if cycle_time < reverse_start:
        return

    # =========================
    # Fase 2:
    # Pac-Man persegue os fantasmas
    # no modo spooked da direita
    # para a esquerda.
    # =========================
    reverse_end = reverse_start + travel_duration

    if cycle_time < reverse_end:
        reverse_time = cycle_time - reverse_start
        distance = reverse_time * speed

        player_x = (
            screen.get_width()
            + screen_margin
            + last_ghost_offset
            - distance
        )

        # Pac-Man olha para a esquerda.
        reversed_player_frame = pygame.transform.flip(
            player_animation_frame,
            True,
            False
        )

        for index in range(len(ghost_names)):
            ghost_x = (
                player_x
                - ghost_distance
                - index * sprite_spacing
            )

            spooked_frame = ghost_images['spooked'][ghost_animation_frame]

            screen.blit(
                spooked_frame,
                (int(ghost_x),animation_y)
            )

        screen.blit(
            reversed_player_frame,
            (int(player_x),animation_y)
        )

def draw_start_screen(screen,title_font,subtitle_font,menu_font,score_font,player_images,ghost_images,counter,player_name,name_buffer,editing_name):
    screen.fill('black')

    def draw_text(text, font, color, x, y, center=False):
        # Sem antialiasing para preservar o visual pixelado do arcade.
        text_surface = font.render(text, False, color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        screen.blit(text_surface, text_rect)

    center_x = config.WINDOW_WIDTH // 2

    # Placar superior inspirado na tela original.
    draw_text('1UP', score_font, config.WHITE, center_x - 280, 18, center=True)
    draw_text('HIGH SCORE', score_font, config.WHITE, center_x, 18, center=True)
    draw_text('2UP', score_font, config.WHITE, center_x + 280, 18, center=True)
    draw_text('00', score_font, config.WHITE, center_x - 280, 54, center=True)

    # Apresentação dos personagens e de seus apelidos.
    draw_text('CHARACTER  /  NICKNAME', subtitle_font, config.WHITE, center_x, 145, center=True)

    ghost_rows = [
        ('blinky', '- SHADOW', '"BLINKY"', config.RED),
        ('pinky', '- SPEEDY', '"PINKY"', config.PINK),
        ('inky', '- BASHFUL', '"INKY"', config.CYAN),
        ('clyde', '- POKEY', '"CLYDE"', config.ORANGE),
    ]

    sprite_x = center_x - 305
    character_x = center_x - 235
    nickname_x = center_x + 75
    first_row_y = 220
    row_spacing = 72

    for index, (ghost_name, character_name, nickname, color) in enumerate(ghost_rows):
        row_y = first_row_y + index * row_spacing
        ghost_frame = ghost_images[ghost_name][0][counter // 10]
        screen.blit(ghost_frame, (sprite_x, row_y - 12))
        draw_text(character_name, menu_font, color, character_x, row_y)
        draw_text(nickname, menu_font, color, nickname_x, row_y)

    # Valores das pastilhas.
    pellet_y = first_row_y + len(ghost_rows) * row_spacing + 18
    pygame.draw.circle(screen, config.WHITE, (center_x - 70, pellet_y), 7)
    draw_text('10 PTS', menu_font, config.WHITE, center_x - 20, pellet_y - 13)

    pygame.draw.circle(screen, config.WHITE, (center_x - 70, pellet_y + 62), 14)
    draw_text('50 PTS', menu_font, config.WHITE, center_x - 20, pellet_y + 49)

    # Animação contínua inspirada na tela original.
    animation_y = pellet_y + 145
    draw_chase_animation(screen,player_images,ghost_images,counter,animation_y)

    # Opções disponíveis no menu inicial.
    menu_y = config.WINDOW_HEIGHT - 272

    if editing_name:
        cursor = ''

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor = '_'

        draw_text(
            'TYPE YOUR NAME',
            menu_font,
            config.WHITE,
            center_x,
            menu_y,
            center=True
        )

        draw_text(
            f'{name_buffer}{cursor}',
            menu_font,
            config.YELLOW,
            center_x,
            menu_y + 38,
            center=True
        )

        draw_text(
            'ENTER CONFIRMS  ESC CANCELS',
            menu_font,
            config.WHITE,
            center_x,
            menu_y + 76,
            center=True
        )

    else:
        draw_text(
            f'PLAYER  {player_name}',
            menu_font,
            config.CYAN,
            center_x,
            menu_y,
            center=True
        )

        draw_text(
            '1 CHANGE NAME   2 LEADERBOARD',
            menu_font,
            config.WHITE,
            center_x,
            menu_y + 38,
            center=True
        )

        # Pisca a cada meio segundo para indicar como começar a partida.
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_text(
                'PRESS ENTER OR SPACE',
                menu_font,
                config.WHITE,
                center_x,
                menu_y + 76,
                center=True
            )

    # Rodapé no estilo da tela arcade.
    draw_text('(C) 1980 MIDWAY MFG. CO.', menu_font, config.PINK, center_x, config.WINDOW_HEIGHT - 82, center=True)
    draw_text('CREDIT  ∞', menu_font, config.WHITE, 40, config.WINDOW_HEIGHT - 140)

def draw_leaderboard_screen(screen,title_font,menu_font,leaderboard):
    """
    Desenha uma tela separada para exibir as cinco melhores pontuações.
    """
    screen.fill('black')

    def draw_text(text,font,color,x,y,center=False):
        # Sem antialiasing para preservar o visual pixelado do arcade.
        text_surface = font.render(str(text),False,color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = (x,y)
        else:
            text_rect.topleft = (x,y)

        screen.blit(text_surface,text_rect)

    center_x = config.WINDOW_WIDTH // 2

    draw_text(
        'LEADERBOARD',
        title_font,
        config.YELLOW,
        center_x,
        155,
        center=True
    )

    draw_text(
        'RANK',
        menu_font,
        config.WHITE,
        center_x - 260,
        275
    )

    draw_text(
        'PLAYER',
        menu_font,
        config.WHITE,
        center_x - 95,
        275
    )

    draw_text(
        'SCORE',
        menu_font,
        config.WHITE,
        center_x + 185,
        275
    )

    if leaderboard:
        for index,entry in enumerate(leaderboard,start=1):
            row_y = 340 + (index - 1) * 62

            draw_text(
                f'{index:02d}',
                menu_font,
                config.WHITE,
                center_x - 260,
                row_y
            )

            draw_text(
                entry['name'],
                menu_font,
                config.CYAN,
                center_x - 95,
                row_y
            )

            draw_text(
                f"{entry['score']:02d}",
                menu_font,
                config.WHITE,
                center_x + 185,
                row_y
            )

    else:
        draw_text(
            'NO SCORES REGISTERED',
            menu_font,
            config.WHITE,
            center_x,
            420,
            center=True
        )

    draw_text(
        'PRESS ESC TO RETURN',
        menu_font,
        config.PINK,
        center_x,
        config.WINDOW_HEIGHT - 110,
        center=True
    )