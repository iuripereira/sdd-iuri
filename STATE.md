# STATE.md — diário de bordo

> Andamento contínuo do trabalho: o que está em curso **agora**, o que acabou de ser feito, os
> problemas do momento e os próximos passos imediatos. Atualize com frequência dentro da própria
> sessão. **Janela rolante:** entrada antiga sai — histórico permanente é [CHANGELOG](CHANGELOG.md)
> + git; débito/pendência/lição é [DEBT.md](DEBT.md); decisão com renúncia é
> [docs/adrs/](docs/adrs/); o que vige é [specs/TRUTH.md](specs/TRUTH.md). Em conflito de merge,
> mantenha a **união das verdades** — nunca sobrescreva o progresso de outra sessão.

**Atualizado em:** 2026-07-20

## Agora
- Archive da delta-008 em PR — última pendência do repo na reorganização de registros; restam
  infra (`gh`) e memória da sessão.

## Feito recentemente
- 2026-07-20 — delta-008 implementada e mergeada (#23): skill `sdd-iuri:handoff`; contagem de
  skills fora da redação viva.
- 2026-07-20 — delta-007 arquivada (#22): MUDA R16 + R18/R19 no TRUTH.md, `v0.4.0` cortada.
- 2026-07-20 — delta-007 implementada e mergeada (#21): DEBT.md canônico (DT-001..007 + lições),
  STATE.md vira diário de bordo, C6 roteia pendência para DT-NNN, templates e ADR-0007.
- 2026-07-19 — Higiene de registros (#19) e backfill de ADRs 0002..0006 (#20).
- 2026-07-19 — Varredura completa de registros do repo + histórico #1–#18 (110 agentes, achados
  verificados adversarialmente) → plano da reorganização aprovado.

## Problemas atuais
- Nenhum bloqueio. Débito durável vive no [DEBT.md](DEBT.md) (DT-001..DT-007).

## Próximos passos imediatos
- Mergear o PR de archive da delta-008 e cortar a tag `v0.5.0`.
- Infra: exigir o check `commits` no ruleset `sdd-protect-main`; atualizar description/topics do
  repo no GitHub.
- Rodar `/plugin update sdd-iuri` no Claude Code local (cache do plugin anterior às deltas novas).
