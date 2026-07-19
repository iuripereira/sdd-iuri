<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** empacotar as 5 skills do framework como plugin do Claude Code, eliminando a allowlist
do `.gitignore` e os caminhos absolutos de máquina.
**Cobre:** R1, R2, R3, R4, R5, R6, RNF1 (da Δ 001)
**Decisões duráveis → ADRs:** nenhuma. O clarify constatou que o formato de plugin não tem campo de
dependência — fato de plataforma, não decisão. ADR-0001 segue vigente e não é reaberta.
**Riscos assumidos:** `${CLAUDE_PLUGIN_ROOT}` só está verificado na doc — a Task 3 valida em execução
antes de qualquer passo depender dele. Mover as skills in-place quebraria a descoberta na hora (dois
níveis não são encontrados), por isso todo trabalho de repo roda num clone fora; a única etapa
irreversível é a Task 8, por último e após verificação.

---

# Empacotamento do sdd-iuri como plugin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** transformar o repositório `claude-skills` — hoje um recorte de `~/.claude/skills/` via allowlist — num plugin do Claude Code instalável por `/plugin install`, com as 5 skills sob o namespace `sdd-iuri:`.

**Architecture:** o repositório sai de dentro de `~/.claude/skills/` e vira um repo comum com `.claude-plugin/plugin.json` na raiz e as skills em `skills/<nome>/`. A allowlist do `.gitignore` deixa de existir porque não há mais skills alheias no mesmo diretório. Os scripts de gate passam a se localizar por `${CLAUDE_PLUGIN_ROOT}` em vez de caminho absoluto. As skills pessoais e de terceiros ficam onde estão, intocadas.

**Tech Stack:** Markdown (skills), JSON (`plugin.json`), Python 3.11+ (os dois gates, sem dependência externa), GitHub Actions, `git`, `gh` CLI.

## Global Constraints

- Idioma PT-BR em documentação, comentários e mensagens de commit. Identificadores dos scripts também em PT-BR.
- Conventional Commits 1.0.0, escopo = nome da skill. Esta delta usa escopo `001-plugin` nos commits de artefato do ciclo.
- PR > 500 linhas é anti-padrão. Renames contam pouco no diff; se o total passar disso, quebrar em dois PRs pelo corte natural entre Task 6 e Task 7.
- Zero dependência supérflua: os gates usam só `re`, `pathlib`, `subprocess`, `tomllib`.
- Co-localização de verificação: cada script de gate mantém o próprio `--selftest`.
- **Nunca `mv` as pastas antigas antes da verificação da Task 7. Nunca converter o `.gitignore` in-place dentro de `~/.claude/skills/`.**
- Fora de escopo, não implemente: marketplace público, vendorizar gates no CI dos projetos gerados, migrar skills pessoais, cortar tag de release.

---

## File Structure

Estado final do repositório (no clone, `~/dev/sdd-iuri/`):

| Caminho | Responsabilidade |
|---|---|
| `.claude-plugin/plugin.json` | manifesto do plugin — só `name` é obrigatório |
| `skills/projeto-init/` | inicialização de projeto (movida da raiz) |
| `skills/projeto-infra/` | infraestrutura GitHub (movida da raiz) |
| `skills/spec-feature/` | ciclo de delta specs + `scripts/check_cycle.py` (movida da raiz) |
| `skills/spec-review/` | revisão adversarial (movida da raiz) |
| `skills/guarding-doc-integrity/` | integridade documental + `scripts/validate_integrity.py` (movida da raiz) |
| `CLAUDE.md`, `CHANGELOG.md`, `STATE.md` | scaffold do projeto — permanecem na raiz |
| `docs/adrs/`, `specs/` | ADRs e ciclo — permanecem na raiz |
| `.github/workflows/ci.yml` | paths atualizados + novo step de grep do RNF1 |
| `.gitignore` | denylist normal; a allowlist morre |

Os scripts permanecem **dentro** de suas skills (`skills/<nome>/scripts/`), não numa pasta `scripts/` na raiz do plugin. Motivo: a regra de co-localização do `CLAUDE.md` — a verificação mora junto do que verifica.

