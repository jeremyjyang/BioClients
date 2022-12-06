#!/usr/bin/env python3
"""
Pandas CSV/TSV utilities.
"""
###
import sys,os,re,logging
import pandas as pd

#############################################################################
def CleanColtags(df):
  oldtags = list(df.columns)[:]
  newtags=[];
  for j,tag in enumerate(oldtags):
    tag = re.sub(r'[\s,;|\\]+', '_', tag.strip())
    if tag=="": tag = f"Column_{j:02d}"
    newtags.append(tag)
  for j in range(len(oldtags)):
    logging.debug(f"""{j}. "{oldtags[j]}" -> "{newtags[j]}" """)
  df.columns = newtags

#############################################################################
def SearchRows(df, cols, coltags, qrys, rels, typs, fout):
  n = df.shape[0]
  for j,tag in enumerate(df.columns):
    if cols:
      if j not in cols: continue
      else: jj = cols.index(j)
    elif coltags:
      if tag not in coltags: continue
      else: jj = coltags.index(tag)
    logging.debug(f"tag={tag}; j={j}; jj={jj}")
    if qrys[jj].upper() in ('NA','NAN'):
      df = df[df[tag].isna()]
    elif typs[jj]=='int':
      df = df[df[tag].astype('int')==int(qrys[jj])]
    elif typs[jj]=='float':
      df = df[df[tag].astype('float')==float(qrys[jj])]
    else:
      df = df[df[tag].astype('str').str.match('^'+qrys[jj]+'$')]
  df.to_csv(fout, '\t', index=False)
  logging.info(f"Rows found: {df.shape[0]} / {n}")

#############################################################################
def SampleRows(df, sample_frac, sample_n, fout):
  n = df.shape[0]
  if sample_n:
    df = df.sample(n=sample_n)
  else:
    df = df.sample(frac=sample_frac)
  df.to_csv(fout, '\t', index=False)
  logging.info(f"Rows sampled: {df.shape[0]} / {n}")

#############################################################################
def RemoveHeader(df, delim, fout):
  df.to_csv(fout, delim, index=False, header=False)

#############################################################################
def SetHeader(df, coltags, delim, fout):
  if not coltags:
    logging.error("Coltags required.")
  elif len(coltags)!=df.shape[1]:
    logging.error(f"len(coltags) != ncol ({len(coltags)} != {df.shape[1]}).")
  else:
    df.to_csv(fout, delim, index=False, header=coltags)

#############################################################################
def ToHtml(df, title, prettify, fout):
  precision=3;
  if prettify:
    from pandas.io.formats.style import Styler #Pandas v1.4.0+.
    styler = Styler(df, precision=precision)
    styler.set_caption(title if title is not None else (f"{df.shape[0]}rows,{df.shape[1]}cols"))
    styler.set_properties(**{'background-color': 'white', 'color':'navy', 'border':'1px solid black'})
    fout.write(styler.to_html())
  else:
    df.round(precision).to_html(fout, index=True, header=True,
	formatters=None, float_format=None, sparsify=None,
	bold_rows=True, border=None, justify=None,
	classes=None, render_links=True,
	show_dimensions=False)

#############################################################################
def Merge(dfA, dfB, merge_how, coltags, delim, fout):
  df = dfA.merge(dfB, how=merge_how, on=coltags)
  df.to_csv(fout, delim, index=False, header=True)
  logging.info(f"Rows in A: {dfA.shape[0]}")
  logging.info(f"Rows in B: {dfB.shape[0]}")
  logging.info(f"Rows out: {df.shape[0]}")

#############################################################################
