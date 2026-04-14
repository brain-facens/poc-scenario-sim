import enum
import uuid
from sqlalchemy import Column, Enum, ForeignKey, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class AtaStatus(enum.Enum):
    COMPLETE = "complete"
    DOING = "doing"
    INTERRUPTED = "interrupted"
    STALE = "stale"

class TranscricaoModel(Base):
    __tablename__ = "transcricoes"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transcricao = Column(Text, nullable=False)
    elapsed_seconds = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to the ATA
    ata = relationship("AtaModel", back_populates="transcricao", uselist=False)


class AtaModel(Base):
    __tablename__ = "atas"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    numero_ata = Column(String, index=True)
    orgao = Column(String)
    sala = Column(String)
    dia = Column(String)
    mes = Column(String)
    n_ano = Column(String)
    hora_inicio = Column(String)
    minutos_inicio = Column(String)
    hora_fim = Column(String)
    minutos_fim = Column(String)
    participantes = Column(Text)
    ausentes = Column(Text)
    condutor = Column(String)
    secretario = Column(String)
    tema = Column(String)
    resumo = Column(Text)
    assuntos_discutidos = Column(Text)
    deliberacoes = Column(Text)
    info_adicional = Column(Text, nullable=True)

    transcricao_id = Column(String(36), ForeignKey("transcricoes.id"), unique=True)
    
    status = Column(Enum(AtaStatus), default=AtaStatus.DOING, nullable=False)
    file_path = Column(String(255), nullable=True)
    error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    transcricao = relationship("TranscricaoModel", back_populates="ata")