---

### Task 1: Clone de trabalho fora de `~/.claude/skills/`

Mover as skills para `skills/` dentro do diretório atual as tornaria invisíveis imediatamente (descoberta é de um nível só), quebrando o framework no meio da execução. Todo o trabalho acontece num clone.

**Files:**
- Create: `~/dev/sdd-iuri/` (clone completo)
- Nenhuma modificação em `~/.claude/skills/`

**Interfaces:**
- Produces: `$REPO` = `~/dev/sdd-iuri` — todas as tasks seguintes operam nesse diretório e em nenhum outro.

- [ ] **Step 1: Confirmar que a branch da delta está publicada**

```bash
cd ~/.claude/skills && git status -sb | head -1
git ls-remote --heads origin feat/001-plugin
```
Expected: a branch aparece no remote. Se não aparecer, `git push -u origin feat/001-plugin` antes de seguir.

- [ ] **Step 2: Clonar para fora**

```bash
mkdir -p ~/dev && git clone git@github.com:iuripereira/claude-skills.git ~/dev/sdd-iuri
cd ~/dev/sdd-iuri && git checkout feat/001-plugin
```

- [ ] **Step 3: Verificar que o clone tem o conteúdo do framework e nada além**

```bash
cd ~/dev/sdd-iuri && ls
```
Expected: `CHANGELOG.md CLAUDE.md README.md STATE.md docs guarding-doc-integrity projeto-infra projeto-init spec-feature spec-review specs` — e **nenhuma** das 12 skills pessoais (`cloudflare`, `notebooklm`, `wrangler`, ...). Se alguma aparecer, pare: a allowlist não estava fazendo o que se supunha.

- [ ] **Step 4: Verificar que o diretório original segue intacto**

```bash
ls ~/.claude/skills/spec-feature/SKILL.md && echo "framework ainda ativo"
```
Expected: o arquivo existe. Nada foi movido ainda.

---

### Task 2: Layout de plugin

**Files:**
- Create: `~/dev/sdd-iuri/.claude-plugin/plugin.json`
- Move: `projeto-init/`, `projeto-infra/`, `spec-feature/`, `spec-review/`, `guarding-doc-integrity/` → `skills/`
- Modify: `~/dev/sdd-iuri/.github/workflows/ci.yml:43-44`

**Interfaces:**
- Consumes: `$REPO` da Task 1.
- Produces: caminho canônico das skills = `skills/<nome>/SKILL.md`; caminho dos gates = `skills/spec-feature/scripts/check_cycle.py` e `skills/guarding-doc-integrity/scripts/validate_integrity.py`. Tasks 3–6 usam esses caminhos.

- [ ] **Step 1: Mover as cinco skills preservando histórico**

```bash
cd ~/dev/sdd-iuri && mkdir -p skills
for s in projeto-init projeto-infra spec-feature spec-review guarding-doc-integrity; do
  git mv "$s" "skills/$s"
done
git status --short | head
```
Expected: linhas `R  <origem> -> skills/<origem>` (renames detectados, histórico preservado).

- [ ] **Step 2: Criar o manifesto**

`~/dev/sdd-iuri/.claude-plugin/plugin.json`:
```json
{
  "name": "sdd-iuri",
  "description": "Spec-Driven Development por delta specs com gates determinísticos: projeto-init, projeto-infra, spec-feature, spec-review e guarding-doc-integrity.",
  "author": {
    "name": "Iuri Pereira"
  },
  "homepage": "https://github.com/iuripereira/sdd-iuri",
  "repository": "https://github.com/iuripereira/sdd-iuri",
  "license": "MIT",
  "keywords": [
    "spec-driven-development",
    "delta-spec",
    "adr",
    "conventional-commits",
    "changelog"
  ]
}
```

O campo `version` é **deliberadamente omitido**: só `name` é obrigatório, e a regra canônica diz que a tag git é a fonte da verdade da versão, não um manifesto. Incluí-lo hoje criaria uma segunda verdade para um valor que não existe (o repo não tem tags). Quando o débito de release do `STATE.md` for resolvido, decidir se o manifesto passa a espelhar a tag — e, se sim, documentar o espelho.

