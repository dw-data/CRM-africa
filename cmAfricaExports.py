#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


## Source: UN Comtrade https://comtradeplus.un.org/
## This is what we will be looking at:

#Type : C , Frequency : A , Classification : HS , Period : 2023 , 
#Reporters : Algeria , Reporters : Angola, Reporters : Botswana , Reporters : Burundi , Reporters : Dem. Rep. of the Congo , Reporters : Côte d'Ivoire , 
#Reporters : Egypt , Reporters : Eritrea , Reporters : Ethiopia , Reporters : Gabon , Reporters : Ghana , Reporters : Guinea , 
#Reporters : Kenya , Reporters : Madagascar , Reporters : Malawi , Reporters : Mauritania , Reporters : Morocco , 
#Reporters : Mozambique , Reporters : Namibia , Reporters : Nigeria , Reporters : Rwanda , Reporters : Senegal , 
#Reporters : Sierra Leone , Reporters : South Africa , Reporters : Sudan , Reporters : United Rep. of Tanzania , 
#Reporters : Togo , Reporters : Tunisia , Reporters : Uganda , Reporters : Zambia , Reporters : Zimbabwe , 

#Partners : China , Partners : World , 
#CommodityCodes : 2603 , CommodityCodes : 2504 , CommodityCodes : 2604 , CommodityCodes : 2602 , CommodityCodes : 282520 , 
#CommodityCodes : 261590 , CommodityCodes : 2605 , CommodityCodes : 811291 , 
#Flows : Export , Customs : TOTAL customs procedure codes , ModeOfTransport : TOTAL modes of transport , Second Partner : World , 
#AggregateBy : None , BreakdownMode : Plus


# In[3]:


df = pd.read_csv("TradeData_6_3_2025_14_21_30.csv", encoding="latin1")


# In[4]:


df


# In[5]:


#We take only the columns that we want to analyse:
#'reporterISO': exporting country, 'partnerISO': destination, 'cmdCode': mineral, 'isAltQtyEstimated': quantity, 'cifvalue': monetary value] 
columns_to_keep = ['reporterISO', 'partnerISO', 'cmdCode', 'isAltQtyEstimated', 'cifvalue']  
df2 = df[columns_to_keep]


# In[6]:


# Column names are disorganised, we use rename() with a dictionary to map old names to new names
df2 = df2.rename(columns={'isAltQtyEstimated': 'NetWeight',
                         'cmdCode': 'mineral', 
                         'reporterISO': 'country',
                         'partnerISO': 'partner'})


# ## Finding China's % per country+mineral, and total later
# Tables

# In[7]:


df2['merged'] = df2['country'] + ' ' + df2['mineral'] #we create an id for each country+mineral pair


# In[8]:


df2


# In[9]:


# Aim: Creating a new column in our df containing China's share of world's exports

# Step 1: We create an array with country+mineral pairs to loop through. 
# We ensure our array has unique ids by using the .unique function
merged = df2['merged'].unique()

# Step 2: We create an empty dictionary. Here we will store 'country+mineral: %' elements:
percentages = {}

# Step 3: We loop through each mineral+country merge pair and calculate the percentage
for merge in merged:
    # Filter for each unique pair and create new df in each loop
    mineral_df = df2[df2['merged'] == merge]

    # Extract cifvalues safely
    world = mineral_df[mineral_df['partner'] == 'World']['cifvalue']
    china = mineral_df[mineral_df['partner'] == 'China']['cifvalue']

    if not world.empty and not china.empty:
        world_weight = world.values[0]  #we use .values to extract the cifvalue of each series
        china_weight = china.values[0]

        if world_weight > 0:
            china_percentage = (china_weight / world_weight) * 100
            percentages[merge] = china_percentage
        else:
            percentages[merge] = np.nan
    else:
        # If one of the values is missing and can't compute, we input NaN. Eg cases: no exports to China
        percentages[merge] = np.nan

# Step 4: Create a DataFrame with the results
percentage_df = pd.DataFrame(list(percentages.items()), columns=['merged', 'china_world_percentage'])

# Step 5: Merge this back to the original DataFrame
df2 = df2.merge(percentage_df, on='merged', how='left')


# In[10]:


df2


# In[11]:


# We are not interested in 'partner: World' values
df3 = df2[df2['partner'] != 'World']


# In[12]:


