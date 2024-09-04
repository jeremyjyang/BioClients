#!/usr/bin/env python3
###

import sys,os,time,logging
import numpy as np
import pandas as pd
import h5py

from ...util import hdf as hdf_util

#############################################################################
def ListSamples(f, fout):
  if "meta" not in f or "samples" not in f["meta"]:
    logging.error("No samples found.")
    return
  #samples_title = f["meta"]["samples/title"]
  #print(pd.DataFrame(samples_title.asstr()[0:10,]))
  samples = f["meta"]["samples"]
  df = pd.DataFrame()
  for i,k in enumerate(list(samples.keys())):
    logging.debug(f"{i+1}. {samples[k].name}")
    if type(samples[k]) is h5py.Dataset:
      df_this = pd.DataFrame(samples[k])
      df = pd.concat([df, df_this], axis=1)
      df = df.drop_duplicates()
    #if i>2: break #DEBUG
  df.columns = list(samples.keys())
  #print(df.iloc[0:10,:])

  for col, dtype in df.dtypes.items():
    if dtype == np.object:  # Only process object columns.
      # decode, or return original value if decode return Nan
      df[col] = df[col].str.decode('utf-8').fillna(df[col]) 

  logging.info(f"Output rows: {df.shape[0]}; columns: {df.shape[1]}")
  df.to_csv(fout, sep="\t", index=False)

#############################################################################
