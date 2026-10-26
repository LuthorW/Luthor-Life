"""As lideranças clínicas do Conti Moretti Hospitais, como personagens completas:
dá para conversar, presentear, fazer amizade e ver eventos de coração.

A rotina de cada médica é montada dia a dia (veja schedule_for): plantão alternando
entre consultórios, internação e recepção, almoço fora do hospital e folgas. Nenhuma
repete o mesmo posto em sequência, duas nunca dividem o mesmo lugar ao mesmo tempo
e o lugar do almoço muda todo dia.
"""

DOCTOR_KEYS = ["yang", "meredith", "milany", "lexie", "izzie", "addison"]


def _look(hair, skin, cloth, accent, pants, shoes, style, eyes):
    return dict(hair=hair, skin=skin, cloth=cloth, accent=accent, pants=pants, shoes=shoes, style=style, eyes=eyes)


COAT, GREEN, GREEN2, COPPER = (244, 244, 248), (18, 63, 53), (29, 89, 74), (183, 123, 101)
_OFF = [(360, None, 0, 0, "down")]

DOCTORS = {
    "yang": dict(
        name="Dra. Cristina Yang", short="Cristina", role="Direção Médica · Conti Moretti",
        look=_look((24, 18, 20), (232, 196, 160), COAT, GREEN, GREEN2, (30, 30, 36), "wavy", (60, 40, 30)),
        portrait="dra_yang.jpg",
        gifts=dict(love=["expresso", "athena", "hecate"], like=["sushi", "relatorio", "cappuccino", "trevo4"],
                   dislike=["flores", "girassois", "rosquinha"]),
        lines=dict(
            low=["Se não for urgente, agenda na recepção. Eu não faço consulta de corredor.",
                 "Cirurgia às duas. Fala rápido.",
                 "Você é a CEO da Luthor Corp? Ótimo. Precisamos de um robô cirúrgico novo.",
                 "Eu não sou simpática. Eu sou excelente. São coisas diferentes."],
            mid=["Seu laboratório faz equipamento médico? Porque deveria.",
                 "A Meredith diz que eu preciso de amigas fora do hospital. Você conta. Eu acho.",
                 "Li o artigo do Brainy sobre nanotecnologia. Ele é irritante. E genial. Gosto dos dois."],
            high=["Você é a minha pessoa fora daqui. Não conta pra Meredith que eu disse isso.",
                  "Se um dia eu montar um centro cirúrgico de ponta, quero a Luthor Corp junto."],
            evening=["Plantão acabou. Agora é só eu, um expresso e zero pacientes."],
            rain=["Chuva = acidente de trânsito = pronto-socorro cheio. Não sai de casa."],
            weekend=["Folga. Estou entediada. Alguém aí tem uma cirurgia?"],
        ),
        reactions=dict(love="...Isso é exatamente o que eu queria. Como você sabia? Não responde.",
                       like="Útil. Obrigada.", neutral="Hm. Obrigada.",
                       dislike="Flores? Eu vou dar pra alguém da internação. Sem ofensa."),
        events={3: dict(flag="cmh_contract", lines=[
            "Convenci a diretoria: a Luthor Corp vai cuidar da manutenção dos nossos equipamentos.",
            "Contrato fechado. Toda segunda-feira cai o pagamento na sua conta.",
            "Não me agradece. Só não deixa nada quebrar."]),
                6: dict(gift="vitamina", lines=["Toma. Vitamina. Eu sei que você não come direito.",
                                                "Eu me importo. Pronto, falei. Agora vai embora."])},
    ),
    "meredith": dict(
        name="Dra. Meredith Grey", short="Meredith", role="Direção Médica · Conti Moretti",
        look=_look((206, 170, 110), (244, 214, 190), COAT, COPPER, GREEN2, (40, 34, 40), "long", (90, 150, 130)),
        portrait="dra_meredith.jpg",
        gifts=dict(love=["vinho", "panquecas", "policial"], like=["cha_camomila", "livro", "tiramisu", "concha"],
                   dislike=["lata", "isotonico"]),
        lines=dict(
            low=["Dormiu bem? Você tem cara de quem dormiu três horas.",
                 "A jornada do paciente começa no acolhimento. Bem-vinda ao Conti Moretti.",
                 "Minha mãe era cirurgiã. Eu prometi que ia ser diferente. Virei cirurgiã. Diferente."],
            mid=["Cuidado com quem você deixa entrar no seu coração. Conselho de médica. E de amiga.",
                 "Às vezes eu venho pra cá só pra ouvir os monitores. É estranho que isso me acalme?",
                 "A Cristina gosta de você. Ela nunca vai admitir. Mas gosta."],
            high=["Você é família agora. E família aqui é quem aparece quando importa.",
                  "Obrigada por cuidar da cidade. E deixa a gente cuidar de você, tá?"],
            evening=["Dia longo. Hora de uma taça de vinho e silêncio."],
            rain=["Chuva me lembra de Seattle. Coisa boa e coisa ruim."],
            weekend=["Folga com as crianças. Parque, sorvete e ninguém sangrando."],
        ),
        reactions=dict(love="Ah, você me conhece! Obrigada, de coração.", like="Que gentil. Obrigada!",
                       neutral="Obrigada, querida.", dislike="Ah... tudo bem. A intenção é que conta."),
        events={3: dict(flag="cmh_care", lines=[
            "Fiz uma coisa. Coloquei seu nome na lista de cuidado prioritário.",
            "Se você desmaiar de cansaço de novo, a conta é por nossa conta.",
            "Mas, por favor: não me faça usar isso."])},
    ),
    "milany": dict(
        name="Dra. Milany Moretti", short="Milany", role="Centro Cardiovascular · Conti Moretti",
        look=_look((70, 44, 32), (226, 186, 156), COAT, COPPER, GREEN, (60, 30, 30), "long", (100, 70, 40)),
        portrait="dra_milany.jpg",
        gifts=dict(love=["rosa_jardim", "tiramisu", "torta_morango"], like=["vinho", "flores", "cappuccino", "kit_cuidado"],
                   dislike=["rosquinha", "lata"]),
        lines=dict(
            low=["Bem-vinda ao Conti Moretti! Sua saúde em primeiro lugar.",
                 "Coração é músculo. Precisa de exercício, descanso e gente boa por perto.",
                 "Se a pressão subir na reunião do conselho, respira. Quatro segundos dentro, seis fora."],
            mid=["Meu avô fundou o primeiro consultório da família com uma maca e muita coragem.",
                 "Cuidado que inspira confiança. Não é só o slogan, é o que eu tento fazer todo dia.",
                 "Excelência que também sabe acolher. Precisão clínica, presença humana."],
            high=["Você virou alguém com quem eu conto. Isso é raro pra mim.",
                  "Quando eu penso em parceria, penso em você e na Luthor Corp."],
            evening=["Plantão encerrado. Meu coração (o literal) agradece."],
            rain=["Dia de chuva o hospital fica mais calmo. Eu aproveito para revisar prontuários."],
            weekend=["No fim de semana eu caminho na orla. Cardiologista dá o exemplo."],
        ),
        reactions=dict(love="Que lindo! Você acertou em cheio. Obrigada!", like="Que carinho, obrigada!",
                       neutral="Obrigada, de verdade.", dislike="Hm... rosquinha? Como cardiologista, vou fingir que não vi."),
        events={3: dict(flag="cmh_discount", lines=[
            "Conversei com a diretoria do Conti Moretti.",
            "A partir de hoje, suas consultas saem pela metade do preço. Prevenção não pode ter barreira.",
            "Sua saúde em primeiro lugar. Literalmente."])},
    ),
    "lexie": dict(
        name="Dra. Lexie Grey", short="Lexie", role="Centro de Neurociências · Conti Moretti",
        look=_look((96, 52, 36), (246, 218, 196), COAT, GREEN2, GREEN2, (40, 40, 46), "short", (110, 80, 50)),
        portrait="dra_lexie.jpg",
        gifts=dict(love=["livro", "livro_mercado", "bolo"], like=["policial", "croissant", "pipoca", "estrela_mar"],
                   dislike=["jornal", "drink"]),
        lines=dict(
            low=["Eu tenho memória fotográfica. Lembro de todas as suas manchetes na CatCo.",
                 "O cérebro consome 20% da sua energia. O seu deve consumir uns 40.",
                 "Sono é quando o cérebro faz a faxina. Não pule a faxina."],
            mid=["Fiz uma lista de 47 curiosidades sobre neurônios. Quer ouvir? Só as dez primeiras?",
                 "A Meredith é minha meia-irmã. É complicado. Mas é bom.",
                 "Você e o Brainy deviam montar um laboratório de neurotecnologia. Eu topo consultoria."],
            high=["Lembro exatamente da primeira vez que você sorriu aqui. Memória fotográfica tem vantagens.",
                  "Você é uma das pessoas mais interessantes que eu conheço. E eu conheço muita gente."],
            evening=["Vou ler um artigo de neurociência e dormir em cima dele. Literalmente."],
            rain=["Chuva melhora a concentração. É ciência. Mais ou menos."],
            weekend=["Bayside Books no sábado é meu ritual sagrado."],
        ),
        reactions=dict(love="Ai, eu AMEI! Eu vou lembrar disso pra sempre. Literalmente.", like="Que legal, obrigada!",
                       neutral="Obrigada!", dislike="Ah... obrigada. Vou guardar. Em algum lugar."),
        events={3: dict(flag="lexie_focus", lines=[
            "Montei pra você uma rotina de foco baseada em neurociência. Pausas, água e respiração.",
            "Seguindo isso, trabalhar no laboratório vai cansar bem menos.",
            "Te mandei por e-mail. Com bibliografia. Óbvio."])},
    ),
    "izzie": dict(
        name="Dra. Izzie Stevens", short="Izzie", role="Centro de Oncologia · Conti Moretti",
        look=_look((240, 214, 140), (248, 222, 200), COAT, (232, 208, 199), GREEN2, (200, 120, 140), "bun", (90, 130, 190)),
        portrait="dra_izzie.jpg",
        gifts=dict(love=["bolo", "torta_morango", "panquecas"], like=["morango", "girassois", "flores", "chocolate"],
                   dislike=["peixe_grelhado", "sardinha"]),
        lines=dict(
            low=["Eu fiz muffins para a ala inteira. Quer um? Brincadeira, acabaram.",
                 "Cuidado multidisciplinar: ninguém cuida de ninguém sozinha.",
                 "Os pacientes adoram quando alguém da Luthor Corp aparece. Volta sempre."],
            mid=["Quando o dia é pesado, eu asso. Ontem foram quatro bolos.",
                 "Sabe o que cura muita coisa? Gente que aparece. Você aparece.",
                 "A Vittoria me ensinou a fazer tiramisù. Eu ensinei a ela a fazer muffin. Empate."],
            high=["Você é sol num dia nublado. Não ri! É sério.",
                  "Se precisar de colo, eu tenho colo e tenho bolo."],
            evening=["Hora de assar alguma coisa e esquecer o dia."],
            rain=["Chuva é dia de forno ligado o dia inteiro."],
            weekend=["Fim de semana é feira, flores e uma receita nova."],
        ),
        reactions=dict(love="AI QUE DELÍCIA! Você é a melhor!", like="Obaa, obrigada!", neutral="Obrigada, linda!",
                       dislike="Peixe? Eu... vou dar pro gato da vizinha. Obrigada mesmo assim!"),
        events={3: dict(gift="bolo", lines=["Fiz um bolo de chocolate só pra você. Inteiro. Não divide.",
                                            "É pra agradecer as visitas. Os pacientes ficam mais felizes quando você vem."])},
    ),
    "addison": dict(
        name="Dra. Addison Montgomery", short="Addison", role="Centro Materno-Infantil · Conti Moretti",
        look=_look((176, 58, 40), (248, 224, 206), COAT, GREEN, (60, 50, 60), (30, 24, 30), "long", (70, 140, 110)),
        portrait="dra_addison.jpg",
        gifts=dict(love=["vinho", "kit_cuidado", "rosa_jardim"], like=["cappuccino", "flores", "caprese", "coral"],
                   dislike=["petiscos", "lata"]),
        lines=dict(
            low=["Saltos de 12 centímetros e plantão de 24 horas. Sim, dá.",
                 "Pediatria, ginecologia e obstetrícia: um andar inteiro de gente nascendo e crescendo.",
                 "Nasceram cinco bebês hoje. Um deles se chama Letícia. Coincidência? Talvez."],
            mid=["Eu morei em Los Angeles por anos. National City tem um charme que LA não tem.",
                 "Uma boa médica escuta. Uma ótima médica escuta e não interrompe.",
                 "Você tem um jeito de chegar nos lugares. Elegância corporativa. Aprovo."],
            high=["Você é das poucas pessoas pra quem eu ligaria às três da manhã.",
                  "Brinde a nós: duas mulheres que não pedem licença pra ser excelentes."],
            evening=["Um vinho tinto e os pés pra cima. Ordem médica."],
            rain=["Chuva? Ótimo dia para nascer. Os bebês não ligam pra meteorologia."],
            weekend=["Domingo de spa. Ninguém me liga, a não ser que esteja em trabalho de parto."],
        ),
        reactions=dict(love="Ah, isso tem estilo. Obrigada, querida.", like="Muito gentil, obrigada!",
                       neutral="Obrigada.", dislike="Petiscos de bar? Fofo. Mas não."),
        events={3: dict(gift="kit_cuidado", lines=["Montei um kit de autocuidado pra você. Hidratante, chá e uma vela.",
                                                   "CEO também precisa de cuidado. Principalmente CEO."])},
    ),
}
for _d in DOCTORS.values():
    _d["schedule"] = dict(default=list(_OFF))
    _d["doctor"] = True

