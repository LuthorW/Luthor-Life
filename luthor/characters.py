"""Personagens de National City: aparência, rotinas, presentes, falas e eventos.

Rotinas: lista de (minuto_do_dia, mapa ou None, x, y, direção). None = fora de cena.
Uma personagem pode ter rotinas diferentes: "default", "weekend" (sáb/dom) e "rain".
Retratos: arquivos em assets/portraits. "moods" troca a foto conforme a emoção.
"""

def look(hair, skin, cloth, accent, pants, shoes, style, shade=None):
    return dict(hair=hair, skin=skin, cloth=cloth, accent=accent, pants=pants, shoes=shoes, style=style)


SKIN_L = (240, 202, 172)
SKIN_M = (222, 178, 146)
SKIN_T = (198, 146, 112)
SKIN_D = (150, 100, 72)

NPCS = {
    # ------------------------------------------------------------------ equipe
    "sam": dict(
        name="Samantha Arias", short="Sam", role="CFO",
        look=look((104, 62, 40), (236, 192, 160), (44, 62, 112), (230, 230, 240), (34, 34, 48), (24, 20, 30), "long"),
        portrait="sam.png",
        gifts=dict(love=["vinho", "bolo"], like=["flores", "livro", "relatorio", "risoto"], dislike=["rosquinha", "lata"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (510, "hq", 21, 11, "down"), (1020, "city", 16, 30, "up"),
                     (1140, "cafe", 11, 7, "left"), (1320, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (600, "city", 34, 56, "down"), (780, "trattoria", 4, 10, "left"),
                     (900, "city", 16, 30, "up"), (1140, "cafe", 11, 7, "left"), (1320, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Bom dia, Luthor. Os números de hoje estão na sua mesa... ou deveriam estar.",
                 "Se você lançar projetos com consistência, o conselho para de me ligar às sete da manhã.",
                 "Relatórios de mercado são baratos e rápidos. Ótimos para manter o caixa respirando.",
                 "A Ruby pediu pra eu te mandar um 'oi'. Ela acha que você é uma super-heroína corporativa.",
                 "Você não vai acreditar, mas o Brainy me pediu pra comprar rosquinhas. Ele disse que é 'cientificamente necessário'.",
                 "Estou coordenando a auditoria depois do apagão. A CatCo não larga do nosso pé."],
            mid=["Sabe, trabalhar com você está me dando flashbacks. Não conta pro conselho.",
                 "Sinto muita falta do nosso tempo de universidade. Das vezes que bebiamos demais.",
                 "Acho que a gente se entende melhor do que qualquer planilha. E olha que eu amo planilhas.",
                 "Às vezes eu penso em largar tudo e abrir uma confeitaria. Aí eu olho o balanço e passa.",
                 "Vi você conversando com a Lucy. Cuidado para não falar coisas demais."],
            high=["Você é como uma irmã para mim. Sabia?",
                  "Senhorita Letícia Luthor, a CEO do ano. E eu sou a CFO do ano. E a melhor amiga do ano. E a melhor amiga da CEO do ano.",
                  "Se o mundo acabar amanhã, pelo menos o fluxo de caixa vai estar positivo."],
            evening=["Fim de expediente. Hoje eu sou só a Sam, tá? Nada de planilhas.",
                     "Você está cansado, Luthor. Hora de ir pra casa."],
            rain=["Chuva em National City... dia perfeito para revisar contratos. Ou para um vinho."],
            weekend=["Fim de semana! A Ruby me arrastou pra praia. Não que eu esteja reclamando.",
                     "A Trattoria é o melhor lugar pra almoçar no fim de semana. E eu não estou falando só da comida.",
                     "a A Ruby quer que você vá à praia com a gente. Eu disse que você ia recusar, mas ela não acredita."],
        ),
        reactions=dict(love="Isso! Você me conhece bem demais. Obrigada, de verdade.",
                       like="Que gentil! Obrigada, Lee.",
                       neutral="Ah, obrigada. Vou achar um lugar pra isso.",
                       dislike="Hm... obrigada? Acho que vou repassar pra alguém do financeiro."),
        events={0: dict(scene="sam_0", flag="sam_intro", lines=["Luthor, você está de volta. E eu estou de volta.",
                                              "A LuthorCorp precisa de uma CFO. E eu preciso da minha melhor amiga."]),
                3: dict(scene="sam_3", flag="sam_bonus", lines=["Luthor, revisei todos os contratos de fornecimento da empresa.",
                                                  "A partir de hoje, a Mesa de Contratos paga 10% a mais por tudo.",
                                                  "Considere um presente de amiga. E de CFO."])},
    ),
    "brainy": dict(
        name="Querl Dox", short="Brainy", role="CTO",
        look=look((44, 34, 36), (226, 186, 156), (30, 30, 42), (150, 90, 230), (28, 28, 36), (18, 16, 22), "short"),
        portrait="brainy.png",
        gifts=dict(love=["rosquinha", "athena", "hecate", "bolo"], like=["livro", "software", "artemis", "sushi"],
                   dislike=["flores", "girassois", "lata"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (450, "hq", 11, 5, "right"), (1200, "city", 23, 33, "left"),
                     (1380, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (540, "books", 6, 7, "up"), (780, "hq", 11, 5, "right"),
                     (1200, "city", 23, 33, "left"), (1380, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Saudações, CEO. Há 87,3% de chance de você ter vindo me pedir algo.",
                 "Os projetos precisam de atenção diária. Nenhum algoritmo substitui comprometimento. Ainda.",
                 "Calculei 1.402 maneiras de otimizar o laboratório. 1.401 exigem mais bancadas.",
                 "Rosquinhas são um dos ápices da culinária deste século. Isso é uma observação. Talvez um pedido.",
                 "O apagão de domingo não foi culpa dos nossos sistemas. 94% de certeza. Estou investigando os 6%."],
            mid=["Estou começando a entender o conceito de 'amizade'. Os dados são promissores.",
                 "Você trabalha com eficiência acima da média humana. É um elogio. Acho.",
                 "Algumas propostas só existem em certos trimestres. O mercado é sazonal. Eu também."],
            high=["Você é a pessoa mais fascinante que eu já analisei. E eu analisei muitas.",
                  "Se eu pudesse escolher qualquer linha temporal, escolheria esta. Com você na diretoria."],
            evening=["O céu está limpo hoje. Ótimo para observar satélites. Os nossos, claro."],
            rain=["Chuva: 100% de probabilidade. Eu avisei ontem. Ninguém me ouve."],
            weekend=["Livrarias são bancos de dados com cheiro bom. A Bayside é minha favorita."],
        ),
        reactions=dict(love="Isto é... altamente satisfatório. Meus níveis de serotonina subiram 34%.",
                       like="Aceitável. Muito aceitável. Obrigado.",
                       neutral="Registrado. Obrigado pelo gesto.",
                       dislike="Flores. Organismos em processo de morte decorativa. ...Obrigado?"),
        events={3: dict(scene="brainy_3", flag="hecate", lines=["CEO, tenho uma confissão: existe um projeto que não está no portfólio.",
                                              "O Projeto Hecate. Materiais experimentais, sinais seguros... e um pouco de mistério.",
                                              "Acho que você está pronta. As propostas já estão no Terminal P&D."]),
                5: dict(scene="brainy_5", flag="drone", lines=["Construí uma coisa pra você. Um drone de laboratório.",
                                             "Ele vai trabalhar em todos os projetos ativos toda manhã, antes de você chegar.",
                                             "Por favor, não o chame de 'robozinho'. Ele é sensível. Eu o programei assim."])},
    ),
    "jess": dict(
        name="Jess", short="Jess", role="Assistente executiva",
        look=look((125, 118, 85), (226, 186, 156), (60, 132, 104), (240, 236, 226), (40, 40, 52), (30, 24, 30), "bun"),
        portrait="jess.png",
        gifts=dict(love=["flores", "girassois", "bolo"], like=["expresso", "cappuccino", "rosquinha", "vinho", "panquecas"],
                   dislike=["lata", "jornal"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (420, "hq", 12, 11, "down"), (1080, "cafe", 12, 4, "right"),
                     (1260, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (600, "market", 7, 7, "up"), (720, "city", 15, 38, "right"),
                     (1080, "cafe", 12, 4, "right"), (1260, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Bom dia, Srta. Luthor! Sua agenda de hoje está... flexível.",
                 "Lembrete: projetos só avançam nos dias em que alguém trabalha neles.",
                 "Os contratos colocados na Mesa de Contratos são fechados toda noite.",
                 "A Sam chega às 8h30. O Brainy chega às 7h30 e às vezes nem vai embora.",
                 "A Lucy Williams, da CatCo, ligou de novo pedindo entrevista. Digo que você está em reunião?"],
            mid=["Reorganizei sua agenda. Você ganhou 12 minutos livres. Não gaste tudo de uma vez.",
                 "Comprei aquelas canetas roxas que você gosta. Não precisa agradecer. Mas pode."],
            high=["Trabalhar aqui é a melhor coisa que já me aconteceu. Obrigada por confiar em mim."],
            evening=["Ainda trabalhando? Eu já estou de folga... mas posso ficar mais cinco minutos."],
            rain=["Deixei um guarda-chuva roxo na recepção. Pra você, claro."],
            weekend=["Sábado é dia de mercado e de parque. E de não atender o telefone. Exceto o seu."],
        ),
        reactions=dict(love="Pra mim?! Vou colocar na recepção pra todo mundo ver!",
                       like="Ah, que fofa! Obrigada, Srta. Luthor.",
                       neutral="Obrigada! Vou guardar com carinho.",
                       dislike="Ah... obrigada. Vou... arquivar."),
        events={3: dict(flag="jess_energy", lines=["Srta. Luthor, eu reestruturei toda a sua agenda.",
                                                   "Menos reuniões inúteis, mais tempo pra você respirar.",
                                                   "Você vai sentir que tem muito mais energia. (+20 de energia máxima)"])},
    ),
    "rafa": dict(
        name="Harry", short="Harry", role="Barista do Grão Nobre",
        look=look((222, 182, 92), (246, 206, 176), (236, 232, 224), (122, 82, 52), (122, 82, 52), (50, 36, 30), "short"),
        portrait="harry.png", portrait_key="harry", shop="cafe", shop_map="cafe",
        gifts=dict(love=["livro", "policial"], like=["flores", "sanduiche", "panquecas"], dislike=["expresso"]),
        schedule=dict(default=[(360, "cafe", 4, 3, "down"), (1320, None, 0, 0, "down")]),
        lines=dict(
            low=["E aí, CEO! O de sempre? ...Brincadeira, ainda não sei qual é o de sempre.",
                 "O Grão Nobre abre às 6h e fecha às 22h. Igual a uma CEO, só que com mais café.",
                 "Um expresso resolve 80% dos problemas. Os outros 20% se resolvem com dois expressos."],
            mid=["Comecei a guardar o melhor grão pra você. Não conta pros outros clientes.",
                 "A Lucy Williams toma cappuccino toda manhã ali no canto. Sempre com um bloquinho. Só dizendo."],
            high=["Você é minha cliente favorita. E olha que eu atendo o Brainy, que pede tudo com medidas exatas."],
            evening=["Último café do dia? Vou fazer um descafeinado. Por ordem médica minha."],
            rain=["Dia de chuva é dia de chocolate quente. Não temos chocolate quente. Mas imagina."],
        ),
        reactions=dict(love="Um livro?! Você é incrível. Vou ler no intervalo hoje mesmo!",
                       like="Valeu demais, CEO!",
                       neutral="Opa, obrigado!",
                       dislike="Café... pra um barista. É tipo dar areia pra praia. Mas valeu!"),
        events={3: dict(flag="rafa_discount", lines=["A partir de hoje você tem desconto de amiga aqui no Grão Nobre.",
                                                     "20% em tudo. E não aceito reclamação!"])},
    ),

    # ------------------------------------------------------------------ romance
    "lucy": dict(
        name="Lucy Williams", short="Lucy", role="Repórter da CatCo", romance=True,
        look=look((236, 200, 120), (244, 206, 180), (40, 44, 80), (190, 50, 60), (52, 64, 96), (40, 30, 30), "long"),
        portrait="lucy.png",
        gifts=dict(love=["panquecas", "policial", "cappuccino", "moqueca"],
                   like=["livro", "expresso", "girassois", "bolo", "peixe_grelhado", "drink"],
                   dislike=["relatorio", "software", "athena", "lata"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (480, "cafe", 14, 4, "left"), (540, "catco", 11, 7, "down"),
                     (780, "trattoria", 12, 8, "left"), (840, "catco", 11, 7, "down"), (1080, "books", 4, 7, "up"),
                     (1200, "bar", 5, 5, "up"), (1380, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (540, "city", 10, 40, "left"), (720, "books", 4, 7, "up"),
                     (960, "city", 26, 56, "down"), (1200, "bar", 5, 5, "up"), (1380, None, 0, 0, "down")],
            rain=[(360, None, 0, 0, "down"), (480, "cafe", 14, 4, "left"), (540, "catco", 11, 7, "down"),
                  (1200, "bar", 5, 5, "up"), (1380, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Letícia Luthor. Veio dar uma declaração oficial ou só me vigiar?",
                 "Estou investigando o apagão. Se a LuthorCorp não tem nada a esconder, não tem por que se preocupar.",
                 "Não precisa fazer essa cara. Eu não mordo. Só publico.",
                 "Gotham University parece outra vida, né? Você ainda prende o cabelo quando fica nervosa.",
                 "Uma falha técnica nunca é só uma falha técnica. É sempre uma história sobre pessoas."],
            mid=["Admito: a LuthorCorp está mais transparente do que eu esperava. Não vou escrever isso. Ainda.",
                 "A Bayside Books é o único lugar da cidade onde ninguém me pergunta 'é verdade que...'.",
                 "Você lembra da biblioteca da faculdade? Eu fingia estudar física quântica só pra te irritar.",
                 "Toda noite eu passo no Noonan's. O Marco jura que o fliperama é imbatível. Duvido."],
            high=["Eu passei anos fugindo de National City. Agora não consigo imaginar estar em outro lugar.",
                  "Você é a única fonte em quem eu confio de olhos fechados. E isso é perigoso pra uma repórter.",
                  "Às vezes eu escrevo seu nome no bloquinho sem perceber. Isso é jornalisticamente preocupante."],
            evening=["O Noonan's é o melhor lugar pra fechar o dia. Senta aí, a próxima é por minha conta."],
            rain=["Chuva sempre me lembra do campus. A gente correndo pra biblioteca, lembra?"],
            weekend=["Folga. Sem pauta, sem prazo. Só eu, um livro e esta cidade barulhenta."],
            partner=["Bom dia, Luthor. Deixei café na cafeteira e um bilhete na geladeira. Não leia em voz alta.",
                     "Hoje fechei uma matéria inteira sem citar a LuthorCorp. Estou orgulhosa de mim.",
                     "Te amo. Pronto, falei antes de você. Ponto pra mim."],
            dating=["Oi, namorada. Ainda soa estranho falar isso. Estranho bom.",
                    "Se a Nia perguntar, a gente só está 'trocando informações'. Ela não acredita, mas tudo bem."],
        ),
        reactions=dict(love="Você lembrou... Ok, Luthor. Você ganhou essa rodada.",
                       like="Hm. Bom gosto. Vou anotar isso.",
                       neutral="Obrigada. Vou tentar não escrever uma matéria sobre isso.",
                       dislike="Material de imprensa da LuthorCorp? Sério? Vou usar como peso de papel."),
        events={
            1: dict(scene="lucy_1", mood="smile", lines=["Sabe o que eu percebi? Você me olha igual na faculdade. Como se fosse um problema pra resolver.",
                                         "Eu não sou um problema, Letícia. Eu sou... uma pergunta em aberto.",
                                         "Me encontra no Noonan's qualquer noite. Sem gravador. Prometo."]),
            4: dict(scene="lucy_4", mood="happy", gift="policial", lines=["Achei isso na Bayside e lembrei de você. Um mistério sem solução óbvia.",
                                                          "Tipo a gente, né?",
                                                          "Não faz essa cara. Aceita o livro e pronto."]),
            6: dict(scene="lucy_6", mood="smile", lines=["Eu escrevi a matéria do apagão. Quer saber o final?",
                                         "Não foi a LuthorCorp. Foi uma falha na rede pública que vocês ajudaram a segurar.",
                                         "Eu precisava saber que você era diferente da sua família. Agora eu sei.",
                                         "E isso me assusta mais do que qualquer pauta."]),
            8: dict(scene="lucy_8", mood="love", lines=["Letícia... eu não sei mais onde termina a repórter e começa eu.",
                                        "Se um dia você me der rosas vermelhas, eu vou aceitar. Só pra você saber.",
                                        "(Rosas vermelhas estão à venda no Mercado Central.)"]),
            10: dict(scene="lucy_10", mood="love", lines=["Às vezes eu acordo e penso: como a gente chegou aqui?",
                                         "Anos de silêncio, um apagão, mil cafés... e você.",
                                         "Se quiser ir mais longe... você sabe onde me encontrar."]),
        },
        date_places=[("bar", 7, 8, "left", "um drinque no Noonan's"), ("city", 24, 56, "down", "pôr do sol na praia"),
                     ("books", 10, 8, "left", "uma noite de leitura na Bayside")],
        date_lines=["Você veio. Eu tinha apostado comigo mesma que viria. Ganhei.",
                    "Sabe o que eu mais gosto em você? Você escuta. Ninguém escuta numa cidade dessas.",
                    "Fica mais um pouco. A cidade pode esperar."],
        accept_lines=["Rosas vermelhas. Clássico, previsível... perfeito.",
                      "Sim, Letícia Luthor. Eu namoro você. Mas a primeira entrevista exclusiva é minha."],
        move_lines=["Um pingente... Isso é o que eu acho que é?",
                    "Morar juntas. Na cobertura dos Luthor. Minha mãe vai desmaiar.",
                    "Sim. Mil vezes sim. Eu levo meus livros, você arranja espaço."],
        morning_gift=["panquecas", "cappuccino", "policial"],
    ),
    "vittoria": dict(
        name="Vittoria Ricci", short="Vittoria", role="Dona do Gruppo Ricci", romance=True,
        look=look((58, 34, 26), (206, 156, 120), (128, 32, 48), (244, 236, 222), (40, 36, 44), (60, 30, 30), "long"),
        portrait="vittoria.png",
        gifts=dict(love=["girassois", "lasanha_nonna", "risoto", "vinho"],
                   like=["flores", "massa_pesto", "peixe_grelhado", "tiramisu", "moqueca", "polvo"],
                   dislike=["rosquinha", "sanduiche", "lata", "jornal"]),
        schedule=dict(
            # mercado cedo, sede do Gruppo Ricci, almoço na Trattoria, parque às 15h e a Trattoria à noite
            default=[(360, None, 0, 0, "down"), (420, "market", 3, 7, "up"), (540, "ricci", 4, 2, "down"),
                     (750, "trattoria", 13, 4, "left"), (900, "city", 17, 39, "right"), (990, "ricci", 4, 2, "down"),
                     (1140, "trattoria", 13, 4, "left"), (1380, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (480, "city", 47, 56, "down"), (660, "trattoria", 13, 4, "left"),
                     (1380, None, 0, 0, "down")],
            rain=[(360, None, 0, 0, "down"), (540, "ricci", 4, 2, "down"), (1140, "trattoria", 13, 4, "left"),
                  (1380, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Buongiorno! Mesa pra uma? Ah, você é a famosa Letícia Luthor. Che piacere!",
                 "Nos restaurantes Ricci só entra ingrediente fresco. Regra número um do grupo. Nem você entra, se estiver cansada.",
                 "Minha nonna dizia: quem cozinha com pressa, come com tristeza.",
                 "Sou de Milão. Rossonera de coração! Vi que a LuthorCorp patrocina o Milan. Ponto pra você."],
            mid=["Passo no Mercado Central toda manhã às sete. A Bea guarda os melhores tomates pra Trattoria.",
                 "O Gruppo Ricci tem doze restaurantes em três países. A sede é pequena, mas tem o melhor café da Bayside.",
                 "Você já cozinhou alguma vez na vida? Não minta pra uma italiana. A gente sabe.",
                 "Às três da tarde eu dou uma volta no parque. Dona de restaurante também precisa respirar, cara mia."],
            high=["Quando você entra no restaurante, eu esqueço o que ia dizer pros investidores. Isso nunca acontece. Mai!",
                  "Eu vim pra National City pra recomeçar. Não sabia que ia encontrar... alguém.",
                  "Tesoro, senta. Hoje eu cozinho só pra você."],
            evening=["A Trattoria fecha às onze. Depois disso, sou só a Vittoria. Sem planilha."],
            rain=["Chuva! Dia perfeito para um risoto bem cremoso. Quer?"],
            weekend=["No fim de semana eu nado cedo, antes de abrir. O mar daqui é quase o Mediterrâneo. Quase."],
            partner=["Buongiorno, amore. Deixei uma coisinha pra você na cozinha. Não abre a geladeira antes do café!",
                     "Ensinei o Harry a fazer um cappuccino decente. Finalmente.",
                     "Ti amo, Letícia. Em italiano parece mais bonito, né?"],
            dating=["Minha namorada! Ainda não acredito. A nonna ia te adorar.",
                    "Já contei pra Bea, pro Marco, pro Joca... Sou italiana, não sei guardar segredo."],
        ),
        reactions=dict(love="Mamma mia! Isso é... perfetto. Grazie, tesoro!",
                       like="Che carina! Grazie mille!",
                       neutral="Grazie! Muito gentil.",
                       dislike="Isso... é industrializado? Dio mio. Bem, obrigada pela intenção."),
        events={
            1: dict(scene="vittoria_1", mood="happy", gift="pizza", lines=["Você de novo! Vou começar a reservar sua mesa.",
                                                      "Toma, uma pizza por conta da casa. A Dona Graça fez, eu só servi. Margherita, como em Napoli.",
                                                      "Não conta pros outros clientes, eh?"]),
            4: dict(scene="vittoria_4", mood="happy", flag="vittoria_family", lines=["Sabe, eu decidi uma coisa. Você agora é família Ricci.",
                                                                 "E família Ricci tem 20% de desconto. É a regra. Regra da nonna.",
                                                                 "Não discute com a regra da nonna."]),
            6: dict(scene="vittoria_6", mood="happy", gift="livro_nonna", lines=["Isto aqui é o caderno de receitas da minha nonna. Eu fiz uma cópia pra você.",
                                                            "Ninguém fora da família viu isso. Nem o Marco, que implora toda semana.",
                                                            "Faz a lasanha. E me traz um pedaço. Quero saber se você tem mão boa."]),
            8: dict(scene="vittoria_8", mood="love", lines=["Letícia, posso ser sincera? Italiana não sabe ser diferente.",
                                        "Eu gosto de você. Mais do que de massa fresca. E isso é muito.",
                                        "Se você sentir o mesmo... rosas vermelhas. Do Mercado Central. Eu vou entender."]),
            10: dict(scene="vittoria_10", mood="love", lines=["Eu fico pensando em como seria acordar com você e fazer café da manhã pra duas.",
                                         "Desculpa, falei alto. Coisa de italiana.",
                                         "...Mas é verdade."]),
        },
        date_places=[("trattoria", 12, 10, "left", "um jantar só nosso na Trattoria"),
                     ("city", 47, 56, "down", "um passeio na praia ao luar"),
                     ("city", 24, 33, "left", "uma volta no parque, perto do chafariz")],
        date_lines=["Você chegou! Separei o melhor vinho e a melhor vista. Que no caso, é você.",
                    "Sabe o que minha nonna diria? 'Essa aí tem fome de vida.' Ela ia te adorar.",
                    "Fica. Esquece os contratos por uma noite, amore."],
        accept_lines=["Rosas! Vermelhas! Dio mio, eu vou chorar. Já estou chorando.",
                      "Sim, sim, sim! Agora você é minha namorada. Vou contar pra Milão inteira."],
        move_lines=["Um pingente... Letícia, isso é um pedido?",
                    "Morar juntas! Vou levar minhas panelas. Todas. Não negocio as panelas.",
                    "Sim, amore. Mil vezes sim."],
        morning_gift=["lasanha", "tiramisu", "risoto", "pizza"],
    ),

    # ------------------------------------------------------------------ cidade
    "nia": dict(
        name="Nia Nal", short="Nia", role="Repórter da CatCo",
        look=look((40, 28, 30), (150, 100, 76), (70, 110, 170), (240, 220, 140), (40, 40, 60), (30, 24, 30), "long"),
        portrait="nia.png",
        gifts=dict(love=["livro", "policial", "girassois"], like=["cappuccino", "flores", "bolo", "tiramisu"],
                   dislike=["lata", "relatorio"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (540, "catco", 4, 7, "down"), (1050, "books", 6, 7, "up"),
                     (1260, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (600, "cafe", 9, 7, "right"), (840, "books", 6, 7, "up"),
                     (1200, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Oi! Nia Nal, da CatCo. A Lucy fala de você. Muito. Não que ela admita.",
                 "Uma cidade também é escrita por quem decide contar suas histórias.",
                 "Estou cobrindo cultura esta semana. Livrarias e cafés viraram o coração da cidade."],
            mid=["Às vezes eu sonho com as notícias antes delas acontecerem. Estranho, né? Esquece que eu disse isso.",
                 "A Lucy está diferente desde que voltou pra cidade. Mais leve. Desconfio do motivo."],
            high=["Você é uma das poucas pessoas poderosas que eu realmente admiro, Letícia."],
            evening=["A Bayside fecha às nove. Eu sempre saio com um livro a mais do que planejei."],
            rain=["Chuva é ótima pra escrever. O som ajuda as palavras a saírem."],
        ),
        reactions=dict(love="Que presente lindo! Você tem um olhar atento, sabia?",
                       like="Obrigada! Que gentil.",
                       neutral="Ah, obrigada!",
                       dislike="Hm... um relatório corporativo? Vou ler... algum dia."),
        events={3: dict(flag="nia_scoop", lines=["Letícia, vou publicar uma matéria sobre a reestruturação da LuthorCorp.",
                                                 "Spoiler: ela é positiva. Os investidores vão gostar.",
                                                 "Considere isso um voto de confiança. (A ação LCORP ganha impulso extra.)"])},
    ),
    "barry": dict(
        name="Barry Allen", short="Barry", role="Fotógrafo da CatCo",
        look=look((96, 54, 32), (236, 196, 166), (150, 32, 44), (128, 128, 134), (50, 56, 80), (34, 30, 34), "short"),
        portrait="barry.png",
        gifts=dict(love=["cappuccino", "rosquinha", "pipoca"], like=["sanduiche", "croissant", "livro", "estrela_mar"],
                   dislike=["lata", "relatorio"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (510, "catco", 14, 10, "up"), (750, "cafe", 12, 7, "up"),
                     (840, "catco", 14, 10, "up"), (1080, "city", 30, 57, "down"), (1200, "bar", 9, 9, "up"),
                     (1350, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (540, "city", 99, 38, "up"), (780, "cafe", 12, 7, "up"),
                     (960, "city", 96, 26, "up"), (1140, "bar", 9, 9, "up"), (1350, None, 0, 0, "down")],
            rain=[(360, None, 0, 0, "down"), (510, "catco", 14, 10, "up"), (1200, "bar", 9, 9, "up"),
                  (1350, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Oi! Barry, da fotografia da CatCo. Desculpa o atraso. Eu sempre chego atrasado. É um talento.",
                 "A Nia escreve, a Lucy investiga e eu corro atrás com a câmera. Literalmente correndo.",
                 "Posso tirar uma foto sua pra matéria da Lucy? Prometo que fica melhor que a da revista."],
            mid=["O melhor horário pra fotografar a orla é às seis da tarde. A luz fica dourada e todo mundo fica bonito.",
                 "A Nia me arrasta pra livraria toda semana. Eu finjo que reclamo. Saio sempre com um livro de ciência.",
                 "A Lucy finge que é durona, mas ela guarda todas as fotos que eu tiro dela com você. Todas."],
            high=["Você é tipo uma heroína pra essa cidade, sabia? Só que de terninho.",
                  "Fiz uma exposição na minha cabeça: 'National City vista de perto'. Você está em metade das fotos."],
            evening=["Fim de expediente! Agora é pizza, Noonan's e tentar não perder a câmera de novo."],
            rain=["Chuva rende foto incrível. Reflexo no asfalto, guarda-chuva colorido... e câmera molhada."],
        ),
        reactions=dict(love="Sério?! Você acertou em cheio. Valeu mesmo!", like="Que demais, obrigado!",
                       neutral="Ah, valeu!", dislike="Hm... vou guardar. Em algum lugar. Longe."),
        events={3: dict(scene="barry_3", lines=["Revelei as fotos da semana. Olha essa sua no calçadão!",
                               "A Lucy pediu uma cópia. Depois pediu outra. Eu não perguntei por quê.",
                               "Se precisar de fotos pra Luthor Corp, é só chamar. Pros amigos é de graça."]),
                6: dict(scene="barry_6", gift="filme_foto", lines=["Ficou perfeita a foto do grupo! Toma um filme novo."])},
    ),
    "theo": dict(
        name="Theo", short="Theo", role="Livreiro da Bayside Books",
        look=look((60, 44, 40), (170, 120, 90), (130, 90, 60), (230, 220, 200), (60, 60, 70), (40, 30, 26), "short"),
        portrait="theo.png", shop="books", shop_map="books",
        gifts=dict(love=["livro", "cappuccino"], like=["policial", "croissant", "bolo"], dislike=["lata", "jornal"]),
        schedule=dict(default=[(360, None, 0, 0, "down"), (480, "books", 13, 4, "down"), (1260, None, 0, 0, "down")]),
        lines=dict(
            low=["Bem-vinda à Bayside Books. Livros com bônus permanentes. Eu juro que não é golpe.",
                 "O Manual do Pescador é o mais vendido. O Joca deu um exemplar pra cada cliente da barraca dele.",
                 "Depois do apagão, as pessoas lembraram que livro não precisa de bateria."],
            mid=["A Lucy Williams senta naquela poltrona todo fim de tarde. Já reservei pra ela, na verdade."],
            high=["Você virou cliente da casa. Isso aqui é quase um clube secreto."],
            evening=["Fechamos às nove. Mas pra você, talvez nove e cinco."],
            rain=["Dia de chuva, dia de livraria cheia. Adoro."],
        ),
        reactions=dict(love="Ah, que maravilha! Obrigado!", like="Muito gentil, obrigado.",
                       neutral="Obrigado!", dislike="Uma CatCo molhada... Não é o melhor estado pra um jornal."),
        events={},
    ),
    "bea": dict(
        name="Bea", short="Bea", role="Dona do Mercado Central",
        look=look((180, 70, 50), (232, 186, 156), (220, 120, 60), (250, 240, 220), (60, 70, 90), (40, 30, 30), "bun"),
        portrait="bea.png", shop="market", shop_map="market",
        gifts=dict(love=["girassois", "bolo"], like=["flores", "panquecas", "cappuccino"], dislike=["lata"]),
        schedule=dict(default=[(360, None, 0, 0, "down"), (420, "market", 13, 4, "down"), (1200, None, 0, 0, "down")]),
        lines=dict(
            low=["Bom dia, querida! Tomate fresquinho, ovo caipira, flor do campo. O que vai ser?",
                 "A Vittoria vem aqui todo dia às sete. Escolhe tomate um por um, sabia?",
                 "Rosas vermelhas? Tenho sim. Mas só vendo pra quem está apaixonada. Brincadeira. Ou não."],
            mid=["Com esses ingredientes dá pra fazer panquecas. Farinha, ovos e leite. Moleza!"],
            high=["Você é a CEO mais simpática que já pisou no meu mercado."],
            evening=["Fecho às oito. Aproveita que o pão de hoje ainda está bom."],
            rain=["Chuva é bom pras hortas. Amanhã chega verdura linda."],
        ),
        reactions=dict(love="Girassóis! Minha flor favorita! Obrigada, querida!", like="Que mimo, obrigada!",
                       neutral="Obrigada, querida!", dislike="Uma lata... Vou reciclar, viu?"),
        events={},
    ),
    "graca": dict(
        name="Dona Graça", short="Graça", role="Chef da Ricci Trattoria",
        look=look((96, 84, 86), (176, 120, 86), (240, 236, 230), (40, 130, 80), (60, 52, 56), (50, 40, 40), "bun"),
        portrait="graca.png", shop="trattoria", shop_map="trattoria",
        gifts=dict(love=["moqueca", "lasanha_nonna"], like=["manjericao", "tomate", "abobora", "cappuccino", "flores"],
                   dislike=["lata", "rosquinha", "sanduiche"]),
        schedule=dict(default=[(360, None, 0, 0, "down"), (540, "trattoria", 9, 4, "down"), (1380, None, 0, 0, "down")]),
        lines=dict(
            low=["Bem-vinda, filha! Senta que a massa já vem. Hoje tem nhoque com molho de tomate da Bea.",
                 "Trinta anos de fogão, dez deles na Itália. Aprendi italiano antes de aprender a fazer um bom risoto.",
                 "A Vittoria cuida dos números. Eu cuido do sabor. Assim ninguém briga. Quase ninguém."],
            mid=["Segredo da casa: um tiquinho de pimenta-do-reino no molho de tomate. Não conta pra nonna da Vittoria.",
                 "Lasanha boa é que nem conversa boa: camada por camada, sem pressa.",
                 "Quando dá saudade da Bahia, eu faço moqueca pra equipe. Ninguém reclama."],
            high=["Você come bem, minha filha. Quem come bem é gente boa. Não erro nunca.",
                  "A Vittoria fala de você o tempo todo. Eu finjo que não ouço. Mas ouço tudo."],
            evening=["Cozinha cheia, panela no fogo e coração tranquilo. É assim que eu gosto."],
            rain=["Dia de chuva pede caldo quentinho. Já botei o feijão pra cozinhar, só por garantia."],
        ),
        reactions=dict(love="Ai, que coisa mais linda! Você tem mão boa, viu?", like="Obrigada, filha!",
                       neutral="Obrigada, querida.", dislike="Comida de pacote? Ai, meu Deus. Mas obrigada pela lembrança."),
        events={3: dict(scene="graca_3", gift="moqueca", lines=["Fiz uma moqueca do jeito da minha mãe, lá em Salvador.",
                                               "Leva pra casa. Esquenta devagar, não deixa ferver.",
                                               "E volta pra me dizer se ficou boa. Eu sei que ficou."])},
    ),
    "marco": dict(
        name="Marco", short="Marco", role="Barman do Noonan's",
        look=look((30, 26, 28), (190, 140, 110), (40, 40, 46), (200, 40, 60), (30, 30, 36), (20, 18, 22), "short"),
        portrait="marco.png", shop="bar", shop_map="bar",
        gifts=dict(love=["moqueca", "peixe_grelhado", "vinho"], like=["petiscos", "pizza", "atum"], dislike=["flores"]),
        schedule=dict(default=[(360, None, 0, 0, "down"), (960, "bar", 4, 3, "down"), (1530, None, 0, 0, "down")]),
        lines=dict(
            low=["Bem-vinda ao Noonan's. O fliperama Meteoro tá ali no canto. O recorde é 32. Ninguém bate.",
                 "Aqui todo mundo é igual. CEO, repórter, pescador. Todo mundo paga a conta.",
                 "A Vittoria jura que meu molho é ruim. Eu juro que ela tá com inveja."],
            mid=["A Lucy senta sempre no mesmo banco. Diz que é por causa da luz. Eu acho que é por causa da porta."],
            high=["Você virou da casa. Primeira rodada? Por minha conta. Às vezes."],
            evening=["Noite boa. O fliperama tá quente hoje."],
            rain=["Chuva enche o bar. Chuva é boa pro bar."],
        ),
        reactions=dict(love="Isso é comida de verdade! Valeu, chefe!", like="Ô, obrigado!",
                       neutral="Valeu!", dislike="Flores num bar? Vou pôr num copo, sei lá."),
        events={},
    ),
    "joca": dict(
        name="Seu Joca", short="Joca", role="Pescador do píer",
        look=look((220, 220, 220), (190, 140, 100), (60, 110, 160), (230, 200, 90), (90, 80, 60), (60, 50, 40), "cap"),
        portrait="joca.png", shop="bait", shop_map="city",
        gifts=dict(love=["moqueca", "atum", "kryptoniano"], like=["peixe_grelhado", "expresso", "sardinha", "drink"],
                   dislike=["software", "relatorio"]),
        schedule=dict(default=[(360, "city", 62, 65, "down"), (1080, "bar", 11, 8, "left"), (1320, None, 0, 0, "down")],
                      rain=[(360, "city", 62, 65, "down"), (1140, "bar", 11, 8, "left"), (1320, None, 0, 0, "down")]),
        lines=dict(
            low=["Ô, moça! Quer pescar? Escolhe a vara na barra, fica de frente pra água e aperta E.",
                 "Quando o peixe morder, aperta rápido! Depois segura o botão pra subir a barra verde.",
                 "Lago do parque tem carpa e tilápia. Aqui no mar tem robalo, lula de noite, polvo...",
                 "Dizem que em noite de chuva do último trimestre aparece um peixe verde brilhante. Eu já vi. Ninguém acredita."],
            mid=["Isca faz o peixe morder bem mais rápido. Cinco pratas cada. Barato!",
                 "Moqueca de peixe fresco é a melhor coisa do mundo. Se fizer uma, me traz um pouquinho?"],
            high=["Vou te contar meu segredo: o peixe bom gosta de quem tem paciência. E de isca boa."],
            evening=["Hora de guardar a vara e tomar uma no Noonan's."],
            rain=["Chuva é dia de peixe-espada! Pega a vara!"],
        ),
        reactions=dict(love="Ô, menina! Isso aí é presente de rei!", like="Opa, valeu!",
                       neutral="Obrigado, moça.", dislike="Papelada de empresa? Vou embrulhar sardinha com isso."),
        events={3: dict(flag="joca_spot", lines=["Vou te contar um segredo de pescador velho.",
                                                 "Tem um jeito de lançar a linha que atrai os peixes raros.",
                                                 "Pronto, agora você sabe. (Peixes raros aparecem mais.)"])},
    ),
    "ian": dict(
        name="Ian", short="Ian", role="Diretor da Marina Luthor",
        look=look((66, 42, 30), (226, 184, 152), (26, 24, 30), (40, 38, 44), (40, 44, 60), (40, 32, 28), "medium"),
        portrait="ian.png",
        gifts=dict(love=["vinho", "atum", "peixe_grelhado"], like=["expresso", "robalo", "livro", "moqueca"],
                   dislike=["rosquinha", "lata"]),
        schedule=dict(
            default=[(360, None, 0, 0, "down"), (480, "marina", 17, 3, "down"), (780, "trattoria", 15, 8, "left"),
                     (870, "marina", 17, 3, "down"), (1140, "bar", 12, 4, "left"), (1320, None, 0, 0, "down")],
            weekend=[(360, None, 0, 0, "down"), (420, "marina", 17, 3, "down"), (1200, None, 0, 0, "down")],
        ),
        lines=dict(
            low=["Letícia! Quanto tempo. Bem-vinda à Marina Luthor. Ainda é estranho ver seu nome na placa e não o do seu pai?",
                 "A divisão náutica é pequena, mas é a única parte da Luthor Corp que cheira a maresia.",
                 "Se quiser sair pro mar, é só falar. Tenho barco, tenho tempo e tenho saudade de conversar com você."],
            mid=["Pesca em alto-mar é outra coisa. Marlim, dourado, garoupa... peixe que não chega perto do píer.",
                 "Fim de semana tem regata. Vento bom, boia no caminho e muita gente gritando. Você ia adorar.",
                 "O laboratório de vocês faz motor melhor que qualquer estaleiro. Me traz um e eu pago bem."],
            high=["A gente se conhece desde as férias no interior, quando a gente era criança. Veleiro de brinquedo no lago, lembra?",
                  "No crachá você é a minha chefe. Fora dele, é a amiga mais antiga que eu tenho."],
            evening=["O sol se pondo atrás do farol é o melhor quadro da cidade. E ninguém cobra ingresso."],
            rain=["Dia de chuva é dia de cuidar dos barcos. E de café forte no clube."],
        ),
        reactions=dict(love="Você lembrou! Isso é a cara de quem me conhece há anos.", like="Boa escolha, Luthor!",
                       neutral="Valeu, Letícia.", dislike="Hm. Vou deixar no barco. Alguém vai querer."),
        events={0: dict(scene="ian_0", flag="marina_vip", lines=["Fechei o trimestre da marina no azul. E criei uma regra nova como diretor."]),
                3: dict(scene="ian_3", flag="marina_vip", lines=["Fechei o trimestre da marina no azul. E criei uma regra nova como diretor.",
                                                  "A CEO paga metade do preço nos passeios. Você me deu autonomia, estou usando.",
                                                  "(Pesca em alto-mar e passeio ao pôr do sol com 50% de desconto.)"]),
                6: dict(scene="ian_6", gift="luvas_vela", lines=["Toma, as minhas luvas de vela. Quero que fiquem com você."])},
    ),
}

EYES = {"sam": (110, 70, 40), "brainy": (60, 40, 34), "jess": (90, 60, 36), "rafa": (70, 130, 190),
        "lucy": (80, 150, 200), "vittoria": (96, 56, 30), "nia": (60, 36, 26), "theo": (70, 48, 30),
        "bea": (90, 150, 90), "marco": (50, 36, 30), "joca": (90, 120, 150), "graca": (80, 52, 34),
        "barry": (90, 130, 170), "ian": (110, 160, 200)}
for _k, _e in EYES.items():
    NPCS[_k]["look"]["eyes"] = _e
NPCS["vittoria"]["look"]["style"] = "wavy"
# roupa de cada personagem (desenhada em sprites.py)
OUTFITS = {"sam": "blazer", "brainy": "blazer", "jess": "blouse", "rafa": "apron", "lucy": "blazer",
           "vittoria": "blazer", "graca": "chef", "nia": "blouse", "theo": "cardigan", "bea": "apron", "marco": "vest", "joca": "fisher"}
for _k, _o in OUTFITS.items():
    NPCS[_k]["look"]["outfit"] = _o

# aparência dos bonequinhos de acordo com os retratos (assets/portraits)
LOOK_UPDATES = {
    "sam": dict(hair=(112, 74, 46), skin=(226, 182, 150), cloth=(98, 106, 62), accent=(242, 240, 234),
                pants=(52, 58, 82), style="wavy", outfit="cardigan"),
    "brainy": dict(hair=(52, 36, 28), skin=(222, 180, 148), cloth=(238, 240, 246), accent=(46, 46, 62),
                   pants=(34, 34, 44), style="medium", outfit="labcoat", goggles=True),
    "jess": dict(hair=(170, 118, 60), skin=(236, 198, 170), cloth=(30, 28, 34), accent=(150, 90, 200),
                 pants=(60, 56, 68), style="long", outfit="skirt_suit", glasses=True),
    "rafa": dict(hair=(190, 118, 52), skin=(236, 196, 160), cloth=(186, 122, 44), accent=(66, 66, 72),
                 pants=(62, 52, 44), style="short", outfit="cardigan"),
    "lucy": dict(hair=(212, 170, 100), skin=(240, 204, 178), cloth=(34, 42, 72), accent=(236, 232, 226),
                 pants=(40, 44, 60), style="long", outfit="peacoat"),
    "vittoria": dict(hair=(96, 60, 40), skin=(214, 166, 130), cloth=(184, 138, 92), accent=(128, 32, 48),
                     pants=(52, 40, 44), style="wavy", outfit="trench"),
    "nia": dict(hair=(36, 28, 32), skin=(238, 204, 182), cloth=(172, 178, 226), accent=(118, 140, 204),
                style="long", outfit="blouse"),
    "barry": dict(outfit="cardigan"),
    "theo": dict(hair=(26, 20, 20), skin=(196, 146, 108), cloth=(226, 214, 180), accent=(196, 182, 146),
                 style="short", outfit="shirt"),
    "bea": dict(hair=(178, 84, 42), skin=(240, 196, 166), cloth=(128, 84, 50), accent=(96, 62, 36),
                style="wavy", outfit="cardigan", hat=(122, 98, 70)),
    "graca": dict(hair=(198, 190, 186), skin=(150, 96, 66), cloth=(30, 26, 30), accent=(204, 56, 44),
                  style="afro", outfit="patterned"),
    "marco": dict(hair=(24, 18, 18), skin=(112, 72, 52), cloth=(36, 32, 38), accent=(186, 36, 50),
                  pants=(30, 30, 36), style="short", outfit="bartender"),
    "joca": dict(hair=(198, 196, 192), skin=(206, 160, 126), cloth=(98, 74, 52), accent=(196, 180, 150),
                 style="long", outfit="fisher", beard="full", beard_color=(214, 210, 204), hat=(104, 92, 72)),
    "ian": dict(cloth=(34, 48, 96), accent=(34, 48, 96), pants=(196, 178, 140), shoes=(124, 82, 50),
                outfit="breton"),
}
for _k, _u in LOOK_UPDATES.items():
    NPCS[_k]["look"].update(_u)

# ===========================================================================
# Médicas do Conti Moretti Hospitais
# ===========================================================================
# As lideranças clínicas do Conti Moretti Hospitais, como personagens completas:
# dá para conversar, presentear, fazer amizade e ver eventos de coração.
#
# A rotina de cada médica é montada dia a dia (veja doctor_schedule): plantão alternando
# entre consultórios, internação e recepção, almoço fora do hospital e folgas. Nenhuma
# repete o mesmo posto em sequência, duas nunca dividem o mesmo lugar ao mesmo tempo
# e o lugar do almoço muda todo dia.

DOCTOR_KEYS = ["yang", "meredith", "milany", "izzie", "addison"]


def _look(hair, skin, cloth, accent, pants, shoes, style, eyes):
    return dict(hair=hair, skin=skin, cloth=cloth, accent=accent, pants=pants, shoes=shoes, style=style, eyes=eyes,
                outfit="coat")


COAT, GREEN, GREEN2, COPPER = (244, 244, 248), (18, 63, 53), (29, 89, 74), (183, 123, 101)
_OFF = [(360, None, 0, 0, "down")]

DOCTORS = {
    "yang": dict(
        name="Dra. Cristina Yang", short="Cristina", role="Direção Médica · Conti Moretti",
        look=_look((24, 18, 20), (232, 196, 160), COAT, GREEN, GREEN2, (30, 30, 36), "wavy", (60, 40, 30)),
        portrait="cristina.png", portrait_key="cristina",
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
        portrait="meredith.png",
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
        portrait="milany.png",
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
                       neutral="Obrigada, de verdade.", dislike="Hm... sério? Como cardiologista, vou fingir que não vi."),
        events={
            0: dict(scene="milany_0", lines=["Amiga, você está de volta! Eu estava ansiosa pra te ver.",]),
            3: dict(flag="cmh_discount", lines=["Conversei com a diretoria do Conti Moretti.",
            "A partir de hoje, suas consultas saem pela metade do preço. Prevenção não pode ter barreira.",
            "Sua saúde em primeiro lugar. Literalmente."])},
            
    ),
    "izzie": dict(
        name="Dra. Izzie Stevens", short="Izzie", role="Centro de Oncologia · Conti Moretti",
        look=_look((240, 214, 140), (248, 222, 200), COAT, (232, 208, 199), GREEN2, (200, 120, 140), "bun", (90, 130, 190)),
        portrait="izzie.png",
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
        portrait="addison.png",
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


def setup_doctor_spots(crowd):
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


def doctor_works(idx, day):
    return (day + idx * 2) % 7 not in (0, 4)


def doctor_schedule(key, day):
    idx = DOCTOR_KEYS.index(key)
    sch = [(360, None, 0, 0, "down")]
    if doctor_works(idx, day):
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


# aparência da Milany de acordo com o retrato (cabelo castanho, solto e ondulado)
DOCTORS["milany"]["look"].update(hair=(112, 68, 42), style="wavy", skin=(236, 200, 172))


NPCS.update(DOCTORS)
NPC_ORDER = ["sam", "brainy", "jess", "rafa", "lucy", "vittoria", "nia", "barry", "theo", "bea", "graca", "marco",
             "joca", "ian"] + DOCTOR_KEYS
TEAM = ["sam", "brainy", "jess", "rafa", "ian"]      # equipe da Luthor Corp (meta de 3 corações e pedidos do laboratório)
ROMANCES = ["lucy", "vittoria"]


# Novos gostos: horta, coletáveis e cinema
_EXTRA_GIFTS = {
    "sam": dict(like=["caprese", "trevo4", "rosa_jardim"]),
    "brainy": dict(love=["trevo4"], like=["pipoca", "vidro_mar", "estrela_mar"]),
    "jess": dict(like=["rosa_jardim", "flor_silvestre", "morango"]),
    "rafa": dict(like=["morango", "torta_morango", "amora"]),
    "lucy": dict(love=["rosa_jardim"], like=["estrela_mar", "pipoca", "torta_morango", "coral"]),
    "vittoria": dict(love=["torta_morango", "sopa_abobora"], like=["manjericao", "tomate", "morango", "abobora", "caprese"]),
    "nia": dict(love=["estrela_mar"], like=["flor_silvestre", "concha", "rosa_jardim"]),
    "theo": dict(like=["pipoca", "trevo4", "flor_silvestre"]),
    "bea": dict(love=["abobora", "rosa_jardim"], like=["morango", "flor_silvestre"]),
    "marco": dict(like=["pipoca", "amora", "sopa_abobora"]),
    "joca": dict(like=["coral", "concha", "sopa_abobora", "isotonico"]),
}
for _k in ("sam", "jess", "nia", "lucy", "vittoria", "bea"):
    _EXTRA_GIFTS[_k].setdefault("like", []).append("kit_cuidado")
for _k, _g in _EXTRA_GIFTS.items():
    for _t, _items in _g.items():
        NPCS[_k]["gifts"].setdefault(_t, []).extend(i for i in _items if i not in NPCS[_k]["gifts"].get(_t, []))
for _k in ROMANCES:
    NPCS[_k]["date_places"].append(("marina", 9, 6, "left", "um passeio de iate ao pôr do sol"))
for _k in ("lucy", "vittoria"):
    NPCS[_k]["date_places"].append(("cinema", 13, 5, "up", "uma sessão no Cine National"))


# ---------------------------------------------------------------------------
# Bonequinhos de acordo com os retratos novos (outubro de 2034)
# ---------------------------------------------------------------------------
SCRUBS = (84, 118, 168)          # pijama cirúrgico azul por baixo do jaleco
LOOK_UPDATES_2 = {
    # Ian: cabelo escuro e casaco de capitão azul-marinho com calça branca (diretor da marina)
    "ian": dict(hair=(30, 24, 26), cloth=(26, 34, 70), accent=(240, 240, 244), pants=(236, 234, 228),
                shoes=(110, 72, 46), style="short", outfit="captain"),
    # Lucy: jaqueta de couro, camiseta branca e jeans (repórter de rua)
    "lucy": dict(cloth=(52, 40, 40), accent=(236, 232, 226), pants=(66, 92, 138), shoes=(40, 32, 34),
                 outfit="leather"),
    # Marco: jaqueta preta com gola marrom
    "marco": dict(cloth=(30, 28, 32), accent=(150, 96, 60)),
    # Harry: cabelo loiro-acobreado e jaqueta caramelo
    "rafa": dict(hair=(196, 140, 70), cloth=(178, 120, 46)),
    # Meredith: loiro mel
    "meredith": dict(hair=(178, 136, 84), accent=(36, 44, 78), pants=SCRUBS),
    # Cristina e Izzie: jaleco branco com pijama azul
    "yang": dict(accent=SCRUBS, pants=SCRUBS, style="wavy"),
    "izzie": dict(hair=(232, 204, 132), accent=SCRUBS, pants=SCRUBS, style="long"),
    # Milany: jaleco por cima de blusa vinho (cabelo solto)
    "milany": dict(accent=(128, 40, 58), pants=(46, 42, 52)),
    # Addison: pijama cirúrgico rosa e cabelo ruivo solto
    "addison": dict(hair=(168, 62, 44), cloth=(222, 112, 132), accent=(200, 92, 112), pants=(214, 104, 124),
                    shoes=(240, 240, 244), style="long", outfit="shirt"),
}
for _k, _u in LOOK_UPDATES_2.items():
    NPCS[_k]["look"].update(_u)

# Roupa das médicas fora do hospital (no hospital, "look" com jaleco ou pijama cirúrgico)
OFF_DUTY = {
    "yang": dict(cloth=(78, 80, 90), accent=(30, 30, 34), pants=(34, 34, 40), shoes=(30, 26, 30), outfit="peacoat"),
    "meredith": dict(cloth=(96, 104, 66), accent=(236, 232, 224), pants=(64, 88, 130), shoes=(110, 76, 52),
                     outfit="blazer"),
    "milany": dict(cloth=(244, 242, 238), accent=(226, 222, 214), pants=(46, 42, 52), shoes=(60, 30, 30),
                   outfit="blouse"),
    "izzie": dict(cloth=(240, 170, 186), accent=(250, 246, 240), pants=(72, 96, 140), shoes=(240, 240, 244),
                  outfit="cardigan"),
    "addison": dict(cloth=(30, 110, 86), accent=(30, 110, 86), pants=(30, 110, 86), shoes=(30, 24, 30),
                    outfit="skirt_suit"),
}
for _k, _u in OFF_DUTY.items():
    NPCS[_k]["look_off"] = dict(NPCS[_k]["look"], **_u)


# ---------------------------------------------------------------------------
# Roupas por estação (a roupa de "look" é a da primavera)
# ---------------------------------------------------------------------------
SEASON = "spring"          # trocada por Game.apply_season


def _w(outfit, cloth, accent=None, pants=None, **kw):
    d = dict(outfit=outfit, cloth=cloth)
    if accent:
        d["accent"] = accent
    if pants:
        d["pants"] = pants
    d.update(kw)
    return d


SHORT = dict(sleeves="short")
# personagem: {estação: mudanças no look}. Médicas: vale para a roupa de fora do hospital (no hospital, jaleco).
WARDROBE = {
    "leticia": dict(
        summer=_w("blouse", (246, 242, 234), (194, 148, 104), (196, 172, 134), **SHORT),
        autumn=_w("trench", (150, 90, 56), (40, 30, 36), (34, 30, 44)),
        winter=_w("peacoat", (36, 40, 62), (236, 232, 226), (34, 30, 44), scarf=(150, 36, 60))),
    "sam": dict(
        summer=_w("blouse", (250, 236, 200), (98, 106, 62), (70, 80, 110), **SHORT),
        autumn=_w("cardigan", (170, 110, 60), (242, 240, 234)),
        winter=_w("peacoat", (124, 100, 78), (242, 240, 234), scarf=(230, 226, 216))),
    "brainy": dict(
        summer=dict(accent=(60, 110, 160)),
        autumn=dict(accent=(110, 46, 40)),
        winter=dict(scarf=(40, 60, 110))),
    "jess": dict(
        summer=_w("skirt_suit", (204, 214, 238), (150, 90, 200), **SHORT),
        autumn=_w("skirt_suit", (112, 62, 52), (150, 90, 200)),
        winter=_w("peacoat", (30, 28, 34), (150, 90, 200), scarf=(150, 90, 200))),
    "rafa": dict(
        summer=_w("shirt", (240, 230, 200), (66, 66, 72), **SHORT),
        autumn=_w("cardigan", (120, 70, 40), (66, 66, 72)),
        winter=_w("peacoat", (62, 50, 40), (66, 66, 72), scarf=(196, 140, 70))),
    "lucy": dict(
        summer=_w("shirt", (238, 234, 228), (66, 92, 138), **SHORT),
        autumn=_w("leather", (112, 70, 46), (238, 234, 228)),
        winter=_w("peacoat", (34, 42, 72), (236, 232, 226), (40, 44, 60), scarf=(236, 232, 226))),
    "vittoria": dict(
        summer=_w("blouse", (250, 246, 240), (128, 32, 48), (220, 200, 170), **SHORT),
        autumn=_w("trench", (128, 32, 48), (184, 138, 92)),
        winter=_w("peacoat", (34, 32, 38), (178, 152, 120), (40, 36, 44), scarf=(178, 152, 120))),
    "nia": dict(
        summer=_w("blouse", (250, 220, 150), (118, 140, 204), **SHORT),
        autumn=_w("cardigan", (120, 90, 150), (172, 178, 226)),
        winter=_w("peacoat", (60, 70, 120), (172, 178, 226), scarf=(240, 220, 150))),
    "barry": dict(
        summer=_w("shirt", (200, 44, 52), (230, 226, 216), **SHORT),
        autumn=_w("cardigan", (120, 40, 40), (230, 226, 216)),
        winter=_w("peacoat", (62, 42, 42), (230, 226, 216), scarf=(226, 196, 60))),
    "theo": dict(
        summer=_w("shirt", (230, 216, 182), (196, 182, 146), **SHORT),
        autumn=_w("cardigan", (110, 80, 50), (226, 214, 180)),
        winter=_w("peacoat", (72, 62, 52), (226, 214, 180), scarf=(180, 60, 50))),
    "bea": dict(
        summer=_w("blouse", (236, 220, 160), (128, 84, 50), **SHORT),
        autumn=_w("cardigan", (178, 84, 42), (96, 62, 36)),
        winter=_w("peacoat", (92, 62, 42), (96, 62, 36), scarf=(230, 200, 120))),
    "graca": dict(
        summer=dict(**SHORT),
        autumn=dict(accent=(214, 120, 40)),
        winter=dict(scarf=(204, 56, 44))),
    "marco": dict(
        summer=dict(**SHORT),
        winter=_w("peacoat", (30, 28, 32), (150, 96, 60), scarf=(150, 96, 60))),
    "joca": dict(
        summer=dict(**SHORT),
        winter=_w("peacoat", (92, 76, 54), (196, 180, 150), scarf=(196, 180, 150))),
    "ian": dict(
        summer=_w("shirt", (244, 244, 248), (26, 34, 70), **SHORT),
        winter=_w("peacoat", (28, 36, 72), (236, 234, 228), scarf=(236, 234, 228))),
    # médicas (roupa de fora do hospital)
    "yang": dict(
        summer=_w("shirt", (230, 230, 236), (30, 30, 34), **SHORT),
        autumn=_w("trench", (84, 84, 94), (30, 30, 34)),
        winter=_w("peacoat", (78, 80, 90), (30, 30, 34), scarf=(30, 30, 34))),
    "meredith": dict(
        summer=_w("blouse", (180, 200, 230), (236, 232, 224), **SHORT),
        autumn=_w("cardigan", (150, 110, 60), (236, 232, 224)),
        winter=_w("peacoat", (60, 70, 92), (236, 232, 224), scarf=(200, 60, 60))),
    "milany": dict(
        summer=_w("blouse", (250, 232, 232), (226, 222, 214), **SHORT),
        autumn=_w("trench", (128, 40, 58), (226, 222, 214)),
        winter=_w("peacoat", (64, 30, 42), (226, 222, 214), scarf=(240, 230, 220))),
    "izzie": dict(
        summer=_w("blouse", (250, 230, 150), (250, 246, 240), **SHORT),
        autumn=_w("cardigan", (190, 110, 80), (250, 246, 240)),
        winter=_w("peacoat", (240, 170, 186), (250, 246, 240), scarf=(250, 246, 240))),
    "addison": dict(
        summer=_w("blouse", (240, 240, 236), (30, 110, 86), (30, 110, 86), **SHORT),
        autumn=_w("skirt_suit", (120, 40, 40), (120, 40, 40), (120, 40, 40)),
        winter=_w("peacoat", (30, 110, 86), (30, 24, 30), (30, 24, 30), scarf=(30, 24, 30))),
}


def dress(key, look, season=None):
    """O look da personagem na estação. Figurantes (key None) seguem uma regra geral."""
    season = season or SEASON
    if season == "spring":
        return look
    ov = WARDROBE.get(key, {}).get(season) if key else None
    if ov is None:
        if season == "summer":
            ov = dict(SHORT)
        elif season == "winter":
            ov = dict(outfit="peacoat", scarf=look.get("accent", (180, 40, 60)))
        else:
            return look
    return {**look, **ov}


def look_for(key, map_name, season=None):
    """Aparência certa para o lugar e a estação: médicas usam jaleco no hospital e roupa de fora no resto."""
    d = NPCS[key]
    if d.get("look_off") and map_name != "hospital":
        return dress(key, d["look_off"], season)
    if d.get("look_off"):
        return d["look"]                       # no hospital, o jaleco é o mesmo o ano todo
    return dress(key, d["look"], season)



# Corpos diferentes, como no Stardew: altura em pixels (+ mais alta, - mais baixa) e ombros largos
BODY = {
    "ian": dict(height=2, broad=True), "marco": dict(height=2, broad=True), "brainy": dict(height=1, broad=True),
    "barry": dict(height=1, broad=True), "rafa": dict(height=1, broad=True), "theo": dict(height=1, broad=True),
    "joca": dict(broad=True), "sam": dict(height=1), "addison": dict(height=1),     # entre elas, só Letícia,
    # Sam e Addison são mais altas (a Letícia fica em entities.PLAYER_LOOK)
    "jess": dict(height=-1), "bea": dict(height=-1), "graca": dict(height=-1), "yang": dict(height=-1),
}
for _k, _b in BODY.items():
    NPCS[_k]["look"].update(_b)
    if NPCS[_k].get("look_off"):
        NPCS[_k]["look_off"].update(_b)