- [ ] **Step 3: Atualizar os paths do CI**

Em `~/dev/sdd-iuri/.github/workflows/ci.yml`, no step `Selftest dos gates`, trocar as duas linhas:
```yaml
          python3 skills/spec-feature/scripts/check_cycle.py --selftest
          python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest
```

- [ ] **Step 4: Verificar que os gates rodam dos caminhos novos**

```bash
cd ~/dev/sdd-iuri
python3 -m json.tool .claude-plugin/plugin.json > /dev/null && echo "plugin.json válido"
python3 skills/spec-feature/scripts/check_cycle.py --selftest
python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest
```
Expected: `plugin.json válido`, depois `selftest: OK (2 fixtures, 5 defeitos detectados)` e `selftest: OK (2 fixtures, C1/C2/C3 detectados)`.

- [ ] **Step 5: Commit**

```bash
cd ~/dev/sdd-iuri
git add -A
git commit -m "feat(001-plugin)!: move as skills para skills/ e adiciona o manifesto de plugin

BREAKING CHANGE: as skills passam a ser invocadas sob o namespace sdd-iuri:
(ex.: /sdd-iuri:spec-feature). O layout antigo, com as skills na raiz do
repositório, dependia de o repo viver dentro de ~/.claude/skills/."
```

---

### Task 3: Validar `${CLAUDE_PLUGIN_ROOT}` empiricamente antes de depender dele

O RNF1 assume que a variável resolve em conteúdo de skill. Isso está verificado na documentação, **não em execução**. Nenhum passo posterior depende dela até este teste passar.

**Files:**
- Create (temporário, descartado ao fim): `~/.claude/plugins/…` via instalação de teste
- Nenhuma modificação de arquivo versionado

**Interfaces:**
- Produces: veredito booleano — se falhar, Tasks 4 e 6 mudam de estratégia (ver Step 4).

- [ ] **Step 1: Publicar a branch para tornar o plugin instalável**

```bash
cd ~/dev/sdd-iuri && git push -u origin feat/001-plugin
```

- [ ] **Step 2: Instalar o plugin a partir da branch**

No Claude Code:
```
/plugin install iuripereira/claude-skills#feat/001-plugin
```
Expected: instalação concluída sem erro.

- [ ] **Step 3: Confirmar que as skills aparecem sob o namespace**

Rodar `/help` (ou abrir a lista de skills) e procurar por `sdd-iuri:spec-feature`, `sdd-iuri:projeto-init`, `sdd-iuri:projeto-infra`, `sdd-iuri:spec-review`, `sdd-iuri:guarding-doc-integrity`.
Expected: as cinco presentes. Se aparecerem com outro prefixo, anotar o prefixo real — ele passa a ser o valor usado na Task 4, e a spec precisa de correção antes de seguir.

- [ ] **Step 4: Confirmar que a variável expande num corpo de skill**

Invocar `/sdd-iuri:guarding-doc-integrity` e observar o caminho impresso no bloco de gate pré-commit da SKILL.md.
Expected: um caminho absoluto real terminando em `/skills/guarding-doc-integrity/scripts/validate_integrity.py`, **não** o literal `${CLAUDE_PLUGIN_ROOT}`.

Se sair o literal: a variável não expande em corpo de skill. Nesse caso, **pare e reporte** — a Task 4 passa a exigir uma alternativa (caminho relativo ao repo do projeto, ou instrução para o agente resolver o caminho a partir da lista de skills), e a métrica do RNF1 precisa ser reescrita antes de prosseguir.

---

### Task 4: Eliminar caminhos absolutos de máquina (RNF1)

**Files:**
- Modify: `skills/spec-feature/references/analyze.md:15`
- Modify: `skills/guarding-doc-integrity/SKILL.md:42`
- Modify: `skills/projeto-init/references/detection.md:98`
- Modify: `skills/spec-feature/references/adapters.md:65`
- Modify: `.github/workflows/ci.yml` (novo step de verificação)

