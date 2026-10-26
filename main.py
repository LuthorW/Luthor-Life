"""Luthor Life — execute com:  python main.py

Modo de teste de cenas (não salva nada):
  python main.py --cenas            lista todas as cutscenes
  python main.py --cena lucy_6      toca uma cena direto
"""
import sys

from luthor.game import Game

if __name__ == "__main__":
    game = Game()
    if "--cenas" in sys.argv or "--cena" in sys.argv:
        from luthor import scenetest
        scenetest.setup(game, sys.argv)
    game.run()
