"""Celular da Letícia (tecla T): apps Mensagens, Agenda, Tempo, Bolsa, Fotos, Pedidos, Habilidades e Mapa.

Mensagens: amigas com 2+ corações mandam mensagens de vez em quando (`MSGS`, por personagem; `GENERIC` serve para
quem não tem fala própria) e a namorada manda bom-dia (`MORNING`). Chegam pela manhã (`morning`) e ao longo do dia
(`tick`, no máx. `MAX_PER_DAY`), com aviso no canto. Cada mensagem tem 3 respostas próprias, e cada resposta tem a
volta de quem mandou (`REPLIES_FOR`, pelo texto; saves antigos também acham). Responder dá amizade (+`REPLY_POINTS`,
uma vez por mensagem); a resposta e a volta ficam guardadas na mensagem (`reply`, `back`) e aparecem na conversa.
Agenda junta as linhas do HUD (festa, eventos, casamento...) e os próximos 7 dias (festas, aniversários).
Bolsa guarda o fechamento de cada noite (`g.phone["stocks"]`). Estado em `g.phone`.
"""
import random

import pygame

from . import ui, audio, art, seasons, festas, habilidades, mural, pedidos, lugares
from .config import (SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_PINK, C_RED,
                     DAYS_PER_QUARTER)
from .data import ITEMS
from .characters import NPCS, NPC_ORDER, ROMANCES

MAX_MSGS = 40
MAX_PER_DAY = 3
REPLY_POINTS = 20
STOCK_DAYS = 28

