# Quantum Commerce - Servidor MCP com FastMCP

Servidor MCP (Model Context Protocol) construído com **FastMCP** em Python, que integra dados do catálogo da Quantum Commerce a partir do arquivo Excel `data/quantum-commerce-chamados.xlsx`.

Suporta conexões via **STDIO** (padrão) e **SSE** (Server-Sent Events via HTTP).

---

## 🚀 Requisitos e Instalação

1. Certifique-se de ter o Python 3.10+ instalado.
2. Navegue até a pasta do projeto:
```bash
cd intergration-arch-final-project
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## 🛠️ Recursos Implementados no Servidor MCP

### 1. Ferramentas (Tools)
- `listar_produtos_por_categoria(categoria)`: Lista os produtos filtrados por categoria (ou exibe todas as categorias/produtos se vazio).
- `obter_produto_por_id(id_produto)`: Dado o ID do produto (ex: `P003`), retorna seus dados completos: ID, Nome, Descrição, Categoria, Preço e Avaliação.
- `buscar_produto_por_nome(nome)`: Busca textual parcial no catálogo pelo nome ou descrição.
- `obter_avaliacao_produto(id_ou_nome)`: Retorna a nota média (review) de 1 a 5 e a classificação qualitativa (Excelente, Regular, Crítica).

### 2. Recursos (Resources)
- `products://catalog`: Retorna o catálogo completo estruturado em JSON contendo metadados, contagem e a lista integral de produtos indexados.

### 3. Prompts
- `recomendar_produto(categoria, orcamento_maximo, preferencia_avaliacao_alta)`: Prompt pré-formatado que orienta o LLM a analisar o catálogo e propor as melhores recomendações de compra com base nas restrições fornecidas.

---

## 🔌 Executando o Servidor

### Modo STDIO (Padrão para Clientes MCP Desktop como Claude Desktop e Cursor)
```bash
python src/server.py --transport stdio
```

#### Exemplo de configuração no Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "quantum-commerce": {
      "command": "python",
      "args": [
        "C:\\caminho\\completo\\intergration-arch-final-project\\src\\server.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

### Modo SSE (Server-Sent Events / HTTP)
Para rodar como serviço HTTP para clientes remotos:
```bash
python src/server.py --transport sse --host 0.0.0.0 --port 8000
```
O servidor estará acessível em `http://localhost:8000/sse`.

---

## 🧪 Testes Automatizados

Para rodar a suíte de testes do cliente MCP:
```bash
python tests/test_client.py
```



---

## 📸 Evidências Comprobatórias (6 Itens da Atividade)

As capturas de comprovação de execução dos 6 itens solicitados estão disponíveis na pasta [`evidencias/`](./evidencias/):

1. **Tool 1**: [`figura_1_tool_listar_produtos_por_categoria.png`](./evidencias/figura_1_tool_listar_produtos_por_categoria.png)
2. **Tool 2**: [`figura_2_tool_obter_produto_por_id.png`](./evidencias/figura_2_tool_obter_produto_por_id.png)
3. **Tool 3**: [`figura_3_tool_buscar_produto_por_nome.png`](./evidencias/figura_3_tool_buscar_produto_por_nome.png)
4. **Tool 4**: [`figura_4_tool_obter_avaliacao_produto.png`](./evidencias/figura_4_tool_obter_avaliacao_produto.png)
5. **Resource**: [`figura_5_resource_catalogo_completo.png`](./evidencias/figura_5_resource_catalogo_completo.png)
6. **Prompt**: [`figura_6_prompt_recomendar_produto.png`](./evidencias/figura_6_prompt_recomendar_produto.png)
7. **Suíte Completa**: [`figura_7_suite_testes_sucesso.png`](./evidencias/figura_7_suite_testes_sucesso.png)
