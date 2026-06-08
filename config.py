# Configurações fixas da janela
WINDOW_WIDTH = 900

#Caminhos sons
SOUND_PATHS = {
    'start_game': 'sounds/start_game.mp3',
    'eating': 'sounds/eating.mp3',
    'press_start': 'sounds/press_start.mp3',
    'death': 'sounds/dead.mp3',
    'power_up': 'sounds/power_up.mp3',
}

#Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 255, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
PELLET_COLOR = (255, 184, 174)

# Espaços lógicos livres acima e abaixo do mapa para a interface
# Essas áreas são preservadas mesmo quando a janela visível é reduzida.
TOP_UI_HEIGHT = 64
BOTTOM_UI_HEIGHT = 64

# A janela visível ocupa no máximo esta proporção da resolução do monitor.
# Reduza o valor para criar uma janela ainda menor.
DISPLAY_MAX_USAGE = 0.85

FPS = 60
FONT_PATH = 'freesansbold.ttf'
FONT_PATH_MENU = 'fonts/Joystix_W00_Proportional.ttf'
FONT_SIZE = 20
MENU_TITLE_FONT_SIZE = 72
MENU_TEXT_FONT_SIZE = 20
BOARD_COLOR = 'blue'

# Configurações fixas do tabuleiro
BOARD_ROWS = 33
BOARD_COLUMNS = 30
CELL_WIDTH = 30
CELL_HEIGHT = 28
BOARD_WIDTH = BOARD_COLUMNS * CELL_WIDTH
BOARD_HEIGHT = BOARD_ROWS * CELL_HEIGHT

# Altura total da janela: interface superior + mapa + interface inferior
WINDOW_HEIGHT = TOP_UI_HEIGHT + BOARD_HEIGHT + BOTTOM_UI_HEIGHT

# Configurações fixas do Pac-Man
PLAYER_START_X = 430
PLAYER_START_Y = 663
PLAYER_START_DIRECTION = 0
PLAYER_SPEED = 3
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
    'blinky': {'x': 425, 'y': 325, 'direction': 0},
    'inky': {'x': 490, 'y': 410, 'direction': 1},
    'pinky': {'x': 430, 'y': 410, 'direction': 2},
    'clyde': {'x': 370, 'y': 410, 'direction': 3},
}
# Tempo necessário para liberar cada fantasma da caixa.
GHOST_RELEASE_DELAYS = {
    'blinky': 0,
    'pinky': 0,
    'inky': 3 * FPS,
    'clyde': 5 * FPS,
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
POWERUP_DURATION = 480
STARTUP_DELAY = 270
DEATH_ANIMATION_DURATION = 120

# FPS * segundos = número de frames

# Configurações do jogador
PLAYER_DEFAULT_NAME = 'PLAYER ONE'
PLAYER_NAME_MAX_LENGTH = 10
PLAYER_NAME_ALLOWED_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '

# Configurações do leaderboard
LEADERBOARD_FILE = 'leaderboard.json'
LEADERBOARD_SIZE = 5

# Cor adicional utilizada no menu
YELLOW = (255,255,0)

# Configurações da fruta bônus
BONUS_START_X = 120
BONUS_START_Y = 182
BONUS_MIN_X = 120
BONUS_MAX_X = 780