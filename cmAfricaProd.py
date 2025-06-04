#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np


# In[2]:


# Source:  5th list of EU's CRM. Annex II of the Regulation proposal COM(2023). 
# https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52023PC0160

CM = [
    "Antimony",
    "Arsenic",
    "Bauxite",
    "Baryte",
    "Beryllium (conc.)",
    "Bismuth",
    "Boron Minerals",
    "Cobalt",
    "Coking Coal",
    "Copper",
    "Feldspar",
    "Fluorspar",
    "Gallium",
    "Germanium",
    "Hafnium",
    "Helium",
    "Rare Earths (REO)",
    "Lithium (Li2O)",
    "Magnesium",
    "Manganese",
    "Graphite",
    "Nickel",
    "Niobium (Nb2O5)",
    "Phosphate Rock (P2O5)",
    "Phosphorus",
    "Platinum",
    "Scandium",
    "Silicon",
    "Strontium",
    "Tantalum (Ta2O5)",
    "Titanium (TiO2)",
    "Tungsten (W)",
    "Vanadium (V)"
]


# In[3]:


## List of African countries from https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_Africa


# In[4]:


url = "https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_Africa"
html = requests.get(url).text
soup = BeautifulSoup(html)


# In[5]:


table = soup.find('table')


# In[6]:


countries = []
rows = table.find_all('tr')
for row in rows:
    cells = row.find_all('td')
    for cell in cells:
        link = cells[2].find('a')
        countries.append(link.text)


# In[7]:


countries = list(dict.fromkeys(countries))


# In[8]:


### Here, we adjust country names as we go


# In[9]:


countries[24] = "Cote d'Ivoire"


# In[10]:


countries[12] = "Congo, D.R."


# In[11]:


## World Mining Data 2025 https://www.world-mining-data.info/?World_Mining_Data___Data_Section


# In[12]:


# We create a dictionary containing dataframes per mineral where at least one African country of our 'countries' list is mentioned
dfs_CM = {}

for mat in CM:
    try:
        df = pd.read_excel(open('6.4. Production_of_Mineral_Raw_Materials_of_individual_Countries_by_Minerals.xlsx', 'rb'), sheet_name=f"{mat}")

        # Use the first row as column headers, and remove first row since it's now the header
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        # Store the DataFrame in the dictionary
        dfs_CM[mat] = df

    except Exception as e:
        print(f"No sheet found for {mat}: {e}")   # These are the critical minerals that WMD has not considered


# In[13]:


## Note : Executed some manual name correction to make the CM list on cell 2 match to names of sheets, after exceptions were raised


# In[14]:


dfs_OK = {}
for material_name, df in dfs_CM.items():
    if any(df['Country'].isin(countries)):
        dfs_OK[material_name] = df


# In[15]:


dfs_OK.keys()


# ## Mapping countries where different CM are produced

# In[16]:


### Building a df of product-country pairs based on matching conditions.

def build_product_country_dataframe(dfs_OK, countries):

    all_products = []
    all_countries = []

    # Iterate through each product in the dictionary
    for product in dfs_OK.keys():
        matches = []
        # Find countries that match the condition for this product
        for country in countries:
            if country in dfs_OK[product]['Country'].values:
                matches.append(country)

        # Add product-country pairs to our lists
        if matches:  # Only if there are matches
            all_products.extend([product] * len(matches)) #We make sure that if one product is named fourth times, there are four rows, idem with countries
            all_countries.extend(matches)

    # Create the final DataFrame
    final_df = pd.DataFrame({'Product': all_products, 'Country': all_countries})
    return final_df

final_df = build_product_country_dataframe(dfs_OK, countries)


# In[17]:


final_df


# In[18]:


final_df.to_csv("productCountry.csv", index=False)


# ## Calculating % change 2019-2023

# In[19]:


## Building function to 1/only consider African countries and 2/ new column with % change from 2019 to 2013
def only_africa(dfs_OK, start_idx, end_idx, countries, initial_df_share=None):
    if initial_df_share is None:
        initial_df_share = pd.DataFrame()

    keys_list = list(dfs_OK.keys())

    for idx in range(start_idx, end_idx + 1):
        element = keys_list[idx]
        df = dfs_OK[element]
        dflatest = df[df['Country'].isin(countries)].copy()
        dflatest['Mineral'] = element
        dflatest['percent_change_5y'] = (dflatest[2023] - dflatest[2019]) / dflatest[2019] * 100
        initial_df_share = pd.concat([initial_df_share, dflatest], ignore_index=True)

    return initial_df_share


# In[20]:


df_africa = only_africa(dfs_OK, 0, 20, countries)


# In[21]:


### Which minerals are causing the increases and decreases?
## We look into top and bottom countries to include takeaways in annos


# In[22]:


df_africa.head()


# In[23]:


df_africa[df_africa["Country"] == "Mozambique"]


# In[24]:


df_africa[df_africa["Country"] == "Malawi"]


# In[25]:


df_africa[df_africa["unit"] == "kg"] 
#!! Platinum uses a different unit, but here we include different units because we are calculating change


# ## Average change in production per country
# Here, we calculate the average change across different minerals per country. 
# keep in mind that minerals with no production in 2019 in positive production in 2023 are not represented in the data

# In[26]:


df_average = df_africa.groupby('Country')['percent_change_5y'].mean().reset_index()


# In[27]:


df_average.to_csv("averageChangeProd_20250604.csv")


# ## Total change in production per country

# In[28]:


df_mapmap = df_africa.groupby('Country')[[2019, 2023]].sum().reset_index()
df_mapmap['percent_change_5y'] = (df_mapmap[2023] - df_mapmap[2019]) / df_mapmap[2019] * 100


# In[29]:


# We keep a column with the number of minerals
df_map2 = final_df.groupby("Country")["Product"].count()


# In[30]:


df_map = pd.merge(df_mapmap, df_map2, how='outer', on="Country")


# In[31]:


df_map["percent_change_5y"] = df_map["percent_change_5y"].round(2)


# In[32]:


df_map.to_csv("TotalChangeProd_20250604.csv")


# ## Total production 2023

# In[33]:


# We exclude platinum; we cannot sum different metrics
df_prod = df_africa[~df_africa["unit"].isin(["kg"])]


# In[34]:


df_prod = df_prod.groupby("Country")[2023].sum()


# In[35]:


df_prod = df_prod.reset_index()  #copy-pasted on googlesheets


# ## Change in production per mineral, per country

# In[36]:


pivot_africa = df_africa.pivot_table(
    index='Country',
    columns='Mineral',
    values='percent_change_5y'
)


# In[37]:


pivot_africa = pivot_africa.round(2)


# In[38]:


pivot_africa


# In[39]:


pivot_africa.to_csv("pivot_w_percentage.csv")


# In[ ]:




