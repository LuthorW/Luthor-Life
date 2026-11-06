"""Eventos de coração novos: cenas para quem ainda não tinha e um bônus para cada amizade.

Novas cenas: Theo 4, Bea 4, Marco 4, Nia 5, Harry 5, Seu Joca 5, Meredith 5, Cristina 5, Izzie 5, Addison 5,
Barry 8, Dona Graça 6, Brainy 8 e Jess 7. Theo, Bea e Marco também ganham um evento de 2 corações sem cena.

Bônus novos (flags):
  theo_livro      todo sábado o Theo separa um livro para você (Livro Raro ou Romance Policial)
  bea_fresh       20% de desconto no Mercado Central
  marco_tab       sinuca e dardos de graça e 25% de desconto no Noonan's
  izzie_doces     doces dão 50% mais energia
  addison_care    presentes rendem 15% mais amizade
  barry_fotos     cada espécie nova de peixe vira foto para a CatCo: +$50
  graca_marmita   toda sexta a Dona Graça manda uma moqueca
"""
from .characters import NPCS
from .cutscenes import SCENES
from .data import FLAG_LABELS, ITEMS
from .config import C_GOLD, C_GREEN

SWEETS = {"rosquinha", "croissant", "tiramisu", "bolo", "torta_morango", "torta_abobora", "chocolate_quente",
          "morango", "amora", "pipoca"}
SWEET_ICONS = {"donut", "cake", "pie", "cocoa", "croissant", "chocbar"}

FLAG_LABELS.update({
    "theo_livro": "Clube do livro do Theo: todo sábado um livro separado para você.",
    "bea_fresh": "Preço de família da Bea: 20% de desconto no Mercado Central.",
    "marco_tab": "Conta da casa no Noonan's: sinuca e dardos de graça e 25% de desconto.",
    "izzie_doces": "Receitas da Izzie: doces dão 50% mais energia.",
    "addison_care": "Embrulho da Addison: presentes rendem 15% mais amizade.",
    "barry_fotos": "Fotos do Barry: cada espécie nova de peixe rende $50 da CatCo.",
    "graca_marmita": "Marmita da Dona Graça: toda sexta chega uma moqueca.",
})

TITLES = {
    "theo_4": "Theo: o clube do livro", "bea_4": "Bea: o caderno dos clientes", "marco_4": "Marco: a música da jukebox",
    "nia_5": "Nia: o sonho", "rafa_5": "Harry: arte no café", "joca_5": "Seu Joca: o barco Iracema",
    "meredith_5": "Meredith: a sombra da mãe", "yang_5": "Cristina: a proposta", "izzie_5": "Izzie: o bolo da notícia boa",
    "addison_5": "Addison: cuidar de quem cuida", "barry_8": "Barry: a exposição", "graca_6": "Dona Graça: a receita da mãe",
    "brainy_8": "Brainy: o substituto", "jess_7": "Jess: a proposta de emprego",
}

SC = {}

SC["theo_4"] = dict(map="books", time=17 * 60, npc="theo", steps=[
    ("ator", "theo", 13, 4, "down"), ("ator", "player", 8, 10, "up"),
    ("camera_ja", 10, 6), ("fade_in",),
    ("legenda", "Bayside Books, fim de tarde", 1.8),
    ("andar", "player", 13, 6), ("virar", "player", "up"),
    ("fala", "theo", "Letícia! Que bom. Eu estava ensaiando um discurso e você chegou bem na parte difícil."),
    ("narra", "Em cima do balcão, seis cadeiras de plástico empilhadas e um cartaz feito à mão: CLUBE DO LIVRO, QUINTAS, 19H."),
    ("fala", "theo", "Faz vinte anos que eu quero um clube do livro. Toda quinta eu arrumo as cadeiras e ninguém vem."),
    ("fala", "theo", "Aí eu pensei: se a CEO da Luthor Corp entrar, metade da cidade entra atrás. É marketing, não é?", "smile"),
    ("emote", "player", "feliz"),
    ("escolha", "O que dizer?", [
        ("Eu entro. E levo a Jess, ela lê três livros por semana.", 70,
         "Três por semana! Vou precisar de mais cadeiras. E de um segundo bule de chá."),
        ("Só se o primeiro livro for um policial.", 55,
         "Combinado. Eu já sei qual: um que nem eu adivinhei o final."),
        ("Theo, eu mal tenho tempo de dormir.", 25,
         "Ninguém tem. Por isso o livro é curto. Pense nisso."),
    ]),
    ("fala", "theo", "Vou fazer melhor: todo sábado eu separo um livro para você. Escolhido a dedo.", "happy"),
    ("efeito", "brilhos", 1.4),
    ("esperar", 0.8), ("fade_out",),
])

