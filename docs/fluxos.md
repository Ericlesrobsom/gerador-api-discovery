# Fluxos observados

Passo a passo do que o painel faz no navegador. Use placeholders; os valores
reais de sessão/CSRF não entram em documento.

## 1. Login

1. `GET /login.php` → formulário `username` + `password`.
2. `POST /login.php` (urlencoded) → `302 Location: index.php` e
   `Set-Cookie: PHPSESSID`.
3. `GET /index.php` → dashboard.
4. Todas as chamadas seguintes usam a mesma origem e o cookie de sessão.

Não há CSRF no login. Não há Bearer token. `GET /logout.php` encerra a sessão.

## 2. Notícias → banner

1. `GET /noticias.php` carrega o feed:
   `GET /futebol/noticias-gerar.php?action=feed`.
2. A página busca a logo:
   `GET /futebol/noticias-gerar.php?action=logo`.
   - Sem logo → mostra erro e bloqueia a geração.
3. O usuário seleciona até 10 notícias e escolhe a cor.
4. `POST /futebol/noticias-gerar.php?action=create` com
   `{ids, color, whatsapp, csrf}` → job com `next:0`.
5. `GET /futebol/cartazes/clean_images.php?user_id=<user_id>`.
6. Para cada índice:
   `POST /futebol/noticias-gerar.php?action=step` com `{job, index, csrf}`.
7. Quando `next == total`, o job traz `gallery_url` e `published`.
8. A galeria (`/futebol/cartazes/`) lista o PNG gerado.

## 3. Filmes/Séries → banner

Mesmo fluxo, trocando:

- `/futebol/noticias-gerar.php` por `/futebol/filmes-series-gerar.php`;
- o feed de notícias pelo feed de filmes/séries;
- as cores são as mesmas.

## 4. Banner esportivo

1. `GET /futbanner.php` (ou `nba.php`, `nfl.php`, `ufc.php`, `esportes.php`,
   `formula1.php`) lista os modelos.
2. O usuário escolhe um modelo:
   `GET /futbanner.php?page=futebol&modelo=<modelo>`.
3. A página monta o formulário `#generationForm` com:
   - `text_color`, `highlight_color`, `card_background_color`;
   - `whatsapp_number` (opcional);
   - `json_data` (jogos do dia).
4. O botão chama `clean_images.php` e envia o form para
   `POST /futebol/<script>.php` em um iframe.
5. As imagens ficam em
   `/futebol/cartazes/user_<user_id>/hoje/` e `/amanha/`.
6. A URL do diretório responde 403 na listagem, mas as imagens são válidas.

## 5. Lote “Gerar Express” `[código]`

1. `GET /lote.php` carrega o catálogo:
   `GET /lote.php?acao=catalogo_modelos`.
2. O usuário seleciona modelos e clica em “GERAR TUDO AGORA”.
3. `GET /futebol/cartazes/rename_images.php?acao=limpar`.
4. Para cada modelo:
   - `POST /futebol/<script>.php` com `whatsapp_number` e `json_data`;
   - `GET /futebol/cartazes/rename_images.php?categoria=<FUT|BASQ|TODOS>&ordem=<n>`.
5. Redireciona para `/futebol/cartazes/`.

## 6. Banner de filme/série (TMDB)

1. `GET /1banners-filmes-series.php?query=<titulo>&type=movie`.
2. O card escolhido navega para
   `?query=<titulo>&type=movie&id=<tmdb_id>&action=select_style`.
3. O usuário escolhe modelo (1–10) e tema.
4. O botão navega para
   `?query=...&type=...&id=...&cast=1&model=<N>&theme=<tema>`.
5. A página “Banner pronto” embute:
   - `svgBannerPath` (`model2/<hash>.svg`);
   - `pngBannerPath` (`model2/<hash>.png`);
   - `bannerHash`, `downloadName`, `telegramCaption`.
6. O navegador baixa o SVG, renderiza em canvas e envia o PNG:
   `POST` na mesma URL, multipart:
   `action=save_rendered_png`, `banner_hash`, `png_file`.
7. O PNG fica em `/model2/<hash>.png`.
8. O botão de Telegram aponta para
   `send_telegram.php?image=<caminho>&caption=<texto>`.

## 7. Xtream — filmes

1. `GET /painel.php` → `GET /painel.php?gp_trending=1` (12 filmes em alta).
2. `GET /painel.php?xt_recent=1` → `{saved:false, movies:[]}` ou a lista salva.
3. Para salvar:
   `POST /painel.php?xt_recent=1` multipart com
   `csrf`, `xt_action=save`, `dns`, `xt_user`, `xt_pass`.
4. O servidor baixa o `player_api.php` e devolve:
   `saved`, `dns`, `user`, `movies`, `error`, `diagnostic`.
