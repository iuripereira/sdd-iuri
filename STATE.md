# STATE.md — estado atual (as-built)

> Handoff vivo. Reflete o que o projeto **é** agora, não o que se planeja (isso vive no
> `specs/TRUTH.md` e nas deltas). Atualize no mesmo commit de toda mudança relevante. Em conflito
> de merge, mantenha a **união das verdades** — nunca sobrescreva o progresso de outra sessão.

**Atualizado em:** 2026-07-18

## O que existe

- **5 skills do framework**, versionadas por allowlist no `.gitignore`: `projeto-init`,
  `projeto-infra`, `spec-feature`, `spec-review`, `guarding-doc-integrity`. As demais pastas de
  `~/.claude/skills` são pessoais e ficam fora do git.
- **2 gates determinísticos**, ambos com `--selftest` rodado no CI:
  `spec-feature/scripts/check_cycle.py` (C1–C5 do ciclo) e
  `guarding-doc-integrity/scripts/validate_integrity.py` (C1–C3 de espelhos).
- **Infra**: ruleset `sdd-protect-main` (PR obrigatório + check `ci` verde), workflows `ci`
  (JSON/TOML/YAML, frontmatter, selftests) e `conventional-commits`.
- **Scaffold próprio**: este arquivo, `CLAUDE.md`, `CHANGELOG.md`, `docs/adrs/`, `specs/TRUTH.md`
  com backfill Δ000 do que já vige.

## O que falta

- Rodar o ciclo de verdade: a Δ001 ainda não existe. As mudanças até aqui entraram como PR direto,
  não como delta spec — o framework passou a se aplicar a si mesmo só a partir deste commit.
- CI dos gates dentro dos projetos do usuário (ver `docs/adrs/ADR-0001`).
- Backfill assistido de `TRUTH.md` em brownfield: existe como tarefa sob demanda, não como fase.
- **`deps.toml` deste repo.** O framework tem valores espelhados que hoje ninguém governa: o limiar
  de particionamento do TRUTH aparece em 7 arquivos e o de tamanho de PR em 5. É exatamente o caso
  de uso da `guarding-doc-integrity`, ainda não aplicado aqui — o bootstrap exige decidir dono e
  espelhos sancionados com o usuário.

## Decisões em aberto

- **Release inicial.** Não há tag; a versão canônica é a tag git, então o repo está formalmente
  pré-`v0.1.0`. Falta decidir se o scaffold atual já justifica cortar a primeira.
- **Vendoring dos scripts de gate** nos projetos gerados — a alternativa ao "rodar local" da
  ADR-0001, caso o gate no CI do projeto passe a ser requisito.

## Pegadinhas / débito conhecido

- **O `.gitignore` é uma allowlist** (`/*` + `!/nome/`), não uma denylist. Consequência: um arquivo
  novo na raiz **não é versionado** até ganhar sua linha `!/...`. Skill nova do framework ou
  artefato novo de scaffold exige editar o `.gitignore` no mesmo commit.
- **`check_cycle.py` é acoplado ao formato do `delta-spec.md`** (um requisito por bloco
  `### Rn — VERBO`). Spec fora do template gera "nenhum bloco encontrado" (ALTO) em vez de
  analisar — falha ruidosa, não silenciosa. Marcado com `ponytail:` no script. Corrigir quando/se
  o template mudar de forma.
- **`Δ000` é convenção, não fase.** É o rótulo do backfill pré-ciclo no `TRUTH.md`; deltas reais
  começam em `Δ001`. Nenhum diretório `specs/000-*/` existe nem deve existir.
- **Metade do gate analyze continua humana** por design (scope creep spec×plan, violação de regra
  canônica). Não é débito a corrigir — é limite reconhecido; automatizar produziria falso negativo
  confiante.

## Histórico de alterações

| Data (AAAA-MM-DD) | Mudança | Ref |
|---|---|---|
| 2026-07-18 | `projeto-init` aplicado ao próprio repo: CLAUDE.md, scaffold e TRUTH.md com backfill Δ000 | #4 |
| 2026-07-18 | `guarding-doc-integrity` integrada ao framework; regra de propagação ganha executor | #3 |
| 2026-07-18 | `check_cycle.py`: primeiro gate determinístico do ciclo | #2 |
