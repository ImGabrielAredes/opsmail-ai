
from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

caminho_banco = (
    BASE_DIR / "data" / "processed" / "opsmail.db"
)

# Quantidades esperadas no nosso MVP
tabelas_esperadas = {
    "raw_chamados": 5,
    "raw_relatos": 8,
    "conciliacao": 8,
    "indicadores_operacionais": 5,
    "analises_ia": 2
}

with sqlite3.connect(caminho_banco) as conexao:

    for tabela, quantidade_esperada in tabelas_esperadas.items():
        consulta = f"SELECT COUNT(*) FROM {tabela}"

        quantidade = conexao.execute(
            consulta
        ).fetchone()[0]

        assert quantidade == quantidade_esperada, (
            f"{tabela}: esperados {quantidade_esperada}, "
            f"encontrados {quantidade}"
        )

        print(f"{tabela}: {quantidade} registros - OK")

    # Cruzar informações produzidas por etapas diferentes
    consulta = """
        SELECT
            a.relato_id,
            a.chamado_id,
            c.status AS status_cadastrado,
            a.situacao_reportada
        FROM analises_ia AS a
        JOIN raw_chamados AS c
            ON a.chamado_id = c.chamado_id
        ORDER BY a.relato_id;
    """

    resultado = pd.read_sql_query(
        consulta,
        conexao
    )

    print("\nConciliação entre IA e chamados:")
    print(resultado.to_string(index=False))

print("\nVerificação integrada concluída!")
