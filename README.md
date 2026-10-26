<div align="center">

<img src="docs/img/logo.png" width="96" alt="Logo da Luthor Corp">

# Luthor Life

**Uma vida executiva em National City**

Simulação de vida em pixel art, no estilo Stardew Valley, feita em Python.

[![Site](https://img.shields.io/badge/site-luthorw.github.io-8a00e6?style=for-the-badge)](https://luthorw.github.io/Luthor-Life/)
[![Baixar](https://img.shields.io/badge/baixar-.zip-2fbf63?style=for-the-badge)](https://github.com/LuthorW/Luthor-Life/archive/refs/heads/main.zip)
[![Python](https://img.shields.io/badge/python-3.10+-b84cff?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![pygame-ce](https://img.shields.io/badge/pygame--ce-2.4+-6ee78c?style=for-the-badge)](https://pyga.me/)

<img src="docs/img/title.png" width="820" alt="Tela de título do Luthor Life">

<img src="docs/img/chars/leticia.png" height="72"> <img src="docs/img/chars/lucy.png" height="72"> <img src="docs/img/chars/sam.png" height="72"> <img src="docs/img/chars/brainy.png" height="72"> <img src="docs/img/chars/vittoria.png" height="72"> <img src="docs/img/chars/jess.png" height="72"> <img src="docs/img/chars/cat.png" height="34"> <img src="docs/img/chars/milany.png" height="72"> <img src="docs/img/chars/nia.png" height="72"> <img src="docs/img/chars/rafa.png" height="72"> <img src="docs/img/chars/dog.png" height="34"> <img src="docs/img/chars/joca.png" height="72">

### [🌐 Conheça o jogo no site](https://luthorw.github.io/Luthor-Life/)

</div>

---

## Sobre

Você é **Letícia Luthor**, CEO da Luthor Corp. Lance projetos no laboratório, pesque no píer, cultive a horta
do terraço, adote um bichinho e encontre o amor numa cidade que vive com você, da manhã até tarde da noite.

Cada dia tem manhã, tarde e noite. A cidade muda de rotina, os moradores entram e saem dos lugares, e você
decide como gastar a sua energia.

## O que fazer

<table>
<tr>
<td width="50%"><img src="docs/img/lab.png" alt="Laboratório"></td>
<td width="50%"><img src="docs/img/terrace.png" alt="Terraço com horta"></td>
</tr>
<tr>
<td><b>🧪 Laboratório P&amp;D</b><br>Compre propostas, trabalhe nos projetos todo dia, lance produtos e acompanhe a ação LCORP.</td>
<td><b>🌱 Horta e bichinho</b><br>Plante no terraço da cobertura, regue, colha e adote um gato ou um cachorro.</td>
</tr>
<tr>
<td><img src="docs/img/fishing.png" alt="Pescaria"></td>
<td><img src="docs/img/karaoke.png" alt="Karaokê"></td>
</tr>
<tr>
<td><b>🎣 Pescaria</b><br>13 espécies no mar e no lago, que mudam com o trimestre, a hora e a chuva.</td>
<td><b>🎤 Karaokê e fliperama</b><br>À noite no Noonan's: acerte as setas no ritmo e ganhe gorjetas.</td>
</tr>
<tr>
<td><img src="docs/img/cutscene.png" alt="Cutscene"></td>
<td><img src="docs/img/hospital.png" alt="Conti Moretti Hospitais"></td>
</tr>
<tr>
<td><b>💜 Romance e cutscenes</b><br>Lucy Williams ou Vittoria Ricci: encontros às 20h, eventos de coração e cenas especiais.</td>
<td><b>🏥 Conti Moretti Hospitais</b><br>12 especialidades, médicas com rotina própria e bônus diferentes a cada consulta.</td>
</tr>
</table>

E ainda: **cozinha** com receitas secretas, **coletáveis** na praia e no parque, **Cine National**, **aquário**,
**livros com bônus permanentes**, **pedidos** da cidade e **centenas de falas** que não se repetem.

## Como jogar

1. Instale o [Python](https://www.python.org/downloads/) 3.10 ou mais novo. No Windows, marque **Add Python to PATH**.
2. [Baixe o jogo](https://github.com/LuthorW/Luthor-Life/archive/refs/heads/main.zip) e extraia, ou clone:
   ```bash
   git clone https://github.com/LuthorW/Luthor-Life.git
   ```
3. No Windows, dê dois cliques em **`Jogar.bat`**. Em qualquer sistema:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

O jogo salva sozinho toda noite, quando você dorme (em `saves/save.json`).

## Controles

| Tecla | Ação |
|---|---|
| `W` `A` `S` `D` / setas | Andar (`Shift` = devagar) |
| `E` / `Espaço` / clique | Interagir, conversar, trabalhar, pescar |
| `1`–`0`, `-`, `=` / roda do mouse | Escolher item da barra |
| `F` / botão direito | Comer, beber ou ler |
| `I` / `Tab` | Mochila |
| `Esc` | Menu: objetivos, relacionamentos, coleções e cenas |
| setas ou `D` `F` `J` `K` | Karaokê |
| `F11` | Tela cheia |

## Dicas

- **Começo:** Relatórios de Mercado são baratos e ficam prontos em 2 dias. O Seu Joca dá uma vara de pesca no píer.
- **Ações:** vender produtos do laboratório faz a LCORP subir (cerca de $1 a cada $800 vendidos numa noite).
- **Romance:** rosas aos 8 corações para namorar, pingente aos 10 para morarem juntas.
- **Conversas:** cada pessoa conversa uma vez por período (manhã, tarde e noite).
- **Durma antes das 2h**, ou você acorda no Conti Moretti com uma conta para pagar.

## Estrutura do projeto

```
Luthor-Life/
├── main.py            # inicia o jogo
├── Jogar.bat          # atalho para Windows
├── assets/            # fonte, logos e retratos
├── docs/              # site do jogo (GitHub Pages)
└── luthor/
    ├── game.py        # núcleo do jogo
    ├── world.py       # mapas de National City (desenhados em texto)
    ├── art.py         # toda a pixel art, gerada por código
    ├── characters.py  # personagens, rotinas, presentes e eventos
    ├── dialogue.py    # falas por período, clima, lugar e amizade
    ├── activities.py  # horta, coletáveis, bichinho, karaokê e cinema
    ├── hospital.py    # Conti Moretti Hospitais
    ├── doctors.py     # as médicas e suas rotinas
    ├── crowd.py       # moradores que circulam pela cidade
    ├── cutscenes.py   # motor de cutscenes
    ├── minigames.py   # pesca, fliperama, fogão e mochila
    └── data.py        # itens, peixes, receitas, livros e lojas
```

Para trocar os retratos, coloque as fotos em `assets/portraits/` e indique o nome do arquivo em
`luthor/characters.py` (campo `portrait`).

## Créditos

Jogo feito por uma pessoa que está cansada da vida real. Personagens e marcas inspirados em obras de terceiros pertencem 
aos seus respectivos donos. Fonte [Jersey 10](https://fonts.google.com/specimen/Jersey+10) sob a SIL Open Font License.

<div align="center"><sub>Feito com 💜 e muitos pixels em National City.</sub></div>
