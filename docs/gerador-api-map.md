# Mapa da API interna — Gerador PRO

- **Alvo:** `https://gerador.pro`
- **Data da captura:** 2026-11-22 (UTC)
- **Método:** navegador real, `fetch`/XHR embrulhados, DOM e respostas reais
- **Conta:** revenda (credenciais não registradas)
- **Natureza:** observado, não é contrato oficial

## Convenções

- `<panel>` = `https://gerador.pro`
- `<user_id>` = id interno da conta (não versionado)
- `<csrf>` = token CSRF da página atual
- `<xt_token>` = token da tela Xtream (também chamado de `csrf` no corpo)
- `<tmdb_id>` = id numérico do TMDB
- `<hash>` = hash hexadecimal de 32 caracteres
- `→` = resposta observada
- `[código]` = comportamento lido no JavaScript da página, sem resposta real

---

## 1. Autenticação

### `GET /login.php`

Formulário clássico, sem CSRF.

```html
<form id="login-form" method="POST" action="login.php">
  <input name="username" type="text" required>
  <input name="password" type="password" required>
  <button type="submit">Entrar</button>
</form>
```

`GET /index.php` sem sessão redireciona para `/login.php`.

### `POST /login.php`

`application/x-www-form-urlencoded`

```text
username=<usuario>&password=<senha>
```

Resposta observada:

```http
HTTP/1.1 302 Found
Location: index.php
Set-Cookie: PHPSESSID=...
```

Depois do login, `GET /index.php` → `200` com o dashboard.

### `GET /logout.php`

Encerra a sessão. Não foi executado na sessão principal (evita derrubar o
portal). O link existe no menu e aponta para `logout.php`.

### Sessão

- Cookie: `PHPSESSID` (HttpOnly conforme o navegador; o valor não é exposto).
- Não há token Bearer.
- As chamadas seguintes usam a mesma origem e o cookie de sessão.
- Se a sessão expirar, a resposta é um redirecionamento para o login; o JS das
  telas checa `response.redirected`.

---

## 2. Dashboard

### `GET /index.php`

HTML server-rendered. Não foi encontrado endpoint JSON do dashboard.

- Mostra o nome da conta, vencimento do plano e os cards de atalho.
- Cards: Banner Futebol, Central de Notícias, Notícias Filmes-Séries, Gerador de
  Vídeo, Banner Filmes, Banner Séries/Novelas, Logo, Canal Telegram, Sair.
- O dashboard também exibe um pop-up de vencimento e um aviso de logo ausente.

### API oficial

Testado em 2026-11-22:

| Caminho | Resultado |
|---|---|
| `/openapi.json` | 404 HTML |
| `/swagger.json` | 404 HTML |
| `/api-docs` | 404 HTML |
| `/docs` | 404 HTML |
| `/redoc` | 404 HTML |
| `/llms.txt` | 404 HTML |
| `/api` | 403 nginx |
| `/api/docs` | 404 HTML |

**Conclusão:** não há API oficial publicada; o mapa abaixo é a API interna do
painel.

---

## 3. Notícias esportivas → banners

Base: `/futebol/noticias-gerar.php`

### `GET ?action=feed`

→ `200 application/json`

```json
{
  "items": [
    {
      "id": "<sha256>",
      "title": "string",
      "summary": "string",
      "link": "https://...",
      "date": "Sun, 22 Nov 2026 23:07:39 -0000",
      "national": false,
      "source": "ge",
      "topic": "",
      "category": "FUTEBOL BRASILEIRO",
      "group": "futebol"
    }
  ],
  "limit": 10
}
```

Observado: **538 itens** no feed; `limit` veio `10`, mas o array não foi cortado
pelo servidor. A UI renderiza em blocos de 24 e permite selecionar até 10.

Grupos usados pela UI: `all`, `futebol`, `f1`, `basquete`, `volei`, `lutas`,
`outros`.

### `GET ?action=logo`

- Com logo cadastrada → `200 image/png`.
- Sem logo → `400 application/json`:

