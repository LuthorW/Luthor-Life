"""História da Luthor Corp: os tios da Letícia (Conrad e Edmund Luthor) tentam tirar ela da presidência.

São cinco capítulos. Cada um tem uma cena num lugar e horário (linha no HUD) e, depois dela, um objetivo:

  1. A carta dos tios ........ sede, 8h-12h ........ objetivo: lançar 5 produtos no laboratório
  2. Visita inesperada ....... frente da sede, 9h-13h  objetivo: faturar $6.000 no total
  3. O espião ................ laboratório, 19h-23h .. objetivo: ação LCORP a $110
  4. O dossiê falso .......... CatCo, 13h-17h ...... objetivo: 4 corações com Sam, Brainy, Jess e Ian
  5. O conselho ............. sala de reuniões, 10h-14h — fim: os tios vendem as ações

Prêmio do fim: produtos valem 10% a mais (flag luthor_livre), $3.000 de dividendos e amizade com a equipe.
A mesa da sala de reuniões da sede (escritorio.py) mostra o capítulo atual.
"""
import pygame

from . import art, ui, audio, world, cutscenes
from .art import new, R, P, shade
from .characters import look, SKIN_L, SKIN_M, SKIN_T
from .cutscenes import SCENES, Cutscene
from .config import SCREEN_W, SCREEN_H, HEART_POINTS, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_PINK

# --- personagens que só aparecem nas cenas -------------------------------------
EXTRAS = {
    "tio_conrad": dict(name="Conrad Luthor", role="Tio da Letícia · acionista",
                       look=dict(look((186, 186, 192), SKIN_L, (38, 38, 46), (230, 230, 236), (38, 38, 46), (24, 22, 26),
                                      "short"), outfit="blazer", glasses=True, height=1)),
    "tio_edmund": dict(name="Edmund Luthor", role="Tio da Letícia · acionista",
                       look=dict(look((120, 116, 120), SKIN_L, (70, 40, 46), (236, 226, 210), (46, 40, 44), (30, 24, 24),
                                      "short"), outfit="blazer", beard="full", beard_color=(170, 166, 170))),
    "rojas": dict(name="Andrea Rojas", role="Amiga da Letícia · conselheira, mora em Metrópolis", portrait="andrea",
                  look=dict(look((40, 30, 34), SKIN_T, (170, 40, 56), (240, 230, 232), (40, 34, 44), (30, 24, 30), "long"),
                            outfit="blazer")),
    "hamilton": dict(name="Sr. Hamilton", role="Conselheiro",
                     look=dict(look((236, 236, 240), SKIN_M, (60, 70, 96), (236, 236, 240), (50, 54, 70), (30, 30, 34),
                                    "short"), outfit="blazer", glasses=True)),
    "espiao": dict(name="Rick", role="Funcionário temporário",
                   look=dict(look((150, 100, 60), SKIN_L, (120, 130, 140), (230, 230, 230), (60, 70, 90), (40, 40, 44),
                                  "short"))),
}

_orig_look_for = cutscenes.look_for


def _look_for(key, map_name, season=None):
    if key in EXTRAS:
        return EXTRAS[key]["look"]
    return _orig_look_for(key, map_name, season)


cutscenes.look_for = _look_for
_orig_speaker = Cutscene.speaker


def _speaker(self, name, mood=None):
    if name in EXTRAS:
        e = EXTRAS[name]
        from .game import MOOD_ALIASES               # retrato desenhado (assets/portraits/<portrait>*.png), se houver
        fname = art.portrait_file(e.get("portrait"), MOOD_ALIASES.get(mood, mood))
        return e["name"], art.portrait(fname, e["look"], art.PORTRAIT_SIZE), e["role"]
    return _orig_speaker(self, name, mood)


Cutscene.speaker = _speaker

# --- capítulos -------------------------------------------------------------------
CHAPTERS = [
    dict(key="historia_1", title="A carta dos tios", map="hq", hours=(8, 12), where="na sede da Luthor Corp"),
    dict(key="historia_2", title="Visita inesperada", map="city", hours=(9, 13), where="na frente da sede",
         spot=(21, 17)),
    dict(key="historia_3", title="O espião", map="hq", hours=(19, 23), where="no laboratório da sede"),
    dict(key="historia_4", title="O dossiê falso", map="catco", hours=(13, 17), where="na redação da CatCo"),
    dict(key="historia_5", title="O conselho", map="hq", hours=(10, 14), where="na sala de reuniões da sede"),
]
TITLES = {c["key"]: f"Luthor Corp: {c['title'].lower()}" for c in CHAPTERS}
TEAM4 = ("sam", "brainy", "jess", "ian")


