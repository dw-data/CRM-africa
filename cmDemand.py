#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np


# In[3]:


# List of EU's CM produced in Africa. The list is a result of previous analysis
# Source1:  5th list of EU's CRM. Annex II of the Regulation proposal COM(2023). 
# https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52023PC0160
# Source2: World Mining Data 2025

CM_EU_Africa = [
'Arsenic', 'Bauxite', 'Baryte', 'Beryllium (conc.)', 'Cobalt', 'Coking Coal', 'Copper', 'Feldspar', 'Fluorspar', 'Rare Earths (REO)', 'Lithium (Li2O)', 'Manganese', 'Graphite', 'Nickel', 'Niobium (Nb2O5)', 'Phosphate Rock (P2O5)', 'Platinum', 'Tantalum (Ta2O5)', 'Titanium (TiO2)', 'Tungsten (W)', 'Vanadium (V)']


# In[4]:


## IEA Critical Materials Dataset https://www.iea.org/data-and-statistics/data-product/critical-minerals-dataset


# ## 1) Future demand, by general uses
# Bar chart

# In[5]:


df = pd.read_excel("CM_Data_Explorer.xlsx", sheet_name="1 Total demand for key minerals")


# In[6]:


df


# In[7]:


# Dropping anything outside present policies scenario
#Columns
df_filter = df.loc[:, :"Unnamed: 7"]  # Keep only columns up to Unnamed: 7
df_filter = df_filter.drop(columns="Unnamed: 2")

#Rows
df_filter = df_filter.drop(index=[0, 1, 2, 4, 17, 18, 28, 29, 37, 38, 50, 51, 59, 60, 68, 69])  


# In[9]:


# Filtering by targetted categories
list = ["Solar PV", "Wind", "Other low emissions power generation", "Electric vehicles", "Grid battery storage", "Hydrogen technologies", "Electricity networks", "Low emissions power generation"]
df_filter_totals = df_filter[~df_filter[0].isin(list)]


# In[11]:


# Cleaning
df_filter.loc[3] = df_filter.loc[3].fillna(0).apply(lambda x: int(x) if pd.notna(x) else x).round()
df_filter.columns = df_filter.iloc[0] 


# ### Analysis

# In[12]:


#Data analysis for first bar chart
total_clean = df_filter_totals.groupby(df_filter_totals[0] == 'Total clean technologies').sum(numeric_only=True)
total_demand = df_filter_totals.groupby(df_filter_totals[0] == 'Total demand').sum(numeric_only=True)
other_uses = df_filter_totals.groupby(df_filter_totals[0] == 'Other uses').sum(numeric_only=True)


# In[13]:


total_clean


# In[14]:


other_uses


# In[30]:


total_demand


# ## 2) Future demand, by mineral
# Small multiples

# In[15]:


df2 = pd.read_excel("CM_Data_Explorer.xlsx", sheet_name="3.2 Cleantech demand by mineral")


# In[16]:


df2


# In[17]:


# Dropping anything outside stated policies scenario

#Columns
df2_filter = df2.loc[:, :"Unnamed: 7"]  # Keep only columns up to Unnamed: 7
df2_filter = df2_filter.drop(columns="Unnamed: 2")

#Rows
df2_filter = df2_filter.drop(index=[0, 1, 2, 4])  


# In[18]:


df2_filter


# In[19]:


df2_filter.loc[3] = df2_filter.loc[3].apply(lambda x: int(x) if pd.notna(x) else x).round()
df2_filter.columns = df2_filter.iloc[0]
df2_filter.columns = df2_filter.columns.fillna('mineral')
df2_filter = df2_filter.drop(index=[3])


# ### Matching IEA's minerals with EU critical minerals found in Africa

# In[23]:


CM_new = []
for mineral in CM_EU_Africa:
    mineral = mineral.split('(')[0].strip()
    CM_new.append(mineral)


# In[24]:


df2_filter['mineral'] = df2_filter['mineral'].replace('Total rare earth elements', 'Rare Earths')


# In[25]:


df2_filter2 = df2_filter[df2_filter['mineral'].isin(CM_new)]


# In[26]:


dfplat = df2_filter[df2_filter['mineral'] == 'PGMs (other than iridum)'] # we want to add this one because it's platinum group


# In[27]:


dfgraph = df2_filter[df2_filter['mineral'] == 'Battery-grade graphite'] # we want to keep this one because it's graphite


# In[28]:


df2_filter2 = pd.concat([df2_filter2, dfplat, dfgraph], ignore_index=True)


# In[29]:


df2_filter2.to_csv("CM_demand_cleantech.csv", index=False)

