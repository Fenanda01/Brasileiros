"""Regras de associação da rede, sem dependência de interface."""
import math
import unicodedata
from urllib.parse import urlencode
import pandas as pd


def normalizar(valor):
    if pd.isna(valor):
        return ''
    texto = unicodedata.normalize('NFKD', str(valor))
    return ' '.join(''.join(c for c in texto if not unicodedata.combining(c)).casefold().split())


def informar(valor):
    return 'Não informado' if normalizar(valor) in {'', 'ni', 'nan', 'none'} else str(valor)


def filtrar_rede(hospitais, operadora, plano):
    # Igualdade exata após normalização; não infere equivalência entre planos.
    if informar(operadora) == 'Não informado' or informar(plano) == 'Não informado':
        return hospitais.iloc[:0].copy()
    return hospitais[
        hospitais['operadora'].map(normalizar).eq(normalizar(operadora))
        & hospitais['plano'].map(normalizar).eq(normalizar(plano))
    ].copy()


def distancia(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    a = min(1, max(0, a))
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def rota(hospital):
    if pd.notna(hospital['latitude']) and pd.notna(hospital['longitude']):
        destino = f"{hospital['latitude']},{hospital['longitude']}"
    else:
        destino = informar(hospital.get('endereco'))
        if destino == 'Não informado':
            destino = str(hospital['hospital']) + ' Goiânia'
    return 'https://www.google.com/maps/dir/?' + urlencode({'api': 1, 'destination': destino})
