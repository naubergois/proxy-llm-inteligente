# Porteiro com cheiro: o caderno que evapora como sinal de rota

**A Scented Doorman: Evaporating Traces as a Routing Signal**

Francisco Nauber Bernardo Gois  
Controladoria e Ouvidoria Geral do Estado do Ceará (CGE-CE), ASESI  
francisco.gois@cge.ce.gov.br

Rascunho v0.1 — 25 de setembro de 2026  
Alvo: TMLR (sem taxa de autor). Alternativas: JAIR, iSys/JBCS.

---

## Abstract (EN)

Routing a query to a cheap or an expensive language model is a solved product problem and an active research one. RouteLLM picks before generation. FrugalGPT escalates after a quality check. Neither uses a shared trace that fades. This draft asks whether an evaporating board — live traces only — can decide stay, swarm, or escalate under a token cap, against those published baselines plus majority vote and a length heuristic. We release an OpenAI-compatible proxy and a 22-item short/long × easy/hard set. The numbers below are a **fixture**: the expensive backend is an oracle and the cheap cell is scripted. On that fixture, length fails on short-hard items (0.20) while wasting the oracle on long-easy ones; FrugalGPT reaches 0.82; scent reaches 0.50 because the first trace pulls later cells. That is wiring, not a finding. A paper claim needs a frozen SLM (MLX) or a real expensive API.

**Keywords:** LLM routing, cascade, stigmergy, small language models, token budget

## Resumo (PT)

Escolher um modelo barato ou um caro já é produto e já é paper. RouteLLM escolhe antes de gerar. FrugalGPT sobe depois de uma nota de qualidade. Nenhum dos dois usa um rastro compartilhado que some. A pergunta deste rascunho: sob o mesmo teto de token, o caderno que evapora decide melhor ficar, juntar células ou subir do que esses baselines, o voto e o corte por comprimento? O proxy e as 22 tarefas estão no GitHub. Os números da Seção 5 são **fiação**: o caro é oráculo e o barato é roteiro. Neles, o comprimento erra o difícil curto (0,20) e gasta o oráculo no fácil longo; FrugalGPT chega a 0,82; o cheiro fica em 0,50 porque o primeiro rastro puxa as células seguintes. Reivindicação de paper pede SLM congelado ou API cara de verdade.

**Palavras-chave:** roteamento de LLM, cascata, estigmergia, modelos pequenos, orçamento de token

---

## 1. Introdução

Um aplicativo não precisa saber o nome do modelo. Ele fala com uma porta só. Por baixo, alguém decide se a pergunta fica numa célula barata, se vale juntar sorteios, ou se sobe para um gerador caro. Essa porta já existe como produto (LiteLLM, OpenRouter). Como pesquisa, a decisão tem dois desenhos publicados.

O primeiro olha o texto e escolhe **antes** de gastar geração. RouteLLM treina um roteador com preferência humana e reduz custo sem cair a qualidade no banco em que foi medido (Ong et al., 2025). Hybrid-LLM faz o corte por dificuldade prevista e qualidade desejada (Ding et al., 2024).

O segundo gera com o barato e **sobe** se a resposta parecer fraca. FrugalGPT é a cascata canônica (Chen et al., 2024). AutoMix verifica a própria saída e escala (Aggarwal et al., 2024).

Falta um terceiro desenho, mais velho que o transformer. Formiga não vota. Ela deixa cheiro; o cheiro some; a próxima lê o que ainda está no chão (Grassé, 1959). A pergunta operacional é estreita: o caderno que evapora pode ser o **sinal de rota** — ficar, enxamear, subir — de um jeito que o roteador pré-geração e a cascata não cobrem?

Três hipóteses, pré-registradas em `experiments/preregister.json`.

- **H1.** O corte por comprimento do prompt erra o item difícil que veio curto e gasta o caro no fácil que veio longo.
- **H2.** RouteLLM e FrugalGPT já batem o sempre-caro em custo. Isso não é novidade deste artigo.
- **H3.** Quando duas amostras do barato discordam, os rastros ainda vivos no caderno mudam acerto ou gasto em relação ao voto e à cascata.

