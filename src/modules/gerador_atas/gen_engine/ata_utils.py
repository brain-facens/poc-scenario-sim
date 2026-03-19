import json

MESES = {
    1: "janeiro", 2: "fevereiro", 3: "março",    4: "abril",
    5: "maio",    6: "junho",     7: "julho",     8: "agosto",
    9: "setembro",10: "outubro",  11: "novembro", 12: "dezembro",
}

_PREPOSICOES = {"de", "da", "do", "das", "dos", "e"}


def _ano_por_extenso(ano: int) -> str:
    dezenas_map = {
        0: "zero",    1: "dez",      2: "vinte",    3: "trinta",   4: "quarenta",
        5: "cinquenta", 6: "sessenta", 7: "setenta", 8: "oitenta", 9: "noventa",
    }
    unidades_map = {
        0: "",      1: "um",    2: "dois",  3: "três",  4: "quatro",
        5: "cinco", 6: "seis",  7: "sete",  8: "oito",  9: "nove",
    }
    dezena  = (ano % 100) // 10
    unidade = ano % 10
    if unidade == 0:
        return dezenas_map[dezena]
    return f"{dezenas_map[dezena]} e {unidades_map[unidade]}"


def _parse_hora(horario: str) -> tuple:
    horario = horario.strip().replace("h", ":").replace("H", ":")
    if ":" in horario:
        partes  = horario.split(":")
        hora    = partes[0].zfill(2)
        minutos = partes[1].zfill(2) if len(partes) > 1 and partes[1] else "00"
    else:
        hora    = horario.zfill(2)
        minutos = "00"
    return hora, minutos


def _to_list(v):
    """Aceita list ou string JSON. Nunca divide por vírgula (frases contêm vírgulas)."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("["):
            try:
                parsed = json.loads(v)
                return [item.strip() if isinstance(item, str) else str(item) for item in parsed]
            except Exception:
                pass
        return [v] if v else []
    return v


def _capitalizar_nome(nome: str) -> str:
    partes = nome.strip().split()
    return " ".join(
        p.lower() if p.lower() in _PREPOSICOES else p.capitalize()
        for p in partes
    )


def normalizar_participante(entrada: str) -> str:
    """
    Aceita 'nome completo' ou 'nome completo - cargo'
    e retorna no formato padronizado 'Nome Completo - Cargo'.
    """
    if " - " in entrada:
        nome, cargo = entrada.split(" - ", 1)
        return f"{_capitalizar_nome(nome)} - {cargo.strip()}"
    return _capitalizar_nome(entrada)


def normalizar_lista_participantes(raw: str) -> list[str]:
    """
    Recebe a string do formulário (separada por vírgula ou quebra de linha)
    e retorna lista normalizada.
    """
    separador = "\n" if "\n" in raw else ","
    itens = [i.strip() for i in raw.split(separador) if i.strip()]
    return [normalizar_participante(i) for i in itens]