# ---------------------------------------------------------------------------
# Rotina diária
# ---------------------------------------------------------------------------
# postos no hospital (consultórios, internação, recepção e saguão)
HSPOTS = [(3, 2, "down"), (9, 2, "down"), (15, 2, "down"), (21, 5, "up"), (23, 5, "up"), (25, 5, "up"),
          (13, 9, "down"), (18, 13, "left")]
# preenchidos por setup_spots() com lugares exclusivos tirados dos figurantes
LUNCH, LEISURE, EVENING = [], [], []


def setup_spots(crowd):
    """Separa lugares fixos para as médicas, que os figurantes não usam."""
    def take(venue, n, mapn=None):
        pool = crowd.spots.get(venue, [])
        if not pool:
            return []
        step = max(1, len(pool) // n)
        picks = [pool[i * step] for i in range(min(n, len(pool)))]
        for p in picks:
            if p in pool:
                pool.remove(p)
        m = mapn or venue
        return [(m, x, y, d) for (x, y, d) in picks]
    LUNCH[:] = take("cafe", 2) + take("trattoria", 3) + take("park", 2, "city")
    LEISURE[:] = take("books", 2) + take("cinema", 2) + take("beach", 2, "city") + take("market", 1) + \
        take("park", 1, "city")
    EVENING[:] = take("bar", 3) + take("trattoria", 2) + take("cinema", 2)


def works(idx, day):
    return (day + idx * 2) % 7 not in (0, 4)


def schedule_for(key, day):
    idx = DOCTOR_KEYS.index(key)
    sch = [(360, None, 0, 0, "down")]
    if works(idx, day):
        start = 420 + idx * 15
        end = 1080 + idx * 20
        n = len(HSPOTS)
        for k, t in enumerate((start, 600, 780, 930)):
            x, y, d = HSPOTS[(idx + day + k * 3) % n]
            sch.append((t, "hospital", x, y, d))
            if t == 600 and LUNCH:
                m, lx, ly, ld = LUNCH[(idx + day) % len(LUNCH)]
                sch.append((720, m, lx, ly, ld))
        if EVENING and (idx + day) % 3 == 0:
            m, x, y, d = EVENING[(idx + day) % len(EVENING)]
            sch.append((end, m, x, y, d))
            sch.append((min(end + 120, 1380), None, 0, 0, "down"))
        else:
            sch.append((end, None, 0, 0, "down"))
    else:
        if LEISURE:
            n = len(LEISURE)
            for j, t in enumerate((600, 840, 1020)):
                m, x, y, d = LEISURE[(idx + day + j * 3) % n]
                sch.append((t, m, x, y, d))
        sch.append((1200, None, 0, 0, "down"))
    return sch
