#!/usr/bin/env python3
"""
Pandas/Tabulate Csv2Markdown.
Tabulate formatting https://pypi.org/project/tabulate/
"""
###
import sys,os,argparse,re,logging
import tabulate
import pandas as pd

# default=lambda(x: f"{x:.3f}"),
#############################################################################
if __name__=='__main__':
  FORMATS = ["plain", "simple", "github", "grid", "fancy_grid", "pipe", "orgtbl", "jira", "presto", "pretty", "psql", "rst", "mediawiki", "moinmoin", "youtrack", "html", "unsafehtml", "latex", "latex_raw", "latex_booktabs", "latex_longtable", "textile", "tsv"]
  parser = argparse.ArgumentParser(description='Pandas/Tabulate Csv2Markdown.')
  parser.add_argument("--i", dest="ifile", required=True, help="input (CSV|TSV)")
  parser.add_argument("--o", dest="ofile", help="output (HTML)")
  parser.add_argument("--csv", action="store_true", help="delimiter is comma")
  parser.add_argument("--tsv", action="store_true", help="delimiter is tab")
  parser.add_argument("--title", help="Markdown heading")
  parser.add_argument("--columns", help="Subset of columns to write (comma delimited)")
  parser.add_argument("--nrows", type=int)
  parser.add_argument("--skiprows", type=int)
  parser.add_argument("--numalign", choices=["center","right","left","decimal"], default="center")
  parser.add_argument("--stralign", choices=["center","right","left"], default="left")
  parser.add_argument("--format", choices=FORMATS, default="github", help="tabulate format (tablefmt)")
  parser.add_argument("--na_rep", default="", help="String representation of NaN")
  parser.add_argument("--float_format", help="Function(float) -> string.")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.csv: delim=','
  elif args.tsv: delim='\t'
  elif re.search('\.csv', args.ifile, re.I): delim=','
  else: delim='\t'

  title = args.title if args.title else f"Csv2Markdown: {os.path.basename(args.ifile)}"
  columns = re.split(r',', args.columns) if args.columns else None

  df = pd.read_csv(args.ifile, sep=delim, nrows=args.nrows, skiprows=args.skiprows)

  if columns is not None:
    df = df[columns]

  if args.na_rep is not None:
    df = df.fillna(args.na_rep)

  table_md = df.to_markdown(tablefmt=args.format)

  md = f"""
# {title}

{table_md}
"""

  fout.write(md)
  fout.close()

