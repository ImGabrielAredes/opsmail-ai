from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

caminho_csv = BASE_DIR / "data" / "raw" / "chamados.csv"

chamados = pd.read_csv(caminho_csv)

colunas_datas = [
    "data_abertura",
    "ultima_atualizacao",
    "prazo_sla"
]

for coluna in colunas_datas:
    chamados[coluna] = pd.to_datetime(
        chamados[coluna],
        errors="coerce",
        utc=True
    )

# Data fixa para tornar os testes reproduzíveis
DATA_REFERENCIA = pd.Timestamp(
    "2026-11-15T21:45:00-03:00"
).tz_convert("UTC")

print("Data de referência:", DATA_REFERENCIA)
print("Total de chamados:", len(chamados))

# Verificar identificadores
id_valido = chamados["chamado_id"].astype("string").str.fullmatch(
    r"(RF|TI|TK|CHG)-\d{6}"
).fillna(False)

id_unico = ~chamados["chamado_id"].duplicated(keep=False)

# Verificar integridade temporal
datas_presentes = chamados[colunas_datas].notna().all(axis=1)

ordem_temporal_valida = (
    chamados["ultima_atualizacao"] >= chamados["data_abertura"]
)

datas_nao_futuras = (
    (chamados["data_abertura"] <= DATA_REFERENCIA)
    & (chamados["ultima_atualizacao"] <= DATA_REFERENCIA)
)

# Selecionar registros aptos aos cálculos
dados_confiaveis = (
    id_valido
    & id_unico
    & datas_presentes
    & ordem_temporal_valida
    &datas_nao_futuras
)

# Quais chamados continuam em andamento?
status_ativos = chamados["status"].isin(
    ["aberto", "em_andamento", "pendente_cliente"]
)

# Converter pausa de SLA para booleano controlado
pausa = (
    chamados["sla_pausado"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map({"true": True, "false": False})
)

avaliaveis = dados_confiaveis & status_ativos

# Inicialmente, não avaliamos o prazo
chamados["situacao_prazo"] = "nao_avaliavel"

# SLA explicitamente pausado
chamados.loc[
    avaliaveis & pausa.eq(True).fillna(False),
    "situacao_prazo"
] = "pausado"

# Chamados ativos com SLA não pausado
sem_pausa = avaliaveis & pausa.eq(False).fillna(False)

chamados.loc[
    sem_pausa & (chamados["prazo_sla"] < DATA_REFERENCIA),
    "situacao_prazo"
] = "prazo_expirado"

chamados.loc[
    sem_pausa & (chamados["prazo_sla"] >= DATA_REFERENCIA),
    "situacao_prazo"
] = "dentro_do_prazo"

print("\nResultado da análise de prazos:")
print(
    chamados[
        ["chamado_id", "status", "situacao_prazo"]
    ].to_string(index=False)
)

# OP-002: Chamados sem atualização há mais de 5 dias

limite_5_dias = DATA_REFERENCIA - pd.Timedelta(days=5)

chamados["sem_atualizacao_5d"] = "nao_avaliavel"

chamados.loc[
    avaliaveis,
    "sem_atualizacao_5d"
] = "nao"

chamados.loc[
    avaliaveis & (chamados["ultima_atualizacao"] < limite_5_dias),
    "sem_atualizacao_5d"
] = "sim"

# OP-003: Chamados abertos há mais de 30 dias

limite_30_dias = DATA_REFERENCIA - pd.Timedelta(days=30)

chamados["aberto_30d"] = "nao_avaliavel"

chamados.loc[
    avaliaveis,
    "aberto_30d"
] = "nao"

chamados.loc[
    avaliaveis & (chamados["data_abertura"] < limite_30_dias),
    "aberto_30d"
] = "sim"

print("\nIndicadores operacionais:")

print(
    chamados[
        [
            "chamado_id",
            "situacao_prazo",
            "sem_atualizacao_5d",
            "aberto_30d",
        ]
    ].to_string(index=False)
)

# Exportar indicadores incluindo a data de referência
caminho_saida = (
    BASE_DIR / "data" / "processed" / "indicadores_operacionais.csv"
)

caminho_saida.parent.mkdir(parents=True, exist_ok=True)

# 1. Cria a coluna com o timestamp ISO
chamados["data_referencia"] = DATA_REFERENCIA.isoformat()

# 2. Adicione "data_referencia" na lista de colunas exportadas!
chamados[
    [
        "chamado_id",
        "status",
        "situacao_prazo",
        "sem_atualizacao_5d",
        "aberto_30d",
        "data_referencia",  # <--- Adicionado aqui
    ]
].to_csv(
    caminho_saida,
    index=False,
    encoding="utf-8-sig",
)

print("\nIndicadores exportados para:", caminho_saida)
print("Chamados com dados temporais confiáveis:", dados_confiaveis.sum())
print("Chamados ativos e avaliáveis:", (dados_confiaveis & status_ativos).sum())