```json
{"error":"Cadastre sua logo no Gerador Pro antes de gerar as notícias."}
```

### `GET ?action=thumb&id=<id>`

→ imagem do card (JPEG/PNG). Sem cache público relevante.

### `POST ?action=create`

`Content-Type: application/json`

```json
{
  "ids": ["<sha256>"],
  "color": "azul",
  "whatsapp": "",
  "csrf": "<csrf>"
}
```

Cores observadas no JS: `azul`, `vermelho`, `verde`, `cinza`, `roxo`, `amarelo`.

→ `200 application/json`

```json
{
  "id": "<job_id>",
  "created": 1795390767,
  "color": "azul",
  "whatsapp": "",
  "next": 0,
  "total": 1,
  "articles": [
    {
      "id": "<sha256>",
      "title": "string",
      "summary": "string",
      "link": "https://...",
      "date": "Sun, 22 Nov 2026 23:28:10 -0000",
      "national": false,
      "source": "ge",
      "topic": "",
      "category": "BRASILEIRÃO SÉRIE B",
      "state": "pending"
    }
  ]
}
```

Limite: **até 10 ids** por lote (validação no JS).

### `POST ?action=step`

```json
{"job": "<job_id>", "index": 0, "csrf": "<csrf>"}
```

→ `200` com o job atualizado. Observado:

- `next` passou de `0` para `1`;
- `articles[0].state` passou de `pending` para `done`;
- `gallery_url` = `/futebol/cartazes/`;
- `published` = timestamp Unix.

Tempo observado: **605 ms** para 1 notícia.

### `GET ?action=status&job=<job_id>` [código]

Usado pelo botão “Continuar geração” quando a conexão cai. Devolve o job.

### `POST ?action=contact` [código]

`application/json`

```json
{"remember": true, "whatsapp": "<numero>", "csrf": "<csrf>"}
```

Salva o WhatsApp para as próximas visitas. Não executado.

### Limpeza e galeria

```http
GET /futebol/cartazes/clean_images.php?user_id=<user_id>
```

→ `200`

```json
{"status":"success","message":"Limpeza concluída.","deleted_count":10}
```

A galeria fica em `GET /futebol/cartazes/` e lista imagens como:

```text
/futebol/cartazes/user_<user_id>/hoje/jogos_DD-MM-AAAA_page_1.png
/futebol/cartazes/user_<user_id>/banner_1.png
```

O fluxo de geração chama `clean_images.php` **antes** de cada lote; isso apaga
as imagens anteriores da conta. Use com cuidado.

---

## 4. Filmes/Séries → banners

Base: `/futebol/filmes-series-gerar.php`

Mesmo contrato das notícias, com diferenças:

### `GET ?action=feed`

→ `200`

```json
{
  "items": [
    {
      "id": "<sha256>",
      "title": "string",
      "summary": "string",
      "link": "https://...",
      "date": "2026-11-22T18:30:00-03:00",
      "national": true,
      "source": "AdoroCinema",
      "topic": "FILMES",
      "category": "FILMES",
      "group": "filmes"
    }
  ],
  "limit": 10
}
```

Observado: **42 itens**. Grupos: `all`, `filmes`, `series`, `streaming`,
`outros`. Cores iguais às das notícias. Limite de 10 por lote.

### `GET ?action=logo`

Mesmo comportamento: `200 image/png` ou `400` com o erro de logo.

### `POST ?action=create` / `?action=step` / `?action=status`

Mesmo shape das notícias, trocando a base. Observado: `create` + `step` em
**724 ms**, `state: "done"`, `gallery_url: "/futebol/cartazes/"`.

---

## 5. Banners esportivos

Páginas:

| Página | Modelos exibidos |
|---|---|
| `/futbanner.php` | 22 cards de futebol |
| `/nba.php` | 15 cards de basquete |
| `/nfl.php` | 6 cards de NFL |
| `/ufc.php` | 6 cards de UFC |
| `/esportes.php` | 7 cards de esportes gerais |
| `/formula1.php` | 7 cards de F1 |

