<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** criar a skill `sdd-iuri:handoff` (própria, PT-BR) que fecha a sessão nos registros
com dono, e tirar a contagem "cinco skills" da redação viva (MUDA R15).
**Cobre:** R1, R2 (da delta-008)
**Decisões duráveis → ADRs:** nenhuma nova (a renúncia ao vendoring da skill externa está
registrada no spec/varredura; não há renúncia arquitetural além das já cobertas por ADR-0007)
**Riscos assumidos:** skill é markdown puro (sem script) — o contrato depende da disciplina do
modelo que a executa, mitigado por instruções explícitas e pelo formato fixo do STATE.md/DEBT.md.

---

# Plano de implementação — delta-008

Origem: plano de sessão aprovado (Etapa 4) + avaliação da skill externa na varredura (contrato,
licença MIT, sobreposições). Motor do plan: sessão aprovada (mesma justificativa da delta-007).

## `skills/handoff/SKILL.md` (novo — markdown puro, sem scripts/)

- **Frontmatter** (padrão do CI: `---`, `name:`, `description:` EN para matching):
  name `handoff`; description "Use when ending a work session or handing work to the next
  session — compacts the session into the project's canonical records: STATE.md (diário de
  bordo), DEBT.md (DT-NNN), current delta status. Triggers: '/sdd-iuri:handoff', 'fechar a
  sessão', 'handoff', 'passar o bastão', optionally with the next session's focus as argument."
- **Corpo (PT-BR)**, seções:
  1. Overview — o que a skill fecha e por quê (registros com dono; R18/R19 do TRUTH).
  2. Processo em 4 passos, na ordem: (a) rotear achados novos → DEBT.md (DT-NNN próximo livre /
     Lições com data+desfecho); (b) atualizar STATE.md nas 4 seções, janela rolante (entrada
     antiga sai — histórico é CHANGELOG+git); (c) delta em curso: citar `specs/NNN-*/`, fase e
     veredito do último gate (rodar `check_cycle.py` se houver dúvida); (d) commitar junto da
     mudança da sessão quando houver (regra "mesmo change" do CLAUDE.md).
  3. Regras herdadas com crédito: "Inspirada na `handoff` de mattpocock/skills (MIT)" —
     referencie por caminho/ID em vez de duplicar; segredos/PII nunca entram no diário
     (ecoa a seção Segurança do CLAUDE.md).
  4. Erros comuns (tabela curta): duplicar o que já está em spec/ADR/CHANGELOG; deixar débito só
     na conversa; STATE virar acumulador de histórico de novo; gravar handoff fora do repo (/tmp).
- Diferenciação explícita: `max:handoff` (ambiente do usuário) segue dona do brief efêmero de
  sessão em /tmp; a `sdd-iuri:handoff` é o handoff **persistente e versionado** do repo.

## Contagem fora da redação viva (MUDA R15)

- `CLAUDE.md:9`: "As cinco skills vivem em `skills/<nome>/`" → "As skills vivem em
  `skills/<nome>/`".
- `README.md:27`: "As cinco skills ficam sob o namespace" → "As skills ficam sob o namespace".
- `README.md` tabela "Os comandos": linha nova do `/sdd-iuri:handoff` (quando usar / o que faz).
- `.claude-plugin/plugin.json` description: acrescenta `handoff` à lista de skills.
- TRUTH consolida R15 sem numeral no archive (bloco R2 da spec).

## Encadeamento

CHANGELOG em `[Não lançado]`; STATE.md (diário) atualizado no mesmo change; archive consolida
R20 (ADICIONA R1→número livre) em domínio novo "Handoff de sessão" + MUDA R15; tag `v0.5.0`.

## TDD

Sem código executável (markdown + JSON). Dispensa justificada: a verificação é o frontmatter
válido (step do CI), `python3 -m json.tool` no manifesto e os greps de contagem/menções.