def goal(g, ch):
    """(texto, cumprido) do objetivo depois do capítulo ch (1..4)."""
    if ch == 1:
        n = g.stats["launched"]
        return f"Lance 5 produtos no laboratório ({min(n, 5)}/5)", n >= 5
    if ch == 2:
        e = g.stats["earned"]
        return f"Fature $6.000 no total (${min(e, 6000):,})".replace(",", "."), e >= 6000
    if ch == 3:
        return f"Leve a ação LCORP a $110 (hoje ${g.stock:.2f})".replace(".", ",", 1), g.stock >= 110
    if ch == 4:
        n = sum(1 for k in TEAM4 if g.hearts(k) >= 4)
        return f"Aliados: 4 corações com Sam, Brainy, Jess e Ian ({n}/4)", n >= 4
    return "", False


def init_state(g):
    g.historia = dict(ch=0)
    apply(g)


def save_state(g):
    return {"historia": g.historia}


def load_state(g, d):
    init_state(g)
    h = d.get("historia") or {}
    g.historia["ch"] = max(0, min(len(CHAPTERS), int(h.get("ch", 0))))


def done(g):
    return g.historia["ch"] >= len(CHAPTERS)


def next_chapter(g):
    """Capítulo liberado e ainda não visto (ou None)."""
    ch = g.historia["ch"]
    if ch >= len(CHAPTERS):
        return None
    if ch == 0:
        return CHAPTERS[0] if g.abs_day() >= 2 else None
    return CHAPTERS[ch] if goal(g, ch)[1] else None


def hud_lines(g):
    ch = g.historia["ch"]
    nxt = next_chapter(g)
    if nxt:
        a, b = nxt["hours"]
        return [(f"Luthor Corp: {nxt['title']} ({nxt['where']}, {a}h-{b}h)", C_GOLD)]
    if 1 <= ch < len(CHAPTERS):
        return [(f"Luthor Corp: {goal(g, ch)[0]}", (236, 200, 120))]
    return []


def check(g):
    c = next_chapter(g)
    if not c or g.map_name != c["map"]:
        return False
    a, b = c["hours"]
    if not a * 60 <= g.minutes <= b * 60:
        return False
    if c.get("spot"):
        tx, ty = g.player.tile
        if abs(tx - c["spot"][0]) > 8 or abs(ty - c["spot"][1]) > 5:
            return False
    idx = CHAPTERS.index(c)

    def end():
        g.historia["ch"] = idx + 1
        if idx + 1 == len(CHAPTERS):
            g.flags.add("luthor_livre")
            g.money += 3000
            for k in TEAM4:
                g.add_friendship(k, 40)
            audio.sfx("reward")
            g.toasts.push("A Luthor Corp é sua, sem tios: produtos valem 10% a mais e $3.000 de dividendos!", C_GOLD)
            g.player.place_tile(14, 16, "up")
        else:
            g.toasts.push(f"Luthor Corp, capítulo {idx + 1}: {goal(g, idx + 1)[0]}", C_GOLD)
        for npc in g.npcs.values():
            npc.snap_to_schedule(g.minutes)
    sc = dict(SCENES[c["key"]], time=g.minutes)
    g.play_scene(c["key"], sc, on_end=end)
    return True


def sell_mult(g, item):
    from .data import ITEMS
    return 1.1 if "luthor_livre" in g.flags and ITEMS[item]["kind"] == "product" else 1.0


# --- mesa da sala de reuniões -------------------------------------------------
def apply(g):
    """A reunião do conselho é na sala de reuniões da sede (escritorio.furnish_reunioes): nada a montar."""
    return


def object_label(g, o):
    if o.kind == "mesa_reuniao":
        return "Mesa de reuniões"
    return None


