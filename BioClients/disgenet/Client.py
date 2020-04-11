#!/usr/bin/env python3
"""
 https://www.disgenet.org/api/
 https://www.disgenet.org/dbinfo
 DisGeNET Disease Types : disease, phenotype, group
 DisGeNET Metrics:
   GDA Score
   VDA Score
   Disease Specificity Index (DSI)
   Disease Pleiotropy Index (DPI)
   Evidence Level (EL)
   Evidence Index (EI)
 GNOMAD pLI (Loss-of-function Intolerant)

 DisGeNET Association Types:
   Therapeutic
   Biomarker
   Genomic Alterations
   GeneticVariation
   Causal Mutation
   Germline Causal Mutation
   Somatic Causal Mutation
   Chromosomal Rearrangement
   Fusion Gene
   Susceptibility Mutation
   Modifying Mutation
   Germline Modifying Mutation
   Somatic Modifying Mutation
   AlteredExpression
   Post-translational Modification

 MeSH Disease classes:
 C01 - Bacterial Infections and Mycoses
 C02 - Virus Diseases
 C03 - Parasitic Diseases
 C04 - Neoplasms
 C05 - Musculoskeletal Diseases
 C06 - Digestive System Diseases
 C07 - Stomatognathic Diseases
 C08 - Respiratory Tract Diseases
 C09 - Otorhinolaryngologic Diseases
 C10 - Nervous System Diseases
 C11 - Eye Diseases
 C12 - Male Urogenital Diseases
 C13 - Female Urogenital Diseases and Pregnancy Complications
 C14 - Cardiovascular Diseases
 C15 - Hemic and Lymphatic Diseases
 C16 - Congenital, Hereditary, and Neonatal Diseases and Abnormalities
 C17 - Skin and Connective Tissue Diseases
 C18 - Nutritional and Metabolic Diseases
 C19 - Endocrine System Diseases
 C20 - Immune System Diseases
 C21 - Disorders of Environmental Origin
 C22 - Animal Diseases
 C23 - Pathological Conditions, Signs and Symptoms
 C24 - Occupational Diseases
 C25 - Substance-Related Disorders
 C26 - Wounds and Injuries
 F01 - Behavior and Behavior Mechanisms
 F02 - Psychological Phenomena
 F03 - Mental Disorders
"""
###
import sys,os,re,argparse,time,json,logging
#
from ..util import rest_utils
#
API_HOST='www.disgenet.org'
API_BASE_PATH='/api'
#
##############################################################################
def GetDiseaseGDAs(base_url, ids, source, fout):
  tags=[]; n_ga=0;
  for id_this in ids:
    url = base_url+"/gda/disease/%s?source=%s"%(id_this, source)
    try:
      rval = rest_utils.GetURL(url, parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))
      continue
    gas = rval
    for ga in gas:
      if not tags:
        tags = [tag for tag in ga.keys() if type(ga[tag]) not in (list,dict)]
        fout.write('\t'.join(tags)+'\n')
      vals=[str(ga[tag]) if tag in ga else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_ga+=1
    #logging.debug(json.dumps(rval, indent=2, sort_keys=True))
  logging.info("IDs: %d; GAs: %d"%(len(ids), n_ga))

##############################################################################
def GetGeneGDAs(base_url, ids, source, fout):
  '''NCBI Entrez Identifier or HGNC Symbol'''
  tags=[]; n_ga=0;
  for id_this in ids:
    url = base_url+"/gda/gene/%s?source=%s"%(id_this, source)
    try:
      rval = rest_utils.GetURL(url, parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))
      continue
    gas = rval
    for ga in gas:
      if not tags:
        tags = [tag for tag in ga.keys() if type(ga[tag]) not in (list,dict)]
        fout.write('\t'.join(tags)+'\n')
      vals=[str(ga[tag]) if tag in ga else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_ga+=1
  logging.info("IDs: %d; GAs: %d"%(len(ids), n_ga))

##############################################################################
def GetUniprotGDAs(base_url, ids, source, fout):
  '''NCBI Entrez Identifier or HGNC Symbol'''
  tags=[]; n_ga=0;
  for id_this in ids:
    url = base_url+"/gda/uniprot/%s?source=%s"%(id_this, source)
    try:
      rval = rest_utils.GetURL(url, parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))
      continue
    gas = rval
    for ga in gas:
      if not tags:
        tags = [tag for tag in ga.keys() if type(ga[tag]) not in (list,dict)]
        fout.write('\t'.join(tags)+'\n')
      vals=[str(ga[tag]) if tag in ga else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_ga+=1
  logging.info("IDs: %d; GAs: %d"%(len(ids), n_ga))

##############################################################################
def GetDiseases(base_url, source, dtype, dclass, nmax, fout):
  tags=[]; n_out=0;
  url = base_url+"/disease/source/%s?format=tsv&limit=%d"%(source, nmax)
  try:
    dss = rest_utils.GetURL(url, parse_json=False)
    #logging.debug(dss)
  except Exception as e:
    logging.error('%s'%(e))
  for line in dss.splitlines():
    fout.write(line+'\n')
    n_out+=1
  logging.info("Diseases: %d"%(n_out-1))

##############################################################################
if __name__=='__main__':
  SOURCES = ["CURATED", "INFERRED", "ANIMAL_MODELS", "ALL", "BEFREE", "CGI", "CLINGEN", "CLINVAR, CTD_human", "CTD_mouse", "CTD_rat", "GENOMICS_ENGLAND", "GWASCAT", "GWASDB", "HPO", "LHGDN", "MGD", "ORPHANET", "PSYGENET", "RGD", "UNIPROT", "ALL"]
  DISEASE_TYPES = ["disease", "phenotype", "group"]
  DISEASE_CLASSES = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "F01", "F02", "F03"]
  parser = argparse.ArgumentParser(
        description='Disgenet (www.disgenet.org) REST API client utility',
        epilog='''\
Example IDs:
	C0019829 (UMLS CUI)
''')
  ops = ['get_diseases', 'get_Disease_GDAs', 'get_Gene_GDAs', 'get_Uniprot_GDAs']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated (Disease UMLS CUIs, or Gene EntrezIDs, HGNC symbols, or UniProtIDs)")
  parser.add_argument("--i", dest="ifile", help="input file of IDs")
  parser.add_argument("--source", choices=SOURCES, default="ALL", help="default=ALL")
  parser.add_argument("--disease_type", choices=DISEASE_TYPES, default="disease")
  parser.add_argument("--disease_class", choices=DISEASE_CLASSES, help="MeSH disease class")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--nmax", type=int, default=1000, help="max results")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout=open(args.ofile,"w")
    if not fout: parser.error('cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('cannot open: %s'%args.ifile)
    ids = [];
    while True:
      line=fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    logging.info('input queries: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op == "get_Disease_GDAs":
    GetDiseaseGDAs(base_url, ids, args.source, fout)

  elif args.op == "get_Gene_GDAs":
    GetGeneGDAs(base_url, ids, args.source, fout)

  elif args.op == "get_Uniprot_GDAs":
    GetUniprotGDAs(base_url, ids, args.source, fout)

  elif args.op == "get_diseases":
    GetDiseases(base_url, args.source, args.disease_type, args.disease_class, args.nmax, fout)

  else:
    parser.error("No operation specified.")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
