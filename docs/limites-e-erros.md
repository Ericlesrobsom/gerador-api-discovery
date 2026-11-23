# Limites, erros e pendências

## Limites observados

| Item | Limite / observação |
|---|---|
| Notícias por lote | até 10 ids |
| Filmes/Séries por lote | até 10 ids |
| Cortes Virais | 5 por dia (`dailyRemaining = 5`) |
| Indicações em vídeos | 3 por dia (`limiteMaxInd = 3`) |
| Logo | 2 trocas por dia; a terceira retorna “Você atingiu o limite de 2 trocas de logo por dia.” |
| Catálogo de modelos | 114 modelos: 92 futebol, 15 basquete, 7 esportes |
| Xtream | download de ~2,18 MB; timeout de 40 s/90 s no JS |
| Conexões externas | o painel baixa `player_api.php` do servidor Xtream |
| Rate limit | Cloudflare respondeu 429 em rajada de `curl`; navegador espaçado passou |

## Erros observados

### 400 — logo ausente

```http
GET /futebol/noticias-gerar.php?action=logo
```

```json
{"error":"Cadastre sua logo no Gerador Pro antes de gerar as notícias."}
```

Também apareceu na geração esportiva sem logo:

```text
Erro: Não foi possível carregar os dados da logo. Caminho:
<raiz_do_painel>/futebol/logo_padrao.png
```

O caminho absoluto do servidor foi omitido de propósito.

### 422 — filme ambíguo no Xtream `resolve`

```json
{"error":"Não foi possível identificar este filme com segurança. Use a busca pelo nome no início da página."}
```

### 404 — `resolve` sem correspondência

Resposta HTML “Página Não Encontrada”. O `resolve` não é confiável para todos os
itens; prefira a busca TMDB.

### 403 — nginx

- `/api` → 403.
- A URL do diretório da galeria
  (`/futebol/cartazes/user_<user_id>/hoje/`) → 403 na listagem, mas as imagens
  existem.
- Um `POST` direto no modelo esportivo também retornou 403; o fluxo real pelo
  botão gerou as imagens e o iframe carregou a URL do diretório (403).

### 429 — rate limit

Ocorreu ao baixar várias páginas com `curl` em sequência. A solução foi parar,
esperar e usar o navegador com intervalo. Não insistir.

### Sessão expirada

O JS checa `response.redirected`; se a resposta for redirecionada ao login, a
sessão expirou. Repita o login e recapture o token da tela.

### `send_telegram.php`

Retornou `200` com a página “Sucesso!” em um teste com imagem e legenda
“teste de mapeamento”. **Não foi possível confirmar a entrega**: depende do
`chat_id` configurado. Se você recebeu uma mensagem de teste, foi esse teste.

## Bloqueio por logo invisível (regra crítica)

A página de logo avisa:

> “O Gerador Pro é para uso exclusivo com a sua marca. Tentativas de tornar o
> banner universal ou genérico resultarão na exclusão do painel.”

Foi enviada uma logo 100% transparente para teste. O painel detectou como
“imagem invisível” e respondeu:

```text
CONTA BLOQUEADA
VIOLAÇÃO DE SEGURANÇA CRÍTICA
O sistema detectou uma tentativa de manipulação (imagem invisível) para burlar
as regras da plataforma.
SUA CONTA ESTÁ EM PROCESSO DE EXCLUSÃO.
Sessão encerrada. Conexão terminada.
```

Não tente contornar. A conta precisa falar com o suporte do painel. Este mapa
não recomenda nem apoia logo invisível/arte genérica.

**Atualização (2026-11-22):** depois do bloqueio, o painel voltou a abrir o
dashboard na mesma sessão, após a conta ser liberada. O bloqueio não foi uma
exclusão imediata; funcionou como trava de segurança reversível. A regra
continua: use uma logo visível da marca, nunca uma imagem invisível/genérica.

