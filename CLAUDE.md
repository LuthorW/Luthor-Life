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
luthor/
  config.py      SCALE=2, TS=16, TILE=32, tela 1280x720, tempo (7s reais = 10 min), cores C_*
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
  hospital.py    Conti Moretti: especialidades, consultas, bônus do dia, farmácia, doação
  crowd.py       figurantes (moradores sem conversa) que circulam pela cidade
  activities.py  horta do terraço, coletáveis, bichinho, karaokê, cinema, céu do terraço
  cutscenes.py   motor de cutscenes (comandos em tuplas) e TODAS as cenas (as do Ian, Barry e Dona Graça no fim)
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
  ui.py          fonte, painéis, Dialog, Choice, Shop, InfoPanel, NumberPrompt, Toasts, HUD
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
  porta de `world.Building`), letreiro em `caprichado.draw_label`. Vidro aceso SEMPRE com `caprichado.LIT`
  (252, 222, 136): é por essa cor que `lighting.py` faz as janelas brilharem. Use as peças `window`, `awning`,
  `bricks`, `cornice`, `door`, `shopfront`, `vaso`, `lantern`, `_arched`. Todos os 13 prédios da cidade já estão
  no estilo novo (os desenhos antigos em art.py, scenery.py e nautical.py ficaram, mas não são mais usados).
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

## Sistemas e regras de design (pedidos da dona)

- **Visual:** personagens no estilo Stardew (sprites.py), mas magrinhas (16x32), a Letícia tem **olhos verdes**,
  **nada de cabelo preso** (sem coque: só soltos, curtos ou black power), sem nuvens no céu,
  cabelo sem cobrir o rosto (franja aberta no meio, mechas por fora das bochechas), e corpos diferentes como no
  Stardew: `look["height"]` (-2..+2 px, cresce para cima; entre elas, só Letícia, Sam e Addison são mais altas) e `look["broad"]` (ombros largos), em `characters.BODY`,
  câmera afastada. Gráficos "bonitinhos".
- **Conversas:** muitas falas e nada de repetição (`lines_seen` guarda as já ditas). Cada personagem conversa
  **uma vez por período** (manhã 6–12h, tarde 12–18h, noite 18–2h); depois disso aparece a fala BUSY e
  um balão "...". Presentes, loja e convites continuam liberados.
- **Figurantes (crowd.py):** não conversam (E mostra o que estão fazendo). Chegam pela rua, entram num lugar,
  ficam um tempo e **sempre saem**. Nunca repetem um dos últimos lugares visitados, nem de um dia para o outro.
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
- **Romance:** Lucy Williams (repórter da CatCo, Brie Larson) e Vittoria Ricci (Adria Arjona), dona do Gruppo Ricci,
  rede de restaurantes com sede em National City (o prédio que antes era o banco). Ela **não é chef**: quem cozinha
  e cuida da loja da Ricci Trattoria é a Dona Graça, chef brasileira veterana.
- **Harry** (antes Rafa) é o barista do Grão Nobre. **Barry Allen**: fotógrafo da CatCo, amigo da Nia e da Lucy.
  **Ian**: diretor da Marina Luthor, a divisão náutica da Luthor Corp. É **funcionário da Letícia** (como a Sam e o
  Brainy), não sócio, e amigo de infância das férias no interior.
  Rosas aos 8 corações → namoro; pingente aos 10 → morar junto. Cutscenes nos eventos de coração.
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
- **Atalhos:** I/Tab mochila, O objetivos, R relacionamentos, M mapa (a mesma tecla fecha). Painéis longos usam
  `ui.InfoPanel(..., scroll=True)` (draw_fn devolve o y final) em vez de crescer.
- **Desmaio às 2h:** acorda no leito do hospital (`HOSPITAL_BED`) com conta.
- **Site:** roxo (#8a00e6 / #b84cff) como principal e verde (#6ee78c) como destaque. As capturas de conversa,
  cena e relacionamentos mostram os retratos de verdade (pedido da dona); a lista de personagens do site usa os
  bonequinhos em pixel art (docs/img/chars).

## Lore aprovada (ainda não está toda no jogo)

- **Letícia e Lucy:** as duas tiveram algo no passado, em Gotham. Durante a doença do pai da Letícia, **Alexander**,
  os **tios** dela ameaçaram a Lucy, e a Letícia foi embora sem explicar nada para protegê-la. Alexander morreu meses
  depois. Nada de apagão nessa história. Eventos de coração:
  2 entrevista fria · 4 Lucy acha a data da morte do Alexander no arquivo da CatCo · 6 no píer, a Letícia fala do
  pai · 8 a verdade sobre os tios (a Lucy fica magoada porque a Letícia decidiu por ela) · 10 pacto na fonte:
  "ninguém decide pela outra, nada de segredos".
- **Letícia e Vittoria (história "normal", sem drama de família):** a Vittoria trabalhou anos em restaurantes dos
  outros, abriu a própria Trattoria, cresceu até o Gruppo Ricci e está inaugurando a sede. Não é chef. Eventos:
  2 a Letícia vira cliente fiel de fim de noite · 4 conversa depois de fechar · 6 a Letícia ajuda às 6h na
  inauguração · 8 primeira folga; a Vittoria tem medo de se apaixonar por alguém tão ocupada quanto ela ·
  10 praia: "Vamos ter uma vida, não só empresas".
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
Para testar outro dia/horário/estação/clima: `python main.py --teste` (abre o save sem gravar; F6 abre o painel,
que também funciona no modo `--cenas`; dá para parar o relógio).

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
