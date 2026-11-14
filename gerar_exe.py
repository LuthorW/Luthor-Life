"""Monta o executável do jogo para Windows: dist/LuthorLife.exe (um arquivo só, sem precisar de Python).

    py gerar_exe.py

Precisa do PyInstaller (py -m pip install pyinstaller). Vão para dentro do .exe só os arquivos do jogo que estão no
git: o código (luthor/), a fonte, os retratos e os logos. A pasta assets/portraits_hd (cópias antigas) fica de fora.
No .exe o jogo salvo fica em %APPDATA%\\Luthor Life\\saves (veja luthor/config.py, FROZEN).
Para publicar: suba dist/LuthorLife.exe numa versão (release) do GitHub; o botão "Baixar o jogo" do site e do
README aponta para releases/latest/download/LuthorLife.exe.
"""
import os
import sys

import PyInstaller.__main__

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")


def data(src, dest):
    return ["--add-data", f"{os.path.join(ROOT, src)}{os.pathsep}{dest}"]


args = [os.path.join(ROOT, "main.py"),
        "--name", "LuthorLife",
        "--onefile", "--windowed", "--noconfirm", "--clean",
        "--icon", os.path.join(A, "favicon.ico"),
        "--distpath", os.path.join(ROOT, "dist"),
        "--workpath", os.path.join(ROOT, "build", "pyinstaller"),
        "--specpath", os.path.join(ROOT, "build"),
        # nada disso é usado pelo jogo (deixa o .exe menor)
        "--exclude-module", "numpy", "--exclude-module", "tkinter", "--exclude-module", "unittest",
        "--exclude-module", "pydoc", "--exclude-module", "PIL"]
args += data("assets/fonts", "assets/fonts")
args += data("assets/portraits", "assets/portraits")
for f in ("catco.png", "cmh.png", "lexcorp.png", "favicon.ico"):
    args += data(f"assets/{f}", "assets")

if __name__ == "__main__":
    PyInstaller.__main__.run(args)
    exe = os.path.join(ROOT, "dist", "LuthorLife.exe")
    if os.path.exists(exe):
        print(f"\nPronto: {exe} ({os.path.getsize(exe) / 1e6:.0f} MB)")
    else:
        sys.exit("O .exe não foi gerado: veja as mensagens acima.")
