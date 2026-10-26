"""Dados do jogo: projetos, itens, peixes, receitas, livros e lojas.

Personagens e falas ficam em characters.py.
"""

# --------------------------------------------------------------------------
# Projetos (o equivalente às sementes). days = dias trabalhados até ficar pronto.
# --------------------------------------------------------------------------
PROJECTS = {
    "relatorio": dict(name="Relatório de Mercado", days=2, cost=20, value=45, quarters=[1, 2, 3, 4],
                      color=(120, 200, 255), icon="doc"),
    "software": dict(name="Software Empresarial", days=4, cost=50, value=120, quarters=[1, 2],
                     color=(90, 220, 170), icon="disk"),
    "demeter": dict(name="Projeto Demeter", days=5, cost=90, value=210, quarters=[2, 3],
                    color=(120, 230, 110), icon="dna"),
    "athena": dict(name="Projeto Athena", days=6, cost=120, value=300, quarters=[1, 3],
                   color=(190, 120, 255), icon="chip"),
    "hera": dict(name="Projeto Hera", days=7, cost=150, value=360, quarters=[3, 4],
                 color=(255, 190, 90), icon="shield"),
    "nike": dict(name="Projeto Nike", days=8, cost=170, value=420, quarters=[4, 1],
                 color=(255, 120, 120), icon="robot"),
    "artemis": dict(name="Projeto Artemis", days=9, cost=200, value=520, quarters=[2],
                    color=(140, 170, 255), icon="satellite"),
    "hecate": dict(name="Projeto Hecate", days=12, cost=400, value=1100, quarters=[1, 2, 3, 4],
                   color=(255, 90, 200), icon="orb", locked_flag="hecate"),
}

PRODUCT_NAMES = {
    "relatorio": "Relatório de Mercado", "software": "Licença de Software", "demeter": "Biomaterial Demeter",
    "athena": "Núcleo Athena", "hera": "Sistema Hera", "nike": "Exotraje Nike", "artemis": "Satélite Artemis",
    "hecate": "Artefato Hecate",
}

# --------------------------------------------------------------------------
# Peixes. where: sea (mar/píer) | pond (lago do parque)
# hours: faixa de horário em minutos do dia (pode passar da meia-noite: até 1560)
# diff: dificuldade 1-100 (movimento do peixe no minigame)
# --------------------------------------------------------------------------
FISH = {
    "sardinha": dict(name="Sardinha", value=30, diff=15, where="sea", quarters=[1, 2, 3, 4], hours=(360, 1560),
                     color=(170, 190, 210)),
    "robalo": dict(name="Robalo", value=75, diff=35, where="sea", quarters=[1, 2, 3, 4], hours=(360, 1200),
                   color=(140, 160, 150)),
    "linguado": dict(name="Linguado", value=90, diff=40, where="sea", quarters=[2, 3], hours=(360, 1560),
                     color=(190, 160, 120)),
    "lula": dict(name="Lula", value=110, diff=50, where="sea", quarters=[1, 2, 3, 4], hours=(1080, 1560),
                 color=(240, 190, 200)),
    "polvo": dict(name="Polvo", value=150, diff=65, where="sea", quarters=[3, 4, 1], hours=(360, 1560),
                  color=(220, 110, 140)),
    "atum": dict(name="Atum", value=180, diff=70, where="sea", quarters=[3, 4], hours=(360, 1140),
                 color=(80, 110, 170)),
    "peixe_espada": dict(name="Peixe-Espada", value=220, diff=78, where="sea", quarters=[1, 2, 3, 4],
                         hours=(360, 1560), weather="chuva", color=(180, 200, 230)),
    "kryptoniano": dict(name="Peixe Kryptoniano", value=900, diff=92, where="sea", quarters=[4],
                        hours=(1260, 1560), weather="chuva", color=(90, 255, 120), legendary=True),
    "tilapia": dict(name="Tilápia", value=35, diff=18, where="pond", quarters=[1, 2, 3, 4], hours=(360, 1560),
                    color=(150, 150, 170)),
    "carpa": dict(name="Carpa", value=50, diff=28, where="pond", quarters=[1, 2, 3, 4], hours=(360, 1560),
                  color=(190, 160, 90)),
    "truta": dict(name="Truta Arco-Íris", value=95, diff=48, where="pond", quarters=[1, 4], hours=(360, 1200),
                  color=(220, 150, 170)),
    "bagre": dict(name="Bagre", value=85, diff=45, where="pond", quarters=[1, 2, 3, 4], hours=(1140, 1560),
                  color=(120, 110, 90)),
    "koi": dict(name="Carpa Koi Dourada", value=320, diff=82, where="pond", quarters=[2], hours=(600, 1080),
                color=(255, 180, 60)),
}
JUNK = {"lata": dict(name="Lata Amassada", value=1), "jornal": dict(name="CatCo Molhada", value=1)}

