# Evidências de Conformidade - Desafio Quantum MCP

Este diretório contém as capturas comprobatórias dos **6 itens** solicitados na atividade acadêmica da FIAP (**Integration Architecture and Connectors**), geradas diretamente a partir do processamento do catálogo da Quantum Commerce (`data/quantum-commerce-chamados.xlsx`).

---

### 📸 Relação das Figuras Comprobatórias

| Item da Atividade | Arquivo de Imagem | Descrição da Comprovação |
| :--- | :--- | :--- |
| **Item 1: Tool** | [`figura_1_tool_listar_produtos_por_categoria.png`](./figura_1_tool_listar_produtos_por_categoria.png) | Execução de `listar_produtos_por_categoria` filtrando pela categoria `brinquedo`. Retorna lista completa com preços e notas. |
| **Item 2: Tool** | [`figura_2_tool_obter_produto_por_id.png`](./figura_2_tool_obter_produto_por_id.png) | Execução de `obter_produto_por_id` para `P003`. Retorna Nome, Categoria, Valor (Preço), Descrição e Avaliação. |
| **Item 3: Tool** | [`figura_3_tool_buscar_produto_por_nome.png`](./figura_3_tool_buscar_produto_por_nome.png) | Execução de `buscar_produto_por_nome` com termo parcial `"quebra-cabeca"` (insensível a acentos e caixa). |
| **Item 4: Tool** | [`figura_4_tool_obter_avaliacao_produto.png`](./figura_4_tool_obter_avaliacao_produto.png) | Execução de `obter_avaliacao_produto` para `P003`. Retorna nota numérica (`3.6`) e classificação qualitativa (`Regular`). |
| **Item 5: Resource** | [`figura_5_resource_catalogo_completo.png`](./figura_5_resource_catalogo_completo.png) | Leitura do recurso `products://catalog`. Expõe em JSON estruturado os 33 produtos, metadados e categorias. |
| **Item 6: Prompt** | [`figura_6_prompt_recomendar_produto.png`](./figura_6_prompt_recomendar_produto.png) | Renderização do prompt `recomendar_produto` com filtros de categoria (`brinquedo`), orçamento (`R$ 150`) e foco em avaliações altas. |
| **Bônus: Suíte Integrada** | [`figura_7_suite_testes_sucesso.png`](./figura_7_suite_testes_sucesso.png) | Suíte automatizada `tests/test_client.py` executando todos os testes com 100% de sucesso (7/7). |

---

> [!NOTE]
> Todas as figuras podem ser regeneradas a qualquer momento executando:
> ```bash
> python scripts/generate_evidence_figures.py
> ```

