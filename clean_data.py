import pandas as pd
import re
import numpy as np

df = pd.read_csv('ebay_tech_deals.csv')

df.drop_duplicates()
def clean_currency(prices):
    def convert_value(x):
        if pd.isna(x):
            return x
        if isinstance(x, str):
            cleaned = re.sub(r'[^\d.-]', '', x.strip())
            if cleaned == '':
                return None
            return cleaned
        return x
    return prices.apply(convert_value)

df['price'] = clean_currency(df['price'])
df['original_price'] = clean_currency(df['original_price'])
df['original_price'] = df['original_price'].fillna(df['price'])
df['shipping'] = df['shipping'].fillna('').astype(str).str.strip()
shipping_missing = (df['shipping'].isin(["", "N/A"]) | 
                    df['shipping'] == '')
df.loc[shipping_missing, 'shipping'] = "Shipping info unavailable"

df['shipping'] = df['shipping'].astype(str).str.strip()
shipping_missing = (df['shipping'].isin(["", "N/A"]) | 
                    df['shipping'].isna())
df.loc[shipping_missing, 'shipping'] = "Shipping info unavailable"

df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['original_price'] = pd.to_numeric(df['original_price'], errors='coerce')

df['discount_percentage'] = np.where(
    (df['original_price'].notna()) & (df['original_price'] != 0),
    ((1 - df['price'] / df['original_price']) * 100).round(2),
    np.nan
)
df = df.dropna(subset=['title', 'price', 'original_price'])
df.to_csv("cleaned_ebay_deals.csv", index=False)
