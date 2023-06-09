import pytest
from connectGame import *


def test_func_fast():
    pass


@pytest.mark.smoke
def test_game_defaults():
    ame = connectGame.gameObject(height=5, length=8)
    assert game.inProgress() == False


@pytest.mark.smoke
def test_game_height_set():
    ame = connectGame.gameObject(height=5, length=8)
    assert game.height == 5


@pytest.mark.smoke
def test_game_length_set():
    ame = connectGame.gameObject(height=5, length=8)
    assert game.length == 8
