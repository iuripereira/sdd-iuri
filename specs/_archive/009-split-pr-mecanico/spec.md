# delta-009 — split de PR mecânico (C7)
Estado: arquivada · Data: 2026-07-20 · Branch: feat/009-split-pr-mecanico

## Contexto (≤3 linhas)
A régua do split condicional de PR (R17) é manual — o analyze mede `git diff` a olho e registra no rodapé. DT-003 pede mecanizá-la: um check no `check_cycle.py` que mede o diff dos artefatos da delta e sinaliza quando passa do limiar de PR.

## Mudanças
<!-- só o que muda; um bloco por requisito; ADICIONA/MUDA/REMOVE em relação ao TRUTH.md -->
### R1 — MUDA R12 (delta-006): a metade mecânica do analyze é um script, não diligência.
- DADO uma delta QUANDO `check_cycle.py` roda ENTÃO ele verifica aceite (C1), cobertura spec↔tasks (C2), estado × localização (C3), archive sem perda (C4), tamanho do TRUTH (C5), pendência roteada (C6) e medição do split de PR (C7), e sai 1 se houver ALTO ou CRÍTICO
- DADO um requisito removido do `TRUTH.md` resultante sem MUDA/REMOVE que o declare QUANDO o gate roda ENTÃO acusa CRÍTICO e o veredito é BLOQUEADO — comparando o `TRUTH.md` contra o merge-base da branch com a main (fallback `HEAD`, com aviso, quando não há base), para que consolidação já commitada não crie janela cega; sufixo reescrito cujo ID permanece no arquivo não é perda
- DADO uma delta cujo diff acumulado de `specs/NNN-nome/` contra o merge-base excede o limiar de PR da regra canônica QUANDO o C7 roda ENTÃO reporta BAIXO recomendando o split dos artefatos (regra em `cycle.md`), sem alterar o código de saída — a medição informa, o split é decisão do ciclo; sem git ou sem merge-base o C7 se omite, como o C4
- DADO a saída do script QUANDO impressa ENTÃO se declara parcial — nomeia os checks mecânicos cobertos e avisa que os checks 3 e 5 do `analyze.md` (scope creep, regra canônica) são humanos e não rodaram
- DADO um `TRUTH.md` com sufixos na notação legada `(ΔNNN)` ou na nova `(delta-NNN)` QUANDO o gate lê os alvos ENTÃO reconhece as duas formas, sem exigir migração dos projetos existentes

## Fora de escopo
- Bloquear o merge de PR grande. O C7 é BAIXO (reporta, não falha o gate) — grande é anti-padrão, não impedimento.
- Split automático (abrir os dois PRs). O C7 mede e recomenda; abrir os PRs segue com o ciclo/humano.
- Medir o diff da implementação (código fora de `specs/NNN-nome/`). O split condicional do R17 governa só os artefatos da delta.

## Dependências e riscos
- Limiar de PR (`500`) materializa como constante no `check_cycle.py` — novo espelho do dono `canonical-rules.md`, sancionado no `deps.toml` (C1 o mantém em sincronia; o `.py` não entra na varredura do C2). Volta a 2 espelhos, sob o teto de 2–3 (o enxugue do DT-002 deixou margem).
- Reusa o merge-base do C4 (`base_c4`) — mesma janela cega residual do DT-007 (base commitada na `main` ou `origin/main` desatualizada), sem piorá-la.
