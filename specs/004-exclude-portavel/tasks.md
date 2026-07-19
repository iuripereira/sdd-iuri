# Tasks — Δ 004
<!-- ordenado por dependência; cada task executável sem contexto extra -->
- [ ] T1 — trocar os excludes `**`-final do template pela forma `**/*.md` (com comentário do
  porquê) e remover o item de débito correspondente do STATE.md · arquivos:
  `skills/guarding-doc-integrity/templates/deps.toml`, `STATE.md` · cobre: R1 · verificação:
  `grep -rn '\*\*"' skills/ deps.toml` sem ocorrência `**"` solta +
  `python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest` → PASS
