import pandas as pd

df = pd.read_csv("openpowerlifting.csv")

print(df["Name"].nunique())

print(df.shape)

for i in df.columns:
    print(df[i].isna().sum())

print(df.head())

df["Name"] = df["Name"].str.lower()
print(df["Name"])
df["Name"] = df["Name"].str.capitalize()
print(df["Name"])
