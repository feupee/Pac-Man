# Configurações fixas da janela
WIDTH = 900
HEIGHT = 950
FPS = 60
FONT_PATH = 'freesansbold.ttf'
FONT_SIZE = 20
BOARD_COLOR = 'blue'

# Configurações fixas do tabuleiro
BOARD_BOTTOM_MARGIN = 50
BOARD_ROWS = 32
BOARD_COLUMNS = 30

# Configurações fixas do Pac-Man
PLAYER_START_X = 450
PLAYER_START_Y = 663
PLAYER_START_DIRECTION = 0
PLAYER_SPEED = 2
PLAYER_SPRITE_SIZE = (45, 45)
LIFE_SPRITE_SIZE = (30, 30)
PLAYER_IMAGE_PATHS = [
    'assets/player_images/1.png',
    'assets/player_images/2.png',
    'assets/player_images/3.png',
]

# Configurações fixas dos fantasmas
GHOST_SPRITE_SIZE = (45, 45)
GHOST_DEFAULT_SPEED = 2
GHOST_POWERUP_SPEED = 1
GHOST_DEAD_SPEED = 4
GHOST_STARTS = {
    'blinky': {'x': 56, 'y': 58, 'direction': 0},
    'inky': {'x': 440, 'y': 388, 'direction': 2},
    'pinky': {'x': 440, 'y': 438, 'direction': 2},
    'clyde': {'x': 440, 'y': 438, 'direction': 2},
}
GHOST_IMAGE_PATHS = {
    # Cada direção possui dois frames de animação.
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    'blinky': {
        0: ['assets/ghost_images/red_01.png', 'assets/ghost_images/red_02.png'],
        1: ['assets/ghost_images/red_03.png', 'assets/ghost_images/red_04.png'],
        2: ['assets/ghost_images/red_05.png', 'assets/ghost_images/red_06.png'],
        3: ['assets/ghost_images/red_07.png', 'assets/ghost_images/red_08.png'],
    },
    'pinky': {
        0: ['assets/ghost_images/pink_01.png', 'assets/ghost_images/pink_02.png'],
        1: ['assets/ghost_images/pink_03.png', 'assets/ghost_images/pink_04.png'],
        2: ['assets/ghost_images/pink_05.png', 'assets/ghost_images/pink_06.png'],
        3: ['assets/ghost_images/pink_07.png', 'assets/ghost_images/pink_08.png'],
    },
    'inky': {
        0: ['assets/ghost_images/blue_01.png', 'assets/ghost_images/blue_02.png'],
        1: ['assets/ghost_images/blue_03.png', 'assets/ghost_images/blue_04.png'],
        2: ['assets/ghost_images/blue_05.png', 'assets/ghost_images/blue_06.png'],
        3: ['assets/ghost_images/blue_07.png', 'assets/ghost_images/blue_08.png'],
    },
    'clyde': {
        0: ['assets/ghost_images/orange_01.png', 'assets/ghost_images/orange_02.png'],
        1: ['assets/ghost_images/orange_03.png', 'assets/ghost_images/orange_04.png'],
        2: ['assets/ghost_images/orange_05.png', 'assets/ghost_images/orange_06.png'],
        3: ['assets/ghost_images/orange_07.png', 'assets/ghost_images/orange_08.png'],
    },
    'spooked': [
        'assets/ghost_images/powerup_01.png',
        'assets/ghost_images/powerup_02.png',
    ],
    'dead': [
        'assets/ghost_images/dead_01.png',
        'assets/ghost_images/dead_02.png',
    ],
}

# Configurações fixas da partida
INITIAL_LIVES = 3
POWERUP_DURATION = 600
STARTUP_DELAY = 180
