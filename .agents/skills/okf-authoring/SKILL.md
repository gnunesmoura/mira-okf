---
name: okf-authoring
description: Crie e edite conteúdo OKF neste repositório usando frontmatter YAML obrigatório, `index.md` e `log.md` conforme a SPEC local. Use quando a tarefa envolver bundles OKF, documentação estrutural, links entre conceitos ou manutenção do acervo.
---

# Open Knowledge Format Authoring

Use esta skill para autoria e manutenção de conteúdo OKF neste repositório.

## Fonte de verdade

- Consulte [`references/SPEC.md`](references/SPEC.md) antes de alterar conteúdo OKF.
- A spec fica apenas como referência interna da skill.

## Regras práticas

1. Todo documento de conceito deve começar com frontmatter YAML válido.
2. O campo `type` é obrigatório e não pode ficar vazio.
3. `index.md` não usa frontmatter; use-o só para listar conteúdos e dar visão progressiva.
4. `log.md` não usa frontmatter; registre eventos por data `YYYY-MM-DD`, mais recente primeiro.
5. Prefira links relativos ao bundle; links quebrados são tolerados.
6. Preserve a estrutura existente do acervo e escreva de forma curta e factual.

## Escopo

- Esta skill cobre apenas autoria OKF neste repositório.
- Não altere `references/SPEC.md` fora de uma atualização deliberada da referência.