SC["bea_4"] = dict(map="market", time=8 * 60, npc="bea", steps=[
    ("ator", "bea", 3, 7, "up"), ("ator", "player", 8, 10, "up"),
    ("camera_ja", 6, 7), ("fade_in",),
    ("legenda", "Mercado Central, logo cedo", 1.8),
    ("andar", "player", 8, 7), ("andar", "player", 5, 7), ("virar", "player", "left"),
    ("fala", "bea", "Bom dia, Letícia! Cheguei agora da central de abastecimento. Quatro da manhã, dá pra acreditar?"),
    ("virar", "bea", "right"),
    ("fala", "bea", "Olha isso. Meu caderno. Cada cliente tem uma página.", "smile"),
    ("narra", "Um caderno de capa mole, cheio de letra redonda: \"Dona Graça: tomate bem maduro. Theo: só tangerina. Brainy: NUNCA coentro.\""),
    ("fala", "bea", "Minha avó tinha uma banca em Lisboa e fazia isso. Dizia que freguês é gente, não é número."),
    ("fala", "bea", "Ano passado uma rede de supermercado quis comprar o prédio. Eu disse não. Três vezes.", "bad"),
    ("escolha", "O que dizer?", [
        ("O que tem escrito na minha página?", 70, "\"Compra rápido, paga direito, sempre leva uma flor a mais.\" Gosto de você."),
        ("Você fez bem. O mercado é o coração do bairro.", 60, "É o que eu acho. Coração não se vende."),
        ("Quanto eles ofereceram?", 25, "Muito. E foi pouco. Pergunta de CEO, essa."),
    ]),
    ("fala", "bea", "A partir de hoje, você paga preço de família aqui. Não discute.", "happy"),
    ("efeito", "brilhos", 1.4),
    ("esperar", 0.8), ("fade_out",),
])

SC["marco_4"] = dict(map="bar", time=23 * 60, npc="marco", steps=[
    ("ator", "marco", 4, 3, "down"), ("ator", "player", 8, 10, "up"), ("segurar", "marco", "cerveja"),
    ("camera_ja", 6, 5), ("fade_in",),
    ("legenda", "Noonan's, quase fechando", 1.8),
    ("andar", "player", 4, 10), ("andar", "player", 4, 5), ("virar", "player", "up"),
    ("fala", "marco", "Última rodada e a casa vazia. Meu horário favorito."),
    ("beber", "marco"), ("segurar", "player", "cerveja"),
    ("fala", "marco", "Quer saber um segredo? A música número 7 da jukebox é minha.", "smile"),
    ("emote", "player", "surpresa"),
    ("fala", "marco", "Eu tinha uma banda de jazz. Tocávamos em Gotham, em porão de hotel, para quatro pessoas e um gato."),
    ("narra", "Ele aperta um botão embaixo do balcão. A jukebox acende e um saxofone começa, meio desafinado, meio bonito."),
    ("efeito", "brilhos", 1.2),
    ("fala", "marco", "Gravamos um disco só. Vendemos trinta. Esse aqui é o último que sobrou."),
    ("escolha", "O que dizer?", [
        ("É lindo, Marco. Por que parou?", 65, "Porque o bar paga as contas. Mas toda noite eu toco ela pra mim."),
        ("Você devia tocar ao vivo aqui no Noonan's.", 70, "...Sexta que vem. Se você vier, eu toco. Fechado?"),
        ("Gotham tem bons porões mesmo.", 30, "E péssimos gatos. Aquele nunca aplaudiu."),
    ]),
    ("fala", "marco", "Daqui pra frente, sua conta é da casa. Sinuca, dardos, o que quiser.", "happy"),
    ("brinde", "marco", "player"), ("beber", "marco"),
    ("esperar", 0.8), ("fade_out",),
])

