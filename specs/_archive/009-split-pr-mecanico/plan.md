<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** mecanizar a régua do split de PR como C7 no `check_cycle.py` (mede o diff dos artefatos da delta vs merge-base, reporta BAIXO acima do limiar de PR). **Cobre:** R1 (MUDA R12) da delta-009. **Decisões duráveis → ADRs:** nenhuma (aplica R17/R12 vigentes; sem renúncia de alternativa nova). **Riscos assumidos:** materializa `500` no `.py` (novo espelho sancionado no `deps.toml`, C1 sincroniza); herda a janela cega do merge-base do C4 (DT-007), sem piorá-la.

---

## Plano de implementação (TDD)

Tipo `tooling` → TDD recomendado (default on). O C7 é lógica pura sobre saída de `git diff` + um limiar; testável pelo selftest co-localizado, como C4. TDD aplicado: fixture do selftest antes da função.

### Passo 1 — constante e sanção do limiar (deps.toml)
- Adicionar `PR_LIMITE = 500` ao topo do `check_cycle.py`, junto de `TRUTH_LIMITE`.
- No `deps.toml`, adicionar `skills/spec-feature/scripts/check_cycle.py` aos `mirrors` do dono `canonical-rules.md` (bloco `pr-limiar-tamanho`). Atualizar o comentário do bloco: de "1 espelho" para "2 espelhos (CLAUDE.md + a constante do gate)".
- Verificação: `validate_integrity.py` verde (C1 acha `500` no dono + 2 espelhos; C2 intacto — `.py` fora do scan).

### Passo 2 — selftest do C7 (RED)
- Adicionar `selftest_c7()` no mesmo molde do `selftest_c4()` (git real, PULADO sem git): monta um repo com base na `main`, cria `specs/009-x/` com artefato > `PR_LIMITE` linhas numa branch, roda `c7_split(root, delta, v)` e afirma BAIXO com o nome do arquivo e a contagem; segundo caso com artefato pequeno afirma `v == []`.
- Chamar `selftest_c7()` ao fim de `selftest()` (depois de `selftest_c4()`).
- Verificação: `check_cycle.py --selftest` falha (função ainda não existe) — o RED.

### Passo 3 — função c7_split (GREEN)
- `c7_split(root, delta, v)`: reusa `base_c4(root)`; `git diff <base> --numstat -- <delta-rel>`; soma a coluna de inserções (ignora linhas binárias `-`); se `> PR_LIMITE`, `v.append(("BAIXO", str(delta-rel), f"{n} linhas adicionadas (limiar {PR_LIMITE})", "abrir primeiro o PR só dos artefatos — split condicional, cycle.md"))`. Sem git/erro → return (omite), como o C4.
- Chamar `c7_split(root, delta, v)` em `checar()`, após `c6_pendencias`.
- Verificação: `check_cycle.py --selftest` verde; `check_cycle.py specs/009-split-pr-mecanico` roda o C7 sem quebrar.

### Passo 4 — consumidores no mesmo change
- `check_cycle.py`: docstring (lista de checks C1–C6 → C1–C7; linha "Automatiza..." menciona o split).
- `analyze.md`: a "Saída extra com LIBERADO" (linha 31) passa a dizer que o C7 mede automaticamente; o humano confere o rodapé em vez de medir a olho.
- `cycle.md`: se cita "C1–C6", ajustar para C7 (grep antes).
- Verificação: `grep -rn 'C6\b\|C1–C6\|C1-C6'` nos docs do ciclo — nenhuma menção defasada.

### Passo 5 — registros
- CHANGELOG `[Não lançado]`: Adicionado (C7). STATE: Agora/Feito. DT-003 → o archive o quita (natureza pendência) na consolidação, junto do MUDA R12 no TRUTH.md.

**Riscos assumidos:** ver cabeçalho.
