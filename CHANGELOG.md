# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato segue [Keep a Changelog 1.0.0](https://keepachangelog.com/pt-BR/1.0.0/)
e o projeto adere ao [Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/).
A versão canônica vive nas tags git `vX.Y.Z`.

<!-- Este arquivo nasceu na aplicação do projeto-init ao próprio repo. Mudanças anteriores
     à sua criação vivem no histórico git; abaixo estão as notáveis ainda não lançadas. -->

## [Não lançado]

### Mudado
- Δ003 arquivada: R17 consolidado no `TRUTH.md`; pendência de mecanização do split roteada
  para o `STATE.md`. (#12)

### Corrigido
- `templates/deps.toml` da `guarding-doc-integrity`: excludes `**`-final (no-op em
  `pathlib` ≤ 3.12) trocados pela forma portável `**/*.md`, com comentário do porquê. (Δ004)

## [0.2.0] - 2026-07-19

### Adicionado
- Split condicional do PR de delta (Δ003): no fim do analyze, o diff de `specs/NNN-nome/` é
  medido contra o limiar canônico de PR — acima dele, os artefatos são mergeados num PR
  próprio antes do implement; dentro dele, o fluxo de PR único segue inalterado
  (`cycle.md` + saída extra do gate em `analyze.md`). (#11)

## [0.1.0] - 2026-07-19

Primeiro release: cria o baseline SemVer do repositório. Tudo abaixo estava
acumulado desde o início do projeto (PRs #1–#9).

### Adicionado
- `deps.toml` na raiz: os limiares espelhados do framework (particionamento do TRUTH.md e
  tamanho de PR) ganham dono e espelhos sancionados, com `validate_integrity.py` rodando
  contra o próprio repo no job `ci`. (#9)
- `check_cycle.py` C6: pendência aberta (`- [ ]` em "Dependências e riscos") de delta arquivada
  é acusada até ser roteada para o `STATE.md`; convenção no template `delta-spec.md`. (Δ002)
- Selftest do C4 com repositório git real (perda pós-commit e falso positivo de MUDA). (Δ002)
- Distribuição como plugin do Claude Code: `.claude-plugin/plugin.json` e skills em `skills/`,
  instalável por `/plugin marketplace add iuripereira/sdd-iuri` +
  `/plugin install sdd-iuri@sdd-iuri`. (#5)
- Step de CI que reprova caminho absoluto de máquina em `skills/` e `.github/` (RNF1 da Δ001). (#5)
- `spec-feature/scripts/check_cycle.py` — gate determinístico do ciclo: aceite verificável (C1),
  cobertura spec↔tasks (C2), estado × localização (C3), archive sem perda (C4) e limiar do
  TRUTH.md (C5). Sai 1 em ALTO/CRÍTICO. (#2)
- `guarding-doc-integrity` integrada ao framework como executora da regra de propagação, com
  `--selftest` no validador. (#3)
- Scaffold do próprio repositório via `projeto-init`: `CLAUDE.md`, `CHANGELOG.md`, `STATE.md`,
  `docs/adrs/`, `specs/TRUTH.md` com backfill do estado vigente (Δ000).
- Validação de TOML e execução dos `--selftest` dos gates no job `ci`.

### Mudado
- A saída do `check_cycle.py` declara-se parcial: checks 3 e 5 do analyze são humanos. (Δ002)
- Grep de portabilidade do CI cobre `$HOME/.claude/skills` e `/home/<user>/.claude/skills`. (Δ002)
- **BREAKING:** as cinco skills passam a ser invocadas sob o namespace `sdd-iuri:`
  (ex.: `/sdd-iuri:spec-feature`). Projetos que citem os nomes antigos precisam atualizar. (#5)
- Os scripts de gate resolvem o próprio caminho por `${CLAUDE_PLUGIN_ROOT}` em vez de
  `~/.claude/skills/...`. (#5)
- `.gitignore` deixa de ser allowlist: fora de `~/.claude/skills/` o repositório contém só o
  framework. (#5)
- `canonical-rules.md`: a regra de propagação passa a apontar para `deps.toml` +
  `guarding-doc-integrity`, no lugar do `scripts/check_docs.py` que nenhuma skill gerava. (#3)
- `templates/deps.toml`: o dono do exemplo passa de `PRD.md` (arquivo que o `projeto-init` nunca
  cria) para `specs/TRUTH.md`; `scan_globs` cobre o TRUTH consolidado mas não as deltas abertas. (#3)
- `analyze.md`, `cycle.md` e `spec-feature/SKILL.md` passam a invocar o gate mecânico antes da
  leitura de juízo. (#2)

### Segurança
- `.gitignore`: bloco de secrets anexado à allowlist. Sem ele, arquivos como `spec-feature/.env`
  seriam versionados — a allowlist re-inclui o diretório inteiro da skill.

### Corrigido
- `check_cycle.py` C4 compara o `TRUTH.md` contra o merge-base da branch com a main — fecha a
  janela cega pós-commit (gate LIBERADO com requisito perdido); fallback `HEAD` com aviso
  quando não há base. (Δ002)
- README: a instalação manual (`cp -r`) não copiava `guarding-doc-integrity`, deixando a skill
  inalcançável para quem seguisse a documentação. (#3)

<!--
No release: renomeie "[Não lançado]" para "## [X.Y.Z] - AAAA-MM-DD",
abra uma nova seção "[Não lançado]" vazia acima, e crie a tag git vX.Y.Z.
Bump derivado dos commits: fix→PATCH, feat→MINOR, !/BREAKING CHANGE→MAJOR (o maior vence).
-->
