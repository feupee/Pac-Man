import sys

import pygame

from config import ALTURA_HUD, COR_HUD, COR_TEXTO, FPS
from entidades import DIRECOES, Fantasma, Pacman
from mapa import Mapa


CORES_FANTASMAS = [
    (255, 60, 60),
    (255, 150, 220),
    (80, 220, 255),
    (255, 170, 70),
]


def criar_personagens(mapa):
    pacman = Pacman(mapa, mapa.posicao_inicial_pacman)

    fantasmas = []
    for indice, bloco_inicial in enumerate(mapa.posicoes_iniciais_fantasmas):
        cor = CORES_FANTASMAS[indice % len(CORES_FANTASMAS)]
        fantasmas.append(Fantasma(mapa, bloco_inicial, cor))

    return pacman, fantasmas


def reiniciar_rodada(pacman, fantasmas):
    pacman.reiniciar()

    for fantasma in fantasmas:
        fantasma.reiniciar()


def desenhar_hud(tela, mapa, fonte, pontos, vidas):
    retangulo_hud = pygame.Rect(
        0,
        mapa.altura_pixels,
        mapa.largura_pixels,
        ALTURA_HUD,
    )
    pygame.draw.rect(tela, COR_HUD, retangulo_hud)

    texto = fonte.render(
        f"Pontos: {pontos}    Vidas: {vidas}",
        True,
        COR_TEXTO,
    )
    tela.blit(texto, (16, mapa.altura_pixels + 16))


def desenhar_mensagem_central(tela, mapa, fonte, mensagem):
    texto = fonte.render(mensagem, True, COR_TEXTO)
    retangulo = texto.get_rect(
        center=(mapa.largura_pixels // 2, mapa.altura_pixels // 2)
    )

    fundo = retangulo.inflate(36, 24)
    pygame.draw.rect(tela, COR_HUD, fundo, border_radius=8)
    tela.blit(texto, retangulo)


def main():
    pygame.init()
    pygame.display.set_caption("Pac-Man em Pygame")

    mapa = Mapa()
    tela = pygame.display.set_mode(
        (mapa.largura_pixels, mapa.altura_janela)
    )
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("arial", 22)

    pacman, fantasmas = criar_personagens(mapa)

    pontos = 0
    vidas = 3
    jogo_encerrado = False
    jogador_venceu = False

    while True:
        delta_tempo = relogio.tick(FPS) / 1000

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if evento.key == pygame.K_r:
                    mapa = Mapa()
                    pacman, fantasmas = criar_personagens(mapa)
                    pontos = 0
                    vidas = 3
                    jogo_encerrado = False
                    jogador_venceu = False

                if not jogo_encerrado and not jogador_venceu:
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        pacman.definir_direcao(DIRECOES["cima"])

                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        pacman.definir_direcao(DIRECOES["baixo"])

                    elif evento.key in (pygame.K_LEFT, pygame.K_a):
                        pacman.definir_direcao(DIRECOES["esquerda"])

                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        pacman.definir_direcao(DIRECOES["direita"])

        if not jogo_encerrado and not jogador_venceu:
            pacman.atualizar(delta_tempo)

            for fantasma in fantasmas:
                fantasma.atualizar(delta_tempo)

            tipo_pastilha = mapa.consumir_pastilha(pacman.bloco_atual)

            if tipo_pastilha == "normal":
                pontos += 10

            elif tipo_pastilha == "especial":
                pontos += 50

            for fantasma in fantasmas:
                if pacman.rect.colliderect(fantasma.rect):
                    vidas -= 1

                    if vidas <= 0:
                        jogo_encerrado = True
                    else:
                        reiniciar_rodada(pacman, fantasmas)

                    break

            if not mapa.pastilhas:
                jogador_venceu = True

        mapa.desenhar(tela)

        pacman.desenhar(tela)

        for fantasma in fantasmas:
            fantasma.desenhar(tela)

        desenhar_hud(tela, mapa, fonte, pontos, vidas)

        if jogo_encerrado:
            desenhar_mensagem_central(
                tela,
                mapa,
                fonte,
                "Fim de jogo. Pressione R para reiniciar.",
            )

        elif jogador_venceu:
            desenhar_mensagem_central(
                tela,
                mapa,
                fonte,
                "Você venceu. Pressione R para reiniciar.",
            )

        pygame.display.flip()


if __name__ == "__main__":
    main()
