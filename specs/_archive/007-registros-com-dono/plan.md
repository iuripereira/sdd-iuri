<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** separar os registros do repo por natureza — pendência/débito/lição no `DEBT.md`
(DT-NNN), STATE.md vira diário de bordo, templates e gate C6 acompanham.
**Cobre:** R1, R2, R3 (da delta-007)
**Decisões duráveis → ADRs:** ADR-0007 (registros com dono; renúncia: GitHub Issues como registro)
**Riscos assumidos:** referências históricas a "Decisões em aberto do STATE.md" em ADRs/_archive
não migram (imutáveis, guarda DT-006); projetos com template antigo criam DEBT.md no 1º roteamento.

---

# Plano de implementação — delta-007

Origem: plano de sessão aprovado (`~/.claude/plans/foamy-mapping-blossom.md`, Etapa 3), derivado
da varredura de registros (110 agentes, achados verificados adversarialmente). Motor da fase plan:
sessão de plan mode aprovada — substitui `superpowers:writing-plans` porque o plano já existia e
foi aprovado pelo usuário antes da abertura da delta (re-planejar duplicaria a decisão).

## Desenho

### DEBT.md (raiz) — formato
- Cabeçalho com o contrato: dono canônico de débito/pendência/guarda/lição; item quitado muda de
  status, nunca some; Issues podem referenciar DT-NNN, nunca ser fonte (ADR-0007).
- **Tabela única**: `ID | Natureza | Descrição | Origem | Aberto em | Gatilho de correção | Status`.
  Naturezas: `débito` (corrigir quando o gatilho disparar), `pendência` (decisão/trabalho roteado
  de delta arquivada — R16), `guarda` (aviso contra "conserto" indevido de histórico imutável).
  Status: `aberto` ou `quitado (AAAA-MM-DD, ref)`.
- **Seção "Lições"**: post-mortems datados com desfecho — nunca viram DT porque não há ação.
- Backfill inicial (da varredura, com origem e data reais):
  - DT-001 débito: parser do `check_cycle.py` acoplado ao formato dos templates — blocos
    `### Rn — VERBO` no spec.md **e task em linha única** no tasks.md (a metade tasks só existia
    na memória da sessão; sofrida na delta-004). Gatilho: template mudar de forma.
  - DT-002 débito: limiar de PR com 4 espelhos sancionados no `deps.toml`, acima do teto de 2–3
    da skill. Gatilho: próxima delta que toque `canonical-rules.md`/`deps.toml` enxuga.
  - DT-003 pendência (origem delta-003): mecanizar a medição do split condicional de PR
    (novo check no `check_cycle.py`, com selftest e MUDA no R12). Gatilho: a régua manual falhar
    numa delta real.
  - DT-004 débito: evidência 100% auto-referencial — o framework nunca rodou em projeto que não
    seja ele mesmo. Gatilho: primeiro projeto real (vira também o teste do backfill brownfield).
  - DT-005 débito: gate pré-commit prometido sem mecanismo — `deps.toml:4`, SKILL da
    guarding-doc-integrity e `canonical-rules.md` prometem validação pré-commit, mas não há hook
    algum (`.git/hooks/` vazio). Gatilho: decidir hook (husky/PreToolUse) ou reescrever a promessa.
  - DT-006 guarda: ADR-0001 cita caminho extinto (`~/.claude/skills/`) e delega ao STATE.md uma
    "limitação conhecida" que nunca existiu lá — ADR é imutável; não corrigir, não migrar.
  - DT-007 débito (origem delta-002): janela cega residual do C4 — consolidação commitada direto
    na main ou `origin/main` desatualizada escapam do merge-base. Gatilho: reproduzir numa delta real.
- O que **não** entra (já tem dono): Δ compat → R12; delta-000 convenção → TRUTH.md:4; metade
  humana do analyze → ADR-0006; versões dos motores → adapters.md; regex MD_LINK → `ponytail:` no
  próprio script.
- Lições (backfill): allowlist do .gitignore → verificação por `git ls-files` (2026-07-18,
  resolvida no #5); "o plano esquece o CHANGELOG" (3 reincidências corrigidas por analyze:
  deltas 001, 004, 005); premissa de plataforma tratada como fato sem validação (delta-001);
  renome citado em N requisitos custa N blocos MUDA (deltas 001/006 → ADR-0005); revisão do
  backfill delta-000 concluída em 2026-07-19 (8/11 conferiam; 3 achados → delta-005).

