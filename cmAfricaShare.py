#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup


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


countries[24] = "Cote d'Ivoire"


# In[9]:


countries[12] = "Congo, D.R."


# In[10]:


## Source: https://www.world-mining-data.info/?World_Mining_Data___Data_Section


# In[11]:


dfs_CM = {}

for mat in CM:
    try:
        df = pd.read_excel(open('6.5. Share_of_World_Mineral_Production_2023_by_Countries.xlsx', 'rb'), sheet_name=f"{mat}")
                # Use the first row as column headers
        df.columns = df.iloc[0]

        # Remove the first row (since it's now the header)
        df = df.iloc[1:].reset_index(drop=True)

        # Store the DataFrame in the dictionary
        dfs_CM[mat] = df

    except Exception as e:
        print(f"No sheet found for {mat}: {e}")


# In[12]:


#We create a dictionary containing various dataframes.
#Each df contains data per mineral. Only dfs naming at least one African country as per the countries list are included
dfs_OK = {}  
for material_name, df in dfs_CM.items():
    if any(df['Country'].isin(countries)):
        dfs_OK[material_name] = df


# ## A-Calculating Africa's share per mineral
# Aesthetic graphs

# In[13]:


### First, we test what we want to put in our function


# In[14]:


element = list(dfs_OK.keys())[0]
matches = []
for country in countries:
    if country in dfs_OK[f"{element}"]['Country'].values:
        matches.append(country)


# In[15]:


# We create dfs per element consisting of the rows referring to our target countries only 
df0 = dfs_OK[f"{element}"][dfs_OK[f"{element}"]['Country'].isin(matches)]


# In[16]:


# We create a variable with the total share (a sum of share per country for each element/df)
result = df0['Share in %'].sum()


# In[17]:


#We create a df where the index is the name of the element and the value is the total share ('result' variable)
df0 = pd.DataFrame(
    result,
    index=[(f"{element}")],
    columns=['share'])


# In[18]:


# We repeat with the second element
element = list(dfs_OK.keys())[1]
matches = []
for country in countries:
    if country in dfs_OK[f"{element}"]['Country'].values:
        matches.append(country)

df1 = dfs_OK[f"{element}"][dfs_OK[f"{element}"]['Country'].isin(matches)]


# In[19]:


result = df1['Share in %'].sum()


# In[20]:


df1 = pd.DataFrame(
    result,
    index=[(f"{element}")],
    columns=['share'])


# In[21]:


#We concatenate
df_share = pd.concat([df0,df1])


# In[22]:


# Now that we know what we want to achieve, we create functions for efficienty

def calculate_country_share(dfs_OK, element, countries, df_share=None):
    # In each df, we only take the rows that refer to our target countries
    # the matches list is the list of African countries contained in the World Mining Data
    matches = []
    for country in countries:
        if country in dfs_OK[element]['Country'].values:
            matches.append(country)
    #We create dfs per element containing only the rows that refer to our target countries
    dflatest = dfs_OK[element][dfs_OK[element]['Country'].isin(matches)]

    #We create a variable that sums the shares of each individual country per critical mineral
    result = dflatest['Share in %'].sum()

    dflatest = pd.DataFrame(
        result,
        index=[element],
        columns=['share'])

    return pd.concat([df_share, dflatest])


# In[23]:


# This function allow for the execution of the previous function on a loop that goes from a key in the our dictionary of dfs
# to another key. Eg, it can loop through the first of the dfs in the dfs_OK dict to the last one, executing the previous function
def calculate_multiple_country_shares(dfs_OK, start_idx, end_idx, countries, initial_df_share=None):

    keys_list = list(dfs_OK.keys())

    for idx in range(start_idx, end_idx + 1):
        element = keys_list[idx]
        initial_df_share = calculate_country_share(dfs_OK, element, countries, initial_df_share)

    return initial_df_share


# In[24]:


df_share = calculate_multiple_country_shares(dfs_OK, 2, 20, countries, df_share)


# In[25]:


df_share.sort_values(by='share', ascending=False)


# ## B-Top shares by country
# Scatterplots

# In[26]:


# We repeat the same logic, but including only rows (per df) that reach a threshold on the share column


# In[27]:


element = list(dfs_OK.keys())[0]
top_share = dfs_OK[f"{element}"][(dfs_OK[f"{element}"]['Country'].isin(countries)) & (df['Share in %'] > 10)].copy()
top_share['Mineral'] = element


# In[28]:


#We have not used this function in the end, as have included all countries no matter what their share is. 
# But we keep the function just in case
def high_share(dfs_OK, element, countries, df_share=None):

    dflatest = dfs_OK[element][dfs_OK[element]['Country'].isin(countries) & (df['Share in %'] > 10)]
    dflatest['Mineral'] = element

    return pd.concat([top_share, dflatest])


# In[29]:


def collect_high_shares(dfs_OK, start_idx, end_idx, countries, initial_df_share=None):
    if initial_df_share is None:
        initial_df_share = pd.DataFrame()

    keys_list = list(dfs_OK.keys())

    for idx in range(start_idx, end_idx + 1):
        element = keys_list[idx]
        df = dfs_OK[element]
        dflatest = df[df['Country'].isin(countries) & (df['Share in %'] > 0)].copy() #We ensure that all countries with a positive share are included
        dflatest['Mineral'] = element
        initial_df_share = pd.concat([initial_df_share, dflatest], ignore_index=True)

    return initial_df_share


# In[30]:


#top_share_total = collect_high_shares(dfs_OK, 0, 20, countries)
share_total = collect_high_shares(dfs_OK, 0, 20, countries)


# In[31]:


share_total


# In[32]:


top_share_total = share_total.sort_values('Share in %', ascending=False)
top_share_total = top_share_total.drop_duplicates(subset='Country', keep='first')


# In[33]:


top_share_total['Country'] = top_share_total['Country'].str.split(',').str[0].str.strip()


# In[34]:


top_countries = set(top_share_total["Country"].to_list()) # We will use this list to find indicators per country


# ## + World Bank indicators

# In[35]:


# We want to find wgi's indicators of our target countries and include them to our df
## Source: https://www.worldbank.org/en/publication/worldwide-governance-indicators


# In[36]:


wgi = pd.read_excel("wgidataset.xlsx")


# In[37]:


wgi = wgi[wgi['countryname'] != 'Congo, Rep.']


# In[38]:


wgi['countryname'] = wgi['countryname'].str.split(',').str[0].str.strip()


# ### 1/Political Stability

# In[39]:


pv = wgi[wgi['countryname'].isin(top_countries) & (wgi['indicator'] == 'pv') & (wgi['year'] == 2023)]


# In[40]:


pv2 = pv[['countryname', 'estimate', 'pctrank']]
pv2 = pv2.rename(columns={'countryname': 'Country'})


# In[41]:


pv_share = pd.merge(pv2, top_share_total, how='inner', on='Country')


# In[42]:


pv_share.head()


# In[43]:


pv_share.to_csv("pv_share2_20250519.csv", index=False)


# ### 2/Rule of law

# In[44]:


rl = wgi[wgi['countryname'].isin(top_countries) & (wgi['indicator'] == 'rl') & (wgi['year'] == 2023)]


# In[45]:


rl2 = rl[['countryname', 'estimate', 'pctrank']]
rl2 = rl2.rename(columns={'countryname': 'Country'})


# In[46]:


rl_share = pd.merge(rl2, top_share_total, how='inner', on='Country')


# In[47]:


rl_share.to_csv("rl_share2_20250528.csv", index=False)


# ### 3/Corruption

# In[48]:


cc = wgi[wgi['countryname'].isin(top_countries) & (wgi['indicator'] == 'cc') & (wgi['year'] == 2023)]


# In[49]:


cc2 = cc[['countryname', 'estimate', 'pctrank']]
cc2 = cc2.rename(columns={'countryname': 'Country'})


# In[50]:


cc_share = pd.merge(cc2, top_share_total, how='inner', on='Country')


# In[51]:


cc_share.to_csv("cc_share.csv", index=False)


# ## C-Ranking per global share
# Tables

# In[52]:


df_rank_min = share_total.drop(columns=["Rank 2022", "Production 2023", "Share in %", "Share cum.%", "Share HHI", "unit"])


# In[53]:


df_rank_min_pivot = df_rank_min.pivot(
    index="Mineral",
    columns="Rank 2023",
    values="Country"
).reset_index()


# In[54]:


df_rank_min_pivot.to_csv("pivotRankMinerals.csv")


# In[55]:


df_rank_min_pivot


# In[58]:


## Complementing table


# In[59]:


share_total["Share in %"] = share_total["Share in %"].astype(float).round(2)
share_total["Share in %"] = share_total["Share in %"].astype(str)
share_total["c_share"] = share_total["Country"] + ": " + share_total["Share in %"] + "%"


# In[60]:


df_rank_pivot = share_total.pivot(
    index="Mineral",
    columns="Rank 2023",
    values="c_share"
).reset_index()


# In[61]:


df_rank_pivot


# In[ ]:


df_rank_pivot.to_csv("topRankDetailTotal.csv", index=False)


# In[ ]:




