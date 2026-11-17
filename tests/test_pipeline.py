
from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED = BASE_DIR / "data" / "processed"


def test_relatorio_conciliacao():
    conciliacao = pd.read_csv(PROCESSED / "conciliacao.csv")

    colunas_obrigatorias = {
        "relato_id",
        "chamado_id",
        "situacao_associacao",
        "dqr_texto_vazio",
        "dqr_data_ausente",
        "dq_005_relato_antes_abertura",
    }

    assert colunas_obrigatorias.issubset(conciliacao.columns)
    assert len(conciliacao) == 8


def test_inconsistencia_temporal():
    conciliacao = pd.read_csv(PROCESSED / "conciliacao.csv")

    inconsistentes = conciliacao.loc[
        conciliacao["dq_005_relato_antes_abertura"],
        "relato_id"
    ]

    assert set(inconsistentes) == {"REL-006", "REL-007"}


def test_tabelas_sqlite():
    banco = PROCESSED / "opsmail.db"

    esperado = {
        "raw_chamados": 5,
        "raw_relatos": 8,
        "conciliacao": 8,
        "indicadores_operacionais": 5,
        "analises_ia": 2,
    }

    with sqlite3.connect(banco) as conexao:
        for tabela, quantidade_esperada in esperado.items():
            quantidade = conexao.execute(
                f"SELECT COUNT(*) FROM {tabela}"
            ).fetchone()[0]

            assert quantidade == quantidade_esperada
