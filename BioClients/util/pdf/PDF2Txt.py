#!/usr/bin/env python
# https://pymupdf.readthedocs.io/en/latest/the-basics.html

import sys,os,re,click,logging
import pandas as pd
import pymupdf


@click.command()
@click.option("--input_file", required=True, type=click.Path(file_okay=True, dir_okay=False, exists=True), help="Input PDF file.")
@click.option("--output_file", required=False, type=click.Path(file_okay=True, dir_okay=False), help="Output TXT file.")
@click.option("--encoding", default="utf8", help="Text encoding.")
@click.option("--describe", is_flag=True, help="Describe document and quit.")
@click.option("--paginate", is_flag=True, help="Write page delimiters.")
@click.option("--pages_selected", default=None, help="Extract only pages specified (comma-separated list)")
@click.option("--extract_tables", is_flag=True, help="")
@click.option("--extract_tables_selected", default=None, help="Extract only tables specified (comma-separated list)")
@click.option("--table_delim", default="\t", help="Table column delimiter.")
@click.option("--debug", is_flag=True)

#############################################################################
def main(input_file, output_file, encoding, describe, paginate, pages_selected, extract_tables, extract_tables_selected, table_delim, debug):
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if debug else logging.INFO))
  fin = pymupdf.open(input_file)
  fout = open(output_file, "wb") if output_file else sys.stdout.buffer
  if describe:
    Describe(fin)
    sys.exit()
  if pages_selected:
    ps = re.split('[, ]+', pages_selected.strip())
    ps = [int(p) for p in ps]
    ps.sort()
    logging.debug(f"Page[s] selected: {ps}")
  else:
    ps = []
  i_p=0
  for page in fin:
    i_p+=1
    if ps and i_p not in ps:
      logging.debug(f"Skipping page: {i_p}")
      continue
    if extract_tables:
      txt = Page2TableTxt(page, encoding, table_delim, None)
    elif extract_tables_selected:
      txt = Page2TableTxt(page, encoding, table_delim, extract_tables_selected)
    else:
      txt = Page2Txt(page, encoding)
    fout.write(txt)
    if paginate:
      fout.write(bytes((12,))) # page delimiter (form feed 0x0C)
  fout.close()

#############################################################################
def Describe(fin):
  df = None;
  i_p=0
  for page in fin:
    i_p+=1
    label = page.get_label()
    tables = page.find_tables().tables
    images = page.get_images()
    links = page.get_links()
    text = page.get_text()
    df = pd.concat([df, pd.DataFrame({'page_number':[page.number+1],
'label':[label if label else '~'], 'text_size':[len(text)],
'n_images':[len(images)], 'n_tables':[len(tables)],
'n_links':[len(links)]})])
  df.to_csv(sys.stdout, "\t", index=False, header=True)
  return df

#############################################################################
def Page2Txt(page, encoding):
  txt = page.get_text().encode(encoding)
  return txt

#############################################################################
def Page2TableTxt(page, encoding, delim, tselected):
  if tselected:
    ts = re.split('[, ]+', tselected.strip())
    ts = [int(t) for t in ts]
    ts.sort()
    logging.debug(f"Table[s] selected: {ts}")
  else:
    ts = []
  tables = page.find_tables()
  logging.debug(f"{len(tables.tables)} table[s] found on page {page.number+1}")
  txt = ""
  if tables.tables:
    i_t=0
    for table in tables:
      i_t+=1
      if ts and i_t not in ts:
        logging.debug(f"Skipping table: {i_t}")
        continue
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