SC["nia_5"] = dict(map="catco", time=19 * 60, npc="nia", steps=[
    ("ator", "nia", 4, 5, "up"), ("ator", "player", 11, 13, "up"),
    ("camera_ja", 7, 7), ("fade_in",),
    ("legenda", "CatCo, redação vazia", 1.8),
    ("andar", "player", 12, 7), ("andar", "player", 5, 7), ("andar", "player", 5, 5), ("virar", "player", "left"),
    ("virar", "nia", "right"),
    ("fala", "nia", "Ah! Letícia. Desculpa, eu estava... escrevendo um sonho.", "shy"),
    ("fala", "nia", "Eu anoto todos. Às vezes eles acontecem. Não do jeito que eu sonhei, mas acontecem."),
    ("fala", "nia", "Essa semana eu sonhei com você numa praça cheia de gente. Todo mundo aplaudindo. Você com vergonha."),
    ("emote", "player", "vergonha"),
    ("fala", "nia", "Viu? Já está acontecendo.", "happy"),
    ("escolha", "O que dizer?", [
        ("Você devia publicar esses sonhos. Como uma coluna.", 65, "\"Sonhos de Nia\". Hum. A Cat Grant ia odiar. Eu adorei."),
        ("E você sonha com o seu futuro também?", 60, "Quase nunca. Acho que a gente não sonha com o que tem medo de saber."),
        ("Eu prefiro números a sonhos.", 25, "Números também são sonhos. Só que com planilha."),
    ]),
    ("fala", "nia", "Obrigada por não rir de mim. Pouca gente não ri.", "smile"),
    ("esperar", 0.8), ("fade_out",),
])

SC["rafa_5"] = dict(map="cafe", time=20 * 60, npc="rafa", steps=[
    ("ator", "rafa", 4, 3, "down"), ("ator", "player", 7, 9, "up"),
    ("camera_ja", 6, 5), ("fade_in",),
    ("legenda", "Grão Nobre, depois de fechar", 1.8),
    ("andar", "player", 4, 9), ("andar", "player", 4, 5), ("virar", "player", "up"),
    ("fala", "rafa", "Porta fechada, máquina ligada. Hora da aula. Hoje: coração no leite.", "happy"),
    ("narra", "Harry desenha um coração perfeito na espuma em três segundos. Depois passa a jarra para você."),
    ("emote", "player", "gota"),
    ("narra", "O seu sai com formato de... batata. Uma batata triste."),
    ("fala", "rafa", "Isso é uma nuvem? Um cachorro? Uma reestruturação societária?", "smile"),
    ("fala", "rafa", "Sabe o meu sonho? Torrar meu próprio café. Uma torrefação pequena, aqui no bairro."),
    ("escolha", "O que dizer?", [
        ("Me manda o plano. A Sam olha os números.", 65, "Sério? ...Ai. Agora vou ter que fazer uma planilha."),
        ("Você é o melhor barista da cidade. Vai dar certo.", 60, "Para de me elogiar, senão o leite talha."),
        ("Torrefação dá lucro?", 25, "Dá cheiro bom. Lucro a gente vê depois."),
    ]),
    ("fala", "rafa", "Esse cappuccino com a batata é seu. Por conta da casa.", "happy"),
    ("efeito", "brilhos", 1.2),
    ("esperar", 0.8), ("fade_out",),
])

