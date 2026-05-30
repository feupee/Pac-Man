import random

import pygame

from config import (
    COR_FUNDO,
    COR_PACMAN,
    TAMANHO_BLOCO,
    VELOCIDADE_FANTASMA,
    VELOCIDADE_PACMAN,
)


DIRECOES = {
    "cima": pygame.Vector2(0, -1),
    "baixo": pygame.Vector2(0, 1),
    "esquerda": pygame.Vector2(-1, 0),
    "direita": pygame.Vector2(1, 0),
}

DIRECOES_POSSIVEIS = list(DIRECOES.values())


class Entidade:
    """
    Classe base para personagens que se movimentam entre os centros
    dos blocos do labirinto.
    """

    def __init__(self, mapa, bloco_inicial, raio, velocidade):
        self.mapa = mapa
        self.bloco_inicial = bloco_inicial
        self.raio = raio
        self.velocidade = velocidade

        self.bloco_atual = bloco_inicial
        self.proximo_bloco = None
        self.posicao = pygame.Vector2(self.mapa.centro_do_bloco(bloco_inicial))
        self.direcao = pygame.Vector2(0, 0)

        self.rect = pygame.Rect(0, 0, raio * 2, raio * 2)
        self._sincronizar_rect()

    def reiniciar(self):
        self.bloco_atual = self.bloco_inicial
        self.proximo_bloco = None
        self.posicao = pygame.Vector2(self.mapa.centro_do_bloco(self.bloco_inicial))
        self.direcao = pygame.Vector2(0, 0)
        self._sincronizar_rect()

    def _sincronizar_rect(self):
        self.rect.center = (round(self.posicao.x), round(self.posicao.y))

    def _obter_bloco_vizinho(self, direcao):
        coluna, linha = self.bloco_atual
        return (
            coluna + int(direcao.x),
            linha + int(direcao.y),
        )

    def _direcao_valida(self, direcao):
        if direcao.length_squared() == 0:
            return False

        bloco_vizinho = self._obter_bloco_vizinho(direcao)
        return not self.mapa.eh_parede(bloco_vizinho)

    def _definir_proximo_bloco(self, direcao):
        self.direcao = pygame.Vector2(direcao)
        self.proximo_bloco = self._obter_bloco_vizinho(self.direcao)

    def _escolher_proximo_bloco(self):
        raise NotImplementedError

    def atualizar(self, delta_tempo):
        """
        Move a entidade de um centro de bloco até o próximo.

        Essa abordagem evita que o personagem atravesse paredes ou fique
        desalinhado ao fazer curvas.
        """
        distancia_restante = self.velocidade * delta_tempo

        while distancia_restante > 0:
            if self.proximo_bloco is None:
                self._escolher_proximo_bloco()

                if self.proximo_bloco is None:
                    break

            destino = pygame.Vector2(
                self.mapa.centro_do_bloco(self.proximo_bloco)
            )
            distancia_ate_destino = self.posicao.distance_to(destino)

            if distancia_restante >= distancia_ate_destino:
                self.posicao = destino
                self.bloco_atual = self.proximo_bloco
                self.proximo_bloco = None
                distancia_restante -= distancia_ate_destino

            else:
                deslocamento = destino - self.posicao
                self.posicao += deslocamento.normalize() * distancia_restante
                distancia_restante = 0

        self._sincronizar_rect()


class Pacman(Entidade):
    def __init__(self, mapa, bloco_inicial):
        super().__init__(
            mapa=mapa,
            bloco_inicial=bloco_inicial,
            raio=TAMANHO_BLOCO // 2 - 4,
            velocidade=VELOCIDADE_PACMAN,
        )
        self.direcao_desejada = pygame.Vector2(0, 0)

    def reiniciar(self):
        super().reiniciar()
        self.direcao_desejada = pygame.Vector2(0, 0)

    def definir_direcao(self, direcao):
        """
        Guarda a direção escolhida pelo jogador.

        A curva somente será executada quando o Pac-Man chegar ao centro
        de um bloco em que essa direção seja válida.
        """
        self.direcao_desejada = pygame.Vector2(direcao)

    def _escolher_proximo_bloco(self):
        if self._direcao_valida(self.direcao_desejada):
            self._definir_proximo_bloco(self.direcao_desejada)

        elif self._direcao_valida(self.direcao):
            self._definir_proximo_bloco(self.direcao)

        else:
            self.direcao = pygame.Vector2(0, 0)
            self.proximo_bloco = None

    def desenhar(self, tela):
        centro = self.rect.center
        pygame.draw.circle(tela, COR_PACMAN, centro, self.raio)

        direcao_boca = self.direcao

        if direcao_boca.length_squared() == 0:
            direcao_boca = DIRECOES["direita"]

        perpendicular = pygame.Vector2(-direcao_boca.y, direcao_boca.x)

        ponta_superior = (
            centro[0] + direcao_boca.x * self.raio + perpendicular.x * self.raio * 0.55,
            centro[1] + direcao_boca.y * self.raio + perpendicular.y * self.raio * 0.55,
        )
        ponta_inferior = (
            centro[0] + direcao_boca.x * self.raio - perpendicular.x * self.raio * 0.55,
            centro[1] + direcao_boca.y * self.raio - perpendicular.y * self.raio * 0.55,
        )

        pygame.draw.polygon(
            tela,
            COR_FUNDO,
            [centro, ponta_superior, ponta_inferior],
        )


class Fantasma(Entidade):
    def __init__(self, mapa, bloco_inicial, cor):
        super().__init__(
            mapa=mapa,
            bloco_inicial=bloco_inicial,
            raio=TAMANHO_BLOCO // 2 - 4,
            velocidade=VELOCIDADE_FANTASMA,
        )
        self.cor = cor

    def _escolher_proximo_bloco(self):
        direcoes_validas = [
            direcao
            for direcao in DIRECOES_POSSIVEIS
            if self._direcao_valida(direcao)
        ]

        if not direcoes_validas:
            self.direcao = pygame.Vector2(0, 0)
            self.proximo_bloco = None
            return

        direcao_oposta = -self.direcao
        direcoes_sem_retorno = [
            direcao
            for direcao in direcoes_validas
            if direcao != direcao_oposta
        ]

        if direcoes_sem_retorno:
            direcoes_validas = direcoes_sem_retorno

        self._definir_proximo_bloco(random.choice(direcoes_validas))

    def desenhar(self, tela):
        centro_x, centro_y = self.rect.center
        topo_y = centro_y - self.raio
        largura = self.raio * 2
        altura_corpo = self.raio

        pygame.draw.circle(
            tela,
            self.cor,
            (centro_x, centro_y - self.raio // 3),
            self.raio,
        )
        pygame.draw.rect(
            tela,
            self.cor,
            pygame.Rect(
                centro_x - self.raio,
                centro_y - self.raio // 3,
                largura,
                altura_corpo + self.raio // 3,
            ),
        )

        raio_olho = 4
        deslocamento_olho = 6
        y_olhos = topo_y + self.raio

        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (centro_x - deslocamento_olho, y_olhos),
            raio_olho,
        )
        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (centro_x + deslocamento_olho, y_olhos),
            raio_olho,
        )
