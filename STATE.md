# STATE.md — diário de bordo

> Andamento contínuo do trabalho: o que está em curso **agora**, o que acabou de ser feito, os problemas do momento e os próximos passos imediatos. Atualize com frequência dentro da própria sessão. **Janela rolante:** entrada antiga sai — histórico permanente é [CHANGELOG](CHANGELOG.md) + git; débito/pendência/lição é [DEBT.md](DEBT.md); decisão com renúncia é [docs/adrs/](docs/adrs/); o que vige é [specs/TRUTH.md](specs/TRUTH.md). Em conflito de merge, mantenha a **união das verdades** — nunca sobrescreva o progresso de outra sessão.

**Atualizado em:** 2026-07-20

## Agora
- Nenhum trabalho em curso.

## Feito recentemente
- 2026-07-20 — delta-009 implementada (#28) e arquivada: **C7** no `check_cycle.py` mede o split
  de PR (BAIXO acima do limiar); MUDA R12 consolidado no TRUTH.md (delta-009); DT-003 quitado.
- 2026-07-20 — DT-002/DT-008 quitados no #27 (mergeado): espelhos do limiar de PR de 4→1
  (`SKILL/detection/analyze.md` citam "o limiar canônico"; `500` só no `CLAUDE.md`); `deps.toml`
  governa `15 linhas` e `10 dom`. Chore, sem tag/bump.
- 2026-07-20 — Formatação: quebra de linha manual removida da prosa em 27 `.md` (style, sem
  delta — mudança mecânica, zero conteúdo/requisito alterado, não cabe no template de spec).
- 2026-07-20 — Fechamento da reorganização de registros (#25): marketplace.json, README,
  docstrings, DEBT.md e ADR-0008 alinhados ao TRUTH vigente; `v0.5.1`.
- 2026-07-20 — delta-008 arquivada (#24): R20 + MUDA R15 no TRUTH.md, `v0.5.0`; ruleset passou a exigir também o check `commits`; description/topics do repo atualizados no GitHub.
- 2026-07-20 — delta-008 implementada (#23): skill `sdd-iuri:handoff`.
- 2026-07-20 — delta-007 implementada (#21) e arquivada (#22): DEBT.md (DT-NNN), STATE diário de bordo, C6 → DT-NNN, ADR-0007, `v0.4.0`.
- 2026-07-19 — Higiene de registros (#19), backfill de ADRs 0002..0006 (#20), varredura completa (110 agentes) e plano aprovado.

## Problemas atuais
- Nenhum bloqueio. Débito durável: [DEBT.md](DEBT.md) (DT-001, DT-003..DT-007 abertos; DT-002/DT-008 quitados).

## Próximos passos imediatos
- Rodar `/plugin update sdd-iuri` no Claude Code local (cache anterior às deltas 007–008).
- Próxima delta livre: 010. Gatilhos armados: DT-004 (rodar o framework num projeto real). Débito aberto: DT-001, DT-004, DT-005, DT-006 (guarda), DT-007.
