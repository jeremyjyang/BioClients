#!/usr/bin/env python3
"""
Access to Ensembl BIOMART REST API.
https://m.ensembl.org/info/data/biomart/biomart_restful.html
"""
import sys,os,re,argparse,time,logging

from ... import ensembl
#
##############################################################################
def DemoXMLQuery(base_url, fout):
  xmltext = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "ensembl_gene_id_version" />
		<Attribute name = "entrezgene_id" />
		<Attribute name = "hgnc_id" />
		<Attribute name = "hgnc_symbol" />
	</Dataset>
</Query>
"""
  ensembl.biomart.Utils.XMLQuery(xmltext, base_url, fout)

##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(prog=sys.argv[0], description="Ensembl BIOMART REST API client", epilog="For XML query file format, see https://m.ensembl.org/info/data/biomart/biomart_restful.html#biomartxml")
  ops = ["xmlQuery", "ensg2ncbi", "ensg2hgnc", "ensg2ncbihgnc", "demo", "show_version"]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ixml", dest="ixmlfile", help="input file, XML query")
  parser.add_argument("--api_host", default=ensembl.biomart.API_HOST)
  parser.add_argument("--api_base_path", default=ensembl.biomart.API_BASE_PATH)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  t0=time.time()

  if args.op=='xmlQuery':
    if not args.ixmlfile:
      parser.error(f"Input XML file required for {args.op}")
      sys.exit(1)
    xmltext = open(args.ixmlfile).read()
    ensembl.biomart.Utils.XMLQuery(xmltext, base_url, fout)

  elif args.op=='ensg2ncbi':
    ensembl.biomart.Utils.ENSG2NCBI(base_url, fout)

  elif args.op=='ensg2hgnc':
    ensembl.biomart.Utils.ENSG2HGNC(base_url, fout)

  elif args.op=='ensg2ncbihgnc':
    ensembl.biomart.Utils.ENSG2NCBIHGNC(base_url, fout)

  elif args.op=='demo':
    DemoXMLQuery(base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')

  logging.info(('%s: elapsed time: %s'%(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
