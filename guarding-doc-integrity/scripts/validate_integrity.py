#!/usr/bin/env python3
"""Valida integridade documental contra o manifesto deps.toml (skill guarding-doc-integrity).

Checks:
  C1  espelhos em sincronia — cada pattern presente no arquivo dono E em cada espelho
  C2  materialização — pattern ausente em qualquer outro arquivo (scan_globs - exclude_globs)
  C3  links — todo link markdown relativo resolve para arquivo existente

Uso: validate_integrity.py [DIR | caminho/deps.toml]   (default: ./deps.toml)
Exit 0 = íntegro; 1 = violações (listadas); 2 = erro de uso/manifesto.
Requer Python 3.11+ (tomllib).
"""
import re
import sys
import tomllib
from pathlib import Path

# ponytail: alvo sem espaços e anchors não validados; portar github_slugify se doer
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def die(msg: str) -> None:
    print(f"ERRO: {msg}")
    sys.exit(2)


def load_manifest(arg: str):
    p = Path(arg)
    manifest = p if p.suffix == ".toml" else p / "deps.toml"
    if not manifest.is_file():
        die(f"manifesto não encontrado: {manifest}")
    try:
        with open(manifest, "rb") as f:
            return manifest.parent.resolve(), tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        die(f"deps.toml inválido: {e}")


def collect(root: Path, globs: list[str]) -> set[Path]:
    files: set[Path] = set()
    for g in globs:
        files.update(x for x in root.glob(g) if x.is_file())
    return files


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
        return
    root, cfg = load_manifest(sys.argv[1] if len(sys.argv) > 1 else ".")
    scan = collect(root, cfg.get("scan_globs", ["**/*.md"]))
    scan -= collect(root, cfg.get("exclude_globs", []))
    violations: list[str] = []

    for owner in cfg.get("owner", []):
        ofile = root / owner["file"]
        sanctioned = [ofile] + [root / m for m in owner.get("mirrors", [])]
        for path in sanctioned:
            if not path.is_file():
                violations.append(f"[C1] arquivo do manifesto não existe: {path.relative_to(root)}")
        sanctioned_ok = [p for p in sanctioned if p.is_file()]
        for val in owner.get("value", []):
            rx = re.compile(val["pattern"])
            name = val.get("name", val["pattern"])
            missing = [p for p in sanctioned_ok if not rx.search(p.read_text(encoding="utf-8"))]
            if missing:
                violations.append(
                    f"[C1] {name}: padrão ausente em "
                    + ", ".join(str(m.relative_to(root)) for m in missing)
                )
            else:
                print(f"[C1] {name}: OK (dono + {len(sanctioned) - 1} espelho(s))")
            for path in sorted(scan - set(sanctioned)):
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if rx.search(line):
                        violations.append(
                            f"[C2] {name}: valor fora dos sancionados — {path.relative_to(root)}:{i}"
                        )

    checked = 0
    for path in sorted(scan):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in MD_LINK.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#", "/")) or "{" in target:
                    continue  # "{...}" = placeholder de template, não link
                checked += 1
                dest = path.parent / target.split("#")[0]
                if not dest.exists():
                    violations.append(f"[C3] link morto — {path.relative_to(root)}:{i} → {target}")
    print(f"[C3] links relativos verificados: {checked}")

    if violations:
        print("\n".join(violations))
        print(f"RESULTADO: FAIL ({len(violations)} violação(ões))")
        sys.exit(1)
    print("RESULTADO: PASS")


def selftest() -> None:
    """Exercita C1/C2/C3 contra fixtures — o gate também precisa de gate."""
    import subprocess
    import tempfile

    manifesto = """scan_globs = ["*.md"]
exclude_globs = []

[[owner]]
file = "PRD.md"
mirrors = ["CLAUDE.md"]

  [[owner.value]]
  name = "limite"
  pattern = 'R\\$ ?2\\.000'
"""

    def rodar(arquivos: dict) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "deps.toml").write_text(manifesto, encoding="utf-8")
            for nome, txt in arquivos.items():
                (root / nome).write_text(txt, encoding="utf-8")
            return subprocess.run(
                [sys.executable, __file__, str(root)], capture_output=True, text=True
            )

    limpo = rodar({
        "PRD.md": "Limite de R$ 2.000 por pedido. Ver [dicionário](CLAUDE.md).\n",
        "CLAUDE.md": "Limite: R$ 2.000.\n",
    })
    assert limpo.returncode == 0, f"fixture limpa deveria passar:\n{limpo.stdout}"
    assert "RESULTADO: PASS" in limpo.stdout

    sujo = rodar({
        "PRD.md": "Limite de R$ 2.000. Ver [sumiu](nao-existe.md).\n",  # C3 link morto
        "CLAUDE.md": "Sem o valor aqui.\n",                            # C1 espelho dessincronizado
        "OUTRO.md": "Cópia solta: R$ 2.000.\n",                        # C2 fora dos sancionados
    })
    assert sujo.returncode == 1, f"fixture suja deveria falhar:\n{sujo.stdout}"
    for codigo in ("[C1]", "[C2]", "[C3]"):
        assert codigo in sujo.stdout, f"não pegou {codigo}:\n{sujo.stdout}"

    print("selftest: OK (2 fixtures, C1/C2/C3 detectados)")


if __name__ == "__main__":
    main()