# --------------------------------------------------------------------------
# Itens
# kind: proposal | product | food | gift | ingredient | dish | fish | junk | tool | bait | book
# value = preço de venda na Mesa de Contratos (itens vendáveis)
# --------------------------------------------------------------------------
ITEMS = {}
for _key, _p in PROJECTS.items():
    ITEMS["prop_" + _key] = dict(name="Proposta: " + _p["name"], kind="proposal", project=_key,
                                 price=_p["cost"], icon="folder", color=_p["color"],
                                 desc=f"Inicia o {_p['name']} numa bancada. Pronto em {_p['days']} dias de trabalho.")
    ITEMS[_key] = dict(name=PRODUCT_NAMES[_key], kind="product", value=_p["value"], icon=_p["icon"],
                       color=_p["color"], desc=f"Coloque na Mesa de Contratos: vale ${_p['value']}.")

for _key, _f in FISH.items():
    ITEMS[_key] = dict(name=_f["name"], kind="fish", value=_f["value"], icon="fish", color=_f["color"],
                       desc=f"Peixe. Vale ${_f['value']}. Bom para cozinhar ou para o aquário.")
for _key, _j in JUNK.items():
    ITEMS[_key] = dict(name=_j["name"], kind="junk", value=_j["value"], icon="can" if _key == "lata" else "paper",
                       color=(150, 150, 160), desc="Lixo. Pelo menos você limpou o mar.")


def _food(name, energy, price, icon, color, desc=""):
    return dict(name=name, kind="food", energy=energy, price=price, icon=icon, color=color,
                desc=desc or f"+{energy} de energia. Aperte F para consumir.")