def use_object(g, o):
    if o.kind != "mesa_reuniao":
        return False
    audio.sfx("page")

    def draw(surf, rect):
        y = rect.y + 70
        ch = g.historia["ch"]
        for i, c in enumerate(CHAPTERS):
            if i < ch:
                col, tag = C_GREEN, "visto"
            elif i == ch:
                col, tag = C_GOLD, "agora"
            else:
                col, tag = C_MUTED, ""
            name = c["title"] if i <= ch else "???"
            ui.text(surf, f"Capítulo {i + 1}: {name}", (rect.x + 30, y), 20, col, bold=i == ch)
            if tag:
                ui.text(surf, tag, (rect.right - 30, y + 2), 16, col, right=True)
            y += 32
        y += 10
        nxt = next_chapter(g)
        if done(g):
            msg = "A Luthor Corp é sua, sem tios. Produtos valem 10% a mais."
        elif nxt:
            msg = f"Próxima cena: {nxt['title']}, {nxt['where']}, entre {nxt['hours'][0]}h e {nxt['hours'][1]}h."
        elif ch == 0:
            msg = "A Sam quer falar com você amanhã de manhã, na sede."
        else:
            msg = "Objetivo: " + goal(g, ch)[0]
        for ln in ui.wrap(msg, 18, rect.w - 60):
            ui.text(surf, ln, (rect.x + 30, y), 18, C_TEXT)
            y += 24
        return y
    g.push(ui.InfoPanel("História da Luthor Corp", draw))
    return True


# --- cenas -----------------------------------------------------------------------
SCENES["historia_1"] = dict(map="hq", time=9 * 60, npc="sam", steps=[
    ("ator", "sam", 4, 6, "up"), ("ator", "player", 5, 9, "up"),
    ("camera_ja", 4, 5), ("fade_in",),
    ("legenda", "História da Luthor Corp: capítulo 1", 2.2),
    ("andar", "player", 5, 3), ("andar", "player", 4, 3), ("virar", "player", "down"),
    ("fala", "sam", "Luthor, senta. Chegou uma carta registrada. Do escritório dos seus tios.", "bad"),
    ("andar", "player", 3, 3), ("sentar", "player"),
    ("narra", "Papel timbrado, letra caprichada. Assinado: Conrad e Edmund Luthor."),
    ("fala", "sam", "Eles têm 30% das ações. Querem uma reunião extraordinária do conselho para \"avaliar a gestão\"."),
    ("fala", "sam", "Tradução: tirar você da cadeira."),
    ("emote", "player", "raiva"),
    ("fala", "player", "Eles esperaram meu pai morrer para tentar. Agora estão esperando eu cair."),
    ("fala", "sam", "Então a gente não cai. O conselho vota com números: produtos, receita, ação em alta. E com gente do nosso lado."),
    ("escolha", "O que dizer?", [
        ("Vamos mostrar resultado.", 50, "Isso. Primeiro passo: cinco produtos lançados. O laboratório é seu."),
        ("Eu não tenho medo deles.", 40, "Eu sei. Eu tenho medo por você, então a gente se completa."),
        ("E se eles tiverem razão?", 30, "Não têm. Eu fiz as contas. Duas vezes."),
    ]),
    ("fala", "sam", "Eu estou com você. Sempre estive.", "smile"),
    ("esperar", 0.6), ("fade_out",),
])

SCENES["historia_2"] = dict(map="city", time=10 * 60, npc="sam", steps=[
    ("ator", "tio_conrad", 21, 17, "down"), ("ator", "tio_edmund", 20, 16, "right"), ("ator", "player", 26, 17, "left"),
    ("camera_ja", 22, 17), ("fade_in",),
    ("legenda", "Capítulo 2: visita inesperada", 2.2),
    ("andar", "player", 23, 17),
    ("virar", "tio_conrad", "right"),
    ("fala", "tio_conrad", "Letícia. Você cresceu. Tem os olhos do Alexander. Só os olhos."),
    ("fala", "tio_edmund", "Viemos conhecer a sede. Achamos que ela vai precisar de alguém experiente quando... bem.", "smile"),
    ("fala", "player", "A sede está bem cuidada. Vocês podem admirar daqui de fora."),
    ("fala", "tio_conrad", "Sempre teimosa. Seu pai também era. E terminou sozinho, num quarto de hospital, cercado de advogados."),
    ("emote", "player", "raiva"),
    ("fala", "tio_edmund", "E aquela jornalista? A de Gotham. Ouvimos dizer que ela mora em National City agora."),
    ("fala", "player", "Cheguem perto dela e vocês vão conhecer a Luthor que o meu pai criou de verdade."),
    ("emote", "tio_edmund", "gota"),
    ("fala", "tio_conrad", "Nos vemos no conselho, sobrinha."),
    ("andar_", "tio_conrad", 14, 17), ("esperar", 0.9), ("andar", "tio_edmund", 20, 17), ("andar", "tio_edmund", 15, 17),
    ("sai", "tio_conrad"), ("sai", "tio_edmund"),
    ("narra", "Suas mãos estão tremendo. Mas você não desviou o olhar nenhuma vez."),
    ("ator", "jess", 21, 16, "down"),
    ("andar", "jess", 22, 17), ("virar", "jess", "right"),
    ("fala", "jess", "Chefe! Eu vi pela janela. Você está bem? Quer um chá? Um advogado? Os dois?", "bad"),
    ("fala", "player", "Estou bem, Jess. Marca uma reunião com a Sam. Vamos precisar de dinheiro em caixa."),
    ("fala", "jess", "Marcado. E chá também. Não discute.", "smile"),
    ("esperar", 0.5), ("fade_out",),
])

