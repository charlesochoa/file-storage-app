import os
import json
import gzip
import pandas as pd
from urllib.request import urlopen

# con esta linea te lo descargas
# !wget http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Digital_Music.json.gz

### load the meta data

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield eval(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

# Get dataframe
df = getDF('meta_Digital_Music.json')

### remove rows with unformatted title (i.e. some 'title' may still contain html style content)
df3 = df.fillna('')
df4 = df3[df3.title.str.contains('getTime')] # unformatted rows
df5 = df3[~df3.title.str.contains('getTime')] # filter those unformatted rows
print(len(df4))
print(len(df5))


print(df.head())