5. `POST` com `xt_action=refresh` atualiza; `delete` remove.
6. `POST` com `xt_action=resolve` tenta achar o TMDB de um item;
   - ambíguo → `422 {"error":"..."}`;
   - não encontrado → `404` HTML.
7. O caminho estável para banner é a busca TMDB:
   `1banners-filmes-series.php?query=...`.

## 8. Xtream — séries

1. `GET /series_banner.php` → `GET /series_banner.php?gp_trending=1`.
2. `GET /series_banner.php?xt_recent=1` → `{saved:false, series:[]}` ou lista.
3. `POST /series_banner.php?xt_recent=1` com
   `csrf`, `xt_action=save`, `dns`, `xt_output=hls|ts`, `xt_user`, `xt_pass`.
4. Resposta: `saved`, `dns`, `user`, `output`, `series`.
5. `delete` remove; `refresh`/`refresh_auto` atualizam.

## 9. Cortes Virais

1. `GET /cortes_prontos.php` → cards com `data-id`, `data-file`, `data-title`.
2. O usuário escolhe um card e uma frase (opcional).
3. `POST /gerar_corte_pronto.php` multipart com
   `csrf_token`, `video_id`, `base_video_file`, `video_title`, `whatsapp`,
   `frase`.
4. A resposta é a URL do MP4 em `/video/final/corte_...mp4`.
5. `POST /salvar_historico.php` com `csrf_token` e `titulo` → `{"ok":true}`.
6. A entrega usa `video_pronto.php` e `download_proxy.php`.

## 10. Vídeos de divulgação

1. `GET /videos_prontos.php` → cards com `data-video-id`,
   `data-video-title`, `data-base-video-file`.
2. `POST /gerar_video_pronto.php` multipart com esses campos + `whatsapp`.
3. A resposta é a URL do MP4 em `/video/final/indijogos_...mp4`.
4. A entrega usa `video_pronto.php` e `download_proxy.php`.

## 11. Vídeo por filme/série + narração

1. `GET /1video.php` → busca `1searchvideo.php`.
2. `GET /1searchvideo.php?query=...&type=movie&modelo=classico`.
3. O card chama `showOptionsModal('...&action=generate&type=movie&id=<id>')`.
4. “Modo automático” faz `GET` na URL de geração.
5. A resposta é a URL do MP4, um `gp_trailer_choice` ou um erro `GP-...`.
6. Para narração:
   - acrescente `gp_narrate=1&gp_voice=alex|m3`;
   - envie o header `X-GP-Alex-CSRF`;
   - leia o header `X-GP-Alex-Ticket`;
   - `POST gp_alex_narracao.php` com `action=start`, `csrf`, `ticket`, `voice`;
   - faça polling com `action=status`, `csrf`, `id`;
   - `done` devolve `video/final/gp_alex_<id>.mp4`.
7. A entrega usa `1video_pronto.php` e `1download_proxy.php`.

## 12. Logo

1. `GET /logo.php` → form multipart.
2. `POST /logo.php` multipart com
   `logo_type=logo_banner_1`, `image=<PNG>`, `upload=`.
3. O campo `upload` é o nome do botão; **`form.submit()` não o envia**.
4. `GET /futebol/noticias-gerar.php?action=logo` deve passar a responder
   `200 image/png`.

## 13. Telegram

1. `GET /config_telegram.php` → form com `chat_id`.
2. `POST /config_telegram.php` com `chat_id` → `200`.
3. Imagens usam `GET /send_telegram.php?image=<caminho>&caption=<texto>`.
4. Na galeria, o botão “Enviar” usa
   `GET /send_telegram.php?image=user_<user_id>%2Fbanner_1.png` (sem legenda).
   Para o dia seguinte, acrescenta `&day=tomorrow`.
5. Vídeos usam um link `data-link` renderizado na página de entrega e
   `&custom_caption=<texto>`; sem `chat_id` o botão não é renderizado.
6. O arquivo `banner_1.png` é sobrescrito pela próxima geração; envie antes de
   gerar a próxima cor.

## 14. Robô Automático

1. `GET /robo_auto_config.php` → form com `ativo` e `incluir_whatsapp`.
2. A página carrega o catálogo por `lote.php?acao=catalogo_modelos`.
3. `POST /robo_auto_config.php` com os checkboxes marcados/desmarcados.
4. Não foi habilitado nenhum envio automático no teste.

## 15. Guia de Jogos

1. `GET /guitexto.php?data_jogos=hoje` (ou `amanha`).
2. O servidor monta o texto em `<textarea id="jogos-texto">`.
3. A página oferece copiar e enviar ao WhatsApp; não há API JSON.
