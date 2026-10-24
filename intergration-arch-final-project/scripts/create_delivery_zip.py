"""
create_delivery_zip.py
Gera o arquivo ZIP final do entregável conforme especificado no Desafio Quantum:
- "Entregável: um arquivo ZIP com a pasta do Código As figuras que comprovem os 6 itens pedido"
Exclui intencionalmente scripts auxiliares internos (como geradores de imagens e do zip)
para manter a pasta de código 100% limpa com o servidor oficial.
"""
import os
import shutil
import zipfile
from pathlib import Path


def create_zip():
    base_dir = Path(__file__).resolve().parent.parent.parent
    project_dir = base_dir / "intergration-arch-final-project"
    entregavel_dir = base_dir / "Integration Architecture and Connectors" / "entregavel"
    entregavel_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = "desafio_quantum_mcp_entrega.zip"
    zip_dest_entregavel = entregavel_dir / zip_filename

    print(f"Compactando arquivos para: {zip_dest_entregavel}")

    # Apenas pastas oficiais do código do servidor MCP (sem scripts utilitários)
    code_subdirs = ["data", "docs", "example", "src", "tests"]
    code_root_files = ["README.md", "requirements.txt"]

    # Figuras de evidência
    evidencias_dir = project_dir / "evidencias"

    with zipfile.ZipFile(zip_dest_entregavel, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Pasta 'codigo/' (estritamente o projeto oficial)
        for root_file in code_root_files:
            file_path = project_dir / root_file
            if file_path.exists():
                arcname = f"codigo/{root_file}"
                zf.write(file_path, arcname)
                print(f"  + [codigo] {arcname}")

        for subdir in code_subdirs:
            dir_path = project_dir / subdir
            if not dir_path.exists():
                continue
            for item in dir_path.rglob("*"):
                if item.is_file():
                    # Ignorar caches
                    if "__pycache__" in str(item) or item.suffix in [".pyc", ".pyo"]:
                        continue
                    rel = item.relative_to(project_dir)
                    arcname = f"codigo/{rel.as_posix()}"
                    zf.write(item, arcname)
                    print(f"  + [codigo] {arcname}")

        # 2. Pasta 'figuras/' (as figuras que comprovem os 6 itens pedido)
        if evidencias_dir.exists():
            for fig in sorted(evidencias_dir.iterdir()):
                if fig.is_file():
                    arcname = f"figuras/{fig.name}"
                    zf.write(fig, arcname)
                    print(f"  + [figuras] {arcname}")

    print(f"\n[SUCESSO] ZIP gerado com sucesso em:")
    print(f"  {zip_dest_entregavel} ({os.path.getsize(zip_dest_entregavel):,} bytes)")

    # Exibir resumo do conteúdo do ZIP
    with zipfile.ZipFile(zip_dest_entregavel, "r") as zf:
        print("\nConteúdo exato do arquivo ZIP:")
        for info in zf.infolist():
            print(f"  {info.filename} ({info.file_size:,} bytes)")


if __name__ == "__main__":
    create_zip()
