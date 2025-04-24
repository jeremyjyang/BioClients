#!/usr/bin/env python3
'''
https://pypi.org/project/entrezpy/
https://entrezpy.readthedocs.io/en/master/
https://academic.oup.com/bioinformatics/article/35/21/4511/5488119
https://dataguide.nlm.nih.gov/eutilities/utilities.html
'''
import os,sys,io,re,json,time,requests,urllib.parse,logging,tqdm
import pandas as pd

import entrezpy.conduit

from .. import util

#############################################################################
def Test(email):
  c = entrezpy.conduit.Conduit(email)
  fetch_influenza = c.new_pipeline()
  sid = fetch_influenza.add_search({'db' : 'nucleotide', 'term' : 'H3N2 [organism] AND HA', 'rettype':'count', 'sort' : 'Date Released', 'mindate': 2000, 'maxdate':2019, 'datetype' : 'pdat'})
  fid = fetch_influenza.add_fetch({'retmax' : 10, 'retmode' : 'text', 'rettype': 'fasta'}, dependency=sid)
  c.run(fetch_influenza)


#############################################################################
#############################################################################
