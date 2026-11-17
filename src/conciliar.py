from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar as duas fontes

chamados = pd.read_csv(
    BASE_DIR / "data" / "raw" / "chamados.csv"
)

relatos = pd.read_json(
    BASE_DIR / "data" / "raw" / "relatos.json",
    dtype=False
)

# Verificar o padrão do identificador
id_valido = chamados["chamado_id"].astype("string").str.fullmatch(
    r"(RF|TI|TK|CHG)-\d{6}"
).fillna(False)

# Verificar se o ID aparece mais de uma vez
id_unico = ~chamados["chamado_id"].duplicated(keep=False)

# Selecionar chamados com ID válido e único
chamados_aptos = chamados.loc[id_valido & id_unico].copy()

print("\nChamados origionais:", len(chamados))
print("Chamados aptos à associação:", len(chamados_aptos))
print(chamados_aptos["chamado_id"])

# Conciliar relatos com chamados aptos
conciliados = relatos.merge(
    chamados_aptos[
        ["chamado_id", "status", "data_abertura", "prazo_sla"]
    ],
    on="chamado_id",
    how="left",
    indicator=True,
    validate="many_to_one"
)

print("\nResultado da conciliação:")
print(
    conciliados[
        ["relato_id", "chamado_id", "status", "_merge"]
    ].to_string(index=False)
)

print("\nResumo:")
print(conciliados["_merge"].value_counts())

# Classificaçao inicial da conciliação

conciliados["situacao_associacao"] = "chamado_nao_encontrado"

# Relatos que encontraram um chamado apto
conciliados.loc[
    conciliados["_merge"] == "both",
    "situacao_associacao"
] = "vinculado_por_id"

# Identificadores duplicados na origem

ids_duplicados = chamados.loc[
    ~id_unico, "chamado_id"
].dropna()

conciliados.loc[
    conciliados["chamado_id"].isin(ids_duplicados),
    "situacao_associacao"
] = "id_duplicado_na_origem"

# Relatos sem identificação do chamado
ids_ausentes = (
    conciliados["chamado_id"].isna()
    | conciliados["chamado_id"].astype("string").str.strip().eq("").fillna(False)
)

conciliados.loc[
    ids_ausentes,
    "situacao_associacao"
] = "chamado_id_ausente"

print("\nClassificação da conciliação:")
print(
    conciliados[
        ["relato_id", "chamado_id", "situacao_associacao"]
    ].to_string(index=False)
)

# DQ-005: Relato anterior à abertura do chamado

# Converter as datas das duas fontes

for coluna in ["data_abertura", "data_atualizacao"]:
    conciliados[coluna] = pd.to_datetime(
        conciliados[coluna],
        errors="coerce",
        utc=True
    )

# Comparar datas apenas de relatos vinculados

dq_005 = (
    (conciliados["situacao_associacao"] == "vinculado_por_id")
    & (conciliados["data_atualizacao"] < conciliados["data_abertura"])
)

# Registrar resultado no DataFrame

conciliados["dq_005_relato_antes_abertura"] = dq_005

print("\nDQ-005 - Relatos anteriores à abertura:")
print(
    conciliados.loc[
        dq_005,
        ["relato_id", "chamado_id", "data_atualizacao","data_abertura"]
    ].to_string(index=False)
)

print("Total de inconsistências DQ-005", dq_005.sum())

# Gerar relatório inicial de conciliação
caminho_saida = BASE_DIR / "data" / "processed" / "conciliacao.csv"

caminho_saida.parent.mkdir(parents=True, exist_ok=True)


# Consolidar Data Quality dos relatos

conciliados["dqr_texto_vazio"] = (
    conciliados["texto"].isna()
    | conciliados["texto"].str.strip().eq("")
)

conciliados["dqr_data_ausente"] = (
    conciliados["data_atualizacao"].isna()
)

conciliados["dqr_relato_id_duplicado"] = (
    conciliados["relato_id"].duplicated(keep=False)
)

# Exportar todas as validações
colunas_relatorio = [
    "relato_id",
    "chamado_id",
    "situacao_associacao",
    "dqr_texto_vazio",
    "dqr_data_ausente",
    "dqr_relato_id_duplicado",
    "dq_005_relato_antes_abertura"
]

caminho_saida = BASE_DIR / "data" / "processed" / "conciliacao.csv"

conciliados[colunas_relatorio].to_csv(
    caminho_saida,
    index=False,
    encoding="utf-8-sig"
)

print("\nRelatório atualizado:", caminho_saida)
print("Colunas exportadas:", colunas_relatorio)