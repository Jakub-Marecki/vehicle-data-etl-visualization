import ssl
import requests
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime

# kody TERYT 16 województw jako liczby (bez zer wiodących)
WOJEWODZTWA = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
API_URL = "https://api.cepik.gov.pl/pojazdy"

class SSLContextAdapter(HTTPAdapter):
    """Adapter HTTPS z niestandardowym SSLContext (SECPLEVEL=1)."""
    def __init__(self, ctx: ssl.SSLContext, **kwargs):
        self.ctx = ctx
        super().__init__(**kwargs)
    def init_poolmanager(self, pools, maxsize, block=False, **kw):
        self.poolmanager = PoolManager(
            num_pools=pools, maxsize=maxsize,
            block=block, ssl_context=self.ctx, **kw
        )
    def proxy_manager_for(self, proxy, **kw):
        kw['ssl_context'] = self.ctx
        return super().proxy_manager_for(proxy, **kw)

def fetch_monthly(woj: int, start: datetime, end: datetime) -> list:
    """Pobiera dane z CEPiK dla jednego województwa i jednego miesiąca."""
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    sess = requests.Session()
    sess.mount("https://", SSLContextAdapter(ctx))

    params = {
        "wojewodztwo": woj,
        "data-od": start.strftime("%Y%m%d"),
        "data-do": end.strftime("%Y%m%d")
    }
    r = sess.get(API_URL, params=params, timeout=20)
    r.raise_for_status()
    payload = r.json()
    # wyciągnij listę z JSON
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for v in payload.values():
            if isinstance(v, list):
                return v
    return []

def main():
    OUT_DIR = r"C:\Users\ASUS ZENBOOK\Desktop\python"
    os.makedirs(OUT_DIR, exist_ok=True)

    all_records = []
    year = 2019
    # pętla po województwach
    for woj in WOJEWODZTWA:
        print(f"Pobieram województwo {woj}…")
        # pętla po miesiącach
        current = datetime(year, 1, 1)
        while current.year == year:
            # koniec miesiąca
            next_month = current + relativedelta(months=1) - relativedelta(days=1)
            try:
                recs = fetch_monthly(woj, current, next_month)
                # dodaj pole identyfikujące
                for r in recs:
                    r['kod_wojewodztwa'] = woj
                    r['data_od'] = current.strftime("%Y-%m-%d")
                    r['data_do'] = next_month.strftime("%Y-%m-%d")
                all_records.extend(recs)
                print(f"  {current.strftime('%Y-%m')}: {len(recs)} rekordów")
            except Exception as e:
                print(f"  błąd {current.strftime('%Y-%m')}: {e}")
            # przejdź do pierwszego dnia kolejnego miesiąca
            current = current + relativedelta(months=1)

    print(f"\nŁącznie pobrano {len(all_records)} rekordów, spłaszczam…")
    df = pd.json_normalize(all_records, sep='_')
    out_path = os.path.join(OUT_DIR, "dane_cepik_2019_all_woj.csv")
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"Zapisano CSV:\n  {out_path}")
    print(f"Finalny DataFrame: {df.shape[0]} wierszy × {df.shape[1]} kolumn")

if __name__ == "__main__":
    main()
