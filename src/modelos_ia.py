
from typing import Literal
from pydantic import BaseModel, Field


class AnaliseRelato(BaseModel):
    resumo: str = Field(min_length=1)

    situacao_reportada: Literal[
        "solucionado",
        "nao_solucionado",
        "indeterminado"
    ]

    pendencia: str | None = None
    proxima_acao: str | None = None
    impacto_mencionado: str | None = None


# Teste temporário fora da classe
if __name__ == "__main__":
    analise = AnaliseRelato(
        resumo="Servidor restabelecido após intervenção.",
        situacao_reportada="solucionado",
        pendencia=None,
        proxima_acao=None,
        impacto_mencionado="Serviço anteriormente indisponível"
    )

    print(analise.model_dump_json(indent=2))
