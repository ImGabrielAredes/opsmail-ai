from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_RAW = BASE_DIR / "data" / "raw"
PASTA_PROCESSED = BASE_DIR / "data" / "processed"

caminho_banco = PASTA_PROCESSED /"opsmail.db"

# 1. Carregar os dados originais
raw_chamados = pd.read_csv(
    PASTA_RAW / "chamados.csv",
    dtype="string",
    keep_default_na=False
)

raw_relatos = pd.read_json(
    PASTA_RAW / "relatos.json",
    dtype=False
)

# 2. Carregar os resultados do pipeline
conciliacao = pd.read_csv(
    PASTA_PROCESSED / "conciliacao.csv"
)

indicadores = pd.read_csv(
    PASTA_PROCESSED / "indicadores_operacionais.csv"
)

# 3. Organizar as tabelas
tabelas = {
    "raw_chamados": raw_chamados,
    "raw_relatos": raw_relatos,
    "conciliacao": conciliacao,
    "indicadores_operacionais": indicadores
}

# 4. Criar conexão com o SQLite
conexao = sqlite3.connect(caminho_banco)


try:
    # 5. Gravar todas as tabelas no banco
    for nome_tabela, dataframe in tabelas.items():
        dataframe.to_sql(
            nome_tabela,
            conexao,
            if_exists="replace",
            index=False
        )

        print(
            f"Tabela {nome_tabela}: "
            f"{len(dataframe)} registros gravados."
        )

    # Fora do FOR: todas as tabelas já foram gravadas
    conexao.commit()

    # 6. Executar nossa primeira consulta SQL
    consulta = """
        SELECT chamado_id, status, situacao_prazo
        FROM indicadores_operacionais
        WHERE situacao_prazo = 'prazo_expirado';
    """

    resultado = pd.read_sql_query(consulta, conexao)

    print("\nChamados com prazo expirado:")
    print(resultado.to_string(index=False))

finally:
    conexao.close()

print("\nBanco criado em:", caminho_banco)


