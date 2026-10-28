"""Cutscenes extras (as cenas originais ficam em cutscenes.py e não são alteradas aqui).

Cenas dos eventos de coração das personagens novas: Ian, Barry e Dona Graça.
"""
from .cutscenes import SCENES
from .characters import NPCS

EXTRA_SCENES = {
    # ----------------------------------------------------------- Ian
    "ian_3": dict(map="marina", time=10 * 60, npc="ian", steps=[
        ("ator", "ian", 17, 3, "down"),
        ("ator", "player", 11, 10, "up"),
        ("camera_ja", 14, 6),
        ("fade_in",),
        ("legenda", "Marina Luthor", 1.6),
        ("andar", "player", 11, 6),
        ("andar", "player", 15, 6),
        ("andar", "player", 15, 3),
        ("virar", "player", "right"),
        ("virar", "ian", "left"),
        ("emote", "ian", "exclamacao"),
        ("fala", "ian", "Chefe! Chegou na hora certa. Acabei de fechar o relatório do trimestre da marina.", "feliz"),
        ("fala", "ian", "Divisão náutica no azul pela primeira vez. Passeios lotados, frota revisada e zero acidentes."),
        ("fala", "player", "Bom trabalho, Ian. Eu sabia que podia deixar a marina nas suas mãos.", "feliz"),
        ("fala", "ian", "E como diretor, criei uma regra nova: a CEO paga metade do preço nos passeios. Pra sempre.", "feliz"),
        ("fala", "ian", "Você me deu autonomia pra tocar a divisão. Estou usando. Não discute com o seu diretor."),
        ("escolha", "O que dizer?", [
            ("Você não precisava, Ian.", 50, "Precisava sim. Você confiou esse lugar a mim. É o mínimo."),
            ("Desconto na minha própria empresa?", 30, "Exatamente. É a decisão mais cara que eu já tomei como diretor."),
            ("Só aceito se você correr a regata comigo.", 60, "Fechado. E eu não vou pegar leve. Nem com a chefe."),
        ]),
        ("efeito", "brilhos", 1.6),
        ("esperar", 1.2),
        ("fade_out",),
    ]),
    "ian_6": dict(map="altomar", time=18 * 60 + 40, npc="ian", steps=[
        ("ator", "ian", 31, 13, "right"),
        ("ator", "player", 26, 13, "right"),
        ("camera_ja", 28, 13),
        ("fade_in",),
        ("legenda", "Alto-mar, fim de tarde", 1.8),
        ("andar", "player", 30, 13),
        ("esperar", 0.8),
        ("virar", "ian", "left"),
        ("fala", "ian", "Lembra das férias no interior? A casa do lago, a gente com uns dez anos?"),
        ("fala", "player", "Lembro de você jurando que sabia velejar. E da gente nadando de volta pra margem.", "feliz"),
        ("emote", "ian", "musica"),
        ("fala", "ian", "Eu sabia velejar. O barco é que não sabia boiar.", "feliz"),
        ("narra", "O sol encosta no mar. Por um instante, os dois ficam em silêncio, como naquele verão."),
        ("fala", "ian", "Toda vez que eu saio com o barco, eu penso naquela época. Era fácil ser feliz."),
        ("fala", "ian", "Toma. São as minhas luvas de vela. As da primeira regata que eu ganhei. Quero que fiquem com você."),
        ("escolha", "O que dizer?", [
            ("Ainda é fácil, Ian. Olha onde a gente está.", 70, "...É. Você tem razão. Como sempre, aliás."),
            ("Eu guardo, mas você me ensina a velejar direito.", 55, "Combinado. Desta vez com colete salva-vidas."),
            ("Você está ficando sentimental.", 20, "Culpa do pôr do sol. E da companhia."),
        ]),
        ("efeito", "brilhos", 2.0),
        ("esperar", 1.6),
        ("fade_out",),
    ]),
    # ----------------------------------------------------------- Barry
    "barry_3": dict(map="catco", time=17 * 60, npc="barry", steps=[
        ("ator", "barry", 14, 10, "down"),
        ("ator", "player", 11, 13, "up"),
        ("camera_ja", 13, 11),
        ("fade_in",),
        ("legenda", "CatCo, fim de expediente", 1.8),
        ("andar", "player", 14, 13),
        ("andar", "player", 14, 11),
        ("virar", "player", "up"),
        ("emote", "barry", "exclamacao"),
        ("fala", "barry", "Letícia! Chegou bem na hora. Acabei de revelar as fotos da semana.", "feliz"),
        ("pulo", "barry"),
        ("narra", "Ele espalha as fotos na mesa: o calçadão de manhã, o farol, o píer... e você, rindo no Grão Nobre."),
        ("fala", "barry", "Essa aqui é a melhor. Você nem percebeu que eu estava lá."),
        ("fala", "barry", "A Lucy pediu uma cópia. Depois pediu outra. Eu não perguntei por quê.", "timido"),
        ("escolha", "O que dizer?", [
            ("Ficou linda, Barry. Você tem talento.", 60, "Sério? Vou emoldurar esse elogio. E a foto."),
            ("A Lucy pediu duas?", 40, "Duas. Uma pra mesa e uma pra carteira, eu acho. Não conta que eu contei!"),
            ("Você me fotografou sem pedir?", 10, "É jornalismo! ...Tá bom, é que a luz estava perfeita. Desculpa."),
        ]),
        ("efeito", "brilhos", 1.4),
        ("esperar", 1.2),
        ("fade_out",),
    ]),
    "barry_6": dict(map="city", time=18 * 60 + 10, npc="barry", steps=[
        ("ator", "barry", 30, 58, "up"),
        ("ator", "nia", 32, 58, "up"),
        ("ator", "lucy", 28, 58, "up"),
        ("ator", "player", 30, 53, "down"),
        ("camera_ja", 30, 56),
        ("fade_in",),
        ("legenda", "A orla no fim de tarde", 1.8),
        ("andar", "player", 30, 56),
        ("fala", "barry", "Chegou a nossa CEO! Agora sim, a foto do grupo fica completa.", "feliz"),
        ("fala", "nia", "Ele está planejando essa foto há uma semana. Fez até desenho.", "feliz"),
        ("fala", "lucy", "Fica do meu lado, Luthor. Ninguém sai bem do lado do Barry, ele não para quieto."),
        ("andar", "player", 29, 56),
        ("virar", "player", "down"),
        ("fala", "barry", "Todo mundo sorrindo! Três, dois, um...", "feliz"),
        ("efeito", "brilhos", 1.2),
        ("narra", "Clique! A luz dourada da tarde pega os quatro de uma vez."),
        ("emote", "lucy", "vergonha"),
        ("fala", "barry", "Ficou perfeita. Vou guardar o negativo. E toma, um filme novo: tira umas fotos suas por aí.", "feliz"),
        ("efeito", "coracoes", 1.6),
        ("esperar", 1.4),
        ("fade_out",),
    ]),
    # ----------------------------------------------------------- Dona Graça
    "graca_3": dict(map="trattoria", time=15 * 60 + 30, npc="graca", steps=[
        ("ator", "graca", 9, 4, "down"),
        ("ator", "player", 10, 11, "up"),
        ("camera_ja", 9, 7),
        ("fade_in",),
        ("legenda", "Ricci Trattoria, entre o almoço e o jantar", 2.0),
        ("andar", "player", 10, 6),
        ("andar", "player", 9, 6),
        ("virar", "player", "up"),
        ("fala", "graca", "Ah, chegou a minha cliente preferida! Vem cá, filha, senta um pouquinho."),
        ("narra", "Um cheiro de dendê e coentro toma conta da cozinha italiana."),
        ("fala", "graca", "Fiz uma moqueca do jeito da minha mãe, lá em Salvador. Não conta pra Vittoria que não é italiano.", "feliz"),
        ("emote", "graca", "musica"),
        ("fala", "graca", "Leva pra casa. Esquenta devagar, não deixa ferver. E volta pra me dizer se ficou boa."),
        ("escolha", "O que dizer?", [
            ("Que cheiro maravilhoso, Dona Graça!", 60, "É o dendê, filha. E trinta anos de fogão."),
            ("A senhora sente saudade da Bahia?", 50, "Todo dia. Mas aqui eu cozinho e a saudade vira tempero."),
            ("Não é contra as regras da casa?", 20, "Regra da casa é comida boa. O resto é detalhe."),
        ]),
        ("efeito", "brilhos", 1.4),
        ("esperar", 1.2),
        ("fade_out",),
    ]),
}
SCENES.update(EXTRA_SCENES)

TITLES = {"ian_3": "Ian: o relatório da marina", "ian_6": "Ian: as férias no interior", "barry_3": "Barry: as fotos da semana",
          "barry_6": "Barry: a foto do grupo", "graca_3": "Dona Graça: a moqueca de Salvador"}

# eventos de coração com cena
NPCS["ian"]["events"] = {
    3: dict(scene="ian_3", flag="marina_vip", lines=NPCS["ian"]["events"][3]["lines"]),
    6: dict(scene="ian_6", gift="luvas_vela", lines=["Toma, as minhas luvas de vela. Quero que fiquem com você."]),
}
NPCS["barry"]["events"] = {
    3: dict(scene="barry_3", lines=NPCS["barry"]["events"][3]["lines"]),
    6: dict(scene="barry_6", gift="filme_foto", lines=["Ficou perfeita a foto do grupo! Toma um filme novo."]),
}
NPCS["graca"]["events"] = {3: dict(scene="graca_3", gift="moqueca", lines=NPCS["graca"]["events"][3]["lines"])}
