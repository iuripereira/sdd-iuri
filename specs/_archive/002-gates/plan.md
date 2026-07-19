<!-- resumo sdd-iuri · ≤15 linhas · única parte do plano lida pelo analyze e pelo humano -->
**Objetivo:** endurecer os gates do ciclo — C4 sem janela cega, selftest do C4 com git real,
C6 de pendência roteada, saída do script declarada parcial, grep de portabilidade ampliado.
**Cobre:** R1, R2, RNF1, RNF2 (da Δ 002)
**Decisões duráveis → ADRs:** nenhuma (convenção do checkbox vive em cycle.md/template; a
renúncia ao matching de texto está registrada na spec)
**Riscos assumidos:** consolidação commitada direto na main continua cega (merge-base==HEAD) —
aceito, o fluxo exige branch+PR; selftest do C4 é PULADO com aviso se `git` faltar no ambiente.

---

# Δ002 — Plano de implementação (gates)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** fechar os três buracos dos gates registrados no STATE.md (janela cega do C4, C4 sem
selftest, pendência que evapora no archive) + saída parcial explícita + grep RNF endurecido.

**Architecture:** tudo vive em `skills/spec-feature/scripts/check_cycle.py` (funções puras +
subprocess git, selftest embutido — convenção de co-localização do repo), nas referências da
skill (`cycle.md`, `analyze.md`, template `delta-spec.md`) e num step do `.github/workflows/ci.yml`.
Nenhum arquivo novo além dos artefatos da delta.

**Tech Stack:** Python 3.11+ stdlib apenas (`re`, `subprocess`, `pathlib`, `tempfile`) — regra
canônica de zero dependência supérflua. Idioma de identificadores/comentários: PT-BR.

## Global Constraints

- Idioma PT-BR em identificadores, comentários, docs e mensagens de commit (CLAUDE.md).
- Stdlib somente; nada de framework de teste — o selftest é `assert` embutido (`--selftest`).
- Todo limiar como constante nomeada; nenhum número mágico solto.
- Conventional Commits, escopo = nome da skill; 1 commit por task (fim de etapa = commit).
- Ao mudar template (`references/templates/`), atualizar consumidores **e** fixtures juntos.
- Verificação de existência de arquivo consulta `git ls-files`, não o filesystem (lição Δ001).

---

### Task 1: C4 compara contra o merge-base (TDD, git real)

**Files:**
- Modify: `skills/spec-feature/scripts/check_cycle.py:124-143` (`c4_archive`)
- Modify: `skills/spec-feature/scripts/check_cycle.py:205-250` (`selftest`)
- Test: o próprio `--selftest` (novo `selftest_c4`)

**Interfaces:**
- Consumes: `blocos()`, `c4_archive(root, bs, v)` existentes.
- Produces: `base_c4(root: Path) -> tuple[str, bool]` (ref do diff, achou-base?); `selftest_c4()`
  chamado por `selftest()`. A assinatura de `c4_archive` **não muda** — T2 e T3 dependem disso.

- [ ] **Step 1: Escrever o teste que falha** — adicionar ao final do script, antes de
  `if __name__ == "__main__":`, e chamar `selftest_c4()` como última linha de `selftest()`:

```python
def selftest_c4() -> None:
    """C4 com git real: perda já commitada é acusada; alvo declarado em MUDA não é."""
    import tempfile

    def rodar(declara_muda: bool):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)

            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

            git("init", "-q", "-b", "main")
            git("config", "user.email", "selftest@sdd")
            git("config", "user.name", "selftest")
            (root / "specs").mkdir()
            (root / "specs" / "TRUTH.md").write_text("- R1 (Δ000) — a\n- R2 (Δ000) — b\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-qm", "base")
            git("checkout", "-qb", "docs/archive")
            (root / "specs" / "TRUTH.md").write_text("- R2 (Δ000) — b\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-qm", "consolida")  # commitado: a antiga janela cega do diff HEAD
            spec = "### R9 — MUDA R1 (Δ000): a\n- DADO a QUANDO b ENTÃO c\n" if declara_muda else ""
            v: list = []
            c4_archive(root, blocos(spec), v)
            return v

    try:
        perdidos = rodar(declara_muda=False)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("selftest C4: PULADO (git indisponível)")
        return
    assert any(s == "CRÍTICO" and "R1" in q for s, _, q, _ in perdidos), \
        f"C4 não acusou perda commitada: {perdidos}"
    assert rodar(declara_muda=True) == [], "C4 acusou falso positivo com MUDA declarado"
    print("selftest C4: OK (git real; perda pós-commit acusada, MUDA declarado liberado)")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest`