SC["joca_5"] = dict(map="city", time=6 * 60 + 30, npc="joca", steps=[
    ("ator", "joca", 60, 58, "down"), ("ator", "player", 60, 53, "down"),
    ("camera_ja", 60, 57), ("fade_in",),
    ("legenda", "Píer da orla, de madrugada", 2.0),
    ("andar", "player", 61, 57), ("virar", "player", "down"),
    ("fala", "joca", "Madrugou, dona Letícia? Senta aqui. O mar está calmo hoje."),
    ("narra", "Lá no fundo, um barquinho azul descascado balança preso numa boia."),
    ("fala", "joca", "Aquele ali é o Iracema. Nome da minha mulher. Quarenta anos pescando juntos.", "smile"),
    ("fala", "joca", "Ela se foi faz cinco anos. O barco ficou. Eu não tenho coragem de vender, nem de sair com ele.", "bad"),
    ("emote", "player", "triste"),
    ("escolha", "O que dizer?", [
        ("O Ian pode reformar o Iracema na marina. Se o senhor quiser.", 70,
         "...O menino do barco? Ele ia fazer isso? Ia ficar azul de novo?"),
        ("Conta como ela era.", 65, "Ria alto. Assustava os peixes. Eu pescava menos e era mais feliz."),
        ("O senhor pensa em parar de pescar?", 25, "Parar? Só se o mar secar, minha filha."),
    ]),
    ("fala", "joca", "Obrigado por ouvir um velho. Agora vai, que o robalo não espera.", "happy"),
    ("esperar", 0.8), ("fade_out",),
])

SC["meredith_5"] = dict(map="hospital", time=20 * 60, npc="meredith", steps=[
    ("ator", "meredith", 6, 12, "right"), ("ator", "player", 13, 15, "up"),
    ("camera_ja", 8, 12), ("fade_in",),
    ("legenda", "Conti Moretti, saguão quase vazio", 1.8),
    ("andar", "player", 8, 15), ("andar", "player", 8, 12), ("virar", "player", "left"),
    ("fala", "meredith", "Letícia. Senta. Eu acabei de sair de doze horas de cirurgia e preciso falar com alguém que não seja paciente."),
    ("fala", "meredith", "Hoje um residente me disse: \"Você opera igualzinho à sua mãe\". Era para ser um elogio."),
    ("fala", "meredith", "Ela foi uma cirurgiã genial. E uma mãe... ocupada.", "bad"),
    ("emote", "player", "reticencias"),
    ("fala", "player", "Eu sei como é. Meu pai construiu a Luthor Corp. Todo mundo espera que eu seja ele."),
    ("escolha", "O que dizer?", [
        ("A gente pode ser boa no que eles eram e diferente no resto.", 70,
         "...É. Talvez seja isso. Boa na mesa de cirurgia. Diferente no jantar de domingo."),
        ("Você não é a sua mãe. Você é a Meredith Grey.", 60, "Isso foi quase um discurso motivacional. Quase."),
        ("Pelo menos você herdou o talento.", 30, "Herdei. E as dívidas emocionais, de brinde."),
    ]),
    ("fala", "meredith", "Obrigada. Agora vai pra casa dormir. Ordem médica.", "smile"),
    ("esperar", 0.8), ("fade_out",),
])

