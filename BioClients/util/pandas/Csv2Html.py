#!/usr/bin/env python3
"""
Pandas CSV2HTML.
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

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Pandas CSV2HTML.')
  parser.add_argument("--i", dest="ifile", required=True, help="input (CSV|TSV)")
  parser.add_argument("--o", dest="ofile", help="output (HTML)")
  parser.add_argument("--csv", action="store_true", help="delimiter is comma")
  parser.add_argument("--tsv", action="store_true", help="delimiter is tab")
  parser.add_argument("--nrows", type=int)
  parser.add_argument("--skiprows", type=int)
  parser.add_argument("--justify", choices=["center","right","left"], default="center")
  parser.add_argument("--classes", default="mystyle", help="CSS classes")
  parser.add_argument("--title", help="HTML title")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.csv: delim=','
  elif args.tsv: delim='\t'
  elif re.search('\.csv', args.ifile, re.I): delim=','
  else: delim='\t'

  title = args.title if args.title else f"CSV2HTML: {os.path.basename(args.ifile)}"

  df = pd.read_csv(args.ifile, sep=delim, nrows=args.nrows, skiprows=args.skiprows)

  table_html = df.to_html(index=False, header=True,
	formatters=None, float_format=None, sparsify=None,
	bold_rows=True, border=None, justify=args.justify,
	classes=args.classes, render_links=True,
	show_dimensions=False)

  pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

  html = f"""
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