ITEMS.update({
    "expresso": _food("Expresso", 25, 15, "cup", (120, 80, 50)),
    "cappuccino": _food("Cappuccino", 30, 22, "cup", (200, 160, 120)),
    "sanduiche": _food("Sanduíche Natural", 50, 40, "sandwich", (230, 190, 110)),
    "rosquinha": _food("Rosquinha", 15, 25, "donut", (240, 140, 190), "+15 de energia. Alguém no laboratório ama isso."),
    "croissant": _food("Croissant", 20, 20, "croissant", (230, 170, 90)),
    "pizza": _food("Pizza Margherita", 60, 45, "pizza", (230, 90, 70)),
    "lasanha": _food("Lasanha da Casa", 85, 70, "lasagna", (220, 120, 70)),
    "tiramisu": _food("Tiramisù", 30, 50, "cake", (200, 170, 130), "+30 de energia. Sobremesa clássica italiana."),
    "petiscos": _food("Porção de Petiscos", 35, 30, "fries", (240, 200, 90)),
    "soda": _food("Soda Italiana", 15, 10, "soda", (120, 200, 255)),
    "drink": _food("Drinque da Casa", 10, 20, "drink", (200, 80, 160), "+10 de energia. Especialidade do Noonan's."),
    # presentes
    "flores": dict(name="Buquê de Flores", kind="gift", price=60, icon="flower", color=(255, 120, 170),
                   desc="Um presente clássico."),
    "girassois": dict(name="Girassóis", kind="gift", price=70, icon="flower", color=(255, 210, 60),
                      desc="Alegres como um dia de sol."),
    "rosas": dict(name="Buquê de Rosas Vermelhas", kind="gift", price=250, icon="flower", color=(220, 30, 60),
                  desc="Dê a quem você ama (8 corações) para começar a namorar."),
    "pingente": dict(name="Pingente de Compromisso", kind="gift", price=1500, icon="pendant", color=(184, 76, 255),
                     desc="Para a pessoa com quem você namora, aos 10 corações. Um pedido para morar juntas."),
    "vinho": dict(name="Vinho Tinto", kind="gift", price=120, icon="wine", color=(150, 30, 60),
                  desc="Safra excelente. Presente sofisticado."),
    "livro": dict(name="Livro Raro", kind="gift", price=90, icon="book", color=(90, 120, 200),
                  desc="Primeira edição. Para quem gosta de ler."),
    "policial": dict(name="Romance Policial", kind="gift", price=45, icon="book", color=(60, 60, 70),
                     desc="Um mistério daqueles que não se larga."),
    # ferramentas
    "vara": dict(name="Vara de Pesca", kind="tool", price=0, icon="rod", color=(160, 110, 60),
                 desc="Selecione e aperte E de frente para a água."),
    "vara_fibra": dict(name="Vara de Fibra de Carbono", kind="tool", price=650, icon="rod", color=(60, 60, 70),
                       desc="Barra de pesca maior. Muito mais fácil fisgar."),
    "isca": dict(name="Isca", kind="bait", price=5, icon="bait", color=(200, 120, 90),
                 desc="Peixes mordem bem mais rápido. Usada automaticamente ao pescar."),
})

INGREDIENTS = {
    "arroz": ("Arroz", 15, (240, 240, 230)), "massa": ("Massa Fresca", 12, (240, 220, 140)),
    "farinha": ("Farinha", 10, (245, 240, 230)), "ovos": ("Ovos", 14, (250, 240, 220)),
    "leite": ("Leite", 10, (240, 244, 250)), "queijo": ("Queijo", 25, (250, 210, 80)),
    "tomate": ("Tomate", 8, (230, 60, 50)), "manjericao": ("Manjericão", 6, (80, 170, 80)),
    "cogumelos": ("Cogumelos", 18, (190, 160, 130)), "limao": ("Limão", 5, (170, 220, 80)),
    "chocolate": ("Chocolate", 20, (110, 70, 50)),
}
ING_ICONS = {"arroz": "sack", "farinha": "sack", "ovos": "egg", "leite": "milk", "queijo": "cheese",
             "massa": "pasta", "manjericao": "leaf", "cogumelos": "mushroom", "chocolate": "chocbar"}
for _key, (_n, _p, _c) in INGREDIENTS.items():
    ITEMS[_key] = dict(name=_n, kind="ingredient", price=_p, icon=ING_ICONS.get(_key, "ingredient"), color=_c,
                       desc="Ingrediente. Use no fogão da cobertura.")