A contribuição deste rascunho é o protocolo e o código, não um ganho medido em SLM. A Seção 5 reporta a fiação. A Seção 6 diz o que o SLM precisa mostrar para H3 viver ou morrer.

## 2. Trabalho relacionado

### 2.1 Roteamento antes de gerar

RouteLLM formaliza a escolha entre um modelo fraco e um forte a partir de dados de preferência e mostra transferência para pares não vistos no treino (Ong et al., 2025). Hybrid-LLM treina um roteador que estima se o modelo pequeno basta e permite ajustar o limiar em teste (Ding et al., 2024). Os dois gastam zero geração do modelo-alvo na decisão. A implementação `routellm` deste repositório **não** reproduz o checkpoint publicado: é um juiz de superfície (tamanho, número ≥ 10, operador). Serve de controle honesto, não de oráculo da literatura.

### 2.2 Cascata depois de gerar

FrugalGPT encadeia APIs e para quando a qualidade estimada basta (Chen et al., 2024). AutoMix gera com o modelo pequeno, auto-verifica e escala (Aggarwal et al., 2024). A política `frugalgpt` daqui instancia o espírito da cascata com um sinal barato: duas amostras, seeds 0 e 1; se o texto normalizado diverge, sobe. Não treinamos um juiz de qualidade.

### 2.3 População e cheiro

Voto de várias amostras da mesma rede é o controle natural de um enxame sem memória. Se o erro é o mesmo em todas as células, a maioria só confirma o erro. Estigmergia, no sentido de Grassé (1959), é o contrário do voto: o meio carrega um rastro que **envelhece**. Cultura emergente e mundos simulados já usaram depósito que some; não mediram acerto contra RouteLLM. Este artigo trata o caderno como sinal de *rota*, não como cultura.

Não reivindicamos um proxy novo. Reivindicamos um sinal.

## 3. Método

Notação. Consulta $q$. Célula barata $B$ e cara $C$. Tamanho do enxame $N=3$. Meia-vida $h=N$. Limiar de consenso $\tau=1$. Corte de comprimento $L=80$ caracteres. Limiar do juiz de superfície $\theta=0{,}4$. Teto de token $K=256$ por item. Seeds de sonda $\{0,1\}$. Seeds de cheiro e de voto $\{10,11,12\}$.

### 3.1 Incerteza

Dadas duas compleções $y_0=B(q;0)$ e $y_1=B(q;1)$, a sonda está insegura se os textos normalizados diferem ou se algum está vazio. Se o backend trouxer log-probabilidade média abaixo de $-1{,}2$, isso também conta. A string «não sei» **não** é o sinal.

### 3.2 Caderno

Cada célula $i$ lê o que ainda não evaporou, gera, escreve o texto, e o relógio anda uma unidade. Com $h=N$, depois de $N$ escritas restam os $N-1$ rastros mais novos. Consenso é a fração do texto majoritário entre os vivos. Se a fração $\ge \tau$, a rota é `cheiro` e a resposta é esse texto. Se o caderno mistura ou esvazia, sobe para $C$, salvo se o teto $K$ impedir.

A célula seguinte tem de ler o caderno. Se o rastro não muda a distribuição da resposta, o que temos é voto com extra, não estigmergia.

### 3.3 Políticas

| Nome | Decisão | Gerações |
|---|---|---|
| `sempre_barato` | sempre $B$ | 1 |
| `sempre_caro` | sempre $C$ | 1 |
| `comprimento` | $B$ se $\|q\|<L$, senão $C$ | 1 |
| `routellm` | $C$ se $s(q)\ge\theta$, senão $B$ | 1 (depois do score) |
| `frugalgpt` | $B$ se $y_0\equiv y_1$, senão $C$ | 2 + talvez 1 |
| `voto` | maioria de $N$ amostras de $B$ | $N$ |
| `cheiro` | sonda; se insegura, enxame no caderno; se o vivo não fecha, $C$ | 2 + $N$ + talvez 1 |