Expected: `AssertionError: C4 não acusou perda commitada: []` — o `diff HEAD` atual é cego
para o commit de consolidação.

- [ ] **Step 3: Implementação mínima** — em `c4_archive`, substituir o bloco do
  `subprocess.run(["git", ..., "diff", "HEAD", ...])` por:

```python
    try:
        base, com_base = base_c4(root)
        diff = subprocess.run(
            ["git", "-C", str(root), "diff", base, "--", *alvo_git],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return  # sem git ou TRUTH não versionado — o check não se aplica
    if not com_base:
        v.append(("BAIXO", "C4", "sem merge-base com origin/main ou main — comparando contra HEAD (janela cega pós-commit)",
                  "rodar numa branch criada a partir da main"))
```

  E adicionar, logo acima de `c4_archive`:

```python
def base_c4(root: Path) -> tuple[str, bool]:
    """Merge-base da branch com a main → (ref, True); sem base → ('HEAD', False)."""
    for ref in ("origin/main", "main"):
        r = subprocess.run(["git", "-C", str(root), "merge-base", "HEAD", ref],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip(), True
    return "HEAD", False
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest`
Expected: as duas linhas `selftest: OK ...` e `selftest C4: OK ...`, exit 0.
Rodar também na delta real: `python3 skills/spec-feature/scripts/check_cycle.py specs/002-gates`
Expected: sem CRÍTICO de C4 (a branch atual não mexeu no TRUTH.md).

- [ ] **Step 5: Commit**

```bash
git add skills/spec-feature/scripts/check_cycle.py
git commit -m "fix(spec-feature): C4 compara contra o merge-base — fecha a janela cega pós-commit"
```

---

### Task 2: C6 — pendência aberta em delta arquivada (TDD)

**Files:**
- Modify: `skills/spec-feature/scripts/check_cycle.py` (novo `c6_pendencias`, chamada em
  `checar`, docstring linhas 9-17)
- Test: o próprio `--selftest` (fixture nova)

**Interfaces:**
- Consumes: nada de T1.
- Produces: `c6_pendencias(root: Path, v: list) -> None`; regexes de módulo `SECAO_RISCOS` e
  `PENDENCIA_ABERTA`. T4 documenta a convenção que este check verifica.

- [ ] **Step 1: Teste que falha** — dentro de `selftest()`, após os asserts existentes:

```python
    arquivada_pendente = """# Δ 001 — x
Estado: arquivada · Data: 2026-01-01 · Branch: feat/001-x

## Mudanças
### R1 — ADICIONA: login
- DADO a QUANDO b ENTÃO c

## Dependências e riscos
- risco informativo comum, sem checkbox
- [ ] pendência aberta: limiar de X não fechado
- [x] pendência já roteada para o STATE.md
"""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        arq = root / "specs" / "_archive" / "001-x"
        arq.mkdir(parents=True)
        (arq / "spec.md").write_text(arquivada_pendente, encoding="utf-8")
        v: list = []
        c6_pendencias(root, v)
        assert len(v) == 1 and v[0][0] == "ALTO" and "1 pendência" in v[0][2], f"C6: {v}"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest`
Expected: `NameError: name 'c6_pendencias' is not defined`

- [ ] **Step 3: Implementação mínima** — após `c5_tamanho`, com os regexes junto aos demais
  (topo do arquivo):