### STATE.md (repo) — novo formato (diário de bordo)
Cabeçalho: objetivo (andamento contínuo da sessão de trabalho; atualizado com frequência dentro
da mesma sessão), janela rolante (histórico permanente é CHANGELOG + git; débito é DEBT.md),
regra "união das verdades" mantida. Seções: `## Agora`, `## Feito recentemente`,
`## Problemas atuais`, `## Próximos passos imediatos`. Conteúdo inicial: estado real da sessão
corrente. Destinos do conteúdo antigo: "O que existe" → README/TRUTH (já cobrem; nada a mover),
"O que falta" → TRUTH "Não implementado" (já duplicado lá — apagar), "Decisões em aberto" →
DT-003 (mecanizar split) e item vendoring **morre** (contradiz a renúncia da ADR-0001, que já tem
cláusula "Reabre quando"), "Pegadinhas" → DT-001/002/005/006 + Lições + já-registrados,
"Histórico de alterações" → apagar (dono: CHANGELOG; a tabela contradiz a tag v0.2.0).

### Gate C6 (`check_cycle.py`) — TDD no contrato
1. RED: fixture do selftest passa a exigir `DEBT.md` na remediação do achado C6
   (assert novo) → selftest falha.
2. GREEN: docstring do C6 (linha ~179), mensagem de remediação (linha ~188: "registrar como
   DT-NNN no DEBT.md e marcar '- [x]'") e fixture (linha ~299: "- [x] pendência já roteada para o
   DEBT.md (DT-NNN)"). Sem mudança de lógica — o check continua acusando `- [ ]` na origem
   (ADR-0006: o gate não valida o destino).

### Consumidores do contrato R16 (mesmo change)
- `cycle.md` regra 7 do archive → destino DEBT.md (DT-NNN, natureza pendência, origem delta-NNN).
- `templates/delta-spec.md` comentário (linhas 24–26) → idem.
- `deps.toml` raiz: `DEBT.md` entra em `exclude_globs` (cita valores, como o STATE); comentário
  do limiar de PR troca o ponteiro morto ("decisão aberta sobre este limiar", fechada na
  delta-003) por "gatilho no DT-002 do DEBT.md".
- `templates/deps.toml` da guarding-doc-integrity: `DEBT.md` no exclude do template distribuído.

### projeto-init (formato distribuído)
- `references/templates/DEBT.md` **novo** (tabela vazia + Lições + contrato no cabeçalho).
- `references/templates/STATE.md` reescrito no formato diário de bordo.
- `references/canonical-rules.md`: módulo docs-sdd — definição do STATE.md passa a diário de
  bordo; entra a linha do DEBT.md (registro canônico, DT-NNN, quitado não some).
- `references/detection.md`: linha `DEBT.md` na matriz de scaffold espelhando a linha de
  `docs/adrs/` (✅ app-web/backend, ⚠️ site-estatico/tooling, ❌ workspace-dados); subsets
  docs-sdd citam DEBT.md junto de ADRs/STATE.
- `SKILL.md` do projeto-init: menção ao scaffold ganha DEBT.md se listar os artefatos.

### Repo (instância)
- `CLAUDE.md`: bullet do STATE.md (seção Documentação) vira diário de bordo + bullet novo do
  DEBT.md; princípio "atualize a doc no mesmo change" continua citando STATE.md.
- `README.md`: linha 83–86 ("estado as-built no STATE.md") vira "andamento no STATE.md (diário
  de bordo), débito e lições no DEBT.md"; link novo para DEBT.md.
- `docs/adrs/ADR-0007-registros-com-dono.md` + índice: decisão desta delta (Context: 4 naturezas
  misturadas; Decision: dono por natureza, DEBT.md file-first; renúncias: Issues como registro —
  atomicidade de commit, numeração compartilhada com PRs, gates offline; STATE multi-papel).
- `CHANGELOG.md` `[Não lançado]`.

## TDD
- T1 (gate): fixture-first, descrito acima — é a única mudança de código.
- Demais tasks são documentação/templates: dispensa de TDD justificada (sem lógica executável;
  a verificação é o `--selftest` + `validate_integrity.py` + grep de consumidores).

## Riscos e mitigação
- Diff total > limiar de PR: split condicional R17 medido no analyze (artefatos vs implementação);
  a implementação em si é majoritariamente .md — se exceder, registrar honestamente no PR
  (precedente delta-001).
- Perda de conteúdo na migração do STATE.md: cada item do STATE atual tem destino nomeado no
  desenho acima; o review estágio 1 confere item a item.
