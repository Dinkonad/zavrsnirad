import pandas as pd

pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

CSV_FILE_PATH = "youtube-tiktok-shorts.csv"
data = pd.read_csv(CSV_FILE_PATH)

print("\n prvih 5 redaka")
print(data.head())

print("\n dimenzije redaka i stupaca")
print(data.shape)

print("\n sažetak po stupcu: nedostajuće vrijednosti, broj unikatnih vrijednosti i tip podatka")
summary = pd.DataFrame({
    "Nedostajuće": data.isna().sum(),
    "Unikatne": data.nunique(),
    "Tip podatka": data.dtypes
})
print(summary)

print("\n broj dupliciranih redaka")
print(data.duplicated().sum())

print("\n distribucija po stupcima")

for column in data.columns:
    print(f"\n")
    print(data[column].value_counts())
    input("enter za podatke o stupcima")





