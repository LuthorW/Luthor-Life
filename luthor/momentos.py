"""Momentos entre personagens: cenas curtas que a Letícia encontra andando pela cidade.

Cada momento acontece num lugar e num horário (alguns só em certos dias ou com sol), uma vez só. Quando a Letícia
passa perto, a cena toca: as duas personagens conversam entre si e, no fim, ela entra na conversa. Rende um pouco de
amizade com as duas, vira foto no álbum do Barry e fica em "Rever cenas". No máximo um momento por dia e nunca em
dia de festa.
"""
from . import festas
from .characters import NPCS
from .cutscenes import SCENES
from .config import C_LILAC

# chave: dict(a, b, titulo, onde (mapa, x, y = ponto perto do qual toca), horas (de, até), dias (dias da semana
# 0=segunda... ou None), sol (só sem chuva), corações (soma mínima com as duas), passos)
MOMENTS = {
    "momento_barry_nia": dict(
        a="barry", b="nia", title="Barry e Nia: a borboleta", where=("city", 20, 27), hours=(8, 12), sun=True,
        hearts=2, player=(20, 31, "up"),
        steps=[
            ("ator", "barry", 18, 25, "right"), ("ator", "nia", 21, 25, "left"),
            ("camera_ja", 20, 27), ("fade_in",),
            ("fala", "barry", "Não se mexe. Tem uma borboleta azul no seu ombro. Isso é capa, Nia. CAPA.", "happy"),
            ("fala", "nia", "Barry, eu tô com o braço levantado há dois minutos. Ele vai cair.", "bad"),
            ("emote", "barry", "estrela"),
            ("efeito", "brilhos", 1.2),
            ("fala", "barry", "Pronto! ...Ah, não. Saiu só o seu cotovelo."),
            ("emote", "nia", "gota"),
            ("fala", "nia", "Sabe o que eu escrevi hoje de manhã? Que \"a melhor foto é a que a gente não planeja\".", "smile"),
            ("andar", "player", 20, 27),
            ("virar", "nia", "down"), ("virar", "barry", "down"),
            ("fala", "player", "Bom dia, equipe da CatCo. A borboleta foi embora?"),
            ("fala", "barry", "Foi. Mas agora tem uma CEO no enquadramento. Sorriam!", "happy"),
            ("efeito", "brilhos", 1.0),
            ("emote", "nia", "feliz"),
            ("esperar", 0.6), ("fade_out",),
        ]),
    "momento_sam_brainy": dict(
        a="sam", b="brainy", title="Sam e Brainy: o orçamento", where=("city", 21, 17), hours=(8, 11), days=(0, 1, 2, 3, 4),
        hearts=3, player=(26, 17, "left"),
        steps=[
            ("ator", "sam", 20, 16, "right"), ("ator", "brainy", 22, 16, "left"),
            ("camera_ja", 22, 17), ("fade_in",),
            ("fala", "brainy", "Eu só preciso de um acelerador de partículas pequeno. Do tamanho de uma garagem."),
            ("fala", "sam", "Brainy, a garagem da sede tem dezenove vagas. Todas ocupadas.", "bad"),
            ("fala", "brainy", "Dezoito, se a Jess estacionar direito.", "happy"),
            ("emote", "sam", "raiva"),
            ("fala", "sam", "Me manda uma planilha. Com custo, prazo e retorno. Em reais, não em \"potencial cósmico\"."),
            ("emote", "brainy", "triste"),
            ("andar", "player", 24, 17), ("virar", "sam", "right"), ("virar", "brainy", "right"),
            ("fala", "player", "Bom dia. Estou ouvindo a palavra \"acelerador\" na frente do prédio?"),
            ("fala", "brainy", "Hipoteticamente.", "shy"),
            ("fala", "sam", "Ele vai mandar a planilha. E eu vou dizer não com todo o carinho do mundo.", "smile"),
            ("emote", "brainy", "gota"),
            ("esperar", 0.5), ("fade_out",),
        ]),
    "momento_lucy_barry": dict(
        a="lucy", b="barry", title="Lucy e Barry: a pauta", where=("city", 48, 17), hours=(13, 17), days=(0, 1, 2, 3, 4),
        hearts=3, player=(53, 17, "left"),
        steps=[
            ("ator", "lucy", 47, 16, "right"), ("ator", "barry", 49, 16, "left"),
            ("camera_ja", 49, 17), ("fade_in",),
            ("fala", "lucy", "Câmera carregada? Bloquinho? Café? Vamos, a coletiva começa em vinte minutos."),
            ("fala", "barry", "Lucy, a coletiva é do outro lado da cidade. Eu chego em vinte minutos. Você não.", "happy"),
            ("emote", "lucy", "pergunta"),
            ("fala", "barry", "Brincadeira! Eu chamo um táxi pra gente. Correndo, mas de táxi."),
            ("andar", "player", 51, 17), ("virar", "lucy", "right"), ("virar", "barry", "right"),
            ("fala", "lucy", "Letícia. Se for sobre a coletiva da prefeitura, eu já tenho três perguntas pra você.", "smile"),
            ("fala", "player", "Eu nem estou na coletiva."),
            ("fala", "lucy", "Por isso mesmo. Depois a gente conversa.", "shy"),
            ("emote", "barry", "reticencias"),
            ("andar_", "barry", 47, 17), ("andar", "lucy", 46, 17),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_graca_vittoria": dict(
        a="graca", b="vittoria", title="Dona Graça e Vittoria: o almoço", where=("city", 82, 33), hours=(11, 15),
        hearts=3, player=(86, 33, "left"),
        steps=[
            ("ator", "vittoria", 83, 32, "down"), ("ator", "graca", 81, 32, "right"),
            ("camera_ja", 82, 33), ("fade_in",),
            ("fala", "vittoria", "Sim, eu sei que o fornecedor atrasou. Não, não pode ser amanhã. Pronto. Ciao.", "bad"),
            ("emote", "graca", "raiva"),
            ("fala", "graca", "Vittoria Ricci. Que horas você comeu hoje?"),
            ("fala", "vittoria", "...Eu tomei um cappuccino.", "shy"),
            ("fala", "graca", "Cappuccino é bebida, minha filha. Senta aqui que tem arroz, feijão e um bife acebolado."),
            ("fala", "vittoria", "Isso não está no cardápio de uma trattoria.", "smile"),
            ("fala", "graca", "No meu está. Dona do Gruppo Ricci também almoça."),
            ("andar", "player", 84, 33), ("virar", "graca", "right"), ("virar", "vittoria", "right"),
            ("fala", "graca", "E você também, Letícia! Duas empresárias com cara de fome. Já pra dentro!", "happy"),
            ("emote", "vittoria", "feliz"),
            ("fala", "player", "Dona Graça, eu tenho uma reunião às..."),
            ("fala", "graca", "Tinha.", "happy"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_joca_ian": dict(
        a="joca", b="ian", title="Seu Joca e Ian: a isca", where=("city", 60, 56), hours=(6, 10), sun=True,
        hearts=2, player=(60, 53, "down"),
        steps=[
            ("ator", "joca", 60, 58, "down"), ("ator", "ian", 61, 57, "down"),
            ("camera_ja", 60, 57), ("fade_in",),
            ("fala", "ian", "Seu Joca, com todo o respeito: isca artificial pega mais robalo."),
            ("fala", "joca", "Rapaz, eu pesco aqui desde antes de você saber andar de barco."),
            ("fala", "ian", "Eu sei andar de barco desde os sete anos.", "smile"),
            ("fala", "joca", "Eu pesco aqui desde antes de você ter sete anos, então."),
            ("emote", "joca", "exclamacao"),
            ("fala", "joca", "Olha aí! Fisgou. Com camarão. Camarão de verdade.", "happy"),
            ("emote", "ian", "gota"),
            ("andar", "player", 60, 56), ("virar", "ian", "up"),
            ("fala", "ian", "Letícia, não diz nada. Eu sei. Eu vi.", "shy"),
            ("fala", "player", "Eu só ia dizer bom dia."),
            ("fala", "joca", "Diz bom dia e leva um robalo, dona Letícia! Pescado do jeito certo.", "happy"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_rafa_jess": dict(
        a="rafa", b="jess", title="Harry e Jess: o café para viagem", where=("city", 36, 17), hours=(7, 10),
        days=(0, 1, 2, 3, 4), hearts=2, player=(32, 17, "right"),
        steps=[
            ("ator", "jess", 41, 17, "left"), ("ator", "rafa", 35, 16, "down"),
            ("camera_ja", 37, 17), ("fade_in",),
            ("andar", "jess", 37, 17),
            ("fala", "jess", "Harry! Expresso duplo, sem açúcar, em três segundos, por favor, eu te amo, tchau.", "bad"),
            ("fala", "rafa", "Já está pronto. Você passa aqui às 8h12 todo dia.", "happy"),
            ("emote", "jess", "surpresa"),
            ("fala", "jess", "Você decorou o meu horário?"),
            ("fala", "rafa", "Decorei o horário de todo mundo. O seu é o único que corre.", "smile"),
            ("emote", "jess", "vergonha"),
            ("andar", "player", 34, 17), ("virar", "jess", "left"), ("virar", "rafa", "left"),
            ("fala", "jess", "Chefe! Seu cappuccino. Eu ia levar pro escritório, juro.", "shy"),
            ("fala", "player", "Respira, Jess. A reunião das nove é minha. Ela espera."),
            ("fala", "rafa", "Viu? Até a CEO concorda. Senta dois minutos.", "happy"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_theo_bea": dict(
        a="theo", b="bea", title="Theo e Bea: a troca", where=("city", 57, 33), hours=(15, 18),
        hearts=2, player=(53, 33, "right"),
        steps=[
            ("ator", "theo", 56, 32, "right"), ("ator", "bea", 58, 32, "left"),
            ("camera_ja", 57, 33), ("fade_in",),
            ("fala", "theo", "Esse aqui é para você. Um romance sobre uma feira em Lisboa. Achei a sua cara."),
            ("fala", "bea", "Theo, você sabe que eu não tenho tempo de ler. Eu tenho um mercado.", "smile"),
            ("fala", "theo", "Dez páginas por noite. É menos do que a lista de compras dos seus clientes."),
            ("fala", "bea", "Tá bom. Mas eu pago em tangerina. Uma por capítulo.", "happy"),
            ("emote", "theo", "coracao"),
            ("andar", "player", 55, 33), ("virar", "theo", "left"), ("virar", "bea", "left"),
            ("fala", "player", "Uma livraria e um mercado fazendo negócio na calçada. A Sam ia adorar."),
            ("fala", "theo", "Não conta para ela. Ela vai querer um contrato.", "smile"),
            ("emote", "bea", "feliz"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_meredith_yang": dict(
        a="meredith", b="yang", title="Meredith e Cristina: a aposta", where=("city", 78, 17), hours=(17, 21),
        hearts=2, player=(74, 17, "right"),
        steps=[
            ("ator", "meredith", 77, 16, "right"), ("ator", "yang", 79, 16, "left"),
            ("camera_ja", 78, 17), ("fade_in",),
            ("fala", "yang", "Quatro horas e doze minutos. Recorde do hospital. Pode anotar.", "happy"),
            ("fala", "meredith", "Você contou a anestesia?"),
            ("fala", "yang", "Eu contei o que importa: a parte em que eu operei.", "smile"),
            ("emote", "meredith", "reticencias"),
            ("fala", "meredith", "Aposta: na próxima, eu faço em quatro horas."),
            ("fala", "yang", "Fechado. Quem perder paga o jantar. No restaurante caro.", "happy"),
            ("andar", "player", 76, 17), ("virar", "meredith", "left"), ("virar", "yang", "left"),
            ("fala", "player", "Boa noite, doutoras. Eu ouvi \"restaurante caro\"?"),
            ("fala", "yang", "Você não está na aposta. Mas pode ser a juíza.", "smile"),
            ("fala", "meredith", "Ela é a juíza. E vai pagar a sobremesa.", "happy"),
            ("emote", "player", "gota"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_izzie_addison": dict(
        a="izzie", b="addison", title="Izzie e Addison: os cupcakes", where=("city", 29, 38), hours=(12, 15),
        days=(5, 6), sun=True, hearts=2, player=(33, 39, "left"),
        steps=[
            ("ator", "izzie", 28, 37, "right"), ("ator", "addison", 31, 37, "left"),
            ("camera_ja", 30, 38), ("fade_in",),
            ("fala", "izzie", "Esse é de limão, esse é de cenoura e esse é... experimental.", "happy"),
            ("fala", "addison", "\"Experimental\" é o de pimenta, não é?", "bad"),
            ("fala", "izzie", "Pimenta e chocolate. É ciência. Confia."),
            ("emote", "addison", "pergunta"),
            ("esperar", 0.4),
            ("emote", "addison", "surpresa"),
            ("fala", "addison", "...Tá. Isso é muito bom. Não conta para ninguém que eu disse.", "smile"),
            ("andar", "player", 31, 39), ("virar", "izzie", "down"), ("virar", "addison", "down"),
            ("fala", "izzie", "Letícia! Pega um. Qualquer um. Menos o último, que é da Addison.", "happy"),
            ("fala", "addison", "Pode pegar o último. Eu já comi três.", "shy"),
            ("emote", "izzie", "coracao"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_marco_graca": dict(
        a="marco", b="graca", title="Marco e Dona Graça: a caipirinha", where=("city", 55, 47), hours=(18, 22),
        hearts=2, player=(51, 47, "right"),
        steps=[
            ("ator", "marco", 54, 46, "right"), ("ator", "graca", 56, 46, "left"),
            ("camera_ja", 55, 47), ("fade_in",),
            ("fala", "marco", "Dona Graça, a senhora precisa me ensinar. A minha caipirinha está com gosto de... vidro."),
            ("fala", "graca", "Primeiro: limão. Não é lima, não é limonada em pó. Limão.", "bad"),
            ("fala", "marco", "Anotado."),
            ("fala", "graca", "Segundo: amassa com carinho. Você está socando o limão como se ele te devesse dinheiro."),
            ("emote", "marco", "gota"),
            ("fala", "graca", "Terceiro: prova antes de servir. Bar bom é bar que prova.", "happy"),
            ("andar", "player", 53, 47), ("virar", "marco", "left"), ("virar", "graca", "left"),
            ("fala", "marco", "Letícia! Aula particular. Amanhã a caipirinha do Noonan's vai ser outra.", "happy"),
            ("fala", "player", "Vou provar. Por motivos científicos."),
            ("segurar", "player", "caipirinha"), ("beber", "player"),
            ("emote", "graca", "estrela"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_sam_milany": dict(
        a="sam", b="milany", title="Sam e Milany: a corrida", where=("city", 66, 53), hours=(6, 9), days=(5, 6),
        sun=True, hearts=3, player=(62, 53, "right"),
        steps=[
            ("ator", "sam", 72, 53, "left"), ("ator", "milany", 75, 53, "left"),
            ("camera_ja", 67, 53), ("fade_in",),
            ("andar_", "sam", 66, 53), ("andar", "milany", 68, 53),
            ("fala", "milany", "Sam... como médica... eu recomendo... uma pausa.", "bad"),
            ("fala", "sam", "Faltam só dois quilômetros. Você que disse que correr faz bem pro coração.", "happy"),
            ("fala", "milany", "Eu disse caminhar. Correr atrás de uma CFO é outra especialidade."),
            ("emote", "milany", "gota"),
            ("andar", "player", 64, 53), ("virar", "sam", "left"), ("virar", "milany", "left"),
            ("fala", "sam", "Letícia! Vem com a gente. A Milany está adorando.", "happy"),
            ("fala", "milany", "A Milany está mentindo pela primeira vez na vida.", "smile"),
            ("fala", "player", "Eu acompanho até a padaria. Depois vocês duas ganham um café."),
            ("emote", "milany", "coracao"),
            ("esperar", 0.4), ("fade_out",),
        ]),
    "momento_lucy_vittoria": dict(
        a="lucy", b="vittoria", title="Lucy e Vittoria: a entrevista", where=("city", 64, 17), hours=(10, 16),
        days=(0, 1, 2, 3, 4), hearts=6, player=(69, 17, "left"),
        steps=[
            ("ator", "lucy", 63, 16, "right"), ("ator", "vittoria", 65, 16, "left"),
            ("camera_ja", 65, 17), ("fade_in",),
            ("fala", "lucy", "Última pergunta: como é inaugurar uma sede no mesmo ano em que a Luthor Corp bate recorde?"),
            ("fala", "vittoria", "Fome de crescer. E a sorte de ter vizinhos que comem bem.", "smile"),
            ("fala", "lucy", "Vizinhos. Tipo... uma certa CEO?", "smile"),
            ("fala", "vittoria", "Isso é jornalismo ou fofoca, senhorita Williams?"),
            ("fala", "lucy", "Em National City, as duas coisas pagam o mesmo.", "happy"),
            ("andar", "player", 67, 17), ("virar", "lucy", "right"), ("virar", "vittoria", "right"),
            ("emote", "lucy", "exclamacao"), ("emote", "vittoria", "exclamacao"),
            ("fala", "player", "...Eu estou interrompendo alguma coisa?"),
            ("fala", "lucy", "Nada! Entrevista de negócios. Muito séria.", "shy"),
            ("fala", "vittoria", "Seriíssima. Ela só perguntou de você umas quatro vezes.", "happy"),
            ("emote", "lucy", "vergonha"),
            ("esperar", 0.4), ("fade_out",),
        ]),
}

TITLES = {k: m["title"] for k, m in MOMENTS.items()}

for _k, _m in MOMENTS.items():
    _px, _py, _pd = _m["player"]
    SCENES[_k] = dict(map=_m["where"][0], time=(_m["hours"][0] + 1) * 60, weather="sol", npc=_m["a"],
                      steps=[("ator", "player", _px, _py, _pd)] + _m["steps"])


def init_state(g):
    g.momentos = dict(seen=[], day=-1)


def save_state(g):
    return {"momentos": g.momentos}


def load_state(g, d):
    init_state(g)
    m = d.get("momentos") or {}
    g.momentos["seen"] = [k for k in m.get("seen", []) if k in MOMENTS]
    g.momentos["day"] = m.get("day", -1)


def _ok(g, k, m):
    if k in g.momentos["seen"] or g.map_name != m["where"][0]:
        return False
    if not (m["a"] in NPCS and m["b"] in NPCS):
        return False
    h0, h1 = m["hours"]
    if not h0 * 60 <= g.minutes <= h1 * 60:
        return False
    if m.get("days") and g.weekday not in m["days"]:
        return False
    if m.get("sun") and g.weather != "sol":
        return False
    if g.hearts(m["a"]) + g.hearts(m["b"]) < m["hearts"]:
        return False
    # quem está num encontro marcado com a Letícia não aparece num momento
    if g.date and not g.date.get("done") and g.date["npc"] in (m["a"], m["b"]) and g.minutes >= 18 * 60:
        return False
    tx, ty = g.player.tile
    x, y = m["where"][1:]
    return abs(tx - x) <= 7 and abs(ty - y) <= 5


def check(g):
    if g.momentos["day"] == g.abs_day() or festas.today(g):
        return False
    for k, m in MOMENTS.items():
        if _ok(g, k, m):
            g.momentos["seen"].append(k)
            g.momentos["day"] = g.abs_day()
            sc = dict(SCENES[k], time=g.minutes, weather=g.weather)

            def end(m=m):
                px, py, _d = m["player"]
                last = [s for s in m["steps"] if s[0] == "andar" and s[1] == "player"]
                if last:
                    px, py = last[-1][2], last[-1][3]
                g.player.place_tile(px, py, m["player"][2])
                for who in (m["a"], m["b"]):
                    g.add_friendship(who, 20)
                    g.npcs[who].snap_to_schedule(g.minutes)
                g.toasts.push(f"Momento: {m['title']}", C_LILAC)
            g.play_scene(k, sc, on_end=end)
            return True
    return False
