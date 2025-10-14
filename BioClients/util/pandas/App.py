#!/usr/bin/env python3
"""
Pandas CSV/TSV utilities.
"""
###
import sys,os,argparse,re,pickle,logging
import pandas as pd

from .. import pandas as util_pandas

#############################################################################
if __name__=='__main__':
  verstr = (f'Python: {sys.version.split()[0]}; pandas: {pd.__version__}')
  parser = argparse.ArgumentParser(prog="BioClients.util.pandas.Utils", description='Pandas utilities for simple datafile transformations.', epilog=verstr)
  ops = ['csv2tsv', 'tsv2csv', 'shape', 'summary', 'showcols', 'list_columns', 'to_html',
	'selectcols', 'selectcols_deduplicate', 'uvalcounts',
	'colvalcounts', 'sortbycols', 'deduplicate', 'colstats', 'searchrows',
	'pickle', 'sample', 'set_header', 'remove_header', 'concat', 'merge']
  compressions=['gzip', 'zip', 'bz2']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", required=True, help="input (CSV|TSV)")
  parser.add_argument("--iB", dest="ifileB", help="input (CSV|TSV) for merge operation")
  parser.add_argument("--o", dest="ofile", help="output (CSV|TSV)")
  parser.add_argument("--coltags", help="cols specified by tag (comma-separated)")
  parser.add_argument("--cols", help="cols specified by idx (1+) (comma-separated)")
  parser.add_argument("--noheader", action="store_true", help="default: line-one is header")
  parser.add_argument("--search_qrys", help="qrys (comma-separated, NA|NaN handled specially)")
  parser.add_argument("--search_rels", default="=", help="relationships (=|>|<) (comma-separated)")
  parser.add_argument("--search_typs", default="str", help="types (str|int|float) (comma-separated)")
  parser.add_argument("--compression", choices=compressions)
  parser.add_argument("--csv", action="store_true", help="delimiter is comma")
  parser.add_argument("--tsv", action="store_true", help="delimiter is tab")
  parser.add_argument("--clean_coltags", action="store_true", help="trim and replace whitespace, punctuation")
  parser.add_argument("--on_bad_lines", choices=["error", "warn", "skip"], default="warn")
  parser.add_argument("--merge_how", choices=["left", "right", "outer", "inner", "cross"], default="inner")
  parser.add_argument("--merge_type", choices=[str, int, float], default=str)
  parser.add_argument("--concat_axis", type=int, choices=[0, 1], default=0)
  parser.add_argument("--nrows", type=int)
  parser.add_argument("--skiprows", type=int)
  parser.add_argument("--sample_frac", type=float, default=.01, help="sampling probability (0-1)")
  parser.add_argument("--sample_n", type=int, help="sampling N")
  parser.add_argument("--html_title", help="table title")
  parser.add_argument("--html_prettify", action="store_true", help="requires Pandas v1.4.0+")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if args.op in ('selectcols', 'selectcols_deduplicate', 'uvalcounts', 'colvalcounts', 'sortbycols'):
    if args.cols:
      logging.info(f"Cols selected: {args.cols}")
    elif args.coltags: 
      logging.info(f"Coltags selected: {args.coltags}")
    else:
      parser.error(f'{args.op} requires --cols or --coltags.')

  logging.info(verstr)

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.compression: compression=args.compression
  elif re.search('\.gz$', args.ifile, re.I): compression='gzip'
  elif re.search('\.bz2$', args.ifile, re.I): compression='bz2'
  elif re.search('\.zip$', args.ifile, re.I): compression='zip'
  else: compression=None

  if args.csv or args.op=='csv2tsv': delim=','
  elif args.tsv or args.op=='tsv2csv': delim='\t'
  elif re.search('\.csv', args.ifile, re.I): delim=','
  elif re.search('\.tsv', args.ifile, re.I) or re.search('\.tab', args.ifile, re.I): delim='\t'
  else: delim='\t'

  cols=None; coltags=None;
  if args.cols:
    cols = [(int(col.strip())-1) for col in re.split(r',', args.cols.strip())]
    logging.info(f"Cols selected: {str(cols)}")
  elif args.coltags:
    coltags = [coltag.strip() for coltag in re.split(r',', args.coltags.strip())]
    logging.info(f"Coltags selected: {','.join(coltags)}")

  search_qrys = [qry.strip() for qry in re.split(r',', args.search_qrys.strip())] if (args.search_qrys is not None) else None
  search_rels = [rel.strip() for rel in re.split(r',', args.search_rels.strip())] if (args.search_rels is not None) else None
  search_typs = [typ.strip() for typ in re.split(r',', args.search_typs.strip())] if (args.search_typs is not None) else None

  df = pd.read_csv(args.ifile, sep=delim, header=(None if args.noheader else 0), compression=compression, on_bad_lines=args.on_bad_lines, nrows=(1 if args.op in ('showcols', 'list_columns') else args.nrows), skiprows=args.skiprows)

  if args.clean_coltags: util_pandas.CleanColtags(df)
    
  if args.op == 'showcols':
    for j,tag in enumerate(df.columns):
      fout.write(f'{j+1}. "{tag}"\n')

  elif args.op == 'list_columns':
    fout.write("\n".join(df.columns)+"\n")

  elif args.op == 'shape':
    fout.write(f"rows: {df.shape[0]}; cols: {df.shape[1]}\n")

  elif args.op == 'summary':
    fout.write(f"rows: {df.shape[0]}; cols: {df.shape[1]}\n")
    fout.write("coltags: {}\n".format(', '.join([f'"{tag}"' for tag in df.columns])))

  elif args.op=='csv2tsv':
    df.to_csv(fout, sep='\t', index=False, header=(not args.noheader))

  elif args.op=='tsv2csv':
    df.to_csv(fout, sep=',', index=False, header=(not args.noheader))

  elif args.op=='to_html':
    util_pandas.ToHtml(df, args.html_title, args.html_prettify, fout)

  elif args.op == 'selectcols':
    logging.info(f"Input: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df = df[coltags] if coltags else df.iloc[:, cols]
    logging.info(f"Output: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df.to_csv(fout, sep='\t', index=False, header=(not args.noheader))

  elif args.op == 'selectcols_deduplicate':
    logging.info(f"Input: rows: {df.shape[0]}; cols: {df.shape[1]}")
    subset = coltags if coltags else df.columns[cols].to_list() if cols else None
    df.drop_duplicates(subset=subset, inplace=True)
    df = df[coltags] if coltags else df.iloc[:, cols]
    logging.info(f"Output: rows: {df.shape[0]}; cols: {df.shape[1]}")
    df.to_csv(fout, sep='\t', index=False, header=(not args.noheader))

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
    df.to_csv(fout, sep='\t', index=False, header=(not args.noheader))

  elif args.op == 'searchrows':
    if args.search_qrys is None: 
      parser.error(f'{args.op} requires --search_qrys.')
    logging.debug(f"search_qrys={search_qrys}")
    logging.debug(f"search_rels={search_rels}")
    logging.debug(f"search_typs={search_typs}")
    util_pandas.SearchRows(df, cols, coltags, search_qrys, search_rels, search_typs, fout)

  elif args.op == 'sample':
    util_pandas.SampleRows(df, args.sample_frac, args.sample_n, fout)

  elif args.op == 'set_header':
    util_pandas.SetHeader(df, coltags, delim, fout)

  elif args.op == 'remove_header':
    util_pandas.RemoveHeader(df, delim, fout)

  elif args.op == 'pickle':
    if not args.ofile:
      parser.error(f'{args.op} requires --o.')
    fout.close()
    with open(args.ofile, 'wb') as fout:
      pickle.dump(df, fout, pickle.HIGHEST_PROTOCOL)

  elif args.op == 'concat':
    if not args.ifileB: parser.error(f'{args.op} requires --iB.')
    dfB = pd.read_csv(args.ifileB, sep=delim, header=(None if args.noheader else 0), compression=compression, on_bad_lines=args.on_bad_lines, nrows=args.nrows, skiprows=args.skiprows)
    util_pandas.Concat(df, dfB, args.concat_axis, delim, fout)

  elif args.op == 'merge':
    if not args.ifileB: parser.error(f'{args.op} requires --iB.')
    if not args.coltags: parser.error(f'{args.op} requires --coltags.')
    dfB = pd.read_csv(args.ifileB, sep=delim, header=(None if args.noheader else 0), compression=compression, on_bad_lines=args.on_bad_lines, nrows=args.nrows, skiprows=args.skiprows)
    if args.clean_coltags: util_pandas.CleanColtags(dfB)
    coltags = [coltag.strip() for coltag in re.split(r',', args.coltags.strip())]
    util_pandas.Merge(df, dfB, args.merge_how, args.merge_type, coltags, delim, fout)

  else:
    parser.error(f'Unknown operation: {args.op}')