**Interfaces:**
- Consumes: veredito da Task 3.
- Produces: invariante verificável — `grep -rn '~/.claude/skills' skills/ .github/` retorna vazio.

- [ ] **Step 1: Escrever a verificação que falha**

Adicionar em `~/dev/sdd-iuri/.github/workflows/ci.yml`, antes do step `Selftest dos gates`:
```yaml
      - name: Portabilidade (RNF1) — zero caminho absoluto de máquina
        run: |
          if grep -rn '~/.claude/skills' skills/ .github/; then
            echo "RNF1: caminho absoluto de máquina encontrado acima"; exit 1
          fi
          echo "RNF1: OK"
```

- [ ] **Step 2: Rodar e confirmar que falha**

```bash
cd ~/dev/sdd-iuri
if grep -rn '~/.claude/skills' skills/ .github/; then echo "FALHA esperada"; fi
```
Expected: lista as 4 ocorrências e imprime `FALHA esperada`.

- [ ] **Step 3: Corrigir as quatro ocorrências**

`skills/spec-feature/references/analyze.md` — a linha de invocação do gate:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/spec-feature/scripts/check_cycle.py specs/NNN-nome
```

`skills/guarding-doc-integrity/SKILL.md` — o bloco do gate pré-commit:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/guarding-doc-integrity/scripts/validate_integrity.py <repo>
```

`skills/projeto-init/references/detection.md` — a referência ao template do TRUTH passa a ser relativa ao plugin:
```
`${CLAUDE_PLUGIN_ROOT}/skills/spec-feature/references/templates/TRUTH.md`
```

`skills/spec-feature/references/adapters.md` — a nota de substituibilidade do `max`: trocar "copiar SKILL.md para `~/.claude/skills/`" por "copiar a SKILL.md para o diretório de skills pessoais do usuário".

- [ ] **Step 4: Rodar e confirmar que passa**

```bash
cd ~/dev/sdd-iuri
grep -rn '~/.claude/skills' skills/ .github/ || echo "RNF1: OK"
```
Expected: `RNF1: OK`.

- [ ] **Step 5: Commit**

```bash
cd ~/dev/sdd-iuri && git add -A
git commit -m "feat(001-plugin): resolve scripts por CLAUDE_PLUGIN_ROOT e verifica no CI

Cobre RNF1: nenhum artefato do framework depende de caminho de máquina."
```

---

### Task 5: Renomear as citações de comando (R2–R6)

São 33 citações de nome cru (`/projeto-init`, `/projeto-infra`, `/spec-feature`, `/spec-review`) em 10 arquivos. Depois do plugin, cada uma está factualmente errada.

**Files:**
- Modify: `skills/spec-feature/SKILL.md`, `skills/spec-feature/references/analyze.md`
- Modify: `skills/spec-review/SKILL.md`
- Modify: `skills/projeto-init/SKILL.md`, `skills/projeto-init/references/canonical-rules.md`, `skills/projeto-init/references/detection.md`
- Modify: `skills/projeto-infra/SKILL.md`
- Modify: `README.md`, `CLAUDE.md`, `specs/TRUTH.md`

**Interfaces:**
- Consumes: o prefixo real confirmado na Task 3, Step 3 (esperado: `sdd-iuri:`).
- Produces: nenhuma citação de comando sem namespace fora de `specs/_archive/` e `CHANGELOG.md`.

- [ ] **Step 1: Listar o estado atual**

```bash
cd ~/dev/sdd-iuri
grep -rn '/projeto-init\|/projeto-infra\|/spec-feature\|/spec-review\|/guarding-doc-integrity' \
  --include="*.md" skills/ README.md CLAUDE.md specs/TRUTH.md | wc -l
```
Expected: `33`.

- [ ] **Step 2: Substituir**

