# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato segue [Keep a Changelog 1.0.0](https://keepachangelog.com/pt-BR/1.0.0/)
e o projeto adere ao [Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/).
A versão canônica vive nas tags git `vX.Y.Z`.

<!-- Este arquivo nasceu na aplicação do projeto-init ao próprio repo. Mudanças anteriores
     à sua criação vivem no histórico git; abaixo estão as notáveis ainda não lançadas. -->

## [Não lançado]

### Adicionado
- `spec-feature/scripts/check_cycle.py` — gate determinístico do ciclo: aceite verificável (C1),
  cobertura spec↔tasks (C2), estado × localização (C3), archive sem perda (C4) e limiar do
  TRUTH.md (C5). Sai 1 em ALTO/CRÍTICO. (#2)
- `guarding-doc-integrity` integrada ao framework como executora da regra de propagação, com
  `--selftest` no validador. (#3)
- Scaffold do próprio repositório via `projeto-init`: `CLAUDE.md`, `CHANGELOG.md`, `STATE.md`,
  `docs/adrs/`, `specs/TRUTH.md` com backfill do estado vigente (Δ000).
- Validação de TOML e execução dos `--selftest` dos gates no job `ci`.

### Mudado
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
- README: a instalação manual (`cp -r`) não copiava `guarding-doc-integrity`, deixando a skill
  inalcançável para quem seguisse a documentação. (#3)

<!--
No release: renomeie "[Não lançado]" para "## [X.Y.Z] - AAAA-MM-DD",
abra uma nova seção "[Não lançado]" vazia acima, e crie a tag git vX.Y.Z.
Bump derivado dos commits: fix→PATCH, feat→MINOR, !/BREAKING CHANGE→MAJOR (o maior vence).
-->