# Cada mensagem: (texto, [(resposta da Letícia, o que a pessoa responde), ...]) — sempre 3 respostas que
# combinam com aquela mensagem. `REPLIES_FOR` acha as respostas pelo texto (mensagens de saves antigos também).
MSGS = {
    "sam": [
        ("Fechei o trimestre com a planilha mais bonita da minha vida. Vem ver? É sério, tem cores.",
         [("Cores? Estou indo agora mesmo.", "Separei até um gráfico de pizza pra você. A pizza é de verdade, a Ruby fez."),
          ("Você é a melhor CFO de National City.", "Só de National City? Vou fingir que não li."),
          ("Imprime e pendura na parede da sala.", "Já está na geladeira de casa. Entre os desenhos da Ruby.")]),
        ("Lembrete amigável da sua CFO: dinheiro parado não rende. Dinheiro investido em mim rende café.",
         [("Um café saindo. Com chantili de bônus.", "Isso é que é retorno sobre investimento."),
          ("Anotado. Vou olhar a Bolsa hoje.", "Ótimo. E não compra tudo de uma vez, por favor."),
          ("Você cobra juros em café?", "Juros compostos. Se atrasar, vira cappuccino.")]),
        ("A Ruby perguntou se a 'tia Letícia' vem jantar. Eu disse que você é ocupada. Ela disse 'ocupada é desculpa'.",
         [("Ela está certa. Diz que eu vou!", "Ela já está arrumando a mesa. Com os pratos de princesa."),
          ("Sexta à noite? Eu levo a sobremesa.", "Combinado. A Ruby pediu sorvete de morango. Muito."),
          ("Essa menina vai ser advogada.", "CFO, ela diz. Igual à mãe. Eu chorei um pouquinho.")]),
    ],
    "brainy": [
        ("O protótipo funcionou na terceira tentativa. A segunda explodiu, mas de um jeito educado.",
         [("Parabéns! E a sala, sobreviveu?", "Noventa e oito por cento dela. O extintor ficou orgulhoso."),
          ("Explodiu de um jeito educado como?", "Ela avisou com um apito antes. Muito respeitosa."),
          ("Me mostra amanhã na bancada.", "Agendado para 9h04. Eu sei que você chega às 9h04.")]),
        ("Calculei que você dorme 22% menos que o recomendado. Não é uma bronca. É um gráfico.",
         [("Prometo dormir mais cedo hoje.", "Registrado. Vou conferir pela luz da cobertura. Brincadeira. Talvez."),
          ("Manda o gráfico, quero ver.", "Enviei em três formatos. O de pizza ficou mais triste."),
          ("E você, dorme quanto?", "Isso é irrelevante para a pesquisa. Próxima pergunta.")]),
        ("Pergunta científica: por que o Harry desenha folhas no meu café e corações no da Jess?",
         [("Hipótese: ele gosta da Jess.", "Hipótese plausível. Vou observar os dois por uma semana. Discretamente."),
          ("Pede um coração na próxima vez.", "Pedi. Ele desenhou um cérebro. Fiquei estranhamente feliz."),
          ("Folha também é bonito, Brainy.", "Verdade. Folhas fazem fotossíntese. Corações só fazem barulho.")]),
    ],
    "jess": [
        ("Sua agenda de amanhã está livre das 15h às 15h10. Aproveite com moderação.",
         [("Dez minutos inteiros? Que luxo!", "Não se acostume. Já tem gente querendo esse horário."),
          ("Bloqueia para um café com você.", "Bloqueado. Eu levo o café, você leva os biscoitos."),
          ("Obrigada por tudo, Jess. De verdade.", "Ah, para. Assim eu fico sem jeito e erro uma vírgula.")]),
        ("Já reorganizei suas reuniões, respondi 40 e-mails e comprei seu café. Bom dia!",
         [("Você é incrível. Bom dia!", "Eu sei. Mas é bom ouvir. Seu café está na mesa, ainda quente."),
          ("São só 8h. Como você faz isso?", "Duas agendas, três alarmes e um segredo que eu não conto."),
          ("Vou te dar um aumento.", "Vou fingir que não está escrito. Mas tirei print.")]),
        ("Lembrete: você é humana e humanas almoçam. Separei 40 minutos. Não negocio.",
         [("Tá bom, mãe. Vou almoçar.", "Mãe não, assistente executiva. E foto do prato, por favor."),
          ("Almoça comigo, então?", "Só se for no Grão Nobre. E você paga, porque eu marquei."),
          ("40 minutos? Pode ser 30?", "Não negocio, eu disse. Agora são 45.")]),
    ],
    "rafa": [
        ("Testei um blend novo hoje. Guardei uma xícara pra você antes que a Jess descubra.",
         [("Guarda bem escondida. Passo aí já.", "Escondi atrás do moedor. Lugar onde ninguém procura."),
          ("Que notas ele tem?", "Chocolate, laranja e um final de castanha. Pareço chique, né?"),
          ("A Jess vai descobrir. Ela sempre descobre.", "Eu sei. Por isso fiz duas xícaras. Uma de isca.")]),
        ("Chegou grão etíope fresquinho. Vem cheirar o saco, é quase uma experiência religiosa.",
         [("Estou indo me converter.", "Missa às 15h, com expresso de comunhão."),
          ("Separa um pacote pra cobertura.", "Separado e com seu nome escrito na embalagem. Com caneta dourada."),
          ("Você fala de café do jeito mais lindo.", "É porque café é a coisa mais linda. Depois de um bom sorriso.")]),
        ("O Brainy pediu um café 'com eficiência máxima'. Servi um expresso duplo. Acho que acertei.",
         [("Acertou em cheio. Ele adora.", "Ele disse 'satisfatório'. Na língua dele, é um abraço."),
          ("Devia ter servido um triplo.", "Pensei nisso, mas a gente precisa dele vivo. O laboratório depende dele."),
          ("Desenha um coração no próximo.", "Vou desenhar um átomo. Combina mais com ele.")]),
    ],
    "lucy": [
        ("Minha editora cortou metade da matéria. A metade boa, claro. Preciso de um café e de você.",
         [("Te encontro no Grão Nobre em 20 minutos.", "Vou estar na mesa do canto, de cara amarrada. Me reconhece fácil."),
          ("Me manda a metade cortada. Eu quero ler.", "Você vai ler tudo? Até a parte das notas fiscais? Ok, agora eu fiquei boba."),
          ("A metade boa era sobre a Luthor Corp?", "Não vou responder isso. Mas era. Um pouquinho.")]),
        ("Achei uma foto nossa de Gotham numa caixa. A gente era muito nova. E muito descabelada.",
         [("Me manda! Eu quero ver.", "Só se você prometer não rir do meu cabelo. Ok, pode rir. Eu ri."),
          ("Eu lembro daquele dia.", "Eu também. Engraçado como algumas coisas não saem da cabeça."),
          ("Você estava linda. Continua.", "Para com isso, Luthor. Estou na redação e fiquei vermelha.")]),
        ("Plantão na redação. Se eu sumir, me procura atrás de uma pilha de arquivos.",
         [("Vou levar um café e um resgate.", "Melhor resgate da história. Traz um muffin também."),
          ("Não fica até tarde, tá?", "Prometo sair antes da meia-noite. Talvez. Provavelmente."),
          ("Qual é a pauta?", "Se eu contar, deixa de ser furo. Mas não é sobre você. Desta vez.")]),
    ],
    "vittoria": [
        ("Provei 14 molhos hoje. Minha língua pediu demissão. Me salva com um jantar sem tomate?",
         [("Jantar sem tomate, prometo. Te busco às 20h.", "Às 20h. Vou estar pronta e morrendo de fome."),
          ("Qual dos 14 ganhou?", "O da Dona Graça, claro. Sempre o da Dona Graça. Não conta pra ninguém."),
          ("Que tal um sushi?", "Sushi! Você é um gênio. E eu sou uma italiana muito traidora.")]),
        ("A Dona Graça disse que você come pouco. Ela mandou eu te alimentar. Eu obedeço a Dona Graça.",
         [("Então pode me alimentar. Eu deixo.", "Hoje à noite, na Trattoria. Mesa da varanda. Sem desculpas."),
          ("Eu como bem! Às vezes.", "'Às vezes' não é resposta que a Dona Graça aceite. Nem eu."),
          ("Todo mundo obedece a Dona Graça.", "Até o fogão. Juro. Ele acende mais rápido quando ela chega.")]),
        ("Inauguramos mais uma mesa na varanda. Ela tem a melhor vista. Está reservada pra você.",
         [("Hoje à noite eu passo lá.", "Vou acender a velinha. E escolher o vinho. Você escolhe a sobremesa."),
          ("A melhor vista é a de quem está na mesa.", "Letícia Luthor, você aprendeu a flertar por mensagem?"),
          ("Que orgulho de você, Vittoria.", "Grazie. Ouvir isso de você vale mais que qualquer crítica.")]),
    ],
    "nia": [
        ("Sonhei com borboletas de novo. Toda vez que eu sonho com isso, alguma coisa boa acontece. Fica de olho!",
         [("Vou ficar de olho! Me conta se acontecer.", "Você vai ser a primeira a saber. Depois do Barry. Ele pergunta todo dia."),
          ("Seus sonhos sempre acertam.", "Quase sempre. Teve aquele do pinguim de chapéu. Ainda estou esperando."),
          ("Algo bom já aconteceu: sua mensagem.", "Ownnn. Viu? Os sonhos nunca erram.")]),
        ("Terminei a matéria sobre a Fundação Luthor. Ficou bonita. Você vai chorar. Avisando antes.",
         [("Já estou com o lenço na mão.", "Pega dois. Tem foto da praça no final."),
          ("Me manda antes de publicar?", "Mando. Mas só pra você ver, não pra mudar. Ética, Letícia."),
          ("Obrigada por contar essa história.", "Ela é bonita porque é verdade. Isso facilita muito o meu trabalho.")]),
        ("O Barry tropeçou no tripé de novo. Ele está bem. O tripé, nem tanto.",
         [("Coitado do tripé! E do Barry.", "O Barry já está rindo. O tripé está de luto."),
          ("Vou dar um tripé novo de presente.", "Sério? Ele vai chorar. De novo. Ele chora fácil."),
          ("Alguém filmou?", "Eu. Claro. Está guardado para o aniversário dele.")]),
    ],
    "barry": [
        ("Tirei uma foto do pôr do sol do píer que ficou absurda. Vou te mandar quando revelar. Eu revelo, sim.",
         [("Mal posso esperar para ver!", "Vou fazer uma cópia grande. Pra parede da sua cobertura."),
          ("Revela? Isso ainda existe?", "Filme tem alma, Letícia. Digital tem pixels."),
          ("Me ensina a fotografar um dia?", "Ensino! Primeira lição: não tropeçar no tripé. Ainda estou aprendendo.")]),
        ("Cheguei atrasado na pauta. De novo. Mas cheguei com croissants, então conta como pontual.",
         [("Croissant sempre conta como pontual.", "Obrigado! Vou mostrar sua mensagem pro meu editor."),
          ("Sobrou algum pra mim?", "Guardei um de chocolate. Está um pouco amassado. Amor amassa."),
          ("Barry, compra um despertador.", "Tenho três. O problema é que eu sou rápido demais pra eles. Ou lento.")]),
        ("Se você aparecer no Parque Central hoje, eu juro que te fotografo do seu lado bom. Todos são.",
         [("Estou indo! Prepara a câmera.", "Já está pronta. E eu também. Mais ou menos."),
          ("Todos são? Você é um amor.", "É a verdade técnica. A luz concorda comigo."),
          ("Só se a foto for pro álbum.", "Fechado! O álbum fica cada vez mais bonito.")]),
    ],
    "theo": [
        ("Chegou uma edição antiga de poesia que tem a sua cara. Guardei atrás do balcão.",
         [("Passo aí hoje. Não vende pra ninguém!", "Ninguém vai encostar. Coloquei uma placa: 'reservado para a CEO'."),
          ("Qual poeta?", "Uma coletânea de 1920, com dedicatória a lápis. Os melhores livros têm história."),
          ("Você sempre acerta meu gosto.", "É meu trabalho. E um prazer. Mais prazer que trabalho.")]),
        ("Um cliente perguntou se a gente vende livros sobre 'como ser CEO'. Mandei ele te procurar.",
         [("Diz pra ele dormir mais que eu.", "Vou anotar na contracapa. Dica número um."),
          ("Eu escreveria um, mas não tenho tempo.", "Esse seria o título perfeito: 'Não tenho tempo'."),
          ("Indica um romance para ele.", "Boa ideia. Todo CEO precisa de uma boa história de amor.")]),
        ("Chuva lá fora, chá aqui dentro e um sofá livre na seção de mistério. Só dizendo.",
         [("Guarda o sofá. Estou indo.", "Já coloquei a chaleira no fogo. Camomila ou preto?"),
          ("Que convite perfeito.", "A chuva ajuda. Eu só faço o chá."),
          ("Qual mistério você recomenda?", "Um clássico, com mordomo inocente. Essa é a graça.")]),
    ],
    "bea": [
        ("Chegaram morangos lindos hoje! Separei uma caixinha. Não conta pros outros clientes.",
         [("Segredo guardado! Passo pegar.", "Estão na geladeira dos fundos, com seu nome."),
          ("A senhora me mima demais.", "Mimo quem merece, filha. E você trabalha demais."),
          ("Vou fazer uma torta com eles.", "Então leva o chantili também. Por conta da casa.")]),
        ("Minha neta aprendeu a fazer troco sozinha. Já pode trabalhar no caixa. Tem seis anos.",
         [("Contrata ela! Vai ser gerente.", "Ela já pediu um crachá. E um aumento."),
          ("Que orgulho! Dá um beijo nela.", "Ela mandou outro de volta. E um desenho de você."),
          ("Seis anos? Mais rápida que eu.", "Mais rápida que todo mundo. Puxou a avó.")]),
        ("Promoção de farinha amanhã. Ouvi dizer que alguém anda fazendo panqueca...",
         [("Fui descoberta! Guarda dois pacotes.", "Guardados. E ovos fresquinhos também."),
          ("Quem te contou?", "A Dona Graça. Ela sabe de tudo. Eu também, um pouco."),
          ("Te levo umas panquecas depois.", "Ah, que delícia! Com mel, por favor.")]),
    ],
    "graca": [
        ("Fiz moqueca hoje e sobrou. Quer dizer, eu fiz a mais pensando em você. Passa aqui, menina.",
         [("Estou indo! Guarda o pirão.", "Pirão guardado e arroz quentinho. Vem logo."),
          ("A senhora é um anjo, Dona Graça.", "Anjo nada. Sou cozinheira. Mas aceito o elogio."),
          ("Posso levar uma amiga?", "Pode trazer quem quiser. Comida boa é pra dividir.")]),
        ("Você comeu hoje? Comeu direito? Não vale café. Café não é comida, é tempero da vida.",
         [("Comi! Uma salada de verdade.", "Salada é enfeite de prato. Vem comer um feijão."),
          ("Ainda não... mas vou comer.", "Vou ficar esperando a foto do prato. Com arroz."),
          ("Café com pão de queijo conta?", "Pão de queijo conta, sim. Mas só porque é brasileiro.")]),
        ("Minha mãe dizia: quem cozinha com raiva salga demais. Hoje eu cozinhei com saudade. Ficou doce.",
         [("Saudade de quê, Dona Graça?", "Da minha terra, menina. Mas aqui também virou casa."),
          ("Que bonito isso.", "Bonito é ter pra quem cozinhar. Isso você me dá."),
          ("Quero provar esse prato doce.", "Vem amanhã. Faço de novo, com a mesma saudade.")]),
    ],
    "marco": [
        ("Inventei um drinque novo. Ainda não tem nome. Pensei em 'A CEO'. Forte e caro.",
         [("Aprovado! Quero o primeiro.", "O primeiro é por conta da casa. O segundo, você paga dobrado."),
          ("Forte e caro? Que exagero.", "Também é elegante e deixa todo mundo acordado. Combina."),
          ("Que tal 'A Reunião das 8h'?", "Esse é amargo demais. Ninguém ia pedir.")]),
        ("Noite tranquila no Noonan's. A mesa de sinuca está te esperando. E eu também, para te ganhar.",
         [("Prepara o taco. Estou indo.", "Já passei giz. Não vai ter desculpa."),
          ("Você nunca me ganhou, Marco.", "Nunca é muito tempo. Hoje é a noite."),
          ("Hoje não, mas amanhã com certeza.", "Vou treinar a noite toda. Prepara o orgulho.")]),
        ("Sexta tem karaokê. A Nia já reservou três músicas. Corre.",
         [("Reserva uma pra mim!", "Reservei. Uma balada bem dramática. Sua cara."),
          ("Só três? A Nia está contida.", "Ela reservou três hoje. Amanhã ela pede mais cinco."),
          ("Eu vou só pra assistir.", "Ninguém só assiste no Noonan's. É regra da casa.")]),
    ],
    "joca": [
        ("Ô moça, o mar tá calmo hoje. Os peixes tão de bom humor. Traz a vara!",
         [("Estou indo pro píer agora!", "Te espero com isca fresquinha. Hoje é dia!"),
          ("E o senhor, já pegou algum?", "Três! Mas soltei dois. Eram pequenos e tinham família."),
          ("Guarda uma isca boa pra mim.", "A melhor, separada. Minhoca de primeira.")]),
        ("Peguei um robalo deste tamanho. Não, maior. Tô abrindo os braços aqui, você que não tá vendo.",
         [("Manda foto ou não aconteceu!", "A foto saiu tremida. Mas o peixe era enorme, juro."),
          ("Daqui já dá pra ver o tamanho.", "Viu? Você entende de pesca. Eu sempre soube."),
          ("Um dia eu pego um maior.", "Pega, sim. Mas aí eu vou ter que pescar dois.")]),
        ("Choveu? Então é dia de peixe-gato no lago. Isso não falha desde 1987.",
         [("Vou tentar no lago hoje!", "Isso! Joga perto das pedras. É lá que eles se escondem."),
          ("Desde 1987? Que precisão.", "Anotado no caderninho. Tenho 40 anos de caderninho."),
          ("Obrigada pela dica, Joca.", "Dica de pescador não se agradece. Se pesca.")]),
    ],
    "ian": [
        ("O veleiro novo chegou. Ela é linda. O veleiro, digo. Vem conhecer?",
         [("Vou hoje à tarde na marina!", "Vou deixar ela brilhando pra você. O veleiro, digo."),
          ("Que nome você deu pra ela?", "Ainda não sei. Aceito sugestões. Nada de 'Barquinho', por favor."),
          ("O veleiro, sei...", "Para com isso. Ela é só um barco. Lindo. Muito lindo.")]),
        ("Lembra quando a gente fazia barquinho de papel no riacho do sítio? Hoje eu fiz um de verdade.",
         [("Lembro! O meu sempre afundava.", "Porque você colocava pedra dentro 'pra dar estabilidade'."),
          ("Você realizou o sonho de criança.", "A gente realizou. Sem a Luthor Corp eu não estaria aqui."),
          ("Vamos fazer um de papel de novo?", "Vamos. No píer, domingo. O perdedor paga o sorvete.")]),
        ("Previsão boa pra amanhã: vento leste, mar liso. Dia perfeito pra regata.",
         [("Prepara o barco. Eu vou!", "Vou deixar tudo pronto. Leva protetor solar."),
          ("Vou te ganhar dessa vez.", "Já ouvi isso antes. Mas eu gosto do otimismo."),
          ("Só se você me deixar no leme.", "No leme? Você sempre mira na boia. Tá bom, deixo.")]),
    ],
    "celeste": [
        ("Chegou uma bolsa de couro que é a sua cara. Não comprei pra você. Comprei pensando em você. É diferente.",
         [("Já estou indo na Boutique!", "Vou deixar ela na vitrine de cima. Só pra você ver primeiro."),
          ("Que diferença sutil.", "Moda é sutileza, querida. Mas a bolsa não é nada sutil."),
          ("Qual cor?", "Caramelo. Combina com quase tudo seu. Menos com pressa.")]),
        ("Vi você passando na rua com aquela roupa e quase saí correndo pra elogiar. Me controlei. Por pouco.",
         [("Pode elogiar sempre que quiser!", "Então: você estava impecável. Pronto, me sinto melhor."),
          ("Era a roupa que você me vendeu.", "Eu sei. Por isso fiquei tão orgulhosa."),
          ("Da próxima vez, sai correndo.", "Vou sair. Com fita métrica e tudo.")]),
        ("Desenhei três croquis hoje. Um deles tem um bolso secreto pra cartão de CEO.",
         [("Eu preciso desse bolso secreto!", "Vou fazer o primeiro sob medida. Passa pra tirar as medidas."),
          ("Me mostra os outros dois?", "Só pessoalmente. Croqui não se manda por mensagem."),
          ("Você é genial, Celeste.", "Diz isso mais alto. A vizinha da CatCo precisa ouvir.")]),
    ],
    "yang": [
        ("Plantão de 30 horas. Estou ótima. Não responda isso com preocupação.",
         [("Ok. Parabéns pelo plantão.", "Obrigada. Viu como é fácil? Ninguém precisa se preocupar."),
          ("Quer um café? Eu levo.", "Expresso duplo. Não, triplo. Sem conversa no corredor."),
          ("Dorme depois, tá?", "Isso foi preocupação. Eu falei. Mas tudo bem, vou dormir.")]),
        ("Operei um coração hoje que batia errado. Agora bate certo. Pode me chamar de incrível.",
         [("Incrível. A mais incrível.", "Finalmente alguém com bom senso nesta cidade."),
          ("Como foi a cirurgia?", "Seis horas, uma válvula nova e zero erros. Do jeito que eu gosto."),
          ("O paciente sabe a sorte que tem?", "Ele vai saber. Eu vou lembrar ele na consulta.")]),
        ("Você dormiu? Se não dormiu, eu vou saber. Eu sempre sei.",
         [("Dormi oito horas. Juro.", "Mentira, mas vou aceitar. Hoje."),
          ("Dormi pouco, confesso.", "Sabia. Hoje você deita antes da meia-noite. Ordem médica."),
          ("E você, dormiu?", "Não é sobre mim. Mas não. Próxima pergunta.")]),
    ],
    "meredith": [
        ("Dia longo. Daqueles em que você só quer uma cerveja e alguém que não pergunte nada.",
         [("Noonan's às 20h? Sem perguntas.", "Perfeito. Você é das boas."),
          ("Estou aqui se precisar. Sem perguntas.", "Obrigada. Às vezes é só disso que eu preciso."),
          ("Uma cerveja eu posso levar.", "Gelada e sem conversa. Combinado.")]),
        ("Uma paciente de 90 anos me disse que o segredo é dançar na cozinha. Estou considerando.",
         [("Considera! Dança mesmo.", "Já dancei hoje de manhã. Queimei a torrada. Valeu a pena."),
          ("Ela parece muito sábia.", "Ela me ensinou mais hoje que três anos de residência."),
          ("Eu danço junto, se quiser.", "Fechado. Mas eu escolho a música.")]),
        ("Se precisar de alguma coisa, você sabe onde me achar. No hospital. Sempre no hospital.",
         [("Obrigada, Meredith. Vale o mesmo.", "Eu sei. Por isso eu mandei."),
          ("Você precisa sair um pouco dali.", "Eu sei. Um dia. Talvez. Me arrasta pro Noonan's."),
          ("Vou levar um lanche pra você.", "Se tiver chocolate, eu aceito sem protestar.")]),
    ],
    "milany": [
        ("Lembrete da sua cardiologista favorita: escada em vez de elevador. Pelo menos às vezes.",
         [("Subi de escada hoje!", "Que orgulho. Seu coração mandou um obrigado."),
          ("Quarenta andares, Milany?", "Às vezes, eu disse. Começa pelos cinco primeiros."),
          ("Você é a minha favorita mesmo.", "Eu sei. Mas é bom ler isso por escrito.")]),
        ("O Conti Moretti ganhou um aparelho novo. Fiquei tão feliz que tirei foto com ele. Normal.",
         [("Muito normal. Manda a foto!", "Mandei. Estamos ótimos. Eu e o aparelho."),
          ("Que bom! Para que ele serve?", "Ecocardiograma em 3D. Dá pra ver o coração batendo em detalhe. Lindo."),
          ("A Fundação ajudou?", "Ajudou, sim. Obrigada, Letícia. De verdade.")]),
        ("Seu coração está ótimo, eu conferi. Mas cuida dele, tá? Ele trabalha muito.",
         [("Prometo cuidar dele.", "Promessa anotada no prontuário."),
          ("Ele trabalha mais do que eu?", "Bem mais. Ele não tira folga nem no fim de semana."),
          ("E o seu, quem cuida?", "Os meus pacientes. E os amigos. Você inclusive.")]),
    ],
    "izzie": [
        ("Fiz cupcakes pra ala de oncologia. Sobraram três. Agora sobrou um. Corre!",
         [("Estou correndo! Guarda pra mim!", "Guardei dentro do armário do vestiário. Ninguém mexe lá."),
          ("Quem comeu os outros dois?", "Eu. Os dois. Foi um dia difícil."),
          ("Que gesto bonito, Izzie.", "Eles sorriem quando veem o glacê. Vale cada fornada.")]),
        ("Uma paciente minha recebeu alta hoje. Chorei no corredor. De alegria, dessa vez.",
         [("Que notícia linda!", "Ela me deu um abraço tão apertado. Ainda estou sentindo."),
          ("Você merece esse dia bom.", "Obrigada. Eu precisava ouvir isso."),
          ("Vamos comemorar?", "Vamos! Eu levo os cupcakes, você leva o resto.")]),
        ("Sabe o que melhora qualquer dia? Glacê. Tenho provas científicas. Mais ou menos.",
         [("Concordo. Glacê de quê?", "Cream cheese. É científico. Mais científico que o de baunilha."),
          ("Me manda as provas.", "Te mando um cupcake. É a prova principal."),
          ("A Cristina concorda?", "Ela diz que não. Mas comeu dois.")]),
    ],
    "addison": [
        ("Três partos hoje, todos lindos. Estou exausta e flutuando.",
         [("Que dia lindo! Descansa um pouco.", "Vou dormir doze horas. Ou duas. Depende dos bebês."),
          ("Três vidas novas no mundo. Que demais.", "É o melhor trabalho do mundo. Não conta pra Cristina."),
          ("Quer um jantar pra comemorar?", "Quero. Com vinho. Depois de dormir.")]),
        ("Comprei sapatos novos. Não precisava. Foi a melhor decisão da semana.",
         [("A Celeste já sabe?", "Foi ela que me vendeu. Ela é perigosa."),
          ("Manda foto!", "Mandei. São vermelhos. Combinam com a minha falta de juízo."),
          ("Sapato novo sempre é necessário.", "Finalmente alguém que entende.")]),
        ("Se a Celeste te perguntar, eu NÃO experimentei o vestido vermelho da vitrine. Três vezes.",
         [("Meu silêncio é garantido.", "Você é uma ótima amiga. E uma péssima testemunha, espero."),
          ("Três vezes? Compra logo.", "Ok. Comprei. Agora você é cúmplice."),
          ("Ela já sabe, Addison.", "Claro que sabe. Ela sabe tudo. Vou me esconder.")]),
    ],
}
GENERIC = [
    ("Passei pela Luthor Corp hoje e lembrei de você. Bom dia!",
     [("Bom dia! Por que não entrou?", "Você parecia ocupada. Da próxima vez, eu entro."),
      ("Que fofo. Bom dia pra você também!", "Tenha um dia lindo!"),
      ("Passa lá amanhã pra um café.", "Combinado! Eu passo.")]),
    ("Que dia corrido! Me conta como foi o seu depois.",
     [("O meu também foi uma loucura.", "Então a gente merece um descanso. Logo."),
      ("Foi bom! Te conto pessoalmente.", "Combinado. Vou guardar as perguntas."),
      ("Respira fundo. Vai dar tudo certo.", "Obrigada. Precisava ouvir isso.")]),
    ("Vi uma coisa engraçada na rua e pensei: a Letícia ia rir. Te conto depois.",
     [("Agora estou curiosa! Conta!", "Pessoalmente é mais engraçado. Juro."),
      ("Já estou rindo sem saber o que é.", "Viu? Eu sabia."),
      ("Me conta no almoço?", "Fechado. Você paga, eu conto.")]),
]
MORNING = {
    "lucy": [
        ("Bom dia. Acordei pensando em você e no café do Harry. Nessa ordem? Não conta.",
         [("Bom dia. Eu também pensei em você.", "Então hoje vai ser um bom dia. Estou decidindo isso agora."),
          ("Qual veio primeiro, eu ou o café?", "Você. Mas o café ficou ofendido. Não conta pra ele."),
          ("Te encontro no Grão Nobre?", "Às 8h30. Eu pago. Não discute.")]),
        ("Bom dia, CEO. Hoje é dia de manchete boa, eu sinto.",
         [("Contanto que a manchete não seja sobre mim.", "Não prometo nada. Mas vou ser gentil."),
          ("Seu instinto nunca erra.", "Quase nunca. Errou uma vez. Com você, lá em Gotham."),
          ("Bom dia, repórter. Boa caçada.", "Obrigada. Volto com a história e com saudade.")]),
        ("Bom dia! Tenta não salvar o mundo antes do almoço, tá?",
         [("Só um pedacinho dele. Prometo.", "Um pedacinho pequeno. Depois almoça comigo."),
          ("Vou salvar só o seu dia.", "Já salvou. Era só isso que eu queria ler."),
          ("Você também. Nada de furo antes do café.", "Ok, ok. Mas se aparecer um furo, eu corro.")]),
    ],
    "vittoria": [
        ("Buongiorno, amore. O dia está lindo. Você também, imagino.",
         [("Buongiorno! Você imagina certo.", "Eu sei. Eu sempre imagino certo."),
          ("Lindo mesmo é o seu bom-dia.", "Ah, Letícia. Assim eu chego atrasada na reunião."),
          ("Café da manhã juntas amanhã?", "Sim! Eu levo o pão, você leva a pressa.")]),
        ("Bom dia! Hoje o cardápio tem uma surpresa pra você. Não pergunta.",
         [("Não vou perguntar. Mas tem chocolate?", "Não pergunta, eu disse! ...Tem."),
          ("Eu adoro surpresas suas.", "Então essa você vai adorar. Às 20h."),
          ("Você sabe que eu vou adivinhar.", "Tenta. Ninguém adivinha a Dona Graça.")]),
        ("Buongiorno! Já tomou café? Se não tomou, eu fico brava. Bravinha.",
         [("Já tomei! Cappuccino do Harry.", "Brava! Em italiano isso é elogio. Hoje eu não fico brava."),
          ("Ainda não... não fica brava.", "Já estou bravinha. Corre tomar."),
          ("Você bravinha deve ser linda.", "Para. Agora eu fiquei vermelha e brava ao mesmo tempo.")]),
    ],
}