Cada card aponta para:

```text
/futbanner.php?page=futebol&modelo=<modelo>
```

Exemplos: `?page=futebol&modelo=1`, `?page=futebol&modelo=nba2blue`,
`?page=futebol&modelo=f1amarelo`.

### Formulário de geração

Na página com modelo selecionado:

```html
<form id="generationForm" method="POST" target="form-response"
      action="futebol/<script>.php">
  <input type="hidden" name="text_color" value="#FFFFFF">
  <input type="hidden" name="highlight_color" value="#FFD700">
  <input type="hidden" name="card_background_color" value="#000000">
  <input type="text" name="whatsapp_number" value="">
  <input type="hidden" name="json_data" value="[...]">
  <button type="submit" id="generateButton">Gerar</button>
</form>
```

- `json_data` é o JSON dos jogos (a página já injeta).
- `whatsapp_number` é opcional.
- O submit vai para `futebol/<script>.php` em um iframe.
- Antes do submit, o JS chama
  `GET /futebol/cartazes/clean_images.php?user_id=<user_id>`.

### `POST /futebol/<script>.php`

`multipart/form-data` com os campos acima.

→ `200` e imagens em:

```text
/futebol/cartazes/user_<user_id>/hoje/jogos_DD-MM-AAAA_page_N.png
/futebol/cartazes/user_<user_id>/amanha/jogos_DD-MM-AAAA_page_N.png
```

Observado: modelo 1 gerou **8 páginas de hoje + 2 de amanhã**. O iframe aponta
para a URL do diretório e o nginx responde **403** na listagem, mas as imagens
existem e aparecem na galeria.

### Catálogo de modelos

```http
GET /lote.php?acao=catalogo_modelos
```

→ `200`

```json
{
  "ok": true,
  "modelos": [
    {
      "id": "1",
      "script": "modelo1.php",
      "nome": "Modelo 1",
      "preview": "futebol/modelo-1.jpg",
      "categoria": "futebol"
    }
  ]
}
```

Observado: **114 modelos** — 92 `futebol`, 15 `basquete`, 7 `esportes`.
O mesmo catálogo alimenta os cards do Robô Automático.

### Lote (“Gerar Express”)

`[código]` em `/lote.php`:

1. `GET /futebol/cartazes/rename_images.php?acao=limpar`
2. Para cada modelo selecionado:
   - `POST /futebol/<script>.php` com `whatsapp_number` e `json_data`;
   - `GET /futebol/cartazes/rename_images.php?categoria=<FUT|BASQ|TODOS>&ordem=<n>`
3. Redireciona para `/futebol/cartazes/`.

Favoritos:

```http
POST /save_favs.php
Content-Type: multipart/form-data

user_id=<user_id>&favoritos=[{"id":"1","script":"modelo1.php"}]
```

Não executado para não sobrescrever favoritos existentes.

---

## 6. Banner de filme/série (TMDB → SVG → PNG)

### Busca

```http
GET /1banners-filmes-series.php?query=<titulo>&type=movie
GET /1banners-filmes-series.php?query=<titulo>&type=tv
```

→ `200` HTML com resultados. Cada card chama:

```js
selectItem('<query>', 'movie', <tmdb_id>, '&action=select_style')
```

e navega para:

```text
/1banners-filmes-series.php?query=<query>&type=movie&id=<tmdb_id>&action=select_style
```

### Escolha de modelo e tema

A página de estilo tem 10 modelos (`data-model` 1–10) e 9 temas
(`data-theme`): `vermelho`, `azul`, `verde`, `roxo`, `cinza`, `rosa`,
`dourado`, `laranja`, `ciano`.

O botão “Gerar banner” navega para:

```text
/1banners-filmes-series.php?query=<query>&type=movie&id=<tmdb_id>&cast=1&model=<1-10>&theme=<tema>
```

Para o modelo 10, o destino é:

```text
/1banners-filmes-series-PANFLETO-APP.php?query=...&type=movie&id=...&cast=1&model=7&theme=...
```

### Página “Banner pronto”

→ `200` HTML com variáveis:

```js
const svgBannerPath = "model2/<hash>.svg";
const pngBannerPath = "model2/<hash>.png";
const bannerHash = "<hash>";
const downloadName = "banner_<titulo>_modelo<N>_<tema>.png";
const telegramCaption = "...";
```

O navegador:

1. baixa o SVG (`GET /model2/<hash>.svg`);
2. renderiza em canvas;
3. envia o PNG por `POST` na mesma URL da página:

```http
POST /1banners-filmes-series.php?query=...&type=movie&id=...&cast=1&model=...&theme=...
Content-Type: multipart/form-data

action=save_rendered_png
banner_hash=<hash>
png_file=<blob>
```

`[código]` a resposta é JSON `{"success":true,"path":"..."}`. O PNG observado
ficou em `GET /model2/<hash>.png` com **7,7 MB**; o SVG tinha **14,3 MB**.

### Indicações com 3 filmes

```text
GET /1banners-filmes-series.php?mode=indicacoes
GET /1banners-filmes-series.php?mode=indicacoes&type=tv
```

### Envio para Telegram

```http
GET /send_telegram.php?image=<caminho>&caption=<texto>
```

→ `200 text/html` com página “Sucesso!”. A entrega real depende do `chat_id`
configurado. Testado com uma imagem gerada; **não** foi possível confirmar se a
mensagem chegou.

---

## 7. Integração Xtream

### Filmes (`painel.php`)

#### `GET /painel.php?gp_trending=1`

→ `200`

```json
{
  "movies": [
    {
      "id": 1300968,
      "title": "Jogos Vorazes: Amanhecer na Colheita",
      "release_date": "2026-11-18",
      "poster_path": "/ibZ6GSHtCeC7fLDJ2uyXNemgYwr.jpg"
    }
  ],
  "stale": false
}
```

Observado: 12 filmes. O pôster é montado como
`https://image.tmdb.org/t/p/w342<poster_path>`.

#### `GET /painel.php?xt_recent=1`

Sem lista salva:

```json
{"saved": false, "movies": []}
```

Com lista salva:

```json
{
  "saved": true,
  "dns": "http://<host>",
  "user": "<xtream_user>",
  "movies": [
    {
      "name": "Nome - 2026",
      "added": 1795248060,
      "poster": "https://image.tmdb.org/t/p/w780/<arquivo>.jpg",
      "year": 2026,
      "tmdb_id": 0
    }
  ],
  "error": null,
  "diagnostic": {
    "version": "<diagnostic_version>",
    "php": "<php_version>",
    "curl": "<curl_version>",
    "attempts": [
      {
        "url": "http://<host>/player_api.php",
        "method": "GET",
        "http": 200,
        "curl": 0,
        "ip": "<ip>",
        "type": "application/json",
        "server": "cloudflare",
        "bytes": 2185222
      }
    ]
  }
}
```

Observado: 20 filmes na primeira resposta e download de **2,18 MB**.

#### `POST /painel.php?xt_recent=1`

`multipart/form-data`

| `xt_action` | Campos | Resposta observada |
|---|---|---|
| `save` | `csrf`, `dns`, `xt_user`, `xt_pass` | `200` com `saved:true`, `dns`, `user`, `movies`, `diagnostic` |
| `refresh` | `csrf` | `200` com o mesmo shape |
| `refresh_auto` | `csrf` | usado em background pelo JS |
| `delete` | `csrf` | `200` `{"saved":false,"movies":[]}` |
| `resolve` | `csrf`, `movie`, `year`, `poster` | `422` ambíguo; `404` HTML quando não encontra |

O `resolve` não é estável: em 22/11/2026 devolveu
`422 {"error":"Não foi possível identificar este filme com segurança. Use a
busca pelo nome no início da página."}` para itens ambíguos e `404` HTML para
outros. O caminho recomendado é a busca TMDB
(`/1banners-filmes-series.php?query=...`), que devolve ids confiáveis.