SC["yang_5"] = dict(map="hospital", time=7 * 60 + 30, npc="yang", steps=[
    ("ator", "yang", 9, 4, "down"), ("ator", "player", 9, 9, "up"),
    ("camera_ja", 9, 6), ("fade_in",),
    ("legenda", "Conti Moretti, consultório da Direção Médica", 1.8),
    ("andar", "player", 9, 6), ("virar", "player", "up"),
    ("fala", "yang", "Você está atrasada dois minutos. Eu fiz uma apresentação de onze slides. Senta."),
    ("narra", "No tablet dela, o desenho de um braço robótico com o logo do Conti Moretti e um ponto de interrogação no lugar do preço."),
    ("fala", "yang", "Robô cirúrgico de nova geração. Cirurgia cardíaca com metade do corte e metade do tempo de recuperação."),
    ("fala", "yang", "Eu não peço dinheiro para ninguém. Estou pedindo para você porque você entende de máquina e não tem medo de número."),
    ("escolha", "O que dizer?", [
        ("Manda o projeto para o Brainy. Se ele aprovar, a Luthor Corp entra.", 70,
         "Ótimo. Ele vai fazer cem perguntas. Eu tenho cento e uma respostas."),
        ("Quantos pacientes ele salva por ano?", 65, "Essa é a pergunta certa. Slide sete. Eu sabia que você ia perguntar."),
        ("Por que não pede para o hospital?", 25, "Porque o hospital demora um ano para dizer talvez."),
    ]),
    ("fala", "yang", "Você não piscou com o preço. Gosto disso.", "smile"),
    ("esperar", 0.8), ("fade_out",),
])

SC["izzie_5"] = dict(map="hospital", time=12 * 60 + 30, npc="izzie", steps=[
    ("ator", "izzie", 6, 14, "right"), ("ator", "player", 13, 15, "up"),
    ("camera_ja", 8, 13), ("fade_in",),
    ("legenda", "Conti Moretti, hora do almoço", 1.8),
    ("andar", "player", 8, 15), ("andar", "player", 8, 14), ("virar", "player", "left"),
    ("fala", "izzie", "Letícia! Pega um pedaço. É bolo de laranja. Eu fiz às cinco da manhã.", "happy"),
    ("fala", "izzie", "Eu cozinho quando estou nervosa. E quando estou feliz. E quando é terça."),
    ("fala", "izzie", "Hoje é feliz: uma paciente minha terminou o tratamento. Exames limpos. Ela chorou, eu chorei, a enfermeira chorou.", "happy"),
    ("emote", "izzie", "coracao"),
    ("escolha", "O que dizer?", [
        ("Que notícia linda. Ela tem sorte de ter você.", 70, "Eu é que tenho sorte. Ela me ensinou a fazer esse bolo, sabia?"),
        ("Me passa a receita?", 60, "Passo! O segredo é raspar a casca. E cantar enquanto mexe."),
        ("Bolo no hospital pode?", 25, "Pode se ninguém da administração descobrir."),
    ]),
    ("fala", "izzie", "Vou te ensinar a fazer doce de verdade. Doce feito com carinho dá mais energia, é ciência. Mais ou menos.", "smile"),
    ("efeito", "brilhos", 1.2),
    ("esperar", 0.8), ("fade_out",),
])

SC["addison_5"] = dict(map="hospital", time=16 * 60, npc="addison", steps=[
    ("ator", "addison", 22, 5, "down"), ("ator", "player", 22, 9, "up"),
    ("camera_ja", 22, 6), ("fade_in",),
    ("legenda", "Conti Moretti, ala de internação", 1.8),
    ("andar", "player", 22, 6), ("virar", "player", "up"),
    ("fala", "addison", "Shh. Os bebês da maternidade estão dormindo e as mães também. Milagre de terça-feira."),
    ("narra", "Em cima do carrinho, uma pilha de caixinhas embrulhadas com fita: uma para cada mãe da ala."),
    ("fala", "addison", "São bobagens. Hidratante, um chá, um bilhete. Mas ninguém cuida de quem cuida, então eu cuido.", "smile"),
    ("fala", "addison", "E você? Quem cuida da CEO?"),
    ("emote", "player", "reticencias"),
    ("escolha", "O que dizer?", [
        ("Acho que ninguém. Eu nunca pensei nisso.", 70, "Então começa por aí. E me deixa te ensinar a embrulhar presente."),
        ("Meus amigos. Aos poucos.", 60, "Bom. Aos poucos é como as melhores coisas chegam."),
        ("Eu tenho uma assistente ótima.", 30, "A Jess cuida da sua agenda. Não de você."),
    ]),
    ("fala", "addison", "O segredo não é o presente. É o bilhete. Escreve de verdade e qualquer coisa vira especial.", "happy"),
    ("esperar", 0.8), ("fade_out",),
])

