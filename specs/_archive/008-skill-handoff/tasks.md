# Tasks — delta-008
<!-- ordenado por dependência; cada task executável sem contexto extra -->
- [x] T1 — criar skills/handoff/SKILL.md (frontmatter EN + corpo PT-BR conforme plan) · arquivos: skills/handoff/SKILL.md · cobre: R1 · verificação: head -1 é ---, grep ^name: e ^description: passam; grep "DEBT.md" e "diário de bordo" no corpo
- [x] T2 — tirar a contagem da redação viva e registrar a 6ª skill · arquivos: CLAUDE.md, README.md, .claude-plugin/plugin.json · cobre: R2 · verificação: grep -rn "cinco skills" CLAUDE.md README.md .claude-plugin/ retorna vazio; python3 -m json.tool .claude-plugin/plugin.json
- [x] T3 (dep: T1) — linha do /sdd-iuri:handoff na tabela de comandos do README · arquivos: README.md · cobre: R1 · verificação: grep "sdd-iuri:handoff" README.md
- [x] T4 (dep: T1..T3) — CHANGELOG em [Não lançado] e STATE.md (diário) no mesmo change · arquivos: CHANGELOG.md, STATE.md · cobre: infra · verificação: grep "delta-008" CHANGELOG.md STATE.md