O score $s(q)$ usa só superfície: comprimento $\ge 80$, contagem de inteiros $\ge 10$, operador aritmético ou a palavra «resto», e número de palavras $\ge 20$. Sem gabarito.

Desfechos: acerto contra gabarito único (igualdade do token normalizado); soma de tokens; taxa de cada rota; acerto por faixa.

### 3.4 Tarefas

Vinte e dois itens em `data/tasks.json`, quatro faixas: fácil curto, fácil longo, difícil curto, difícil longo. H1 mora no par difícil-curto versus fácil-longo. No backend mock cada item tem um regime de capacidade (`easy`, `flip`, `stuck`, `noisy`). Esse regime é modelo da célula fraca, não resultado.

## 4. Implementação

O código vive em `src/proxy_llm/`. Uma porta stdlib em `127.0.0.1:8787` expõe `POST /v1/chat/completions` e devolve `route` e `usage.total_tokens`.

| Módulo | Papel no artigo |
|---|---|
| `board.py` | caderno, `tick`, consenso dos vivos |
| `uncertainty.py` | desacordo e logprob |
| `judge.py` | $s(q)$ |
| `backends.py` | $B$ mock / MLX; $C$ oráculo ou HTTP |
| `router.py` | as sete políticas |
| `bench.py` | `fumo.jsonl` + `fumo.summary.json` |
| `plot.py` | Figuras 1 e 2 |

Enxame, neste Mac de 16 GB, é a mesma rede com outro sorteio. Chave de API não entra no git.

## 5. Fiação (mock, 25 de setembro de 2026)

O caro devolve o gabarito. O barato acerta o fácil, discorda no `flip`, erra com confiança no `stuck` e acerta cerca de 30% no `noisy`. Sem SLM, a Tabela 1 e as Figuras 1–2 medem se o protocolo distingue as políticas, não se o cheiro ganha.

**Tabela 1.** Acerto e token no conjunto ($n=22$). Fonte: `results/fumo.summary.json`.

| política | acerto | tokens | rotas |
|---|---:|---:|---|
| sempre_barato | 0,45 | 176 | barato 22 |
| sempre_caro | 1,00 | 1408 | caro 22 |
| comprimento | 0,64 | 624 | barato 14, caro 8 |
| routellm | 0,68 | 792 | barato 11, caro 11 |
| frugalgpt | 0,82 | 1056 | barato 11, caro 11 |
| voto | 0,32 | 528 | voto 22 |
| cheiro | 0,50 | 808 | barato 11, cheiro 8, caro 3 |

H1 aparece no recorte. `comprimento` acerta 0,20 no difícil curto ($n=10$) e 1,00 no fácil longo ($n=3$), este último chamando o oráculo. `routellm` sobe um pouco no difícil curto (0,30) porque números grandes e operadores empurram $s(q)$. `frugalgpt` chega a 0,70 no difícil curto: o regime `flip` discorda e escala. `cheiro` fica em 0,20 nessa faixa — o mesmo piso do sempre-barato — e só 0,40 no difícil longo.

H2, na fiação, segura: FrugalGPT e o juiz de superfície gastam menos token que o sempre-caro e acertam mais que o sempre-barato. Não é descoberta.

H3, na fiação, cai. O caderno puxa a célula seguinte para o primeiro rastro (probabilidade de seguir $=0{,}7$ no mock). Se o primeiro erra, o vivo fecha no erro e o porteiro **não** sobe. A cascata, que olha a sonda e não o consenso posterior, sobe no `flip`. O voto, sem caro, confirma o erro correlacionado (0,32 no geral; 0,00 no difícil).

Isso é o que o protocolo tinha de mostrar antes do SLM: as políticas não colapsam numa só coluna, e o cheiro pode perder da cascata quando o rastro alinha o erro.

## 6. Discussão

O nulo do mock é informativo. Estigmergia não é mágica: é correlação introduzida de propósito. Se $B$ erra igual, o caderno estável é um voto atrasado. A cascata escapa porque a incerteza mora na sonda, não no consenso. Para H3 viver num SLM, precisamos de um regime em que (i) duas amostras discordam com frequência no item difícil curto, (ii) o rastro às vezes desloca a terceira célula para o gabarito, e (iii) o caderno misto dispara o caro sem ir ao caro sempre.

