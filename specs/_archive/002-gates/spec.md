# Δ 002 — gates
Estado: arquivada · Data: 2026-07-18 · Branch: feat/002-gates

## Contexto (≤3 linhas)
O archive da Δ001 confirmou os três buracos registrados no STATE.md: o C4 tem janela cega
pós-commit (diff contra `HEAD`), o check mais importante não tem selftest, e pendência de risco
evapora no `_archive/`. Endurecer os gates antes da próxima delta, enquanto o custo é um script.

## Mudanças
<!-- só o que muda; um bloco por requisito; ADICIONA/MUDA/REMOVE em relação ao TRUTH.md -->

### R1 — MUDA R12 (Δ000): a metade mecânica do analyze é um script, não diligência
- DADO uma delta QUANDO `check_cycle.py` roda ENTÃO ele verifica aceite (C1), cobertura
  spec↔tasks (C2), estado × localização (C3), archive sem perda (C4), tamanho do TRUTH (C5) e
  pendência roteada (C6), e sai 1 se houver ALTO ou CRÍTICO
- DADO um requisito removido do `TRUTH.md` sem MUDA/REMOVE que o declare QUANDO o gate roda
  ENTÃO acusa CRÍTICO e o veredito é BLOQUEADO — comparando o `TRUTH.md` contra o **merge-base
  da branch com a main** (fallback: `HEAD`, com aviso, quando não há base), para que
  consolidação já commitada não crie janela cega
- DADO a saída do script QUANDO impressa ENTÃO se declara **parcial** — nomeia os checks
  mecânicos cobertos e avisa que os checks 3 e 5 do `analyze.md` (scope creep, regra canônica)
  são humanos e não rodaram

### R2 — ADICIONA: pendência de risco sobrevive ao archive
<!-- convenção fechada no clarify: pendência aberta = checkbox `- [ ]` na seção de riscos;
     roteada = `- [x]`. C6 não faz matching de texto com o STATE — determinismo sobre riqueza. -->
- DADO uma delta com pendência aberta (item `- [ ]` em "Dependências e riscos") QUANDO o archive
  roda ENTÃO a pendência é copiada para a seção "Decisões em aberto" do `STATE.md` e o item vira
  `- [x]`, no mesmo commit da consolidação
- DADO uma delta arquivada QUANDO o C6 roda ENTÃO acusa ALTO por delta com item `- [ ]`
  remanescente na seção "Dependências e riscos" do `spec.md`, reportando a contagem de itens
  <!-- ajustado no review: agregado por delta (1 achado com contagem), não 1 achado por item —
       efeito prático idêntico (exit 1, contagem visível) -->


## Requisitos não funcionais

### RNF1 — MUDA RNF4 (Δ000): todo script de gate carrega o próprio teste, validado no CI
- Métrica: 100% dos scripts do framework expõem `--selftest` com fixtures; o C4 é coberto com
  **repositório git real** — caso positivo (perda acusada) e falso positivo (alvo declarado em
  MUDA não acusado)
- Verificação: job `ci` executa `check_cycle.py --selftest` e `validate_integrity.py --selftest`

### RNF2 — MUDA RNF5 (Δ001): portabilidade — nenhum artefato do framework depende de caminho de máquina
- Métrica: zero ocorrências de caminho de instalação legado em `skills/**` e `.github/**` —
  cobrindo as variantes `~/.claude/skills`, `$HOME/.claude/skills` e `/home/<user>/.claude/skills`;
  toda invocação de script do framework resolve por `${CLAUDE_PLUGIN_ROOT}`
- Verificação: step no job `ci` rodando
  `! grep -rnE '(~|\$HOME|/home/[^/ ]+)/[.]claude/skills' skills/ .github/`

## Fora de escopo
- Rodar os gates no CI dos projetos gerados — ADR-0001 segue vigente.
- Automatizar os checks 3 e 5 do analyze — juízo, não regex (limite reconhecido no TRUTH.md).
- Selftest dos demais checks com git real — só o C4 usa git; C1–C3/C5 já têm fixtures em tmpdir.

## Dependências e riscos
- **Convenção do C6 fechada no clarify (2026-07-18): checkbox.** Alternativa renunciada: marcador
  `**Pendência:**` com matching de substring no STATE.md — mais informativo, porém frágil a
  renomeação; determinismo venceu. Exige atualizar `delta-spec.md` (template) e `cycle.md` junto.
- **Merge-base exige uma referência de main.** Repositório sem `origin/main` nem `main` local
  (ex.: fixtures) cai no fallback `HEAD` com aviso — o comportamento atual, degradação graciosa.
  `origin/main` desatualizada (sem fetch) pode gerar CRÍTICO falso — mitigado pelo "git pull
  antes de ramificar" do CLAUDE.md; registrado no review.
- Mudar `cycle.md`/template é mudar o que o ciclo diz sobre si mesmo — consumidores e fixtures
  atualizam juntos (regra de testes do CLAUDE.md).
