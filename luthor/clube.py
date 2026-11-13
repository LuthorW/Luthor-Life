"""Clube do livro do Theo: toda quinta, das 18h às 20h, na Bayside Books (Theo com 3+ corações).

O Theo espera na mesa da livraria (cadeira 10,8). Conversando com ele no horário aparece "Clube do livro".
A primeira reunião tem cena (com a Nia e o Brainy); depois, o Theo apresenta o livro da semana e a Letícia
dá a opinião dela. Cada reunião: amizade com o Theo (+ Nia e Brainy), carisma e 1h do relógio; a cada 3
reuniões o Theo dá um Livro Raro. Uma reunião por semana.
"""
import random

from . import ui, audio, habilidades
from .data import ITEMS
from .config import C_GOLD, C_GREEN, C_LILAC

DAY = 3                              # quinta-feira (g.weekday: 0 = segunda)
START, END = 18 * 60, 20 * 60
SEAT = ("books", 10, 8, "right")
MIN_HEARTS = 3
MEMBERS = ("nia", "brainy")
GIFT_EVERY = 3

BOOKS = [
    ("O Farol de Duas Luzes", "Uma faroleira que guarda o segredo da cidade inteira. Ela devia ter contado?",
     [("Devia. Segredo demais apaga o farol.", "Bem colocado. A Nia anotou isso no caderno dela."),
      ("Não. Às vezes guardar é proteger.", "Proteger ou decidir pelos outros? O Brainy já está preparando um gráfico."),
      ("Ela devia ter contado para uma pessoa só.", "O meio-termo. Diplomática como uma CEO.")]),
    ("A Cozinheira de Palermo", "Ela troca o restaurante da família por um barco de pesca. Coragem ou fuga?",
     [("Coragem. Recomeçar é a parte difícil.", "A Vittoria ia concordar. E ia reclamar da receita do capítulo 4."),
      ("Fuga, mas uma fuga bonita.", "Uma fuga bonita. Vou usar essa frase na vitrine."),
      ("As duas coisas. Todo recomeço tem um pouco de fuga.", "Isso foi profundo demais para uma quinta-feira.")]),
    ("Engrenagens de Vidro", "Um robô aprende a mentir para salvar a inventora. Ele virou humano ou virou perigoso?",
     [("Virou humano. Mentir por amor é muito humano.", "O Brainy ficou em silêncio por dez segundos. Isso é um elogio."),
      ("Perigoso. Quem mente uma vez mente de novo.", "Rígida! O Brainy aplaudiu. A Nia, nem tanto."),
      ("Virou os dois. Como todo mundo.", "Os dois. Eu gosto de respostas que não fecham.")]),
    ("Cartas para o Inverno", "Duas amigas trocam cartas por quarenta anos sem nunca se encontrar. Final feliz?",
     [("Feliz. Elas nunca deixaram de escrever.", "A Nia chorou no capítulo final. Eu também. Não conta para ninguém."),
      ("Triste. Elas deviam ter se encontrado.", "Triste e justo. Quarenta anos é muito tempo para ter medo."),
      ("Depende de quem lê.", "Resposta de quem já releu um livro e achou outro final.")]),
    ("O Mapa da Cidade Submersa", "Uma cartógrafa acha uma cidade embaixo do mar. Ela devia revelar ao mundo?",
     [("Sim. Conhecimento é para dividir.", "Uma cientista falando. O Brainy concorda com entusiasmo."),
      ("Não. Algumas coisas devem ficar quietas.", "O Seu Joca ia gostar dessa resposta. O mar também."),
      ("Só depois de proteger a cidade.", "Pensamento de quem cuida de uma fundação. Aprovado.")]),
    ("A Última Sessão do Cine Aurora", "O cinema vai fechar e o projecionista exibe o filme da vida dele. Qual seria o seu?",
     [("Um filme de detetive, com final impossível.", "Clássico. A Lucy ia pedir para assistir junto."),
      ("Uma comédia romântica. Sem vergonha nenhuma.", "Sem vergonha nenhuma! A Nia bateu palmas."),
      ("Um documentário sobre National City.", "Que bonito. Com o pôr do sol no píer, claro.")]),
    ("Sementes de Março", "Uma mãe planta uma árvore para cada filho. A mais nova não cresce. O que isso quer dizer?",
     [("Que cada um tem o seu tempo.", "Exatamente o que eu queria ouvir. A Nia disse que sonhou com isso."),
      ("Que a terra estava errada, não a árvore.", "Leitura afiada. Ninguém tinha pensado nisso."),
      ("Que ela precisava de mais atenção.", "Ou de menos. Às vezes a gente rega demais.")]),
    ("O Xadrez do Conde", "Um conde joga xadrez por cartas com um prisioneiro. Quem ganha de verdade?",
     [("O prisioneiro. Ele ganhou um amigo.", "Lindo. O Brainy pediu revanche com você depois."),
      ("O conde. Ele aprendeu a perder.", "Aprender a perder vale mais que o troféu. Concordo."),
      ("Nenhum dos dois. O jogo nunca termina.", "Resposta de enxadrista. O Brainy ficou impressionado.")]),
]


def init_state(g):
    g.clube = dict(meetings=0, week=-1, book=0)


def save_state(g):
    return {"clube": g.clube}


