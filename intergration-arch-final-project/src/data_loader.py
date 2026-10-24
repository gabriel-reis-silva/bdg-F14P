"""
data_loader.py
Módulo responsável por carregar e processar os dados da planilha
quantum-commerce-chamados.xlsx, consolidando os produtos únicos em cache.
Corrige problemas comuns de mojibake (dupla codificação UTF-8 lida como Latin-1/CP1252).
"""
from pathlib import Path
from typing import Dict, List, Optional
import unicodedata
import pandas as pd


def fix_encoding(text: str) -> str:
    """Corrige textos com dupla codificação UTF-8 gravados no Excel."""
    if not isinstance(text, str):
        return text
    try:
        # Se contiver sequências típicas como 'Ã§', 'Ã¡', converte de latin1 de volta para utf-8
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def normalize_text(text: str) -> str:
    """Normaliza texto para minúsculas e sem acentos, facilitando buscas flexíveis."""
    if not text:
        return ""
    fixed = fix_encoding(text)
    nfkd = unicodedata.normalize("NFKD", fixed.strip().lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class ProductCatalog:
    """Gerencia o catálogo de produtos extraídos da base da Quantum Commerce."""

    def __init__(self, excel_path: Optional[Path | str] = None):
        if excel_path is None:
            current_dir = Path(__file__).resolve().parent
            excel_path = current_dir.parent / "data" / "quantum-commerce-chamados.xlsx"
        
        self.excel_path = Path(excel_path)
        self._products_by_id: Dict[str, dict] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Lê a planilha Excel e indexa produtos únicos."""
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.excel_path}")

        df = pd.read_excel(self.excel_path)

        cols = [
            "id_produto",
            "nome_produto",
            "categoria_produto",
            "preco",
            "avaliacao_produto",
            "descricao_produto",
        ]

        for expected in cols:
            if expected not in df.columns:
                raise ValueError(f"Coluna obrigatória ausente no arquivo Excel: '{expected}'")

        unique_products = df.drop_duplicates(subset=["id_produto"]).copy()

        for _, row in unique_products.iterrows():
            prod_id = str(row["id_produto"]).strip()
            if not prod_id or prod_id.lower() == "nan":
                continue

            try:
                preco_val = float(row["preco"])
            except (ValueError, TypeError):
                preco_val = 0.0

            try:
                avaliacao_val = float(row["avaliacao_produto"])
            except (ValueError, TypeError):
                avaliacao_val = 0.0

            nome = fix_encoding(str(row["nome_produto"]).strip())
            descricao = fix_encoding(str(row["descricao_produto"]).strip()) if pd.notna(row["descricao_produto"]) else ""
            categoria = fix_encoding(str(row["categoria_produto"]).strip()).lower()

            self._products_by_id[prod_id] = {
                "id_produto": prod_id,
                "nome": nome,
                "descricao": descricao,
                "categoria": categoria,
                "preco": round(preco_val, 2),
                "avaliacao": round(avaliacao_val, 2),
                "_normalized_nome": normalize_text(nome),
                "_normalized_desc": normalize_text(descricao),
                "_normalized_cat": normalize_text(categoria),
            }

    def get_all_products(self) -> List[dict]:
        """Retorna todos os produtos do catálogo (removendo chaves internas de busca)."""
        return [
            {k: v for k, v in p.items() if not k.startswith("_")}
            for p in self._products_by_id.values()
        ]

    def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """Obtém os dados de um produto pelo seu ID (ex: 'P003')."""
        if not product_id:
            return None
        prod = self._products_by_id.get(str(product_id).strip())
        if not prod:
            return None
        return {k: v for k, v in prod.items() if not k.startswith("_")}

    def list_by_category(self, category: Optional[str] = None) -> List[dict]:
        """
        Lista produtos filtrando pela categoria (com normalização de acentos).
        Se categoria for vazia ou None, lista todos os produtos.
        """
        if not category:
            return self.get_all_products()

        cat_norm = normalize_text(category)
        return [
            {k: v for k, v in prod.items() if not k.startswith("_")}
            for prod in self._products_by_id.values()
            if cat_norm in prod["_normalized_cat"]
        ]

    def search_by_name(self, query: str) -> List[dict]:
        """Busca produtos cujo nome ou descrição contenham o termo pesquisado (insensível a acentos/caixa)."""
        if not query:
            return []

        term_norm = normalize_text(query)
        results = []
        for prod in self._products_by_id.values():
            if term_norm in prod["_normalized_nome"] or term_norm in prod["_normalized_desc"]:
                results.append({k: v for k, v in prod.items() if not k.startswith("_")})
        return results

    def get_rating(self, identifier: str) -> Optional[dict]:
        """
        Retorna a nota de avaliação de um produto por ID ou busca por nome.
        """
        if not identifier:
            return None

        clean_id = identifier.strip()
        prod = self.get_product_by_id(clean_id)
        
        if not prod:
            matching = self.search_by_name(clean_id)
            if matching:
                prod = matching[0]

        if not prod:
            return None

        nota = prod["avaliacao"]
        if nota >= 4.0:
            status = "Excelente"
        elif nota >= 3.0:
            status = "Regular"
        else:
            status = "Critica / Baixa"

        return {
            "id_produto": prod["id_produto"],
            "nome": prod["nome"],
            "avaliacao": nota,
            "status_qualitativo": status,
        }

    def get_categories(self) -> List[str]:
        """Retorna a lista única de categorias presentes no catálogo."""
        cats = {prod["categoria"] for prod in self._products_by_id.values()}
        return sorted(list(cats))

