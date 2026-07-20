#!/usr/bin/env python3
"""Gate determinístico do ciclo sdd-iuri — checa o que é mecânico numa delta spec.
Saída parcial: os checks 3 e 5 do analyze (scope creep, regra canônica) continuam humanos.

Automatiza os checks 1 e 2 do analyze (references/analyze.md), o estado ×
localização da delta, a verificação obrigatória do archive (references/cycle.md,
regra 6), o limiar de particionamento do TRUTH.md e a pendência roteada
(cycle.md, regra 7). Os checks 3 e 5 do analyze (scope creep spec×plan,
violação de regra canônica) continuam com o modelo — são juízo, não regex.

  C1  aceite verificável — Rn com DADO/QUANDO/ENTÃO; RNFn com Métrica + Verificação
  C2  cobertura spec ↔ tasks — órfãos nos dois sentidos; task sem verificação
  C3  estado × localização — delta 'aplicada' fora de _archive/ é trabalho inacabado
  C4  archive sem perda — requisito sumido do TRUTH.md sem MUDA/REMOVE que o declare
  C5  tamanho do TRUTH.md — acima de 800 linhas, particionar em truth/<dominio>.md
  C6  pendência roteada — '- [ ]' em "Dependências e riscos" de delta arquivada

Uso: check_cycle.py [DELTA_DIR]   (default: a única delta não arquivada em ./specs)
     check_cycle.py --selftest
Exit 0 = sem ALTO/CRÍTICO · 1 = corrigir antes de seguir · 2 = erro de uso.
"""
import re
import subprocess
import sys
from pathlib import Path

TRUTH_LIMITE = 800
ORDEM = {"CRÍTICO": 0, "ALTO": 1, "MÉDIO": 2, "BAIXO": 3}

