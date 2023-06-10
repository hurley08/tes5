import pytest
from connectGame import *


def test_func_fast():
    game = gameObject()
    pass


@pytest.mark.smoke
def test_game_defaults():
    game = gameObject(height=5, length=8)

    assert game.inProgress == False
    assert game.winner == False
    assert game.playerCumulative == {1: 0, 2: 0}
    assert game.colors == {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}


@pytest.mark.smoke
def test_game_height_set():
    game = gameObject(height=5, length=8)
    assert game.height == 5


@pytest.mark.smoke
def test_game_length_set():
    game = gameObject(height=5, length=8)
    assert game.length == 8
