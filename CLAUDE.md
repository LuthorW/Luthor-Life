# Luthor Life — notas do projeto

Jogo de simulação de vida em pixel art (estilo Stardew Valley / Coral Island), em Python + pygame-ce,
no universo da Luthor Corp. A jogadora é **Letícia Luthor**, CEO da Luthor Corp, em National City.
A dona do projeto fala português do Brasil: responda, comente o código e escreva textos do jogo em pt-BR.

- Repositório: https://github.com/LuthorW/Luthor-Life (branch `main`)
- Site do jogo: pasta `docs/` (GitHub Pages → https://luthorw.github.io/Luthor-Life/)
- Rodar: `python main.py` (ou `Jogar.bat` no Windows). Dependência única: `pygame-ce>=2.4`.
- A máquina da dona é Windows com Python 3.14.

## Estrutura

```
main.py              inicia Game().run()
Jogar.bat            acha o Python, instala pygame-ce e abre o jogo (cuidado: redirecionamentos >nul)
assets/fonts/        Jersey10.ttf (OFL) — fonte pixel da interface
assets/portraits/    retratos em ALTA resolução (nome.png + _feliz/_ruim/_timido), inclusive das médicas (sem dra_);
                     a dona prefere a qualidade boa: NÃO reduza a resolução para economizar espaço
limpar_retratos.py   apaga fundo branco/xadrez desenhado nos PNGs, sem mudar a resolução
assets/cmh.png       logo do Conti Moretti Hospitais
assets/lexcorp.png   logo da Luthor Corp
saves/               save.json e settings (fora do git)
docs/                site (index.html, style.css, script.js, img/, fonts/)
docs/wiki/           wiki do jogo (estilo wiki do Stardew), GERADA por gerar_wiki.py: não edite os .html à mão
gerar_wiki.py        `py gerar_wiki.py` monta docs/wiki/ a partir dos dados do jogo (páginas de personagens, itens,
                     peixes, receitas, calendário, festas, lojas...), a busca (busca.js) e as imagens (ícones, cabeças,
                     medalhas, mapa, retratos em WebP menores só para a wiki). wiki.css e wiki.js são escritos à mão.
                     Rode de novo depois de mudar falas, presentes, itens, rotinas, eventos etc. Não mexe no save
luthor/
  config.py      SCALE=2, TS=16, TILE=32, tela 1280x720, tempo (7s reais = 10 min), estação de 14 dias, cores C_*
  game.py        classe Game: estado, loop, interação, HUD, desenho, fim do dia, save/load
  world.py       mapas (interiores desenhados em texto), OBJECT_DEFS, portas CITY_DOORS/INTERIOR_DOORS
  art.py         TODA a pixel art é procedural (tiles, prédios, objetos, personagens 16x32, ícones)
  sprites.py     personagens estilo Stardew (cabeça grande de 12 px, rosto do jogo original com nariz, cabelo em mechas); roupas por `look["outfit"]`
                 (shirt, blazer, coat, chef, apron, vest, cardigan, fisher, blouse, trench, peacoat, skirt_suit,
                 patterned, breton, bartender, tech, labcoat, leather, captain); extras: beard, glasses, hat; substitui art._frames
  nautical.py    arte da Marina Luthor (clube, iate, veleiro, cais), tiles 'deep'/'deck' e o casco do alto-mar
  marina.py      Marina Luthor: peixes de alto-mar, projetos náuticos, passeios, regata (minigame), encomendas do Ian
                 (pagam 25% a mais que a Mesa de Contratos, pois são para a própria Luthor Corp)
  gifts.py       presentes extras (26 itens nas lojas), 4 coletáveis novos, gostos de cada personagem (ama/gosta/
                 não gosta) e as falas de "não gostei" para coletáveis e itens novos (`dislike_line`)
  scenery.py     cenário estilo Stardew: árvores grandes (copa some atrás), grama/terra, cantos e enfeites do chão
  entities.py    Player, NPC (rotina e caminho entre mapas), Car
  characters.py  NPCS (aparência, rotina, falas base, presentes, reações, eventos), NPC_ORDER, TEAM, ROMANCES;
                 no fim, as 5 médicas (DOCTORS, DOCTOR_KEYS) e a rotina diária delas (`doctor_schedule`)
  dialogue.py    LINES por período/clima/lugar/amizade, REACTIVE (falas condicionais), BUSY
  falas.py       MAIS: falas extras de todas as personagens (mesmas categorias de LINES), somadas no fim de
                 dialogue.py (a Celeste, no boutique.py, que monta as falas dela depois). Fala nova: pode entrar aqui
  hospital.py    Conti Moretti: especialidades, consultas, bônus do dia, farmácia, doação
  crowd.py       figurantes (moradores sem conversa) que circulam pela cidade
  activities.py  horta do terraço, coletáveis, bichinho, karaokê, cinema, céu do terraço
  cutscenes.py   motor de cutscenes (comandos em tuplas) e TODAS as cenas (as do Ian, Barry e Dona Graça no fim);
                 comando ("beijo", a, b) para beijo animado; `dating_scene` devolve a cena <chave>_pedido;
                 bebidas nas cenas: ("segurar", nome, item|None), ("beber", nome[, item]), ("brinde", a, b), ("acenar", nome);
                 ("chamar", fn): roda fn(g) no meio da cena e, se ela devolver passos, eles entram ali; nas escolhas, um
                 5º elemento chamável na opção é chamado quando ela é escolhida (a degustação conta acertos assim)
  poses.py       poses dos bonequinhos: sentada (SEAT_LIFT), braços "hold"/"mouth"/"wave"/"up"/"toast"/"umbrella"/"reach"/
                 "work", rostos happy/read/open/kiss/shut/love, `walk`/`lean`/`tiptoe` e `kiss_pose` (cache). Quadros
                 com margem `PAD`=6 px de arte de cada lado (braços erguidos em Y): `anchor()` já soma o PAD
  assentos.py    para onde cada assento olha (`face`: mesa ao lado, TV/mesinha de centro/tapete, cinema = tela) e os
                 desenhos virados (de costas e de lado) em 2 camadas: "base" e "front" (encosto/braço por cima de quem senta)
  animacoes.py   regar (regador), bancada (mãos e faíscas), vara de pesca (arremesso, boia, carretilha no minigame,
                 peixe erguido), deitar na cama (`Sleeper`), bichinho no colo no sofá, aceno dos amigos, gaivotas na
                 praia, gatinho de rua no Parque Central, modo foto (P) e as bebidas novas (cerveja, caipirinha, taça)
  emotes.py      emotes em estilo emoji (pixel art 20x20 com contorno): coracao, feliz, vergonha, gota, raiva,
                 triste, zzz, surpresa, beijo, estrela, pergunta, exclamacao, musica, brilho, reticencias
  festas.py      festas das estações (FESTIVALS: barracas/enfeites temporários no mapa da cidade, lugar de cada um,
                 cena de abertura, atividades), aniversários (BIRTHDAYS, presente x5) e o calendário (tecla C)
  casal.py       vida a dois (café da manhã, pedidos do dia a dia, aniversário de namoro) e ciúmes leves Lucy/Vittoria
  casamento.py   Anel de Noivado (Mercado, 14 dias morando junto), pedido no terraço, noivado e o casamento no Jardim do
                 Mirante (cena montada com os convidados), falas de casadas (`chat_line`)
  historia.py    história da Luthor Corp: os tios Conrad e Edmund, 5 capítulos (CHAPTERS) com cena + objetivo, atores extras
                 só das cenas (EXTRAS); a mesa da sala de reuniões mostra os capítulos
  escritorio.py  móveis dos escritórios: o da Letícia na sede (x 1..8, y 2..8, `furnish`: mesa de CEO, cadeira executiva,
                 retrato do pai Alexander, aparador, globo, carrinho de bar, cantinho de estar), a sala de reuniões da
                 sede (x 26..32, y 2..8, `furnish_reunioes`: mesa 5x2, telão, cavalete), a salinha da Sam (x 26..32,
                 y 12..16, `furnish_sam`) e o Gruppo Ricci (`furnish_ricci`: escritório da Vittoria e sala de projetos,
                 sem cozinha)
  fundacao.py    Fundação Luthor: 6 obras (PROJECTS) com doação de itens/dinheiro na mesa da sede, objetos novos na cidade
                 (PROPS), benefícios permanentes e a inauguração da praça
  momentos.py    MOMENTS: 12 cenas curtas entre dois NPCs, no máx. 1 por dia, ao passar perto do lugar no horário
  eventos.py     cenas e bônus novos dos eventos de coração de quem não tinha (Theo, Bea, Marco, Nia, Harry, Joca,
                 médicas, Barry, Dona Graça, Brainy, Jess); entram por `setdefault` em `NPCS[k]["events"]`
  closet.py      closet da Letícia no guarda-roupa da cobertura e no provador da boutique (LOOKS; 2 abas: roupas e
                 acessórios; comprar é só na Boutique; presentes de looks em GIFTS; comentários)
  boutique.py    La Boutique (entre o Grão Nobre e a CatCo, porta 42,15): Celeste Waite, 12 acessórios
                 (ACCESSORIES, item kind "acessorio", um por espaço SLOTS), 6 looks novos, loja com provador virtual
                 (`BoutiqueShop`), móveis, fachada, falas/aniversário/eventos da Celeste e a cena celeste_4
  decor.py       decorar a cobertura pelo computador de casa (CATALOG; só móveis comprados mexem), piano
  album.py       álbum de fotos do Barry (2 corações): cada cena especial vira foto em saves/album/<cena>.png
                 (cada espaço de jogo tem o seu: album, album2, album3)
  jogos_salvos.py  3 espaços de jogo salvo (save.json, save2.json, save3.json) e a tela de escolha (`SlotMenu`)
  celular.py     celular da Letícia (tecla T): apps Mensagens (amigas com 2+ corações mandam mensagens, `MSGS`;
                 cada mensagem tem 3 respostas próprias com a volta de quem mandou, `REPLIES_FOR`; responder dá
                 amizade e a conversa mostra a resposta e a volta), Agenda (linhas do HUD + próximos 7 dias), Tempo, Bolsa (fechamentos em
                 `g.phone["stocks"]`; E negocia se leu o livro), Fotos (escolhe as fotos do mural), Pedidos,
                 Habilidades e Mapa. Estado em `g.phone`
  pedidos.py     quadro de pedidos de pé no Grão Nobre (8,2): bilhetes novos à noite, entrega conversando com quem
                 pediu até o prazo (3 dias); paga dinheiro + amizade, sem castigo. `g.pedidos`. Espaços do quadro
                 liberados pelos pedidos entregues (`UNLOCK` = 0, 3, 7: começa com 1, vai a 3; `slots`/`max_active`)
  lugares.py     CatCo: estúdio da CatCo TV na sala de vidro (câmera `camera_estudio`: entrevista ao vivo 1x por semana
                 em dia útil 9h-18h, 3 assuntos; anúncio de $400 = produtos +15% por 3 noites, `sell_mult`), arquivo de
                 matérias antigas (`ARTICLES`, 1 por dia); mesas com o monitor de costas (`desk_r`, `desk_news`: quem
                 trabalha senta atrás); adega e barris do Ricci; leitos ocupados no hospital (`bed_patient`, o leito
                 da Letícia fica livre); balcão de portaria, caixas de correio, vitrine da sede; textos por lugar
                 (`PLACE_LOOK`). Estado em `g.catco`. Matérias antigas lidas: o arquivo mostra as manchetes da Letícia
  noticias.py    manchetes da CatCo sobre o que a Letícia faz: toda noite compara o estado com a noite anterior
                 (`snapshot`/`_diff`: namoro, mudança, casamento, peixe lendário, obras da Fundação, LCORP, vendas,
                 bichinho, entrevista) e soma os acontecimentos do dia (`event`: lançamento, sommelier, pediatria);
                 as 3 maiores vão para o feed (`g.noticias`). Aparecem no resumo da noite, na banca, na TV, nos e-mails,
                 no arquivo da CatCo e em falas reativas (Nia, Harry, Barry, Lucy, Sam, Vittoria, Izzie). Save antigo:
                 a 1ª noite só tira a foto, sem manchete
  degustacao.py  degustação de vinhos com a Vittoria na adega do Ricci (1x por semana, 2+ corações, ela na sede):
                 cena com 3 taças, ela descreve cor/aroma/boca/região e a Letícia escolhe entre 3 nomes (`WINES`);
                 acerto +30, erro +10 (nunca tira), culinária, 2+ acertos = Vinho Tinto, 3 = flag `sommelier`. `g.degust`
  pediatria.py   brinquedoteca no saguão do Conti Moretti (tapete 20..24,12..14, baú 24,12; `furnish`) e voluntariado
                 (9h-19h, 1x por dia): contar história (-10 de energia) ou levar doce/pelúcia (`GIFTS`) = amizade com as
                 5 médicas, carisma; na 1ª visita e na `DRAWING_AT` vira manchete (e ganha um desenho). `g.pediatria`.
                 As crianças são trabalhadores do crowd.py com `height=-6`
  habilidades.py pesca, ciência, culinária e carisma (níveis 0-5, `LEVELS`); `gain` é chamado na pesca, bancada,
                 lançamento, fogão, conversa e presente; bônus pequenos por nível e um extra no nível 5. `g.skills`
  mural.py       mural de fotos na parede da cobertura (9,1, em cima da escrivaninha, no lugar de uma janela):
                 até 4 fotos do álbum do Barry ou do modo foto (saves/fotos), escolhidas no app Fotos (`g.mural`)
  conquistas.py  46 medalhas em 4 categorias (tecla K e menu de pausa), aviso que desliza no canto de baixo
  surpresa.py    aniversário da Letícia (`BDAY` = outono, dia 6): festa surpresa no terraço das 19h às 23h, a Jess de
                 anfitriã, convidados = namorada + amigas com 2+ corações (`guests`), um presente de cada (`GIFTS`);
                 perdeu a festa = bolo da Jess de manhã. `g.surpresa`. O casamento nunca cai nesse dia
  andrea.py      Andrea Rojas (mora em Metrópolis; look de `historia.EXTRAS["rojas"]`, retrato `andrea.png` + humores):
                 mensagens no celular
                 (`celular.EXTRA_SENDERS`) e uma visita por estação (`VISITS`: café, praia, Trattoria, terraço) com cena,
                 aviso na véspera, $400 de parceria, energia, carisma e presente. `g.andrea`
  colecao.py     primeira coleção da Celeste (depois do desfile, flag `celeste_desfile`): investir $2500 conversando com
                 ela; em 3 noites lança 4 looks na Boutique, manchete na CatCo e $150 de royalties por semana. `g.colecao`
  coracoes.py    eventos de coração que faltavam na lore: lucy_5 (arquivo da CatCo), vittoria_5 (inauguração às 6h) e
                 vittoria_7 (o medo de amar alguém ocupada); saves antigos marcam como vistos se já passaram deles
  encontros.py   encontros especiais com a namorada: piquenique (Parque Central), veleiro ao pôr do sol (alto-mar),
                 cinema a dois e jantar a quatro mãos na cobertura; entram em `date_places`, cena própria (`scene`) e
                 bônus em `after` (energia cheia, pesca, carisma, culinária + prato). `g.encontros`
  clube.py       clube do livro do Theo: quinta 18h-20h na Bayside Books (Theo com 3+ corações), 8 livros (`BOOKS`),
                 1ª reunião com cena (Nia e Brainy), depois Dialog + escolha; amizade, carisma e um Livro a cada 3. `g.clube`
  corrida.py     corrida com a Sam na orla (terça, quinta, sábado, 6h-7h40; 2+ corações): +40 de amizade, energia máxima
                 +20 no dia e +5 para sempre a cada 5 corridas (até +25, `bonus` em `Game.max_energy`). `g.corrida`
  laboratorio.py melhorias do laboratório no painel (11,2) da sede: centrífuga (projetos -1 dia), impressora 3D
                 (produtos +10%), câmara de crescimento (Projeto Gaia) e supercomputador (Projeto Prometeu); cada uma
                 aparece encostada na parede (`apply`). `g.lab["owned"]`
  interiores.py  interiores caprichados: chão com textura, paredes de 2 tiles com papel de parede/lambri (`STYLES`),
                 sombra dos móveis e enfeites de parede automáticos (`THEMES`)
  natureza.py    mar com profundidade, ondulação e ondas subindo na areia; reflexos do pôr do sol e luar; árvores,
                 arbustos e tufinhos de grama balançando ao vento
  jogos.py       sinuca e dardos no Noonan's, xadrez com o Brainy (opção na conversa, 1x por dia)
  clima.py       tempestade (raios e trovões; o clima continua "chuva") e arco-íris na manhã depois da chuva
  timetest.py    modo de teste de dia/horário: `python main.py --teste` (F6 abre o painel; não salva nada)
  scenetest.py   modo de teste de cenas: `python main.py --cenas` / `--cena chave` (não salva nada)
  minigames.py   pesca, fliperama Meteoro, fogão, mochila
  effects.py     borboletas, vagalumes, pétalas, brilho na água, luz de janela
  lighting.py    iluminação: "mapa de luz" multiplicado no mundo (noite azul, chuva, pôr do sol dourado) com luz
                 de postes, janelas acesas, portas, faróis e em volta da Letícia; letreiros (NEON_STYLES) brilham.
                 Interiores: `INTERIOR` (clima de cada lugar: cor de dia/noite e luz do teto) e `EMITTERS`
                 (objetos que brilham: TV, aquário, fogão, neon, jukebox, telão...)
  caprichado.py  cidade caprichada (referência aprovada pela dona): calçada de pedra, meio-fio, asfalto, sombra dos
                 prédios, prédios redesenhados (`BUILDERS` + letreiros em `draw_label`), poste de lanterna, mesinhas
                 com guarda-sol, lousa, floreiras (`street_decor`/`FACADE_DECOR`) e pombos (`Pigeons`)
  citymap.py     mapa da cidade (tecla M) com a posição de cada personagem
  seasons.py     estações (Q1 primavera, Q2 verão, Q3 outono, Q4 inverno): grama, árvores, neve, coletáveis
  audio.py       som: efeitos gerados por código (músicas existem no código, mas DESLIGADAS: MUSIC_ENABLED)
  ui.py          fonte, painéis com moldura em pixel art, Dialog, Choice, Shop, InfoPanel, NumberPrompt, Toasts, HUD
  data.py        PROJECTS, ITEMS, FISH, RECIPES, BOOKS, SHOPS, CROPS, FORAGE, FLAG_LABELS, GOALS, TIPS
```

## Convenções importantes

- **Escala:** arte em 16 px por tile, ampliada por `SCALE` (2). Use sempre `TILE`/`SCALE` em vez de números
  fixos de pixel. Interiores usam zoom 1,5x (`Game.zoom_for`); a cidade, 1,0x.
- **Arte nova:** crie a função `_algo()` desenhando numa `new(w, h)` em pixels de arte e registre em
  `art.OBJECT_BUILDERS` (módulos novos fazem `art.OBJECT_BUILDERS.update(...)`). O objeto também precisa de
  uma entrada em `world.OBJECT_DEFS` = (largura, altura, sólido, camada "obj" | "decal" | "wall").
- **Ícones de item:** `art._icon(kind, color)`; módulos novos estendem via wrapper (ver `activities._icon_extra`).
- **Cidade (mapa v2, 112x80; o mar vai até o fim para a câmera mostrar o oceano):** áreas verdes em `world.CITY_AREAS` (park, woods, garden, beach) — figurantes e
  coletáveis usam essas áreas. Saves antigos são convertidos por `world.old_city_xy` (campo `city_layout`).
- **Retratos:** `assets/portraits/<chave>.png` + `_feliz`, `_ruim` (ou `_bravo`), `_timido`, achados por
  `art.portrait_file` (o Harry usa `portrait_key="harry"`; a chave interna continua `rafa`). Humores: happy/smile ->
  feliz, bad -> ruim, shy/love -> tímido. Presente amado = tímido, presente ruim = ruim. Fundo branco ou xadrez
  desenhado é apagado por `art._clear_fake_bg`. Médicas seguem o mesmo padrão
  (a Cristina, chave interna `yang`, usa `portrait_key="cristina"`).
  **Retrato novo:** coloque o PNG em assets/portraits e rode `py limpar_retratos.py` se ele tiver fundo (usa numpy;
  limpa pelo padrão do xadrez). O jogo reduz em etapas na hora de mostrar (`art._shrink`).
- **Carros (entities.Car):** freiam de verdade (`sqrt(2·desaceleração·folga)`) e param a `Car.GAP` do carro da frente
  e de quem estiver a pé na faixa (Letícia, NPCs, figurantes: `Game.update_cars` passa os `walkers`); a lataria
  (`Car.rect`) bloqueia a jogadora. Na faixa de pedestres eles esperam a pessoa passar.
- **Prédio caprichado novo:** função `_estilo(W, H, night)` em `caprichado.BUILDERS` (porta alinhada ao tile da
  porta de `world.Building`; para a porta ficar no meio, o prédio precisa de largura ímpar em tiles: a CatCo tem 9),
  letreiro em `caprichado.draw_label` (`_sign` centraliza as letras na faixa do letreiro, como na Luthor Corp, na CatCo, no Noonan's, no Cine National
  e nos Apartamentos Bayside). Vidro aceso SEMPRE com `caprichado.LIT`
  (252, 222, 136): é por essa cor que `lighting.py` faz as janelas brilharem. Use as peças `window`, `awning`,
  `bricks`, `cornice`, `door`, `shopfront`, `vaso`, `lantern`, `_arched`. Todos os 13 prédios da cidade já estão
  no estilo novo (os desenhos antigos em art.py, scenery.py e nautical.py ficaram, mas não são mais usados).
  O Noonan's é o único com a porta de lado (pedido da dona); o Cine National (9 tiles) e os Apartamentos Bayside
  (7 tiles, porta em 78,45) têm a porta no meio. A banca de jornais fica no vão entre o Gruppo Ricci e o hospital
  (`kiosk` news em 70,15). No saguão da sede, a recepção da Jess (11..13,12) e o `tapete_saguao` (10..14, 13..16)
  ficam no eixo da porta (x 12).
- **Iluminação:** não use véu semitransparente por cima do mundo; mexa em `lighting.py` (cores NIGHT_* e manchas
  de luz). Luz nova = desenhar uma mancha na camada com BLEND_RGB_ADD.
- **Ruas:** NPCs evitam o asfalto (`GameMap.road`) e atravessam só pelas faixas; entram e saem pelas calçadas.
- **Colisão:** `world.HITBOXES` define a parte que bloqueia a jogadora em objetos pequenos (poste, banco, árvore,
  arbusto...); NPCs desviam do tile inteiro. A jogadora escorrega pelas quinas (`Player._slide`).
- **Mapas:** interiores são listas de strings (W parede, G vidro, o madeira, m mármore, t azulejo, c carpete,
  b carpete azul, k xadrez, r terracota, D porta). Toda porta de interior precisa estar em
  `INTERIOR_DOORS` e `CITY_DOORS`. **Sempre teste se todas as salas são alcançáveis** (`m.find_path`):
  já houve bug de prateleira bloqueando a entrada da internação.
- **Rotinas de NPC:** lista de `(minuto_do_dia, mapa ou None, x, y, direção)`; `None` = fora de cena.
  Tipos: `default`, `weekend`, `rain`. Encontros sobrescrevem 19h–22h.
- **Fonte pixel (Jersey 10) NÃO tem** ♥ ♪ ▲ ▼ ✓ ±. Desenhe com pygame ou use texto simples.
- **Save:** campos novos sempre com valor padrão no `load` (jogos salvos antigos têm que continuar abrindo).
  Módulos têm `init_state / save_state / load_state` chamados por `Game`.
- **Hooks no Game:** `activities.*` e `hospital.*` são chamados em `reset_state`, `update`, `resolve_target`,
  `target_label`, `use_object`, `object_image`, `draw_world`, `process_night`, `save`/`load`.
- **Classe CSS `.split`** já existe no site (grade de 2 colunas): não reutilize esse nome.
- **Interface em pixel art:** use `ui.panel` (moldura chanfrada com pedrinhas douradas nos cantos dos painéis
  grandes), `ui.box` (cartões e linhas escolhidas), `ui.slot` (espaço de item afundado; escolhido = moldura clara e
  cantinhos dourados), `ui.highlight` (faixa da opção) e `ui.cut_rect` (cantos em escadinha). Tudo em passos de
  `ui.U` = 2 px (1 px de arte). Nada de `border_radius` em interface nova.
- **Paredes dos interiores (interiores.py):** a fileira de parede de cima vira parede de 2 tiles (`_is_upper`):
  sanca, papel de parede, roda-meio, lambri e rodapé. Divisórias finas continuam com 1 tile e topo escuro. Enfeites
  de parede ("wall" e decalques na face) sobem até 8 px de arte (`interiores.lift`, em `draw_world` e em
  `_build_floor`) para ficar no meio da parede. Estilo novo de lugar = entrada em `STYLES` (e `THEMES` se quiser
  enfeites automáticos; a cobertura, o terraço e os apartamentos não ganham).

## Sistemas e regras de design (pedidos da dona)

- **Visual:** personagens no estilo Stardew (sprites.py), mas magrinhas (16x32), a Letícia tem **olhos verdes**,
  **nada de cabelo preso** (sem coque: só soltos, curtos ou black power), sem nuvens no céu,
  cabelo sem cobrir o rosto (franja aberta no meio, mechas por fora das bochechas), e corpos diferentes como no
  Stardew: `look["height"]` (-2..+2 px, cresce para cima; -3..-6 só para crianças, `sprites.SHORT_ROWS`; entre elas, só Letícia, Sam e Addison são mais altas) e `look["broad"]` (ombros largos), em `characters.BODY`,
  câmera afastada. Gráficos "bonitinhos".
- **Conversas:** muitas falas e nada de repetição (`lines_seen` guarda as já ditas). Cada personagem conversa
  **uma vez por período** (manhã 6–12h, tarde 12–18h, noite 18–2h); depois disso aparece a fala BUSY e
  um balão "...". Presentes, loja e convites continuam liberados.
- **Figurantes (crowd.py):** não conversam (E mostra o que estão fazendo). Chegam pela rua, entram num lugar,
  ficam um tempo e **sempre saem**. Nunca repetem um dos últimos lugares visitados, nem de um dia para o outro.
  **Trabalhadores** (`WORKERS`): figurantes com posto e horário fixos (4 redatores da CatCo, recepcionista do Ricci e do
  hospital, porteiros do Bayside e do Residencial, pacientes na sala de espera com `chance` por dia). Os postos ficam em
  `crowd.reserved` (outros figurantes não usam). Chegam pela rua e vão embora no fim do turno (`tick_workers`).
- **Alcance da conversa:** `Game.npc_near` acha a personagem num cone na frente da Letícia (até 1,9 tile, 0,9 de lado;
  com um móvel sólido bem na frente, só até 1,4), sem atravessar parede. O tile exato da frente continua tendo prioridade.
- **Sede da Luthor Corp e Gruppo Ricci (escritorio.py):** a sede tem 34 tiles de largura: escritório da Letícia
  (x 1..8), laboratório (x 10..24) e sala de reuniões (x 26..32, entrada pelo corredor da fileira 10, em 29-30,9;
  o tile (24,10) tem que ficar livre). Embaixo dela, atrás do vidro, a salinha da Sam (porta em 25,14, pela área de
  espera de madeira): a Sam trabalha sentada na cadeira azul (29,12), e as cenas sam_0/2/8 acontecem ali. No Gruppo Ricci a
  Vittoria trabalha sentada na cadeira de veludo (4,2), atrás da mesa de mármore; a sala da direita é a sala de projetos
  das casas novas (não existe mais cozinha: a Vittoria não é chef).
- **Médicas (fim de characters.py):** Cristina, Meredith, Milany, Izzie e Addison (a Lexie saiu do jogo).
  Duas roupas: `look` no hospital (jaleco/pijama) e `look_off` fora dele (`OFF_DUTY`, `characters.look_for`;
  `NPC.current_frames` e os atores das cenas escolhem pela sala). conversáveis e presenteáveis. Plantão alternando postos sem repetir em sequência,
  nunca duas no mesmo lugar, almoço em lugar diferente a cada dia, 2 folgas por semana.
  Benefícios de 3 corações: Milany (consulta pela metade), Meredith (hospital grátis se desmaiar),
  Cristina (contrato de $200 às segundas), Izzie e Addison (presentes).
- **Presentes:** coletáveis também são presenteáveis; são neutros para quase todo mundo, algumas personagens gostam
  e algumas odeiam (cada uma tem uma fala própria para coletável odiado e outra para item novo de que não gosta).
- **Conti Moretti Hospitais** segue o site do projeto `CMHospitais` (pasta irmã): 12 especialidades,
  lideranças clínicas, cores verde #123f35, cobre #b77b65, papel #fbfaf8. Consulta: energia cheia + bônus do dia.
- **La Boutique (boutique.py):** a Celeste Waite (estilista **francesa, de Lyon**: nada de raízes brasileiras; estudou em Milão; rosto da
  **Sofia Boutella**, com o cabelo pintado cor de vinho como no bonequinho; `NPCS["celeste"]`, retratos `celeste.png` + `_feliz`/`_ruim`/`_timido`) fica no balcão (12,4)
  das 9h40 às 19h. A loja tem 2 abas: roupas (o look vai direto para o closet) e acessórios (vão para a mochila).
  Acessório: F na mochila ou o closet/provador veste (sai da mochila e fica guardado em `g.closet["acc"]`; em uso em
  `g.closet["worn"]` = espaço -> chave); dá para presentear (gostos em `boutique.TASTES`). Os acessórios são chaves
  do look (`sunglasses`, `earrings`, `necklace`/`pendant`, `bag`, `beret`, `tiara`) desenhadas em
  `sprites._accessories` (aparecem andando, sentada e nas cenas). Roupas `dress`/`dress_floral` (vestido até o
  joelho, pernas à mostra; poses sentadas em `poses._sit_front`/`_sit_side`). Eventos: 2 lenço de seda, 4 cena
  celeste_4 (VIP: 20% de desconto, flag `celeste_vip`), 6 vestido "assinatura" no closet, 8 cena celeste_8 (desfile no
  píer ao pôr do sol, com plateia na areia; o comando de cena ("comenta_look", nome) faz a personagem comentar a roupa
  que a Letícia está usando; no fim, flag `celeste_desfile` e o vestido "passarela" chega à noite, `boutique.night`). Compras contam em
  `g.stats["boutique"]`.
- **Romance:** Lucy Williams (repórter da CatCo, Brie Larson) e Vittoria Ricci (Adria Arjona), dona do Gruppo Ricci,
  rede de restaurantes com sede em National City (o prédio que antes era o banco). Ela **não é chef**: quem cozinha
  e cuida da loja da Ricci Trattoria é a Dona Graça, chef brasileira veterana.
- **Harry** (antes Rafa) é o barista do Grão Nobre. **Barry Allen**: fotógrafo da CatCo, amigo da Nia e da Lucy.
  **Ian**: diretor da Marina Luthor, a divisão náutica da Luthor Corp. É **funcionário da Letícia** (como a Sam e o
  Brainy), não sócio, e amigo de infância das férias no interior.
  Rosas aos 8 corações → namoro; pingente aos 10 → morar junto. **Só a Lucy e a Vittoria passam de 8 corações:**
  todas as outras param em 8 (`config.FRIEND_CAP_HEARTS`, `Game.heart_cap`; saves antigos acima disso voltam para 8 no
  `load`; o painel de relacionamentos mostra 8 corações para elas). Evento de coração novo de amiga: no máximo 8. Cutscenes nos eventos de coração.
  **9 e 10 corações só namorando:** antes das rosas a Lucy e a Vittoria também param em 8 (`heart_cap`); o painel mostra
  os corações 9 e 10 apagados com cadeado (`ui.hearts_row(..., locked_from=)`).
- **Eventos de coração com cena** não tocam na hora: ficam pendentes (aviso + linha rosa no HUD) até a jogadora
  estar no mapa da cena (barco do alto-mar começa na marina) entre 3h antes e 3h depois do horário da cena; na
  cidade, também perto do ponto da cena (`Game.check_scene_events`, `scene_place`). Eventos sem cena aparecem na hora. Eventos de **0 corações** são surpresa:
  tocam no lugar e horário certos, mas sem aviso nem linha rosa no HUD.
- **Tela e retratos nítidos:** o jogo desenha num quadro de 1280x720 (`Game.screen`); `Game.present` amplia
  para a janela (tela cheia = resolução do monitor) e redesenha os retratos em alta (`ui.blit_portrait` registra,
  `art.portrait_hd`). Retrato novo na interface: use `ui.blit_portrait`.
- **Caixa de fala:** retrato grande solto à esquerda, **fora** da caixa (a caixa não fica atrás dele); a caixa de texto
  começa ao lado, com texto maior e o nome em cima, na borda. PNG sem quadro, fotos .jpg com moldura.
- **Ações LCORP:** variação noturna = aleatório + vendas de produtos/800 × `STOCK_PER_800` (2,5) + bônus (Nia, doação).
  Compra e venda com quantidade livre (`ui.NumberPrompt`) e "Vender todas".
- **Estações:** `seasons.set_season` troca cores/árvores e reconstrói o chão (Game.apply_season, automático
  quando o trimestre muda). Roupas por estação em `characters.WARDROBE` + `dress()` (primavera = `look`);
  sprites ganharam `scarf` (cachecol) e `sleeves="short"`. No inverno a "chuva" vira neve. Chance de chuva: primavera 25%, verão 12%, outono 32%, inverno 35%.
- **Som:** `audio.sfx(nome)` para efeitos (conversa, menus, lojas, itens, coração, pesca...). A dona NÃO gostou
  das músicas geradas: desligadas (`audio.MUSIC_ENABLED = False`). Passos também saíram (testados duas vezes; `audio.STEPS_ENABLED = False`): não colocar de novo sem ela pedir.
  Volume dos efeitos no menu de pausa (settings `sfx`).
- **Bichinhos (activities.py):** gato e cachorro desenhados em `_cat`/`_dog` (4 direções, andar de 4 quadros,
  sentado, piscando, rabo abanando, dormindo); o nome é digitado na adoção (`ui.TextPrompt`, Tab sugere) e pode ser
  trocado na caminha. A caminha fica no canto da sala, `activities.PET_BED` = (24, 14) (igual a `world.build_home`).
- **Casas (fim de world.py):** portaria `bayside` (aberta 7h–23h) com Lucy, Vittoria, Brainy, Jess, Nia e Barry, e
  portaria `residencial` (Residencial Luthor, sempre aberta) com Sam, Ian, Milany e o elevador da cobertura: a porta da
  rua leva à portaria e a cobertura (`home`) sai para ela. `APARTMENTS`, decoração em `APT_STYLE` (quarto separado da sala por parede; cozinha em `KITCHENS`: no
  Residencial igual à da cobertura, no Bayside compacta; tamanhos em `APT_SIZE`), uma cama para cada
  morador em `beds.py` (`bed_<chave>`). A porta só abre com o dono em casa e 2 corações (`Game.door_open`); na casa
  dos outros os móveis só mostram uma frase (`Game.APT_LOOK`). As rotinas trocam o "fora de cena" pela casa
  (`characters._at_home`, também na rotina diária das médicas); NPCs andam em 3 níveis (cidade → portaria →
  apartamento/cobertura, `SUB_PARENT`/`LOBBY_DOORS`/`APT_DOORS` em entities.NPC). Morando junto, vira a cobertura.
- **Comer/beber/ler (`Game.start_eat_fx` / `_eat_pose`):** a Letícia segura o item nas mãos (poses de poses.py):
  comer = prato no peito, três mordidas (leva à boca com a boca aberta, "nhac" com farelos, mastiga), item some;
  beber = leva o copo à boca e vai inclinando, olhos fechados nos goles; ler = livro aberto no peito (de frente aparece
  a capa, de lado as páginas), olhando para baixo, duas páginas viram. No fim, carinha feliz (^^) e emoji acima da
  cabeça (`player_emote`: feliz / estrela). Sentada, continua virada para a mesa; de costas, o item aparece acima da
  cabeça. Onde fica a mão: `poses.anchor`. Sons `eat`/`gulp`/`page`/`yum`/`reward`.
- **Pedido de namoro:** dar as rosas (8 corações) não mostra nada na personagem: marca `Game.proposal` e avisa
  onde e quando será o pedido (`proposal_text`, linha rosa no HUD). A cena `<chave>_pedido` toca no lugar/horário
  (`scene_ready`) e, no fim, `accept_proposal` começa o namoro. As cenas de pedido terminam com ("beijo", ...).
  O nome antigo `namoro_<chave>` é a mesma cena: `cutscenes.same_scene` junta os dois nomes (lista do `--cenas`,
  "Rever cenas", saves antigos e álbum), para o pedido não aparecer duplicado.
  Porta de apartamento abre sozinha quando há evento com cena marcado ali naquele horário (`Game.door_open`).
- **Posições nas cenas:** conversa a dois = na mesma linha, frente a frente, a 1 ou 2 tiles (nunca na diagonal
  colada nem uma atrás da outra olhando para o mesmo lado). Grupo = triângulo: as duas personagens frente a frente a
  2 tiles e a Letícia chega no meio, 1 tile abaixo, olhando para cima, e elas viram para baixo (padrão dos momentos).
  Mesa = cada uma senta numa cadeira (`"sentar"`). Ninguém começa ou para dentro de parede/móvel, no asfalto, nem anda
  por cima de outra atriz (`walk_to` anda primeiro na horizontal, depois na vertical: quebre em dois "andar" se precisar).
  A Letícia entra pela porta do lugar.
- **Caixa de escolhas (`ui.Choice`):** no pé da tela como no Stardew, pergunta em cima, setinha na opção,
  no máximo 6 visíveis com rolagem (rodinha do mouse também).
- **Sentar:** cadeiras, banquetas, bancos, sofás e poltronas (`poses.SEAT_LIFT` = `Game.SEATS`, altura do assento em
  px de arte). Ela vira para a mesa ao lado (`seat_dir`); `Player.seat` (t/off: desliza até o assento e "plof"),
  `Player.rise` ao levantar; andar ou E levanta (E com alguém na frente conversa). Funciona até na casa dos outros.
  Quadros sentada em poses.py (mesmas peças de sprites.py): de frente colo mais claro (cor "G"), joelhos e canelas; de
  lado coxa para a frente; de costas sem pernas e mãos na mesa. De vez em quando ela balança os pés (`swinging`).
  **NPCs e figurantes também sentam** quando param em cima de um assento (`NPC._check_seat`, `poses.NPC_SEATS`, que
  inclui as poltronas do cinema); sentados, olham para a mesa e às vezes para a frente. Cutscenes não mudaram.
- **Assentos virados (assentos.py):** cada cadeira, banqueta, poltrona, sofá e poltrona de cinema tem uma direção
  (`o.face`, calculada por `_compute` e refeita sozinha quando a lista de objetos muda; a decoração chama `invalidate`):
  mesa encostada > TV/mesinha de centro (sem parede no meio) > tapete > de frente para a parede de baixo vira "up" >
  "down". Sofás 3x1 só viram para cima/baixo e só para o que está bem na frente deles. Cinema sempre "up".
  Desenhos "up" (de costas) e "right" (de lado; "left" é espelhado) em `BUILDERS`, cada um com camada "base" (no lugar
  do objeto, por `Game.object_image`) e "front" (encosto visto de trás, braço da poltrona de lado), que entra na lista
  de desenho em `sort_key + FRONT_BIAS` (`assentos.world_items`). Quem senta fica em `sitter_sort` (entre as duas):
  `Player.seat["sort"]` e `NPC.sort_y`. A Letícia (`seat_dir`) e os NPCs (`seat_face`) sentam virados para `face`.
  Assento novo = entrada em `KINDS` (e `BUILDERS` se precisar de desenho virado). No sofá de costas o bichinho deita
  no encosto, do lado dela (`animacoes.LapPet`, `BACKREST_TOP`). Sofá/poltrona sem TV, mesinha ou tapete e com a frente
  apertada (até 2 tiles livres até a parede/móvel, `_run`) vira de costas para o lado aberto da sala.
  **Cenas:** ("sentar", nome) senta o ator no assento do tile onde ele está (virado para `face`, desenho e ordem iguais
  aos dos NPCs, `Actor.sort_y`); ("levantar", nome) ou andar levanta.
- **Bônus das cenas:** Sam 4 (`sam_bonus`, Mesa de Contratos +10%) e 8 (`sam_bonus2`, +25%; 35% no total, em
  `sell_value`); Vittoria 2 (`vittoria_coffee`: cappuccino grátis 1x por dia na loja da Trattoria, `ricci_coffee`).
  Ian 4 (`ian_deepfish`: peixes de alto-mar +15%), Milany 6 (`milany_care`: +20 de energia ao entrar no hospital,
  1x por dia, `milany_visit`), Brainy 6 sem cena (`brainy_fast`: projetos 1 dia mais rápidos, `Game.project_days`),
  Jess 5 com a cena nova `jess_5` (`jess_agenda`: das 9h às 12h o relógio anda 10% mais devagar).
- **Beijo:** opção "Beijar" na conversa com quem você namora ou mora junto (`Game.kiss`): as duas ficam de lado, uma
  de frente para a outra, a `poses.KISS_DIST` = 16 px de arte (1 tile; perto disso os rostos se embolam), de mãos dadas
  (braço "reach", as mãos se encontram no meio). Etapas de `poses.kiss_pose`: "close" (olhos fechados), "kiss"
  (inclinam 1 px, `lean`, os narizes e lábios se tocam; quem é mais baixa fica na ponta dos pés) e "after" (rosto
  "love": sorriso com bochechas coradas). Som `kiss` e corações subindo; +30 de amizade uma vez por dia (`Game.kissed`).
  O comando ("beijo", a, b) das cenas usa as mesmas poses. O abraço antigo ("hug"/"hug2") saiu: a dona não gostou.
- **Copos (entities.DRINK_SPRITES):** bebidas na mão são copinhos em pixel art (cerveja, taça, caipirinha, xícara,
  refrigerante, drink), não o ícone grande da mochila, para não tapar o rosto. `draw_drink` põe o fundo do copo no
  ponto de `DRINK_AT` (segurar = peito, beber = só a boca, brinde = altura do peito: os dois copos se tocam entre
  atores a 1 tile). Gole inclina no máx. 35 graus; de costas, o copo não aparece.
- **Animações do dia a dia (animacoes.py, `g.act`):** regar, bancada, "pegou" (braços abertos em Y, "viva!", e o peixe flutuando acima da cabeça como no Stardew; braços colados na cabeça pareciam antenas ou orelhas, a dona achou estranho) e dormir travam
  o andar enquanto duram. A cama não encerra o dia na hora: ela deita (`player.hidden`, a cabeça no travesseiro e o
  cobertor da própria cama por cima), "zzz" e só então `end_day`. Na pesca, `g.reel` fica ligado durante o minigame.
- **Guarda-chuva:** chovendo (fora do inverno) todo mundo na rua anda de guarda-chuva (`entities.UMBRELLA["on"]`,
  ligado por `animacoes.update_fx`); a Letícia usa um roxo. Quem está de guarda-chuva sorri em vez de acenar.
- **NPCs comendo/bebendo:** sentados em café, Trattoria, Noonan's, Gruppo Ricci, hospital e marina pegam algo de
  `entities.SNACKS` e dão goles/mordidas de vez em quando (`NPC._tick_snack`).
- **Aceno:** amigos com 2+ corações (ou namorada) acenam quando a Letícia passa perto, 1x por período (`g.waved`).
- **Modo foto (P):** esconde HUD e avisos; Enter salva em saves/fotos/; 1 acena, 2 sorri, 3 coração; P/Esc sai.
- **Sobretudo (trench):** do tamanho do blazer (até a cintura) para o corpo da Vittoria ficar igual ao das outras.
- **Festas (festas.py):** uma por estação: Festa das Flores (primavera, dia 7, 9h–15h, Parque Central, anfitriã Nia,
  Dança das Flores no mastro com quem tem 4+ corações), Luau de Verão (verão, dia 7, 18h–23h, praia, Dona Graça, sopa
  do caldeirão: o ingrediente dá amizade com todos, nunca tira), Feira da Colheita (outono, dia 7, 10h–17h, calçadão
  central, Sam, concurso pelo valor do item: $600/$300/$100, o item volta) e Noite das Luzes (inverno, dia 10, 18h–22h,
  Jardim do Mirante, Jess, amigo secreto sorteado no 1º dia do inverno: presente x3 e a Letícia ganha um de volta).
  `sync` monta os objetos temporários no dia (sólidos em `m.solid`, desmontados no dia seguinte), `override` leva todo
  mundo para o seu lugar (`spots`, calculado longe das barracas e portas), `check` toca a abertura uma vez ao chegar,
  barraca = loja só daquele dia. Dia de festa tem sol (menos no inverno) e não dá para marcar encontro à noite.
  Na Feira, as linhas 37-38 do calçadão ficam atrás dos telhados: enfeites só até a linha 36 (ou no vão entre prédios).
- **Aniversários:** `festas.BIRTHDAYS` (trimestre, dia), nunca em dia de festa. Presente no dia: amado x5, gostou x3,
  neutro x2 (+ fala de aniversário), balãozinho na mão dela, fala própria na primeira conversa, aviso na noite anterior,
  linha rosa no HUD e no painel de relacionamentos. Itens novos: Coroa de Flores, Água de Coco, Torta de Abóbora,
  Chocolate Quente (barracas) e Porta-retrato.
- **Vida a dois (casal.py):** morando junto, café da manhã na cozinha em algumas manhãs (sempre no fim de semana),
  com beijo e um prato embrulhado; um pedido pequeno por dia (item, visita no trabalho ou chegar em casa entre 19h e
  22h), entregue conversando, +60 de amizade e nada de castigo se não der. Aniversário de namoro a cada 56 dias
  (`casal["since"]`, contado desde o pedido): jantar com cena (morando junto, no terraço; namorando, no 1º lugar de
  encontro dela), presente x3 no dia e um Porta-retrato de presente.
- **Ciúmes leves:** conversas, presentes, encontros, danças e beijos com Lucy/Vittoria contam atenção (últimos 3
  dias). Se uma recebeu bem mais que a outra, a outra comenta na próxima conversa (no máx. a cada 4 dias); as três
  respostas sempre dão amizade. Se a Letícia namora uma, a outra não tem ciúmes.
- **Casamento (casamento.py):** o Anel de Noivado ($3000) só aparece no Mercado depois de 14 dias morando junto
  (`MIN_DAYS`). Dar o anel marca o pedido para a mesma noite, no terraço (19h–23h); depois do sim, o casamento é
  7 dias depois (pula festas e aniversários), 15h–19h, no Jardim do Mirante (`GARDEN`): a Sam celebra, a Jess fica de
  um lado e a madrinha (Nia para a Lucy, Dona Graça para a Vittoria) do outro; os outros NPCs viram convidados. No fim:
  flag `casadas`, +$2000 e amizade com todos. Estado em `g.casamento`; o painel de relacionamentos mostra o status.
- **História da Luthor Corp (historia.py):** a partir do 3º dia. Cada capítulo tem cena (linha no HUD, lugar e
  horário) e, depois, um objetivo que libera o próximo (lançar 5 produtos, faturar $6000, ação a $110, 4 corações com
  Sam/Brainy/Jess/Ian). No fim (`luthor_livre`): produtos +10%, $3000 e amizade com a equipe. A reunião do conselho é na
  sala de reuniões da sede (`mesa_reuniao`, que também abre o painel dos capítulos; a Letícia senta na cabeceira). Personagens só de cena
  (tios, Andrea Rojas, Hamilton, o espião) ficam em `EXTRAS`, com look próprio; o retrato sai do bonequinho, a não ser
  que o extra tenha `portrait` (a Andrea tem: `andrea.png`, também no celular via `EXTRA_SENDERS[...]["portrait"]`).
  **Andrea Rojas é amiga da Letícia** e mora em Metrópolis: conselheira do lado dela, nunca vilã nem rival (andrea.py).
- **Fundação Luthor (fundacao.py):** mesa na sede (`HQ_DESK`). Doar itens da mochila ou dinheiro; a obra completa
  aparece na cidade na noite seguinte (`night`: ready → built; `apply` põe os objetos de `PROPS` e recalcula `m.solid`).
  Benefícios: coreto (conversas +10%), peixaria (peixes +10%), horta (cesta às segundas), lanternas (+coletáveis),
  biblioteca (livros e mercado mais baratos). A praça só abre com as outras 5 prontas; a inauguração dá amizade com todos.
  Objeto novo na cidade não pode tapar porta nem caminho: teste com `m.find_path`.
- **Momentos (momentos.py):** cenas entre dois NPCs (`MOMENTS`: lugar, horário, dias, sol, corações mínimos **com as
  duas**: `min(hearts(a), hearts(b)) >= hearts`). Tocam no
  máx. 1 por dia, nunca em dia de festa, quando a Letícia passa perto; +20 de amizade com as duas e vão para a galeria.
- **Eventos novos (eventos.py):** bônus em `shop_mult` (Bea: mercado -20%, Marco: bar -25%), `food_mult` (Izzie: doces
  x1,5), `gift_mult` (Addison +15%), `new_fish` (Barry: +$50 por espécie nova), `marco_tab` (jogos de graça) e presentes
  da manhã (Theo aos sábados, Dona Graça às sextas).
- **Closet / decoração / álbum:** o look escolhido vale no jogo e nas cenas (`closet.player_look`; "Roupa da estação" =
  troca sozinha). Na decoração, um móvel não pode tapar a porta, um lugar reservado (namorada, bichinho, cenas) nem
  deixar canto sem acesso (`decor.can_place`). As fotos do álbum só vão para o disco junto com o save (nos modos de
  teste, nada); os testes têm que apagar fotos novas de saves/album.
- **Minigames (jogos.py):** sinuca (6 bolas em 8 tacadas) e dardos (9 dardos) custam `PLAY_COST`; xadrez com regras
  completas e o Brainy joga mais sério conforme a Letícia ganha.
- **Clima especial (clima.py):** tempestade é sorteada na véspera (`STORM_CHANCE` por estação) e continua sendo
  "chuva" para rotinas, peixes e figurantes; relâmpago clareia a tela (`draw_flash`), trovões são efeitos gerados por
  código. Arco-íris de 6h às 11h num dia de sol depois de chuva (70%). No inverno, nenhum dos dois.
- **Vários jogos salvos (jogos_salvos.py):** 3 espaços. O 1 é o saves/save.json de sempre (saves antigos abrem
  nele); `Game.slot` diz onde salvar e carregar, e `settings["slot"]` guarda o último usado (é o que "Continuar"
  abre; vazio = o mais recente). Tela de título: Continuar, Carregar jogo e Novo jogo (escolhe o espaço; X apaga).
  Cartão do espaço lido do arquivo (`info`): data, dinheiro, lugar, namoro/casamento e medalhas.
  **Testes:** salvem num espaço que não existia (ou troquem `jogos_salvos.SAVE_DIR`/`SAVE_PATH`) e apaguem depois
  saves/save2.json, save3.json e as pastas album2/album3 que criarem.
- **Conquistas (conquistas.py):** `ACHIEVEMENTS` (chave, categoria, nome, descrição) conferidas em `check` (a cada
  10 min do jogo e na noite); ao carregar, `sync` dá de uma vez as que já foram cumpridas, com um aviso só. Estado em `g.conquistas`
  (got, when). Aviso desliza no canto de baixo à esquerda quando não há janela aberta. Presentes dados contam em
  `g.stats["gifts"]`.
- **Módulos novos (game.NOVOS):** surpresa, andrea, colecao, coracoes, encontros, clube, corrida e laboratorio são
  chamados de uma vez por `_each(nome, ...)` (init_state, load_state, night, morning, talk_options) e `_first(nome, ...)`
  (chat_line, check); `save_state` e `hud_lines` também passam por todos. Módulo novo com estado próprio: basta pôr
  em `NOVOS`. Ganchos genéricos para não mexer nos sistemas antigos: `celular.EXTRA_SENDERS` (quem manda mensagem sem
  ser NPC), `celular.AGENDA_EXTRA`/`AGENDA_TODAY` (linhas da Agenda), `festas.CAL_EXTRA` (linhas do calendário),
  `noticias.EXTRA_EVENTS` (manchetes de eventos novos) e `scenetest.DYNAMIC` (cenas montadas na hora no `--cenas`).
  Projetos que precisam de flag usam `locked_flag` (o Terminal P&D só mostra a proposta com a flag).
- **Mar e natureza (natureza.py):** o mar troca os tiles "sea"/"sea_foam" (`draw_sea`: mais escuro longe da areia,
  cristas andando para a praia, brilhinhos; no pôr do sol reflete pêssego e lilás). Ondas sobem e voltam pela areia
  (`draw_shore`, o píer fica de fora). Depois da iluminação, `draw_glints` põe o caminho do sol (pôr do sol) e o
  luar (noite) no mar; chovendo, nada. Árvores e arbustos (`SWAY`) entortam a copa 1–2 px com rajadas que atravessam
  a cidade (mais na chuva/tempestade); `natureza.faded` é a copa translúcida no mesmo quadro. Tufinhos de grama
  (`draw_ground`) só ao ar livre e fora do inverno. Sem nuvens.
- **Atalhos:** I/Tab mochila, O objetivos, R relacionamentos, K conquistas, M mapa, C calendário (a mesma tecla fecha), P modo foto,
  T celular. Painéis longos usam
  `ui.InfoPanel(..., scroll=True)` (draw_fn devolve o y final) em vez de crescer.
- **Desmaio às 2h:** acorda no leito do hospital (`HOSPITAL_BED`) com conta.
- **Site:** roxo (#8a00e6 / #b84cff) como principal e verde (#6ee78c) como destaque. As capturas de conversa,
  cena e relacionamentos mostram os retratos de verdade (pedido da dona); a lista de personagens do site usa os
  bonequinhos em pixel art (docs/img/chars).

## Lore aprovada (ainda não está toda no jogo)

- **Letícia e Lucy:** as duas tiveram algo no passado, em Gotham. Durante a doença do pai da Letícia, **Alexander**,
  os **tios** dela ameaçaram a Lucy, e a Letícia foi embora sem explicar nada para protegê-la. Alexander morreu meses
  depois. Nada de apagão no jogo (a dona pediu para tirar tudo sobre isso). Eventos de coração:
  2 entrevista fria · 4 Lucy acha a data da morte do Alexander no arquivo da CatCo · 6 no píer, a Letícia fala do
  pai · 8 a verdade sobre os tios (a Lucy fica magoada porque a Letícia decidiu por ela) · 10 pacto na fonte:
  "ninguém decide pela outra, nada de segredos".
- **Letícia e Vittoria (história "normal", sem drama de família):** a Vittoria trabalhou anos em restaurantes dos
  outros, abriu a própria Trattoria, cresceu até o Gruppo Ricci e está inaugurando a sede. Não é chef. Eventos:
  2 a Letícia vira cliente fiel de fim de noite · 4 conversa depois de fechar · 6 a Letícia ajuda às 6h na
  inauguração · 8 primeira folga; a Vittoria tem medo de se apaixonar por alguém tão ocupada quanto ela ·
  10 praia: "Vamos ter uma vida, não só empresas".
- **No jogo:** as cenas da Lucy (lucy_1/2, 6, 8, 10) e da Vittoria escritas pela dona ficaram como estão; coracoes.py
  completou o que faltava: lucy_5 (arquivo da CatCo), vittoria_5 (inauguração às 6h) e vittoria_7 (o medo).
- **Dona Graça:** a dona prefere o retrato ilustrado (não pixel art) para ela.

## Migração para o Godot 4 (ABANDONADA)

**A dona testou a versão Godot, não gostou e prefere continuar no Python** (é mais fácil para ela mexer). Todo o
trabalho novo vai para o jogo Python. A pasta `godot/` e os exportadores em `tools/` ficaram só como registro;
não mexa neles sem ela pedir. O texto abaixo descreve como ficou a tentativa.

A dona decidiu migrar para o **Godot 4** (GDScript, versão padrão, não .NET) para ter um visual mais bonito, mais
animações e, depois, versão para **celular**. Regras:

- Fazer numa pasta nova **`godot/`**, sem mexer na versão Python, que continua jogável até o Godot alcançar.
- **Personagens ficam exatamente como estão hoje** (os bonequinhos de sprites.py e os retratos). A dona NÃO gostou
  de personagens redesenhados "caprichados" nem dos estilos 3D (HD-2D, voxel, low poly): continua 2D, estilo
  Stardew.
- **Ruas e prédios:** ela gostou da versão caprichada da cidade (calçadas de pedra, asfalto com faixas, prédios com
  mais detalhe, toldos, vasos, postes, luz dourada no fim da tarde). Seguir esse caminho.
- Aproveitar o que o Godot faz bem: Light2D (postes, vitrines, neon roxo da Luthor Corp, escurecer conforme o
  relógio), chuva/neve com partículas e shader de asfalto molhado, TileMap, animações (árvores, fumaça, letreiros,
  carros), câmera suave, navegação dos NPCs, exportação para web e celular (controles de toque).
- A arte é procedural no Python: exportar sprites, tiles e objetos para PNG com um script (`tools/`) e importar no
  Godot com filtro **Nearest** (pixel art nítida), em vez de redesenhar à mão.
- Dados (falas, presentes, rotinas, itens, cenas) devem virar arquivos de dados (JSON/Resources) lidos pelo Godot,
  sem reescrever o conteúdo à mão.
- Ordem das etapas, cada uma jogável antes da próxima:
  1. rua principal com a Letícia andando, câmera e colisões;
  2. relógio, dia/noite com luzes e clima;
  3. NPCs com rotinas, diálogos e presentes;
  4. interiores (café, CatCo, hospital, Marina...);
  5. sistemas (mochila, ações, objetivos, save);
  6. animações extras e versão para celular.

### Estado do Godot (as 6 etapas feitas + tudo o que faltava do Python)

O Godot 4.7.2 da dona fica em `C:\Users\letic\Downloads\Godot_v4.7.2-stable_win64.exe\` (use o `_console.exe`
para rodar pela linha de comando). Para abrir: no Godot, "Importar" → `godot/project.godot`.

```
tools/exportar_godot.py   py tools/exportar_godot.py: importa o jogo com SCALE=1 (arte em 16 px) e gera
                          godot/assets/gerado/ (tiles.png, chao_bordas.png, agua_bordas_*.png, objetos/,
                          predios/ dia e noite, personagens/leticia.png) e godot/data/cidade.json
godot/project.godot       1280x720, stretch canvas_items, filtro Nearest, renderizador Compatibility (web/celular)
godot/cenas/principal.tscn  Cidade + Jogadora (CharacterBody2D, Camera2D zoom 2) + HUD
godot/scripts/cidade.gd   monta QUALQUER mapa do JSON (a cidade ou um interior): TileMapLayer do chão (água animada),
                          bordas (com tapetes e decoração de parede já desenhados), sombras, objetos e prédios num
                          Node2D com y-sort, letreiros, colisões, `saidas` (portas) e `balcoes`; `ativar(false)`
                          esconde o mapa e tira as colisões da física (todos os mapas começam em 0,0)
data/mapas/<nome>.json    os 13 interiores (home, hq, cafe, catco, books, market, trattoria, bar, terrace, cinema,
                          hospital, ricci, marina), exportados por `exportar_interior`; arte em gerado/mapas/<nome>/.
                          O alto-mar (só de barco) ainda não foi para o Godot
godot/scripts/jogadora.gd correr é o padrão e Shift anda devagar (igual ao Python), escorregar nas quinas,
                          piscar e respirar
godot/scripts/relogio.gd  relógio (7 s = 10 min, 6h–2h), clima do dia (chance por estação), escuridão e pôr do
                          sol com as mesmas curvas do Python (Game.darkness / Game.sunset)
godot/scripts/ambiente.gd CanvasModulate (noite azulada, chuva acinzentada) + brilho dourado somado no pôr do sol;
                          PointLight2D nos postes, farol, portas, neon (Luthor Corp, Noonan's, cinema) e janelas
                          (textura = predios/<estilo>_luzes.png); luz fraca na Letícia; chuva (CPUParticles2D numa
                          CanvasLayer), chão molhado e reflexos das luzes no asfalto
godot/shaders/chao_molhado.gdshader  película d'água, brilho andando e pingos (máscara gerado/molhado.png)
tools/exportar_personagens.py  (chamado pelo exportador) data/personagens.json (rotinas, falas base + dialogue.LINES,
                          BUSY, gostos, reações, falas de "não gostei", eventos), data/itens.json + gerado/itens.png,
                          folhas de quadros em gerado/personagens/<chave>.png e retratos em assets/retratos/*.webp
godot/scripts/estado.gd   amizade, conversas/presentes do dia, falas já ditas, eventos, namoro e mochila
godot/scripts/npc.gd      NPC com rotina (port de entities.NPC): sai do interior pela porta, anda pela cidade, entra
                          no destino e anda até o lugar dele; só aparece no mapa em que a Letícia está (o nó vai
                          para o "Mundo" do mapa onde está). Médicas trocam para `sprite_hospital` no hospital
godot/scripts/personagens.gd  cria os NPCs, um AStarGrid2D por mapa (asfalto com peso 40: atravessam nas faixas),
                          conversa por cima do balcão (`balcoes`), rotina do dia
                          (default/weekend/rain; médicas: `por_dia`, 84 dias exportados e repetidos), conversa
                          (pick_line), presentes (rosas/pingente, gostos, retrato tímido/ruim) e eventos sem cena
godot/scripts/interface.gd  caixa de fala (retrato fora da caixa, reduzido com Lanczos para o tamanho da tela),
                          menu de escolhas e avisos (canto de cima à esquerda, como ui.Toasts)
godot/scripts/hud.gd      HUD IGUAL ao do Python (a dona não gostou do HUD antigo): quadro do relógio/clima/LCORP,
                          dinheiro, lugar, linhas de missões, energia vertical, barra de 12 itens e o aviso "E ..."
                          (`rotulo_alvo` = Game.target_label); fontes = tamanho do Python × 1,5
godot/scripts/video.gd    resolução (1280x720 a 3840x2160, padrão 1920x1080) e tela cheia, em user://config.cfg;
                          no menu do Esc e na tela de título. O jogo é montado em 1280x720 e ampliado (canvas_items)
godot/scripts/principal.gd  carrega todos os mapas, troca de mapa ao pisar numa porta (`trocar_mapa`, com cortina),
                          câmera 2x na cidade e 3x dentro (sala menor que a tela fica centralizada)
godot/scripts/sistemas.gd usar objetos (cama, bancadas, Terminal P&D, Mesa de Contratos, computador/ações, cafeteira,
                          banca, TV...), comer/ler (F), lojas (`abrir_loja`), mochila/relacionamentos/objetivos,
                          fim do dia (`fim_do_dia` -> `processar_noite` -> resumo -> manhã), desmaio às 2h (hospital),
                          save em user://save.json (`dados_save`/`aplicar_save`) e tela de título
godot/scripts/ui/         janelas empilháveis da Interface: Janela (base), PainelInfo (rolagem), Loja, Quantidade
                          (NumberPrompt), MochilaPainel (24 espaços, E pega/troca)
data/jogo.json            projetos, lojas, livros, objetivos, benefícios, descrições (FLAVOR), notícias, dicas,
                          constantes e o atlas das bancadas (gerado/bancadas.png), por `exportar_jogo`
godot/scripts/carros.gd   carros nas avenidas (faixas do Python), freiam quando a Letícia está na frente, farol à noite
godot/scripts/efeitos.gd  borboletas, pétalas (primavera) / folhas (outono), brilho na água e vagalumes (CanvasLayer
                          que segue a câmera, para brilharem no escuro); shaders/vento.gdshader balança as copas
godot/scripts/toque.gd    controles de toque (direcional + E, F, I, R, O, Esc) que só aparecem em telas de toque;
                          export_presets.cfg tem Windows, Web e Android (os modelos de exportação não estão instalados)
godot/scripts/cena.gd     motor das cutscenes (cutscenes.Cutscene): os 18 comandos, atores (ator_cena.gd), balões
                          (balao.gd), efeitos (efeitos_cena.gd), faixas pretas, legendas, fotos e Esc para pular
godot/scripts/historia.gd eventos de coração com cena no lugar/horário (linha rosa no HUD), abertura do jogo novo,
                          cena do namoro (rosas) e da mudança (pingente), convite e cena de encontro
data/cenas.json           as 22 cenas do Python + dados de romance (tools/exportar_personagens.exportar_cenas)
data/estacoes.json        o que muda por estação: chão da cidade/terraço, árvores, roupas de todos, mapa da cidade
                          (tools/exportar_estacoes.py); Sistemas.atualizar_estacao troca tudo; inverno = neve
godot/scripts/lazer.gd    pesca (linha, boia, "!", minigame ui/pesca_jogo.gd), aquário, fogão (ui/fogao.gd),
                          fliperama Meteoro (ui/meteoro.gd), coleções, rever cenas, controles e o menu de pausa (Esc)
godot/scripts/figurantes.gd  os 20 figurantes (crowd.py) reaproveitando o NPC; data/figurantes.json
godot/scripts/atividades.gd  coletáveis, horta do terraço, bichinho (bichinho.gd), espreguiçadeira, telescópio,
                          karaokê (ui/karaoke.gd), cinema (ui/filme.gd) e o céu do terraço; data/atividades.json
godot/scripts/hospital.gd consultas das 12 especialidades com o bônus do dia (estado.buffs), farmácia, lanches,
                          lideranças, doação trimestral e a placa da Ala Luthor
godot/scripts/marina.gd   encomendas do Ian, passeios (alto-mar, pôr do sol, regata em ui/regata.gd) e o timão
godot/scripts/som.gd      classe estática `Sons` (Sons.tocar("confirm")): os efeitos do audio.py exportados em WAV
                          (assets/sons); volume na pausa. Não é autoload: autoloads não existem quando os testes
                          (`--script`) compilam os scripts
ui/mapa_cidade.gd         mapa da cidade (M) com a posição de todos; o desenho vem do citymap._base de cada estação
godot/testes/*.gd         testes automáticos; `sh testes/rodar_todos.sh <Godot_console.exe>` roda todos
                          (o da etapa 4 também confere se todas as salas de cada interior são alcançáveis)
```

- **Arte nova ou mudada no Python → rode `py tools/exportar_godot.py` de novo** (e abra o Godot para reimportar).
  Não edite os PNGs de `godot/assets/gerado/` à mão: eles são sobrescritos.
- Coordenadas no Godot são em **pixels de arte** (tile = 16); a câmera amplia 2x na cidade (interiores: 3x, que é
  o 1,5x do Python). O nó da jogadora fica no ponto dos pés (`Player.y` do Python).
- Letreiros: Label com o tamanho de fonte de tela do Python e `scale = 0.5`, para ficar nítido com o zoom 2x.
- Controles registrados em código (`principal._registrar_controles`): setas/WASD, Shift, F11, D-pad e analógico.
  R relacionamentos, O objetivos, J missões (`Sistemas.abrir_missoes`), M mapa. Sem lista de teclas na tela.
- Exportação para celular/web/Windows: a dona disse que não precisa por enquanto.
- Testar: `<godot>_console.exe --path godot --script res://testes/teste_etapa1.gd` (abre uma janela por alguns
  segundos e imprime OK/FALHA). Só checar erros de script: `--headless --path godot --quit-after 120`.
- **Visual caprichado (só Godot):** `tools/arte_caprichada.py` troca, na hora de exportar, a calçada (pedras em
  amarração + meio-fio desenhado em `decorar_ruas`), o asfalto, as faixas, o poste (lanterna) e os prédios
  `tower`, `cafe` e `catco`, seguindo a imagem de referência da dona (fim de tarde / noite com Light2D / chuva).
  Enfeites só do Godot ficam em `EXTRAS_CIDADE` (mesinha do café, cavalete, vasos) e não podem tapar portas.
  Para caprichar outro prédio: função `_estilo(W, H, night)` em `NOVOS_PREDIOS` (porta alinhada ao tile da porta).
  O jogo Python continua com a arte antiga.
- Luzes no renderizador Compatibility: cada desenho recebe no máximo `max_lights_per_object` (16) luzes, por isso
  camadas grandes são cortadas em pedaços de 256 px (`Cidade._em_pedacos`). Prédios trocam para o desenho `_noite`
  com escuridão > 0,3; as luzes acendem a partir de 0,12. O chão molha rápido e seca devagar
  (`Ambiente.sincronizar()` pula a transição; chamado na virada do dia).
- Teclas de teste: `[` e `]` mudam a hora, F7 liga/desliga a chuva, F8 pausa o relógio, F9 põe presentes na mochila
  (o HUD mostra dia, hora, clima, dinheiro e energia). Jogo: E usa/conversa/confirma, F come/lê, I/Tab mochila,
  R relacionamentos, O objetivos, 1-9/0/-/= ou rodinha escolhem o item da barra.
- **Retratos no Godot:** WebP **sem perda**, na resolução original (mesmos pixels do PNG, quase metade do tamanho;
  a dona não quer retrato reduzido). O exportador só refaz um retrato quando o PNG muda. Na tela, a interface
  reduz com Lanczos para o tamanho real (como `art.portrait_hd`).
- Conversas e menus pausam o relógio e os NPCs (`Relogio.em_dialogo`), como no Stardew.
- **Save do Godot:** `user://save.json` (AppData do Godot), separado do save do Python. Campos novos sempre com valor
  padrão em `Estado.do_save` / `Sistemas.aplicar_save`. Grava ao dormir ou desmaiar, como no Python. Rodando pelos
  testes (`get_tree().get_script() != null`) não há tela de título nem save, e o jogo começa na rua.
- O relógio não vira mais o dia sozinho: às 2h emite `desmaio` e `Sistemas.fim_do_dia(true)` processa a noite.
  O clima de cada dia é o sorteado na véspera (`Relogio.clima_amanha`).
- Números que vêm do JSON chegam como float no GDScript: compare com `int(...)` (ex.: trimestres das propostas).
- Interiores: a noite escurece bem menos (véu 70/190 do Python; terraço 150/190), sem chuva, sem luz dourada e sem a
  luz da Letícia. As bancadas mudam de desenho pelo atlas gerado/bancadas.png.
- Cutscenes: durante a cena `Interface.bloqueio` para o jogo, os NPCs de verdade somem (`Personagens.ocultar_todos`)
  e a cena usa atores e câmera próprios; o Ambiente usa `hora_forcada`/`clima_forcado`. Nos testes as cenas de
  evento não disparam sozinhas (`Sistemas.modo_teste_sem_cenas`).
- Bônus das consultas (estado.buffs, valem até a noite): cardiologia (velocidade), neurologia (bancada), ortopedia
  (pesca), pediatria (bichinho), oncologia, ginecologia (presentes), gastro (comida), endocrino (pratos), dermato
  (karaokê), urologia (desmaio grátis), oftalmo (coletáveis), psiquiatria (conversas).
- Falas reativas: o texto vem de data/reativas.json e as condições foram reescritas em
  `Personagens._condicao_reativa`, na mesma ordem de `dialogue.REACTIVE`. **Fala reativa nova no Python = nova
  condição no GDScript.**
- Ainda não foram para o Godot: os outros prédios no estilo caprichado. Músicas e passos ficam de fora (pedido da dona).

## Como testar

Para ver uma cutscene sem progresso: `python main.py --cenas` (lista, F5 reabre) ou `python main.py --cena lucy_6`.
Nesse modo `Game.save` é desligado. Títulos da lista vêm de `Game.scene_title`.
O casamento também está na lista, uma versão por noiva: `--cena casamento_lucy`, `casamento_vittoria`,
`casamento_pedido_lucy` e `casamento_pedido_vittoria` (montadas na hora por `casamento.wedding_scene`/`proposal_scene`).
Para testar outro dia/horário/estação/clima: `python main.py --teste` (abre o save sem gravar; F6 abre o painel,
que também funciona no modo `--cenas`; dá para parar o relógio e mudar os corações com cada personagem).

Não há suíte de testes no repositório. Para checar sem abrir janela, rode o jogo em modo headless:

```python
import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
from luthor.game import Game
g = Game()
g.step(1/60, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])  # título: Enter = "Continuar" se houver save, senão "Novo jogo"
for _ in range(600): g.step(1/60, [])
pygame.image.save(g.screen, "shot.png")                                  # captura de tela
```

Dicas: cutscenes ficam em `g.modals` (chame `.finish()` para pular); para simular teclas seguradas,
substitua `pygame.key.get_pressed`. Antes de entregar uma mudança, rode alguns dias simulados
(`g.end_day()`), salve e carregue (`g.save(); g.load()`) e confira capturas de tela.

## Histórico resumido

1. Jogo base: laboratório, cidade, amizades, pesca.
2. Romances Lucy e Vittoria, tela cheia (F11), minigames, mapa maior, novos lugares.
3. Cutscenes e gráficos mais caprichados.
4. Personagens magras, câmera afastada, falas por período sem repetição, horta, coletáveis, pet, karaokê, cinema.
5. Conti Moretti Hospitais, ações com quantidade livre, figurantes, médicas como personagens completas.
6. Site em `docs/` e README novo para o GitHub.
7. Cidade ampliada (Bosque Bayside, Jardim do Mirante, farol), cenário estilo Stardew e colisão mais suave.
8. Calçadão reorganizado (portas alinhadas ao desenho, bancos de lado), mar maior e personagens estilo Stardew.
9. Sede do Gruppo Ricci no lugar do banco; Vittoria vira dona da rede e a Dona Graça assume a cozinha da Trattoria.
10. Retratos em pixel art com 4 humores, Rafa vira Harry, Barry e Ian, Marina Luthor (alto-mar, pôr do sol, regata,
    encomendas), bonequinhos de acordo com os retratos e NPCs fora da rua.
11. Lexie sai do jogo; médicas e todas as cenas juntas (characters.py / cutscenes.py); retratos novos das médicas
    sem dra_; 14 presentes e 4 coletáveis novos; coletáveis odiados por algumas personagens. Bonequinhos ajustados
    aos retratos novos (`LOOK_UPDATES_2` no fim de characters.py; Letícia em `entities.PLAYER_LOOK`).
12. Médicas com roupa de hospital e roupa de fora; jaqueta de couro (Lucy) e casaco de capitão (Ian);
    cabelos soltos para todas.
13. Retratos nítidos na tela cheia (redesenhados na resolução do monitor) e sem esticar na caixa de fala.
14. Rosto mais à mostra (franja aberta), alturas e ombros diferentes por personagem; figurantes variados.
15. Som: efeitos gerados por código, com volume no menu de pausa (músicas e passos testados e retirados).
16. Estações: cenário, efeitos (pétalas, folhas, neve), coletáveis e roupas de todos mudam a cada trimestre.
17. Decisão de migrar para o Godot 4 (depois abandonada) (pasta `godot/`) e lore aprovada da Lucy e da Vittoria.
18. Godot, etapa 1: exportador `tools/exportar_godot.py`, cidade inteira no Godot com a Letícia andando, câmera
    suave e colisões iguais às do Python. Visual caprichado das ruas e de 3 prédios (`tools/arte_caprichada.py`).
19. Godot, etapa 2: relógio, dia/noite com Light2D (postes, janelas, vitrines, neon), pôr do sol dourado, chuva
    com partículas, chão molhado e reflexos.
20. Godot, etapa 3: os 19 personagens com rotina pela cidade, caixa de fala com retrato, amizade, presentes,
    eventos sem cena e barra de itens.
21. Godot, etapa 4: os 13 interiores com portas, câmera 3x, NPCs entrando, andando e saindo dos prédios, conversa
    por cima do balcão e médicas de jaleco no hospital. Correr virou o padrão (Shift anda devagar).
22. Godot, etapa 5: HUD de dinheiro/energia, laboratório, Terminal P&D, Mesa de Contratos, ações LCORP, lojas,
    comer/ler, mochila, relacionamentos, objetivos, dormir/desmaiar com resumo da noite, save e tela de título.
23. Godot, etapa 6 e o resto do jogo: carros, vento, borboletas, vagalumes, fumaça, controles de toque e
    exportação; cutscenes e eventos de coração, namoro, mudança e encontros; estações e neve; pesca, aquário,
    fogão, Meteoro, pausa e coleções; figurantes, pedidos, e-mails e mapa (M); horta, coletáveis, bichinho,
    karaokê e cinema; hospital (consultas e bônus) e Marina (encomendas, alto-mar, pôr do sol, regata); sons.
24. Godot: HUD igual ao do Python (hud.gd), painel de missões (J) e opção de resolução (padrão 1920x1080).
25. A dona desistiu do Godot e voltou para o Python. Iluminação nova (`lighting.py`: mapa de luz com postes,
    janelas, portas, faróis e pôr do sol dourado) e carros que freiam para pessoas e para o carro da frente.
26. Luz dentro dos prédios (luz de teto, cantos mais escuros, objetos que brilham, clima de cada lugar) e cidade
    caprichada (`caprichado.py`): calçadas de pedra, meio-fio, asfalto, os 13 prédios redesenhados, sombras, mesinhas,
    lousas, floreiras, pombos, árvores mais cheias e grama com folhinhas.
27. Estações de 14 dias (saves antigos convertidos), caixa de escolhas no pé da tela, emotes em emoji,
    pedido de namoro marcado com beijo animado nas cenas, sentar nas cadeiras e bônus das cenas da Sam e da Vittoria.
28. Bônus do Ian, da Milany, do Brainy e da Jess (cena nova `jess_5`), beijo na `lucy_10` e emotes mais variados nas cenas.
29. Festas das estações (flores, luau, feira, luzes), aniversários com calendário (C), vida a dois depois do pingente
    (café da manhã, pedidos, aniversário de namoro) e ciúmes leves entre a Lucy e a Vittoria.
30. Tempestade e arco-íris, sinuca/dardos/xadrez, closet, decoração da cobertura, álbum do Barry, Fundação Luthor,
    momentos entre personagens, cenas e bônus para quem não tinha, casamento e a história da Luthor Corp (os tios e o
    conselho). Site atualizado com as novidades.
31. Animações novas (poses.py): sentar de verdade (desliza, pernas dobradas, balança os pés), NPCs e figurantes
    sentados nas cadeiras, comer/beber/ler com o item nas mãos, mordidas, goles, páginas virando e carinha feliz.
32. Mais animações (animacoes.py): beijo novo (abraço, ponta dos pés), NPCs comendo e bebendo nas mesas, brindes com
    cerveja/caipirinha/vinho nas cenas de bar, regar, bancada, vara de pesca, deitar na cama, guarda-chuva, aceno,
    bichinho no colo, gaivotas, gatinho de rua e modo foto. Sobretudo da Vittoria do tamanho do blazer.
33. Braços erguidos em Y com o peixe flutuando acima da cabeça, beijo refeito (de mãos dadas, narizes se tocando,
    bochechas coradas depois) e bebidas em copinhos pequenos que não tapam mais o rosto.
34. Três espaços de jogo salvo, 36 conquistas (K), interiores caprichados (paredes de 2 tiles com papel de parede e
    lambri, chão com textura, sombra dos móveis, quadros e arandelas), mar com ondas na areia e reflexos do pôr do
    sol e do luar, árvores e grama ao vento, e menus/HUD com moldura em pixel art.
35. Sofás, poltronas e cadeiras virados para o lugar certo (TV, mesa, mesinha de centro, tela do cinema), com
    desenhos de costas e de lado; encosto e braço por cima de quem senta; bichinho no encosto do sofá.
36. Escritório da Letícia caprichado (escritorio.py) e a mesa do conselho saiu do saguão; a sede ficou mais larga
    (34 tiles) com uma sala de reuniões própria, onde acontece a reunião do conselho (historia_5) com todos sentados
    (comando "sentar"). Gruppo Ricci remodelado: escritório novo da Vittoria e sala de projetos no lugar da cozinha de
    testes. Salinha da Sam embaixo da sala de reuniões. Sofás encostados na parede de baixo viram de costas para a sala.
37. La Boutique com a Celeste Waite (personagem nova com rotina, falas, presentes e eventos): roupas novas,
    acessórios que a Letícia usa (óculos, chapéus, brincos, colares, lenço, bolsas) e que podem ser presenteados,
    provador virtual na loja e provador de verdade dentro dela. Barra de energia voltou ao desenho simples.
    Amizades travadas em 8 corações (só Lucy e Vittoria chegam a 10), letreiros da Luthor Corp e da CatCo
    centralizados e a CatCo com 9 tiles para a porta ficar no meio.
38. Celular da Letícia (T) com mensagens, agenda, tempo, bolsa, fotos, pedidos e habilidades; desfile da Celeste no píer
    (8 corações); quadro de pedidos no Grão Nobre; habilidades com níveis (pesca, ciência, culinária, carisma) e mural
    de fotos na cobertura.
39. Fachadas novas do Noonan's (pub verde com letreiro dourado), do Cine National e dos Apartamentos Bayside (com nome),
    letreiros e portas centralizados; banca de jornais entre o Gruppo Ricci e o hospital; tapete no eixo da porta e da
    recepção da sede; mais de 300 falas novas (falas.py); respostas do celular que combinam com cada mensagem; o
    apagão saiu do jogo.
40. 10 peixes novos (8 no mar/lago e 2 no alto-mar) e aquário em grupos com rolagem; 9 e 10 corações só namorando;
    momentos pedem corações com as duas; quadro de pedidos começa com 1 espaço; CatCo com estúdio de TV (entrevistas e
    anúncio), arquivo e redatores trabalhando; monitores de costas nas mesas; sala de vinhos do Ricci; pacientes no
    Conti Moretti; portarias e saguão da sede mobiliados, com porteiros; alcance maior para conversar.
41. Notícias da CatCo que reagem ao que a Letícia faz (banca, TV, e-mails, arquivo, falas), degustação de vinhos com a
    Vittoria na adega do Ricci, voluntariado na brinquedoteca da pediatria (crianças menores), 3 medalhas novas e a
    Andrea Rojas como amiga da Letícia.
42. Aniversário surpresa da Letícia no terraço, visitas e mensagens da Andrea Rojas, primeira coleção da Celeste,
    eventos da Lucy e da Vittoria que faltavam na lore, encontros especiais (piquenique, veleiro, cinema e jantar),
    clube do livro do Theo, corrida com a Sam, melhorias do laboratório, 7 medalhas novas (46) e site atualizado.
43. Wiki do jogo em docs/wiki (gerar_wiki.py): uma página por personagem e por item, peixes, receitas, calendário,
    festas, lojas, lugares, laboratório, Fundação, hospital, habilidades e conquistas, com busca e tema claro/escuro.
    Retratos da Celeste e da Andrea Rojas (cenas, celular, site e wiki).
