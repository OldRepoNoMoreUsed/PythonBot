import pytest

from Bot import MainAlonso


@pytest.fixture()
def bot():
    return MainAlonso.BotAlonso()


def test(bot):
    bot.fonction_pour_prouver_que_je_peux_faire_des_test()
    assert 1 == bot.fonction_pour_prouver_que_je_peux_faire_des_test()
