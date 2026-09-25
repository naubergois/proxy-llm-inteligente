# Protocolo

Pré-registro em `experiments/preregister.json`: N, meia-vida, limiar do caderno, corte de comprimento, limiar RouteLLM, teto de token, seeds.

## Incerteza

Duas amostras do barato, seeds 0 e 1. Se o texto normalizado diverge, está inseguro. Logprob baixo vale se o backend trouxer. A string «não sei» não é o sinal.

## O caderno como sinal

N células escrevem e o relógio anda. Com `half_life = N`, restam os dois rastros mais novos. Se eles concordam (`tau = 1`), fica. Se misturam ou o caderno esvaziou, sobe. A célula seguinte lê o que ainda está vivo — se o rastro não muda a resposta, não é estigmergia.

## Políticas

| Nome | O que faz |
|---|---|
| `sempre_barato` | Uma célula fraca. |
| `sempre_caro` | Uma chamada forte (oráculo no mock). |
| `comprimento` | Prompt &lt; 80 caracteres → barato; senão caro. Controle fraco. |
| `routellm` | Score só do texto (tamanho, número grande, operador). Uma geração. |
| `frugalgpt` | Duas amostras; se discordam, sobe. |
| `voto` | N amostras independentes, maioria. Sem caro. |
| `cheiro` | Duas amostras; se discordam, enxame no caderno; se o vivo não fecha, sobe. |

## Tarefas

`data/tasks.json`: fácil curto, fácil longo, difícil curto, difícil longo. Gabarito único. No mock, cada item tem regime (`easy` / `flip` / `stuck` / `noisy`). Isso é modelo de capacidade, não resultado de paper.

## Desfechos

Acerto no gabarito. Tokens. Taxa de cada rota. Acerto por faixa (H1 mora no difícil curto vs fácil longo).

## Máquina

16 GB. Um modelo na RAM. Enxame = a mesma rede, outro sorteio. Sem chave no repositório.
