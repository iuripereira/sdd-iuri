# Analyze — delta-007 · 2026-07-19
| # | Severidade | Onde | Inconsistência | Ação sugerida |
|---|---|---|---|---|
| 1 | MÉDIO | PR da delta | Diff total projetado (artefatos + implementação ~12 arquivos .md + 1 .py) deve exceder o limiar canônico de PR mesmo sem split (artefatos sozinhos ficam dentro) | Registrar honestamente no corpo do PR, como no precedente da delta-001; não fatiar a migração (perderia atomicidade do MUDA R16 com seus 6 consumidores) |

**Checks humanos (3 e 5, além do script):**
- **3 — spec × plan:** resumo do plan cobre R1–R3; ADR-0007 declarada em "Decisões duráveis";
  nada no plano sem base na spec (backfill DT e migração do STATE são os cenários 1–2 de R2 e 2
  de R3). Sem scope creep.
- **4 — TRUTH:** R1 cita o alvo vigente "MUDA R16 (delta-002)" e repete integralmente o cenário 2
  do R16 que continua valendo (consolidação mecânica, ADR-0005). R2/R3 não conflitam com R3
  vigente (o scaffold segue dirigido pela matriz de detection.md — a delta só adiciona uma linha).
- **5 — regras canônicas:** destino da pendência muda **por MUDA R16 nesta delta** (não por edição
  avulsa); ADRs e `_archive/` intocados (imutabilidade); tag será cortada no archive (regra da
  tríade); nenhum valor de limiar materializado fora dos donos — `DEBT.md` entra em
  `exclude_globs` nos dois deps.toml (T7).

**Split condicional (R17):** `git diff origin/main --shortstat -- specs/007-registros-com-dono/`
→ **173 linhas adicionadas** (< limiar canônico de PR) → **PR único** carrega artefatos +
implementação.

**Veredito:** LIBERADO