```python
SECAO_RISCOS = re.compile(r"^##\s+Depend[êe]ncias e riscos\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
PENDENCIA_ABERTA = re.compile(r"^\s*-\s*\[ \]", re.M)


def c6_pendencias(root: Path, v: list) -> None:
    """Pendência aberta (`- [ ]` em riscos) não sobrevive ao archive sem rotear pro STATE.md."""
    for p in sorted((root / "specs" / "_archive").glob("*/spec.md")):
        m = SECAO_RISCOS.search(p.read_text(encoding="utf-8"))
        if not m:
            continue
        n = len(PENDENCIA_ABERTA.findall(m.group(1)))
        if n:
            v.append(("ALTO", str(p.relative_to(root)),
                      f"{n} pendência(s) aberta(s) '- [ ]' em delta arquivada",
                      "copiar para 'Decisões em aberto' do STATE.md e marcar '- [x]'"))
```

  Chamar `c6_pendencias(root, v)` em `checar()`, após `c5_tamanho(root, v)`. Atualizar a lista
  de checks na docstring (linhas 9-13) acrescentando:
  `C6  pendência roteada — '- [ ]' em "Dependências e riscos" de delta arquivada`

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest`
Expected: OK nas três frentes (fixtures, C4 git, C6), exit 0.
Run: `python3 skills/spec-feature/scripts/check_cycle.py specs/002-gates`
Expected: nenhum achado de C6 (a Δ001 arquivada não tem `- [ ]` em riscos).

- [ ] **Step 5: Commit**

```bash
git add skills/spec-feature/scripts/check_cycle.py
git commit -m "feat(spec-feature): C6 acusa pendência aberta em delta arquivada"
```

---

### Task 3: saída do script declarada parcial

**Files:**
- Modify: `skills/spec-feature/scripts/check_cycle.py:194-201` (`main`) e docstring (linha 2-7)

**Interfaces:**
- Consumes: nada — só apresentação.
- Produces: formato de saída novo; T4 cita o texto em `analyze.md`.

**TDD dispensado (justificativa):** é I/O de apresentação puro — um `print` sem lógica; o
selftest não captura stdout e um teste de string de banner seria acoplamento sem valor.
Verificação: execução manual abaixo.

- [ ] **Step 1: Editar** — em `main()`:

```python
    print(f"# Analyze (mecânico, parcial) — {delta.name}")
```

  e, entre a tabela e o veredito:

```python
    print("\nParcial: cobre C1–C6; os checks 3 e 5 do analyze.md (scope creep, regra canônica) são juízo humano e não rodaram.")
```

  Na docstring, trocar a frase "checa o que é mecânico numa delta spec." por
  "checa o que é mecânico numa delta spec — **saída parcial**: os checks 3 e 5 do analyze
  continuam humanos."

- [ ] **Step 2: Verificar**

Run: `python3 skills/spec-feature/scripts/check_cycle.py specs/002-gates`
Expected: título `# Analyze (mecânico, parcial) — 002-gates`, linha `Parcial: ...` antes do
veredito, exit inalterado. `--selftest` continua OK.

- [ ] **Step 3: Commit**

```bash
git add skills/spec-feature/scripts/check_cycle.py
git commit -m "feat(spec-feature): saída do check_cycle declara-se parcial"
```

---

### Task 4: convenção do checkbox nos docs da skill

**Files:**
- Modify: `skills/spec-feature/references/templates/delta-spec.md:23-24` (seção riscos)
- Modify: `skills/spec-feature/references/cycle.md:71-76` (regra 6) e nova regra 7
- Modify: `skills/spec-feature/references/analyze.md:18-21` (parágrafo da metade mecânica)
- Modify: `skills/spec-feature/SKILL.md` (linha `C1 aceite · ... · C5 tamanho do TRUTH`)

**Interfaces:**
- Consumes: comportamento implementado em T1–T3 (documenta, não inventa).
- Produces: a convenção que o C6 (T2) verifica; regra de archive que a skill executa.

- [ ] **Step 1: template `delta-spec.md`** — trocar a seção final por:

```markdown
## Dependências e riscos
<!-- pendência ABERTA = item checkbox `- [ ]` (o C6 acusa se sobrar em delta arquivada);
     risco informativo = bullet comum. No archive, pendência aberta é copiada para
     "Decisões em aberto" do STATE.md e o item vira `- [x]`. -->
- {{deltas anteriores, libs, decisões pendentes}}
```

- [ ] **Step 2: `cycle.md`** — na regra 6 do archive, trocar a frase final
  "rode `scripts/check_cycle.py <delta>` **depois de consolidar e antes de commitar**. Ele lê o
  `git diff HEAD` do TRUTH.md e acusa CRÍTICO em requisito removido que a delta não declara
  como alvo de MUDA/REMOVE." por:
  "rode `scripts/check_cycle.py <delta>` **depois de consolidar** (antes ou depois de commitar —
  o C4 compara o TRUTH.md contra o merge-base da branch com a main, sem janela cega pós-commit)
  e ele acusa CRÍTICO em requisito removido que a delta não declara como alvo de MUDA/REMOVE."
  E acrescentar a regra 7:

```markdown
7. **Pendência roteada:** item `- [ ]` em "Dependências e riscos" do spec arquivado é pendência
   aberta — copie-a para a seção "Decisões em aberto" do `STATE.md` e marque `- [x]`, no mesmo
   commit da consolidação. O C6 do `check_cycle.py` acusa ALTO para `- [ ]` remanescente.
```

- [ ] **Step 3: `analyze.md`** — no parágrafo "Cobre os checks **1 e 2** abaixo, a verificação
  de archive (cycle.md, regra 6) e o limiar do TRUTH.md", acrescentar ", e a pendência roteada
  do archive (regra 7 — C6)". Manter a frase dos checks 3 e 5.