SC["barry_8"] = dict(map="city", time=17 * 60 + 30, npc="barry", steps=[
    ("ator", "barry", 10, 40, "left"), ("ator", "player", 14, 44, "up"),
    ("camera_ja", 11, 41), ("fade_in",),
    ("legenda", "Lago do Parque Central, luz dourada", 2.0),
    ("andar", "player", 12, 41), ("andar", "player", 12, 40), ("virar", "player", "left"),
    ("virar", "barry", "right"),
    ("fala", "barry", "Letícia! Notícia: uma galeria de Gotham quer expor minhas fotos. Uma sala inteira. MINHA.", "happy"),
    ("pulo", "barry"),
    ("fala", "barry", "O nome da exposição é \"National City de perto\". E a foto principal... bom, é você."),
    ("emote", "player", "surpresa"),
    ("fala", "barry", "Rindo, na festa, com o cabelo cheio de confete. Ninguém acredita que é a CEO da Luthor Corp.", "smile"),
    ("escolha", "O que dizer?", [
        ("Pode usar. Mas eu quero uma cópia autografada.", 70, "Fechado! A primeira cópia é sua. Com dedicatória e tudo."),
        ("Barry, que orgulho. Você merece.", 65, "Para, senão eu choro na frente do lago e assusto os patos."),
        ("A assessoria precisa aprovar.", 25, "...Eu mando por e-mail. Com cópia para a Jess. Em três vias."),
    ]),
    ("fala", "barry", "Ah, e a CatCo quer uma série sobre os peixes da cidade. Cada peixe novo que você pescar, eu fotografo. E a revista paga!", "happy"),
    ("efeito", "brilhos", 1.4),
    ("esperar", 0.8), ("fade_out",),
])

SC["graca_6"] = dict(map="trattoria", time=10 * 60, npc="graca", steps=[
    ("ator", "graca", 7, 3, "down"), ("ator", "player", 10, 11, "up"),
    ("camera_ja", 9, 6), ("fade_in",),
    ("legenda", "Ricci Trattoria, antes de abrir", 1.8),
    ("andar", "player", 15, 9), ("andar", "player", 15, 4), ("andar", "player", 8, 4), ("virar", "player", "left"),
    ("fala", "graca", "Lava a mão e vem cá. Hoje você não é CEO, é ajudante de cozinha.", "happy"),
    ("narra", "Na bancada: aipim, coco ralado, açúcar e uma colher de pau que parece mais velha que a Trattoria."),
    ("fala", "graca", "Bolo de aipim da minha mãe. Ela fazia todo domingo, lá em Salvador, e a rua inteira sabia."),
    ("fala", "graca", "Eu nunca ensinei pra ninguém. A Vittoria pediu, eu enrolei. Mas você tem mão de quem não desiste."),
    ("emote", "player", "vergonha"),
    ("escolha", "O que dizer?", [
        ("É uma honra, Dona Graça. Vou guardar essa receita.", 70, "Guarda no coração. Papel molha."),
        ("A senhora ensina a Vittoria também?", 60, "Ensino. Mas não conta que você aprendeu primeiro."),
        ("Isso leva muito tempo?", 25, "Leva o tempo que leva, filha. Bolo não tem pressa."),
    ]),
    ("fala", "graca", "E toda sexta eu vou mandar uma marmita pra você. Moqueca. Que você vive de café, eu sei.", "happy"),
    ("efeito", "brilhos", 1.4),
    ("esperar", 0.8), ("fade_out",),
])

