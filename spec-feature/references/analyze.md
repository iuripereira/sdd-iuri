# Gate analyze — verificação cruzada spec × plan × tasks × regras canônicas

**Read-only.** Roda entre `tasks` e `implement`, sempre, no ciclo completo (é barato — não pule
"porque a spec é simples"). Não corrige nada: reporta e, quando CRÍTICO, bloqueia.

Insumos: `spec.md`, `tasks.md`, **só o cabeçalho-resumo** do `plan.md` (o bloco do template
resumo-plan.md no topo do arquivo, do comentário inicial até a linha `**Riscos assumidos:**`),
`TRUTH.md`, `canonical-rules.md` da skill projeto-init + `CLAUDE.md` do projeto. As regras
canônicas consideradas são as dos **módulos aplicáveis ao tipo** (matriz de detection.md),
mesmo que o CLAUDE.md do projeto não as monte.

## Ordem de checagem (do barato ao caro)

1. **Aceite verificável** — todo Rn da spec tem DADO/QUANDO/ENTÃO bem-formado (os três campos,
   ENTÃO com resultado verificável). Validação estrita: Rn sem cenário = ALTO. Todo RNFn tem
   Métrica com limiar verificável e Verificação preenchidas — RNF em prosa ("rápido", "seguro")
   ou qualidade redigida como Rn sem limiar = ALTO.
2. **Cobertura spec ↔ tasks** — cada Rn/RNFn tem ≥1 task (`cobre: Rn`/`RNFn`); cada task mapeia
   a um requisito ou declara `cobre: infra`. Detecta órfãos nos dois sentidos (requisito sem
   task = ALTO; task sem requisito nem `infra` = MÉDIO).
3. **Consistência spec × plan** — o resumo do plan cobre os mesmos Rn; nada no plano sem base na
   spec (scope creep); plano não contradiz cenários de aceite.
4. **Duplicação/divergência com o TRUTH.md** — requisito novo que duplica ou conflita com
   requisito vigente não marcado como MUDA/REMOVE (= ALTO); bloco MUDA que não repete cenário
   vigente aparentemente ainda válido (= ALTO — o archive substitui integralmente; cenário não
   repetido se perde).
5. **Regras canônicas** — plano/tasks não violam `canonical-rules.md` + CLAUDE.md do projeto.
   Exemplos: changelog em EN, sobrescrita de arquivo existente (clobber), PR>500 linhas
   planejado num único passo, versão com fonte da verdade ≠ tag git. Violação = CRÍTICO.

## Severidades e veredito

- **CRÍTICO** — viola regra canônica → **bloqueia** o implement até correção.
- **ALTO** — Rn sem task · task sem verificação · conflito com TRUTH.md → recomenda corrigir antes.
- **MÉDIO/BAIXO** — reporta apenas. Achado fora dos enums acima → MÉDIO por default.

**Veredito:** `BLOQUEADO` somente com ≥1 CRÍTICO · `LIBERADO COM RESSALVAS` com ALTO/MÉDIO
pendentes · `LIBERADO` sem achados relevantes. Ressalvas: o usuário decide seguir ou corrigir.

## Formato do relatório (gravar em `specs/NNN-nome/analyze.md`)

```markdown
# Analyze — Δ {{NNN}} · {{AAAA-MM-DD}}
| # | Severidade | Onde | Inconsistência | Ação sugerida |
|---|---|---|---|---|
| 1 | CRÍTICO | tasks.md T3 | {{...}} | {{...}} |

**Veredito:** LIBERADO | LIBERADO COM RESSALVAS | BLOQUEADO
```

Sem achados: tabela vazia + veredito LIBERADO (o relatório existe mesmo limpo — é o registro de
que o gate rodou). Após correções de um BLOQUEADO, rode o gate de novo e sobrescreva o relatório.
