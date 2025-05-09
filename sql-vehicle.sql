WITH vehicle_model_table AS(
SELECT
attributes_data_pierwszej_rejestracji_w_kraju AS rok_rejestracji,
attributes_marka AS marka,
attributes_model AS model,
COUNT(*) AS ilosc_zarejestrowanych_modeli,
SUM(CASE WHEN attributes_pochodzenie_pojazdu LIKE '%NOWY%' THEN 1 ELSE 0 END) AS ilosc_nowych_modeli,
COUNT(*) - SUM(CASE WHEN attributes_pochodzenie_pojazdu LIKE '%NOWY%' THEN 1 ELSE 0 END) AS ilosc_używanych_modeli,
(SUM(CASE WHEN attributes_pochodzenie_pojazdu LIKE '%NOWY%' THEN 1 ELSE 0 END) * 100) / COUNT(*) AS procent_nowych_modeli

FROM POJAZDY.dane_pojazdy

GROUP BY
attributes_data_pierwszej_rejestracji_w_kraju,
attributes_marka,
attributes_model

)
SELECT
  vmt.rok_rejestracji,
  vmt.marka,
  vmt.model,
  vmt.ilosc_zarejestrowanych_modeli,
  vmt.ilosc_nowych_modeli,
  vmt.procent_nowych_modeli,
SUM(vmt.ilosc_zarejestrowanych_modeli) OVER (PARTITION BY vmt.marka,vmt.rok_rejestracji) AS ilosc_zarejestrowanych_marka,
SUM(vmt.ilosc_nowych_modeli) OVER (PARTITION BY vmt.marka,vmt.rok_rejestracji) AS ilosc_nowych_marka,
SUM(vmt.ilosc_nowych_modeli) OVER (PARTITION BY marka, rok_rejestracji) * 100 / SUM(vmt.ilosc_zarejestrowanych_modeli) OVER (PARTITION BY marka, rok_rejestracji) AS procent_nowych_marka


FROM vehicle_model_table AS vmt
GROUP BY vmt.rok_rejestracji,
  vmt.marka,
  vmt.model,
  vmt.ilosc_zarejestrowanych_modeli,
  vmt.ilosc_nowych_modeli,
  vmt.procent_nowych_modeli;