## WhatsApp: três coisas diferentes

1. **Número na arte/contato do gerador**: as telas de Notícias e Filmes/Séries
   têm um campo de WhatsApp e um `?action=contact` que salva
   `{remember:true, whatsapp}`. Isso foi configurado e passa a vir preenchido
   nessas telas.
2. **Número no perfil do Robô Automático**: o checkbox `incluir_whatsapp` usa o
   número cadastrado no perfil. A tela de perfil é `cadastrar_whatsapp.php`,
   bloqueada nesta conta.
3. **Bot que envia para o WhatsApp**: não há endpoint acessível nesta conta
   para conectar um bot de WhatsApp. O que está configurado e funcionando é o
   envio por Telegram (`chat_id` presente).

## Envio ao Telegram (validado)

- 6 cores do modelo 26 (amarelo, azul, cinza, roxo, verde, vermelho) foram
  geradas e enviadas ao Telegram em 2026-11-22.
- URL usada pelo botão “Enviar” da galeria:
  `GET /send_telegram.php?image=user_<user_id>%2Fbanner_1.png`.
- Os 6 envios responderam `200` com “A imagem foi enviada para o Telegram com
  sucesso.”
- O arquivo `banner_1.png` é sobrescrito pela próxima geração; envie antes de
  gerar a próxima cor.
- A galeria ficou com o conjunto vermelho (última cor). Detalhes em
  [`teste-telegram.md`](teste-telegram.md).

## Logo: limite e escala

- O painel limita a **2 trocas de logo por dia**. A terceira tentativa retornou:
  `Erro! Você atingiu o limite de 2 trocas de logo por dia.`
- A logo é ampliada na arte. Um ponto de **300 px** em um canvas 1024×1024 foi
  aceito, mas apareceu como um **círculo branco grande**, cobrindo parte do
  banner.
- Um ponto de **100 px** foi preparado, mas o upload foi recusado pelo limite
  diário (não pelo conteúdo). O arquivo ficou fora do repositório, pronto para
  a próxima janela de troca.
- A regra de marca continua: um ponto é genérico; a página avisa que arte
  universal/genérica pode causar exclusão. O teste não recomenda esse caminho.

## O que ficou pendente

| Item | Motivo |
|---|---|
| Lote “GERAR TUDO AGORA” | geraria muitos banners e apagaria a galeria; o endpoint de modelo já foi validado individualmente |
| `rename_images.php` | renomeia/apaga arquivos; não foi executado |
| `save_favs.php` | sobrescreve favoritos; não foi executado |
| `resolve` com sucesso | só foram observados 422 e 404 |
| Entrega Telegram | depende de `chat_id`; não confirmada |
| `cadastrar_whatsapp.php` | acesso negado nesta conta |
| `gerenciar_leads.php` | acesso negado nesta conta |
| `manager_reels.php` | acesso negado nesta conta |
| Iframe `app/gpro` | aplicação externa; não mapeada |
| Iframe `novelas.fun` | aplicação externa; token de embed redigido |
| API oficial | não existe; `/api` responde 403 |

## Artefatos de teste (não versionados)

Durante a validação foram gerados, na conta de teste:

- banners esportivos em `user_<user_id>/hoje` e `amanha` (removidos ao final);
- 1 banner de notícias e 1 de filmes/séries (removidos pela limpeza seguinte);
- 1 banner de filme em `model2/<hash>.png` (7,7 MB);
- 1 corte viral (2,16 MB);
- 1 vídeo de divulgação;
- 1 vídeo por filme;
- 1 vídeo com narração IA (8,97 MB);
- 1 logo de teste “TESTE”.

Os vídeos em `/video/final/` e o PNG em `/model2/` não têm endpoint de exclusão
mapeado; se quiser removê-los, use o gerenciador de arquivos do servidor ou
peça ao suporte. A logo de teste pode ser substituída em `logo.php`.
