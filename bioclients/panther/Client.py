#!/usr/bin/env python3
"""
PantherDb  REST API client
http://pantherdb.org/help/PANTHERhelp.jsp
"""
###
import sys,os,argparse,re,urllib.parse,logging
#
from ..util import rest
#
#############################################################################
def ListSpecies(base_url, fout):
  """
E.g.
Long Name	Short Name	NCBI Taxon Id
Homo sapiens	HUMAN	9606
  """
  n_species=0;
  url = base_url+'?type=organism'
  rval = rest.GetURL(url)
  if not rval:
    return
  for line in rval.splitlines():
    if not line: continue
    vals = re.split('\t', line)
    fout.write('\t'.join(vals)+'\n')
    n_species+=1
  logging.info('n_species = %d'%(n_species))

#############################################################################
### The following parameters are required.
### type - This refers to the search type and should be specified as "matchingOrtholog"
### inputOrganism - The organism/genome being queried by the search term(s)
### targetOrganism -  Target organism for ortholgos from search.  Multiple organisms can be specified, separated by commas
### orthologType - LDO or all - LDO will return only least diverged ortholog for each gene (single "best" ortholog), and all will return all orthologs if more than one
### searchTerm - query terms, these should optimally be Uniprot of MOD gene identifiers, but, other identifiers are supported such as gene symbols.  Maximum of 10 query terms can be submitted, separated by commas.
### For the inputOrganism and targetOrganism, the 5-letter Uniprot code is used, see the Short Name field on the summaryStats page for a list of available organisms and the associated codes.
### Example - http://www.pantherdb.org/webservices/ortholog.jsp?type=matchingOrtholog&inputOrganism=MOUSE&targetOrganism=HUMAN&orthologType=all&searchTerm=101816
### For each match, the following data are returned:
### If search term has no match in the input organism:
### <searchTerm>    "Search term not found in input organism <inputOrganism"
### If gene is found, but it has no ortholog in the database or orthologType specified is not found in the database:
### <searchTerm>     <matchedGene>    "No ortholog found in target organism <targetOrganism>"
#############################################################################
# SearchOrthologs(base_url, iorg, torg, ologtype, uniprot, fout, verbose):

#############################################################################
# Example /search.jsp?keyword=KEYWORD&type=getList&listType=LISTTYPE
# where KEYWORD is the search term and LISTTYPE = (gene|family|pathway|category)
def SearchFamilies(base_url, term, fout):
  url = base_url+'?type=getList&listType=family&keyword=%s'%(urllib.parse.quote(term))
  rval = rest.GetURL(url)
  if not rval:
    return
  logging.debug(rval)

#############################################################################
if __name__=='__main__':
  API_HOST="www.pantherdb.org"
  API_BASE_PATH="/webservices/garuda/search.jsp"
  parser = argparse.ArgumentParser(description='PantherDb REST API client utility')
  ops = ['list_species', 'search_families']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query term")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  if args.op=='list_species':
    ListSpecies(base_url, fout)

  elif args.op=='search_families':
    SearchFamilies(base_url, args.query, fout)

  else:
    parser.print_help()