```bash
cd ~/dev/sdd-iuri
for f in $(grep -rl '/projeto-init\|/projeto-infra\|/spec-feature\|/spec-review\|/guarding-doc-integrity' \
             --include="*.md" skills/ README.md CLAUDE.md specs/TRUTH.md); do
  sed -i 's|/projeto-init|/sdd-iuri:projeto-init|g; s|/projeto-infra|/sdd-iuri:projeto-infra|g;
          s|/spec-feature|/sdd-iuri:spec-feature|g; s|/spec-review|/sdd-iuri:spec-review|g;
          s|/guarding-doc-integrity|/sdd-iuri:guarding-doc-integrity|g' "$f"
done
```

- [ ] **Step 3: Corrigir os falsos positivos do sed**

O sed também atinge caminhos de arquivo que contêm esses nomes (ex.: `skills/spec-feature/references/`). Localizar e reverter:
```bash
cd ~/dev/sdd-iuri
grep -rn 'sdd-iuri:spec-feature/\|sdd-iuri:projeto-init/\|sdd-iuri:projeto-infra/\|sdd-iuri:spec-review/\|sdd-iuri:guarding-doc-integrity/' --include="*.md" .
```
Para cada ocorrência listada, reverter o prefixo (é caminho, não comando). Repetir o grep até sair vazio.

- [ ] **Step 4: Verificar**

```bash
cd ~/dev/sdd-iuri
grep -rn '[^:]/spec-feature\b\|[^:]/projeto-init\b\|[^:]/projeto-infra\b\|[^:]/spec-review\b' \
  --include="*.md" skills/ README.md CLAUDE.md specs/TRUTH.md | grep -v 'skills/' || echo "R2-R6: OK"
python3 skills/spec-feature/scripts/check_cycle.py --selftest
```
Expected: `R2-R6: OK` e o selftest passando (as fixtures não citam comandos, então nada deve quebrar).

- [ ] **Step 5: Commit**

```bash
cd ~/dev/sdd-iuri && git add -A
git commit -m "feat(001-plugin): cita as skills pelo namespace sdd-iuri:

Cobre R2-R6: R1, R4, R5, R10 e R14 do TRUTH citavam o comando por string, que
fica errada com o namespace do plugin."
```

---

### Task 6: `.gitignore` de allowlist para denylist

Só é seguro no clone: no diretório original, a allowlist é o que esconde as 12 skills pessoais.

**Files:**
- Modify: `~/dev/sdd-iuri/.gitignore` (substituição completa)

- [ ] **Step 1: Confirmar que está no clone, não no original**

```bash
pwd
```
Expected: `/home/iuri/dev/sdd-iuri`. **Se imprimir `/home/iuri/.claude/skills`, pare** — converter aqui tornaria rastreáveis as 12 skills alheias.

- [ ] **Step 2: Substituir o conteúdo**

`~/dev/sdd-iuri/.gitignore`:
```
# === secrets & dados sensíveis (NUNCA versionar) ===
# .env e variantes → em produção viram GitHub Secrets / Key Vault / Doppler
.env
.env.*
!.env.example
*.pem
*.key
# Dados sensíveis / PII — never relax
data/
leads.json
*.leads.json
secrets/
# Derivados regeneráveis
node_modules/
dist/
.next/
__pycache__/
```

A allowlist (`/*` + `!/nome/`) desaparece: não há mais skills alheias neste repositório.

- [ ] **Step 3: Verificar que nada inesperado passou a ser rastreável**

```bash
cd ~/dev/sdd-iuri && git status --short
```
Expected: apenas `M .gitignore`. Qualquer arquivo novo listado é um artefato que a allowlist escondia — investigar antes de commitar.

- [ ] **Step 4: Commit**

```bash
cd ~/dev/sdd-iuri && git add -A
git commit -m "chore(001-plugin): converte o .gitignore de allowlist para denylist

A allowlist existia para recortar o framework de dentro de ~/.claude/skills/.
Fora dali, o repositório contém só o framework."
```

---

### Task 7: Documentação de instalação e abertura do PR

**Files:**
- Modify: `~/dev/sdd-iuri/README.md` (seção Instalação e tabela de comandos)
- Modify: `~/dev/sdd-iuri/CLAUDE.md` (remover a blockquote "Fronteira do repositório" e a ressalva de allowlist na seção Segurança)
- Modify: `~/dev/sdd-iuri/STATE.md` (seção "O que existe")
- Modify: `~/dev/sdd-iuri/CHANGELOG.md` (seção `[Não lançado]`)

