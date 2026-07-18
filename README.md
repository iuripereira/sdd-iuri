# claude-skills — framework sdd-iuri

As skills do framework **sdd-iuri** para [Claude Code](https://claude.com/claude-code):
um framework de Spec-Driven Development por **delta specs** (só o que muda), com estados
`proposta → aplicada → arquivada` e uma fonte da verdade (`specs/TRUTH.md`) que cresce a cada
archive. O framework orquestra; plugins de terceiros executam as fases — e cada fase degrada
com aviso quando o plugin falta, nunca quebra.

Divisão de responsabilidade: **grill-me previne construir a coisa errada; Superpowers previne
construir sem disciplina; ponytail previne construir demais.**

## Instalação

```bash
# 1. As skills (este repo) — em ~/.claude/skills/
git clone https://github.com/iuripereira/claude-skills.git ~/.claude/skills
# (~/.claude/skills já existe com outras skills? Clone em pasta temporária e copie:)
#   git clone https://github.com/iuripereira/claude-skills.git /tmp/sdd \
#     && cp -r /tmp/sdd/projeto-init /tmp/sdd/projeto-infra /tmp/sdd/spec-feature \
#           /tmp/sdd/spec-review /tmp/sdd/guarding-doc-integrity ~/.claude/skills/

# 2. Os motores de terceiros (dentro do Claude Code)
/plugin install superpowers@claude-plugins-official   # plan, implement, review (testado: 6.x)
/plugin install ponytail@ponytail                     # anti-over-engineering always-on (4.x)
/plugin install max@max4c-skills                      # clarify: grill-me/grill-with-docs (0.8.0)
```

Pré-requisitos para o módulo de infra: `gh` autenticado e remote no GitHub.
Contratos, fallbacks e política de versões: `spec-feature/references/adapters.md`.

## Os comandos

| Comando | Quando usar | O que faz |
|---|---|---|
| `/projeto-init` | uma vez por repositório | Detecta o tipo (app-web · backend · site-estatico · workspace-dados · tooling), gera o `CLAUDE.md` a partir das regras canônicas, cria o scaffold (CHANGELOG, STATE, ADRs, `specs/` + TRUTH.md nos tipos com ciclo), oferece a infra e confere os plugins. Nunca sobrescreve nada |
| `/projeto-infra` | após criar o remote GitHub; ou avulsa em repo existente | Branch protection (rulesets), CI, Conventional Commits, release-please (changelog PT-BR), CodeRabbit/claude-code-action. Idempotente: 2ª rodada = no-op relatado |
| `/spec-feature` | a cada incremento de feature | Orquestra o ciclo: specify → clarify → plan → tasks → analyze → implement → review → archive → PR. Cria `specs/NNN-nome/`, numeração global, branch semântica; no archive consolida o `TRUTH.md` |
| `/spec-review` | opcional, antes do implement | Revisão adversarial da spec/plan via grill-me — recomendada quando a spec toca segurança, dados persistentes, contrato externo ou dependência nova |
| `/guarding-doc-integrity` | quando um valor de negócio vive em mais de um arquivo | Governança de fontes de verdade: manifesto `deps.toml` (dono → espelhos sancionados) + validador determinístico como gate pré-commit. É o executor da "regra de propagação" do `CLAUDE.md` |

Os gates determinísticos do framework — `spec-feature/scripts/check_cycle.py` (ciclo) e
`guarding-doc-integrity/scripts/validate_integrity.py` (espelhos) — rodam **local**, na fase
analyze/archive e no pré-commit. Ambos têm `--selftest` validado no CI deste repo.

## Caminho feliz (greenfield)

Projeto vazio ou só com um prompt-rascunho:

1. `/projeto-init` na pasta → tipo detectado (pasta vazia: ele pergunta), `CLAUDE.md` + scaffold.
2. Crie o repo no GitHub (`gh repo create ... --source .`) e rode `/projeto-infra` (ou aceite a
   oferta do init). Rulesets exigem repo público ou GitHub Pro.
3. `/spec-feature` → **Δ001 = walking skeleton** (a menor fatia vertical funcional — nunca "o
   sistema inteiro"). O prompt-rascunho vira insumo do specify/clarify; a visão além do skeleton
   vira seção "Não implementado" do TRUTH.md.
4. Repita `/spec-feature` por incremento. O `TRUTH.md` é a soma dos archives.

```
specify → clarify → plan → tasks → analyze → implement → review → archive → PR
          (grill)   (superpowers, plan.md    (gate       (superpowers + TDD    (TRUTH.md)
                     em specs/NNN/)          read-only)   + ponytail full)
```

## Brownfield (projeto com SDD anterior)

Tudo é **idempotência defensiva** — nada é sobrescrito nem migrado sem pedido:

- `CLAUDE.md` existente → o init gera `CLAUDE.generated.md` + diff; você decide o merge.
- Scaffold: só cria o que falta; `.gitignore` recebe append; `docs/specs/` antigos ficam como
  estão (o ciclo novo vive em `specs/`, o histórico antigo não é tocado).
- `TRUTH.md` nasce vazio e cresce com as **novas** deltas; para backfill do que já vige,
  sumarize o estado atual nele (tarefa assistida, sob demanda).
- `/projeto-infra` consulta o que já existe (rulesets, workflows) e só preenche lacunas.
- Numeração NNN continua do maior existente; nunca reinicia.

## Convenções deste repositório

`main` protegida por ruleset: mudanças só via PR com o check `ci` verde (valida JSON, YAML e
frontmatter dos SKILL.md) e commits no padrão Conventional Commits.