# --------------------------------------------------------------------------
# Horta do terraço. days = noites regadas até ficar pronta. regrow = dias para
# produzir de novo depois da colheita (None = a planta sai do canteiro).
# --------------------------------------------------------------------------
CROPS = {
    "manjericao": dict(name="Manjericão", seed=10, days=2, item="manjericao", qty=2, regrow=None, color=(80, 170, 80)),
    "tomate": dict(name="Tomate", seed=18, days=3, item="tomate", qty=3, regrow=2, color=(230, 60, 50)),
    "morango": dict(name="Morango", seed=30, days=4, item="morango", qty=2, regrow=2, color=(236, 50, 80)),
    "girassol": dict(name="Girassol", seed=25, days=4, item="girassois", qty=1, regrow=None, color=(255, 210, 60)),
    "rosa": dict(name="Roseira", seed=40, days=5, item="rosa_jardim", qty=1, regrow=3, color=(240, 100, 150)),
    "abobora": dict(name="Abóbora", seed=35, days=6, item="abobora", qty=1, regrow=None, color=(240, 140, 40)),
}
for _key, _c in CROPS.items():
    ITEMS["semente_" + _key] = dict(name=f"Sementes de {_c['name']}", kind="seed", crop=_key, price=_c["seed"],
                                    icon="seed", color=_c["color"],
                                    desc=f"Plante num canteiro do terraço e regue todo dia. Pronto em {_c['days']} dias.")
ITEMS.update({
    "morango": dict(name="Morangos", kind="crop", value=45, energy=12, icon="berry", color=(236, 50, 80),
                    desc="Da sua horta! +12 de energia (F), vale $45. Bom para sobremesas."),
    "rosa_jardim": dict(name="Rosa do Jardim", kind="crop", value=110, icon="rose", color=(240, 100, 150),
                        desc="Uma rosa cor-de-rosa cultivada por você. Vale $110. Ótimo presente."),
    "abobora": dict(name="Abóbora", kind="crop", value=220, icon="pumpkin", color=(240, 140, 40),
                    desc="Enorme e laranjinha. Vale $220. Dá uma sopa incrível."),
})

# --------------------------------------------------------------------------
# Coletáveis: aparecem todo dia na praia e no parque. Passe por cima para pegar.
# --------------------------------------------------------------------------
FORAGE = {
    "concha": dict(name="Concha", value=25, where="beach", weight=50, icon="shell", color=(250, 214, 196)),
    "vidro_mar": dict(name="Vidro do Mar", value=35, where="beach", weight=26, icon="seaglass", color=(120, 210, 200)),
    "estrela_mar": dict(name="Estrela-do-mar", value=45, where="beach", weight=16, icon="star", color=(250, 150, 90)),
    "coral": dict(name="Coral", value=80, where="beach", weight=8, icon="coral", color=(250, 110, 130)),
    "flor_silvestre": dict(name="Flores Silvestres", value=20, where="park", weight=50, icon="wildflower",
                           color=(200, 160, 255)),
    "amora": dict(name="Amoras", value=30, where="park", weight=24, icon="berry", color=(110, 50, 120), energy=10),
    "trevo4": dict(name="Trevo de 4 Folhas", value=150, where="park", weight=5, icon="clover", color=(80, 190, 90)),
}
for _key, _f in FORAGE.items():
    ITEMS[_key] = dict(name=_f["name"], kind="forage", value=_f["value"], icon=_f["icon"], color=_f["color"],
                       desc=f"Achado na {'praia' if _f['where'] == 'beach' else 'grama do parque'}. Vale ${_f['value']}. "
                            f"Dá para vender ou presentear.")
    if _f.get("energy"):
        ITEMS[_key]["energy"] = _f["energy"]
FORAGE_EXTRA = {"park": [("cogumelos", 22)]}      # ingredientes que também aparecem no parque

ITEMS.update({
    "pipoca": _food("Pipoca", 20, 15, "popcorn", (250, 230, 150), "+20 de energia. Doce e salgada, do Cine National."),
    "vitamina": _food("Vitamina C Efervescente", 35, 30, "soda", (250, 170, 60),
                      "+35 de energia. Da Farmácia Conti Moretti."),
    "cha_camomila": _food("Chá de Camomila", 20, 12, "cup", (240, 220, 140), "+20 de energia. Calma em forma de chá."),
    "barra_cereal": _food("Barra de Cereal", 15, 8, "chocbar", (200, 160, 100)),
    "isotonico": _food("Isotônico", 18, 10, "soda", (120, 220, 200)),
    "kit_cuidado": dict(name="Kit Autocuidado", kind="gift", price=80, icon="pendant", color=(110, 200, 160),
                        desc="Hidratante, chá e uma vela cheirosa. Um presente carinhoso."),
    "petisco_pet": dict(name="Petisco de Pet", kind="treat", price=12, icon="bone", color=(220, 170, 120),
                        desc="Selecione e faça carinho no seu bichinho: ele fica muito feliz."),
})