- [ ] **Step 1: Reescrever a instalação do README**

Substituir o bloco de `git clone`/`cp -r` por:
```bash
# 1. O framework (este repo)
/plugin install iuripereira/sdd-iuri

# 2. Os motores de terceiros
/plugin install superpowers@claude-plugins-official   # plan, implement, review (testado: 6.x)
/plugin install ponytail@ponytail                     # anti-over-engineering always-on (4.x)
/plugin install max@max4c-skills                      # clarify: grill-me/grill-with-docs (0.8.0)
```
Na tabela de comandos, prefixar os cinco com `/sdd-iuri:`.

- [ ] **Step 2: Remover do `CLAUDE.md` o que deixou de valer**

Apagar a blockquote `> **Fronteira do repositório.** …` (o repo não vive mais dentro de `~/.claude/skills/`) e, na seção Segurança, a frase que começa em `**Atenção:** o `.gitignore` deste repo é uma *allowlist*` até `…protege `spec-feature/.env` e afins.` — substituir por `.env` no `.gitignore` (+ `chmod 600` local).

- [ ] **Step 3: Atualizar o `STATE.md`**

Em "O que existe", trocar a linha das 5 skills "versionadas por allowlist no `.gitignore`" por "distribuídas como plugin `sdd-iuri`, em `skills/`". Em "Pegadinhas", remover o item da allowlist (deixou de existir) e adicionar linha no "Histórico de alterações".

- [ ] **Step 4: Registrar no `CHANGELOG.md`**

Em `~/dev/sdd-iuri/CHANGELOG.md`, sob `## [Não lançado]`, acrescentar às categorias existentes:

```markdown
### Adicionado
- Distribuição como plugin do Claude Code: `.claude-plugin/plugin.json` e skills em `skills/`,
  instalável por `/plugin install iuripereira/sdd-iuri`. (#5)
- Step de CI que reprova caminho absoluto de máquina em `skills/` e `.github/` (RNF1 da Δ001). (#5)

### Mudado
- **BREAKING:** as cinco skills passam a ser invocadas sob o namespace `sdd-iuri:`
  (ex.: `/sdd-iuri:spec-feature`). Projetos que citem os nomes antigos precisam atualizar. (#5)
- Os scripts de gate resolvem o próprio caminho por `${CLAUDE_PLUGIN_ROOT}` em vez de
  `~/.claude/skills/...`. (#5)
- `.gitignore` deixa de ser allowlist: fora de `~/.claude/skills/` o repositório contém só o
  framework. (#5)
```

- [ ] **Step 5: Verificar a suíte inteira**

```bash
cd ~/dev/sdd-iuri
python3 -m json.tool .claude-plugin/plugin.json > /dev/null
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/ci.yml'))"
grep -rn '~/.claude/skills' skills/ .github/ || echo "RNF1: OK"
python3 skills/spec-feature/scripts/check_cycle.py --selftest
python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest
python3 skills/spec-feature/scripts/check_cycle.py specs/001-plugin
```
Expected: tudo verde; o `check_cycle` da delta acusa apenas `tasks.md` até a fase tasks rodar.

- [ ] **Step 6: Commit e PR**

```bash
cd ~/dev/sdd-iuri && git add -A
git commit -m "docs(001-plugin): instalação por plugin e remoção da fronteira de allowlist"
git push
gh pr create --base main --head feat/001-plugin --title "feat(001-plugin)!: empacota o framework como plugin do Claude Code"
```
Aguardar `ci` e `commits` verdes antes de seguir para a Task 8.

---

### Task 8: Migração local (irreversível — só depois do PR mergeado)

Única etapa destrutiva. Nada aqui roda antes de a Task 3 ter passado e o PR estar mergeado.

