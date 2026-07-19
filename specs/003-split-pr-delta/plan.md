<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** adicionar ao ciclo o split condicional do PR da delta — artefatos primeiro,
implementação depois — quando o diff de `specs/NNN-nome/` exceder o limiar canônico de PR.
**Cobre:** R1 (da Δ 003)
**Decisões duráveis → ADRs:** nenhuma — processo do ciclo, reversível por delta futura.
**Riscos assumidos:** regra manual (não mecanizada); pendência de mecanização registrada
na spec e roteada no archive.

## Passos

1. `cycle.md`: nova subseção "PR da delta — split condicional" logo após o parágrafo de
   fim de fase, com o comando de medição (`git diff origin/main --shortstat -- specs/NNN-nome/`),
   os dois desfechos (split / PR único) e as branches de cada PR (`docs/NNN-nome` para os
   artefatos, `tipo/NNN-nome` para a implementação). Referencia o limiar **sem** o número.
2. `analyze.md`: a medição vira saída extra do gate — com veredito LIBERADO, medir e registrar
   no rodapé do relatório qual forma de PR o ciclo segue.
3. **TDD dispensado** (justificativa exigida pelo repo): mudança documental sem lógica
   executável nova; a verificação é o `validate_integrity.py` (C2 acusa se o valor do limiar
   materializar fora dos sancionados) + `check_cycle.py` da própria delta.