# --------------------------------------------------------------------------
# Receitas (fogão da cobertura). "fish" = qualquer peixe.
# --------------------------------------------------------------------------
RECIPES = {
    "panquecas": dict(name="Panquecas", needs={"farinha": 1, "ovos": 1, "leite": 1}, energy=45, value=80,
                      color=(230, 180, 100), icon="pancake"),
    "peixe_grelhado": dict(name="Peixe Grelhado", needs={"fish": 1, "limao": 1}, energy=55, value=120,
                           color=(210, 150, 90), icon="dish"),
    "massa_pesto": dict(name="Massa ao Pesto", needs={"massa": 1, "manjericao": 1, "queijo": 1}, energy=60,
                        value=110, color=(110, 180, 80), icon="dish"),
    "risoto": dict(name="Risoto de Cogumelos", needs={"arroz": 1, "cogumelos": 1, "queijo": 1}, energy=70,
                   value=140, color=(220, 200, 150), icon="dish"),
    "bolo": dict(name="Bolo de Chocolate", needs={"farinha": 1, "ovos": 1, "chocolate": 1}, energy=50, value=150,
                 color=(110, 70, 50), icon="cake"),
    "sushi": dict(name="Sushi", needs={"arroz": 1, "fish": 2}, energy=80, value=260, color=(240, 120, 110),
                  icon="sushi", book="livro_mundo"),
    "moqueca": dict(name="Moqueca", needs={"fish": 2, "tomate": 1, "limao": 1}, energy=90, value=280,
                    color=(240, 140, 50), icon="dish", book="livro_mundo"),
    "lasanha_nonna": dict(name="Lasanha da Nonna", needs={"massa": 1, "queijo": 1, "tomate": 1, "leite": 1},
                          energy=100, value=300, color=(220, 110, 60), icon="lasagna", book="livro_nonna"),
    "caprese": dict(name="Salada Caprese", needs={"tomate": 2, "manjericao": 1, "queijo": 1}, energy=40, value=130,
                    color=(230, 80, 70), icon="dish"),
    "torta_morango": dict(name="Torta de Morango", needs={"farinha": 1, "ovos": 1, "morango": 2}, energy=55, value=210,
                          color=(236, 70, 100), icon="cake"),
    "sopa_abobora": dict(name="Sopa de Abóbora", needs={"abobora": 1, "leite": 1}, energy=75, value=320,
                         color=(240, 150, 50), icon="dish"),
}
for _key, _r in RECIPES.items():
    ITEMS[_key] = dict(name=_r["name"], kind="dish", energy=_r["energy"], value=_r["value"], icon=_r["icon"],
                       color=_r["color"], desc=f"+{_r['energy']} de energia (F). Vale ${_r['value']}. Ótimo presente.")

# --------------------------------------------------------------------------
# Livros da Bayside Books: ler (F) dá um bônus permanente.
# --------------------------------------------------------------------------
BOOKS = {
    "livro_pesca": dict(name="Manual do Pescador", price=300, flag="book_fish",
                        effect="A barra de pesca fica 30% maior."),
    "livro_energia": dict(name="Gestão do Tempo para CEOs", price=500, flag="book_energy",
                          effect="+15 de energia máxima."),
    "livro_nonna": dict(name="Receitas da Nonna", price=250, flag="book_nonna",
                        effect="Aprende a Lasanha da Nonna."),
    "livro_mundo": dict(name="Cozinha do Mundo", price=350, flag="book_world",
                        effect="Aprende Sushi e Moqueca."),
    "livro_mercado": dict(name="Mercados & Ações", price=400, flag="book_stocks",
                          effect="Libera investimentos em ações LCORP no seu computador."),
}
for _key, _b in BOOKS.items():
    ITEMS[_key] = dict(name=_b["name"], kind="book", price=_b["price"], icon="book", color=(180, 120, 60),
                       desc=f"Leia com F: {_b['effect']}")

