# STATE.md — estado atual (as-built)

> Handoff vivo. Reflete o que o projeto **é** agora, não o que se planeja (isso vive no
> `specs/TRUTH.md` e nas deltas). Atualize no mesmo commit de toda mudança relevante. Em conflito
> de merge, mantenha a **união das verdades** — nunca sobrescreva o progresso de outra sessão.

**Atualizado em:** 2026-07-19

## O que existe

- **5 skills do framework** em `skills/`, distribuídas como plugin `sdd-iuri` e invocadas sob esse
  namespace: `projeto-init`, `projeto-infra`, `spec-feature`, `spec-review`,
  `guarding-doc-integrity`. Manifesto em `.claude-plugin/plugin.json` (sem campo `version`: a tag
  git é a fonte da verdade e ainda não há tag).
- **2 gates determinísticos**, ambos com `--selftest` rodado no CI:
  `skills/spec-feature/scripts/check_cycle.py` (C1–C6 do ciclo) e
  `skills/guarding-doc-integrity/scripts/validate_integrity.py` (C1–C3 de espelhos). São
  referenciados por `${CLAUDE_PLUGIN_ROOT}`, com step de CI que reprova caminho absoluto (RNF5).
- **Infra**: ruleset `sdd-protect-main` (PR obrigatório + check `ci` verde), workflows `ci`
  (JSON/TOML/YAML, frontmatter, selftests, integridade documental) e `conventional-commits`.
- **Governança de espelhos aplicada ao próprio repo**: `deps.toml` na raiz mapeia os dois
  limiares espelhados (particionamento do TRUTH.md → dono RNF1 em `specs/TRUTH.md`; tamanho
  de PR → dono `canonical-rules.md`), e `validate_integrity.py` roda contra o repo no job `ci`.
- **Scaffold próprio**: este arquivo, `CLAUDE.md`, `CHANGELOG.md`, `docs/adrs/`, `specs/TRUTH.md`
  com backfill Δ000 do que já vige.

## O que falta

- CI dos gates dentro dos projetos do usuário (ver `docs/adrs/ADR-0001`).
- Backfill assistido de `TRUTH.md` em brownfield: existe como tarefa sob demanda, não como fase.

## Decisões em aberto

- **Release inicial.** Não há tag; a versão canônica é a tag git, então o repo está formalmente
  pré-`v0.1.0`. Falta decidir se o scaffold atual já justifica cortar a primeira. A Δ001 agravou:
  foi `feat!` (BREAKING) mergeada sem baseline para classificar o bump.
- **Vendoring dos scripts de gate** nos projetos gerados — a alternativa ao "rodar local" da
  ADR-0001, caso o gate no CI do projeto passe a ser requisito.
- **O limiar de PR ≤ 500 linhas conta os artefatos efêmeros da delta.** 2 de 2 deltas estouraram
  por causa do `plan.md` (Δ001: 913; Δ002: 626, sendo ~410 de plan) — o débito foi declarado nos
  dois PRs. Decidir se o limiar passa a excluir `specs/` (medir só código + docs duráveis) ou se
  o limite é esse mesmo; a regra canônica é o dono do valor.

## Pegadinhas / débito conhecido

- **A allowlist do `.gitignore` cobrou seu preço ao morrer.** Enquanto existiu, `git add -A` pulava
  em silêncio qualquer artefato novo da raiz. Na execução da Δ001 ela engoliu o
  `.claude-plugin/plugin.json` — o commit "adiciona o manifesto" não continha o manifesto, e a
  verificação passou porque testava o arquivo em disco, não no git. Lição que sobrevive à
  allowlist: **verificação de "arquivo existe" deve consultar `git ls-files`, não o filesystem.**
- **`check_cycle.py` é acoplado ao formato do `delta-spec.md`** (um requisito por bloco
  `### Rn — VERBO`). Spec fora do template gera "nenhum bloco encontrado" (ALTO) em vez de
  analisar — falha ruidosa, não silenciosa. Marcado com `ponytail:` no script. Corrigir quando/se
  o template mudar de forma.
- **`Δ000` é convenção, não fase.** É o rótulo do backfill pré-ciclo no `TRUTH.md`; deltas reais
  começam em `Δ001`. Nenhum diretório `specs/000-*/` existe nem deve existir.
