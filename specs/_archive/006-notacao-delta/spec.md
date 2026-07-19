# delta-006 — notacao-delta
Estado: arquivada · Data: 2026-07-19 · Branch: feat/006-notacao-delta

## Contexto (≤3 linhas)
O símbolo `Δ` (U+0394) que identifica as deltas não é digitável num teclado comum. Troca
aprovada por `delta-NNN` nos artefatos vivos e templates; o gate passa a reconhecer as duas
notações (legada `(ΔNNN)` e nova `(delta-NNN)`) para não quebrar projetos já existentes.

## Mudanças
### R1 — MUDA R6 (Δ000): a delta declara só o que muda em relação ao TRUTH.md
> Bloco integral; só o exemplo do cenário 1 muda de notação. Cenário 2 repetido como vige.

R6 — a delta declara só o que muda em relação ao TRUTH.md.
- DADO o `TRUTH.md` vigente QUANDO a spec é redigida ENTÃO cada bloco é ADICIONA, MUDA ou REMOVE,
  e blocos MUDA/REMOVE citam o alvo vigente (ex.: "MUDA R2 (delta-001)")
- DADO um requisito na delta QUANDO a spec é validada ENTÃO ele tem cenário DADO/QUANDO/ENTÃO
  verificável; qualidade sem limiar fechado vira pendência em riscos, não RNF

### R2 — MUDA R7 (Δ000): a delta percorre os estados proposta → aplicada → arquivada
> Bloco integral; cenário 1 troca o sufixo `(ΔNNN)` por `(delta-NNN)`. Cenário 2 repetido.

R7 — a delta percorre os estados proposta → aplicada → arquivada, e o archive faz parte
do "pronto".
- DADO um PR mergeado QUANDO o archive roda ENTÃO o spec.md vira `Estado: arquivada`, o requisito
  é consolidado no `TRUTH.md` com sufixo `(delta-NNN)` e o diretório move para `specs/_archive/NNN-nome/`
- DADO um bloco MUDA QUANDO o archive consolida ENTÃO o requisito vigente é substituído
  **integralmente** pelo bloco da delta — a consolidação é mecânica, não infere intenção

### R3 — MUDA R12 (Δ002): a metade mecânica do analyze é um script, não diligência
> Bloco integral; os três cenários vigentes repetidos + cenário novo da dupla notação. O
> cenário 2 ganha a precisão "removido do arquivo resultante" (o C4 mede presença de ID, não
> ausência no diff) — é o que torna a migração de sufixo em massa não-acusável.

R12 — a metade mecânica do analyze é um script, não diligência.
- DADO uma delta QUANDO `check_cycle.py` roda ENTÃO ele verifica aceite (C1), cobertura
  spec↔tasks (C2), estado × localização (C3), archive sem perda (C4), tamanho do TRUTH (C5) e
  pendência roteada (C6), e sai 1 se houver ALTO ou CRÍTICO
- DADO um requisito removido do `TRUTH.md` resultante sem MUDA/REMOVE que o declare QUANDO o gate
  roda ENTÃO acusa CRÍTICO e o veredito é BLOQUEADO — comparando o `TRUTH.md` contra o merge-base
  da branch com a main (fallback `HEAD`, com aviso, quando não há base), para que consolidação
  já commitada não crie janela cega; sufixo reescrito cujo ID permanece no arquivo não é perda
- DADO a saída do script QUANDO impressa ENTÃO se declara parcial — nomeia os checks mecânicos
  cobertos e avisa que os checks 3 e 5 do `analyze.md` (scope creep, regra canônica) são humanos
- DADO um `TRUTH.md` com sufixos na notação legada `(ΔNNN)` ou na nova `(delta-NNN)` QUANDO o
  gate lê os alvos ENTÃO reconhece as duas formas, sem exigir migração dos projetos existentes

## Requisitos não funcionais
<!-- sem RNF: migração de notação + capacidade de parsing, sem qualidade nova a medir -->

## Fora de escopo
- Renomear diretórios (`specs/NNN-nome/`) e branches (`tipo/NNN-nome`) — já são digitáveis; o
  `NNN` numérico nunca dependeu do símbolo.
- Reescrever histórico imutável: ADRs, `specs/_archive/`, seções lançadas do CHANGELOG e a
  tabela "Histórico de alterações" do STATE.md — `delta-NNN` só em conteúdo vivo.
- Remover a notação `Δ` do parser — mantida como forma aceita (compat com TRUTH legado);
  removê-la seria breaking (MAJOR).

## Dependências e riscos
- Notação `delta-NNN` aprovada pelo usuário em 2026-07-19 (rejeitados `DE-NNN`, que colide com
  o ID `DEP-NNN` do scaffold estático, e `D-NNN`, críptico).
- Esta delta estreia a notação: seus próprios blocos MUDA citam alvos na forma **vigente**
  (`(Δ000)`/`(Δ002)`) — é o que está no TRUTH hoje; a forma nova é emitida a partir do archive.

## Clarify — relatório de ambiguidade (grill-me, modo spec)
<!-- grelhado no plan mode: notação, fronteira vivo/histórico e a armadilha do C4 resolvidas -->
```
Goals:        0.0   ✓ notação escolhida (delta-NNN), 3 alvos MUDA definidos
Acceptance:   0.0   ✓ cada bloco verificável por grep + selftest do gate
Boundaries:   0.0   ✓ fora de escopo explícito (dirs/branches, histórico imutável, remover Δ)
Alternatives: 0.25  ✓ DE-NNN e D-NNN considerados e rejeitados com porquê
Assumptions:  0.0   ✓ único acoplamento (regex ALVO) e armadilha do C4 verificados no código
──────────────────────────────
Aggregate:    0.05  ✓ abaixo do limiar (0.2 spec)
```
