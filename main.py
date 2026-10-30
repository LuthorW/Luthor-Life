"""Luthor Life — execute com:  python main.py

Modos de teste (não salvam nada):
  python main.py --cenas            lista todas as cutscenes
  python main.py --cena lucy_6      toca uma cena direto
  python main.py --teste            seu jogo salvo + painel para mudar dia, horário, estação e clima (F6)
"""
import sys

from luthor.game import Game

if __name__ == "__main__":
    game = Game()
    if "--cenas" in sys.argv or "--cena" in sys.argv:
        from luthor import scenetest, timetest
        scenetest.setup(game, sys.argv)
        timetest.install(game)                 # F6 também muda dia/horário no teste de cenas
    elif "--teste" in sys.argv:
        from luthor import timetest
        timetest.setup(game)
    game.run()