SELLABLE = {"product", "fish", "dish", "junk", "crop", "forage"}

# --------------------------------------------------------------------------
# Lojas. Abertas quando o atendente está no local.
# --------------------------------------------------------------------------
SHOPS = {
    "cafe": dict(title="Grão Nobre", subtitle="Café, comida e presentes.",
                 stock=["expresso", "cappuccino", "croissant", "sanduiche", "rosquinha", "flores", "vinho", "livro"],
                 discount_flag="rafa_discount"),
    "market": dict(title="Mercado Central", subtitle="Ingredientes frescos, flores e presentes especiais.",
                   stock=["arroz", "massa", "farinha", "ovos", "leite", "queijo", "tomate", "manjericao",
                          "cogumelos", "limao", "chocolate", "flores", "girassois", "vinho", "rosas", "pingente",
                          "semente_manjericao", "semente_tomate", "semente_morango", "semente_girassol",
                          "semente_rosa", "semente_abobora"]),
    "books": dict(title="Bayside Books", subtitle="Livros que mudam vidas (e dão bônus permanentes).",
                  stock=["livro", "policial", "livro_pesca", "livro_energia", "livro_nonna", "livro_mundo",
                         "livro_mercado"]),
    "trattoria": dict(title="Ricci Trattoria", subtitle="Cozinha italiana de verdade. Grazie!",
                      stock=["pizza", "lasanha", "tiramisu", "soda", "vinho"], discount_flag="vittoria_family"),
    "bar": dict(title="Noonan's", subtitle="Bebidas, petiscos e fliperama.",
                stock=["soda", "drink", "petiscos", "vinho"]),
    "pharmacy": dict(title="Farmácia Conti Moretti", subtitle="Sua saúde em primeiro lugar.",
                     stock=["vitamina", "cha_camomila", "isotonico", "barra_cereal", "kit_cuidado"]),
    "bait": dict(title="Barraca do Joca", subtitle="Tudo pra pescaria. 'Peixe bom é peixe fisgado!'",
                 stock=["isca", "vara_fibra", "limao"]),
}

CAFE_STOCK = SHOPS["cafe"]["stock"]

FLAG_LABELS = {
    "sam_bonus": "Contratos renegociados: +10% em tudo que você vende.",
    "hecate": "Projeto Hecate liberado no Terminal P&D.",
    "drone": "Drone de laboratório: trabalha nos projetos toda manhã.",
    "jess_energy": "Agenda otimizada: +20 de energia máxima.",
    "rafa_discount": "Desconto de amiga: 20% no Grão Nobre.",
    "vittoria_family": "Família Ricci: 20% de desconto na Trattoria.",
    "nia_scoop": "Fonte da CatCo: a ação LCORP ganha impulso extra.",
    "joca_spot": "Segredo do Joca: peixes raros aparecem mais.",
    "book_fish": "Manual do Pescador: barra de pesca 30% maior.",
    "book_energy": "Gestão do Tempo: +15 de energia máxima.",
    "book_nonna": "Receita aprendida: Lasanha da Nonna.",
    "book_world": "Receitas aprendidas: Sushi e Moqueca.",
    "book_stocks": "Investimentos liberados no computador.",
    "coffee_machine": "Cafeteira executiva: um expresso grátis por dia.",
    "cmh_checkup": "Check-up completo no Conti Moretti: +15 de energia máxima.",
    "cmh_wing": "Ala Luthor inaugurada no Conti Moretti Hospitais.",
    "cmh_discount": "Dra. Milany: consultas no Conti Moretti pela metade do preço.",
    "cmh_care": "Dra. Meredith: se desmaiar, o hospital não cobra nada.",
    "cmh_contract": "Dra. Cristina: contrato de manutenção, +$200 toda segunda.",
    "lexie_focus": "Dra. Lexie: trabalhar no laboratório gasta 5 a menos de energia.",
}

