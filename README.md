# Pac-Man em Pygame — código base

Base inicial para um projeto educacional de recriação do Pac-Man com Python e Pygame.

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

- Setas ou `W`, `A`, `S`, `D`: movimentar o Pac-Man
- `R`: reiniciar a partida
- `Esc`: fechar o jogo

## Arquivos

- `main.py`: loop principal, eventos, pontuação, vidas e reinício
- `config.py`: constantes e cores
- `mapa.py`: mapa em grade, paredes e pastilhas
- `entidades.py`: Pac-Man, fantasmas e movimentação entre blocos

## Legenda do mapa

Dentro de `mapa.py`, cada caractere representa um elemento:

- `#`: parede
- `.`: pastilha comum
- `o`: pastilha especial
- `P`: posição inicial do Pac-Man
- `G`: posição inicial de um fantasma
- espaço: corredor vazio

## Limitações intencionais desta versão

Esta é uma base inicial. Ainda não há:

- sprites e animações;
- efeito real das pastilhas especiais;
- modo vulnerável dos fantasmas;
- inteligência individual para cada fantasma;
- teletransporte pelos túneis laterais;
- sons;
- tela inicial ou fases múltiplas.
