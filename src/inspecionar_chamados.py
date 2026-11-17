
from pathlib import Path
import pandas as pd

# 1. Localizar a pasta principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Construir o caminho do CSV
caminho_csv = BASE_DIR / "data" / "raw" / "chamados.csv"

# 3. Verificar se o arquivo existe
print("Procurando arquivo em:", caminho_csv)
print("Arquivo encontrado?", caminho_csv.exists())

# 4. Ler o CSV com Pandas
df = pd.read_csv(caminho_csv)

# 4.1. Conversão de data_abertura de string para datetime.
df["data_abertura"] = pd.to_datetime(
    df["data_abertura"],
    errors="coerce",
    utc=True
)

#4.2 Conversão de ultima_atualizacao de string para datetime
df["ultima_atualizacao"] = pd.to_datetime(
    df["ultima_atualizacao"],
    errors="coerce",
    utc=True
)

#4.3. Conversão do prazo_sla de string para datetime
df["prazo_sla"] = pd.to_datetime(
    df["prazo_sla"],
    errors="coerce",
    utc=True
)


# 5. Exibir os primeiros registros
print(df.head())

# 6. Exibir a quantidade de linhas e colunas
print("Dimensões:", df.shape)

#7.DQ-001: identificar as atualizações que são anteriores a abertura do chamado

datas_inconsistentes = (
    df["ultima_atualizacao"] < df["data_abertura"]
)

chamados_invalidos = df[datas_inconsistentes]
print("Chamados com datas inconsistentes:")
print(chamados_invalidos)

#8. DQ-002: identificadores inválidos
ids_validos= df["chamado_id"].astype("string").str.fullmatch(
    r"(RF|TI|TK|CHG)-\d{6}"
).fillna(False)

ids_invalidos = ~ids_validos

#DQ-003: datas ausentes ou inválidas

colunas_datas = [
    "data_abertura",
    "ultima_atualizacao",
    "prazo_sla",
]

#DQ-004: identificadores duplicados
ids_duplicados = (
    df["chamado_id"].notna()
    & df["chamado_id"].duplicated(keep=False)
)

print("\nDQ-002 - IDs inválidos:")
print(df.loc[ids_invalidos, ["chamado_id"]])

print("\nDQ-003 - Datas inválidas:")
for coluna in colunas_datas:
    datas_invalidas = df[coluna].isna()

    print(f"\n{coluna}: {datas_invalidas.sum()} problemas")
    print(df.loc[datas_invalidas, ["chamado_id", coluna]])

print("\nDQ-004 - IDs duplicados:")
print(df.loc[ids_duplicados, ["chamado_id"]])


# 9. Consolidar as ocorrências de Data Quality
ocorrencias = []

def registrar_erros(mascara, regra, descricao):
    for indice in df.index[mascara]:
        ocorrencias.append({
            "linha_csv": indice + 2,
            "chamado_id": df.loc[indice, "chamado_id"],
            "regra": regra,
            "descricao": descricao
        })

# Registrar DQ-001
registrar_erros(
    datas_inconsistentes,
    "DQ-001",
    "Última atualização anterior à abertura"
)

# Registrar DQ-002
registrar_erros(
    ids_invalidos,
    "DQ-002",
    "Identificador inválido"
)

# Registrar DQ-003
for coluna in colunas_datas:
    registrar_erros(
        df[coluna].isna(),
        "DQ-003",
        f"Data inválida ou ausente: {coluna}"
    )

# Registrar DQ-004
registrar_erros(
    ids_duplicados,
    "DQ-004",
    "Identificador duplicado"
)

# 10. Gerar o relatório CSV
relatorio = pd.DataFrame(
    ocorrencias,
    columns=["linha_csv", "chamado_id", "regra", "descricao"]
)

caminho_saida = BASE_DIR / "data" / "processed" / "inconsistencias.csv"
caminho_saida.parent.mkdir(parents=True, exist_ok=True)

relatorio.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("\nRelatório de inconsistências:")
print(relatorio)
print("Arquivo gerado em:", caminho_saida)

print("Inconsistências temporais:", len(chamados_invalidos))
print("Total de ocorrências de Data Quality:", len(relatorio))

