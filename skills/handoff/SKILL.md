---
name: handoff
description: Use when ending a work session or handing work to the next session in a project that follows the sdd-iuri records — compacts the session into the canonical records instead of an ephemeral brief: STATE.md (diário de bordo), DEBT.md (DT-NNN/lições), current delta status. Triggers include "/sdd-iuri:handoff", "fechar a sessão", "handoff", "passar o bastão", "encerrar por hoje", optionally with the next session's focus as argument.
---

# handoff

## Overview

Fecha a sessão de trabalho **nos registros com dono** do repositório (R18/R19 do TRUTH.md do framework): o andamento vai para o `STATE.md` (diário de bordo), o que a sessão descobriu de durável vai para o `DEBT.md` (DT-NNN / Lições), e a delta em curso fica citada com fase e gate. O handoff é **persistente e versionado** — a próxima sessão (ou outra máquina, ou outro humano) lê o repo e continua; nada vive só na conversa.

> Inspirada na `handoff` de [mattpocock/skills](https://github.com/mattpocock/skills) (MIT); reescrita para gravar nos registros do sdd-iuri em vez de um brief efêmero em `/tmp`.

Argumento opcional: o **foco da próxima sessão** (`/sdd-iuri:handoff terminar a migração do gate`) — entra nos "Próximos passos imediatos".

## Processo (na ordem — o diário fecha por último)

1. **Rotear os achados novos.** Débito, pendência ou guarda descoberto na sessão e ainda sem registro → linha `DT-NNN` no `DEBT.md` (próximo número livre; natureza, origem, data, gatilho, status). Post-mortem sem ação pendente → seção **Lições**, com data e desfecho. Projeto sem `DEBT.md` → crie do template da `projeto-init`.
2. **Atualizar o `STATE.md`** nas quatro seções — `Agora`, `Feito recentemente` (com data e ref de PR/commit), `Problemas atuais`, `Próximos passos imediatos` (foco do argumento em primeiro) — e o campo "Atualizado em". **Janela rolante:** entrada antiga sai; histórico permanente é CHANGELOG + git, não o diário.
3. **Citar a delta em curso**, se houver `specs/NNN-*/`: número, fase em que parou (specify … archive) e o veredito do último gate — em dúvida, rode `python3 ${CLAUDE_PLUGIN_ROOT}/skills/spec-feature/scripts/check_cycle.py specs/NNN-nome`.
4. **Commitar junto do trabalho da sessão** quando houver mudança pendente (regra do CLAUDE.md: doc no mesmo change). Sessão só de leitura → commit próprio do diário é aceitável.

## Regras de conteúdo

- **Referencie, não duplique** (regra de ouro): o que já está em spec, plan, ADR, DEBT.md, CHANGELOG ou commit entra por caminho/ID (`DT-003`, `specs/_archive/007-*/`, `#21`), nunca copiado.
- **Segredo/PII nunca entra no diário** — nem em nenhum registro versionado (seção Segurança do CLAUDE.md).

## Erros comuns

| Erro | Correto |
|---|---|
| Gravar o handoff fora do repo (/tmp, gist, memória da IA) | O handoff do sdd-iuri é o próprio repo: STATE.md + DEBT.md versionados |
| Deixar débito descoberto só na conversa | Rotear para DT-NNN **antes** de fechar o diário (passo 1 vem primeiro) |
| STATE.md virar acumulador de histórico de novo | Janela rolante; histórico é CHANGELOG + git (R19) |
| Duplicar conteúdo de spec/ADR/CHANGELOG no diário | Referência por caminho/ID |
| Esquecer a delta em curso | Passo 3 é obrigatório quando existe `specs/NNN-*/` |
