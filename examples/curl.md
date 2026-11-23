# Exemplos com `curl`

> Substitua `<usuario>`, `<senha>`, `<panel>`, `<csrf>`, `<user_id>`, `<job_id>`,
> `<tmdb_id>` e `<video_url>` pelos valores da sua conta. Nunca comite o cookie
> nem o token.

## Login e cookie jar

```bash
PANEL="https://gerador.pro"
JAR="cookies.txt"

curl -s -c "$JAR" -b "$JAR" -o /dev/null -w "%{http_code} %{redirect_url}\n" \
  -d "username=<usuario>&password=<senha>" \
  "$PANEL/login.php"

curl -s -b "$JAR" "$PANEL/index.php" | grep -o '<title>[^<]*' | head -1
```

O login deve responder `302` com `Location: index.php`. O `cookies.txt` contém
`PHPSESSID`; trate como segredo e apague no fim.

## Extrair o CSRF de uma tela

```bash
curl -s -b "$JAR" "$PANEL/noticias.php" -o noticias.html
CSRF=$(grep -o 'const CSRF="[^"]*"' noticias.html | cut -d'"' -f2)
test -n "$CSRF" && echo "csrf ok"
```

Para `painel.php`/`series_banner.php`, o padrão é `const xtToken = "..."`.
Para `cortes_prontos.php`, é `const csrfToken = "..."`.

## Feed de notícias

```bash
curl -s -b "$JAR" \
  "$PANEL/futebol/noticias-gerar.php?action=feed" \
  | head -c 400
```

## Criar e processar um banner de notícias

```bash
curl -s -b "$JAR" -H "Content-Type: application/json" \
  -d "{\"ids\":[\"<id>\"],\"color\":\"azul\",\"whatsapp\":\"\",\"csrf\":\"$CSRF\"}" \
  "$PANEL/futebol/noticias-gerar.php?action=create"
```

Guarde o `id` do job e o `total`. Depois, para cada índice:

```bash
curl -s -b "$JAR" -H "Content-Type: application/json" \
  -d "{\"job\":\"<job_id>\",\"index\":0,\"csrf\":\"$CSRF\"}" \
  "$PANEL/futebol/noticias-gerar.php?action=step"
```

Quando `next == total`, a resposta traz `gallery_url` e `published`.

## Xtream — salvar lista de filmes

```bash
curl -s -b "$JAR" \
  -F "csrf=$XT_TOKEN" \
  -F "xt_action=save" \
  -F "dns=http://<host>" \
  -F "xt_user=<xtream_user>" \
  -F "xt_pass=<xtream_pass>" \
  "$PANEL/painel.php?xt_recent=1"
```

Leitura:

```bash
curl -s -b "$JAR" "$PANEL/painel.php?xt_recent=1"
```

Remoção:

```bash
curl -s -b "$JAR" -F "csrf=$XT_TOKEN" -F "xt_action=delete" \
  "$PANEL/painel.php?xt_recent=1"
```

## Cortes Virais

```bash
CSRF_CORTES=$(curl -s -b "$JAR" "$PANEL/cortes_prontos.php" \
  | grep -o 'const csrfToken = "[^"]*"' | cut -d'"' -f2)

curl -s -b "$JAR" \
  -F "csrf_token=$CSRF_CORTES" \
  -F "video_id=<id>" \
  -F "base_video_file=<arquivo>.mp4" \
  -F "video_title=<titulo>" \
  -F "whatsapp=" \
  -F "frase=" \
  "$PANEL/gerar_corte_pronto.php"
```

A resposta é a URL do MP4. Depois:

```bash
curl -s -b "$JAR" \
  -F "csrf_token=$CSRF_CORTES" \
  -F "titulo=<titulo>" \
  "$PANEL/salvar_historico.php"
```

## Vídeo de divulgação

```bash
curl -s -b "$JAR" \
  -F "video_id=<vid_id>" \
  -F "video_title=<titulo>" \
  -F "base_video_file=<arquivo>.mp4" \
  -F "whatsapp=" \
  "$PANEL/gerar_video_pronto.php"
```

## Vídeo por filme

```bash
curl -s -b "$JAR" \
  "$PANEL/1searchvideo.php?modelo=classico&action=generate&type=movie&id=<tmdb_id>&whatsapp="
```

A resposta é a URL do MP4, um `gp_trailer_choice` ou um erro `GP-...`.

## Narração IA

Primeiro gere com `gp_narrate=1` e o header CSRF, e guarde o ticket do header
`X-GP-Alex-Ticket`:

```bash
curl -s -D headers.txt -b "$JAR" \
  -H "X-GP-Alex-CSRF: $ALEX_CSRF" \
  "$PANEL/1searchvideo.php?modelo=classico&action=generate&type=movie&id=<tmdb_id>&whatsapp=&gp_narrate=1&gp_voice=alex"

TICKET=$(grep -i '^x-gp-alex-ticket:' headers.txt | tr -d '\r' | awk '{print $2}')
```

Inicie:

```bash
curl -s -b "$JAR" -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "action=start" \
  --data-urlencode "csrf=$ALEX_CSRF" \
  --data-urlencode "ticket=$TICKET" \
  --data-urlencode "voice=alex" \
  "$PANEL/gp_alex_narracao.php"
```

Faça polling:

```bash
curl -s -b "$JAR" -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "action=status" \
  --data-urlencode "csrf=$ALEX_CSRF" \
  --data-urlencode "id=<id>" \
  "$PANEL/gp_alex_narracao.php"
```

## Download proxy

```bash
curl -s -b "$JAR" -I \
  "$PANEL/download_proxy.php?file=$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' '<video_url>')"
```

Deve responder `200 video/mp4` com `Content-Length`.

## Limpeza

```bash
rm -f cookies.txt headers.txt noticias.html
```

Nunca comite `cookies.txt`, `headers.txt` ou arquivos com token.
