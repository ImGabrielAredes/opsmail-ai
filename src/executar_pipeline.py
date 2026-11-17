import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_SRC = BASE_DIR / "src"

# Etapas do pipeline, na ordem correta
ETAPAS = [
    "inspecionar_chamados.py",
    "inspecionar_relatos.py",
    "conciliar.py",
    "regras_operacionais.py",
    "persistir_sqlite.py"
]

def executar(nome_script):
    caminho_script = PASTA_SRC / nome_script

    print(f"\nIniciando: {nome_script}", flush=True)

    subprocess.run(
        [sys.executable, str(caminho_script)],
        cwd=BASE_DIR,
        check=True
    )

    print(f"Concluído: {nome_script}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--com-ia",
        action="store_true",
        help="Executa também o Gemini e a verificação final."
    )

    argumentos = parser.parse_args()

    for etapa in ETAPAS:
        executar(etapa)

    if argumentos.com_ia:
        executar("analisar_relatos.py")
        executar("verificar_pipeline.py")

    print("\nPIPELINE FINALIZADO COM SUCESSO!")
