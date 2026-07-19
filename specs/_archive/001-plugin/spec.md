# Δ 001 — plugin
Estado: arquivada · Data: 2026-07-18 · Branch: feat/001-plugin

## Contexto (≤3 linhas)
O framework vive como recorte de `~/.claude/skills/` via allowlist no `.gitignore`, com caminhos
absolutos de máquina dentro das skills e instalação por `cp -r`. Empacotá-lo como plugin do Claude
Code resolve distribuição, acoplamento de caminho e agrupamento de uma vez — e o custo do rename é
mínimo enquanto nenhum projeto downstream existe.

## Mudanças
<!-- só o que muda; um bloco por requisito; ADICIONA/MUDA/REMOVE em relação ao TRUTH.md -->

### R1 — ADICIONA: o framework é distribuído e instalado como plugin do Claude Code
<!-- cenário corrigido durante o implement: `/plugin install owner/repo` não existe — o argumento é
     resolvido como marketplace. Detalhe em "Dependências e riscos". -->
- DADO um usuário sem o framework QUANDO ele roda `/plugin marketplace add iuripereira/sdd-iuri`
  seguido de `/plugin install sdd-iuri@sdd-iuri` ENTÃO as cinco skills ficam disponíveis sob o
  namespace `sdd-iuri:`, sem cópia manual de arquivos e sem que o repositório precise viver dentro
  de `~/.claude/skills/`
- DADO o repositório do framework QUANDO o Claude Code registra o marketplace ENTÃO encontra
  `.claude-plugin/marketplace.json` **e** `.claude-plugin/plugin.json` na raiz, com as skills em
  `skills/<nome>/SKILL.md`

### R2 — MUDA R1 (Δ000): a skill `projeto-init` classifica o repositório e monta o `CLAUDE.md`
<!-- muda só a forma de citar a skill: o nome de invocação passa a ter um dono único (R1) -->
- DADO um repositório sem `CLAUDE.md` QUANDO a skill `projeto-init` roda ENTÃO o tipo é
  classificado pela tabela de `detection.md` e o `CLAUDE.md` contém os módulos que a matriz marca
  para o tipo, com o texto copiado de `canonical-rules.md`

### R3 — MUDA R4 (Δ000): a skill `projeto-infra` configura a infraestrutura e é idempotente
- DADO um repositório já configurado QUANDO a skill `projeto-infra` roda de novo ENTÃO ela consulta
  o que existe, preenche só as lacunas e relata no-op no restante
- DADO falha de infra (sem rede, `gh` não autenticado) QUANDO o init a invoca ENTÃO o init reporta
  e segue, sem travar

### R4 — MUDA R5 (Δ000): uma feature é uma delta spec, com numeração global ao repositório
- DADO um incremento novo QUANDO a skill `spec-feature` abre a delta ENTÃO cria `specs/NNN-nome/`
  com `NNN` = max(`specs/`, `specs/_archive/`) + 1 e a branch `tipo/NNN-nome`
- DADO uma versão maior do projeto QUANDO uma delta nova é aberta ENTÃO a numeração continua do
  maior existente e nunca reinicia

### R5 — MUDA R10 (Δ000): o ciclo aplicável varia por tipo
- DADO um projeto `site-estatico` QUANDO o ciclo roda ENTÃO é o reduzido (specify → plan →
  implement → review), com clarify e analyze sob demanda
- DADO um projeto `workspace-dados` QUANDO a skill `spec-feature` é invocada ENTÃO ela recusa com
  explicação e aponta o scaffold estático do `projeto-init`

### R6 — MUDA R14 (Δ000): a revisão adversarial da spec é um toggle opcional, distinto do analyze
- DADO uma spec que toca segurança, dados persistentes, contrato externo ou dependência nova
  QUANDO a skill `spec-review` roda ENTÃO produz achados + edições propostas em blocos
  antes/depois, sem aplicar nenhuma sem aprovação do usuário

## Requisitos não funcionais

### RNF1 — ADICIONA: portabilidade — nenhum artefato do framework depende de caminho de máquina
- Métrica: zero ocorrências de `~/.claude/skills` em `skills/**` e `.github/**`; toda invocação de
  script do framework resolve por `${CLAUDE_PLUGIN_ROOT}`
- Verificação: step no job `ci` rodando
  `! grep -rn '~/.claude/skills' skills/ .github/` (falha o PR se houver ocorrência)

## Fora de escopo
- Publicar em marketplace público — `/plugin install owner/repo` já basta para instalar direto do
  git; marketplace vira decisão separada se houver usuários além do autor.
- Vendorizar os gates no CI dos projetos gerados — a ADR-0001 segue vigente e não é reaberta aqui.
- Migrar as skills pessoais e de terceiros que dividem `~/.claude/skills/` — elas ficam onde estão,
  intocadas.
- Cortar a primeira tag de release (`v0.1.0`) — decisão registrada em aberto no `STATE.md`.

## Dependências e riscos
- **Breaking change de invocação.** `/spec-feature` passa a `/sdd-iuri:spec-feature` em todas as
  cinco skills. O custo hoje é ~10 substituições de texto porque nenhum projeto downstream existe;
  cresce a cada projeto gerado. **A janela barata expira.** Classificar o bump exigiria antes
  resolver o débito de release (zero tags) — registrado no `STATE.md`, fora do escopo desta delta.
- **A migração tem ordem obrigatória, por dois motivos independentes.** (a) Converter a allowlist em
  `.gitignore` normal **enquanto o repo ainda estiver em `~/.claude/skills/`** torna rastreáveis as
  12 skills pessoais e de terceiros que a allowlist esconde hoje. (b) Remover as cinco pastas antigas
  enquanto a sessão depende delas quebra o ambiente. Sequência: clonar para fora → converter o
  `.gitignore` no clone → instalar o plugin → verificar que as skills respondem pelo nome novo → só
  então apagar as pastas antigas. **Nunca `mv` primeiro, nunca converter in-place.**
- **`${CLAUDE_PLUGIN_ROOT}` está verificado na documentação, não em execução.** Validar na fase
  implement, com o plugin instalado, antes de apagar qualquer coisa.
- **Rename do repositório** (`claude-skills` → `sdd-iuri`) muda a URL de clone. O GitHub redireciona,
  mas README e `adapters.md` precisam citar a nova no mesmo PR.
- **Erro de fato corrigido no implement:** a spec original afirmava instalação por
  `/plugin install owner/repo`, "sem marketplace". **É falso** — o comando resolve o argumento como
  marketplace e falha com *"Marketplace não encontrado"*. Um repo de plugin único precisa de
  `.claude-plugin/marketplace.json` (com `plugins[].source: "./"`) **além** do `plugin.json`, e a
  instalação é em duas etapas. A afirmação veio de uma pesquisa em documentação que não foi
  validada em execução — o mesmo padrão que a Task 3 existia para prevenir, só que aplicado à
  premissa errada: eu tratei a forma de instalar como fato dado e só coloquei a expansão de
  `${CLAUDE_PLUGIN_ROOT}` sob teste.
- **Resolvido no clarify:** o formato de plugin **não tem** campo de dependência — verificado nos
  cinco `plugin.json` instalados (o grep por `depend|requires|peer` só bate em prosa de um campo
  `skillInstructions`). A cobertura existente basta e não vira requisito novo: R9/RNF2 degradam a
  fase com aviso, e o passo 6 do `projeto-init` confere na inicialização.
