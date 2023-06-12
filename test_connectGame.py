import pytest
from connectGame import gameObject


@pytest.fixture
def game():
    game = gameObject(height=5, length=8)
    return game


@pytest.fixture
def started_game(game):
    started_game = game.start_game()
    game = started_game
    return game


def test_func_fast():
    p = "penis"
    pass


@pytest.mark.smoke
def test_game_defaults(game):

    assert game.inProgress == False
    assert game.winner == False
    assert game.playerCumulative == {1: 0, 2: 0}
    assert game.colors == {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}


@pytest.mark.smoke
def test_more_default_params(game):
    assert game.drawBoardTurn == False
    assert game.drawBoardGameOver == True
    assert game.comPort == "COM3"
    assert game.commsArduino == False


@pytest.mark.smoke
def test_game_height_set(game):
    assert game.height == 5


@pytest.mark.smoke
def test_game_length_set(game):
    assert game.length == 8


@pytest.mark.smoke
def test_game_area(started_game):
    assert len(game.board.keys()) == 40


@ pytest.mark.smoke
def start_game_defaults(started_game):
    print(started_game)
    assert game.inProgress == True
    assert game.winner == False
    assert game.currentPlayer in [1, 2]
    assert game.lastTurn == 0
    assert game.currentTurn == 1
    assert game.lastMove == None
    assert game.currentMove == None