### Séries (`series_banner.php`)

#### `GET /series_banner.php?gp_trending=1`

Mesmo shape de `movies`, com séries em alta (12 itens observados).

#### `GET /series_banner.php?xt_recent=1`

Sem lista:

```json
{"saved": false, "series": []}
```

Com lista:

```json
{
  "saved": true,
  "dns": "http://<host>",
  "user": "<xtream_user>",
  "output": "hls",
  "series": [
    {
      "name": "Nome 2026",
      "added": 1795334459,
      "poster": "https://image.tmdb.org/t/p/w780/<arquivo>.jpg",
      "year": 2026,
      "tmdb_id": 0
    }
  ]
}
```

#### `POST /series_banner.php?xt_recent=1`

`multipart/form-data` com `csrf`, `xt_action`, e:

- `save`: `dns`, `xt_output` (`hls` ou `ts`), `xt_user`, `xt_pass`;
- `refresh`, `refresh_auto`, `delete`;
- `resolve`: `movie`, `year`, `poster`.

Observado: `save` → `200` `saved:true`, `output:"hls"`, séries com
`name/added/poster/year/tmdb_id`; `delete` → `200` `{"saved":false,"series":[]}`.

O `xt_pass` é enviado ao servidor e não é devolvido nas leituras. Não registre
essa senha em log, nota ou repositório.

---

## 8. Cortes Virais

### `GET /cortes_prontos.php`

→ HTML com cards:

```html
<button class="generate"
        data-id="<id>"
        data-file="<arquivo>.mp4"
        data-title="<titulo>">
```

Também tem:

- `GET /cortes_prontos.php?q=<busca>&ordem=recentes|populares|az`;
- `csrfToken` em `const csrfToken = "<csrf>"`;
- `dailyRemaining` (limite de 5 por dia na conta observada).

### `POST /gerar_corte_pronto.php`

`multipart/form-data`

```text
csrf_token=<csrf>
video_id=<id>
base_video_file=<arquivo>.mp4
video_title=<titulo>
whatsapp=<opcional>
frase=<opcional>
```

→ `200 text/plain` com a URL do MP4:

```text
https://gerador.pro/video/final/corte_<user_id>_<timestamp>_<hash>.mp4
```

Observado: **4,7 s**, arquivo de **2,16 MB**.

### `POST /salvar_historico.php`

`multipart/form-data`

```text
csrf_token=<csrf>&titulo=<titulo>
```

→ `200 application/json` `{"ok":true}`.

### `GET /meus_cortes.php`

HTML com o histórico de cortes.

### Entrega

```http
GET /video_pronto.php?video_url=<url>&video_title=<titulo>
GET /download_proxy.php?file=<url>
```

O proxy responde `200 video/mp4` com `Content-Length` e faz streaming do
arquivo.

---

## 9. Vídeos de divulgação

### `GET /videos_prontos.php`

→ HTML com cards:

```html
<button class="result-btn"
        data-video-id="vid_<id>"
        data-video-title="<titulo>"
        data-base-video-file="<arquivo>.mp4">
```

Categorias: `divulgação`, `indicação`, `ufc`, `destaques`, `futebol`.
Indicações têm limite de 3 por dia (`limiteMaxInd = 3`).

### `POST /gerar_video_pronto.php`

`multipart/form-data`

```text
video_id=vid_<id>
video_title=<titulo>
base_video_file=<arquivo>.mp4
whatsapp=<opcional>
```

→ `200 text/plain` com a URL:

```text
https://gerador.pro/video/final/indijogos_<hash>.mp4
```

Observado: **4,3 s**.

### Entrega

```http
GET /video_pronto.php?video_url=<url>&video_title=<titulo>
GET /download_proxy.php?file=<url>
```

---

## 10. Gerar vídeo por filme/série (TMDB)

### `GET /1video.php`

Formulário GET para `1searchvideo.php`:

