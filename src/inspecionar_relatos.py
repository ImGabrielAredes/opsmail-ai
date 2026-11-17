from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
caminho_json = BASE_DIR / "data" / "raw" / "relatos.json"

print("Procurando arquivo em:", caminho_json)

if not caminho_json.exists():
    raise FileNotFoundError(
        f"Arquivo de relatos não encontrado: {caminho_json}"
    )


df_relatos = pd.read_json(caminho_json, dtype=False)
print(df_relatos.head())
print("Dimensões:", df_relatos.shape)

df_relatos["data_atualizacao"] = pd.to_datetime(
    df_relatos["data_atualizacao"],
    errors="coerce",
    utc=True
)

# DQR-001: IDs de relatos duplicados
ids_duplicados = df_relatos["relato_id"].duplicated(keep=False)

# DQR-001.1: Relatos sem identidicação

relatos_sem_id = (
    df_relatos["relato_id"].isna() |
    df_relatos["relato_id"].str.strip().eq("")
)

# DQR-002: chamados sem identificação
chamados_sem_id = (
    df_relatos["chamado_id"].isna()
    | df_relatos["chamado_id"].str.strip().eq("")

)

# DQR-003: relatos sem conteúdo
textos_vazios = (
    df_relatos["texto"].isna() |
    df_relatos["texto"].str.strip().eq("")
)

# DQR-004: data da última atualização divergente

datas_invalidas = df_relatos["data_atualizacao"].isna()

print("\nResumo do Data Quality dos relatos:")
print("IDs duplicados:", ids_duplicados.sum())
print("Relatos sem ID:", relatos_sem_id.sum())
print("Chamados sem ID:", chamados_sem_id.sum())
print("Relatos sem conteúdo:", textos_vazios.sum())
print("Datas inválidas:", datas_invalidas.sum())