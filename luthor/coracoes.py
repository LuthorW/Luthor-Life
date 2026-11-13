"""Eventos de coração que completam a história combinada da Lucy e da Vittoria (lore do CLAUDE.md).

As cenas que já existiam ficam como estão; estas entram nos espaços livres:
  lucy_5      a Lucy acha, no arquivo da CatCo, a data da morte do Alexander e percebe que a Letícia foi embora
              de Gotham meses antes; ela não força a conversa (a Letícia conta tudo no píer, lucy_6)
  vittoria_5  6h da manhã: a Letícia ajuda a Vittoria a arrumar a inauguração oficial da sede do Gruppo Ricci
  vittoria_7  fim de noite na Trattoria: a Vittoria confessa o medo de se apaixonar por alguém tão ocupada quanto ela
Saves antigos: quem já viu o evento seguinte não recebe o novo fora de ordem (`load_state`).
"""
from .characters import NPCS
from .cutscenes import SCENES
from . import eventos

SCENES["lucy_5"] = dict(map="catco", time=18 * 60 + 30, npc="lucy", steps=[
    ("ator", "lucy", 12, 3, "up"),
    ("ator", "player", 11, 13, "up"),
    ("camera_ja", 11, 5),
    ("fade_in",),
    ("legenda", "Arquivo da CatCo, fim de tarde", 1.8),
    ("narra", "A redação está quase vazia. A Lucy está parada na frente do arquivo, com uma pasta antiga aberta nas mãos."),
    ("andar", "player", 9, 13),
    ("andar", "player", 9, 3),
    ("andar", "player", 10, 3),
    ("virar", "player", "right"),
    ("virar", "lucy", "left"),
    ("fala", "lucy", "Letícia. Eu não ouvi você entrar."),
    ("fala", "player", "Você está com cara de quem achou uma pauta. Ou um fantasma."),
    ("fala", "lucy", "Um pouco das duas coisas. Eu estava procurando uma matéria antiga sobre a Luthor Corp e achei isto."),
    ("narra", "É uma nota de falecimento, recortada de um jornal de negócios: \"Alexander Luthor, fundador da Luthor Corp\". "
              "Com a data."),
    ("fala", "lucy", "Eu fiz as contas sem querer. Jornalista faz conta sem querer. Você foi embora de Gotham meses antes disso."),
    ("fala", "lucy", "Você foi embora quando ele ficou doente. E eu passei anos achando que tinha sido por minha causa.", "bad"),
    ("emote", "player", "triste"),
    ("fala", "player", "Não foi por sua causa, Lucy. Nunca foi."),
    ("fala", "lucy", "Então foi por quê?"),
    ("escolha", "O que dizer?", [
        ("Eu vou te contar tudo. Mas não aqui, no meio da redação.", 60,
         "Tudo bem. Eu esperei anos. Posso esperar até você escolher o lugar."),
        ("Meu pai estava morrendo e eu não sabia o que fazer.", 50,
         "Eu sinto muito. De verdade. Eu queria ter estado lá. Mesmo sem saber de nada."),
        ("Tem uma parte dessa história que envolve você. Eu preciso de coragem.", 60,
         "Envolve eu? ...Tá. Respira. Quando você estiver pronta, eu escuto. Sem gravador."),
    ]),
    ("fala", "lucy", "Eu não vou publicar nada sobre isso, se é o que você está pensando. Isso não é matéria. É você.", "smile"),
    ("fala", "player", "Eu sei. Obrigada, Lucy."),
    ("fala", "lucy", "O píer, à noite, é um bom lugar para conversas difíceis. Caso você esteja procurando um."),
    ("narra", "A Lucy guarda a pasta no arquivo com cuidado, como quem guarda uma coisa que não é dela."),
    ("esperar", 0.6),
    ("fade_out",),
])

SCENES["vittoria_5"] = dict(map="city", time=6 * 60 + 10, npc="vittoria", steps=[
    ("ator", "vittoria", 65, 16, "up"),
    ("ator", "player", 58, 17, "right"),
    ("camera_ja", 63, 16),
    ("fade_in",),
    ("legenda", "Gruppo Ricci, 6h da manhã", 1.8),
    ("narra", "A rua ainda está vazia. Na frente da sede do Gruppo Ricci, uma faixa enrolada, caixas de vasos e uma "
              "Vittoria descabelada."),
    ("andar", "player", 63, 17),
    ("andar", "player", 63, 16),
    ("virar", "player", "right"),
    ("virar", "vittoria", "left"),
    ("emote", "vittoria", "surpresa"),
    ("fala", "vittoria", "Letícia?! São seis da manhã! Ninguém em National City acorda às seis. Só eu e os pombos."),
    ("fala", "player", "Você disse que a inauguração oficial era hoje. E que a equipe só chegava às oito."),
    ("fala", "vittoria", "Eu disse isso em voz alta? Dio mio. Eu falo demais quando estou nervosa.", "shy"),
    ("fala", "vittoria", "A sede já funciona faz semanas, mas hoje é o dia da placa, da imprensa, da fita. Do nome Ricci "
                         "na fachada. Eu passei a vida trabalhando no restaurante dos outros para chegar aqui."),
    ("fala", "player", "Então me dá uma tarefa. Eu sou ótima em carregar vaso."),
    ("fala", "vittoria", "A CEO da Luthor Corp, carregando vaso de manjericão. A CatCo pagaria uma fortuna por essa foto.",
     "happy"),
    ("narra", "Por uma hora, as duas penduram a faixa, arrumam os vasos na porta e varrem a calçada. A Vittoria reclama "
              "da faixa torta três vezes. Ela não está torta."),
    ("efeito", "brilhos", 1.4),
    ("escolha", "O que dizer quando terminam?", [
        ("Ficou lindo. Ficou com a sua cara.", 60, "Com a minha cara de quem não dormiu? ...Brincadeira. Obrigada. Ficou mesmo."),
        ("Sua nonna ia ficar orgulhosa.", 70, "Não fala isso agora, que eu borro o rímel antes da imprensa chegar."),
        ("Às dez eu volto para a fita. Na primeira fila.", 60, "Na primeira fila, do meu lado. Isso não é um convite, é uma ordem."),
    ]),
    ("fala", "vittoria", "Sabe o que é engraçado? Eu tinha medo de abrir a sede sozinha. E não abri.", "love"),
    ("fala", "vittoria", "Toma: o primeiro vinho com o rótulo novo do Gruppo Ricci. O número um é seu."),
    ("emote", "vittoria", "coracao"),
    ("esperar", 0.6),
    ("fade_out",),
])