def _all_entries():
    for lst in MSGS.values():
        yield from lst
    yield from GENERIC
    for lst in MORNING.values():
        yield from lst


REPLIES_FOR = {text: replies for text, replies in _all_entries()}
DEFAULT_REPLIES = [("Que bom! Me conta mais depois.", "Pode deixar. Eu conto tudo."),
                   ("Haha, adorei!", "Sabia que você ia gostar."),
                   ("Obrigada por lembrar de mim.", "Sempre.")]


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.phone = dict(msgs=[], seq=0, today=0, stocks=[])


def save_state(g):
    return {"phone": g.phone}


def load_state(g, d):
    init_state(g)
    p = d.get("phone") or {}
    g.phone["msgs"] = [m for m in p.get("msgs", []) if isinstance(m, dict) and m.get("npc") in NPCS][-MAX_MSGS:]
    g.phone["seq"] = int(p.get("seq", len(g.phone["msgs"])))
    g.phone["today"] = int(p.get("today", 0))
    g.phone["stocks"] = [float(x) for x in p.get("stocks", [])][-STOCK_DAYS:]
    if not g.phone["stocks"]:
        g.phone["stocks"] = [float(getattr(g, "stock_prev", 100.0)), float(getattr(g, "stock", 100.0))]


def replies_for(m):
    """As 3 respostas (resposta, volta) que combinam com a mensagem."""
    return REPLIES_FOR.get(m.get("text", ""), DEFAULT_REPLIES)


