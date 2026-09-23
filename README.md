# Analiza podataka društvenih mreža i predikcija popularnosti video sadržaja korištenjem skladišta podataka

Završni rad na Fakultetu informatike, Sveučilište Jurja Dobrile u Puli (kolegij: Skladišta i rudarenje podataka, mentor: izv. prof. dr. sc. Goran Oreški).

Projekt pokriva cjelokupan proces izgradnje skladišta podataka i predikcijskog modela nad javno dostupnim skupom podataka videozapisa s TikToka i YouTube Shortsa — od sirovih podataka, preko relacijskog i dimenzijskog modela, ETL procesa i vizualizacije, do modela strojnog učenja za predviđanje popularnosti sadržaja.

## Struktura projekta

- **1_EDA** – eksplorativna analiza izvornog skupa podataka
- **2_relacijski_model** – čišćenje podataka i izrada relacijskog modela (MySQL)
- **3_dimenzijski_model** – transformacija u zvjezdastu shemu (dimenzijski model)
- **4_etl** – ETL proces izrađen u Apache Sparku (ekstrakcija, transformacija, učitavanje)
- **5_vizualizacija** – interaktivni Power BI dashboardi
- **6_predikcijski_model** – model strojnog učenja (Random Forest) za predikciju visokog angažmana videozapisa

## Korištene tehnologije

Python, MySQL, Apache Spark (PySpark), Power BI, scikit-learn, pandas
