#!/usr/bin/env python3
"""Exporta markdown -> PDF/DOCX assinável com capa parametrizada (skill doc-entregavel, ADR-0009).

Generalização do pipeline validado nos PRDs/contratos IMEX (imex-contratos):
- docx: pandoc (pypandoc) md->docx para o corpo; capa inserida via python-docx.
- pdf:  python-markdown -> HTML+CSS -> google-chrome --headless --print-to-pdf.

Imagens referenciadas no markdown (`![](docs/diagrams/arquitetura.svg)`) são embutidas
pelos dois pipelines — renderize os diagramas do doc-profile ANTES (mmdc/dbml-renderer;
PNG para docx, SVG ou PNG para pdf) e referencie-os no md de entrada.

Uso:
  exporta_entregavel.py {docx|pdf} <entrada.md> <saida> \
      --titulo "Documento de Requisitos do Produto (PRD)" \
      --projeto "Nome do Projeto" --versao 1.0 --data "20 de julho de 2026" \
      [--anexo "Anexo V ao Contrato ..."] [--local "Cidade/UF"] \
      [--assinatura "Razão Social — CONTRATANTE"] [--assinatura "... — CONTRATADO"]

Entregável é congelado: nova baseline -> novo arquivo versionado -> nova assinatura.
Nunca sobrescreva um entregável já enviado ao cliente.
"""
import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

# Cambria = fonte dos contratos IMEX; Caladea = metricamente compatível; Noto Serif = fallback
CSS = '''
@page { size: 8.5in 11in; margin: 2.2cm 2.4cm; }
body { font-family: Cambria, Caladea, 'Noto Serif', Georgia, serif; font-size: 10.5pt; color: #000; }
h1 { font-size: 13.5pt; color: #365F91; font-weight: bold; }
h2 { font-size: 12.5pt; color: #4F81BD; }
h3 { font-size: 11.5pt; color: #4F81BD; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
th, td { border: 0.5pt solid #999; padding: 3pt 5pt; text-align: left; vertical-align: top; }
code, pre { font-family: 'Courier New', monospace; font-size: 9pt; }
pre { white-space: pre-wrap; }
img { max-width: 100%; }
blockquote { margin-left: 0.5cm; color: #333; }
.capa { text-align: center; margin-top: 3cm; }
.capa h1 { font-size: 26pt; color: #17365D; }
.assin { margin-top: 2.5cm; text-align: left; }
.linha { margin-top: 1.6cm; border-top: 0.75pt solid #000; width: 11cm; padding-top: 2pt; }
.quebra { page-break-after: always; }
'''


def le_markdown(caminho):
    md = pathlib.Path(caminho).read_text(encoding='utf-8')
    # TOC markdown (âncoras internas) vira ruído no documento final
    return re.sub(r'<!-- BEGIN TOC -->.*?<!-- END TOC -->', '', md, flags=re.S)


def exporta_pdf(args, md):
    import markdown
    corpo = markdown.markdown(md, extensions=['tables', 'fenced_code', 'sane_lists'])
    assin = ''.join(f'<div class="linha"><b>{a}</b></div>' for a in args.assinatura)
    anexo = f'<p>{args.anexo}</p>' if args.anexo else ''
    local = (f'<p>{args.local}, ____ de ______________ de ____.</p>'
             if args.local else '')
    capa = f'''
<div class="capa">
  <h1>{args.titulo}</h1>
  <h2 style="color:#17365D">{args.projeto}</h2>
  <p><b>Versão {args.versao}, de {args.data}</b></p>
  {anexo}
  <div class="assin">{local}{assin}</div>
</div>
<div class="quebra"></div>
'''
    # <base> aponta para a pasta do md — imagens relativas resolvem de lá
    base = pathlib.Path(args.entrada).resolve().parent.as_uri() + '/'
    html = (f"<html><head><meta charset='utf-8'><base href='{base}'>"
            f"<title>{args.projeto} v{args.versao}</title>"
            f"<style>{CSS}</style></head><body>{capa}{corpo}</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        h = pathlib.Path(tmp) / 'doc.html'
        h.write_text(html, encoding='utf-8')
        destino = pathlib.Path(args.saida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--no-pdf-header-footer', f'--print-to-pdf={destino.resolve()}',
                        str(h)], check=True, capture_output=True)


def exporta_docx(args, md):
    import pypandoc
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.shared import Pt

    C, E = WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT
    with tempfile.TemporaryDirectory() as tmp:
        corpo = pathlib.Path(tmp) / 'corpo.docx'
        pypandoc.convert_text(
            md, 'docx', format='gfm', outputfile=str(corpo),
            extra_args=['--resource-path', str(pathlib.Path(args.entrada).resolve().parent)])
        d = Document(str(corpo))

        linhas = [(args.titulo, 22, True, C),
                  (args.projeto, 16, True, C),
                  (f'Versão {args.versao}, de {args.data}', 12, True, C)]
        if args.anexo:
            linhas.append((args.anexo, 11, False, C))
        if args.local:
            linhas += [('', 11, False, E),
                       (f'{args.local}, ____ de ______________ de ____.', 11, False, E)]
        for a in args.assinatura:
            linhas += [('', 11, False, E),
                       ('_________________________________________________', 11, False, E),
                       (a, 11, True, E)]
        # insert_paragraph_before(primeiro) insere sempre imediatamente antes de `primeiro`,
        # ou seja, APÓS as linhas já inseridas — a ordem de iteração é a ordem final.
        primeiro = d.paragraphs[0]
        for texto, tam, negrito, alinh in linhas:
            p = primeiro.insert_paragraph_before('')
            r = p.add_run(texto)
            r.bold = negrito
            r.font.size = Pt(tam)
            p.alignment = alinh
        quebra = primeiro.insert_paragraph_before('')
        quebra.add_run().add_break(WD_BREAK.PAGE)

        destino = pathlib.Path(args.saida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        d.save(str(destino))


def selftest():
    """Fixture mínima md -> docx (e pdf, se houver chrome); acusa saída vazia/ausente."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'doc.md').write_text('# Título\n\ncorpo\n\n| a | b |\n|---|---|\n| 1 | 2 |\n',
                                    encoding='utf-8')
        base = ['--titulo', 'T', '--projeto', 'P', '--versao', '0.0', '--data', 'hoje',
                '--local', 'X/Y', '--assinatura', 'A — CONTRATANTE']
        for fmt in ('docx', 'pdf'):
            if fmt == 'pdf':
                from shutil import which
                if not which('google-chrome'):
                    print('selftest: pdf PULADO (google-chrome ausente)')
                    continue
            saida = tmp / f'doc.{fmt}'
            main([fmt, str(tmp / 'doc.md'), str(saida)] + base)
            assert saida.exists() and saida.stat().st_size > 0, f'{fmt}: saída vazia'
            print(f'selftest: {fmt} OK ({saida.stat().st_size} bytes)')
    print('selftest: OK')


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('formato', choices=['docx', 'pdf'])
    ap.add_argument('entrada')
    ap.add_argument('saida')
    ap.add_argument('--titulo', required=True)
    ap.add_argument('--projeto', required=True)
    ap.add_argument('--versao', required=True)
    ap.add_argument('--data', required=True)
    ap.add_argument('--anexo', default='')
    ap.add_argument('--local', default='')
    ap.add_argument('--assinatura', action='append', default=[])
    args = ap.parse_args(argv)
    md = le_markdown(args.entrada)
    (exporta_docx if args.formato == 'docx' else exporta_pdf)(args, md)
    print('OK', args.saida)


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        selftest()
    else:
        main(sys.argv[1:])
