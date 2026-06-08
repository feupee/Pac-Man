import math

import pygame


def multiply_matrices(matrix_a,matrix_b):
    """
    Multiplica duas matrizes manualmente.

    Não utiliza NumPy nem funções prontas de transformação.
    """

    result = []

    for row in range(len(matrix_a)):
        result_row = []

        for column in range(len(matrix_b[0])):
            value = 0

            for index in range(len(matrix_b)):
                value += matrix_a[row][index] * matrix_b[index][column]

            result_row.append(value)

        result.append(result_row)

    return result


class BonusFruit:
    """
    Representa uma fruta vetorial animada.

    Os vértices são rotacionados e transladados manualmente
    por meio de matrizes homogêneas.
    """

    def __init__(self,x_pos,y_pos,min_x,max_x):
        self.start_x = x_pos
        self.start_y = y_pos

        self.x_pos = x_pos
        self.y_pos = y_pos

        self.min_x = min_x
        self.max_x = max_x

        self.speed = 2
        self.rotation_speed = 3
        self.angle = 0

        self.active = True

        # Os vértices são definidos em relação ao centro da fruta.
        # O centro da fruta corresponde à origem local (0,0).
        self.body_vertices = [
            (-11,-5),
            (-8,-11),
            (-3,-14),
            (0,-12),
            (3,-14),
            (8,-11),
            (11,-5),
            (10,5),
            (5,12),
            (0,14),
            (-5,12),
            (-10,5),
        ]

        self.leaf_vertices = [
            (2,-14),
            (9,-22),
            (16,-20),
            (10,-13),
        ]

        self.stem_vertices = [
            (0,-12),
            (7,-24),
        ]

    @property
    def hitbox(self):
        """
        Retângulo simples utilizado para detectar a coleta da fruta.

        A hitbox não precisa acompanhar a rotação visual.
        """

        return pygame.Rect(
            self.x_pos - 16,
            self.y_pos - 26,
            32,
            42
        )

    def create_rotation_matrix(self):
        """
        Cria manualmente a matriz homogênea de rotação.
        """

        angle_radians = math.radians(self.angle)

        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)

        return [
            [cos_angle,-sin_angle,0],
            [sin_angle, cos_angle,0],
            [0,         0,        1],
        ]

    def create_translation_matrix(self):
        """
        Cria manualmente a matriz homogênea de translação.
        """

        return [
            [1,0,self.x_pos],
            [0,1,self.y_pos],
            [0,0,1],
        ]

    def create_transformation_matrix(self):
        """
        Combina as transformações.

        A ordem é importante:
        primeiro ocorre a rotação e depois a translação.
        """

        rotation_matrix = self.create_rotation_matrix()
        translation_matrix = self.create_translation_matrix()

        return multiply_matrices(
            translation_matrix,
            rotation_matrix
        )

    def transform_vertex(self,vertex,transformation_matrix):
        """
        Multiplica um vértice pela matriz homogênea resultante.
        """

        x,y = vertex

        homogeneous_vertex = [
            [x],
            [y],
            [1],
        ]

        transformed_vertex = multiply_matrices(
            transformation_matrix,
            homogeneous_vertex
        )

        transformed_x = round(transformed_vertex[0][0])
        transformed_y = round(transformed_vertex[1][0])

        return transformed_x,transformed_y

    def transform_vertices(self,vertices,transformation_matrix):
        """
        Aplica a transformação a todos os vértices de uma figura.
        """

        return [
            self.transform_vertex(vertex,transformation_matrix)
            for vertex in vertices
        ]

    def update(self):
        """
        Atualiza a animação da fruta.

        A posição horizontal produz a translação.
        O ângulo produz a rotação.
        """

        if not self.active:
            return

        self.x_pos += self.speed

        if self.x_pos >= self.max_x:
            self.x_pos = self.max_x
            self.speed = -abs(self.speed)

        elif self.x_pos <= self.min_x:
            self.x_pos = self.min_x
            self.speed = abs(self.speed)

        self.angle = (
            self.angle + self.rotation_speed
        ) % 360

    def draw(self,screen):
        """
        Desenha a fruta usando somente os vértices transformados.
        """

        if not self.active:
            return

        transformation_matrix = self.create_transformation_matrix()

        transformed_body = self.transform_vertices(
            self.body_vertices,
            transformation_matrix
        )

        transformed_leaf = self.transform_vertices(
            self.leaf_vertices,
            transformation_matrix
        )

        transformed_stem = self.transform_vertices(
            self.stem_vertices,
            transformation_matrix
        )

        pygame.draw.line(
            screen,
            (0,180,0),
            transformed_stem[0],
            transformed_stem[1],
            3
        )

        pygame.draw.polygon(
            screen,
            (0,200,0),
            transformed_leaf
        )

        pygame.draw.polygon(
            screen,
            (255,0,0),
            transformed_body
        )

        pygame.draw.polygon(
            screen,
            (255,255,255),
            transformed_body,
            1
        )

    def collect_if_colliding(self,player_rect):
        """
        Desativa a fruta quando o Pac-Man encosta nela.

        Retorna a pontuação obtida.
        """

        if self.active and player_rect.colliderect(self.hitbox):
            self.active = False
            return 500

        return 0

    def reset(self):
        """
        Faz a fruta reaparecer na posição inicial.
        """

        self.x_pos = self.start_x
        self.y_pos = self.start_y
        self.speed = abs(self.speed)
        self.angle = 0
        self.active = True