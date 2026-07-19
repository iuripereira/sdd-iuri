<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** declarar o fallback do review estágio 1 no `adapters.md` e corrigir no TRUTH.md (via archive) as duas redações imprecisas do backfill Δ000.
**Cobre:** R1, RNF1, RNF2 (da Δ005)
**Decisões duráveis → ADRs:** nenhuma
**Riscos assumidos:** nenhum novo — edições de documentação; TDD dispensado (sem lógica; justificativa na T1).

---

# Δ005 — achados da revisão do backfill Δ000 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** o `adapters.md` passa a declarar fallback para **todas** as fases da tabela de contrato (fechando o furo do review estágio 1); as redações de R13/RNF3 corrigidas entram no TRUTH.md na consolidação do archive.

**Architecture:** duas frentes. (1) `adapters.md`: a seção Superpowers ganha o fallback do review estágio 1 — conferência inline da spec contra o diff, com aviso de degradação. (2) TRUTH.md: os blocos MUDA da spec substituem R13/RNF2/RNF3 integralmente no archive (mecânica padrão do ciclo); no implement só se verifica que nenhum artefato de skill reproduz as frases antigas.

**Tech Stack:** Markdown; Python 3.11+ só para os gates.

## Global Constraints

- Idioma PT-BR; Conventional Commits com escopo da skill: `fix(spec-feature): ...`.
- Só `skills/spec-feature/references/adapters.md` e `CHANGELOG.md` mudam no implement; TRUTH.md muda apenas no archive.
- TDD dispensado (tipo tooling, dispensa por task permitida): edição de documentação, sem lógica nova — não há teste a escrever (renúncia no spec.md).

---

### Task 1: Fallback do review estágio 1 no adapters.md + CHANGELOG

**Files:**
- Modify: `skills/spec-feature/references/adapters.md` (seção "## Superpowers")
- Modify: `CHANGELOG.md` (`### Corrigido` sob `[Não lançado]`)

**Interfaces:**
- Consumes: nada (task única de edição).
- Produces: seção de fallback cobrindo review estágio 1; verificação do RNF2 (cada motor da tabela com fallback declarado) passa a ser satisfeita.

- [ ] **Step 1: Declarar o fallback no adapters.md**

Na seção `## Superpowers`, após o bullet `**Fallback (superpowers ausente):** gere \`plan.md\` próprio (...)`, adicionar:

```markdown
- **Fallback do review estágio 1 (superpowers ausente):** conduza a conferência inline —
  cada Rn/RNFn da spec confrontado com o diff da delta, com veredito por requisito — e
  registre o aviso *"review estágio 1 degradado: superpowers/requesting-code-review não
  instalado"*. O estágio 2 segue o fallback do ponytail abaixo.
```

- [ ] **Step 2: Verificar cobertura de fallback por linha da tabela**

Run: `grep -n "Fallback" skills/spec-feature/references/adapters.md`
Expected: seções de fallback cobrindo clarify (max), plan+implement (superpowers), review estágio 1 (superpowers), review estágio 2/transversal (ponytail) — todas as linhas da tabela de contrato.

- [ ] **Step 3: Verificar que as frases antigas de R13/RNF3 não vivem em artefato de skill**

Run: `grep -rn "só o TRUTH.md consolidado está no escopo\|no-op relatado" skills/`
Expected: nenhuma ocorrência (as frases só existiam no `specs/TRUTH.md`, que o archive substitui).

- [ ] **Step 4: Entrada no CHANGELOG.md**

Sob `## [Não lançado]`, adicionar:

```markdown
### Corrigido
- `adapters.md` declara o fallback do review estágio 1 (conferência inline com aviso) —
  fecha o furo do RNF2 apontado pela revisão do backfill Δ000; redações de R13/RNF3
  corrigidas na consolidação. (Δ005)
```

- [ ] **Step 5: Commit**

```bash
git add skills/spec-feature/references/adapters.md CHANGELOG.md
git commit -m "fix(spec-feature): declara o fallback do review estágio 1 no adapters.md

Fecha o furo do RNF2 (toda fase com motor de terceiro tem fallback
declarado) apontado pela revisão do backfill Δ000.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Self-Review

1. **Spec coverage:** RNF1 (fallback por motor) ↔ Steps 1–2; R1 e RNF2 (redações) ↔ Step 3 no implement + consolidação mecânica no archive. Sem gaps.
2. **Placeholder scan:** sem TBD/TODO.
3. **Type consistency:** n/a (sem código).
