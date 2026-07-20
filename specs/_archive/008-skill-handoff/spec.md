# delta-008 — skill-handoff
Estado: arquivada · Data: 2026-07-20 · Branch: feat/008-skill-handoff

## Contexto (≤3 linhas)
Com os registros com dono (delta-007), falta o executor que fecha a sessão: uma skill que compacte
o andamento no STATE.md (diário de bordo) e roteie o que a sessão descobriu para os donos (DEBT.md,
ADRs). Própria, inspirada na `handoff` de mattpocock/skills (MIT) — avaliação na varredura da sessão.

## Mudanças

### R1 — ADICIONA: a skill handoff compacta a sessão nos registros com dono
- DADO uma sessão de trabalho neste repositório ou num projeto do framework QUANDO o usuário
  invoca `/sdd-iuri:handoff [foco da próxima sessão]` ENTÃO o `STATE.md` (diário de bordo) é
  atualizado nas quatro seções — Agora, Feito recentemente, Problemas atuais, Próximos passos
  imediatos — com o foco informado refletido nos próximos passos
- DADO débito, pendência ou lição descoberto na sessão e ainda sem registro QUANDO o handoff roda
  ENTÃO ele entra no `DEBT.md` (linha `DT-NNN` ou seção Lições) antes de o diário ser fechado
- DADO uma delta em curso em `specs/NNN-*/` QUANDO o handoff roda ENTÃO o diário cita a delta, a
  fase em que parou e o veredito do último gate
- DADO conteúdo já registrado em spec/plan/ADR/DEBT/CHANGELOG/commit QUANDO o handoff escreve
  ENTÃO referencia por caminho/ID em vez de duplicar, e segredo/PII não entra no diário

### R2 — MUDA R15 (delta-001): o framework é distribuído e instalado como plugin do Claude Code
- DADO um usuário sem o framework QUANDO ele roda `/plugin marketplace add iuripereira/sdd-iuri`
  seguido de `/plugin install sdd-iuri@sdd-iuri` ENTÃO as skills do plugin ficam disponíveis sob o
  namespace `sdd-iuri:`, sem cópia manual de arquivos e sem que o repositório precise viver
  dentro de `~/.claude/skills/`
- DADO o repositório do framework QUANDO o Claude Code registra o marketplace ENTÃO encontra
  `.claude-plugin/marketplace.json` **e** `.claude-plugin/plugin.json` na raiz, com as skills em
  `skills/<nome>/SKILL.md`

## Fora de escopo
- Vendorizar ou traduzir a skill externa (renúncia avaliada na varredura: EN vendored seria
  intocável pela regra do CLAUDE.md, gravaria em /tmp e duplicaria a `max:handoff` do ambiente).
- Handoff automático no fim de toda sessão — a invocação é manual, do usuário.
- Scaffold da skill em projetos gerados (a skill vem com o plugin; não é artefato de scaffold).

## Dependências e riscos
- delta-007 arquivada (DEBT.md e STATE diário vigentes — R16/R18/R19): satisfeita.
- A contagem de skills sai da redação viva (R15, CLAUDE.md, README) de propósito — a próxima
  skill não deve exigir outra rodada de MUDA por causa de um numeral.
- Crédito de inspiração a mattpocock/skills (MIT): cortesia em linha única na SKILL.md, não
  obrigação (não há cópia de porção substancial).
