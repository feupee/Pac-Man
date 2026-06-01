import pygame
import config

pygame.init()

tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
temporizador = pygame.time.Clock()
fonte = pygame.font.SysFont('freesansbold.ttf', 20)

run = True
while run:
    timer.tick(config.FPS)
    screen.fill(config.COR_FUNDO)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()