Se, no Qwen 0,5B ou no Tucano 0,6B, o cheiro não bater FrugalGPT em acerto por token, o artigo reporta o nulo. Esse é um resultado publicável. O que não é publicável é vender a Tabela 1 como capacidade de modelo.

O juiz `routellm` é fraco de propósito. Trocar por um checkpoint RouteLLM treinado seria um baseline mais duro e um experimento à parte.

## 7. Limitações

Vinte e dois itens. Um idioma. Gabarito curto. O caro do mock é oráculo. $N$ e $h$ estão acoplados. O teto $K=256$ raramente aperta no mock. Sem intervalo de confiança: uma seed de protocolo. Sem humano no laço.

## 8. Conclusão

A porta já existia. A cascata já existia. O voto já existia. O que este rascunho fecha é o desenho: um caderno com meia-vida como sinal de ficar ou subir, medido contra os baselines que a área já aceita, com incerteza que não é uma palavra combinada. A fiação corre. O paper começa quando a mesma tabela sair de um SLM.

---

## Reprodução

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,plot]"
python -m proxy_llm.bench --no-cache
python -m proxy_llm.plot
```

Código: https://github.com/naubergois/proxy-llm-inteligente  
Pré-registro: `experiments/preregister.json`  
Tarefas: `data/tasks.json`

SLM (ainda não é a Tabela 1):

```bash
pip install -e ".[mlx]"
python -m proxy_llm.bench --backend mlx --no-cache --model mlx-community/Qwen2.5-0.5B-Instruct-4bit
```

## Disponibilidade de dados

Tarefas, pré-registro, jsonl e figuras deste rascunho estão no repositório público. Nenhum dado pessoal.

## Ética

Sem sujeitos humanos. Sem dado de ouvidoria ou de processo administrativo.

## Contribuições (CRediT)

Francisco Nauber Bernardo Gois: conceptualização, software, redação.

## Financiamento

Nenhum financiamento externo. O autor é servidor da CGE-CE.

## Conflito de interesse

Nenhum.

## Uso de IA

Texto e código deste rascunho foram produzidos com assistência de modelo de linguagem no Cursor. Hipóteses, pré-registro, recusa de reivindicar o mock e a lista de baselines publicados foram decisões do autor. Nenhuma citação foi inventada: RouteLLM, FrugalGPT, Hybrid-LLM, AutoMix e Grassé (1959) foram conferidos na fonte.

## Referências

Aggarwal, P., Madaan, A., Anand, A., Potharaju, S. P., Mishra, S., Zhou, P., Gupta, A., Rajagopal, D., Kappaganthu, K., Yang, Y., Upadhyay, S., Faruqui, M., & Mausam. (2024). *AutoMix: Automatically mixing language models*. NeurIPS 2024. https://arxiv.org/abs/2310.12963

Chen, L., Zaharia, M., & Zou, J. (2024). FrugalGPT: How to use large language models while reducing cost and improving performance. *Transactions on Machine Learning Research*. https://openreview.net/forum?id=cSimKw5p6R

Ding, D., Mallick, A., Wang, C., Sim, R., Mukherjee, S., Rühle, V., Lakshmanan, L. V. S., & Awadallah, A. H. (2024). Hybrid LLM: Cost-efficient and quality-aware query routing. *ICLR 2024*. https://arxiv.org/abs/2404.14618

Grassé, P.-P. (1959). La reconstruction du nid et les coordinations interindividuelles chez *Bellicositermes natalensis* et *Cubitermes* sp. La théorie de la stigmergie: Essai d'interprétation du comportement des termites constructeurs. *Insectes Sociaux, 6*, 41–80.

Ong, I., Almahairi, A., Wu, V., Chiang, W.-L., Wu, T., Gonzalez, J. E., Kadous, M. W., & Stoica, I. (2025). RouteLLM: Learning to route LLMs with preference data. *ICLR 2025*. https://arxiv.org/abs/2406.18665