**Files:**
- Delete: `~/.claude/skills/{projeto-init,projeto-infra,spec-feature,spec-review,guarding-doc-integrity}/`
- Delete: `~/.claude/skills/{CLAUDE.md,CHANGELOG.md,STATE.md,.gitignore,.github/}`, `~/.claude/skills/{docs,specs}/`
- Delete: `~/.claude/skills/.git/`

- [ ] **Step 1: Renomear o repositório no GitHub**

```bash
gh repo rename sdd-iuri --repo iuripereira/claude-skills
cd ~/dev/sdd-iuri && git remote set-url origin git@github.com:iuripereira/sdd-iuri.git
git fetch --prune && git remote -v
```
O GitHub mantém redirect da URL antiga; ainda assim README e `adapters.md` já citam a nova.

- [ ] **Step 2: Reinstalar o plugin do `main` renomeado**

```
/plugin uninstall sdd-iuri
/plugin install iuripereira/sdd-iuri
```

- [ ] **Step 3: Verificar que as cinco skills respondem pelo nome novo — ANTES de apagar nada**

Confirmar na lista de skills: `sdd-iuri:projeto-init`, `sdd-iuri:projeto-infra`, `sdd-iuri:spec-feature`, `sdd-iuri:spec-review`, `sdd-iuri:guarding-doc-integrity`.
Expected: as cinco presentes e invocáveis. **Se qualquer uma faltar, pare aqui** — o estado antigo em `~/.claude/skills/` ainda está intacto e é o fallback.

- [ ] **Step 4: Conferir que o clone está sincronizado com o remote**

```bash
cd ~/dev/sdd-iuri && git checkout main && git pull && git status -sb
git log --oneline -1
```
Expected: `## main...origin/main` sem divergência, com o commit de merge do PR. Esta é a garantia de que nada só existe em `~/.claude/skills/`.

- [ ] **Step 5: Apagar o estado antigo**

```bash
cd ~/.claude/skills
rm -rf projeto-init projeto-infra spec-feature spec-review guarding-doc-integrity
rm -rf docs specs .github .git
rm -f CLAUDE.md CHANGELOG.md STATE.md README.md .gitignore
ls
```
Expected: restam apenas as 12 skills pessoais e de terceiros (`agents-sdk`, `cloudflare`, …), nenhum artefato do framework.

- [ ] **Step 6: Verificação final**

```bash
ls ~/.claude/skills | wc -l          # 12
cd ~/dev/sdd-iuri && git status -sb  # limpo, sincronizado
python3 skills/spec-feature/scripts/check_cycle.py --selftest
```
E, no Claude Code, invocar `/sdd-iuri:spec-feature` para confirmar que o ciclo responde a partir do plugin.

---

## Self-Review

**Cobertura da spec:**

| Requisito | Task |
|---|---|
| R1 — distribuição e instalação como plugin | Task 2 (manifesto + layout), Task 3 (validação), Task 7 (documentação) |
| R2 — `projeto-init` citada por nome | Task 5 |
| R3 — `projeto-infra` citada por nome | Task 5 |
| R4 — `spec-feature` citada por nome | Task 5 |
| R5 — ciclo por tipo, `spec-feature` citada por nome | Task 5 |
| R6 — `spec-review` citada por nome | Task 5 |
| RNF1 — portabilidade, zero caminho de máquina | Task 4 (correção + step de CI) |
| Trava de ordem da migração | Task 1 (clone antes de tudo), Task 6 Step 1 (guarda de `pwd`), Task 8 (destrutivo por último) |

**Placeholders:** nenhum passo diz "TBD", "ajuste conforme necessário" ou "trate os erros". Os dois pontos de julgamento (Task 3 Step 4 se a variável não expandir; Task 5 Step 3 falsos positivos do sed) têm critério objetivo e instrução de parar e reportar.

**Consistência:** o caminho dos gates é `skills/<skill>/scripts/<arquivo>.py` em todas as tasks (2, 4, 7, 8). O prefixo de namespace é `sdd-iuri:` em todas (3, 5, 7, 8), com a Task 3 Step 3 encarregada de confirmá-lo antes de a Task 5 aplicá-lo em massa.