def unread(g):
    return sum(1 for m in g.phone["msgs"] if not m.get("read"))


def _send(g, key, text, toast=True):
    g.phone["seq"] += 1
    g.phone["msgs"].append(dict(id=g.phone["seq"], npc=key, text=text, day=g.abs_day(), time=g.minutes,
                                read=False, replied=False))
    g.phone["msgs"] = g.phone["msgs"][-MAX_MSGS:]
    g.phone["today"] += 1
    if toast:
        audio.sfx("blip")
        g.toasts.push(f"Mensagem de {NPCS[key]['short']} (T para ler)", C_PINK if key in ROMANCES else C_LILAC)


def _fresh_text(g, key):
    """Uma mensagem que essa personagem ainda não mandou (ou a menos recente)."""
    pool = [t for t, _ in (MSGS.get(key) or GENERIC)]
    sent = [m["text"] for m in g.phone["msgs"] if m["npc"] == key]
    left = [t for t in pool if t not in sent]
    return random.choice(left or pool)


def _random_friend(g):
    keys = [k for k in NPC_ORDER if g.hearts(k) >= 2 and k != g.partner]
    today = {m["npc"] for m in g.phone["msgs"] if m["day"] == g.abs_day()}
    keys = [k for k in keys if k not in today]
    return random.choice(keys) if keys else None