- [ ] **Step 4: `SKILL.md`** — na linha dos checks do `check_cycle.py`
  (`C1 aceite · C2 cobertura · C3 estado · C4 archive sem perda · C5 tamanho do TRUTH`),
  acrescentar ` · C6 pendência roteada`.

- [ ] **Step 5: Verificar consistência**

Run: `grep -rn 'diff HEAD' skills/` → vazio.
Run: `grep -rln 'C6' skills/spec-feature/` → SKILL.md, cycle.md, analyze.md, check_cycle.py.

- [ ] **Step 6: Commit**

```bash
git add skills/spec-feature/
git commit -m "docs(spec-feature): convenção de pendência (checkbox) e regras de archive do C4/C6"
```

---

### Task 5: grep de portabilidade endurecido (RNF2)

**Files:**
- Modify: `.github/workflows/ci.yml:41-47` (step "Portabilidade")

**Interfaces:** nenhuma — step isolado de CI.

- [ ] **Step 1: Editar o step** — trocar o `if grep ...` por:

```yaml
      - name: Portabilidade (RNF5) — zero caminho absoluto de maquina
        run: |
          # padrao com [.] para nao casar com esta propria linha do workflow
          if grep -rnE '(~|\$HOME|/home/[^/ ]+)/[.]claude/skills' skills/ .github/; then
            echo "RNF5: caminho absoluto de maquina encontrado acima"; exit 1
          fi
          echo "RNF5: OK"
```

  (O nome muda de RNF1→RNF5: número consolidado no TRUTH.md pela Δ001.)

- [ ] **Step 2: Verificar localmente com o comando idêntico ao do CI**

Run: `if grep -rnE '(~|\$HOME|/home/[^/ ]+)/[.]claude/skills' skills/ .github/; then echo FALHOU; else echo OK; fi`
Expected: `OK` (zero ocorrências das três variantes).
Run: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))" 2>/dev/null || echo "validar YAML no CI"`
Expected: sem erro de parse (o job `ci` valida YAML de toda forma).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: endurece o grep de portabilidade (RNF5) para \$HOME e /home/<user>"
```

---

### Task 6: CHANGELOG + STATE.md

**Files:**
- Modify: `CHANGELOG.md` (seção `[Não lançado]`)
- Modify: `STATE.md` (débito resolvido, descrição dos gates, histórico)

**Interfaces:** nenhuma.

- [ ] **Step 1: CHANGELOG** — sob `## [Não lançado]` / `### Adicionado`:

```markdown
- `check_cycle.py` C6: pendência aberta (`- [ ]` em "Dependências e riscos") de delta arquivada
  é acusada até ser roteada para o `STATE.md`; convenção no template `delta-spec.md`. (Δ002)
- Selftest do C4 com repositório git real (perda pós-commit e falso positivo de MUDA). (Δ002)
```

  Sob `### Mudado`:

```markdown
- `check_cycle.py` C4 compara o `TRUTH.md` contra o merge-base da branch com a main — sem a
  janela cega pós-commit; fallback `HEAD` com aviso quando não há base. (Δ002)
- A saída do `check_cycle.py` declara-se parcial: checks 3 e 5 do analyze são humanos. (Δ002)
- Grep de portabilidade do CI cobre `$HOME/.claude/skills` e `/home/<user>/.claude/skills`. (Δ002)
```

- [ ] **Step 2: STATE.md** — (a) em "O que existe", trocar "(C1–C5 do ciclo)" por "(C1–C6 do
  ciclo)"; (b) remover os quatro débitos resolvidos: "C4 tem janela cega e não tem selftest",
  "A saída do check_cycle.py é indistinguível...", "Pendência em 'Dependências e riscos' não tem
  gate...", "O grep do RNF1 só pega o literal..."; (c) acrescentar linha no histórico:
  `| 2026-07-18 | Δ002: C4 via merge-base + selftest git real, C6 de pendência, saída parcial, grep RNF5 ampliado | Δ002 |`

- [ ] **Step 3: Verificação final completa**

Run: `python3 skills/spec-feature/scripts/check_cycle.py --selftest && python3 skills/guarding-doc-integrity/scripts/validate_integrity.py --selftest && python3 skills/spec-feature/scripts/check_cycle.py specs/002-gates`
Expected: selftests OK; gate da delta sem ALTO/CRÍTICO.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md STATE.md
git commit -m "docs: registra a Δ002 no CHANGELOG e limpa o débito resolvido do STATE.md"
```