SC["brainy_8"] = dict(map="hq", time=21 * 60, npc="brainy", steps=[
    ("ator", "brainy", 11, 3, "up"), ("ator", "player", 12, 16, "up"),
    ("camera_ja", 13, 5), ("fade_in",),
    ("legenda", "Laboratório da Luthor Corp, noite", 1.8),
    ("andar", "player", 17, 16), ("andar", "player", 17, 3), ("andar", "player", 12, 3), ("virar", "player", "left"),
    ("virar", "brainy", "right"),
    ("fala", "brainy", "CEO. Pergunta hipotética: se uma IA fizesse o meu trabalho 40% mais rápido, você me demitiria?"),
    ("emote", "player", "pergunta"),
    ("fala", "brainy", "Não é hipotética. Eu construí a IA. Ela é ótima. Eu estou... preocupado.", "bad"),
    ("narra", "Na tela do terminal, uma janela pisca: \"OLÁ, SOU A QUERL 2.0. COMO POSSO OTIMIZAR SEU DIA?\""),
    ("escolha", "O que dizer?", [
        ("A IA é rápida. Mas foi você que teve a ideia. Isso ela não faz.", 75,
         "...Isso é verdade. Ela nem sabe o que é uma ideia. Eu perguntei."),
        ("Ninguém aqui substitui você, Brainy.", 60, "Estatisticamente improvável. Emocionalmente... obrigado."),
        ("40% mais rápido? Me manda o relatório.", 20, "Eu sabia. Vou apagá-la. Brincadeira. Talvez."),
    ]),
    ("fala", "brainy", "Vou renomear a IA para \"Assistente do Brainy\". Hierarquia é importante.", "happy"),
    ("emote", "brainy", "estrela"),
    ("esperar", 0.8), ("fade_out",),
])

SC["jess_7"] = dict(map="hq", time=18 * 60 + 30, npc="jess", steps=[
    ("ator", "jess", 12, 11, "down"), ("ator", "player", 12, 16, "up"),
    ("camera_ja", 12, 12), ("fade_in",),
    ("legenda", "Luthor Corp, depois do expediente", 1.8),
    ("andar", "player", 12, 13), ("virar", "player", "up"),
    ("fala", "jess", "Chefe, eu preciso te contar uma coisa e prefiro falar rápido, antes de perder a coragem."),
    ("fala", "jess", "Uma empresa de Metropolis me ofereceu um cargo de diretora. Salário dobrado. Sala com janela.", "shy"),
    ("emote", "player", "surpresa"),
    ("fala", "jess", "Eu disse que ia pensar. Pensei. E vim te dizer que eu fico."),
    ("fala", "jess", "Aqui ninguém me chama de \"a assistente\". Você me chama de Jess. E me escuta.", "smile"),
    ("escolha", "O que dizer?", [
        ("Então a sala com janela é aqui. E o cargo novo também.", 75,
         "Você... Chefe. Eu vou chorar e borrar a agenda inteira."),
        ("Eu ia lutar por você, sabia? Com contrato e tudo.", 65, "Eu sei. A Sam já tinha um rascunho pronto. Eu vi."),
        ("Você tem certeza? É muito dinheiro.", 30, "Tenho. Dinheiro não organiza a minha vida. Você deixa eu organizar a sua."),
    ]),
    ("fala", "jess", "Agora vai pra casa. Sua agenda de amanhã começa às oito e eu já tirei duas reuniões chatas.", "happy"),
    ("efeito", "brilhos", 1.2),
    ("esperar", 0.8), ("fade_out",),
])

SCENES.update(SC)

