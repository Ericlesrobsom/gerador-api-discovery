# Gerador PRO — descoberta da API interna

Mapa observado da API interna do painel **Gerador PRO** (`https://gerador.pro`),
obtido pelo navegador em **22/11/2026**, sem acesso ao código-fonte do servidor.

> **Não é uma API oficial.** O painel não publica OpenAPI, Swagger ou `llms.txt`;
> `/api` responde **403**. Este repositório documenta apenas o que apareceu em
> requisições e respostas reais. Rotas, campos e comportamentos podem mudar sem
> aviso.

> ⚠️ **Regra crítica do painel:** a página de logo proíbe imagens
> genéricas/invisíveis. Um teste com logo 100% transparente foi detectado como
> “imagem invisível” e **bloqueou a conta**. O bloqueio foi revertido no mesmo
> dia, mas a regra continua: use uma logo visível da marca. Veja
> [`docs/limites-e-erros.md`](docs/limites-e-erros.md).

## O que tem aqui

| Arquivo | Conteúdo |
|---|---|
| [`docs/gerador-api-map.md`](docs/gerador-api-map.md) | mapa completo dos endpoints, corpos e respostas |
| [`docs/fluxos.md`](docs/fluxos.md) | passo a passo dos fluxos (login, banners, vídeos, Xtream) |
| [`docs/seguranca.md`](docs/seguranca.md) | sessão, CSRF, redação e limites de uso |
| [`docs/limites-e-erros.md`](docs/limites-e-erros.md) | limites, erros observados e o que ficou pendente |
| [`openapi.yaml`](openapi.yaml) | especificação **não oficial** dos endpoints mapeados |
| [`skill/SKILL.md`](skill/SKILL.md) | método reutilizável de descoberta pelo navegador |
| [`examples/curl.md`](examples/curl.md) | exemplos com placeholders |

## Escopo validado

- Login por formulário clássico (`POST /login.php`), sessão `PHPSESSID`.
- Dashboard e menu administrativo.
- Notícias esportivas → banners (lote de até 10).
- Filmes/Séries → banners (lote de até 10).
- Banners esportivos: futebol, NBA, NFL, UFC, esportes e Fórmula 1.
- Catálogo de 114 modelos de banner.
- Integração Xtream: filmes e séries (salvar, atualizar, remover, resolver).
- Cortes Virais (vídeo curto a partir de um arquivo base).
- Vídeos de divulgação (prontos).
- Gerar vídeo por filme/série (TMDB) + trailer alternativo.
- Narração por IA (voz `alex` e `m3`).
- Banner de filme/série por modelo e tema (SVG → PNG no navegador).
- Logo, Telegram, Robô Automático, Guia de Jogos.
- App G Pro Player e G Pro Player TV (iframes externos).
- Telas com acesso negado para esta conta.

## O que foi executado de verdade

- Login em sessão isolada (cookie jar separado, descartado depois).
- 1 banner de notícias e 1 banner de filmes/séries.
- 1 banner esportivo real (10 páginas geradas: 8 de hoje + 2 de amanhã).
- 1 corte viral (MP4 de 2,16 MB, ~4,7 s).
- 1 vídeo de divulgação (MP4, ~4,3 s).
- 1 vídeo por filme (MP4, ~20 s).
- 1 vídeo com narração IA (MP4 de 8,97 MB, ~35 s).
- 1 banner de filme (SVG de 14,3 MB → PNG de 7,7 MB).
- Ciclo Xtream completo: salvar (2,18 MB), ler, atualizar e remover.
- Upload de logo de teste, POST de Telegram vazio e POST do Robô com tudo
  desmarcado.
- Contato de WhatsApp salvo nas telas de Notícias e Filmes/Séries
  (`remember:true`), com o número retornando no `SAVED_CONTACT`.
- Limpeza da galeria de teste ao final (10 imagens removidas).

## O que não foi executado

- “GERAR TUDO AGORA” do lote (`lote.php`) com vários modelos.
- `save_favs.php` (para não sobrescrever favoritos existentes).
- `rename_images.php` (renomeia/apaga imagens; destrutivo).
- Confirmação de entrega do `send_telegram.php` (depende do `chat_id`).
- Um `resolve` Xtream com sucesso (só foram observados 422 e 404).
- Telas `cadastrar_whatsapp.php`, `gerenciar_leads.php` e `manager_reels.php`
  (redirecionam para `access_denied` nesta conta).
- Conteúdo interno dos iframes `app/gpro` e `novelas.fun`.

## Aviso legal

O painel, seus bundles, HTML, CSS, imagens e modelos são propriedade do
fornecedor. Este repositório **não redistribui** código do painel; contém apenas
documentação própria baseada em observação. Use somente em conta própria e com
autorização. Não há senhas, cookies, tokens, CSRF ou dados de clientes aqui.

## Licença

MIT para o conteúdo próprio deste repositório. Marcas e conteúdo de terceiros
pertencem aos respectivos donos. Veja [`LICENSE`](LICENSE) e
[`NOTICE.md`](NOTICE.md).