def morning(g):
    g.phone["today"] = 0
    if g.dating and g.dating != g.partner and g.dating in MORNING:
        _send(g, g.dating, random.choice(MORNING[g.dating])[0], toast=False)
    k = _random_friend(g)
    if k and random.random() < 0.6:
        _send(g, k, _fresh_text(g, k), toast=False)
    if unread(g):
        g.toasts.push(f"Você tem {unread(g)} mensagem(ns) nova(s) no celular (T).", C_LILAC)


def tick(g):
    """A cada 10 minutos do jogo: de vez em quando chega uma mensagem (9h às 21h)."""
    if not (9 * 60 <= g.minutes <= 21 * 60) or g.phone["today"] >= MAX_PER_DAY or g.modals:
        return
    if random.random() < 0.035:
        k = _random_friend(g)
        if k:
            _send(g, k, _fresh_text(g, k))


def night(g, notes):
    g.phone["stocks"] = (g.phone["stocks"] + [round(float(g.stock), 2)])[-STOCK_DAYS:]


# ---------------------------------------------------------------------------
# Agenda
# ---------------------------------------------------------------------------
def agenda(g):
    """[(título, [(texto, cor)])] de hoje e dos próximos 7 dias."""
    from . import casamento, casal, fundacao, historia
    out = []
    today = []
    if g.date and not g.date.get("done"):
        today.append((f"Encontro às 20h com {NPCS[g.date['npc']]['short']}: {g.date['desc']}", C_PINK))
    for txt, col in (festas.hud_lines(g) + casamento.hud_lines(g) + casal.hud_lines(g) + fundacao.hud_lines(g)
                     + historia.hud_lines(g) + pedidos.hud_lines(g)
                     + lugares.hud_lines(g)):
        today.append((txt, col))
    for key, h, ev in [e for e in g.pending_scene_events() if e[1] > 0]:
        where, a, b = g.scene_place(ev["scene"])
        today.append((f"Evento de {NPCS[key]['short']}: {where} ({g.fmt_hour(a)} a {g.fmt_hour(b)})", C_PINK))
    if g.request:
        r = g.request
        left = r["deadline"] - g.abs_day()
        today.append((f"E-mail de {NPCS[r['npc']]['short']}: {r['qty']}x {ITEMS[r['item']]['name']} "
                      f"({'vence hoje' if left <= 0 else f'{left} dia(s)'})", C_GOLD))
    out.append(("Hoje", today or [("Nada marcado. Dia livre!", C_MUTED)]))
    base = g.abs_day()
    for i in range(1, 8):
        y, q, d = g.date_from_abs(base + i)
        items = []
        f = festas.festival_on(q, d)
        if f:
            items.append((f"{f['name']} {f['place']}, {g.fmt_hour(f['start'])} às {g.fmt_hour(f['end'])}", C_GOLD))
        for k in festas.birthday_keys(q, d):
            items.append((f"Aniversário de {NPCS[k]['short']}", C_PINK))
        wq = g.casamento.get("wedding_qd") if hasattr(g, "casamento") else None
        if wq and list(wq) == [y, q, d]:
            items.append(("O casamento! Jardim do Mirante, 15h", C_PINK))
        if items:
            label = "Amanhã" if i == 1 else g.date_label(d, q, y, short=True)
            out.append((label, items))
    return out


# ---------------------------------------------------------------------------
# O aparelho
# ---------------------------------------------------------------------------
APPS = [("msgs", "Mensagens", (120, 200, 120)), ("agenda", "Agenda", (240, 120, 120)),
        ("tempo", "Tempo", (110, 180, 250)), ("bolsa", "Bolsa", (240, 200, 90)),
        ("fotos", "Fotos", (230, 140, 220)), ("pedidos", "Pedidos", (220, 160, 100)),
        ("habil", "Habilidades", (170, 130, 255)), ("mapa", "Mapa", (120, 210, 200))]
