from pydantic import BaseModel, field_validator

from modules.gerador_atas.gen_engine.ata_utils import _to_list


# ---------------------------------------------------------------------------
# Input schemas (request bodies)
# ---------------------------------------------------------------------------

class AtaInputManual(BaseModel):
    """Fields the caller must supply about the meeting."""
    numero_ata:      str
    orgao:           str
    sala:            str
    hora_inicio_raw: str
    hora_fim_raw:    str
    participantes:   str
    ausentes:        str = ""
    condutor:        str
    secretario:      str
    info_adicional:  str = ""
    # Optional pre-existing transcription text.
    # If omitted the caller must upload an audio file in the route.
    transcricao:     str = ""


# ---------------------------------------------------------------------------
# Output / read schemas
# ---------------------------------------------------------------------------

class AtaData(BaseModel):
    """Full structured ATA, as returned by the LLM pipeline."""
    numero_ata:          str
    orgao:               str
    sala:                str
    dia:                 str
    mes:                 str
    n_ano:               str
    hora_inicio:         str
    minutos_inicio:      str
    hora_fim:            str
    minutos_fim:         str
    participantes:       list[str]
    ausentes:            list[str]
    condutor:            str
    secretario:          str
    tema:                str
    resumo:              str
    assuntos_discutidos: list[str]
    deliberacoes:        list[str]

    @field_validator("participantes", "ausentes", "assuntos_discutidos", "deliberacoes", mode="before")
    @classmethod
    def parse_lists(cls, v):
        return _to_list(v)

    class Config:
        from_attributes: bool = True


class TranscricaoResponse(BaseModel):
    """Response from the audio transcription endpoint."""
    transcricao: str
    elapsed_seconds: float