```text
modelo=classico|cinema|netx
type=movie|tv
query=<titulo>
whatsapp=<opcional>
message=<opcional>
```

### `POST /log_search.php`

`multipart/form-data`

```text
query=<titulo>&type=movie&whatsapp=<opcional>
```

→ `200 text/html` com corpo vazio. É só telemetria de busca.

### `GET /1searchvideo.php?query=<q>&type=movie&modelo=classico`

→ HTML de resultados. Cada card chama:

```js
showOptionsModal('1searchvideo.php?modelo=classico&action=generate&type=movie&id=<tmdb_id>&whatsapp=')
```

### `GET /1searchvideo.php?...&action=generate&type=movie&id=<tmdb_id>`

→ `200 text/plain` com a URL do MP4:

```text
https://gerador.pro/video/final/<hash>.mp4
```

Observado: **~20 s**.

Respostas alternativas:

```json
{
  "action": "gp_trailer_choice",
  "choice_token": "<32 hex>",
  "candidate": {
    "video_id": "<11 chars>",
    "title": "string",
    "kind": "legendado|..."
  }
}
```

Para aceitar: adicione `&gp_trailer_accept=<choice_token>`.
Para usar outro link: `&manual_url=https://www.youtube.com/watch?v=...`.

Falha amigável:

```json
{
  "ok": false,
  "message": "string",
  "reference": "GP-XXXX-XXXXXXXXXXXX"
}
```

### Narração por IA

Quando `&gp_narrate=1&gp_voice=alex|m3` é enviado com o header
`X-GP-Alex-CSRF: <csrf>`, a resposta inclui o header `X-GP-Alex-Ticket`.

Fluxo:

```http
POST /gp_alex_narracao.php
Content-Type: application/x-www-form-urlencoded

action=start&csrf=<csrf>&ticket=<ticket>&voice=alex
```

→ `200`

```json
{"ok":true,"id":"<32 hex>","status":"queued","message":"Preparando a narração."}
```

Depois:

```http
POST /gp_alex_narracao.php
Content-Type: application/x-www-form-urlencoded

action=status&csrf=<csrf>&id=<id>
```

→ `200`

```json
{
  "ok": true,
  "status": "running|done|error",
  "message": "Adicionando a voz e ajustando o volume do trailer.",
  "url": "https://gerador.pro/video/final/gp_alex_<id>.mp4",
  "reference": "GP-VOZ-XXXXXXXXXXXX"
}
```

Observado: `running` com a mensagem de voz; depois `done` com o MP4 de
**8,97 MB** em ~35 s. O `reference` aparece em erros e é o código de suporte.

### Entrega

```http
GET /1video_pronto.php?modelo=classico&video_url=<url>&tmdb_id=<id>&media_type=movie
GET /1download_proxy.php?file=<url>
```

O proxy responde `200 video/mp4` e faz streaming.

---

## 11. Guia de Jogos

### `GET /guitexto.php?data_jogos=hoje|amanha`

→ HTML server-rendered com um `<textarea id="jogos-texto">` já preenchido.

Observado:

- `hoje`: **4.733 bytes** de texto;
- `amanha`: **1.107 bytes**.

Formato:

```text
📆 | *JOGOS DE HOJE - 22/11/2026*
━━━━━━━━━━━━━━━━━━
🏆 *CAMPEONATO RUSSO*
⚽ *Dinamo Moscow* x *Krasnodar*
⏰ 08:00
📺 XSPORTS
```

Não há endpoint JSON; o texto é montado no servidor.

---

## 12. Logo

### `GET /logo.php`

Formulário:

```html
<form method="post" enctype="multipart/form-data" action="logo.php">
  <input type="hidden" name="logo_type" value="logo_banner_1">
  <input type="file" name="image" accept="image/png, image/jpeg, image/gif, image/webp">
  <button type="submit" name="upload">Enviar</button>
</form>
```

O botão tem `name="upload"`. **`form.submit()` não envia esse campo**; é preciso
clicar no botão ou incluir `upload` no `FormData`.

