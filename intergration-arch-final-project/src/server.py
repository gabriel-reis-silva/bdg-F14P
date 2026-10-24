"""
server.py
Servidor FastMCP para consulta e recomendação de produtos da Quantum Commerce.
Suporta transportes STDIO e SSE via argumentos de linha de comando.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Garantir import do data_loader
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import ProductCatalog

# Instancia o servidor FastMCP
mcp = FastMCP(
    name="QuantumCommerceServer",
    instructions="Servidor MCP para consulta de catálogo, produtos, avaliações e recomendações da Quantum Commerce."
)

# Inicializa o catálogo de produtos
catalog = ProductCatalog()


# ==========================================
# MCP TOOLS
# ==========================================

@mcp.tool()
def listar_produtos_por_categoria(categoria: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lista produtos filtrados por categoria.
    Se nenhuma categoria for informada, lista todos os produtos disponíveis.
    Categorias conhecidas: brinquedo, game, livro, maquiagem, outros.
    """
    return catalog.list_by_category(categoria)


@mcp.tool()
def obter_produto_por_id(id_produto: str) -> Dict[str, Any]:
    """
    Dado o ID de um produto (ex: 'P001', 'P003', 'P031'), retorna os dados completos:
    ID, Nome, Descrição, Categoria, Preço e Avaliação.
    """
    produto = catalog.get_product_by_id(id_produto)
    if not produto:
        return {
            "erro": f"Produto com ID '{id_produto}' não foi encontrado no catálogo.",
            "status": 404
        }
    return produto


@mcp.tool()
def buscar_produto_por_nome(nome: str) -> List[Dict[str, Any]]:
    """
    Busca produtos cujo nome ou descrição contenham o termo pesquisado (busca parcial).
    Exemplos: 'mochila', 'cafeteira', 'teclado', 'quebra-cabeça'.
    """
    resultados = catalog.search_by_name(nome)
    if not resultados:
        return [{"mensagem": f"Nenhum produto encontrado para o termo '{nome}'."}]
    return resultados


@mcp.tool()
def obter_avaliacao_produto(id_ou_nome: str) -> Dict[str, Any]:
    """
    Dado o ID ou o nome de um produto, retorna a nota de avaliação/review (de 1 a 5)
    e uma classificação qualitativa (Excelente, Regular, Crítica).
    """
    review = catalog.get_rating(id_ou_nome)
    if not review:
        return {
            "erro": f"Não foi possível localizar avaliação para '{id_ou_nome}'.",
            "status": 404
        }
    return review


# ==========================================
# MCP RESOURCES
# ==========================================

@mcp.resource("products://catalog")
def obter_catalogo_completo() -> str:
    """
    Resource que expõe o catálogo completo de produtos em formato JSON estruturado,
    incluindo totalizadores e categorias disponíveis.
    """
    todos = catalog.get_all_products()
    categorias = catalog.get_categories()
    
    dados = {
        "sistema": "Quantum Commerce MCP",
        "total_produtos": len(todos),
        "categorias_disponiveis": categorias,
        "produtos": todos
    }
    return json.dumps(dados, ensure_ascii=False, indent=2)


# ==========================================
# MCP PROMPTS
# ==========================================

@mcp.prompt()
def recomendar_produto(
    categoria: str,
    orcamento_maximo: Optional[float] = None,
    preferencia_avaliacao_alta: bool = True
) -> str:
    """
    Gera um prompt orientando o modelo a analisar e sugerir os produtos ideais
    dentro do catálogo da Quantum Commerce com base em categoria, preço e notas.
    """
    produtos = catalog.list_by_category(categoria)
    
    if orcamento_maximo is not None:
        produtos = [p for p in produtos if p["preco"] <= orcamento_maximo]

    if preferencia_avaliacao_alta:
        produtos = sorted(produtos, key=lambda x: x["avaliacao"], reverse=True)

    resumo_produtos = json.dumps(produtos, ensure_ascii=False, indent=2)

    prompt = f"""Você é um consultor especializado de compras da Quantum Commerce.
O cliente está buscando produtos na categoria '{categoria}'.
Filtros aplicados:
- Orçamento máximo: {'R$ ' + str(orcamento_maximo) if orcamento_maximo else 'Sem limite estipulado'}
- Priorizar melhores avaliações: {'Sim' if preferencia_avaliacao_alta else 'Não'}

Aqui estão as opções encontradas no nosso catálogo:
{resumo_produtos}

Por favor:
1. Apresente as 2 a 3 melhores opções de acordo com o custo-benefício e a nota de avaliação.
2. Destaque os pontos positivos e o preço de cada recomendação.
3. Alerte o cliente caso algum produto tenha nota abaixo de 3.0.
"""
    return prompt


# ==========================================
# PONTO DE ENTRADA E SUPORTE A TRANSPORTES
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Quantum Commerce MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Tipo de transporte MCP: 'stdio' (padrão) ou 'sse'."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host para o transporte SSE (padrão: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta para o transporte SSE (padrão: 8000)"
    )

    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Iniciando Servidor FastMCP via SSE em http://{args.host}:{args.port}...")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        # Padrão STDIO
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

