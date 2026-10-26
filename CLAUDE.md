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
assets/portraits/    fotos dos retratos (lucy*.jpg, sam.jpg, brainy.jpg, dra_*.jpg...)
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
                 (shirt, blazer, coat, chef, apron, vest, cardigan, fisher, blouse); substitui art._frames
  scenery.py     cenário estilo Stardew: árvores grandes (copa some atrás), grama/terra, cantos e enfeites do chão
  entities.py    Player, NPC (rotina e caminho entre mapas), Car
  characters.py  NPCS (aparência, rotina, falas base, presentes, reações, eventos), NPC_ORDER, TEAM, ROMANCES
  dialogue.py    LINES por período/clima/lugar/amizade, REACTIVE (falas condicionais), BUSY
  doctors.py     as 6 médicas como NPCs completas + rotina diária gerada (schedule_for)
  hospital.py    Conti Moretti: especialidades, consultas, bônus do dia, farmácia, doação
  crowd.py       figurantes (moradores sem conversa) que circulam pela cidade
  activities.py  horta do terraço, coletáveis, bichinho, karaokê, cinema, céu do terraço
  cutscenes.py   motor de cutscenes (comandos em tuplas) e as cenas
  minigames.py   pesca, fliperama Meteoro, fogão, mochila
  effects.py     borboletas, vagalumes, pétalas, brilho na água, luz de janela
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

- **Visual:** personagens no estilo Stardew (sprites.py), mas magrinhas (16x32), a Letícia tem **olhos verdes**, sem nuvens no céu,
  câmera afastada. Gráficos "bonitinhos".
- **Conversas:** muitas falas e nada de repetição (`lines_seen` guarda as já ditas). Cada personagem conversa
  **uma vez por período** (manhã 6–12h, tarde 12–18h, noite 18–2h); depois disso aparece a fala BUSY e
  um balão "...". Presentes, loja e convites continuam liberados.
- **Figurantes (crowd.py):** não conversam (E mostra o que estão fazendo). Chegam pela rua, entram num lugar,
  ficam um tempo e **sempre saem**. Nunca repetem um dos últimos lugares visitados, nem de um dia para o outro.
- **Médicas (doctors.py):** conversáveis e presenteáveis. Plantão alternando postos sem repetir em sequência,
  nunca duas no mesmo lugar, almoço em lugar diferente a cada dia, 2 folgas por semana.
  Benefícios de 3 corações: Milany (consulta pela metade), Meredith (hospital grátis se desmaiar),
  Cristina (contrato de $200 às segundas), Lexie (trabalho gasta menos energia), Izzie e Addison (presentes).
- **Conti Moretti Hospitais** segue o site do projeto `CMHospitais` (pasta irmã): 12 especialidades,
  lideranças clínicas, cores verde #123f35, cobre #b77b65, papel #fbfaf8. Consulta: energia cheia + bônus do dia.
- **Romance:** Lucy Williams (repórter da CatCo, Brie Larson) e Vittoria Ricci (chef, Adria Arjona).
  Rosas aos 8 corações → namoro; pingente aos 10 → morar junto. Cutscenes nos eventos de coração.
- **Ações LCORP:** variação noturna = aleatório + vendas de produtos/800 + bônus (Nia, doação).
  Compra e venda com quantidade livre (`ui.NumberPrompt`) e "Vender todas".
- **Desmaio às 2h:** acorda no leito do hospital (`HOSPITAL_BED`) com conta.
- **Site:** roxo (#8a00e6 / #b84cff) como principal e verde (#6ee78c) como destaque. No site use só os sprites
  em pixel art, não as fotos reais dos retratos.

## Como testar

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
