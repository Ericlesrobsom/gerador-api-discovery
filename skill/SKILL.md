---
name: gerador-api-discovery
description: Mapear a API interna do painel Gerador PRO (gerador.pro) pelo navegador, sem código-fonte do servidor, capturando login, banners, vídeos, Xtream, cortes, logo e Telegram. Use quando o pedido for "mapear o gerador", "descobrir os endpoints do gerador.pro" ou reproduzir a captura de shape neste painel.
user-invocable: true
---

# Descoberta da API do Gerador PRO pelo navegador

Método para reconstruir a API interna de um painel PHP clássico usando apenas o
navegador: navegação, DOM, `fetch`/XHR e respostas reais. **Não adivinhe campo
nem alias.** Primeiro observe; depois documente.

## Resultado esperado

Um `gerador-api-map.md` com, para cada fluxo:

1. método + path + query;
2. autenticação (cookie/CSRF) e como é obtida;
3. corpo do request com tipos;
4. resposta real sanitizada com status e tipos;
5. erros observados;
6. paginação/filtros/limites;
7. o que ficou desconhecido.

## Regras de ouro

1. **Só campo observado vira contrato.** O resto fica em “desconhecido”.
2. **Tipo importa:** string, number, bool, null, array.
3. **Somente leitura por padrão.** Escritas só no descartável e com autorização.
4. **Segredo não entra em nota, log ou relatório.** CSRF, cookie, senha,
   `xt_pass`, ticket e token de embed são `***`.
5. **Uma aba, uma sessão.** Não abra dois portais no mesmo painel.
6. **Evidência antes de conclusão.** Cada endpoint aponta o fluxo e o horário.
7. **Sem força bruta, sem bypass.** Não teste IDOR, outro tenant, 2FA/CAPTCHA.
8. **API oficial vence.** Se existir OpenAPI/`llms.txt`, use-a. Neste painel não
   existe (`/api` → 403), então a API interna é a única fonte.

## Pré-requisitos

- URL exata (`https://gerador.pro`).
- Conta de teste/revenda com o menor privilégio que mostre os menus.
- Escopo: login, notícias, filmes/séries, esportes, Xtream, cortes, vídeos,
  banner de filme, logo, Telegram, robô.
- Autorização explícita para escrita. Sem ela: só leitura.
- Onde salvar o relatório.

## Fase 0 — preparação

1. Liste o canvas e os portais:

```bash
maestri list
```

2. Crie as notas duráveis:

```bash
maestri note create --name "Gerador API - capturas"
maestri note create --name "Gerador API - mapa"
maestri note create --name "Gerador API - decisoes"
```

3. Crie o portal e ligue **um** agente a ele:

```bash
maestri portal create "https://gerador.pro" "gerador"
maestri connect "<Batedor>" "gerador"
```

4. Registre no topo da nota: URL, data/hora UTC, versão do painel (se visível) e
   escopo autorizado.

## Fase 1 — recon passivo

Use sempre o loader para evitar aspas quebradas no PowerShell:

```powershell
$S = "$HOME\.agents\skills\sigma-api-discovery"
& "$S\assets\avaliar.ps1" -Portal "gerador" -Arquivo "$S\assets\inspecionar.js"
```

O retorno mostra framework, storages, cookies, scripts e recursos. Neste painel
o esperado é:

- PHP clássico, sem React/Vue/Next;
- `PHPSESSID` como único cookie de sessão;
- formulários `POST`/`GET` clássicos;
- `fetch` para AJAX em algumas telas.

Complementos:

```bash
maestri portal logs-start "gerador"
maestri portal snapshot "gerador"
maestri portal html "gerador"
```

## Fase 2 — captura de rede

Instale o hook **antes** de cada fluxo (ele morre em navegação/reload):

```powershell
& "$S\assets\avaliar.ps1" -Portal "gerador" -Arquivo "$S\assets\hook-rede.js"
```

Ciclo:

1. `window.__sigmaCap = [];` **não** reatribua o array; se precisar limpar,
   use `window.__sigmaCap.length = 0`.
2. Execute uma ação.
3. Exporte com `exportar.js`.
4. Sanitize e grave na nota.
5. Repita.

Se a saída for grande, exporte em fatias.

### Login

- `GET /login.php` → form `username`/`password`.
- `POST /login.php` → `302` e `Set-Cookie: PHPSESSID`.
- Não há CSRF no login.
- Valide em um cookie jar separado para não derrubar a sessão principal.

## Fase 3 — fluxos do Gerador

Percorra na ordem, marcando `observado`, `inferido` ou `pendente`:

1. **Auth:** login, logout, sessão, expiração.
2. **Dashboard:** cards e vencimento; não há JSON.
3. **Notícias:** `futebol/noticias-gerar.php` (feed, logo, thumb, create, step,
   status, contact, clean_images).
4. **Filmes/Séries:** `futebol/filmes-series-gerar.php` (mesmo shape).
5. **Esportes:** `futbanner.php`/`nba.php`/`nfl.php`/`ufc.php`/`esportes.php`/
   `formula1.php`; form POST para `futebol/<script>.php`.
6. **Lote:** `lote.php`; catálogo, `save_favs.php`, `rename_images.php`.
7. **Banner de filme/série:** `1banners-filmes-series.php` (busca, estilo,
   `model`/`theme`, SVG→PNG, `save_rendered_png`, `send_telegram.php`).
8. **Xtream filmes:** `painel.php?gp_trending=1`, `?xt_recent=1` (GET/POST
   `save|refresh|refresh_auto|delete|resolve`).
9. **Xtream séries:** `series_banner.php` (mesmo, com `xt_output`).
10. **Cortes:** `cortes_prontos.php`, `gerar_corte_pronto.php`,
    `salvar_historico.php`, `meus_cortes.php`.
11. **Vídeos prontos:** `videos_prontos.php`, `gerar_video_pronto.php`.
12. **Vídeo por filme:** `1video.php`, `1searchvideo.php` (`action=generate`),
    `gp_trailer_ui.js`, `gp_alex_classico.js`, `gp_alex_narracao.php`.
13. **Guia de jogos:** `guitexto.php?data_jogos=hoje|amanha`.
14. **Logo:** `logo.php` (multipart, campo `upload`).
15. **Telegram:** `config_telegram.php`, `send_telegram.php`.
16. **Robô:** `robo_auto_config.php`, `lote.php?acao=catalogo_modelos`.
17. **App/Novelas:** `app.php`, `novelas.php` (iframes externos).
18. **Acesso negado:** `cadastrar_whatsapp.php`, `gerenciar_leads.php`,
    `manager_reels.php`.

## Fase 4 — leitura do JavaScript

Se a captura não cobrir um fluxo, leia o JS servido:

```js
(async () => {
  const alvos = [...document.scripts].map(s => s.src).filter(Boolean);
  const saida = [];
  for (const src of alvos.slice(0, 20)) {
    try {
      const txt = await (await fetch(src)).text();
      const rotas = [...new Set((txt.match(/["'`](\/[a-zA-Z0-9_\-./{}:]*\.php[^"'`]*)["'`]/g) || []))];
      saida.push({ src, bytes: txt.length, rotas: rotas.slice(0, 100) });
    } catch (e) { saida.push({ src, erro: String(e) }); }
  }
  return JSON.stringify(saida).slice(0, 20000);
})()
```

Não redistribua bundles. Use o JS só para localizar rotas; a captura de rede
continua sendo a fonte de verdade.

## Fase 5 — replay controlado

Repita uma chamada pela própria página, com a mesma sessão e o mesmo CSRF. Um
endpoint por vez. Se a resposta vier com dado de outro tenant, pare.

## Fase 6 — relatório

Preencha `docs/gerador-api-map.md` e espelhe o resumo na nota. Qualidade mínima:

- request e response reais sanitizados;
- todo campo com tipo e exemplo;
- todo id com nome e formato;
- erros com status e corpo;
- desconhecidos explícitos;
- nenhuma credencial/token/dado pessoal.

## Armadilhas específicas deste painel

- **`form.submit()` não envia o nome do botão.** No upload de logo, o campo
  `upload` é o nome do botão; inclua-o no `FormData` ou clique no botão.
- **Logo é obrigatória** para banners de notícias/filmes e esportivos. Sem ela,
  a API responde 400 ou um erro de `logo_padrao.png`.
- **A galeria é apagada** por `clean_images.php` antes de cada lote.
- **O iframe do banner esportivo** carrega a URL do diretório e recebe 403, mas
  as imagens existem.
- **`resolve` do Xtream é instável** (422/404). Prefira a busca TMDB.
- **CSRF por tela**: `csrfToken`, `CSRF`, `xtToken`, `data-csrf`. Não reutilize.
- **Cloudflare 429** em rajadas de `curl`; use o navegador com intervalo.
- **`send_telegram.php`** pode enviar mensagem real; só use com chat de teste.
- **`novelas.fun`** tem token de embed; redija.

## Definition of Done

- Fluxos cobertos ou marcados `indisponível`/`pendente`.
- Cada endpoint validado por replay ou justificativa.
- Relatório salvo e resumo na nota.
- Riscos e limites ditos em voz alta.
- Nada criado/cobrado/apagado fora do descartável autorizado.