def load_state(g, d):
    init_state(g)
    c = d.get("clube") or {}
    g.clube["meetings"] = int(c.get("meetings", 0))
    g.clube["week"] = int(c.get("week", -1))
    g.clube["book"] = int(c.get("book", 0))


def unlocked(g):
    return g.hearts("theo") >= MIN_HEARTS or "theo_livro" in g.flags


def _week(g):
    return (g.abs_day() - 1) // 7


def open_now(g):
    return g.weekday == DAY and START <= g.minutes < END and g.clube["week"] != _week(g)


def override(g, npc):
    """Quinta à tarde o Theo espera o clube sentado à mesa da livraria."""
    if npc.key != "theo" or g.weekday != DAY or not unlocked(g):
        return
    m, x, y, d = SEAT
    a, b = START - 10, END + 10
    sch = npc.schedule
    last = None
    for e in sch:
        if e[0] <= b:
            last = e
    new_s = [e for e in sch if e[0] < a] + [(a, m, x, y, d)]
    if last is not None:
        new_s.append((b, last[1], last[2], last[3], last[4]))
    new_s += [e for e in sch if e[0] > b]
    npc.schedule = new_s


def hud_lines(g):
    if unlocked(g) and open_now(g) and g.map_name in ("books", "city"):
        return [("Clube do livro: Bayside Books, até as 20h", C_LILAC)]
    return []


def talk_options(g, npc, opts, acts):
    if npc.key != "theo" or g.map_name != "books" or not unlocked(g) or not open_now(g):
        return
    opts.append("Clube do livro")
    acts.append(lambda: meeting(g, npc))


def _reward(g):
    c = g.clube
    c["meetings"] += 1
    c["week"] = _week(g)
    c["book"] = (c["book"] + 1) % len(BOOKS)
    g.add_friendship("theo", 50)
    for k in MEMBERS:
        g.add_friendship(k, 20)
    habilidades.gain(g, "carisma", 8)
    g.minutes = min(g.minutes + 60, 25 * 60)
    for n in g.npcs.values():
        n.check_schedule(g.minutes)
    audio.sfx("page")
    g.toasts.push("Clube do livro: +amizade com o Theo, a Nia e o Brainy; +carisma", C_GREEN)
    if c["meetings"] % GIFT_EVERY == 0 and "livro" in ITEMS and g.add_item("livro"):
        g.toasts.push(f"O Theo separou um presente: {ITEMS['livro']['name']}!", C_GOLD, "livro")


def first_scene(g):
    t, q, opts = BOOKS[0]
    return dict(map="books", time=18 * 60 + 20, npc="theo", steps=[
        ("ator", "theo", 10, 8, "right"), ("sentar", "theo"),
        ("ator", "nia", 11, 10, "up"),
        ("ator", "brainy", 11, 6, "down"),
        ("ator", "player", 8, 10, "up"),
        ("camera_ja", 11, 8), ("fade_in",),
        ("legenda", "Bayside Books: o primeiro clube do livro", 2.0),
        ("andar", "player", 8, 9), ("andar", "player", 13, 9), ("andar", "player", 13, 8), ("andar", "player", 12, 8),
        ("sentar", "player"),
        ("fala", "theo", "Senhoras e senhor, declaro aberta a primeira reunião do Clube do Livro da Bayside. "
                         "Regra número um: ninguém conta o final para quem não terminou.", "happy"),
        ("fala", "brainy", "Regra número dois: eu terminei três vezes. Tenho anotações. Muitas."),
        ("fala", "nia", "Regra número três: se eu sonhar com o livro, conta como leitura.", "happy"),
        ("fala", "theo", f"Livro da semana: \"{t}\". {q}"),
        ("escolha", "O que você acha?", [(o[0], 40, o[1]) for o in opts]),
        ("emote", "nia", "estrela"),
        ("fala", "theo", "Toda quinta, das seis às oito. Chá por minha conta, opiniões fortes por conta de vocês.", "smile"),
        ("emote", "theo", "feliz"),
        ("esperar", 0.6),
        ("fade_out",),
    ])


def meeting(g, npc):
    if g.clube["meetings"] == 0:
        g.clube["book"] = 0
        g.play_scene("clube_livro", first_scene(g), on_end=lambda: _reward(g), remember=False)
        return
    t, q, opts = BOOKS[g.clube["book"] % len(BOOKS)]
    intro = random.choice(["Chá servido, cadeiras no lugar. Vamos ao livro da semana.",
                           "A Nia trouxe biscoitos e o Brainy trouxe um fichamento de doze páginas. Começamos?",
                           "Mais uma quinta, mais um livro. Eu adoro quintas."])

    def ask():
        def pick(i):
            g.push(ui.Dialog(npc.name, [opts[i][1]], g.portrait_for(npc, "happy"), subtitle="clube do livro",
                             on_close=lambda: _reward(g)))
        g.push(ui.Choice(f"\"{t}\": {q}", [o[0] for o in opts], pick))
    g.push(ui.Dialog(npc.name, [intro, f"Livro da semana: \"{t}\"."], g.portrait_for(npc, "smile"),
                     subtitle="clube do livro", on_close=ask))


from . import scenetest  # noqa: E402
scenetest.DYNAMIC["clube_livro"] = first_scene
