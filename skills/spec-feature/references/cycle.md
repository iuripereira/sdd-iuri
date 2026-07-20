# Ciclo sdd-iuri — máquina de estados e fases

## Estados da delta (vivem no cabeçalho do `spec.md`)

```
proposta ──(analyze LIBERADO + implement + review + merge)──▶ aplicada ──(consolidação)──▶ arquivada
```

- **proposta** — de specify até o fim do review. Vive em `specs/NNN-nome/`.
- **aplicada** — código mergeado; falta consolidar. Estado transitório: não pare aqui.
- **arquivada** — consolidada no `TRUTH.md` e movida para `specs/_archive/NNN-nome/`.

## Fases — critérios de entrada/saída

| Fase | Entrada | Saída (critério de pronto) | Motor |
|---|---|---|---|
| specify | pedido de feature; `TRUTH.md` lido | `specs/NNN-nome/spec.md` rascunho no template; branch `tipo/NNN-nome` criada | nativo |
| clarify | spec rascunho | ambiguidades resolvidas; spec consolidada: todo Rn com DADO/QUANDO/ENTÃO; RNFs aplicáveis (desempenho, segurança, acessibilidade, ...) elicitados com métrica; ADRs gravados se grill-with-docs | max:grill-me / max:grill-with-docs |
| plan | spec consolidada | `plan.md` em `specs/NNN-nome/` com o cabeçalho-resumo (≤15 linhas) prependido | superpowers:writing-plans |
| tasks | plan.md | `tasks.md`: cada task com arquivos, `cobre: Rn`/`RNFn` (ou `cobre: infra`, para task sem requisito) e verificação, ordenada por dependência | nativo (template) |
| analyze | spec + plan + tasks | `analyze.md` com veredito LIBERADO (ou ressalvas aceitas pelo usuário) | nativo (analyze.md) |
| implement | analyze liberado | todas as tasks concluídas com as verificações rodadas; TDD conforme coluna `tdd` do tipo | superpowers:executing-plans ou subagent-driven-development |
| review | implementação completa | estágio 1 (conformidade com a spec) ok; estágio 2 (qualidade) ok com delete-list do /ponytail-review tratada | superpowers + ponytail:ponytail-review |
| archive | PR mergeado | Estado: arquivada; TRUTH.md consolidado; diretório em `_archive/` | nativo (regras abaixo) |

Fim de cada fase = **commit dos artefatos na branch da delta** (regra canônica: fim de etapa = commit). Não acumule o ciclo inteiro num commit só.

## PR da delta — split condicional (delta-003)

O limiar de tamanho de PR (dono: regra canônica do git-workflow, no projeto-init) vale para o PR da delta — **e os artefatos do ciclo contam**. No fim do analyze (veredito LIBERADO), meça:

```bash
git diff origin/main --shortstat -- specs/NNN-nome/
```

- **Linhas adicionadas acima do limiar** → split: os artefatos são mergeados primeiro num PR próprio (branch `docs/NNN-nome`, commit `docs(NNN-nome): artefatos da delta-NNN`); a implementação segue depois em `tipo/NNN-nome`, com PR separado.
- **Dentro do limiar** → um único PR carrega artefatos + implementação (fluxo vigente).

Implementação que sozinha excede o limiar já tem regra própria: fim de etapa = commit + PR — não acumule etapas. O valor do limiar não é repetido aqui de propósito (fonte canônica única); em repo com `deps.toml`, o C2 do `validate_integrity.py` acusa a materialização.

Ciclo reduzido (site-estatico): specify → plan → implement → review. clarify/analyze entram sob demanda (spec ambígua ou toque em regra canônica).

## Triagem do clarify (escolha do motor — reporte ao usuário)

`grill-with-docs` quando a spec toca **contrato externo, modelo de dados persistente, dependência nova ou segurança** → decisão durável em jogo → gera ADRs (contrato em adapters.md). Caso contrário `grill-me` (stateless, menos tokens). Sem o plugin max → fallback do adapters.md.

## Consolidação entrevista → delta spec (passo nativo, ex-to-spec)

Ao fim do clarify, sintetize **da conversa já feita** — NUNCA re-entreviste:
1. Cada decisão da entrevista vira um Rn novo ou ajusta um existente, sempre com DADO/QUANDO/ENTÃO verificável.
2. Qualidade discutida (desempenho, segurança, acessibilidade, capacidade, ...) vira RNFn com Métrica e Verificação. Qualidade sem limiar fechado na entrevista **não vira RNF** — vai para "Dependências e riscos" como pendência ("rápido" não é requisito; "p95 < 300ms" é).
3. Renúncias explícitas vão para "Fora de escopo".
4. Pendências sem resposta vão para "Dependências e riscos" — não invente resposta.
5. Decisão durável discutida sem ADR gravado? Registre o ADR agora (template do projeto, `docs/adrs/`), antes do plan.

## Regras de archive (consolidação no TRUTH.md)

O `TRUTH.md` vive em **`specs/TRUTH.md`**. Blocos MUDA/REMOVE da delta devem **citar o alvo vigente** nele (ex.: "MUDA R2 (delta-001)"). `specs/TRUTH.md` inexistente (primeiro archive) → crie de `templates/TRUTH.md` antes de consolidar.

1. **ADICIONA** → o requisito entra no domínio correspondente do TRUTH.md com sufixo `(delta-NNN)`, cenário DADO/QUANDO/ENTÃO incluído. Recebe o **próximo número R livre do TRUTH.md** — a numeração do TRUTH é global e nunca reutiliza número (nem de requisito removido); o Rn local da delta não migra.
2. **MUDA** → substitui **integralmente** o requisito vigente (texto + cenários) pelo bloco da delta; o sufixo passa a `(delta-NNN)` da delta nova. Por isso o bloco MUDA deve conter a versão completa do requisito — cenário vigente que continua valendo é **repetido na delta**; o archive consolida mecanicamente, não infere intenção.
3. **REMOVE** → apaga a entrada do TRUTH.md.
4. **Blocos RNFn** seguem as regras 1–3 igualmente, consolidando na seção **Não funcionais** do TRUTH.md (Métrica e Verificação incluídas), com numeração RNF própria — também global e nunca reutilizada.
5. Atualize `Estado: arquivada` no spec.md e mova `specs/NNN-nome/` → `specs/_archive/NNN-nome/` (com plan.md, tasks.md, analyze.md juntos — o histórico completo vive no archive).
6. **Verificação obrigatória (diff):** todo Rn/RNFn ADICIONA/MUDA da delta presente no TRUTH.md consolidado; todo REMOVE ausente; nenhum requisito de outras deltas alterado. Perda de requisito no archive é o pior bug do ciclo — por isso é mecânica, não conferida a olho: rode `scripts/check_cycle.py <delta>` **depois de consolidar** (antes ou depois de commitar — o C4 compara o TRUTH.md contra o merge-base da branch com a main, sem janela cega pós-commit) e ele acusa CRÍTICO em requisito removido que a delta não declara como alvo de MUDA/REMOVE.
7. **Pendência roteada:** item `- [ ]` em "Dependências e riscos" do spec arquivado é pendência aberta — registre-a no `DEBT.md` como `DT-NNN` (natureza: pendência, origem: `delta-NNN`) e marque `- [x]`, no mesmo commit da consolidação. Projeto sem `DEBT.md` cria o arquivo a partir do template da projeto-init nesse momento. O C6 do `check_cycle.py` acusa ALTO para `- [ ]` remanescente.

Particionamento do TRUTH.md: acima de ~800 linhas ou ~10 domínios claros → dividir em `truth/<dominio>.md` e o TRUTH.md vira índice (a regra já está no template).

## Economia de tokens (NFR de primeira classe)

Artefatos **duráveis** (spec.md, TRUTH.md) são enxutos — limites nos templates. O `plan.md` é artefato **efêmero de execução**: verboso por design (executável por subagente sem contexto), arquivado junto com a delta e fora do caminho depois. Não pós-processe o plan para "enxugar" — só o cabeçalho-resumo importa para humanos e para o analyze.
