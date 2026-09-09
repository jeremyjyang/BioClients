#!/usr/bin/env python3
'''
Parse, process Entrez PubMed XML (summaries or full), normally obtained via Entrez eUtils,
e.g. entrez_pubmed_search.pl.

Note that other Entrez XML (e.g. PubChem) very similar.
'''
import os,sys,re,time,argparse,logging

from xml.etree import ElementTree
from xml.parsers import expat

from .. import util
from ..pubmed import Utils_XML

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='process PubMed XML (summaries or full), typically obtained via Entrez eUtils.')
  ops=['summary2tsv', 'summary2abstract', 'full2tsv', 'full2abstract', 'full2authorlist']
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--i", dest="ifile", required=True, help="input file, XML")
  parser.add_argument("--ids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--idfile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="max to return")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--odir", help="output directory")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile)

  pmids=[]
  if args.idfile:
    fin_ids = open(args.idfile)
    if not fin_ids: logging.error(f"Cannot open idfile: {args.idfile}")
    while True:
      line = fin_ids.readline()
      if not line: break
      try:
        ids.append(int(line.rstrip()))
      except:
        logging.error(f"Bad input ID: {line}")
        continue
    if args.verbose:
      logging.info(f"Input IDs: {len(ids)}")
    fin_ids.close()

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  try:
    tree = ElementTree.parse(fin)
  except Exception as e:
    logging.error(f"Failed to parse XML: {e}")

  if args.op == 'summary2tsv':
    Utils_XML.PubMed_Docsum2Tsv(tree, fout)

  elif args.op == 'full2tsv':
    Utils_XML.PubMed_Doc2Tsv(tree, fout)

  elif args.op == 'full2authorlist':
    Utils_XML.PubMed_Doc2AuthorList(tree, fout)

  elif args.op == 'summary2abstract':
    if not ids: parser.error('--summary2abstract requires --ids.')
    n_out=0;
    for id_this in ids:
      logging.info(f"{id_this:08d}")
      if args.odir: fout = open(f"{args.odir}/{id_this:08d}_title_and_abstract.txt", "w")
      ok = Utils_XML.PubMed_Docsum2AbstractText(tree, id_this, fout, args.verbose)
      if ok: n_out+=1
      else: logging.error(f"No title or abstract found for PMID: {id_this}")
      if odir: fout.close()
    logging.info(f"Abstracts found: {n_out}")

  elif args.op == 'full2abstract':
    if not ids: parser.error('--full2abstract requires --ids.')
    n_out=0;
    for id_this in ids:
      if args.verbose:
        logging.info(f"{id_this:08d}")
      if args.odir: fout = open(f"{args.odir}/{id_this:08d}_title_and_abstract.txt", "w")
      ok = Utils_XML.PubMed_Doc2AbstractText(tree, id_this, fout, args.verbose)
      if ok: n_out+=1
      else: logging.error(f"No title or abstract found for PMID: {id_this}")
      if args.odir: fout.close()
    logging.info('abstracts found: %d'%n_out)

  else:
    parser.error(f"Operation invalid: {args.op}.")