# (personagem, corações, evento)
NEW_EVENTS = [
    ("theo", 2, dict(lines=["Sabia que você é a única cliente que lê a orelha do livro antes de comprar?",
                            "Isso diz muito sobre uma pessoa. Eu gosto de quem lê a orelha."])),
    ("theo", 4, dict(scene="theo_4", flag="theo_livro", lines=["Todo sábado eu separo um livro para você."])),
    ("bea", 2, dict(lines=["Separei as melhores tangerinas da caixa. Não conta pro Theo, ele acha que são dele.",
                           "Volta sempre, viu? Você já tem uma página no meu caderno."], gift="morango")),
    ("bea", 4, dict(scene="bea_4", flag="bea_fresh", lines=["Para você, preço de família."])),
    ("marco", 2, dict(lines=["Você é a única cliente que agradece o gelo. Sério. Ninguém agradece o gelo.",
                             "Pra você, o próximo drinque sai com uma cereja a mais."])),
    ("marco", 4, dict(scene="marco_4", flag="marco_tab", lines=["Sua conta é da casa daqui pra frente."])),
    ("nia", 5, dict(scene="nia_5", lines=["Obrigada por não rir dos meus sonhos."])),
    ("rafa", 5, dict(scene="rafa_5", gift="cappuccino", lines=["Esse cappuccino é por conta da casa."])),
    ("joca", 5, dict(scene="joca_5", gift="robalo", lines=["Leva esse robalo, pescado do jeito certo."])),
    ("meredith", 5, dict(scene="meredith_5", lines=["Obrigada por ouvir."])),
    ("yang", 5, dict(scene="yang_5", lines=["Você não piscou com o preço."])),
    ("izzie", 5, dict(scene="izzie_5", flag="izzie_doces", lines=["Doce feito com carinho dá mais energia."])),
    ("addison", 5, dict(scene="addison_5", flag="addison_care", lines=["O segredo é o bilhete."])),
    ("barry", 8, dict(scene="barry_8", flag="barry_fotos", lines=["Cada peixe novo, uma foto para a CatCo."])),
    ("graca", 6, dict(scene="graca_6", flag="graca_marmita", lines=["Toda sexta tem marmita."])),
    ("brainy", 8, dict(scene="brainy_8", gift="software", lines=["Hierarquia é importante."])),
    ("jess", 7, dict(scene="jess_7", lines=["Eu fico."])),
]
for _k, _h, _ev in NEW_EVENTS:
    if _k in NPCS:
        NPCS[_k].setdefault("events", {}).setdefault(_h, _ev)


# ---------------------------------------------------------------------------
# Bônus
# ---------------------------------------------------------------------------
def shop_mult(g, shop_id):
    if shop_id == "market" and "bea_fresh" in g.flags:
        return 0.8
    if shop_id == "bar" and "marco_tab" in g.flags:
        return 0.75
    return 1.0


def play_cost(g, base):
    return 0 if "marco_tab" in g.flags else base


def food_mult(g, item):
    if "izzie_doces" not in g.flags:
        return 1.0
    it = ITEMS.get(item, {})
    return 1.5 if item in SWEETS or it.get("icon") in SWEET_ICONS else 1.0


def gift_mult(g, taste):
    return 1.15 if "addison_care" in g.flags and taste != "dislike" else 1.0


def new_fish(g, fish):
    if "barry_fotos" in g.flags:
        g.money += 50
        g.toasts.push("O Barry fotografou o peixe novo para a CatCo: +$50", C_GOLD)


def morning(g):
    if "theo_livro" in g.flags and g.weekday == 5:
        item = "livro" if g.abs_day() % 2 else "policial"
        if g.add_item(item):
            g.toasts.push(f"O Theo separou um livro para você: {ITEMS[item]['name']}.", C_GREEN, item)
    if "graca_marmita" in g.flags and g.weekday == 4:
        if g.add_item("moqueca"):
            g.toasts.push("Chegou a marmita da Dona Graça: Moqueca!", C_GREEN, "moqueca")