SCENES["historia_3"] = dict(map="hq", time=21 * 60, npc="brainy", steps=[
    ("ator", "espiao", 11, 2, "down"), ("ator", "brainy", 12, 3, "left"), ("ator", "player", 17, 10, "up"),
    ("camera_ja", 13, 5), ("fade_in",),
    ("legenda", "Capítulo 3: o espião", 2.2),
    ("andar", "player", 17, 5), ("andar", "player", 17, 3), ("andar", "player", 14, 3), ("virar", "player", "left"),
    ("virar", "brainy", "right"),
    ("fala", "brainy", "CEO. Desculpe o horário. Eu deixei uma armadilha no Terminal P&D. Ela pegou alguém."),
    ("fala", "espiao", "Eu só ia copiar uns arquivos! Me pagaram! Eu juro que não sabia para quem era!", "bad"),
    ("fala", "brainy", "Eu sei para quem era. O pen drive dele tem uma pasta chamada \"Para C. e E. Luthor\". Pouco discreto."),
    ("emote", "player", "exclamacao"),
    ("escolha", "O que dizer?", [
        ("Ele vai contar tudo isso para o conselho. Por escrito.", 60,
         "Vai. E eu guardei os registros. Três cópias. Uma em papel, para os mais antiquados."),
        ("Chama a segurança.", 40, "Já chamei. Estão subindo com cara de quem perdeu o jantar."),
        ("Quanto te pagaram?", 30, "Dois mil. Ele vendeu nossos projetos por dois mil. Ofensivo, na verdade."),
    ]),
    ("andar", "espiao", 11, 6), ("andar", "espiao", 17, 6), ("sai", "espiao"),
    ("fala", "brainy", "Eles querem nossos projetos para dizer ao conselho que o laboratório não é seu."),
    ("fala", "brainy", "Mas o laboratório é seu. E meu. E da Sam. É nosso.", "smile"),
    ("esperar", 0.5), ("fade_out",),
])

SCENES["historia_4"] = dict(map="catco", time=15 * 60, npc="lucy", steps=[
    ("ator", "lucy", 16, 8, "right"), ("ator", "nia", 20, 8, "left"), ("ator", "player", 11, 13, "up"),
    ("camera_ja", 17, 9), ("fade_in",),
    ("legenda", "Capítulo 4: o dossiê falso", 2.2),
    ("andar", "player", 12, 9), ("andar", "player", 18, 9), ("virar", "player", "up"),
    ("virar", "lucy", "down"), ("virar", "nia", "down"),
    ("fala", "nia", "Letícia! Chegou isso na redação hoje de manhã. Sem remetente."),
    ("narra", "Um dossiê grosso: \"Luthor Corp esconde falhas graves nos projetos\". Fotos borradas, carimbos tortos."),
    ("fala", "lucy", "Parece sério. Até você ler com atenção. Metade das datas é de antes do laboratório existir."),
    ("fala", "lucy", "Um furo desses salva o mês de qualquer repórter. Mas eu não publico nada sem ouvir o outro lado."),
    ("fala", "lucy", "Principalmente quando o outro lado é você.", "shy"),
    ("fala", "nia", "E eu sonhei com isso, sabia? Um papel pegando fogo. Achei que era só fome.", "smile"),
    ("escolha", "O que dizer?", [
        ("Obrigada por me procurar primeiro.", 70,
         "Sempre. É assim que se faz jornalismo. E é assim que se faz com quem importa."),
        ("Publiquem a verdade: quem mandou o dossiê.", 60,
         "Já estou nisso. O carimbo é de um escritório de advocacia de Gotham. Adivinha de quem."),
        ("Isso é coisa dos meus tios.", 50, "Eu imaginei. Eu lembro bem deles. Dessa vez eu não vou ficar quieta."),
    ]),
    ("fala", "nia", "A matéria sai sexta: \"Quem tem medo da Luthor Corp?\". Spoiler: os tios.", "happy"),
    ("esperar", 0.5), ("fade_out",),
])

