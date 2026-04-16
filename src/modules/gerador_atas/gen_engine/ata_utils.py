import json
"""
Utility functions for generating meeting minutes (atas) in the gerador_atas module.

This module provides helper functions for formatting dates, times, and participant names
in Portuguese for use in meeting minutes generation.
"""

MESES = {
    1: "janeiro", 2: "fevereiro", 3: "março",    4: "abril",
    5: "maio",    6: "junho",     7: "julho",     8: "agosto",
    9: "setembro",10: "outubro",  11: "novembro", 12: "dezembro",
}
"""Dictionary mapping month numbers to Portuguese month names."""

_PREPOSICOES = {"de", "da", "do", "das", "dos", "e"}
"""Set of Portuguese prepositions that should remain lowercase when capitalizing names."""


def _ano_por_extenso(ano: int) -> str:
    dezenas_map = {
        0: "",         1: "dez",      2: "vinte",    3: "trinta",   4: "quarenta",
        5: "cinquenta", 6: "sessenta", 7: "setenta", 8: "oitenta", 9: "noventa",
    }
    unidades_map = {
        0: "",      1: "um",    2: "dois",  3: "três",  4: "quatro",
        5: "cinco", 6: "seis",  7: "sete",  8: "oito",  9: "nove",
    }

    milhares = ano // 1000
    resto    = ano % 1000
    centenas = resto // 100
    dezena   = (resto % 100) // 10
    unidade  = resto % 10

    partes = []

    if milhares:
        partes.append("dois mil" if milhares == 2 else f"{unidades_map[milhares]} mil")

    if centenas:
        centenas_map = {
            1: "cento", 2: "duzentos", 3: "trezentos", 4: "quatrocentos",
            5: "quinhentos", 6: "seiscentos", 7: "setecentos",
            8: "oitocentos", 9: "novecentos",
        }
        partes.append(centenas_map[centenas])

    if dezena and unidade:
        partes.append(f"{dezenas_map[dezena]} e {unidades_map[unidade]}")
    elif dezena:
        partes.append(dezenas_map[dezena])
    elif unidade:
        partes.append(unidades_map[unidade])

    return " e ".join(partes)


def _parse_hora(horario: str) -> tuple:
    """
    Parse a time string and return hour and minute as a tuple.
    
    This function handles various time formats by converting 'h' or 'H' to ':' and
    ensuring proper zero-padding for hours and minutes.
    
    Args:
        horario (str): Time string to parse (e.g., "9h30", "09:30", "9")
        
    Returns:
        tuple: A tuple containing (hour, minute) as strings with zero-padding
        
    Example:
        >>> _parse_hora("9h30")
        ('09', '30')
        >>> _parse_hora("14")
        ('14', '00')
    """
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
    """
    Convert a value to a list, handling both direct lists and JSON string representations.
    
    This function accepts either a list or a JSON string representation of a list,
    and returns a properly formatted list. It never splits by comma since phrases
    may contain commas.
    
    Args:
        v: The value to convert to a list
        
    Returns:
        list: A list representation of the input value
        
    Example:
        >>> _to_list('["item1", "item2"]')
        ['item1', 'item2']
        >>> _to_list(['item1', 'item2'])
        ['item1', 'item2']
        >>> _to_list('item1')
        ['item1']
    """
    if v is None:
        return []
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
    """
    Capitalize a name, keeping Portuguese prepositions lowercase.
    
    This function capitalizes the first letter of each word in a name, except for
    common Portuguese prepositions which remain lowercase.
    
    Args:
        nome (str): The name to capitalize
        
    Returns:
        str: The capitalized name with prepositions in lowercase
        
    Example:
        >>> _capitalizar_nome("joão da silva")
        'João da Silva'
        >>> _capitalizar_nome("maria dos santos")
        'Maria dos Santos'
    """
    partes = nome.strip().split()
    return " ".join(
        p.lower() if p.lower() in _PREPOSICOES else p.capitalize()
        for p in partes
    )


def normalizar_participante(entrada: str) -> str:
    """
    Normalize a participant string (name and optional role) to standard format.
    
    This function accepts either a full name or a name with role (separated by " - ")
    and returns it in the standardized format "Nome Completo - Cargo".
    
    Args:
        entrada (str): The participant string to normalize
        
    Returns:
        str: The normalized participant string
        
    Example:
        >>> normalizar_participante("joão da silva")
        'João da Silva'
        >>> normalizar_participante("maria dos santos - coordenadora")
        'Maria dos Santos - Coordenadora'
    """
    if " - " in entrada:
        nome, cargo = entrada.split(" - ", 1)
        return f"{_capitalizar_nome(nome)} - {cargo.strip()}"
    return _capitalizar_nome(entrada)


def normalizar_lista_participantes(raw: str) -> list[str]:
    """
    Normalize a raw string of participants into a list of standardized names.
    
    This function accepts a string with participants separated by commas or newlines
    and returns a list of normalized participant names.
    
    Args:
        raw (str): Raw string containing participant names separated by commas or newlines
        
    Returns:
        list[str]: List of normalized participant names
        
    Example:
        >>> normalizar_lista_participantes("joão da silva, maria dos santos")
        ['João da Silva', 'Maria dos Santos']
        >>> normalizar_lista_participantes("joão da silva\\nmaria dos santos")
        ['João da Silva', 'Maria dos Santos']
    """
    import re
    if "\n" in raw:
        itens = [i.strip() for i in raw.split("\n") if i.strip()]
    else:
        itens = [i.strip() for i in re.split(r',|\s+e\s+', raw) if i.strip()]
        
    return [normalizar_participante(i) for i in itens]
