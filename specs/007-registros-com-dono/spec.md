# delta-007 — registros-com-dono
Estado: proposta · Data: 2026-07-19 · Branch: feat/007-registros-com-dono

## Contexto (≤3 linhas)
O STATE.md acumula quatro naturezas (as-built, backlog, débito+lições, histórico duplicando o
CHANGELOG) e a evolução do framework fica invisível. A varredura de registros da sessão definiu:
cada registro com um dono — débito/pendências/lições no `DEBT.md` (DT-NNN), STATE.md vira diário de bordo.

## Mudanças

### R1 — MUDA R16 (delta-002): pendência de risco sobrevive ao archive — roteada para o DEBT.md
- DADO uma delta com pendência aberta (item `- [ ]` em "Dependências e riscos") QUANDO o archive
  roda ENTÃO a pendência é registrada no `DEBT.md` como item `DT-NNN` de natureza pendência, com
  origem `delta-NNN`, e o item do spec vira `- [x]`, no mesmo commit da consolidação
- DADO uma delta arquivada QUANDO o C6 roda ENTÃO acusa ALTO por delta com item `- [ ]`
  remanescente na seção "Dependências e riscos" do `spec.md`, reportando a contagem de itens

### R2 — ADICIONA: DEBT.md é o registro canônico de débito, pendências e lições, com IDs estáveis
- DADO um débito, pendência ou guarda novo QUANDO registrado ENTÃO entra no `DEBT.md` da raiz como
  linha `DT-NNN` (próximo número livre — numeração global, nunca reutilizada) com natureza,
  descrição, origem, data de abertura, gatilho de correção e status
- DADO um item quitado QUANDO a correção mergeia ENTÃO o status do item muda para quitado, com
  data — a linha nunca é apagada (a trajetória aberto→quitado é o registro da evolução)
- DADO um tipo de projeto que recebe `docs/adrs/` na matriz de detection.md QUANDO o scaffold do
  projeto-init roda ENTÃO cria também `DEBT.md` a partir do template da skill, e só se não existir

### R3 — ADICIONA: STATE.md é diário de bordo, não acumulador de estado
- DADO o template STATE.md do projeto-init QUANDO o scaffold cria o arquivo ENTÃO o formato tem as
  seções "Agora", "Feito recentemente", "Problemas atuais" e "Próximos passos imediatos", com
  janela rolante declarada e a regra de merge "união das verdades" mantida
- DADO conteúdo que tem dono próprio (as-built → TRUTH.md/README, débito/pendência/lição →
  DEBT.md, decisão com renúncia → ADR, histórico → CHANGELOG) QUANDO ele surgir no STATE.md
  ENTÃO é movido para o dono no mesmo bloco de trabalho e o STATE.md apenas referencia

## Fora de escopo
- GitHub Issues como registro de débito — renúncia registrada na ADR-0007; issue pode referenciar
  um DT-NNN para discussão, nunca ser a fonte.
- Skill de handoff (delta-008).
- Migração automática do STATE.md de projetos já inicializados pelo framework (idempotência
  defensiva, RNF3: nada é migrado sem pedido). A migração retroativa **deste** repo é tarefa
  explícita desta delta.

## Dependências e riscos
- ADRs e `specs/_archive/` continuam citando "Decisões em aberto do STATE.md" — histórico
  imutável, não migra; a guarda DT-006 do novo DEBT.md registra isso contra "consertos".
- Projetos criados com o template antigo de STATE.md seguem válidos; a mensagem nova do C6 aponta
  o DEBT.md e o projeto que não o tiver cria o arquivo no primeiro roteamento.
- Etapas 1–2 da sessão (PRs #19–#20) já mergeadas: ADR-0002..0006 existem; a ADR-0007 desta delta
  continua a numeração.
