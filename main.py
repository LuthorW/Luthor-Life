"""Luthor Life — execute com:  python main.py

Modos de teste (não salvam nada):
  python main.py --cenas            lista todas as cutscenes
  python main.py --cena lucy_6      toca uma cena direto
  python main.py --teste            seu jogo salvo + painel para mudar dia, horário, estação e clima (F6)
"""
import sys

from luthor.game import Game

def smoke_test(path):
    """--conferir foto.png: abre o jogo sem janela, passa pela tela de título até a cidade e salva uma foto.
    Serve para testar o .exe (gerar_exe.py) sem jogar; não salva nada."""
    import os
    import pygame
    game = Game()
    game.save = lambda *a, **k: None
    enter = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)]
    for i in range(900):
        game.step(1 / 60, enter if i % 60 == 30 and game.scene != "play" else [])
    pygame.image.save(game.screen, path)
    if sys.stdout:                             # no .exe sem console não há onde imprimir
        print("ok", game.scene, os.path.getsize(path))


if __name__ == "__main__":
    if "--conferir" in sys.argv:
        smoke_test(sys.argv[sys.argv.index("--conferir") + 1])
        sys.exit(0)
    game = Game()
    if "--cenas" in sys.argv or "--cena" in sys.argv:
        from luthor import scenetest, timetest
        scenetest.setup(game, sys.argv)
        timetest.install(game)                 # F6 também muda dia/horário no teste de cenas
    elif "--teste" in sys.argv:
        from luthor import timetest
        timetest.setup(game)
    game.run()
