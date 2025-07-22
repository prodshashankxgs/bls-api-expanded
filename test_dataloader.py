from data.load_data import DataLoader

tickers = [
    "CPSCJEWE Index",
    "CPIQWAN Index", 
    "CPSCWG Index",
    "CPSCMB Index",
    "CPSCINTD Index",
    "CPIQSMFN Index"
]    

dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")

print("DataFrame shape:", df.shape)
print("\nDataFrame columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\nDataFrame info:")
print(df.info())