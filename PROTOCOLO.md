# Protocolo

Pré-registrar: teto de token, N do enxame, meia-vida do caderno, limiar de incerteza, seeds.

## Rotas

| Rota | Quando |
|---|---|
| `cache` | Mesma pergunta (hash) já vista nesta sessão. |
| `barato` | Primeira tentativa, uma célula. |
| `cheiro` | Barato inseguro (resposta curta demais, ou “não sei”, ou baixa concordância se N>1). Enxame no caderno que some. |
| `caro` | Cheiro ainda inseguro **ou** o barato caiu. Uma chamada. |
| `voto` | Controle: N amostras, maioria. Mesmo orçamento que o cheiro. |

## Baselines

1. Sempre `barato`.
2. Sempre `caro` (no mock, um gerador mais fiel).
3. Comprimento: se o prompt tem < 80 caracteres → barato; senão caro.

## Desfechos

Acerto no gabarito. Tokens (ou caracteres, no mock). Taxa de cada rota. Latência.

## Máquina

16 GB. Um modelo na RAM. Enxame = a mesma rede, outro sorteio. Sem chave no repositório.
