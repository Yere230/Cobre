"""
Script de PRUEBA — no modifica ni reemplaza nada del robot principal
(actualizar_datos.py). Su único objetivo es ver si el mismo endpoint de
Yahoo Finance que ya usamos para precios también entrega historial de
dividendos para acciones chilenas, usando el parámetro events=div.

Si esto funciona bien, se integra al robot principal más adelante.
Si no trae nada útil, se descarta sin haber tocado lo que ya funciona.
"""

import json
from datetime import datetime, timezone

import requests

HEADERS_YAHOO = {"User-Agent": "Mozilla/5.0 (compatible; CobreBot/1.0; +personal use)"}

# Muestra chica de acciones conocidas como buenas pagadoras de dividendos,
# para no gastar tiempo probando las 55 si esto no resulta.
TICKERS_PRUEBA = ["COPEC.SN", "BSANTANDER.SN", "CHILE.SN", "CCU.SN", "ENELCHILE.SN"]


def probar_dividendos(ticker_yahoo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_yahoo}"
    params = {"interval": "1d", "range": "2y", "events": "div"}
    try:
        r = requests.get(url, headers=HEADERS_YAHOO, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        result = data["chart"]["result"][0]
        eventos = result.get("events", {})
        dividendos = eventos.get("dividends", {})

        if not dividendos:
            return {
                "ticker": ticker_yahoo,
                "encontrado": False,
                "detalle": "Yahoo respondió correctamente pero sin ninguna sección de dividendos",
            }

        lista = []
        for _, info in dividendos.items():
            fecha = datetime.fromtimestamp(info["date"], tz=timezone.utc).strftime("%Y-%m-%d")
            lista.append({"fecha": fecha, "monto": info["amount"]})
        lista.sort(key=lambda x: x["fecha"], reverse=True)

        return {"ticker": ticker_yahoo, "encontrado": True, "dividendos": lista}

    except Exception as e:
        return {"ticker": ticker_yahoo, "encontrado": False, "detalle": f"Error: {e}"}


def main():
    resultados = []
    for t in TICKERS_PRUEBA:
        print(f"\nProbando {t}...")
        r = probar_dividendos(t)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        resultados.append(r)

    with open("data/prueba_dividendos.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    exitosos = sum(1 for r in resultados if r["encontrado"])
    print(f"\n=== Resumen: {exitosos} de {len(TICKERS_PRUEBA)} tickers tuvieron datos de dividendos ===")


if __name__ == "__main__":
    main()