SCENES["historia_5"] = dict(map="hq", time=11 * 60, npc="sam", steps=[
    ("ator", "jess", 28, 4, "down"), ("ator", "brainy", 29, 4, "down"), ("ator", "rojas", 30, 4, "down"),
    ("ator", "sam", 31, 4, "down"),
    ("ator", "ian", 28, 7, "up"), ("ator", "hamilton", 29, 7, "up"), ("ator", "tio_edmund", 30, 7, "up"),
    ("ator", "tio_conrad", 31, 7, "up"),
    ("sentar", "jess"), ("sentar", "brainy"), ("sentar", "rojas"), ("sentar", "sam"),
    ("sentar", "ian"), ("sentar", "hamilton"), ("sentar", "tio_edmund"), ("sentar", "tio_conrad"),
    ("ator", "player", 29, 10, "up"),
    ("camera_ja", 29, 6), ("fade_in",),
    ("legenda", "Capítulo 5: reunião extraordinária do conselho", 2.4),
    ("andar", "player", 29, 8), ("andar", "player", 32, 8), ("andar", "player", 32, 5), ("sentar", "player"),
    ("fala", "tio_conrad", "Vamos ser breves. A Luthor Corp precisa de uma liderança madura."),
    ("fala", "tio_conrad", "Propomos a saída da senhora Letícia Luthor da presidência."),
    ("fala", "tio_edmund", "Com todo o respeito à memória do nosso irmão, claro.", "smile"),
    ("fala", "rojas", "Eu peguei o primeiro voo quando soube desta reunião. Antes de votar, quero ouvir a minha amiga.", "smile"),
    ("fala", "sam", "Mostra para eles, Luthor.", "smile"),
    ("escolha", "O que você apresenta?", [
        ("As pessoas: a equipe, a cidade e a Fundação.", 60, "Empresa é gente. E a cidade inteira está do nosso lado."),
        ("Os resultados: o laboratório nunca lançou tanto.", 50, "E nunca vendeu tanto. Página três do relatório."),
        ("A verdade: o espião, o dossiê falso e quem pagou por eles.", 60, "Brainy, os registros, por favor."),
    ]),
    ("fala", "brainy", "Registros do Terminal P&D. O pen drive do espião. A pasta \"Para C. e E. Luthor\". Trouxe em papel."),
    ("fala", "brainy", "E a matéria da CatCo de sexta. A Lucy e a Nia confirmaram tudo com o escritório de Gotham."),
    ("emote", "tio_conrad", "raiva"), ("emote", "tio_edmund", "gota"),
    ("fala", "ian", "A Marina Luthor fechou o trimestre no azul. Eu voto com a Letícia. Desde as férias no interior.", "happy"),
    ("fala", "rojas", "Eu também. E proponho outra coisa: quem contratou espionagem contra a própria empresa vende as ações.", "happy"),
    ("fala", "hamilton", "Apoiado. Por unanimidade, menos dois."),
    ("narra", "A votação termina rápido. As mãos levantadas não deixam dúvida."),
    ("fala", "tio_conrad", "Isso não termina aqui."),
    ("levantar", "player"), ("andar", "player", 32, 6), ("virar", "player", "left"),
    ("fala", "player", "Termina, tio. Vocês vendem as ações, a Luthor Corp compra."),
    ("fala", "player", "E vocês nunca mais chegam perto de ninguém que eu amo."),
    ("levantar", "tio_edmund"), ("levantar", "tio_conrad"),
    ("andar_", "tio_edmund", 30, 8), ("andar", "tio_conrad", 31, 8),
    ("andar_", "tio_edmund", 30, 10), ("andar", "tio_conrad", 29, 8),
    ("andar", "tio_conrad", 29, 10),
    ("sai", "tio_conrad"), ("sai", "tio_edmund"),
    ("fala", "sam", "Você sabe o que isso quer dizer? A Luthor Corp é nossa. Sem tios. Sem sombra.", "happy"),
    ("fala", "jess", "Eu anotei tudo. Inclusive a cara deles na hora da votação.", "happy"),
    ("efeito", "confete", 3),
    ("legenda", "A Luthor Corp é sua", 2.4),
    ("esperar", 0.6), ("fade_out",),
])
