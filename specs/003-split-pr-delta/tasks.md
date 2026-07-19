# Tasks — Δ 003
<!-- ordenado por dependência; cada task executável sem contexto extra -->
- [x] T1 — adicionar a subseção "PR da delta — split condicional" ao cycle.md · arquivos: skills/spec-feature/references/cycle.md · cobre: R1 · verificação: python3 skills/guarding-doc-integrity/scripts/validate_integrity.py . retorna PASS (limiar não materializado)
- [x] T2 (dep: T1) — registrar a medição como saída extra do gate no analyze.md · arquivos: skills/spec-feature/references/analyze.md · cobre: R1 · verificação: python3 skills/spec-feature/scripts/check_cycle.py specs/003-split-pr-delta sai 0 e a medição da própria Δ003 fica no rodapé do analyze.md
