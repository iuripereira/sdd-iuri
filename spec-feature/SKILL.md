---
name: spec-feature
description: Use when starting, resuming, or archiving a feature increment in a project that follows the sdd-iuri cycle (specs/NNN-name/ with delta specs). Triggers include "/spec-feature", "nova feature", "delta spec", "specify", "clarify", "analyze", "arquivar a delta", "consolidar no TRUTH.md", or the sdd-ciclo module in the project's CLAUDE.md.
---

# spec-feature

## Overview

Orquestra o ciclo por incremento do sdd-iuri: **delta specs** (só o que muda em relação ao
`TRUTH.md`), estados **proposta → aplicada → arquivada**, com fases delegadas a motores de
terceiros via adapters (`references/adapters.md`). O framework orquestra; os plugins executam.
Plugin ausente → a fase **degrada com aviso, nunca quebra** (fallbacks nos adapters).

Pipeline completo:
```
specify → clarify → plan → tasks → analyze → implement → review → archive → PR
```
Detalhe das fases (critérios de entrada/saída, máquina de estados, consolidação da entrevista):
`references/cycle.md`. Gate analyze: `references/analyze.md`.

## Aplicabilidade por tipo (coluna `ciclo` do projeto-init/detection.md)

| Tipo | Ciclo |
|---|---|
| app-web, backend | completo (TDD gate duro) |
| tooling | completo (TDD recomendado: default on, dispensável por task com justificativa no plan.md) |
| site-estatico | reduzido: specify → plan → implement → review (clarify e analyze opcionais, sob demanda); TDD off → verificação visual + build |
| workspace-dados | **não se aplica** — recuse com explicação e aponte o scaffold estático do projeto-init |

## Processo (resumo — detalhe em cycle.md)

1. **Abrir a delta**: `NNN` = max(specs/, specs/_archive/) + 1 — **global ao repositório, nunca
   reinicia**; é ID estável citado em ADRs, commits e TRUTH.md. Crie `specs/NNN-nome/` e a branch
   `tipo/NNN-nome` (`tipo` = Conventional Commits: `feat`, `fix`, ...; ex.:
   `feat/001-walking-skeleton`). Rascunhe `spec.md` a partir de
   `references/templates/delta-spec.md`, lendo o `TRUTH.md` antes (o que já vige não entra —
   só ADICIONA/MUDA/REMOVE). `TRUTH.md` ausente (greenfield/pré-ciclo) → trate como vazio;
   ele nasce do template no primeiro archive.
2. **Conduzir as fases na ordem do pipeline**, invocando o motor de cada fase conforme o
   contrato em `references/adapters.md`. Reporte ao usuário a escolha de motor quando houver
   gatilho (ex.: grill-with-docs em vez de grill-me).
3. **Gate analyze** (ciclo completo): sempre roda — é read-only e barato. Veredito BLOQUEADO
   (violação de regra canônica) interrompe até correção.
4. **Archive faz parte do "pronto"**: mergeado o PR, marque `Estado: arquivada`, consolide no
   `TRUTH.md` (ADICIONA/MUDA/REMOVE — regras em cycle.md) e mova o diretório para
   `specs/_archive/NNN-nome/`. Delta aplicada fora do `_archive/` é trabalho inacabado.

## Greenfield (primeira delta)

Δ001 **não** é "o sistema inteiro": é o walking skeleton — a menor fatia vertical funcional.
O `TRUTH.md` nasce só com a estrutura do template e cresce a cada archive. Visão global prévia
vira seção "Não implementado" do TRUTH.md inicial, nunca uma delta gigante.

## Erros comuns

| Erro | Correto |
|---|---|
| Spec do sistema inteiro em greenfield | Δ001 = walking skeleton |
| Pular analyze "porque a spec é simples" | analyze é read-only e barato — sempre roda no ciclo completo |
| Requisito sem DADO/QUANDO/ENTÃO | Validação estrita: todo Rn tem cenário de aceite |
| RNF em prosa ("deve ser rápido") | Todo RNFn tem Métrica com limiar + Verificação; sem limiar fechado → pendência em riscos |
| Delta aplicada esquecida fora do `_archive/` | archive + consolidação no TRUTH.md fazem parte do "pronto" |
| Re-entrevistar o usuário na consolidação | Sintetizar da conversa do clarify já feita (cycle.md) |
| Plano salvo em `docs/superpowers/plans/` | Preferência no CLAUDE.md redireciona para `specs/NNN-nome/plan.md` |
| Reiniciar numeração NNN por versão maior | Numeração global; reiniciar quebra referências |
| Aplicar o ciclo em workspace-dados | Recusar e apontar o scaffold estático do projeto-init |

## Arquivos da skill

- `references/cycle.md` — máquina de estados, critérios de entrada/saída por fase, consolidação
  entrevista→spec, regras de archive/TRUTH.md.
- `references/analyze.md` — roteiro do gate de verificação cruzada + formato do relatório.
- `references/adapters.md` — contratos de integração (max, superpowers, ponytail), fallbacks,
  política de versões e detecção de breaking change.
- `references/templates/` — `delta-spec.md`, `tasks.md`, `TRUTH.md`, `resumo-plan.md`.
