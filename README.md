# Luthor Life

Um jogo de simulação de vida no estilo Stardew Valley / Coral Island, no universo da Luthor Corp.
Você é **Letícia Luthor**, CEO da Luthor Corporation, em National City.

Comande o laboratório, feche contratos, pesque no píer, cozinhe na cobertura, jogue fliperama no
Noonan's, faça amizades e, quem sabe, encontre o amor: **Lucy Williams** (repórter da CatCo) ou
**Vittoria Ricci** (chef da Ricci Trattoria).

## Como jogar

**Windows:** dê dois cliques em `Jogar.bat` (na primeira vez ele instala o pygame).

**Manual:**
```
pip install pygame-ce
python main.py
```
Precisa de Python 3.9+ (recomendado 3.13). Se o `pygame-ce` der problema, `pip install pygame` também funciona.

## Controles

| Tecla | Ação |
|---|---|
| WASD / setas | Andar (Shift = andar devagar) |
| E / Espaço / clique | Interagir, conversar, trabalhar, pescar |
| 1–9, 0, -, = / roda do mouse | Escolher item da barra |
| I / Tab | Mochila (24 espaços, organizar e jogar fora) |
| F / botão direito | Comer, beber ou ler o item escolhido |
| Esc | Menu: mochila, objetivos, relacionamentos, coleções, opções |
| F11 | Tela cheia |
| Setas ou D F J K | Karaokê (no Noonan's) |

## National City

- **Cobertura:** a porta de vidro no alto da sala leva ao **terraço**, com horta, espreguiçadeiras e telescópio.
- **Centro:** Residencial Luthor (sua cobertura), Luthor Corp, Café Grão Nobre, CatCo Worldwide Media,
  banco e o **Conti Moretti Hospitais**.
- **Parque central:** chafariz, bancos e um **lago para pescar** peixes de água doce.
- **Calçadão Bayside:** Bayside Books, Mercado Central, Ricci Trattoria, Noonan's, **Cine National**
  (agora dá para entrar) e o **Abrigo Patinhas**, a barraquinha de adoção.
- **Orla:** praia, guarda-sóis, a barraca do Joca e o **píer** para pescar no mar.
- Carros nas avenidas, pôr do sol, noite com postes acesos, chuva e rotinas de fim de semana.

## O que fazer

- **Laboratório** (Luthor Corp): compre propostas no Terminal P&D, inicie projetos nas bancadas, trabalhe
  todo dia e venda os produtos na Mesa de Contratos.
- **Pesca:** o Seu Joca dá uma vara na primeira conversa no píer. Fique de frente para a água, aperte E,
  espere o "!" e aperte E. No minigame, segure Espaço para manter o peixe dentro da barra verde.
  São 13 espécies (mar e lago), que variam com o trimestre, o horário e a chuva. Tem uma lendária...
- **Cozinhar:** compre ingredientes no Mercado Central e use o fogão da cobertura. Pratos dão muita
  energia, valem bem e são ótimos presentes.
- **Aquário:** coloque um peixe de cada espécie no aquário da sala.
- **Fliperama Meteoro** (Noonan's): $10 por partida, cada moeda vale $3.
- **Livros** (Bayside Books): bônus permanentes. Leia com F.
- **Investimentos:** com o livro "Mercados & Ações", compre e venda ações LCORP pelo computador.
- **Pedidos:** a equipe e os moradores pedem itens por e-mail, com recompensa.
- **Horta no terraço:** compre sementes no Mercado Central (manjericão, tomate, morango, girassol, roseira
  e abóbora), plante nos canteiros e regue todo dia (ou use o regador para regar tudo). A chuva rega
  sozinha. Tomate, morango e roseira produzem de novo depois da colheita. Há receitas novas com o que você planta.
- **Coletáveis:** todo dia aparecem conchas, vidro do mar, estrelas-do-mar e corais na praia, e flores,
  amoras, cogumelos e trevos de 4 folhas no parque. É só passar por cima. Dá para vender ou presentear.
- **Bichinho:** adote um gato ou um cachorro no Abrigo Patinhas (9h às 18h, doação de $100), escolha a cor
  e o nome. Faça carinho todo dia (+energia), dê petiscos, e às vezes ele deixa presentes perto da cama.
- **Karaokê** (Noonan's, das 18h às 2h): use a jukebox. Aperte as setas no ritmo, ganhe gorjetas e
  impressione quem estiver no bar.
- **Cinema:** compre o ingresso na bilheteria (12h à meia-noite). São seis filmes que se revezam.
  O cinema também é uma opção de encontro com a Lucy e a Vittoria.
- **Conti Moretti Hospitais:** na recepção você agenda consultas ($90, uma por dia) nas 12 especialidades
  do site, atendidas pelas lideranças clínicas (Dra. Milany Moretti, Dra. Cristina Yang, Dra. Meredith Grey,
  Dra. Lexie Grey, Dra. Izzie Stevens e Dra. Addison Montgomery). A consulta renova a energia e dá um bônus
  no dia, diferente para cada especialidade. Fazer as 12 dá +15 de energia máxima para sempre. Tem farmácia,
  máquina de lanches e doação da Luthor Corp (uma por trimestre: a ação LCORP sobe e nasce a Ala Luthor).
  Se você desmaiar de cansaço, acorda num leito do hospital.
- **As médicas são personagens:** dá para conversar, presentear e fazer amizade com as seis lideranças
  (fotos em `assets/portraits/dra_*.jpg`). Elas chegam para o plantão, revezam entre consultórios,
  internação e recepção, almoçam fora (num lugar diferente a cada dia), têm folgas e vão embora no fim
  do turno. Com 3 corações cada uma dá um benefício: consulta pela metade do preço (Milany), hospital de
  graça se desmaiar (Meredith), contrato de $200 toda segunda (Cristina), trabalho mais leve (Lexie) e
  presentes (Izzie e Addison).
- **Ações:** no computador, escolha quantas ações comprar ou vender (digite o número ou use as setas),
  ou venda todas de uma vez.
- **Descansar:** uma hora na espreguiçadeira do terraço recupera energia.

## Moradores

A cidade tem moradores que não conversam, mas vivem a rotina: chegam pela rua, entram no café, na CatCo,
na livraria, no mercado, na Trattoria, no Noonan's, no cinema, no hospital, no parque ou na praia, ficam um
tempo e vão embora, para outro lugar ou para casa. Ninguém fica parado o dia todo, e ninguém repete o mesmo
lugar em sequência. Aperte E perto de um morador para observar o que ele
está fazendo.

## Conversas

Cada personagem tem muitas falas, que variam com o período do dia, o clima, o fim de semana, o lugar,
a amizade e o que está acontecendo no jogo. O jogo lembra o que já foi dito e não repete as falas.
Depois de conversar com alguém, a conversa fica bloqueada até o próximo período (manhã, tarde ou noite).
Presentes, lojas e convites continuam disponíveis.

## Cutscenes

O jogo tem cenas animadas com câmera, barras de cinema, balões de emoção, escolhas e efeitos:
a abertura (com um passeio pela cidade), os eventos de coração da Lucy e da Vittoria (2, 4, 6, 8 e 10),
o começo do namoro, a mudança para a cobertura, os encontros e alguns momentos da equipe.
Esc pula uma cena. No menu (Esc), **Rever cenas** reprisa as que você já viu.

Para criar ou editar cenas, abra `luthor/cutscenes.py`: cada cena é uma lista de comandos simples, como
`("andar", "lucy", 15, 7)`, `("emote", "lucy", "coracao")` e `("fala", "lucy", "Oi, Luthor.", "love")`.
A lista completa de comandos está no topo do arquivo.

## Romance

Lucy e Vittoria têm eventos especiais aos 2, 4, 6, 8 e 10 corações.

1. Aos **8 corações**, dê um **Buquê de Rosas Vermelhas** (Mercado Central) para começar a namorar.
2. Namorando, convide para **encontros** às 20h (Noonan's, praia, Trattoria...). Não dê bolo!
3. Aos **10 corações**, dê o **Pingente de Compromisso**: ela vem morar com você na cobertura
   e deixa um presente toda manhã.

Só dá para namorar uma pessoa por vez.

## Personagens

| Personagem | Onde encontrar | Benefício especial |
|---|---|---|
| Samantha Arias (CFO) | Sede, parque, café | Contratos +10% (3♥) |
| Querl Dox — Brainy (CTO) | Laboratório, parque | Projeto Hecate (3♥), drone (5♥) |
| Jess (assistente) | Recepção, café | +20 de energia (3♥) |
| Rafa (barista) | Grão Nobre | 20% de desconto (3♥) |
| **Lucy Williams** (CatCo) | Café de manhã, CatCo, Bayside, Noonan's à noite | Romance |
| **Vittoria Ricci** (chef) | Mercado às 7h, Trattoria, parque às 15h | Romance; desconto e receita da nonna |
| Nia Nal (CatCo) | CatCo, Bayside | Matéria que valoriza a LCORP (3♥) |
| Theo, Bea, Marco | Livraria, mercado, bar | Lojas |
| Seu Joca | Píer | Vara de pesca, iscas; segredo de pesca (3♥) |

## Para modificar

- `luthor/data.py` — projetos, itens, peixes, receitas, livros, lojas e objetivos.
- `luthor/characters.py` — personagens, rotinas, presentes, falas e eventos.
- `luthor/world.py` — mapas (os interiores são desenhados em texto).
- `luthor/art.py` — toda a pixel art é gerada por código (personagens em pixel art).
- `luthor/cutscenes.py` — as cenas e o motor de cutscenes.
- `luthor/dialogue.py` — falas por período do dia, clima, lugar e amizade.
- `luthor/activities.py` — horta, coletáveis, bichinho, karaokê e cinema.
- `luthor/hospital.py` — Conti Moretti Hospitais: especialidades, lideranças e consultas.
- `luthor/crowd.py` — moradores que circulam pela cidade.
- `luthor/effects.py` — borboletas, vagalumes, pétalas, brilhos na água e luz pelas janelas.
- `assets/portraits/` — fotos dos retratos. Para a Vittoria, coloque `vittoria.jpg`
  (e opcionalmente `vittoria_feliz.jpg` e `vittoria_apaixonada.jpg`). Para a Jess, coloque uma foto
  e indique o nome do arquivo em `characters.py`.

O jogo salvo fica em `saves/save.json`. Jogos salvos de versões anteriores continuam funcionando.

Fonte: Jersey 10 (SIL Open Font License, em `assets/fonts/OFL.txt`).
#   L u t h o r - L i f e  
 