- **O TRUTH.md (Δ000) nunca foi revisado.** Os 14 requisitos e 4 RNFs são sumarização de um passe,
  sem validação contra as skills. É a raiz da árvore — erro ali é herdado por todo MUDA futuro, e o
  C4 protege a integridade da consolidação, não a correção do conteúdo.
- **Determinismo só alcança o papel.** `implement` e `review` — onde o dano real acontece — não têm
  gate mecânico. Consciente, mas registrado: o esforço cobriu o perímetro mais barato de errar.
- **Evidência 100% auto-referencial.** O framework nunca rodou em projeto que não seja ele mesmo.
- **Zero tags em 5 merges, contra a própria tríade de release.** A regra canônica diz "Tag = release
  a cada merge na `main`"; os PRs #2 e #3 foram `feat` e não geraram tag. Consequência: qualquer
  classificação de bump (MINOR/MAJOR) é decorativa enquanto não houver linha de base, e não existe
  ponto de retorno versionado. Corrigir antes ou logo depois da Δ001 — se antes, cortar `v0.1.0`
  cria o baseline pré-plugin. Nenhum gate percebe a violação hoje: o `analyze` checa regra canônica,
  mas não olha estado de release.
- **Renomear um termo citado em N requisitos custa N blocos MUDA completos.** Observado na Δ001:
  trocar a forma de citar as skills exigiu cinco blocos, cada um repetindo o requisito íntegro. É o
  preço da consolidação mecânica do archive (`cycle.md`, regra 2) — o archive não infere intenção,
  então o cenário que não for repetido se perde. Funcionando como projetado; reavaliar só se o
  padrão se repetir em outra delta.
- **ADR-0001 cita `~/.claude/skills/<skill>/scripts/`, caminho extinto pela Δ001.** Não corrigir:
  ADR é imutável após Accepted e a decisão (gates rodam local) segue válida — o caminho é contexto
  histórico. Registrado para ninguém "consertar" o ADR por engano; o grep do RNF5 deliberadamente
  não varre `docs/`.
- **O `templates/deps.toml` da `guarding-doc-integrity` exclui `**/_archive/**` — no-op em
  Python ≤ 3.12.** `pathlib.glob` só casa diretórios num `**` final, então o exclude não filtra
  nada; o `deps.toml` deste repo usa a forma portável `**/_archive/**/*.md`. Corrigir o template
  passa pelo ciclo (é mudança de skill) — candidato a entrar na próxima delta.
- **O limiar de PR tem 4 espelhos sancionados no `deps.toml`, acima do teto de 2–3 da skill.**
  Baseline consciente do estado atual; enxugar junto com a decisão aberta sobre o limiar.
- **Metade do gate analyze continua humana** por design (scope creep spec×plan, violação de regra
  canônica). Não é débito a corrigir — é limite reconhecido; automatizar produziria falso negativo
  confiante.

## Histórico de alterações

| Data (AAAA-MM-DD) | Mudança | Ref |
|---|---|---|
| 2026-07-19 | `deps.toml` do repo: limiares do TRUTH e de PR com dono/espelhos; gate de integridade no `ci` | #9 |
| 2026-07-18 | Δ002 arquivada: TRUTH consolidado (R16, MUDA R12/RNF4/RNF5), delta em `_archive/` | Δ002 |
| 2026-07-18 | Δ002: C4 via merge-base + selftest git real, C6 de pendência, saída parcial, grep RNF5 ampliado | #7 |
| 2026-07-18 | Δ001 arquivada: review pós-merge (2 importantes, 4 menores — tratados), TRUTH consolidado (R15, RNF5, 5 MUDA), delta em `_archive/` | Δ001 |
| 2026-07-18 | Δ001 implementada: repo vira o plugin `sdd-iuri` — skills em `skills/`, namespace `sdd-iuri:`, `${CLAUDE_PLUGIN_ROOT}` | #5 |
| 2026-07-18 | `projeto-init` aplicado ao próprio repo: CLAUDE.md, scaffold e TRUTH.md com backfill Δ000 | #4 |
| 2026-07-18 | `guarding-doc-integrity` integrada ao framework; regra de propagação ganha executor | #3 |
| 2026-07-18 | `check_cycle.py`: primeiro gate determinístico do ciclo | #2 |
