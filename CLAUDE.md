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
  scenetest.py   modo de teste de cenas: `python main.py --cenas` / `--cena chave` (não salva nada)
  minigames.py   pesca, fliperama Meteoro, fogão, mochila
  effects.py     borboletas, vagalumes, pétalas, brilho na água, luz de janela
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
  sprites ganharam `scarf` (cachecol) e `sleeves="short"`. No inverno a "chuva" vira neve.
- **Som:** `audio.sfx(nome)` para efeitos (conversa, menus, lojas, itens, coração, pesca...). A dona NÃO gostou
  das músicas geradas: desligadas (`audio.MUSIC_ENABLED = False`). Passos também saíram (testados duas vezes; `audio.STEPS_ENABLED = False`): não colocar de novo sem ela pedir.
  Volume dos efeitos no menu de pausa (settings `sfx`).
- **Atalhos:** I/Tab mochila, O objetivos, R relacionamentos (a mesma tecla fecha). Painéis longos usam
  `ui.InfoPanel(..., scroll=True)` (draw_fn devolve o y final) em vez de crescer.
- **Desmaio às 2h:** acorda no leito do hospital (`HOSPITAL_BED`) com conta.
- **Site:** roxo (#8a00e6 / #b84cff) como principal e verde (#6ee78c) como destaque. As capturas de conversa,
  cena e relacionamentos mostram os retratos de verdade (pedido da dona); a lista de personagens do site usa os
  bonequinhos em pixel art (docs/img/chars).

## Como testar

Para ver uma cutscene sem progresso: `python main.py --cenas` (lista, F5 reabre) ou `python main.py --cena lucy_6`.
Nesse modo `Game.save` é desligado. Títulos da lista vêm de `Game.scene_title`.

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
