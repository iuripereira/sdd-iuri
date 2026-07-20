---
name: doc-entregavel
description: Use when exporting a frozen client deliverable (PDF/DOCX with signature cover and embedded diagrams) from a project whose doc-profile.yaml declares publico.cliente true — at the moment declared in the profile (entrega-prd, fechamento-fase). Triggers include "/sdd-iuri:doc-entregavel", "exportar entregável", "gerar PDF para o cliente", "documento para assinatura", "congelar o PRD", or the visual-documentation gate of the sdd-iuri spec flow.
---

# doc-entregavel

## Overview

Exporta o **entregável congelado para o cliente**: renderiza os diagramas declarados no `doc-profile.yaml`, monta o documento final (PRD/spec + diagramas embutidos + capa de assinatura) e exporta **PDF e/ou DOCX** em `docs/entregaveis/`. Generalização do pipeline validado nos PRDs e contratos IMEX. Documentação cliente é **isenta da economia de tokens** (exceção registrada na ADR-0009 do sdd-iuri) — completude e fidelidade visual dominam; a renderização é via CLI, o custo de tokens é marginal.

Distinção central (ADR-0009): documentação **interna** é viva (Mermaid inline, mantida junto do código); o **entregável** é congelado — exportado em momento definido, versionado no nome do arquivo, re-assinado a cada baseline. **Nunca sobrescreva um entregável já enviado**: nova baseline → novo arquivo → nova assinatura.

## Processo

1. **Ler o `doc-profile.yaml`** da raiz do projeto. Exige `publico.cliente: true` — perfil ausente ou `cliente: false` → oriente o usuário a criar/ajustar o perfil (template no projeto-init) e **pare**; a decisão é dele, não sua.
2. **Renderizar os diagramas** declarados com `obrigatorio: true`, a partir dos fontes na pasta `saida` do perfil (ex.: `docs/diagrams/`):
   - `.mmd` → `mmdc -i arq.mmd -o arq.svg` (pdf) e `-o arq.png --scale 2` (docx)
   - `.dbml` → `dbml-renderer -i schema.dbml -o schema.svg`
   - `.puml` → `plantuml -tsvg` · `.d2` → `d2 arq.d2 arq.svg`
   Ferramenta ausente → reporte o comando de instalação (seção de setup do README do sdd-iuri) e pergunte se segue sem o diagrama — **nunca entregue silenciosamente incompleto**.
   SVG que precise virar PNG (docx): `rsvg-convert -z 2 arq.svg -o arq.png`; sem rsvg-convert, embrulhe num HTML mínimo (`<img src="arq.svg">`, margin 0) e capture com `google-chrome --headless=new --screenshot --hide-scrollbars --window-size=<LxA nativo do SVG>` — screenshot do SVG "cru" corta e captura scrollbar.
3. **Montar o markdown final**: documento base (PRD.md ou o que o usuário indicar) com os diagramas referenciados como imagem markdown — SVG no pdf, PNG no docx:
   ```markdown
   ![Arquitetura]({{saida do perfil}}/arquitetura.svg)
   ```
   Confirme com o usuário versão e data da baseline.
4. **Exportar** com `${CLAUDE_PLUGIN_ROOT}/skills/doc-entregavel/scripts/exporta_entregavel.py`, uma chamada por formato em `entregaveis.formato`, capa vinda de `entregaveis.capa` do perfil:
   ```bash
   exporta_entregavel.py pdf  PRD.md docs/entregaveis/prd-<projeto>-v<versao>.pdf \
     --titulo "<capa.titulo>" --projeto "<nome>" --versao <v> --data "<data por extenso>" \
     --anexo "<capa.anexo>" --local "<capa.local>" --assinatura "<capa.assinaturas[0]>" ...
   ```
5. **Verificar e reportar**: abra/inspecione o resultado (tamanho > 0, diagramas presentes, capa correta) e liste os arquivos gerados. Dependências do host: `pip install pypandoc-binary python-docx markdown` (docx/pdf) e google-chrome (pdf) — ausentes, reporte o comando e pare o formato afetado, sem quebrar o outro.

## Erros comuns

| Erro | Correto |
|---|---|
| Sobrescrever entregável de baseline anterior | Novo arquivo com a nova versão no nome; o antigo é histórico assinado |
| Exportar sem `publico.cliente: true` no perfil | Orientar a registrar a decisão no doc-profile primeiro (ADR-0009) |
| SVG no DOCX | PNG no docx (`--scale 2`); SVG só no pdf |
| Entregar sem um diagrama porque a CLI faltava | Reportar a ferramenta ausente e perguntar — nunca degradar em silêncio |
| Capa hardcoded no script | Capa vem de `entregaveis.capa` do doc-profile, por argumento |
| "Enxugar" o entregável por economia de tokens | Cliente é isento (ADR-0009); completude domina. RNF1 vale só para a doc interna |

## Arquivos da skill

- `scripts/exporta_entregavel.py` — md → docx (pypandoc + python-docx) e md → pdf (markdown → HTML+CSS → chrome headless), capa parametrizada. `--selftest` valida o próprio script.
