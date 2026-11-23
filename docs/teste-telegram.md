# Teste de envio ao Telegram (2026-11-22)

## Objetivo

Validar, na prática:

1. logo **visível** de teste (não invisível);
2. geração dos banners de **jogos do dia** em cada cor;
3. envio de uma imagem de cada cor para o Telegram configurado.

## Modelo e cores

Família `modelo26` (futebol), 6 variantes:

| Modelo | Cor | Script |
|---|---|---|
| 93 | amarelo | `modelo26amarelo.php` |
| 94 | azul | `modelo26azul.php` |
| 95 | cinza | `modelo26cinza.php` |
| 96 | roxo | `modelo26roxo.php` |
| 97 | verde | `modelo26verde.php` |
| 98 | vermelho | `modelo26vermelho.php` |

Cada página foi aberta em:

```text
/futbanner.php?page=futebol&modelo=<id>
```

e o formulário `#generationForm` foi enviado para
`/futebol/modelo26<cor>.php` com `whatsapp_number` preenchido.

## Imagens geradas

A galeria fica em `/futebol/cartazes/` e, para este modelo, gerou:

```text
capa_com_logo.png
banner_1.png
banner_2.png
banner_3.png
(banner_4.png no vermelho)
```

As imagens usam a logo visível de teste “TESTE” e o número de WhatsApp
informado. O número não é registrado neste repositório.

## Envio

O botão “Enviar” da galeria usa:

```http
GET /send_telegram.php?image=user_<user_id>%2Fbanner_1.png
```

Para o dia seguinte, o JS acrescenta `&day=tomorrow`.

Resultado observado em **cada uma das 6 cores**:

```http
HTTP/1.1 200 OK
```

```text
Sucesso! A imagem foi enviada para o Telegram com sucesso.
```

## Observações

- O arquivo `user_<user_id>/banner_1.png` é **sobrescrito** pela próxima
  geração. Envie a imagem antes de gerar a próxima cor.
- O envio padrão da galeria não inclui legenda; a imagem chega sozinha.
- O `chat_id` do Telegram já estava configurado em `config_telegram.php`.
- A logo invisível bloqueou a conta; a logo visível foi aceita após a
  liberação. Não use imagem invisível/genérica.
- O teste foi feito em conta própria; a galeria ficou com o conjunto vermelho
  (última cor gerada). Os envios estão no Telegram.