PHONE = pygame.Rect(0, 0, 400, 660)
PHONE.center = (SCREEN_W // 2, SCREEN_H // 2)
SCREEN = PHONE.inflate(-36, -100)
SCREEN.y = PHONE.y + 44


def _app_icon(surf, kind, r, color):
    ui.cut_rect(surf, tuple(max(0, c - 70) for c in color), r.move(0, 3), 3)
    ui.cut_rect(surf, color, r, 3)
    k = r.w // 16
    x, y = r.x, r.y
    W = (250, 250, 255)
    D = tuple(max(0, c - 110) for c in color)

    def R(px, py, w, h, col=W):
        pygame.draw.rect(surf, col, (x + px * k, y + py * k, w * k, h * k))
    if kind == "msgs":
        R(3, 4, 10, 7); R(5, 11, 2, 2); R(5, 6, 6, 1, D); R(5, 8, 4, 1, D)
    elif kind == "agenda":
        R(3, 4, 10, 9); R(3, 4, 10, 2, (200, 40, 60)); R(5, 3, 1, 2, D); R(10, 3, 1, 2, D)
        for i in range(3):
            for j in range(2):
                R(5 + i * 2, 8 + j * 2, 1, 1, D)
    elif kind == "tempo":
        R(4, 4, 5, 5, (255, 220, 90)); R(6, 8, 7, 4); R(5, 9, 2, 3); R(13, 9, 1, 2)
    elif kind == "bolsa":
        R(3, 12, 10, 1, D); R(4, 9, 2, 3); R(7, 7, 2, 5); R(10, 4, 2, 8)
    elif kind == "fotos":
        R(3, 5, 10, 8); R(6, 4, 4, 1); R(6, 7, 4, 4, D); R(7, 8, 2, 2)
    elif kind == "pedidos":
        R(4, 3, 8, 10); R(5, 5, 6, 1, D); R(5, 7, 6, 1, D); R(5, 9, 4, 1, D); R(7, 2, 2, 2, (200, 40, 60))
    elif kind == "habil":
        R(7, 3, 2, 2); R(5, 5, 6, 2); R(3, 7, 10, 2); R(5, 9, 6, 2); R(4, 11, 3, 2); R(9, 11, 3, 2)
    else:
        R(3, 4, 3, 9); R(6, 3, 4, 9, (230, 240, 230)); R(10, 4, 3, 9); R(7, 6, 2, 2, (220, 60, 80))


class Phone(ui.Modal):
    def __init__(self, g):
        self.g = g
        self.app = None
        self.sel = 0
        self.list_sel = 0
        self.top = 0
        self.reading = None
        self.t = 0.0
        self.msg, self.msg_t = "", 0.0

    # --- navegação --------------------------------------------------------
    def handle(self, ev):
        if ev.type == pygame.MOUSEWHEEL and self.app:
            self.move(-ev.y)
            return
        if ev.type != pygame.KEYDOWN:
            return
        back = ev.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE)
        if self.app is None:
            if back or ev.key == pygame.K_t:
                audio.sfx("cancel")
                self.done = True
            elif ev.key in (pygame.K_LEFT, pygame.K_a):
                self.sel = (self.sel - 1) % len(APPS); audio.sfx("move")
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.sel = (self.sel + 1) % len(APPS); audio.sfx("move")
            elif ev.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 3) % len(APPS); audio.sfx("move")
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 3) % len(APPS); audio.sfx("move")
            elif ev.key in ui.CONFIRM:
                self.open(APPS[self.sel][0])
            return
        if ev.key == pygame.K_t:
            audio.sfx("cancel")
            self.done = True
        elif back:
            audio.sfx("cancel")
            if self.reading is not None:
                self.reading = None
            else:
                self.app = None
        elif ev.key in (pygame.K_UP, pygame.K_w):
            self.move(-1)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.move(1)
        elif ev.key in (pygame.K_LEFT, pygame.K_a) and self.app == "fotos":
            self.move(-1)
        elif ev.key in (pygame.K_RIGHT, pygame.K_d) and self.app == "fotos":
            self.move(1)
        elif ev.key in ui.CONFIRM:
            self.confirm()

    def say(self, msg):
        self.msg, self.msg_t = msg, 2.6

    def open(self, app):
        audio.sfx("open")
        if app == "mapa":
            from .citymap import CityMap
            self.g.push(CityMap(self.g))
            return
        self.app, self.list_sel, self.top, self.reading = app, 0, 0, None
        if app == "msgs" and self.g.phone["msgs"]:
            self.list_sel = 0

    def rows(self):
        g = self.g
        if self.app == "msgs":
            return list(reversed(g.phone["msgs"]))
        if self.app == "fotos":
            return mural.photos(g)[::-1]
        if self.app == "agenda":
            out = []
            for title, items in agenda(g):
                out.append(("title", title, C_GOLD))
                out += [("item", t, c) for t, c in items]
            return out
        return []

    def move(self, d):
        n = len(self.rows())
        if self.reading is not None or n == 0:
            if self.app in ("agenda",):
                pass
            return
        self.list_sel = (self.list_sel + d) % n
        audio.sfx("move")

    def confirm(self):
        g = self.g
        if self.app == "msgs":
            rows = self.rows()
            if not rows:
                return
            if self.reading is None:
                m = rows[min(self.list_sel, len(rows) - 1)]
                m["read"] = True
                self.reading = m
                audio.sfx("page")
                return
            m = self.reading
            if m.get("replied"):
                self.say("Você já respondeu essa mensagem.")
                audio.sfx("blip")
                return

            options = replies_for(m)

            def pick(i, m=m, options=options):
                m["replied"] = True
                m["reply"], m["back"] = options[i]
                g.add_friendship(m["npc"], REPLY_POINTS)
                habilidades.gain(g, "carisma", 3)
                audio.sfx("love" if m["npc"] in ROMANCES else "confirm")
                self.say(f"Você respondeu {NPCS[m['npc']]['short']}. (+amizade)")
            g.push(ui.Choice(f"Responder {NPCS[m['npc']]['short']}:", [o[0] for o in options], pick))
        elif self.app == "fotos":
            rows = self.rows()
            if rows:
                pid = rows[min(self.list_sel, len(rows) - 1)][0]
                audio.sfx("confirm")
                self.say(mural.toggle(g, pid))
        elif self.app == "bolsa":
            if "book_stocks" in g.flags:
                g.open_stocks()
            else:
                audio.sfx("blip")
                self.say("Para negociar ações, leia o livro de investimentos (Bayside Books).")
        elif self.app == "pedidos":
            self.say("Entregue conversando com quem pediu.")

    def update(self, dt):
        self.t += dt
        self.msg_t = max(0.0, self.msg_t - dt)

    # --- desenho ----------------------------------------------------------
    def draw(self, surf):
        g = self.g
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((8, 4, 16, 120))
        surf.blit(veil, (0, 0))
        # corpo do aparelho
        ui.cut_rect(surf, (20, 14, 30), PHONE.move(4, 6), 4)
        ui.cut_rect(surf, (48, 34, 70), PHONE, 4)
        ui.cut_rect(surf, (90, 64, 128), PHONE.inflate(-6, -6), 3)
        ui.cut_rect(surf, (36, 26, 54), PHONE.inflate(-12, -12), 3)
        pygame.draw.rect(surf, (18, 12, 26), (PHONE.centerx - 30, PHONE.y + 18, 60, 6))       # alto-falante
        pygame.draw.rect(surf, (90, 64, 128), (PHONE.centerx - 34, PHONE.bottom - 40, 68, 8))  # botão
        ui.cut_rect(surf, (14, 10, 24), SCREEN.inflate(4, 4), 2)
        pygame.draw.rect(surf, (28, 20, 44), SCREEN)
        # barra de status
        ui.text(surf, g.fmt_hour(g.minutes), (SCREEN.x + 10, SCREEN.y + 4), 16, C_TEXT, bold=True)
        ui.text(surf, "LuthorNet", (SCREEN.centerx, SCREEN.y + 4), 14, C_LILAC, center=True)
        bat = pygame.Rect(SCREEN.right - 34, SCREEN.y + 8, 22, 10)
        pygame.draw.rect(surf, C_MUTED, bat, 2)
        frac = g.energy / max(1, g.max_energy)
        pygame.draw.rect(surf, C_GREEN if frac > 0.3 else C_RED, (bat.x + 3, bat.y + 3, int(16 * frac), 4))
        pygame.draw.rect(surf, C_MUTED, (bat.right, bat.y + 3, 2, 4))
        body = pygame.Rect(SCREEN.x + 10, SCREEN.y + 30, SCREEN.w - 20, SCREEN.h - 40)
        if self.app is None:
            self.draw_home(surf, body)
        else:
            title = dict((a, n) for a, n, _ in APPS)[self.app]
            ui.text(surf, title, (body.x, body.y), 24, C_GOLD, bold=True)
            ui.text(surf, "Esc: voltar", (body.right, body.y + 8), 13, C_MUTED, right=True)
            inner = pygame.Rect(body.x, body.y + 38, body.w, body.h - 38)
            getattr(self, "draw_" + self.app)(surf, inner)
        if self.msg_t > 0:
            r = pygame.Rect(SCREEN.x + 8, SCREEN.bottom - 70, SCREEN.w - 16, 60)
            ui.box(surf, r, (50, 36, 74), border=C_LILAC)
            for i, ln in enumerate(ui.wrap(self.msg, 15, r.w - 20)[:3]):
                ui.text(surf, ln, (r.centerx, r.y + 6 + i * 17), 15, C_TEXT, center=True)

    def draw_home(self, surf, body):
        g = self.g
        y, q = g.year, g.quarter
        ui.text(surf, g.date_label(short=True), (body.centerx, body.y + 6), 18, C_TEXT, bold=True, center=True)
        ui.text(surf, "Bom dia, Letícia" if g.minutes < 12 * 60 else
                ("Boa tarde, Letícia" if g.minutes < 18 * 60 else "Boa noite, Letícia"),
                (body.centerx, body.y + 30), 15, C_LILAC, center=True)
        size, gap = 72, 22
        x0 = body.centerx - (3 * size + 2 * gap) // 2
        for i, (key, name, color) in enumerate(APPS):
            col, row = i % 3, i // 3
            r = pygame.Rect(x0 + col * (size + gap), body.y + 74 + row * (size + 40), size, size)
            if i == self.sel:
                ui.cut_rect(surf, (255, 236, 170), r.inflate(8, 8), 3)
            _app_icon(surf, key, r, color)
            ui.text(surf, name, (r.centerx, r.bottom + 6), 14, C_TEXT if i == self.sel else C_MUTED,
                    bold=i == self.sel, center=True)
            badge = unread(g) if key == "msgs" else (len(g.pedidos["active"]) if key == "pedidos" else 0)
            if badge:
                b = pygame.Rect(r.right - 16, r.y - 6, 22, 20)
                ui.cut_rect(surf, (220, 50, 70), b, 2)
                ui.text(surf, str(badge), (b.centerx, b.y + 1), 15, (255, 255, 255), bold=True, center=True,
                        shadow=False)
        ui.text(surf, "Setas: escolher   E: abrir   T: guardar", (body.centerx, body.bottom - 20), 13, C_MUTED,
                center=True)

    def _list_window(self, n, visible):
        if self.list_sel < self.top:
            self.top = self.list_sel
        elif self.list_sel >= self.top + visible:
            self.top = self.list_sel - visible + 1
        self.top = max(0, min(self.top, max(0, n - visible)))
        return range(self.top, min(n, self.top + visible))

    def draw_msgs(self, surf, r):
        g = self.g
        rows = self.rows()
        if self.reading is not None:
            m = self.reading
            npc = g.npcs[m["npc"]]
            p = g.portrait_for(npc, size=64)
            ui.blit_portrait(surf, p, (r.x, r.y))
            ui.text(surf, NPCS[m["npc"]]["name"], (r.x + 74, r.y + 6), 18, C_TEXT, bold=True)
            ui.text(surf, self._when(m), (r.x + 74, r.y + 30), 13, C_MUTED)
            bubble = pygame.Rect(r.x, r.y + 80, r.w - 30, 10)
            lines = ui.wrap(m["text"], 17, bubble.w - 24)
            bubble.h = 20 + 21 * len(lines)
            ui.box(surf, bubble, (62, 46, 92))
            for i, ln in enumerate(lines):
                ui.text(surf, ln, (bubble.x + 12, bubble.y + 10 + i * 21), 17, C_TEXT)
            yy = bubble.bottom + 14
            if m.get("replied") and m.get("reply"):
                # a resposta da Letícia (à direita, verde) e a volta de quem mandou (à esquerda)
                for txt, mine in ((m["reply"], True), (m.get("back", ""), False)):
                    if not txt:
                        continue
                    lines = ui.wrap(txt, 16, r.w - 70)
                    bw = min(r.w - 30, max(ui.font(16).size(ln)[0] for ln in lines) + 26)
                    bb = pygame.Rect(r.right - bw if mine else r.x, yy, bw, 18 + 20 * len(lines))
                    ui.box(surf, bb, (52, 104, 76) if mine else (62, 46, 92))
                    for i, ln in enumerate(lines):
                        ui.text(surf, ln, (bb.x + 12, bb.y + 9 + i * 20), 16, C_TEXT)
                    yy = bb.bottom + 10
            elif m.get("replied"):
                rb = pygame.Rect(r.right - 150, yy, 150, 32)
                ui.box(surf, rb, (60, 110, 80))
                ui.text(surf, "Respondida", (rb.centerx, rb.y + 7), 15, C_TEXT, center=True)
            else:
                ui.text(surf, "E: responder (+amizade)", (r.right, yy + 6), 15, C_GREEN, right=True)
            return
        if not rows:
            ui.text(surf, "Nenhuma mensagem ainda.", (r.centerx, r.y + 40), 16, C_MUTED, center=True)
            ui.text(surf, "Amigas com 2 corações mandam mensagens.", (r.centerx, r.y + 64), 13, C_MUTED, center=True)
            return
        self.list_sel = min(self.list_sel, len(rows) - 1)
        h = 70
        for k, i in enumerate(self._list_window(len(rows), (r.h - 20) // h)):
            m = rows[i]
            row = pygame.Rect(r.x, r.y + k * h, r.w, h - 6)
            if i == self.list_sel:
                ui.box(surf, row, ui.C_PANEL_2, border=ui.C_ACCENT_2)
            npc = g.npcs[m["npc"]]
            ui.blit_portrait(surf, g.portrait_for(npc, size=48), (row.x + 6, row.y + 8))
            ui.text(surf, NPCS[m["npc"]]["short"], (row.x + 62, row.y + 6), 16,
                    C_PINK if m["npc"] in ROMANCES else C_TEXT, bold=not m.get("read"))
            ui.text(surf, self._when(m), (row.right - 8, row.y + 8), 12, C_MUTED, right=True)
            prev = m["text"] if len(m["text"]) < 34 else m["text"][:33].rstrip() + "..."
            ui.text(surf, prev, (row.x + 62, row.y + 30), 13, C_TEXT if not m.get("read") else C_MUTED)
            if not m.get("read"):
                pygame.draw.rect(surf, (90, 200, 120), (row.right - 16, row.y + 34, 8, 8))

    def _when(self, m):
        g = self.g
        d = g.abs_day() - m["day"]
        h = g.fmt_hour(m.get("time", 360))
        return f"hoje, {h}" if d == 0 else ("ontem" if d == 1 else f"há {d} dias")

    def draw_agenda(self, surf, r):
        rows = self.rows()
        y = r.y
        self.list_sel = min(self.list_sel, max(0, len(rows) - 1))
        start = self.list_sel
        for kind, txt, col in rows[start:]:
            if kind == "title":
                if y + 26 > r.bottom:
                    break
                ui.text(surf, txt, (r.x, y), 18, col, bold=True)
                y += 26
            else:
                lines = ui.wrap(txt, 15, r.w - 16)
                if y + 18 * len(lines) > r.bottom:
                    break
                pygame.draw.rect(surf, col, (r.x + 2, y + 6, 6, 6))
                for ln in lines:
                    ui.text(surf, ln, (r.x + 14, y), 15, C_TEXT)
                    y += 18
                y += 6
        if self.list_sel > 0:
            ui.text(surf, "mais acima", (r.right, r.y - 22), 12, C_MUTED, right=True)

    def draw_tempo(self, surf, r):
        g = self.g
        season = seasons.of_quarter(g.quarter)
        snow = season == "winter"

        def kind(w, storm, rainbow=False):
            if w == "chuva":
                return "snow" if snow else ("storm" if storm else "rain")
            return "rainbow" if rainbow else "sun"
        names = {"sun": "Sol", "rain": "Chuva", "storm": "Tempestade", "snow": "Neve", "rainbow": "Arco-íris"}
        for i, (title, k) in enumerate((("Hoje", kind(g.weather, g.storm, g.rainbow)),
                                        ("Amanhã", kind(g.weather_tomorrow, g.storm_tomorrow)))):
            box = pygame.Rect(r.x, r.y + i * 140, r.w, 128)
            ui.box(surf, box, (40, 30, 62))
            ui.text(surf, title, (box.x + 14, box.y + 10), 20, C_GOLD, bold=True)
            ui.draw_weather_icon(surf, (box.x + 60, box.y + 76), k, False, pygame.time.get_ticks())
            ui.text(surf, names[k], (box.x + 120, box.y + 56), 22, C_TEXT, bold=True)
            tip = {"rain": "Peixes de chuva aparecem no lago.", "storm": "Raios e trovões. Melhor ficar perto de casa.",
                   "snow": "Neve na cidade. Agasalhe-se!", "sun": "Bom dia para pescar e passear.",
                   "rainbow": "Arco-íris pela manhã!"}[k]
            for j, ln in enumerate(ui.wrap(tip, 14, box.w - 140)[:2]):
                ui.text(surf, ln, (box.x + 120, box.y + 84 + j * 17), 14, C_MUTED)
        left = DAYS_PER_QUARTER - g.day
        nxt = seasons.NAMES[seasons.SEASONS[(seasons.SEASONS.index(season) + 1) % 4]]
        ui.text(surf, f"{seasons.NAMES[season]}, dia {g.day} de {DAYS_PER_QUARTER}", (r.x, r.y + 290), 17, C_TEXT,
                bold=True)
        ui.text(surf, ("Amanhã começa: " + nxt) if left == 1 else
                (f"Último dia da estação!" if left == 0 else f"Faltam {left} dias para: {nxt}"),
                (r.x, r.y + 314), 15, C_LILAC)

    def draw_bolsa(self, surf, r):
        g = self.g
        hist = list(g.phone["stocks"])
        if not hist or abs(hist[-1] - g.stock) > 0.001:
            hist = (hist + [g.stock])[-STOCK_DAYS:]
        trend = g.stock - g.stock_prev
        ui.text(surf, "LCORP", (r.x, r.y), 18, C_MUTED, bold=True)
        ui.text(surf, f"$ {g.stock:.2f}".replace(".", ","), (r.x, r.y + 20), 32, C_TEXT, bold=True)
        ui.text(surf, f"{'+' if trend >= 0 else ''}{trend:.2f} ontem".replace(".", ","), (r.right, r.y + 34), 16,
                C_GREEN if trend >= 0 else C_RED, bold=True, right=True)
        chart = pygame.Rect(r.x, r.y + 70, r.w, 210)
        ui.slot(surf, chart, fill=(18, 12, 28))
        real_lo, real_hi = min(hist), max(hist)
        lo, hi = real_lo, real_hi
        if hi - lo < 1:                             # pouca variação: margem para a linha não ficar colada
            lo, hi = lo - 1, hi + 1
        for k in range(1, 4):
            yy = chart.y + k * chart.h // 4
            pygame.draw.line(surf, (40, 30, 56), (chart.x + 4, yy), (chart.right - 4, yy))
        pts = []
        n = len(hist)
        for i, v in enumerate(hist):
            x = chart.x + 10 + (chart.w - 20) * (i / max(1, n - 1))
            y = chart.bottom - 12 - (chart.h - 24) * ((v - lo) / (hi - lo))
            pts.append((int(x), int(y)))
        col = C_GREEN if hist[-1] >= hist[0] else C_RED
        if len(pts) > 1:
            pygame.draw.lines(surf, col, False, pts, 3)
        for p in pts[-1:]:
            pygame.draw.rect(surf, (255, 255, 255), (p[0] - 3, p[1] - 3, 6, 6))
        ui.text(surf, f"últimos {n} dias  ·  máx. {real_hi:.2f}  ·  mín. {real_lo:.2f}".replace(".", ","),
                (chart.centerx, chart.bottom + 6), 13, C_MUTED, center=True)
        val = int(g.stock * g.shares)
        ui.text(surf, f"Suas ações: {g.shares}", (r.x, chart.bottom + 34), 17, C_TEXT, bold=True)
        ui.text(surf, f"valem $ {val:,}".replace(",", "."), (r.right, chart.bottom + 34), 17, C_GOLD, bold=True,
                right=True)
        ui.text(surf, "E: comprar ou vender" if "book_stocks" in g.flags else "Negociar: leia o livro de investimentos",
                (r.centerx, chart.bottom + 66), 14, C_LILAC, center=True)

    def draw_fotos(self, surf, r):
        g = self.g
        rows = self.rows()
        if not rows:
            for i, ln in enumerate(("Nenhuma foto ainda.", "Tire fotos no modo foto (P)",
                                    "ou ganhe o álbum do Barry.")):
                ui.text(surf, ln, (r.centerx, r.y + 30 + i * 22), 15, C_MUTED, center=True)
            return
        self.list_sel = min(self.list_sel, len(rows) - 1)
        shown = set(mural.shown(g))
        tw, th = (r.w - 12) // 2, 96
        visible_rows = (r.h - 30) // (th + 28)
        first_row = self.list_sel // 2
        if first_row < self.top:
            self.top = first_row
        elif first_row >= self.top + visible_rows:
            self.top = first_row - visible_rows + 1
        for i in range(self.top * 2, min(len(rows), (self.top + visible_rows) * 2)):
            pid, title, img = rows[i]
            col, row = i % 2, i // 2 - self.top
            cell = pygame.Rect(r.x + col * (tw + 12), r.y + row * (th + 28), tw, th)
            if i == self.list_sel:
                ui.cut_rect(surf, (255, 236, 170), cell.inflate(8, 8), 2)
            surf.blit(pygame.transform.smoothscale(img, cell.size), cell.topleft)
            if pid in shown:
                pin = pygame.Rect(cell.right - 22, cell.y + 4, 18, 18)
                ui.cut_rect(surf, (220, 60, 80), pin, 2)
                pygame.draw.rect(surf, (255, 240, 240), (pin.x + 6, pin.y + 6, 6, 6))
            t = title if len(title) < 22 else title[:21] + "..."
            ui.text(surf, t, (cell.centerx, cell.bottom + 4), 12, C_TEXT if i == self.list_sel else C_MUTED,
                    center=True)
        hint = "E: pôr/tirar do mural" + ("" if g.mural else " (agora: as 4 mais novas)")
        ui.text(surf, hint, (r.centerx, r.bottom - 18), 13, C_LILAC, center=True)

    def draw_pedidos(self, surf, r):
        g = self.g
        y = r.y
        items = []
        for p in g.pedidos["active"]:
            have = min(g.count_item(p["item"]), p["qty"])
            left = pedidos.days_left(g, p)
            items.append((f"Quadro: {NPCS[p['npc']]['short']}", f"{pedidos.label(p)}  ·  tem {have}/{p['qty']}  ·  "
                          f"{'vence hoje' if left <= 0 else f'{left} dia(s)'}  ·  ${p['reward']}",
                          C_GREEN if have >= p["qty"] else C_GOLD))
        if g.request:
            q = g.request
            have = min(g.count_item(q["item"]), q["qty"])
            items.append((f"E-mail: {NPCS[q['npc']]['short']}", f"{q['qty']}x {ITEMS[q['item']]['name']}  ·  tem "
                          f"{have}/{q['qty']}  ·  ${q['reward']}", C_GREEN if have >= q["qty"] else C_GOLD))
        mo = g.marina.get("order") if hasattr(g, "marina") else None
        if mo:
            from . import marina
            items.append(("Marina Luthor", marina.order_text(g), (120, 190, 240)))
        if not items:
            ui.text(surf, "Nenhum pedido aceito.", (r.centerx, r.y + 30), 16, C_MUTED, center=True)
        for title, body, col in items:
            box = pygame.Rect(r.x, y, r.w, 76)
            ui.box(surf, box, (40, 30, 62))
            ui.text(surf, title, (box.x + 12, box.y + 8), 17, col, bold=True)
            for j, ln in enumerate(ui.wrap(body, 14, box.w - 24)[:2]):
                ui.text(surf, ln, (box.x + 12, box.y + 32 + j * 18), 14, C_TEXT)
            y += 84
        n = len(g.pedidos["offers"])
        ui.text(surf, f"Bilhetes no quadro do Grão Nobre: {n}", (r.centerx, r.bottom - 40), 14, C_LILAC, center=True)
        ui.text(surf, f"Pedidos do quadro entregues: {g.pedidos['done']}", (r.centerx, r.bottom - 20), 13, C_MUTED,
                center=True)

    def draw_habil(self, surf, r):
        habilidades.draw_panel(surf, self.g, r)


def open_phone(g):
    audio.sfx("open")
    g.push(Phone(g))
