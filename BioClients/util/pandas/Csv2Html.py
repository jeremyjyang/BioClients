#!/usr/bin/env python3
"""
Pandas Csv2Html.
"""
###
import sys,os,argparse,re,logging
import pandas as pd

#############################################################################
def CSS():
  return """\
/* includes alternating gray and white with on-hover color */

.mystyle {
  font-size: 11pt; 
  font-family: Arial;
  border-collapse: collapse; 
  border: 1px solid silver;
}

.mystyle table {
  width: 100%;
}

.mystyle td, th {
  padding: 5px;
  max-width:400px;
  word-wrap:break-word;
  overflow-wrap: break-word;
}

.mystyle tr:nth-child(even) {
  background: #E0E0E0;
}

.mystyle tr:hover {
  background: silver;
  cursor: pointer;
}
"""

# default=lambda(x: f"{x:.3f}"),
#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Pandas CSV2HTML.')
  parser.add_argument("--i", dest="ifile", required=True, help="input (CSV|TSV)")
  parser.add_argument("--o", dest="ofile", help="output (HTML)")
  parser.add_argument("--csv", action="store_true", help="delimiter is comma")
  parser.add_argument("--tsv", action="store_true", help="delimiter is tab")
  parser.add_argument("--title", help="HTML title")
  parser.add_argument("--nrows", type=int)
  parser.add_argument("--skiprows", type=int)
  parser.add_argument("--justify", choices=["center","right","left"], default="center")
  parser.add_argument("--classes", default="mystyle", help="CSS classes")
  parser.add_argument("--columns", help="Subset of columns to write (comma delimited)")
  parser.add_argument("--index_columns", help="Index columns for hierarchical (comma delimited)")
  parser.add_argument("--na_rep", default="", help="String representation of NaN")
  parser.add_argument("--float_format", help="Function(float) -> string.")
  parser.add_argument("--border", type=int, default=1, help="Border size.")
  parser.add_argument("--table_id", help="CSS ID.")
  parser.add_argument("--sparsify", action="store_true", help="Set to False for a DataFrame with a hierarchical index to print every multiindex key at each row.")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.csv: delim=','
  elif args.tsv: delim='\t'
  elif re.search('\.csv', args.ifile, re.I): delim=','
  else: delim='\t'

  title = args.title if args.title else f"Csv2Html: {os.path.basename(args.ifile)}"
  columns = re.split(r',', args.columns) if args.columns else None

  df = pd.read_csv(args.ifile, sep=delim, nrows=args.nrows, skiprows=args.skiprows)

  if args.index_columns is not None:
    df.set_index(re.split(r',', args.index_columns), drop=True, append=False, inplace=True)

  table_html = df.to_html(header=True,
	index=(args.index_columns is not None), 
	formatters=None, float_format=args.float_format, na_rep=args.na_rep,
	columns=columns, sparsify=args.sparsify,
	bold_rows=True, border=args.border, justify=args.justify,
	classes=args.classes, table_id=args.table_id, render_links=True,
	show_dimensions=False)

  pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

  html = f"""
<!DOCTYPE html>
<html>
  <head><title>{title}</title></head>
  <style type="text/css">{CSS()}</style>
  <body>
    {table_html}
  </body>
</html>
"""

  fout.write(html)
  fout.close()

