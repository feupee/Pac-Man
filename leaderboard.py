import json
from pathlib import Path

import config

LEADERBOARD_PATH = Path(__file__).with_name(config.LEADERBOARD_FILE)


def load_leaderboard():
    """
    Carrega o leaderboard salvo em disco.

    Caso o arquivo ainda não exista ou esteja corrompido,
    devolve uma lista vazia para que o jogo continue funcionando.
    """
    try:
        with open(LEADERBOARD_PATH,'r',encoding='utf-8') as file:
            leaderboard = json.load(file)
    except (FileNotFoundError,json.JSONDecodeError,OSError):
        return []

    if not isinstance(leaderboard,list):
        return []

    valid_entries = []

    for entry in leaderboard:
        if not isinstance(entry,dict):
            continue

        name = str(
            entry.get('name',config.PLAYER_DEFAULT_NAME)
        ).strip()

        score = entry.get('score',0)

        if not isinstance(score,int):
            continue

        valid_entries.append({
            'name': name[:config.PLAYER_NAME_MAX_LENGTH] or config.PLAYER_DEFAULT_NAME,
            'score': max(0,score)
        })

    valid_entries.sort(
        key=lambda entry: entry['score'],
        reverse=True
    )

    return valid_entries[:config.LEADERBOARD_SIZE]


def save_leaderboard(leaderboard):
    """
    Salva o leaderboard em formato JSON.
    """
    with open(LEADERBOARD_PATH,'w',encoding='utf-8') as file:
        json.dump(
            leaderboard,
            file,
            ensure_ascii=False,
            indent=4
        )


def add_score(leaderboard,player_name,score):
    """
    Adiciona uma nova pontuação, ordena o ranking e mantém
    somente as cinco melhores posições.
    """
    updated_leaderboard = leaderboard + [
        {
            'name': player_name,
            'score': score
        }
    ]

    updated_leaderboard.sort(
        key=lambda entry: entry['score'],
        reverse=True
    )

    updated_leaderboard = updated_leaderboard[
        :config.LEADERBOARD_SIZE
    ]

    save_leaderboard(updated_leaderboard)

    return updated_leaderboard