### `POST /logo.php`

`multipart/form-data`

```text
logo_type=logo_banner_1
image=<arquivo PNG>
upload=
```

→ `200`. Depois:

```http
GET /futebol/noticias-gerar.php?action=logo
```

→ `200 image/png` (11 KB no teste). Sem logo → `400` com o erro de logo.

A página informa **2 trocas por dia** na conta observada.

---

## 13. Telegram

### `GET /config_telegram.php`

Formulário:

```html
<form method="POST" action="/config_telegram.php">
  <input type="text" name="chat_id" placeholder="Ex: -100123456789 ou 987654321">
  <button type="submit" name="salvar">Salvar Chat ID</button>
</form>
```

### `POST /config_telegram.php`

`multipart/form-data` ou urlencoded

```text
chat_id=<id do chat>
```

→ `200` e a página mostra sucesso. Um POST com `chat_id` vazio também retornou
`200` (sem alterar nada, pois o campo já estava vazio).

### `GET /send_telegram.php?image=<caminho>&caption=<texto>`

→ `200 text/html` com página “Sucesso!”. A entrega depende do `chat_id`.
Não foi possível confirmar a entrega; o teste usou uma imagem gerada e a
legenda “teste de mapeamento”.

---

## 14. Robô Automático

### `GET /robo_auto_config.php`

Formulário:

```html
<form method="POST" action="/robo_auto_config.php">
  <input type="checkbox" name="ativo" value="1">
  <input type="checkbox" name="incluir_whatsapp" value="1">
  <button type="submit">Salvar configuração</button>
</form>
```

A página também carrega o catálogo de modelos por
`GET /lote.php?acao=catalogo_modelos` e monta cards com frases prontas.

### `POST /robo_auto_config.php`

`multipart/form-data`

```text
ativo=1            (opcional)
incluir_whatsapp=1 (opcional)
```

→ `200`. Um POST sem os checkboxes (desmarcados) também retornou `200`.
Não foi habilitado nenhum envio automático.

---

## 15. App G Pro Player e G Pro Player TV

### `GET /app.php`

→ HTML com iframe:

```text
https://gerador.pro/app/gpro/?embed=1
```

### `GET /novelas.php`

→ HTML com iframe:

```text
https://novelas.fun/?embed=1&k=***
```

O parâmetro `k` é um token de embed; foi redigido. O conteúdo interno dos
iframes é de outro domínio/aplicação e não foi mapeado.

---

## 16. Telas com acesso negado

Para a conta observada:

| Tela | Resultado |
|---|---|
| `/cadastrar_whatsapp.php` | redireciona para `/index.php?access_denied` |
| `/gerenciar_leads.php` | redireciona para `/index.php?access_denied` |
| `/manager_reels.php` | redireciona para `/index.php?access_denied` |

Isso indica **indisponível nesta conta/plano**, não que o endpoint não exista.
O menu do dashboard exibe “Configurar WhatsApp”, “Link de Indicação” e
“App G Pro Drama”, mas o acesso é negado.

---

## 17. Resumo dos tokens por tela

| Tela | Token | Onde vai |
|---|---|---|
| `cortes_prontos.php` | `csrfToken` (JS) | `csrf_token` em `gerar_corte_pronto.php` e `salvar_historico.php` |
| `noticias.php` | `CSRF` (JS) | `csrf` no JSON de `noticias-gerar.php` |
| `filmes-series.php` | `CSRF` (JS) | `csrf` no JSON de `filmes-series-gerar.php` |
| `painel.php` | `xtToken` (JS) | `csrf` no FormData de `painel.php?xt_recent=1` |
| `series_banner.php` | `xtToken` (JS) | `csrf` no FormData de `series_banner.php?xt_recent=1` |
| `1searchvideo.php` (resultados) | `data-csrf` em `#gp-alex-script` | `csrf` em `gp_alex_narracao.php` e header `X-GP-Alex-CSRF` |

Os valores são rotativos por sessão/página e não devem ser versionados.
