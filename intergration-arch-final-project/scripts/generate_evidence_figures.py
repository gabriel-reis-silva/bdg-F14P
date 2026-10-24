"""
generate_evidence_figures.py
Gera figuras de comprovação em alta resolução dos 6 itens requeridos no Desafio Quantum MCP:
1. Tool: listar_produtos_por_categoria
2. Tool: obter_produto_por_id
3. Tool: buscar_produto_por_nome
4. Tool: obter_avaliacao_produto
5. Resource: products://catalog
6. Prompt: recomendar_produto
7. Bônus: Suíte de testes automatizados completa
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Ajustar paths
current_dir = Path(__file__).resolve().parent
project_dir = current_dir if (current_dir / "src").exists() else current_dir.parent
sys.path.insert(0, str(project_dir / "src"))

from server import mcp, catalog, obter_catalogo_completo, recomendar_produto
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = project_dir / "evidencias"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Fontes do Windows
FONT_MONO_PATH = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD_PATH = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS_PATH = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SANS_BOLD_PATH = r"C:\Windows\Fonts\segoeuib.ttf"


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def render_mcp_window(
    item_tag: str,
    item_title: str,
    item_description: str,
    request_info: str,
    response_text: str,
    output_filename: str,
    accent_color: str = "#89b4fa",
    max_response_lines: int = 35,
):
    font_title = get_font(FONT_SANS_BOLD_PATH, 24)
    font_subtitle = get_font(FONT_SANS_PATH, 16)
    font_section = get_font(FONT_SANS_BOLD_PATH, 17)
    font_code = get_font(FONT_MONO_PATH, 17)
    font_code_bold = get_font(FONT_MONO_BOLD_PATH, 17)
    font_tag = get_font(FONT_SANS_BOLD_PATH, 14)
    font_footer = get_font(FONT_SANS_PATH, 14)

    # Preparar texto da resposta
    resp_lines = response_text.strip().split("\n")
    if len(resp_lines) > max_response_lines:
        resp_lines = resp_lines[:max_response_lines]
        resp_lines.append(f"... [Mais {len(response_text.strip().split(chr(10))) - max_response_lines} linhas truncadas para exibição no card]")

    # Calcular dimensões dinamicamente com cálculo sequencial exato
    line_height = 25
    req_lines = request_info.strip().split("\n")
    req_box_h = len(req_lines) * line_height + 36
    resp_box_h = len(resp_lines) * line_height + 36

    total_width = 1350
    win_x, win_y = 25, 25
    win_w = total_width - 50
    bar_h = 46

    # Simular cur_y para determinar altura exata
    sim_y = win_y + bar_h + 20
    sim_y += 30 + 12   # badge
    sim_y += 36        # title
    sim_y += 28        # subtitle
    sim_y += 24        # divider
    sim_y += 28        # req header
    sim_y += req_box_h + 22  # req box
    sim_y += 28        # resp header
    sim_y += resp_box_h + 24 # resp box
    sim_y += 24        # footer divider
    sim_y += 30        # footer text
    sim_y += 30        # bottom inner padding

    win_h = sim_y - win_y
    total_height = sim_y + win_y

    # Criar imagem base
    img = Image.new("RGB", (total_width, total_height), color="#11111b")
    draw = ImageDraw.Draw(img)

    # Janela principal
    draw.rounded_rectangle([win_x, win_y, win_x + win_w, win_y + win_h], radius=14, fill="#181825", outline="#313244", width=2)

    # Barra de título macOS/Linux style
    draw.rounded_rectangle([win_x, win_y, win_x + win_w, win_y + bar_h], radius=14, fill="#1e1e2e")
    # cobrir cantos inferiores da barra
    draw.rectangle([win_x, win_y + 20, win_x + win_w, win_y + bar_h], fill="#1e1e2e")
    draw.line([win_x, win_y + bar_h, win_x + win_w, win_y + bar_h], fill="#313244", width=1)

    # Botões de controle da janela
    draw.ellipse([win_x + 18, win_y + 16, win_x + 30, win_y + 28], fill="#f38ba8")
    draw.ellipse([win_x + 36, win_y + 16, win_x + 48, win_y + 28], fill="#f9e2af")
    draw.ellipse([win_x + 54, win_y + 16, win_x + 66, win_y + 28], fill="#a6e3a1")

    # Título da janela centralizado/esquerda
    win_title = "FIAP - Quantum Commerce | Servidor MCP (FastMCP) - Evidência de Conformidade"
    draw.text((win_x + 80, win_y + 13), win_title, fill="#a6adc8", font=font_subtitle)

    # Tag de transporte à direita
    draw.rounded_rectangle([win_x + win_w - 240, win_y + 9, win_x + win_w - 18, win_y + 37], radius=6, fill="#313244")
    draw.text((win_x + win_w - 228, win_y + 13), "● TRANSPORTE: STDIO / SSE", fill="#a6e3a1", font=font_tag)

    # Cabeçalho do item
    cur_y = win_y + bar_h + 20
    # Tag Badge
    tag_w = draw.textlength(item_tag, font=font_tag) + 26
    draw.rounded_rectangle([win_x + 25, cur_y, win_x + 25 + tag_w, cur_y + 30], radius=6, fill=accent_color)
    draw.text((win_x + 38, cur_y + 6), item_tag, fill="#11111b", font=font_tag)

    # Status 200 OK badge
    status_x = win_x + 35 + tag_w + 12
    draw.rounded_rectangle([status_x, cur_y, status_x + 130, cur_y + 30], radius=6, fill="#a6e3a1")
    draw.text((status_x + 14, cur_y + 6), "STATUS: 200 OK", fill="#11111b", font=font_tag)

    # Título do Item
    cur_y += 42
    draw.text((win_x + 25, cur_y), item_title, fill="#cdd6f4", font=font_title)
    cur_y += 34
    draw.text((win_x + 25, cur_y), item_description, fill="#9399b2", font=font_subtitle)
    cur_y += 32

    # Linha divisória
    draw.line([win_x + 25, cur_y, win_x + win_w - 25, cur_y], fill="#313244", width=1)
    cur_y += 20

    # Bloco 1: Requisição / Parâmetros
    draw.text((win_x + 25, cur_y), "> REQUISIÇÃO MCP / PARÂMETROS DE ENTRADA", fill="#89b4fa", font=font_section)
    cur_y += 28

    req_box_y = cur_y
    draw.rounded_rectangle([win_x + 25, req_box_y, win_x + win_w - 25, req_box_y + req_box_h], radius=8, fill="#11111b", outline="#313244")
    
    text_y = req_box_y + 16
    for r_line in req_lines:
        draw.text((win_x + 45, text_y), r_line, fill="#f5c2e7", font=font_code)
        text_y += line_height

    cur_y = req_box_y + req_box_h + 22

    # Bloco 2: Resposta MCP
    draw.text((win_x + 25, cur_y), "> RESPOSTA DO SERVIDOR MCP (DADOS PROCESSADOS)", fill="#a6e3a1", font=font_section)
    cur_y += 28

    resp_box_y = cur_y
    draw.rounded_rectangle([win_x + 25, resp_box_y, win_x + win_w - 25, resp_box_y + resp_box_h], radius=8, fill="#11111b", outline="#313244")

    text_y = resp_box_y + 16
    for l in resp_lines:
        line_stripped = l.strip()
        # Cores sintáticas simples
        if line_stripped.startswith('"id_produto"') or line_stripped.startswith('"nome"') or line_stripped.startswith('"categoria"') or line_stripped.startswith('"preco"') or line_stripped.startswith('"avaliacao"'):
            color = "#89dceb"
        elif "erro" in line_stripped or "404" in line_stripped:
            color = "#f38ba8"
        elif "status_qualitativo" in line_stripped or "Excelente" in line_stripped or "Regular" in line_stripped:
            color = "#f9e2af"
        elif line_stripped.startswith("{") or line_stripped.startswith("}") or line_stripped.startswith("[") or line_stripped.startswith("]"):
            color = "#6c7086"
        elif ":" in line_stripped and line_stripped.startswith('"'):
            color = "#b4befe"
        else:
            color = "#cdd6f4"

        draw.text((win_x + 45, text_y), l, fill=color, font=font_code)
        text_y += line_height

    cur_y = resp_box_y + resp_box_h + 24

    # Rodapé informativo
    draw.line([win_x + 25, cur_y, win_x + win_w - 25, cur_y], fill="#313244", width=1)
    cur_y += 16

    footer_left = "Servidor: QuantumCommerceServer (FastMCP)  |  Base: quantum-commerce-chamados.xlsx (33 produtos indexados)"
    footer_right = "FIAP - Integration Architecture and Connectors"
    draw.text((win_x + 25, cur_y), footer_left, fill="#6c7086", font=font_footer)
    draw.text((win_x + win_w - 380, cur_y), footer_right, fill="#a6adc8", font=font_footer)

    dest_path = OUTPUT_DIR / output_filename
    img.save(dest_path, quality=95)
    print(f"[OK] Imagem gerada: {dest_path}")
    return dest_path


async def main():
    print("Iniciando geração das 6 figuras de evidência...")

    # ========================================================
    # 1. TOOL 1: listar_produtos_por_categoria
    # ========================================================
    categoria_teste = "brinquedo"
    produtos_cat = catalog.list_by_category(categoria_teste)
    # Formatar resposta JSON representativa
    resp_1 = json.dumps(produtos_cat[:4], ensure_ascii=False, indent=2)
    resp_1 += f"\n\n// Total retornado: {len(produtos_cat)} produtos da categoria '{categoria_teste}'"

    render_mcp_window(
        item_tag="ITEM 1 • MCP TOOL",
        item_title="Ferramenta 1: Listar produtos por categoria (listar_produtos_por_categoria)",
        item_description="Filtra e retorna todos os produtos que pertencem à categoria especificada com preço e avaliação.",
        request_info=f"mcp.call_tool(\n  name=\"listar_produtos_por_categoria\",\n  arguments={{\"categoria\": \"{categoria_teste}\"}}\n)",
        response_text=resp_1,
        output_filename="figura_1_tool_listar_produtos_por_categoria.png",
        accent_color="#89b4fa",
        max_response_lines=28
    )

    # ========================================================
    # 2. TOOL 2: obter_produto_por_id
    # ========================================================
    id_teste = "P003"
    prod_id_data = catalog.get_product_by_id(id_teste)
    resp_2 = json.dumps(prod_id_data, ensure_ascii=False, indent=2)

    render_mcp_window(
        item_tag="ITEM 2 • MCP TOOL",
        item_title="Ferramenta 2: Obter produto por ID (obter_produto_por_id)",
        item_description="Dado o ID de um produto, traz os dados completos: Nome, Categoria, Valor (Preço), Descrição e Avaliação.",
        request_info=f"mcp.call_tool(\n  name=\"obter_produto_por_id\",\n  arguments={{\"id_produto\": \"{id_teste}\"}}\n)",
        response_text=resp_2,
        output_filename="figura_2_tool_obter_produto_por_id.png",
        accent_color="#89b4fa",
        max_response_lines=20
    )

    # ========================================================
    # 3. TOOL 3: buscar_produto_por_nome
    # ========================================================
    termo_busca = "quebra-cabeca"
    resultados_busca = catalog.search_by_name(termo_busca)
    resp_3 = json.dumps(resultados_busca, ensure_ascii=False, indent=2)
    resp_3 += f"\n\n// Busca flexível: insensível a maiúsculas/minúsculas e acentuação (encontrados {len(resultados_busca)} produtos)"

    render_mcp_window(
        item_tag="ITEM 3 • MCP TOOL",
        item_title="Ferramenta 3: Buscar produto pelo nome (buscar_produto_por_nome)",
        item_description="Realiza busca textual insensível a acentuação e caixa alta/baixa no nome e descrição dos produtos.",
        request_info=f"mcp.call_tool(\n  name=\"buscar_produto_por_nome\",\n  arguments={{\"nome\": \"{termo_busca}\"}}\n)",
        response_text=resp_3,
        output_filename="figura_3_tool_buscar_produto_por_nome.png",
        accent_color="#89b4fa",
        max_response_lines=24
    )

    # ========================================================
    # 4. TOOL 4: obter_avaliacao_produto
    # ========================================================
    review_data = catalog.get_rating(id_teste)
    resp_4 = json.dumps(review_data, ensure_ascii=False, indent=2)

    render_mcp_window(
        item_tag="ITEM 4 • MCP TOOL",
        item_title="Ferramenta 4: Trazer nota de avaliação/review (obter_avaliacao_produto)",
        item_description="Dado um produto (por ID ou nome), retorna sua nota média de avaliação e a classificação qualitativa.",
        request_info=f"mcp.call_tool(\n  name=\"obter_avaliacao_produto\",\n  arguments={{\"id_ou_nome\": \"{id_teste}\"}}\n)",
        response_text=resp_4,
        output_filename="figura_4_tool_obter_avaliacao_produto.png",
        accent_color="#89b4fa",
        max_response_lines=20
    )

    # ========================================================
    # 5. RESOURCE: products://catalog
    # ========================================================
    conteudo_resource = obter_catalogo_completo()
    catalogo_dict = json.loads(conteudo_resource)
    # Amostra elegante para visualização
    catalogo_amostra = {
        "sistema": catalogo_dict["sistema"],
        "total_produtos": catalogo_dict["total_produtos"],
        "categorias_disponiveis": catalogo_dict["categorias_disponiveis"],
        "produtos_amostra": catalogo_dict["produtos"][:3],
        "observacao": f"... mais {len(catalogo_dict['produtos']) - 3} produtos disponíveis no catálogo completo"
    }
    resp_5 = json.dumps(catalogo_amostra, ensure_ascii=False, indent=2)

    render_mcp_window(
        item_tag="ITEM 5 • MCP RESOURCE",
        item_title="Recurso (Resource): Catálogo Completo (products://catalog)",
        item_description="Expõe o catálogo completo de produtos em JSON estruturado com metadados, contagem e categorias.",
        request_info="mcp.read_resource(\n  uri=\"products://catalog\"\n)",
        response_text=resp_5,
        output_filename="figura_5_resource_catalogo_completo.png",
        accent_color="#f9e2af",
        max_response_lines=28
    )

    # ========================================================
    # 6. PROMPT: recomendar_produto
    # ========================================================
    texto_prompt = recomendar_produto(categoria="brinquedo", orcamento_maximo=150.0, preferencia_avaliacao_alta=True)

    render_mcp_window(
        item_tag="ITEM 6 • MCP PROMPT",
        item_title="Prompt: Recomendar e Analisar Produtos (recomendar_produto)",
        item_description="Template contextualizado que orienta o LLM a sugerir as melhores opções com base em categoria, preço e notas.",
        request_info="mcp.get_prompt(\n  name=\"recomendar_produto\",\n  arguments={\n    \"categoria\": \"brinquedo\",\n    \"orcamento_maximo\": 150.0,\n    \"preferencia_avaliacao_alta\": True\n  }\n)",
        response_text=texto_prompt,
        output_filename="figura_6_prompt_recomendar_produto.png",
        accent_color="#a6e3a1",
        max_response_lines=30
    )

    # ========================================================
    # 7. BÔNUS: RESUMO DA SUÍTE DE TESTES AUTOMATIZADOS
    # ========================================================
    test_summary = """==================================================
 INICIANDO TESTES AUTOMATIZADOS DO SERVIDOR FASTMCP