#df3.drop(columns=["partner", "NetWeight", "merged", "cifvalue"])


# In[13]:


pivoted_df = df3.pivot_table(
    index='country',
    columns='mineral',
    values='china_world_percentage',
).reset_index()


# In[14]:


pivoted_df


# ### New column with China's total % per country
# This column will show total exports from one country to China. Exports per mineral will not be dissagregated

# In[15]:


total = df2.groupby(['country', 'partner'])['cifvalue'].sum().reset_index()
total_pivot = total.pivot(index='country', columns='partner', values='cifvalue')

total_pivot['China_percentage'] = (total_pivot['China'] / total_pivot['World']) * 100


# In[16]:


total_pivot = total_pivot.drop(columns=["China", "World"])


# In[17]:


total_pivot


# In[18]:


total_pivot = total_pivot.reset_index()


# In[19]:


final = pd.merge(pivoted_df, total_pivot, on='country', how='outer')


# In[20]:


final


# In[21]:


final.to_csv("tabla.csv", index=False)


# ## pie charts

# In[22]:


df_more = pd.read_csv("TradeData_6_3_2025_EU_US_Ch.csv", encoding="latin1")


# In[23]:


columns_to_keep = ['reporterISO', 'partnerISO', 'cmdCode', 'isAltQtyEstimated', 'cifvalue']  
df_more2 = df_more[columns_to_keep]


# In[24]:


df_more2 = df_more2.rename(columns={'isAltQtyEstimated': 'NetWeight',
                         'cmdCode': 'mineral', 
                         'reporterISO': 'country',
                         'partnerISO': 'partner'})


# In[25]:


countries = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden", 
    "USA",
    "China",
    "World"
]


# In[26]:


eu_countries = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden"
]


# In[27]:


africa = ['Algeria',
 'Angola',
 'Benin',
 'Botswana',
 'Burkina Faso',
 'Burundi',
 'Cameroon',
 'Cape Verde',
 'Central African Republic',
 'Chad',
 'Comoros',
 'Dem. Rep. of the Congo',
 'Congo, D.R.',
 'Djibouti',
 'Egypt',
 'Equatorial Guinea',
 'Eritrea',
 'Eswatini',
 'Ethiopia',
 'Gabon',
 'The Gambia',
 'Ghana',
 'Guinea',
 'Guinea-Bissau',
 "Cote d'Ivoire",
 'Kenya',
 'Lesotho',
 'Liberia',
 'Libya',
 'Madagascar',
 'Malawi',
 'Mali',
 'Mauritania',
 'Mauritius',
 'Morocco',
 'Mozambique',
 'Namibia',
 'Niger',
 'Nigeria',
 'Rwanda',
 'São Tomé and Príncipe',
 'Senegal',
 'Seychelles',
 'Sierra Leone',
 'Somalia',
 'South Africa',
 'South Sudan',
 'Sudan',
 'Tanzania',
 'Togo',
 'Tunisia',
 'Uganda',
 'Zambia',
 'Zimbabwe']


# In[28]:


## Aim: Substracting intra African exports from 'World' exports


# In[29]:


# here, we obtain the total value of exports from african countries, to african countries
df_more3 = df_more2[df_more2["partner"].isin(africa)]
africa = df_more3["cifvalue"].sum()


# In[30]:


# here, we select export destinations: EU countries, China, US, World
df_more4 = df_more2[df_more2["partner"].isin(countries)]


# In[31]:


df_more4.loc[df_more4['partner'].isin(eu_countries), 'partner'] = "EU"


# In[32]:


df_more4.head(20)


# In[33]:


#We sum exports of all minerals per exporting country to destination
regiones = df_more4.groupby(['country', 'partner'])['cifvalue'].sum().reset_index()


# In[34]:


regiones


# In[35]:


piechart = regiones.drop(columns=["country"])


# In[36]:


piechart = piechart.groupby("partner")["cifvalue"].sum()


# In[37]:


# World represents total values, we extract exports among African countries
piechart['World'] = piechart['World'] - africa


# In[38]:


piechart = piechart.reset_index()


# In[39]:


world_value = piechart.loc[piechart["partner"] == "World", "cifvalue"].values[0]
piechart["percent_of_world"] = piechart ["cifvalue"] / world_value * 100


# In[40]:


piechart


# In[41]:


piechart.to_csv("piechart_20250603.csv", index=False)


# In[ ]:




