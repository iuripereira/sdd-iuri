<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** trocar o símbolo `Δ` por `delta-NNN` nos artefatos vivos e templates; o gate passa a reconhecer as duas notações e o C4 a medir perda por presença de ID (não por ausência no diff).
**Cobre:** R1 (MUDA R6), R2 (MUDA R7), R3 (MUDA R12)
**Decisões duráveis → ADRs:** nenhuma
**Riscos assumidos:** a migração em massa dos sufixos do TRUTH exigiu refinar o C4 (mede ID no arquivo resultante) para não acusar CRÍTICO em cadeia; TDD no T1 (lógica pura de parser).

---

# delta-006 — notação delta-NNN — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** conteúdo vivo do framework identifica deltas por `delta-NNN`; `check_cycle.py` aceita `(ΔNNN)` e `(delta-NNN)`, e o C4 só acusa perda quando o ID some do TRUTH.md resultante.

**Architecture:** o único código acoplado é a regex `ALVO` ([check_cycle.py:30](skills/spec-feature/scripts/check_cycle.py#L30)). A migração de sufixos em massa no TRUTH.md dispararia o C4 (CRÍTICO por ID em linha removida do diff) — por isso o C4 passa a ler o TRUTH resultante e só acusar IDs realmente ausentes. Templates e docs vivos são substituição textual mecânica.

**Tech Stack:** Python 3.11+ (gate), Markdown (docs/templates).

## Global Constraints

- Idioma PT-BR; Conventional Commits escopo de skill: `feat(spec-feature): ...` (MINOR — capacidade nova).
- Notação nova só em conteúdo vivo; histórico imutável (ADRs, `_archive/`, CHANGELOG lançado, tabela Histórico do STATE) intocado.
- TDD no T1 (parser puro): fixture antes da implementação. T2–T5 são edição de dado — sem teste.

---

### Task 1: check_cycle.py — dupla notação + C4 por presença de ID (TDD)

**Files:**
- Modify: `skills/spec-feature/scripts/check_cycle.py` (regex `ALVO` L30; msg L143; `c4_archive` L138-161; `selftest`/`selftest_c4` fixtures)

**Interfaces:**
- Consumes: nada.
- Produces: `ALVO` aceitando as duas notações; `c4_archive` que não acusa reescrita de sufixo.

- [ ] **Step 1: Atualizar as fixtures do selftest para a notação nova + caso misto (falha primeiro)**

Em `selftest`: `# Δ 001 — x` → `# delta-001 — x` (duas fixtures, L241 e L283). Em `selftest_c4`, adicionar um terceiro caso `rodar(reescreve_sufixo=True)`: TRUTH base `- R1 (Δ000) — a\n- R2 (Δ000) — b\n` → resultante `- R1 (delta-000) — a\n- R2 (delta-000) — b\n`, spec vazio (sem MUDA) → **espera `[]`** (reescrita não é perda). Rodar antes de implementar: deve FALHAR (C4 atual acusa R1/R2 como perdidos).

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest`
Expected: AssertionError no caso novo (prova que a lógica atual erra).

- [ ] **Step 2: Ampliar a regex ALVO**

Linha 30:
```python
ALVO = re.compile(r"\b(R(?:NF)?\d+)\s*\((?:Δ\s*|delta-)\d+\)")
```

- [ ] **Step 3: C4 mede perda por presença de ID no TRUTH resultante**

Em `c4_archive`, após montar `perdidos` do diff, filtrar pelos IDs que ainda existem no TRUTH.md do working tree (estado resultante):
```python
truth_atual = (root / "specs" / "TRUTH.md")
presentes = set(ALVO.findall(truth_atual.read_text(encoding="utf-8"))) if truth_atual.is_file() else set()
perdidos = {rid for rid in perdidos if rid not in presentes}
```
(O `ALVO.findall` devolve o grupo 1 = o ID `Rn`/`RNFn`, então `presentes` é o conjunto de IDs ainda no arquivo.)

- [ ] **Step 4: Atualizar a mensagem-exemplo da linha 143**

`"declarar o alvo (ex.: 'MUDA R2 (Δ001)')"` → `"declarar o alvo (ex.: 'MUDA R2 (delta-001)')"`.

- [ ] **Step 5: Selftest verde**

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest`
Expected: `selftest: OK (...)` + `selftest C4: OK (...)`, incluindo o caso de reescrita de sufixo.

- [ ] **Step 6: Commit**

```bash
git add skills/spec-feature/scripts/check_cycle.py specs/006-notacao-delta/tasks.md
git commit -m "feat(spec-feature): gate reconhece delta-NNN e Δ; C4 mede perda por ID

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: Templates emitem delta-NNN

**Files:** `skills/spec-feature/references/templates/delta-spec.md` (L1), `.../tasks.md` (L1), `.../resumo-plan.md` (L3), `.../TRUTH.md` (L6, L10), `skills/spec-feature/references/analyze.md` (L60 — modelo de relatório)

- [ ] **Step 1: Substituir a notação nos templates**

`# Δ {{NNN}}` → `# delta-{{NNN}}`; `Δ {{NNN}}` → `delta-{{NNN}}`; `(Δ{{NNN}})` → `(delta-{{NNN}})`.

- [ ] **Step 2: Verificar**

Run: `grep -rn 'Δ' skills/spec-feature/references/templates/ ; grep -n 'Δ' skills/spec-feature/references/analyze.md`
Expected: zero ocorrências.

- [ ] **Step 3: Commit** (`git commit -m "docs(spec-feature): templates emitem delta-NNN"`)

---

### Task 3: Docs vivos do framework

**Files:** `skills/spec-feature/SKILL.md` (L53, L61), `skills/spec-feature/references/cycle.md` (L29, L39, L72, L75, L80), `skills/spec-feature/references/analyze.md` (L52), `CLAUDE.md` (L68), `README.md` (L55)

- [ ] **Step 1: Substituir** `Δ001`→`delta-001`, `ΔNNN`→`delta-NNN`, `(Δ003)`→`(delta-003)`, `(ΔNNN)`→`(delta-NNN)`.
- [ ] **Step 2: Verificar** — `grep -rn 'Δ' CLAUDE.md README.md skills/` → zero.
- [ ] **Step 3: Commit** (`git commit -m "docs: migra menções vivas de Δ para delta-NNN"`)

---

### Task 4: Varredura do TRUTH.md do repo (depende de T1)

**Files:** `specs/TRUTH.md`

- [ ] **Step 1: Migrar sufixos + comentário do cabeçalho**

`(Δ000)`→`(delta-000)`, `(Δ001)`→`(delta-001)`, etc. (todos os sufixos); comentário L4–5 (`Δ000`/`Δ001`) idem; exemplo interno de R6 (`"MUDA R2 (Δ001)"`) — esse texto muda aqui só na consolidação do archive, **não** no implement. No implement migra-se só os sufixos e o comentário.

- [ ] **Step 2: Rodar o gate na delta (o C4 refinado não acusa a migração)**

Run: `python3 skills/spec-feature/scripts/check_cycle.py specs/006-notacao-delta`
Expected: veredito LIBERADO (sem CRÍTICO — todos os IDs seguem no arquivo).

- [ ] **Step 3: Commit** (`git commit -m "docs: migra sufixos do TRUTH.md para delta-NNN"`)

---

### Task 5: STATE.md (vivo) + CHANGELOG

**Files:** `STATE.md`, `CHANGELOG.md`

- [ ] **Step 1: STATE** — menções `Δ` **fora** da tabela Histórico → `delta-NNN` (a pegadinha "`Δ000` é convenção" e afins); remover a proposta da notação de "Decisões em aberto" (virou realidade). Tabela Histórico e linhas já lançadas: intocadas.
- [ ] **Step 2: CHANGELOG** — sob `[Não lançado]`: `### Adicionado` (gate reconhece `delta-NNN` além de `Δ`; C4 mede perda por ID) + `### Mudado` (docs/templates emitem `delta-NNN`). (delta-006)
- [ ] **Step 3: Verificação final** — `grep -rn 'Δ' CLAUDE.md README.md skills/ specs/TRUTH.md STATE.md` → zero fora de `_archive`/tabela Histórico.
- [ ] **Step 4: Commit** (`git commit -m "docs: registra a migração delta-NNN no STATE e CHANGELOG"`)

---

## Self-Review

1. **Spec coverage:** R1/R2/R3 (MUDA R6/R7/R12) — os textos consolidam no archive; a capacidade (dupla notação, C4 por ID) é T1; a emissão `delta-NNN` é T2–T5. Cada Rn tem task com `cobre:`.
2. **Placeholder scan:** sem TBD/TODO.
3. **Type consistency:** `ALVO.findall` devolve grupo único (o ID) — usado consistentemente em `alvos`, `perdidos` e `presentes`.
