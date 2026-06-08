def create_hitbox(center_x,center_y,width,height):
    """
    Cria uma hitbox retangular a partir do centro e das dimensões.

    A hitbox é representada manualmente por uma tupla:
    (posição_x,posição_y,largura,altura).
    """

    return (
        center_x - width // 2,
        center_y - height // 2,
        width,
        height
    )


def rectangles_collide(hitbox_a,hitbox_b):
    """
    Verifica manualmente se dois retângulos possuem uma área em comum.

    Não utiliza funções prontas de detecção. A colisão existe quando os
    intervalos dos retângulos se sobrepõem simultaneamente nos eixos X e Y.
    """

    x_a,y_a,width_a,height_a = hitbox_a
    x_b,y_b,width_b,height_b = hitbox_b

    overlap_x = (
        x_a < x_b + width_b
        and x_a + width_a > x_b
    )

    overlap_y = (
        y_a < y_b + height_b
        and y_a + height_a > y_b
    )

    return overlap_x and overlap_y