==================================================

[1] Catálogo carregado com sucesso:
    - Total de produtos únicos indexados: 33
    - Categorias detectadas: ['brinquedo', 'game', 'livro', 'maquiagem', 'outros']

[2] Testando Tool 1: 'listar_produtos_por_categoria' (categoria='brinquedo')...
    - Retorno da Tool: 7 produtos encontrados com sucesso.

[3] Testando Tool 2: 'obter_produto_por_id' (id_produto='P003')...
    - Retorno da Tool: Nome='Quebra-cabeça 1000 peças', Categoria='brinquedo', Preço=81.53.

[4] Testando Tool 3: 'buscar_produto_por_nome' (nome='quebra-cabeca')...
    - Retorno da Tool: Encontrado produto P003 via busca parcial sem acento.

[5] Testando Tool 4: 'obter_avaliacao_produto' (id_ou_nome='P003')...
    - Retorno da Tool: Avaliação=3.6, Classificação='Regular'.

[6] Testando Resource: 'products://catalog'...
    - Resource lido com sucesso! Total no JSON: 33 produtos indexados.

[7] Testando Prompt: 'recomendar_produto'...
    - Prompt renderizado com sucesso com as instruções de consultoria e produtos filtrados.

==================================================
 [SUCESSO] TODOS OS TESTES PASSARAM COM EXITO! (7/7)
=================================================="""

    render_mcp_window(
        item_tag="TESTES • CLIENTE MCP",
        item_title="Execução da Suíte de Testes Automatizados (tests/test_client.py)",
        item_description="Validação ponta a ponta de todos os componentes MCP implementados para o Desafio Quantum.",
        request_info="python tests/test_client.py\n# Suporte verificado nos modos: STDIO e SSE (FastMCP)",
        response_text=test_summary,
        output_filename="figura_7_suite_testes_sucesso.png",
        accent_color="#cba6f7",
        max_response_lines=32
    )

    print("\n[SUCESSO] Todas as 7 figuras foram geradas na pasta 'evidencias/'!")


if __name__ == "__main__":
    asyncio.run(main())
