#!/usr/bin/env python
# https://pymupdf.readthedocs.io/en/latest/the-basics.html

import sys,os,click,logging
import pymupdf

logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG))

@click.command()
@click.option("--input_file", required=True, type=click.Path(file_okay=True, dir_okay=False, exists=True), help="Input PDF file.")
@click.option("--output_file", required=False, type=click.Path(file_okay=True, dir_okay=False), help="Output TXT file.")
@click.option("--encoding", default="utf8", help="Text encoding.")
@click.option("--table_delim", default="\t", help="Table column delimiter.")
@click.option("--paginate", is_flag=True, help="Write page delimiters.")
@click.option("--extract_tables", is_flag=True, help="")

#############################################################################
def main(input_file, output_file, encoding, paginate, extract_tables, table_delim):
  fin = pymupdf.open(input_file)
  fout = open(output_file, "wb") if output_file else sys.stdout.buffer
  for page in fin:
    if extract_tables:
      txt = Page2TableTxt(page, encoding, table_delim)
    else:
      txt = Page2Txt(page, encoding)
    fout.write(txt)
    if paginate:
      fout.write(bytes((12,))) # page delimiter (form feed 0x0C)
  fout.close()

#############################################################################
def Page2Txt(page, encoding):
  txt = page.get_text().encode(encoding)
  return txt

#############################################################################
def Page2TableTxt(page, encoding, delim):
  tables = page.find_tables()
  logging.debug(f"{len(tables.tables)} table[s] found on {page}")
  txt = ""
  if tables.tables:
    for table in tables:
      rows = table.extract()
      for row in rows:
        j=0;
        for cell in row:
          j+=1
          if cell is None: cell = ""
          if j>1: txt += delim
          txt += cell
        txt += "\n"
  return txt.encode(encoding)

#############################################################################
if __name__ == '__main__':
  main()

