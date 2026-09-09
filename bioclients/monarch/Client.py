#!/usr/bin/env python
"""
Monarch REST client 

https://monarchinitiative.org/page/services
https://monarchinitiative.org/docs/files/api-js.html
https://github.com/monarch-initiative/owlsim-v3
https://github.com/monarch-initiative/monarch-analysis

/search	searches over ontology terms via OntoQuest
/autocomplete	proxy for vocbaulary services autocomplete
/disease	disease info or page
/phenotype	phenotype info or page
/simsearch	OwlSim search using search profile of ontology classes

https://monarchinitiative.org/disease/OMIM_127750.json
https://monarchinitiative.org/phenotype/HP_0000003.json
https://monarchinitiative.org/compare/OMIM:270400/NCBIGene:5156,OMIM:249000,OMIM:194050.json

We use OwlSim for semantic matching when comparing two entities (such as genes,
diseases, or genotypes) with sets of attributes (phenotypes). URLs are of the form
/compare/:x/:y.json
where x can be either an entity or a list of phenotypes and y can be a list of
entities and/or sets of phenotypes.
This wraps a call to getGroupwiseSimilarity(x,y) in OwlSim. This works such that
given a query id (such as a gene, genotype, disease), and one or more target
identifiers, it will map each to it's respective phenotypes, and perform an OwlSim
comparison of the query to each target. You are permitted to mix query and target
types. For example, your query can be a disease, and the target(s) be a list of
gene(s), disease(s), phenotype(s), and/or genotype(s). You can indicate to union the
phenotypes of either the query or the target with a plus "+". Only one entity may be
supplied for the query, whereas multiple target entities are allowed (delimited by a
comma).  For details on owlsim, see http://owlsim.org

Paths:
/compare/:id1/:id2
/compare/:id1/:id2,id3,...idN
/compare/:id1+:id2/:id3,:id4,...idN
/compare/:id1/:id2+:id3,:id4,:id5+:id6,...,:idN

IC = Information Content
LCS = Least Common Subsumers
See OwlSim docs and pubs.
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3653101/
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import monarch
#
##############################################################################
if __name__=='__main__':
  epilog='''\
compare: idAs vs idBs, OwlSim phenotype-based similarity
Entity: gene|disease|genotype
Examples:
OMIM:612528 (human disease),
HP:0005978 (human disease: T2DM),
DOID:1612 (human disease: breast cancer),
NCBIGene:7084 (human gene),
NCBIGene:5156 (human gene),
NCBIGene:3257 (human gene),
NCBIGene:26564 (mouse gene)
'''
  parser = argparse.ArgumentParser(description="Monarch Initiative REST client", epilog=epilog)
  ops = [
        "get_disease",
        "get_disease_relationships",
        "get_phenotype",
        "get_gene",
        "compare_phenotypes"
	]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input ID file")
  parser.add_argument("--idAs", help="input IDs (comma-separated)")
  parser.add_argument("--idBs", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=monarch.API_HOST)
  parser.add_argument("--api_base_path", default=monarch.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  idAs=[]; idBs=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): idAs.append(line.rstrip())
    fin.close()
  elif args.idAs:
    idAs = re.split(r'[,\s]+', args.idAs)
  logging.info("Input idAs: {len(idAs)}")
  if args.idBs:
    idBs = re.split(r'[,\s]+', args.idBs)
  logging.info("Input idBs: {len(idBs)}")

  if args.op=="get_disease":
    monarch.GetDisease(idAs, base_url, fout)

  elif args.op=="get_disease_relationships":
    monarch.GetDiseaseRelationships(idAs, base_url, fout)

  elif args.op=="get_phenotype":
    parser.error(f"Unimplemented operation: {args.op}")
    #monarch.GetPhenotype(idAs, base_url, fout)

  elif args.op=="get_gene":
    monarch.GetGene(idAs, base_url, fout)

  elif args.op=="compare_phenotypes":
    monarch.ComparePhenotypes(idAs, idBs, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
