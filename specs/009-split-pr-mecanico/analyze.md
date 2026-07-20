# Analyze — delta-009 · 2026-07-20
| # | Severidade | Onde | Inconsistência | Ação sugerida |
|---|---|---|---|---|

**Veredito:** LIBERADO

Metade mecânica (`check_cycle.py specs/009-split-pr-mecanico`): sem achados — C1 (aceite do R1), C2 (T1–T5 cobrem R1/infra, todas com verificação), C3/C4/C5/C6 limpos.

Metade humana (checks 3 e 5 do `analyze.md`):
- **spec × plan (scope creep):** resumo do plan cobre R1 e nada além; o plano implementa só o C7. Sem creep.
- **TRUTH.md:** R1 é MUDA R12 (delta-006) declarado, repetindo os 4 cenários vigentes + o C7 no primeiro + o cenário novo do split; não duplica nem conflita com R17 (mecaniza a medição que o R17 já prevê manualmente).
- **regras canônicas:** `500` materializado no `.py` é constante nomeada (`PR_LIMITE`) e espelho sancionado no `deps.toml` (par do `TRUTH_LIMITE=800`), não valor mágico; changelog PT-BR; sem clobber; fonte da versão = tag git.

**Forma do PR (split condicional, R17):** medir `git diff origin/main --shortstat -- specs/009-split-pr-mecanico/` no fim da implementação. Artefatos + implementação previstos bem abaixo do limiar — PR único esperado.
