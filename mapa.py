import pygame

from config import (
    ALTURA_HUD,
    COR_FUNDO,
    COR_PAREDE,
    COR_PASTILHA,
    TAMANHO_BLOCO,
)


MAPA_BASE = [
    "#####################",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#o###.###.#.###.###o#",
    "#...................#",
    "#.###.#.#######.#.###",
    "#.....#....#....#...#",
    "#####.#### # ####.###",
    "#####.#    G    #.###",
    "#####.#.##   ##.#.###",
    "#.........P.........#",
    "#.###.#.#######.#.###",
    "#o..#.#....#....#..o#",
    "###.#.###.#.#.###.###",
    "#.....#...#.#...#...#",
    "#.#######.#.#.#######",
    "#...................#",
    "#####################",
]


class Mapa:
    """
    Armazena a estrutura do labirinto.

    Cada caractere do MAPA_BASE representa um bloco:
    # -> parede
    . -> pastilha comum
    o -> pastilha especial
    P -> posição inicial do Pac-Man
    G -> posição inicial de um fantasma
    espaço -> corredor vazio
    """

    def __init__(self):
        self.linhas = [list(linha) for linha in MAPA_BASE]
        self.altura = len(self.linhas)
        self.largura = len(self.linhas[0])

        self.paredes = set()
        self.pastilhas = {}
        self.posicao_inicial_pacman = None
        self.posicoes_iniciais_fantasmas = []

        self._carregar_elementos()

    @property
    def largura_pixels(self):
        return self.largura * TAMANHO_BLOCO

    @property
    def altura_pixels(self):
        return self.altura * TAMANHO_BLOCO

    @property
    def altura_janela(self):
        return self.altura_pixels + ALTURA_HUD

    def _carregar_elementos(self):
        for linha, conteudo_linha in enumerate(self.linhas):
            for coluna, caractere in enumerate(conteudo_linha):
                bloco = (coluna, linha)

                if caractere == "#":
                    self.paredes.add(bloco)

                elif caractere == ".":
                    self.pastilhas[bloco] = "normal"

                elif caractere == "o":
                    self.pastilhas[bloco] = "especial"

                elif caractere == "P":
                    self.posicao_inicial_pacman = bloco
                    self.linhas[linha][coluna] = " "

                elif caractere == "G":
                    self.posicoes_iniciais_fantasmas.append(bloco)
                    self.linhas[linha][coluna] = " "

        if self.posicao_inicial_pacman is None:
            raise ValueError("O mapa precisa ter uma posição inicial marcada com P.")

    def centro_do_bloco(self, bloco):
        coluna, linha = bloco
        return (
            coluna * TAMANHO_BLOCO + TAMANHO_BLOCO // 2,
            linha * TAMANHO_BLOCO + TAMANHO_BLOCO // 2,
        )

    def eh_parede(self, bloco):
        coluna, linha = bloco

        if coluna < 0 or coluna >= self.largura:
            return True

        if linha < 0 or linha >= self.altura:
            return True

        return bloco in self.paredes

    def consumir_pastilha(self, bloco):
        """
        Remove a pastilha do bloco informado e retorna seu tipo.
        Retorna None se não existir uma pastilha nesse bloco.
        """
        return self.pastilhas.pop(bloco, None)

    def desenhar(self, tela):
        tela.fill(COR_FUNDO)

        for coluna, linha in self.paredes:
            retangulo = pygame.Rect(
                coluna * TAMANHO_BLOCO,
                linha * TAMANHO_BLOCO,
                TAMANHO_BLOCO,
                TAMANHO_BLOCO,
            )
            pygame.draw.rect(tela, COR_PAREDE, retangulo, border_radius=5)

        for bloco, tipo in self.pastilhas.items():
            centro = self.centro_do_bloco(bloco)
            raio = 3 if tipo == "normal" else 7
            pygame.draw.circle(tela, COR_PASTILHA, centro, raio)
