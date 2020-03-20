#!/usr/bin/env python3
#############################################################################
'''
Functions for BRENDA API (SOAP) access.

"EC" refers to Enzyme Commission.  EC Numbers are assigned based on functionality,
the catalyzed reaction, not the protein itself.  Hence multiple proteins can 
exist for a given ECN or ECN+organism.

Default is human enzymes, organism="Homo sapiens".

Ref: http://www.brenda-enzymes.org/soap.php

Ref:	BRENDA: a resource for enzyme data and metabolic information.
	Schomburg I, Chang A, Hofmann O, Ebeling C, Ehrentreich F, Schomburg D.
	Trends Biochem Sci. 2002 Jan;27(1):54-6.
	http://www.ncbi.nlm.nih.gov/pubmed/11796225

Ref:	BRENDA in 2015: exciting developments in its 25th year of existence.
	Nucleic Acids Res. 2014 Nov 5. pii: gku1068. [Epub ahead of print]
	Chang A, Schomburg I, Placzek S, Jeske L, Ulbrich M, Xiao M, Sensen CW, Schomburg D.
	http://www.ncbi.nlm.nih.gov/pubmed/25378310.

Ref: http://en.wikipedia.org/wiki/Enzyme_inhibitor
'''
#############################################################################
import sys,os,time,argparse,logging,hashlib
import string,re,json

from .. import brenda

API_HOST = "www.brenda-enzymes.org"
API_BASE_PATH = "/soap"

#############################################################################
if __name__=='__main__':
  epilog='''\
OPERATIONS:
get = get record;
get_names = get enzyme names;
get_systematicname = get systematic enzyme name;
get_organism = get organism;
get_sequence = get sequence;
get_pdb = get PDB code;
get_ligands = get ligands code;
get_inhibitors = get enzyme inhibitors;
get_activators = get enzyme activating cpds;
get_kivalues = get enzyme Ki values;
get_kmvalues = get enzyme Km values;
get_references = get references;
get_inhibitordata = get inhibitor data (CSV);
get_sequencedata = get sequence data (CSV);
get_liganddata = get ligand data (CSV);
get_referencedata = get reference data (CSV);
list_all = list all ECNs (for specified organism);
list_fromsynonyms = list ECNs linked to synonyms;
list_frominhibitors = list ECNs linked to inhibitors;
list_fromactivators = list ECNs linked to activating cpds;
list_fromkivalues = list ECNs linked to Ki values;
list_fromkmvalues = list ECNs linked to Km values;
list_organisms = list all organisms;
Notes:
"get*" operations (require --ecn or --ifile).;
Km is concentration of substrate for half-max enzyme velocity, where velocity is rate of reaction product formation.;
Ki is concentration of substrate for half-max enzyme inhibition.
'''
  IDTYPE='ecn';
  ORGANISM='Homo sapiens';

  parser = argparse.ArgumentParser(description='BRENDA API client', epilog=epilog)
  ops = [ 'get', 'get_names', 'get_systematicname', 'get_organism', 'get_sequence', 'get_pdb', 'get_ligands', 'get_inhibitors', 'get_activators', 'get_kivalues', 'get_kmvalues', 'get_references', 'get_inhibitordata', 'get_sequencedata', 'get_liganddata', 'get_referencedata', 'list_all', 'list_fromsynonyms', 'list_frominhibitors', 'list_fromactivators', 'list_fromkivalues', 'list_fromkmvalues', 'list_organisms']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file of ECNs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--ecns", help="ECNs (comma-separated)")
  parser.add_argument("--organism", default=ORGANISM, help="organism (may be 'all')")
  parser.add_argument("--nmax", type=int, default=None, help="max NMAX ECNs")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st NSKIP ECNs")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_user", help="API username")
  parser.add_argument("--api_key", help="API key")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  API_BASE_URL='https://'+args.api_host+args.api_base_path

  SOAP_CLIENT = brenda.Utils.SoapAPIClient(API_BASE_URL)

  API_PARAMS = args.api_user+","+hashlib.sha256(args.api_key).hexdigest()

  organism = None if args.organism.lower()=='all' else args.organism

  if args.ofile:
    fout = open(ofile, "w")
  else:
    fout = sys.stdout

  ecns=[]
  if args.ifile:
    fin = open(args.ifile)
    i=0;
    while True:
      line = fin.readline()
      if not line: break
      i+=1
      if skip>0 and i<skip: continue
      ecns.append(line.rstrip())
      if nmax>0 and len(ecns)==nmax: break
    logging.info('input ECNs: %d'%(len(ecns)))
    fin.close()
  elif args.ecns:
    ecns = re.split(r'[,\s]+', args.ecns)

  t0=time.time()

  if args.op[:4]=="get_" and not ecns: parser.error("Operation %s requires --ecns or --ifile."%args.op)

  if args.op=="get":
    rstr = brenda.Utils.GetECN(SOAP_CLIENT, API_PARAMS, ecns)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_inhibitordata":
    brenda.Utils.GetInhibitorData(SOAP_CLIENT, API_PARAMS, ecns, args.organism, fout)

  elif args.op=="get_sequencedata":
    brenda.Utils.GetSequenceData(SOAP_CLIENT, API_PARAMS, ecns, args.organism, fout)

  elif args.op=="get_liganddata":
    brenda.Utils.GetLigandData(SOAP_CLIENT, API_PARAMS, ecns, args.organism, fout)

  elif args.op=="get_referencedata":
    brenda.Utils.GetReferenceData(SOAP_CLIENT, API_PARAMS, ecns, args.organism, fout)

  elif args.op=="get_names":
    rstr = brenda.Utils.GetNames(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results=brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_systematicname":
    rstr = brenda.Utils.GetSystematicName(SOAP_CLIENT, API_PARAMS, ecn)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_organism":
    rstr = brenda.Utils.GetOrganism(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_sequence":
    rstr = brenda.Utils.GetSequence(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_pdb":
    rstr = brenda.Utils.GetPdb(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_kivalues":
    rstr = brenda.Utils.GetKiValues(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    #logging.debug('rstr="%s"'%rstr)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_kmvalues":
    rstr = brenda.Utils.GetKmValues(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results=brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_inhibitors":
    rstr = brenda.Utils.GetInhibitors(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_activators":
    rstr = brenda.Utils.GetActivators(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_ligands":
    rstr = brenda.Utils.GetLigands(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="get_references":
    rstr = brenda.Utils.GetReferences(SOAP_CLIENT, API_PARAMS, ecns, args.organism)
    results = brenda.Utils.ParseResultDictString(rstr)
    brenda.Utils.OutputResultsDict(results, fout)

  elif args.op=="list_all":
    rstr = brenda.Utils.ListECNumbers(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="list_fromsynonyms":
    rstr = brenda.Utils.ListECNumbersFromSynonyms(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="list_frominhibitors":
    rstr = brenda.Utils.ListECNumbersFromInhibitors(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="list_fromactivators":
    rstr = brenda.Utils.ListECNumbersFromActivators(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="list_fromkivalues":
    rstr = brenda.Utils.ListECNumbersFromKiValue(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="list_fromkmvalues":
    rstr = brenda.Utils.ListECNumbersFromKmValue(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="list_organisms":
    rstr = brenda.Utils.ListOrganisms(SOAP_CLIENT, API_PARAMS)
    results = brenda.Utils.ParseResultListString(rstr)
    brenda.Utils.OutputResultsList(results, fout)

  elif args.op=="test":
    brenda.Utils.Test1(API_BASE_URL)

  else:
    parser.error("Invalid operation: %s"%args.op)


  logging.info('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

