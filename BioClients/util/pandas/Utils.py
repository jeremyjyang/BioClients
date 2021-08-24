#!/usr/bin/env python3
"""
Pandas CSV/TSV utilities.
"""
###
import sys,os,argparse,re,pickle,logging
import pandas as pd

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
if __name__=='__main__':
  verstr = (f'Python: {sys.version.split()[0]}; pandas: {pd.__version__}')
  parser = argparse.ArgumentParser(prog="BioClients.util.pandas.Utils", description='Pandas utilities for simple datafile transformations.', epilog=verstr)
  ops = ['csv2tsv', 'shape', 'summary', 'showcols', 'to_html',
	'selectcols', 'selectcols_deduplicate', 'uvalcounts',
	'colvalcounts', 'sortbycols', 'deduplicate', 'colstats', 'searchrows',
	'pickle', 'sample', 'set_header', 'remove_header']
  compressions=['gzip', 'zip', 'bz2']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", required=True, help="input (CSV|TSV)")
  parser.add_argument("--o", dest="ofile", help="output (CSV|TSV)")
  parser.add_argument("--coltags", help="cols specified by tag (comma-separated)")
  parser.add_argument("--cols", help="cols specified by idx (1+) (comma-separated)")
  parser.add_argument("--search_qrys", help="qrys (comma-separated, NA|NaN handled specially)")
  parser.add_argument("--search_rels", default="=", help="relationships (=|>|<) (comma-separated)")
  parser.add_argument("--search_typs", default="str", help="types (str|int|float) (comma-separated)")
  parser.add_argument("--compression", choices=compressions)
  parser.add_argument("--csv", action="store_true", help="delimiter is comma")
  parser.add_argument("--tsv", action="store_true", help="delimiter is tab")
  parser.add_argument("--disallow_bad_lines", action="store_true", help="default=allow+skip+warn")
  parser.add_argument("--nrows", type=int)
  parser.add_argument("--skiprows", type=int)
  parser.add_argument("--sample_frac", type=float, default=.01, help="sampling probability (0-1)")
  parser.add_argument("--sample_n", type=int, help="sampling N")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if args.op in ('selectcols', 'uvalcounts', 'colvalcounts', 'sortbycols'):
    if not (args.cols or args.coltags): 
      parser.error(f'{args.op} requires --cols or --coltags.')

  logging.info(verstr)

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.compression: compression=args.compression
  elif re.search('\.gz$', args.ifile, re.I): compression='gzip'
  elif re.search('\.bz2$', args.ifile, re.I): compression='bz2'
  elif re.search('\.zip$', args.ifile, re.I): compression='zip'
  else: compression=None

  if args.csv or args.op=='csv2tsv': delim=','
  elif args.tsv: delim='\t'
  elif re.search('\.csv', args.ifile, re.I): delim=','
  elif re.search('\.tsv', args.ifile, re.I) or re.search('\.tab', args.ifile, re.I): delim='\t'
  else: delim='\t'

  cols=None; coltags=None;
  if args.cols:
    cols = [(int(col.strip())-1) for col in re.split(r',', args.cols.strip())]
  elif args.coltags:
    coltags = [coltag.strip() for coltag in re.split(r',', args.coltags.strip())]

  search_qrys = [qry.strip() for qry in re.split(r',', args.search_qrys.strip())] if (args.search_qrys is not None) else None
  search_rels = [rel.strip() for rel in re.split(r',', args.search_rels.strip())] if (args.search_rels is not None) else None
  search_typs = [typ.strip() for typ in re.split(r',', args.search_typs.strip())] if (args.search_typs is not None) else None

  df = pd.read_csv(args.ifile, sep=delim, compression=compression, error_bad_lines=args.disallow_bad_lines, nrows=(1 if args.op=='showcols' else args.nrows), skiprows=args.skiprows)

  if args.op == 'showcols':
    for j,tag in enumerate(df.columns):
      fout.write(f'{j+1}. "{tag}"\n')

  elif args.op == 'shape':
    fout.write(f"rows: {df.shape[0]}; cols: {df.shape[1]}\n")

  elif args.op == 'summary':
    fout.write(f"rows: {df.shape[0]}; cols: {df.shape[1]}\n")
    fout.write("coltags: {}\n".format(', '.join([f'"{tag}"' for tag in df.columns])))

  elif args.op=='csv2tsv':
    df.to_csv(fout, '\t', index=False)

  elif args.op=='to_html':
    df.to_html(fout, index=False, header=True,
	formatters=None, float_format=None, sparsify=None,
	bold_rows=True, border=None, justify=None,
	classes=None, render_links=True,
	show_dimensions=False)

  elif args.op == 'selectcols':
    logging.info(f"Input: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df = df[coltags] if coltags else df.iloc[:, cols]
    logging.info(f"Output: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df.to_csv(fout, '\t', index=False)

  elif args.op == 'selectcols_deduplicate':
    logging.info(f"Input: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df = df[coltags] if coltags else df.iloc[:, cols]
    df.drop_duplicates(inplace=True)
    logging.info(f"Output: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df.to_csv(fout, '\t', index=False)

  elif args.op == 'uvalcounts':
    for j,tag in enumerate(df.columns):
      if cols and j not in cols: continue
      if coltags and tag not in coltags: continue
      logging.info(f'{j+1}. {tag}: {df[tag].nunique()}')

  elif args.op == 'colvalcounts':
    for j,tag in enumerate(df.columns):
      if cols and j not in cols: continue
      if coltags and tag not in coltags: continue
      logging.info(f'{j+1}. {tag}:')
      for key,val in df[tag].value_counts().iteritems():
        logging.info(f'\t{tag}: {val:6d}: {key}')

  elif args.op == 'colstats':
    for j,tag in enumerate(df.columns):
      if cols and j not in cols: continue
      if coltags and tag not in coltags: continue
      fout.write(f'{j+1}. {tag}:\n')
      fout.write(f'\tN: {df[tag].size}\n')
      fout.write(f'\tN_isna: {df[tag].isna().sum()}\n')
      fout.write(f'\tmin: {df[tag].min():.2f}\n')
      fout.write(f'\tmax: {df[tag].max():.2f}\n')
      fout.write(f'\tmean: {df[tag].mean():.2f}\n')
      fout.write(f'\tmedian: {df[tag].median():.2f}\n')
      fout.write(f'\tstd: {df[tag].std():.2f}\n')

  elif args.op == 'deduplicate':
    df.drop_duplicates(inplace=True)
    df.to_csv(fout, '\t', index=False)

  elif args.op == 'searchrows':
    if args.search_qrys is None: 
      parser.error(f'{args.op} requires --search_qrys.')
    logging.debug(f"search_qrys={search_qrys}")
    logging.debug(f"search_rels={search_rels}")
    logging.debug(f"search_typs={search_typs}")
    SearchRows(df, cols, coltags, search_qrys, search_rels, search_typs, fout)

  elif args.op == 'sample':
    SampleRows(df, args.sample_frac, args.sample_n, fout)

  elif args.op == 'set_header':
    SetHeader(df, coltags, delim, fout)

  elif args.op == 'remove_header':
    RemoveHeader(df, delim, fout)

  elif args.op == 'pickle':
    if not args.ofile:
      parser.error(f'{args.op} requires --o.')
    fout.close()
    with open(args.ofile, 'wb') as fout:
      pickle.dump(df, fout, pickle.HIGHEST_PROTOCOL)

  else:
    parser.error(f'Unknown operation: {args.op}')
