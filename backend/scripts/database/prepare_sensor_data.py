import pandas as pd

RAW_PATH = "data/sensor/raw/sensor_data_1_year.csv"
OUTPUT_PATH = "data/sensor/processed/sensor_data_clean.csv"

# Load raw CSV
df = pd.read_csv(RAW_PATH)

# Rename ThingSpeak fields to meaningful names
df = df.rename(columns={
    "created_at": "timestamp",
    "field1": "temperature",
    "field2": "humidity",
    "field3": "pressure",
    "field4": "dew_point",
})

# Keep only useful columns
df = df[[
    "timestamp",
    "entry_id",
    "temperature",
    "humidity",
    "pressure",
    "dew_point",
]]

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

# Convert numeric columns
numeric_columns = ["entry_id", "temperature", "humidity", "pressure", "dew_point"]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove rows without valid timestamp
df = df.dropna(subset=["timestamp"])

# Sort by timestamp
df = df.sort_values("timestamp")

# Add source column
df["source"] = "1_year_sensor_dataset"

# Save cleaned dataset
df.to_csv(OUTPUT_PATH, index=False)

print("Cleaned data saved to:", OUTPUT_PATH)
print("Final shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)