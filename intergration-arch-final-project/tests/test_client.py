"""
test_client.py
Script de verificação automatizada que atua como cliente MCP, testando:
1. Carregamento do catálogo a partir do XLSX.
2. Execução das 4 tools.
3. Leitura do resource products://catalog.
4. Renderização do prompt recomendar_produto.
"""
import asyncio
import json
import sys
from pathlib import Path

# Configuração de encoding padrão para saída de terminal no Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ajusta path para importar src
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from server import mcp, catalog, obter_catalogo_completo, recomendar_produto


async def call_mcp_tool(mcp_server, tool_name, arguments):
    """Executa a ferramenta garantindo compatibilidade entre diferentes versões do FastMCP."""
    if hasattr(mcp_server, "call_tool"):
        return await mcp_server.call_tool(tool_name, arguments=arguments)
    tools = await mcp_server.get_tools()
    tool = tools[tool_name]
    return await tool.run(arguments)


async def run_tests():
    print("==================================================")
    print(" INICIANDO TESTES AUTOMATIZADOS DO SERVIDOR FASTMCP")
    print("==================================================")

    # 1. Teste de Catálogo e Leitura do Excel
    produtos = catalog.get_all_products()
    print(f"\n[1] Catálogo carregado com sucesso:")
    print(f"    - Total de produtos únicos indexados: {len(produtos)}")
    print(f"    - Categorias detectadas: {catalog.get_categories()}")
    assert len(produtos) == 33, f"Esperado 33 produtos, encontrado {len(produtos)}"

    # 2. Teste Tool 1: listar_produtos_por_categoria
    print("\n[2] Testando Tool: 'listar_produtos_por_categoria' (categoria='brinquedo')...")
    res_cat = await call_mcp_tool(mcp, "listar_produtos_por_categoria", arguments={"categoria": "brinquedo"})
    print(f"    - Retorno da Tool:")
    print(f"      {str(res_cat)[:250]}...")
    if hasattr(res_cat, "is_error"):
        assert not res_cat.is_error, "Erro ao listar por categoria"

    # 3. Teste Tool 2: obter_produto_por_id
    id_teste = "P003"
    print(f"\n[3] Testando Tool: 'obter_produto_por_id' (id_produto='{id_teste}')...")
    res_id = await call_mcp_tool(mcp, "obter_produto_por_id", arguments={"id_produto": id_teste})
    print(f"    - Retorno da Tool:")
    print(f"      {str(res_id)[:250]}...")
    if hasattr(res_id, "is_error"):
        assert not res_id.is_error, "Erro ao obter produto por ID"

    # 4. Teste Tool 3: buscar_produto_por_nome
    termo_busca = "quebra-cabeca"  # testando busca sem acento
    print(f"\n[4] Testando Tool: 'buscar_produto_por_nome' (nome='{termo_busca}')...")
    res_busca = await call_mcp_tool(mcp, "buscar_produto_por_nome", arguments={"nome": termo_busca})
    print(f"    - Retorno da Tool:")
    print(f"      {str(res_busca)[:250]}...")
    if hasattr(res_busca, "is_error"):
        assert not res_busca.is_error, "Erro ao buscar produto por nome"
    assert "P003" in str(res_busca), "Deveria encontrar o produto P003"

    # 5. Teste Tool 4: obter_avaliacao_produto
    print(f"\n[5] Testando Tool: 'obter_avaliacao_produto' (id_ou_nome='{id_teste}')...")
    res_aval = await call_mcp_tool(mcp, "obter_avaliacao_produto", arguments={"id_ou_nome": id_teste})
    print(f"    - Retorno da Tool:")
    print(f"      {str(res_aval)[:250]}...")
    if hasattr(res_aval, "is_error"):
        assert not res_aval.is_error, "Erro ao obter avaliacao"
    assert "3.6" in str(res_aval) or "Regular" in str(res_aval)

    # 6. Teste Resource: products://catalog
    print("\n[6] Testando Resource: 'products://catalog'...")
    conteudo_resource = obter_catalogo_completo()
    catalogo_json = json.loads(conteudo_resource)
    print(f"    - Resource lido com sucesso! Total no JSON: {catalogo_json['total_produtos']} produtos.")
    assert catalogo_json["total_produtos"] == 33

    # 7. Teste Prompt: recomendar_produto
    print("\n[7] Testando Prompt: 'recomendar_produto'...")
    texto_prompt = recomendar_produto(categoria="brinquedo", orcamento_maximo=150.0, preferencia_avaliacao_alta=True)
    print(f"    - Prompt renderizado com sucesso (primeiras 200 letras):")
    print(f"      {texto_prompt[:200]}...")
    assert "brinquedo" in texto_prompt
    assert "150.0" in texto_prompt

    print("\n==================================================")
    print(" [SUCESSO] TODOS OS TESTES PASSARAM COM EXITO!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
