# Pac-Man em Pygame

Projeto educacional de recriação do Pac-Man com Python e Pygame.

## Requisitos

- Python 3.10 ou superior
- Pygame

Instale a biblioteca:

```bash
pip install pygame
```

## Como executar

Abra o terminal dentro da pasta do projeto e rode:

```bash
python main.py
```

## Controles

- `Enter` ou `Espaço`: iniciar a partida na tela inicial
- Setas direcionais: movimentar o Pac-Man
- `R`: reiniciar a partida
- `Esc`: fechar o jogo

## Interface

A janela foi separada em três áreas:

- área superior reservada para pontuação e indicadores;
- área central ocupada pelo tabuleiro;
- área inferior reservada para vidas e novos elementos de interface.

As alturas podem ser ajustadas no arquivo `config.py` por meio de:

```python
TOP_UI_HEIGHT = 80
BOTTOM_UI_HEIGHT = 90
```

## Fonte personalizada do menu

O arquivo `config.py` utiliza o caminho convencional:

```python
FONT_PATH_MENU = 'fonts/Joystix_W00_Proportional.ttf'
```

Coloque a fonte nessa pasta para utilizá-la. Caso o arquivo não esteja disponível, o jogo utiliza automaticamente uma fonte alternativa.

## Arquivos principais

- `main.py`: loop principal, tela inicial, desenho do tabuleiro e interface;
- `config.py`: dimensões, caminhos, velocidades e demais constantes;
- `board.py`: mapa em grade;
- `pacman.py`: comportamento do jogador;
- `ghost.py`: comportamento dos fantasmas.

## Dimensionamento automático da janela

O jogo mantém uma resolução lógica completa para preservar o mapa, as colisões e as áreas de interface superior e inferior. A janela visível é reduzida automaticamente para caber no monitor.

A proporção máxima ocupada na tela pode ser alterada no arquivo `config.py`:

```python
DISPLAY_MAX_USAGE = 0.85
```

Por exemplo, use `0.75` para uma janela menor. A janela também pode ser redimensionada manualmente; o quadro é ajustado proporcionalmente com barras pretas quando necessário.

## Fonte arcade personalizada

Para utilizar a fonte arcade, coloque o arquivo `Joystix_W00_Proportional.ttf` dentro da pasta `fonts/`. Sem esse arquivo, uma fonte alternativa é carregada automaticamente.