SCENES["vittoria_7"] = dict(map="trattoria", time=23 * 60 + 20, npc="vittoria", steps=[
    ("ator", "vittoria", 12, 8, "right"),
    ("sentar", "vittoria"),
    ("segurar", "vittoria", "taca_vinho"),
    ("ator", "player", 10, 11, "up"),
    ("camera_ja", 13, 9),
    ("fade_in",),
    ("legenda", "Ricci Trattoria, depois do fechamento", 1.8),
    ("fala", "vittoria", "A última cliente da noite. De novo. A Dona Graça já chama de \"a mesa da Letícia\"."),
    ("andar", "player", 15, 11),
    ("andar", "player", 15, 9),
    ("andar", "player", 14, 9),
    ("andar", "player", 14, 8),
    ("sentar", "player"),
    ("segurar", "player", "taca_vinho"),
    ("fala", "player", "É o único lugar da cidade onde ninguém me pede uma assinatura."),
    ("fala", "vittoria", "Aqui você só assina a conta. E nem isso, porque eu não deixo."),
    ("brinde", "vittoria", "player"),
    ("beber", "vittoria"),
    ("narra", "A Vittoria gira a taça devagar. Por um tempo, as duas ficam só ouvindo a cozinha esfriar."),
    ("fala", "vittoria", "Posso te contar uma coisa? Uma coisa que eu não conto nem para a Dona Graça?"),
    ("fala", "player", "Pode."),
    ("fala", "vittoria", "Eu tenho medo de gostar demais de alguém que vive igual a mim. Correndo. Com a agenda lotada.",
     "shy"),
    ("fala", "vittoria", "Duas agendas cheias não fazem uma vida. Fazem duas empresas que se cruzam de vez em quando, "
                         "às onze da noite, numa Trattoria fechada."),
    ("emote", "player", "reticencias"),
    ("escolha", "O que dizer?", [
        ("Então a gente arruma espaço. Começando por esta mesa.", 80,
         "Começando por esta mesa... Você fala isso com uma calma que dá vontade de acreditar."),
        ("Eu também tenho medo. Mas eu continuo vindo.", 70,
         "Você continua vindo. Toda noite. Eu reparei, sabia? Eu reparo em tudo que é seu."),
        ("Nenhuma empresa minha é mais importante que isto aqui.", 70,
         "Cuidado com o que você diz para uma italiana às onze da noite. A gente leva tudo a sério."),
    ]),
    ("fala", "vittoria", "Tá. Eu vou tentar ter menos medo. Mas só se você continuar sendo a última cliente.", "love"),
    ("fala", "player", "Combinado. A mesa é minha."),
    ("emote", "vittoria", "coracao"),
    ("esperar", 0.6),
    ("fade_out",),
])

NEW_EVENTS = {
    "lucy": {5: dict(scene="lucy_5", mood="smile",
                     lines=["Obrigada por não fugir da conversa no arquivo. Quando quiser, o píer está lá.",
                            "Eu guardei a pasta de volta. Algumas coisas não são matéria."])},
    "vittoria": {5: dict(scene="vittoria_5", mood="happy", gift="vinho",
                         lines=["A foto da inauguração saiu na CatCo. Você aparece no canto, segurando um vaso. Perfeita.",
                                "Ainda não acredito que você apareceu às seis. Ninguém aparece às seis."]),
                 7: dict(scene="vittoria_7", mood="love",
                         lines=["Sobre o que eu disse na Trattoria... eu falei sério. Mas estou com menos medo hoje.",
                                "A mesa do canto agora tem uma plaquinha: \"reservada\". Adivinha para quem."])},
}
for _k, _evs in NEW_EVENTS.items():
    for _h, _ev in _evs.items():
        NPCS[_k].setdefault("events", {}).setdefault(_h, _ev)

eventos.TITLES.update({"lucy_5": "Lucy: o arquivo da CatCo", "vittoria_5": "Vittoria: a inauguração às 6h",
                       "vittoria_7": "Vittoria: a mesa da Letícia"})

# quem já viu o evento seguinte não recebe o novo fora de ordem
_AFTER = {"lucy:5": "lucy:6", "vittoria:5": "vittoria:6", "vittoria:7": "vittoria:8"}


def load_state(g, d):
    for new, later in _AFTER.items():
        if later in g.events_seen:
            g.events_seen.add(new)
