# Tasks — Δ 004
<!-- ordenado por dependência; cada task executável sem contexto extra -->
- [x] T1 — trocar os excludes `**`-final do template pela forma `**/*.md` (comentário do porquê) remover o débito do STATE.md e registrar em Corrigido do CHANGELOG.md · arquivos: `skills/guarding-doc-integrity/templates/deps.toml`, `STATE.md`, `CHANGELOG.md` · cobre: R1 · verificação: `grep -rn '\*\*"' skills/ deps.toml` sem `**"` solto + `python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest` PASS