CABECALHO = re.compile(r"^###\s+(R(?:NF)?\d+)\s*[—-]\s*(ADICIONA|MUDA|REMOVE)\b(.*)$")
ALVO = re.compile(r"\b(R(?:NF)?\d+)\s*\((?:Δ\s*|delta-)\d+\)")  # aceita (ΔNNN) legado e (delta-NNN)
TAREFA = re.compile(r"^\s*-\s*\[[ xX]\]\s*(T\d+)")
SECAO_RISCOS = re.compile(r"^##\s+Depend[êe]ncias e riscos\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
PENDENCIA_ABERTA = re.compile(r"^\s*-\s*\[ \]", re.M)
# ponytail: um requisito por bloco ###; spec que fuja do template não é parseada


def die(msg: str) -> None:
    print(f"ERRO: {msg}")
    sys.exit(2)


def campo(texto: str, nome: str):
    """Valor de 'nome: valor' até '·' ou fim de linha. None se ausente ou placeholder."""
    m = re.search(rf"{nome}\s*:\s*([^·\n]*)", texto, re.IGNORECASE)
    if not m:
        return None
    v = m.group(1).strip()
    return None if not v or "{{" in v else v


def blocos(spec_txt: str) -> list[tuple[str, str, str, str]]:
    """[(id, verbo, resto-do-cabeçalho, corpo)] dos ### Rn/RNFn do spec.md."""
    out: list[tuple[str, str, str, str]] = []
    atual, corpo = None, []
    for line in spec_txt.splitlines():
        m = CABECALHO.match(line)
        if m:
            if atual:
                out.append((*atual, "\n".join(corpo)))
            atual, corpo = (m.group(1), m.group(2), m.group(3)), []
        elif atual and line.startswith("## "):
            out.append((*atual, "\n".join(corpo)))
            atual, corpo = None, []
        elif atual:
            corpo.append(line)
    if atual:
        out.append((*atual, "\n".join(corpo)))
    return out


def c1_aceite(bs, v: list) -> None:
    for rid, verbo, _, corpo in bs:
        if verbo == "REMOVE":
            continue  # REMOVE não precisa de cenário — está saindo
        onde = f"spec.md {rid}"
        if rid.startswith("RNF"):
            if not campo(corpo, r"M[ée]trica"):
                v.append(("ALTO", onde, "RNF sem Métrica preenchida", "limiar verificável (ex.: p95 < 300ms) ou vira pendência em riscos"))
            if not campo(corpo, r"Verifica[çc][ãa]o"):
                v.append(("ALTO", onde, "RNF sem Verificação preenchida", "declarar como medir (teste de carga, axe-core, ...)"))
            continue
        alto = corpo.upper()
        faltam = [k for k in ("DADO", "QUANDO", "ENTÃO") if k not in alto]
        if faltam:
            v.append(("ALTO", onde, f"cenário de aceite sem {'/'.join(faltam)}", "todo Rn tem DADO/QUANDO/ENTÃO"))
        elif not re.search(r"ENTÃO\s+\S", corpo) or "{{" in corpo:
            v.append(("ALTO", onde, "cenário de aceite vazio ou não preenchido", "ENTÃO com resultado verificável"))


def c2_cobertura(bs, tasks_txt: str, v: list) -> None:
    ids_spec = {rid for rid, _, _, _ in bs}
    cobertos: set[str] = set()
    achou_task = False
    for line in tasks_txt.splitlines():
        m = TAREFA.match(line)
        if not m:
            continue
        achou_task, tid = True, m.group(1)
        cobre = campo(line, "cobre")
        if not cobre:
            v.append(("MÉDIO", f"tasks.md {tid}", "task sem 'cobre:'", "mapear a um Rn/RNFn ou declarar 'cobre: infra'"))
        else:
            for alvo in re.split(r"[,/]", cobre):
                alvo = alvo.strip()
                if alvo.lower() == "infra":
                    continue
                cobertos.add(alvo)
                if alvo not in ids_spec:
                    v.append(("ALTO", f"tasks.md {tid}", f"cobre '{alvo}', que não existe no spec.md", "corrigir a referência ou adicionar o requisito"))
        if not campo(line, r"verifica[çc][ãa]o"):
            v.append(("ALTO", f"tasks.md {tid}", "task sem 'verificação:'", "declarar comando ou critério de pronto"))
    if not achou_task:
        v.append(("ALTO", "tasks.md", "nenhuma task encontrada", "gerar tasks.md a partir do template"))
        return
    for rid in sorted(ids_spec - cobertos):
        v.append(("ALTO", f"spec.md {rid}", "requisito sem task que o cubra", f"adicionar task com 'cobre: {rid}'"))


def c3_estado(root: Path, v: list) -> None:
    for p in sorted((root / "specs").glob("*/spec.md")):
        if re.search(r"^Estado:\s*aplicada\b", p.read_text(encoding="utf-8"), re.M):
            v.append(("ALTO", str(p.relative_to(root)), "delta 'aplicada' fora de _archive/", "consolidar no TRUTH.md e mover — archive faz parte do pronto"))
    for p in sorted((root / "specs" / "_archive").glob("*/spec.md")):
        if not re.search(r"^Estado:\s*arquivada\b", p.read_text(encoding="utf-8"), re.M):
            v.append(("MÉDIO", str(p.relative_to(root)), "delta em _archive/ sem 'Estado: arquivada'", "corrigir o cabeçalho do spec.md"))


def base_c4(root: Path) -> tuple[str, bool]:
    """Merge-base da branch com a main → (ref, True); sem base → ('HEAD', False)."""
    for ref in ("origin/main", "main"):
        r = subprocess.run(["git", "-C", str(root), "merge-base", "HEAD", ref],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip(), True
    return "HEAD", False


def c4_archive(root: Path, bs, v: list) -> None:
    """Requisito removido do TRUTH.md tem que estar declarado como alvo de MUDA/REMOVE."""
    alvos = {a for _, verbo, head, _ in bs if verbo in ("MUDA", "REMOVE") for a in ALVO.findall(head)}
    for _, verbo, head, _ in bs:
        if verbo in ("MUDA", "REMOVE") and not ALVO.findall(head):
            v.append(("ALTO", "spec.md", f"bloco {verbo} sem citar o alvo vigente", "declarar o alvo (ex.: 'MUDA R2 (delta-001)')"))
    alvo_git = ["specs/TRUTH.md", "specs/truth"]
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
    perdidos = set()
    for line in diff.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            perdidos.update(r for r in ALVO.findall(line) if r not in alvos)
    # ID ainda presente no TRUTH resultante não é perda — cobre reescrita de sufixo em massa
    # (ex.: (ΔNNN)→(delta-NNN)), que remove a linha antiga no diff mas mantém o requisito.
    truth_atual = root / "specs" / "TRUTH.md"
    if truth_atual.is_file():
        presentes = set(ALVO.findall(truth_atual.read_text(encoding="utf-8")))
        perdidos -= presentes
    for rid in sorted(perdidos):
        v.append(("CRÍTICO", "specs/TRUTH.md", f"{rid} sumiu do TRUTH.md sem MUDA/REMOVE que o declare", "restaurar o requisito ou declarar o alvo na delta"))


def c5_tamanho(root: Path, v: list) -> None:
    truth = root / "specs" / "TRUTH.md"
    if truth.is_file():
        n = len(truth.read_text(encoding="utf-8").splitlines())
        if n > TRUTH_LIMITE:
            v.append(("BAIXO", "specs/TRUTH.md", f"{n} linhas (limiar {TRUTH_LIMITE})", "particionar em truth/<dominio>.md e virar índice"))


def c6_pendencias(root: Path, v: list) -> None:
    """Pendência aberta (`- [ ]` em riscos) não sobrevive ao archive sem rotear pro DEBT.md."""
    for p in sorted((root / "specs" / "_archive").glob("*/spec.md")):
        m = SECAO_RISCOS.search(p.read_text(encoding="utf-8"))
        if not m:
            continue
        n = len(PENDENCIA_ABERTA.findall(m.group(1)))
        if n:
            v.append(("ALTO", str(p.relative_to(root)),
                      f"{n} pendência(s) aberta(s) '- [ ]' em delta arquivada",
                      "registrar como DT-NNN no DEBT.md (natureza: pendência) e marcar '- [x]'"))


def checar(root: Path, delta: Path) -> list:
    spec, tasks = delta / "spec.md", delta / "tasks.md"
    if not spec.is_file():
        die(f"spec.md não encontrado em {delta}")
    bs = blocos(spec.read_text(encoding="utf-8"))
    v: list = []
    if not bs:
        v.append(("ALTO", "spec.md", "nenhum bloco '### Rn — ADICIONA|MUDA|REMOVE'", "usar templates/delta-spec.md"))
    c1_aceite(bs, v)
    c2_cobertura(bs, tasks.read_text(encoding="utf-8") if tasks.is_file() else "", v)
    c3_estado(root, v)
    c4_archive(root, bs, v)
    c5_tamanho(root, v)
    c6_pendencias(root, v)
    return v


def achar_delta(root: Path) -> Path:
    deltas = [p for p in sorted((root / "specs").glob("*/spec.md"))]
    if not deltas:
        die("nenhuma delta em ./specs — passe o diretório explicitamente")
    if len(deltas) > 1:
        die("mais de uma delta aberta: " + ", ".join(str(p.parent.name) for p in deltas))
    return deltas[0].parent


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "--selftest":
        selftest()
        return
    if arg:
        delta = Path(arg).resolve()
        if not delta.is_dir():
            die(f"não é diretório: {delta}")
        root = delta.parent.parent if delta.parent.name == "specs" else delta.parent.parent.parent
    else:
        root = Path.cwd()
        delta = achar_delta(root)
    v = sorted(checar(root, delta), key=lambda f: ORDEM.get(f[0], 2))

    print(f"# Analyze (mecânico, parcial) — {delta.name}")
    print("| # | Severidade | Onde | Inconsistência | Ação sugerida |")
    print("|---|---|---|---|---|")
    for i, (sev, onde, o_que, acao) in enumerate(v, 1):
        print(f"| {i} | {sev} | {onde} | {o_que} | {acao} |")
    print("\nParcial: cobre C1–C6; os checks 3 e 5 do analyze.md (scope creep, regra canônica) são juízo humano e não rodaram.")
    sevs = {f[0] for f in v}
    veredito = "BLOQUEADO" if "CRÍTICO" in sevs else "LIBERADO COM RESSALVAS" if v else "LIBERADO"
    print(f"\n**Veredito:** {veredito}")
    sys.exit(1 if sevs & {"CRÍTICO", "ALTO"} else 0)


def selftest() -> None:
    import tempfile

    limpa_spec = """# delta-001 — x
Estado: proposta · Data: 2026-01-01 · Branch: feat/001-x

## Mudanças
### R1 — ADICIONA: login
- DADO usuário anônimo QUANDO envia credencial válida ENTÃO recebe sessão

## Requisitos não funcionais
### RNF1 — ADICIONA: latência
- Métrica: p95 < 300ms sob 100 req/s
- Verificação: teste de carga no CI
"""
    limpa_tasks = "- [ ] T1 — form · arquivos: a.py · cobre: R1 · verificação: pytest\n" \
                  "- [ ] T2 — cache · arquivos: b.py · cobre: RNF1 · verificação: k6\n"
    suja_spec = limpa_spec.replace(
        "- DADO usuário anônimo QUANDO envia credencial válida ENTÃO recebe sessão", "- deve funcionar bem"
    ).replace("- Métrica: p95 < 300ms sob 100 req/s", "- Métrica: {{...}}") + \
        "\n### R2 — ADICIONA: logout\n- DADO sessão ativa QUANDO sai ENTÃO sessão encerra\n"
    suja_tasks = "- [ ] T1 — form · arquivos: a.py · cobre: R9 · verificação: pytest\n" \
                 "- [ ] T2 — cache · arquivos: b.py · cobre: RNF1\n"

    def rodar(spec_txt, tasks_txt):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            delta = root / "specs" / "001-x"
            delta.mkdir(parents=True)
            (delta / "spec.md").write_text(spec_txt, encoding="utf-8")
            (delta / "tasks.md").write_text(tasks_txt, encoding="utf-8")
            return checar(root, delta)

    assert rodar(limpa_spec, limpa_tasks) == [], "delta limpa deveria passar sem achados"

    achados = " · ".join(f"{o} {q}" for _, o, q, _ in rodar(suja_spec, suja_tasks))
    for esperado in (
        "spec.md R1 cenário de aceite sem DADO/QUANDO/ENTÃO",  # C1 Rn
        "spec.md RNF1 RNF sem Métrica preenchida",             # C1 RNF placeholder
        "tasks.md T1 cobre 'R9', que não existe",              # C2 referência morta
        "tasks.md T2 task sem 'verificação:'",                 # C2 task sem verificação
        "spec.md R2 requisito sem task",                       # C2 órfão
    ):
        assert esperado in achados, f"não pegou: {esperado}\nachados: {achados}"

    arquivada_pendente = """# delta-001 — x
Estado: arquivada · Data: 2026-01-01 · Branch: feat/001-x

## Mudanças
### R1 — ADICIONA: login
- DADO a QUANDO b ENTÃO c

## Dependências e riscos
- risco informativo comum, sem checkbox
- [ ] pendência aberta: limiar de X não fechado
- [x] pendência já roteada para o DEBT.md (DT-NNN)
"""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        arq = root / "specs" / "_archive" / "001-x"
        arq.mkdir(parents=True)
        (arq / "spec.md").write_text(arquivada_pendente, encoding="utf-8")
        v: list = []
        c6_pendencias(root, v)
        assert len(v) == 1 and v[0][0] == "ALTO" and "1 pendência" in v[0][2], f"C6: {v}"
        assert "DEBT.md" in v[0][3], f"C6 deve rotear para o DEBT.md (delta-007): {v}"

    print("selftest: OK (3 fixtures, 6 defeitos detectados)")
    selftest_c4()


def selftest_c4() -> None:
    """C4 com git real: perda já commitada é acusada; alvo declarado em MUDA não é."""
    import tempfile

    def rodar(resultante: str, spec: str = ""):
        """TRUTH base legado (Δ000) → estado `resultante` num commit; roda o C4 sobre `spec`."""
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
            (root / "specs" / "TRUTH.md").write_text(resultante, encoding="utf-8")
            git("add", "-A")
            git("commit", "-qm", "consolida")  # commitado: a antiga janela cega do diff HEAD
            v: list = []
            c4_archive(root, blocos(spec), v)
            return v

    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except (FileNotFoundError, OSError):
        print("selftest C4: PULADO (git indisponível)")
        return
    # git presente: daqui em diante toda falha é ruidosa — PULADO não mascara regressão
    perdidos = rodar("- R2 (Δ000) — b\n")  # R1 removido de fato, sem MUDA
    assert any(s == "CRÍTICO" and "R1" in q for s, _, q, _ in perdidos), \
        f"C4 não acusou perda commitada: {perdidos}"
    declara = rodar("- R2 (Δ000) — b\n", "### R9 — MUDA R1 (Δ000): a\n- DADO a QUANDO b ENTÃO c\n")
    assert declara == [], "C4 acusou falso positivo com MUDA declarado"
    # reescrita de sufixo (Δ→delta) preserva os IDs no arquivo → não é perda, sem MUDA
    reescreve = rodar("- R1 (delta-000) — a\n- R2 (delta-000) — b\n")
    assert reescreve == [], f"C4 acusou reescrita de sufixo como perda: {reescreve}"
    print("selftest C4: OK (git real; perda acusada, MUDA e reescrita de sufixo liberados)")


if __name__ == "__main__":
    main()
