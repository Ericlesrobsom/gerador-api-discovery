# Segurança, sessão e redação

## Autenticação

- Login clássico por formulário: `POST /login.php` com `username` e `password`.
- Sessão por cookie `PHPSESSID`; não há Bearer token nem API key.
- Não há CSRF no login.
- `GET /logout.php` encerra a sessão.

## CSRF por tela

O painel usa tokens diferentes em cada tela. Eles são rotativos e não devem ser
copiados para nota, log ou repositório.

| Tela | Token | Uso |
|---|---|---|
| `cortes_prontos.php` | `csrfToken` | `csrf_token` em `gerar_corte_pronto.php` e `salvar_historico.php` |
| `noticias.php` | `CSRF` | `csrf` no JSON de `noticias-gerar.php` |
| `filmes-series.php` | `CSRF` | `csrf` no JSON de `filmes-series-gerar.php` |
| `painel.php` | `xtToken` | `csrf` no FormData de `painel.php?xt_recent=1` |
| `series_banner.php` | `xtToken` | `csrf` no FormData de `series_banner.php?xt_recent=1` |
| `1searchvideo.php` | `data-csrf` em `#gp-alex-script` | `csrf` em `gp_alex_narracao.php`; header `X-GP-Alex-CSRF` |

Ao reproduzir um fluxo fora do navegador, primeiro carregue a tela, extraia o
token da própria página e use-o na mesma sessão. Não tente adivinhar nem reutilizar
token de outra tela.

## O que nunca deve ser versionado

- Senha da conta.
- Cookie `PHPSESSID` ou qualquer cookie de sessão.
- Tokens `csrf`, `csrf_token`, `xtToken`, `data-csrf`, `X-GP-Alex-CSRF`,
  `X-GP-Alex-Ticket`.
- Credenciais Xtream (`xt_user`, `xt_pass`, DNS privado).
- URL com token de embed (`novelas.fun/?embed=1&k=...`).
- Nome/e-mail/telefone/WhatsApp de cliente.
- Imagens e vídeos gerados na conta.
- Bundles, HTML, CSS ou modelos do painel.

## Redação aplicada neste repositório

- `<user_id>`, `<csrf>`, `<xt_token>`, `<tmdb_id>`, `<job_id>`, `<hash>`,
  `<video_url>` são placeholders.
- O token do iframe `novelas.fun` foi substituído por `***`.
- Nenhuma resposta bruta de sessão foi incluída; só shapes e exemplos
  sanitizados.
- Nenhum caminho absoluto do servidor foi publicado (exceto o exemplo de erro
  de logo, que é genérico).

## Regras de uso

1. Use somente em conta própria e com autorização do dono do painel.
2. Não tente IDOR, troca de id de outro tenant, força bruta ou bypass de
   2FA/CAPTCHA.
3. Se aparecer dado de outro cliente/revenda, pare e reporte.
4. Ações que criam, editam, renovam, apagam, cobram ou enviam mensagem exigem
   confirmação explícita. O teste autorizado deste mapa foi feito em conta
   própria; ainda assim, os fluxos destrutivos foram evitados quando possível.
5. `clean_images.php` apaga imagens anteriores da conta. Não chame “só para
   testar”.
6. `rename_images.php` renomeia/apaga imagens. Não chame sem saber o estado da
   galeria.
7. `save_favs.php` sobrescreve a lista de favoritos. Não chame com `[]` sem
   backup.
8. `send_telegram.php` pode enviar mensagem real. Só use com `chat_id` de teste.
9. Respeite o rate limit do Cloudflare. Em `429`, pare e reduza o ritmo; não
   insista.

## Limites de responsabilidade

Este mapa é uma fotografia de 2026-11-22. O painel é proprietário e pode mudar
sem aviso. Não há garantia de contrato, estabilidade ou autorização de uso. A
licença MIT cobre apenas o conteúdo próprio deste repositório.
