<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** trocar os dois excludes `**`-final do `templates/deps.toml` pela forma portável `**/*.md`, com comentário explicando o porquê.
**Cobre:** R1 (da Δ004)
**Decisões duráveis → ADRs:** nenhuma (a convenção já estava fixada no `deps.toml` da raiz)
**Riscos assumidos:** nenhum novo — mudança de dado (template), sem toque em lógica; TDD dispensado por task (justificativa na T1).

---

# Δ004 — exclude portável no template deps.toml — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** os `exclude_globs` do template distribuído pela `guarding-doc-integrity` passam a usar globs que funcionam identicamente em Python ≤ 3.12 e 3.13+.

**Architecture:** mudança de dado num único arquivo TOML de template. `pathlib.Path.glob` em Python ≤ 3.12 casa só diretórios num `**` final; como `collect()` (validate_integrity.py:39-43) filtra `is_file()`, um exclude `**`-final vira no-op. A forma `**/*.md` casa arquivos em todas as versões. O script não muda.

**Tech Stack:** TOML (template), Python 3.11+ (só para rodar a verificação).

## Global Constraints

- Idioma PT-BR em comentários e commits (CLAUDE.md).
- Commit no padrão Conventional Commits, escopo = nome da skill: `fix(guarding-doc-integrity): ...`.
- Nenhum valor mágico novo; nenhuma mudança fora de `skills/guarding-doc-integrity/templates/deps.toml` e `STATE.md`.
- TDD dispensado nesta delta (tipo tooling, dispensa por task permitida): a mudança é dado puro num template — não há lógica nova a testar; testar o glob seria testar o `pathlib` (renúncia registrada no spec.md, "Fora de escopo").

---

### Task 1: Globs portáveis no template + débito quitado no STATE.md

**Files:**
- Modify: `skills/guarding-doc-integrity/templates/deps.toml:12-13`
- Modify: `STATE.md` (remover o item de débito "O `templates/deps.toml` da `guarding-doc-integrity` exclui `**/_archive/**`...")
- Modify: `CHANGELOG.md` (entrada em `Corrigido` sob `[Não lançado]` — achado do analyze, check 5)

**Interfaces:**
- Consumes: nada de outras tasks (task única).
- Produces: template corrigido; nenhum consumidor de código depende dele (verificado no clarify: SKILL.md não materializa os globs; selftest usa `exclude_globs = []`).

- [ ] **Step 1: Editar os excludes do template**

Em `skills/guarding-doc-integrity/templates/deps.toml`, substituir as linhas 12–13:

```toml
# Onde citar valores é legítimo (changelogs, CRs, deltas arquivadas):
exclude_globs = ["CHANGELOG.md", "docs/changes/**", "**/_archive/**"]
```

por:

```toml
# Onde citar valores é legítimo (changelogs, CRs, deltas arquivadas).
# Globs de diretório terminam em '**/*.md', nunca em '**' solto: pathlib em
# Python <= 3.12 casa só diretórios num '**' final e o exclude viraria no-op.
exclude_globs = ["CHANGELOG.md", "docs/changes/**/*.md", "**/_archive/**/*.md"]
```

- [ ] **Step 2: Verificar que não sobrou glob `**`-final no repo**

Run: `grep -rn '\*\*"' skills/ deps.toml`
Expected: toda ocorrência termina em `**/*.md"` (nenhuma em `**"` solto).

- [ ] **Step 3: Rodar o selftest do validador (consumidor intacto)**

Run: `python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest`
Expected: `RESULTADO: PASS` (fixtures não tocam o template; garante que nada quebrou por acidente).

- [ ] **Step 4: Remover o item de débito do STATE.md**

Em `STATE.md`, seção "Pegadinhas / débito conhecido", remover o item inteiro:

```markdown
- **O `templates/deps.toml` da `guarding-doc-integrity` exclui `**/_archive/**` — no-op em
  Python ≤ 3.12.** `pathlib.glob` só casa diretórios num `**` final, então o exclude não filtra
  nada; o `deps.toml` deste repo usa a forma portável `**/_archive/**/*.md`. Corrigir o template
  passa pelo ciclo (é mudança de skill) — candidato a entrar na próxima delta.
```

(A linha do "Histórico de alterações" entra no archive, não aqui.)

- [ ] **Step 4b: Entrada no CHANGELOG.md**

Sob `## [Não lançado]`, adicionar (criando o grupo `### Corrigido` se não existir):

```markdown
### Corrigido
- `templates/deps.toml` da `guarding-doc-integrity`: excludes `**`-final (no-op em
  `pathlib` ≤ 3.12) trocados pela forma portável `**/*.md`, com comentário do porquê. (Δ004)
```

- [ ] **Step 5: Commit**

```bash
git add skills/guarding-doc-integrity/templates/deps.toml STATE.md CHANGELOG.md
git commit -m "fix(guarding-doc-integrity): exclui com globs portáveis no template deps.toml

**/_archive/** e docs/changes/** eram no-op em pathlib <= 3.12 (** final
casa só diretórios). Forma **/*.md tem o mesmo efeito em 3.13+.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Self-Review

1. **Spec coverage:** R1 (cenário novo do MUDA R13 — excludes terminam em `**/*.md` com comentário) ↔ Task 1 Steps 1–2. Sem gaps; a delta não tem RNF.
2. **Placeholder scan:** sem TBD/TODO; todos os steps têm conteúdo literal.
3. **Type consistency:** n/a (sem código novo).
