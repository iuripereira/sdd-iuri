# Δ 004 — exclude-portavel
Estado: arquivada · Data: 2026-07-19 · Branch: fix/004-exclude-portavel

## Contexto (≤3 linhas)
Os `exclude_globs` do `templates/deps.toml` da `guarding-doc-integrity` terminam em `**` —
no-op em `pathlib` ≤ 3.12 (casa só diretórios). O `deps.toml` deste repo já usa a forma
portável; o template distribuído aos usuários segue com o bug (STATE.md, débito conhecido).

## Mudanças
### R1 — MUDA R13 (Δ000): todo glob de exclude no template referência arquivos, não diretórios
> Bloco integral do R13 vigente, com o cenário novo ao final; os dois primeiros cenários
> permanecem como estão no TRUTH.md.

R13 — valor de negócio duplicado entre arquivos é governado por manifesto e validado por script.
- DADO um repo com `deps.toml` QUANDO `validate_integrity.py` roda ENTÃO verifica espelhos em
  sincronia (C1), materialização fora dos sancionados (C2) e links relativos vivos (C3),
  saindo 1 em qualquer violação
- DADO uma delta ainda aberta propondo valor novo QUANDO o validador roda ENTÃO ela não é
  acusada — só o `TRUTH.md` consolidado está no escopo de varredura
- DADO o `templates/deps.toml` da skill QUANDO um `exclude_globs` mira conteúdo de diretório
  ENTÃO o glob termina em `**/*.md` (nunca em `**` solto), com comentário no template
  explicando o porquê — `pathlib` ≤ 3.12 casa só diretórios num `**` final e o exclude
  viraria no-op

## Requisitos não funcionais
<!-- sem RNF: correção pontual de template, sem qualidade nova a medir -->

## Fora de escopo
- Mudar `scan_globs` ou a lógica de `collect()` no `validate_integrity.py` — o script está
  correto; o bug é só nos globs de exemplo do template. Normalizar o `**` final dentro de
  `collect()` foi considerado e rejeitado: o `deps.toml` da raiz já fixou a convenção
  contrária (globs portáveis, script com semântica `pathlib` pura — magia no glob
  surpreenderia quem conhece o padrão).
- Detectar `**` final mecanicamente (novo check no validador) — YAGNI até reincidir.
- Fixture nova no `--selftest` para o exclude — a lógica do script não muda; testar o
  comportamento do `pathlib` seria testar o Python, não o framework.

## Dependências e riscos
- O `deps.toml` deste repo (raiz) já usa a forma portável — é a referência do fix, nada a
  migrar aqui.
- Python 3.13+ mudou o `glob`: `**` final passou a casar arquivos também. A forma `**/*.md`
  é a única com comportamento idêntico nas duas famílias — por isso o template a adota.

## Clarify — relatório de ambiguidade (grill-me, modo spec)
<!-- gate do clarify; dúvidas resolvidas por exploração do código, sem entrevista -->
```
Goals:        0.0   ✓ dois globs, forma-alvo e comentário definidos
Acceptance:   0.0   ✓ cenário verificável por grep no template
Boundaries:   0.0   ✓ fora de escopo explícito (collect(), check novo, fixture)
Alternatives: 0.25  ✓ normalização no script considerada e rejeitada com porquê
Assumptions:  0.25  ✓ semântica 3.12/3.13 respaldada no comentário do deps.toml da raiz
──────────────────────────────
Aggregate:    0.10  ✓ abaixo do limiar (0.2 spec)
```