NEWS = [
    "CatCo Magazine elege a Luthor Corp a empresa mais inovadora do ano.",
    "Apagão de domingo: Lucy Williams e Barry Allen investigam a infraestrutura da cidade.",
    "Analistas preveem trimestre forte para o setor aeroespacial.",
    "Ricci Trattoria é eleita a melhor massa de National City. 'É a receita da minha nonna', diz a chef.",
    "Trânsito intenso na Avenida Siegel. Linhas expressas operam com atraso no centro.",
    "Café Grão Nobre é eleito o melhor expresso da cidade pelo terceiro ano.",
    "Bayside Books registra recorde de movimento depois do apagão.",
    "Pescadores relatam brilho verde no mar em noites de chuva. Lenda urbana?",
    "Noonan's anuncia novo recorde no fliperama 'Meteoro'. Quem vai superar?",
]

TIPS = [
    "Dica: projetos só avançam nos dias em que você trabalha neles na bancada.",
    "Dica: a Mesa de Contratos e a caixa de coleta do píer vendem produtos, peixes e pratos à noite.",
    "Dica: conversar todo dia aumenta a amizade. Presentes ajudam ainda mais.",
    "Dica: o Joca, no píer, vende iscas. Peixes mordem bem mais rápido com isca.",
    "Dica: cozinhe no fogão da cobertura. Pratos dão muita energia e são ótimos presentes.",
    "Dica: a Bayside Books vende livros com bônus permanentes.",
    "Dica: F11 alterna a tela cheia.",
    "Dica: I abre a mochila. Use para organizar os 24 espaços.",
    "Dica: a porta de vidro da sala leva ao terraço. Plante sementes do Mercado e regue todo dia.",
    "Dica: conchas e flores aparecem todo dia na praia e no parque. É só passar por cima.",
    "Dica: a barraquinha de adoção fica no calçadão, perto do Noonan's. Que tal um bichinho?",
    "Dica: à noite, a jukebox do Noonan's vira karaokê.",
    "Dica: o Cine National está aberto! Ótimo lugar para um encontro.",
    "Dica: o Conti Moretti Hospitais agenda consultas na recepção. Cada especialidade dá um bônus no dia.",
    "Dica: no computador, você escolhe quantas ações LCORP quer comprar ou vender.",
]

GOALS = [
    ("launch10", "Lançar 10 projetos"),
    ("money10k", "Acumular $ 10.000"),
    ("stock150", "Levar a ação LCORP a $ 150"),
    ("friends3", "Chegar a 3 corações com toda a equipe"),
    ("stations12", "Expandir o laboratório para 12 bancadas"),
    ("hecate", "Lançar o Projeto Hecate"),
    ("fish10", "Pescar 10 espécies diferentes"),
    ("aquarium", "Completar o aquário (13 peixes)"),
    ("cook5", "Cozinhar 5 receitas diferentes"),
    ("romance", "Começar a namorar"),
    ("partner", "Morar junto com alguém especial"),
    ("arcade", "Fazer 40 pontos no fliperama Meteoro"),
    ("garden", "Colher 15 vezes na horta do terraço"),
    ("forage", "Encontrar todos os 7 coletáveis"),
    ("pet", "Adotar um bichinho"),
    ("karaoke", "Tirar nota S no karaokê"),
    ("cinema", "Assistir a 5 filmes no Cine National"),
    ("checkup", "Check-up completo no Conti Moretti (12 especialidades)"),
]
