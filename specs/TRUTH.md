# claude-skills — Fonte da verdade
<!-- consolidado a cada archive; histórico das deltas em specs/_archive/ -->
<!-- particionamento: >~800 linhas ou >~10 domínios → truth/<dominio>.md e este vira índice -->
<!-- Δ000 = backfill do estado pré-ciclo (PRs #1–#3), consolidado no projeto-init deste repo.
     Deltas reais começam em Δ001. -->

## Inicialização de projeto

- R1 (Δ000) — `/sdd-iuri:projeto-init` classifica o repositório em um de cinco tipos e monta o `CLAUDE.md`
  a partir das regras canônicas, não do conhecimento genérico do modelo.
  - DADO um repositório sem `CLAUDE.md` QUANDO `/sdd-iuri:projeto-init` roda ENTÃO o tipo é classificado
    pela tabela de `detection.md` e o `CLAUDE.md` contém os módulos que a matriz marca para o tipo,
    com o texto copiado de `canonical-rules.md`
- R2 (Δ000) — o init nunca sobrescreve arquivo existente.
  - DADO um `CLAUDE.md` já presente QUANDO o init roda ENTÃO ele grava `CLAUDE.generated.md` ao
    lado e mostra o diff, deixando a decisão de merge com o usuário
  - DADO um `.gitignore` já presente QUANDO o init roda ENTÃO o bloco de secrets é anexado
    (append), nunca substituído
- R3 (Δ000) — o scaffold criado varia por tipo.
  - DADO o tipo detectado QUANDO o scaffold roda ENTÃO só são criados os arquivos que a matriz de
    `detection.md` marca para aquele tipo, e só os que ainda não existem
  - DADO um tipo com ciclo QUANDO o scaffold roda ENTÃO cria `specs/` + `TRUTH.md`, e **não**
    `docs/specs/` + `SPEC-TEMPLATE.md`

## Infraestrutura

- R4 (Δ000) — `/sdd-iuri:projeto-infra` configura branch protection, CI, Conventional Commits e release,
  e é idempotente.
  - DADO um repositório já configurado QUANDO `/sdd-iuri:projeto-infra` roda de novo ENTÃO ele consulta o
    que existe, preenche só as lacunas e relata no-op no restante
  - DADO falha de infra (sem rede, `gh` não autenticado) QUANDO o init a invoca ENTÃO o init
    reporta e segue, sem travar

## Ciclo de features

- R5 (Δ000) — uma feature é uma delta spec, com numeração global ao repositório.
  - DADO um incremento novo QUANDO `/sdd-iuri:spec-feature` abre a delta ENTÃO cria `specs/NNN-nome/` com
    `NNN` = max(`specs/`, `specs/_archive/`) + 1 e a branch `tipo/NNN-nome`
  - DADO uma versão maior do projeto QUANDO uma delta nova é aberta ENTÃO a numeração continua do
    maior existente e nunca reinicia
- R6 (Δ000) — a delta declara só o que muda em relação ao TRUTH.md.
  - DADO o `TRUTH.md` vigente QUANDO a spec é redigida ENTÃO cada bloco é ADICIONA, MUDA ou REMOVE,
    e blocos MUDA/REMOVE citam o alvo vigente (ex.: "MUDA R2 (Δ001)")
  - DADO um requisito na delta QUANDO a spec é validada ENTÃO ele tem cenário DADO/QUANDO/ENTÃO
    verificável; qualidade sem limiar fechado vira pendência em riscos, não RNF
- R7 (Δ000) — a delta percorre os estados proposta → aplicada → arquivada, e o archive faz parte
  do "pronto".
  - DADO um PR mergeado QUANDO o archive roda ENTÃO o spec.md vira `Estado: arquivada`, o requisito
    é consolidado no `TRUTH.md` com sufixo `(ΔNNN)` e o diretório move para `specs/_archive/NNN-nome/`
  - DADO um bloco MUDA QUANDO o archive consolida ENTÃO o requisito vigente é substituído
    **integralmente** pelo bloco da delta — a consolidação é mecânica, não infere intenção
- R8 (Δ000) — as fases do pipeline são delegadas a motores de terceiros por contrato.
  - DADO a fase clarify/plan/implement/review QUANDO ela roda ENTÃO o motor é o declarado em
    `adapters.md`, invocado com o contrato de formato/destino e verificado após a fase
- R9 (Δ000) — plugin ausente degrada a fase, nunca quebra o ciclo.
  - DADO um plugin não instalado QUANDO a fase que depende dele roda ENTÃO o fallback documentado
    em `adapters.md` assume e o usuário recebe aviso explícito de qual fase degradou
- R10 (Δ000) — o ciclo aplicável varia por tipo.
  - DADO um projeto `site-estatico` QUANDO o ciclo roda ENTÃO é o reduzido (specify → plan →
    implement → review), com clarify e analyze sob demanda
  - DADO um projeto `workspace-dados` QUANDO `/sdd-iuri:spec-feature` é invocado ENTÃO a skill recusa com
    explicação e aponta o scaffold estático do `projeto-init`

## Gates determinísticos

- R11 (Δ000) — o gate analyze roda sempre no ciclo completo e é read-only.
  - DADO uma delta com spec, plan e tasks QUANDO o analyze roda ENTÃO grava
    `specs/NNN-nome/analyze.md` com veredito, **inclusive quando não há achados** — o relatório é
    o registro de que o gate rodou
  - DADO um achado CRÍTICO QUANDO o veredito é emitido ENTÃO é BLOQUEADO e o implement não começa
    até correção
- R12 (Δ000) — a metade mecânica do analyze é um script, não diligência.
  - DADO uma delta QUANDO `check_cycle.py` roda ENTÃO ele verifica aceite (C1), cobertura
    spec↔tasks (C2), estado × localização (C3), archive sem perda (C4) e tamanho do TRUTH (C5),
    e sai 1 se houver ALTO ou CRÍTICO
  - DADO um requisito removido do `TRUTH.md` sem MUDA/REMOVE que o declare QUANDO o gate roda
    ENTÃO acusa CRÍTICO e o veredito é BLOQUEADO
- R13 (Δ000) — valor de negócio duplicado entre arquivos é governado por manifesto e validado
  por script.
  - DADO um repo com `deps.toml` QUANDO `validate_integrity.py` roda ENTÃO verifica espelhos em
    sincronia (C1), materialização fora dos sancionados (C2) e links relativos vivos (C3),
    saindo 1 em qualquer violação
  - DADO uma delta ainda aberta propondo valor novo QUANDO o validador roda ENTÃO ela não é
    acusada — só o `TRUTH.md` consolidado está no escopo de varredura

## Revisão

- R14 (Δ000) — a revisão adversarial da spec é um toggle opcional, distinto do analyze.
  - DADO uma spec que toca segurança, dados persistentes, contrato externo ou dependência nova
    QUANDO `/sdd-iuri:spec-review` roda ENTÃO produz achados + edições propostas em blocos antes/depois,
    sem aplicar nenhuma sem aprovação do usuário

## Não funcionais

- RNF1 (Δ000) — economia de tokens é requisito, não consequência.
  - Métrica: `TRUTH.md` ≤ 800 linhas (acima disso, particiona); o analyze lê só o cabeçalho-resumo
    do plan (≤15 linhas), nunca o plano inteiro
  - Verificação: `check_cycle.py` C5; contrato de insumos em `analyze.md`
- RNF2 (Δ000) — o ciclo degrada com aviso em vez de abortar.
  - Métrica: toda fase com motor de terceiro tem fallback nativo declarado
  - Verificação: tabela de contrato em `adapters.md` — uma linha por fase, com o ponto sensível a
    breaking change
- RNF3 (Δ000) — idempotência defensiva: nada é sobrescrito nem migrado sem pedido.
  - Métrica: 2ª execução de `/sdd-iuri:projeto-init` e `/sdd-iuri:projeto-infra` = no-op relatado
  - Verificação: rodar duas vezes em repo já inicializado e conferir o relatório
- RNF4 (Δ000) — todo script de gate carrega o próprio teste, validado no CI.
  - Métrica: 100% dos scripts do framework expõem `--selftest` com fixtures
  - Verificação: job `ci` executa `check_cycle.py --selftest` e `validate_integrity.py --selftest`

## Não implementado
<!-- visão conhecida que ainda não vige; não é delta e não tem número -->

- **CI dos gates dentro dos projetos do usuário.** Hoje os gates rodam local (analyze, archive,
  pré-commit); o porquê e as alternativas renunciadas estão em
  [ADR-0001](../docs/adrs/ADR-0001-gates-rodam-local.md).
- **Backfill assistido de TRUTH.md em brownfield.** Existe como tarefa sob demanda, não como fase.
- **Por design, fora de escopo:** os checks 3 e 5 do analyze (scope creep spec×plan, violação de
  regra canônica) e o mérito da spec no `/sdd-iuri:spec-review` continuam com o modelo — são juízo, não
  regex, e automatizá-los produziria falso negativo confiante.
