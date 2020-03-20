#!/usr/bin/env python3
### TO DO: Port to Py3.
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
import sys,os,time,getopt,codecs,hashlib
import string,re,json

from .. import brenda


from SOAPpy import WSDL ## for extracting URL of endpoint from WSDL file
from SOAPpy import SOAPProxy

API_HOST = "www.brenda-enzymes.org"
API_BASE_PATH = "/soap"

API_USR="jjyang@salud.unm.edu"
API_PW="HepEicDatewJiH9"

#############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  idtype='ecn';
  organism='Homo sapiens';
  usage='''\
%(PROG)s - BRENDA client

operations (require --ecn or --ecnfile):
        --get ....................... get record
        --getnames .................. get enzyme names
        --getsystematicname ......... get systematic enzyme name
        --getorganism ............... get organism
        --getsequence ............... get sequence
        --getpdb .................... get PDB code
        --getligands ................ get ligands code
        --getinhibitors ............. get enzyme inhibitors
        --getactivators ............. get enzyme activating cpds
        --getkivalues ............... get enzyme Ki values
        --getkmvalues ............... get enzyme Km values
        --getreferences ............. get references
        --get_inhibitordata ......... get inhibitor data (CSV)
        --get_sequencedata .......... get sequence data (CSV)
        --get_liganddata ............ get ligand data (CSV)
        --get_referencedata ......... get reference data (CSV)
operations:
        --list_all .................. list all ECNs (for specified organism)
        --list_fromsynonyms ......... list ECNs linked to synonyms
        --list_frominhibitors ....... list ECNs linked to inhibitors
        --list_fromactivators ....... list ECNs linked to activating cpds
        --list_fromkivalues ......... list ECNs linked to Ki values
        --list_fromkmvalues ......... list ECNs linked to Km values
        --listorganisms ............. list all organisms
params:
        --ecn ECN ................... ECN
        --ecnfile ECNFILE ........... input file of ECNs
        --skip NSKIP ................ skip 1st NSKIP ECNs
        --nmax NMAX ................. max NMAX ECNs
        --organism ORG .............. organism [%(ORGANISM)s] (may be "all")
        --o OFILE ................... output file [stdout]
        --api_host HOST ............. [%(API_HOST)s]
        --api_base_path PATH ........ [%(API_BASE_PATH)s]
options:
        --v[v[v]] ................... verbose [very [very]]
        --h ......................... this help

Notes:
Km is concentration of substrate for half-max enzyme velocity, where velocity is rate of reaction product formation.
Ki is concentration of substrate for half-max enzyme inhibition.
'''%{   'PROG':PROG,
        'API_HOST':API_HOST,
        'API_BASE_PATH':API_BASE_PATH,
        'ORGANISM':organism
        }

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  get=False;
  getnames=False;
  get_inhibitordata=False;
  get_sequencedata=False;
  get_liganddata=False;
  get_referencedata=False;
  getsystematicname=False;
  getorganism=False;
  getsequence=False;
  getpdb=False;
  getligands=False;
  getreferences=False;
  getinhibitors=False;
  getactivators=False;
  getkivalues=False;
  getkmvalues=False;
  test=False;
  verbose=0;
  skip=0; nmax=0;
  ecn=None;
  ecnfile=None;
  uniprot=None;
  list_all=False;
  listorganisms=False;
  list_fromsynonyms=False;
  list_frominhibitors=False;
  list_fromactivators=False;
  list_fromkivalues=False;
  list_fromkmvalues=False;
  ofile=None;

  opts,pargs=getopt.getopt(sys.argv[1:],'',['o=',
    'get',
    'getnames',
    'get_inhibitordata',
    'get_sequencedata',
    'get_liganddata',
    'get_referencedata',
    'getsystematicname',
    'getorganism',
    'getsequence',
    'getpdb',
    'getligands',
    'getreferences',
    'getinhibitors',
    'getactivators',
    'getkivalues',
    'getkmvalues',
    'test',
    'ecn=',
    'ecnfile=',
    'uniprot=',
    'list_all',
    'listorganisms',
    'list_fromsynonyms',
    'list_frominhibitors',
    'list_fromactivators',
    'list_fromkivalues',
    'list_fromkmvalues',
    'organism=',
    'skip=', 'nmax=',
    'api_host=',
    'api_base_path=',
    'help','v','vv','vvv'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--o': ofile=val
    elif opt=='--test': test=True
    elif opt=='--get': get=True
    elif opt=='--getnames': getnames=True
    elif opt=='--get_inhibitordata': get_inhibitordata=True
    elif opt=='--get_sequencedata': get_sequencedata=True
    elif opt=='--get_liganddata': get_liganddata=True
    elif opt=='--get_referencedata': get_referencedata=True
    elif opt=='--getsystematicname': getsystematicname=True
    elif opt=='--getorganism': getorganism=True
    elif opt=='--getsequence': getsequence=True
    elif opt=='--getpdb': getpdb=True
    elif opt=='--getligands': getligands=True
    elif opt=='--getreferences': getreferences=True
    elif opt=='--getinhibitors': getinhibitors=True
    elif opt=='--getactivators': getactivators=True
    elif opt=='--getkivalues': getkivalues=True
    elif opt=='--getkmvalues': getkmvalues=True
    elif opt=='--ecn': ecn=val
    elif opt=='--ecnfile': ecnfile=val
    elif opt=='--uniprot': uniprot=val
    elif opt=='--list_all': list_all=True
    elif opt=='--list_fromsynonyms': list_fromsynonyms=True
    elif opt=='--list_frominhibitors': list_frominhibitors=True
    elif opt=='--list_fromactivators': list_fromactivators=True
    elif opt=='--list_fromkivalues': list_fromkivalues=True
    elif opt=='--list_fromkmvalues': list_fromkmvalues=True
    elif opt=='--listorganisms': listorganisms=True
    elif opt=='--organism': organism=val
    elif opt=='--skip': skip=int(val)
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s\n%s'%(opt,usage))

  API_BASE_URL='http://'+API_HOST+API_BASE_PATH
  SOAP_CLIENT = SOAPProxy(API_BASE_URL+"/brenda_server.php")

  API_PARAMS=API_USR+","+hashlib.sha256(API_PW).hexdigest()

  if organism.lower()=='all': organism = None

  if ofile:
    fout=codecs.open(ofile,"w","utf8","replace")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=codecs.getwriter('utf8')(sys.stdout,errors="replace")

  ecns=[]
  if ecnfile:
    fin=open(ecnfile)
    if not fin: ErrorExit('ERROR: cannot open ecnfile: %s'%ecnfile)
    i=0;
    while True:
      line=fin.readline()
      if not line: break
      i+=1
      if skip>0 and i<skip: continue
      ecns.append(line.rstrip())
      if nmax>0 and len(ecns)==nmax: break
    if verbose:
      print >>sys.stderr, '%s: input ECNs: %d'%(PROG,len(ecns))
    fin.close()
    if ecns: ecn=ecns[0]
  elif ecn:
    ecns.append(ecn)

  t0=time.time()

  if get:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetECN(SOAP_CLIENT,API_PARAMS,ecn,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif get_inhibitordata:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    GetInhibitorData(SOAP_CLIENT,API_PARAMS,ecns,organism,fout,verbose)

  elif get_sequencedata:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    GetSequenceData(SOAP_CLIENT,API_PARAMS,ecns,organism,fout,verbose)

  elif get_liganddata:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    GetLigandData(SOAP_CLIENT,API_PARAMS,ecns,organism,fout,verbose)

  elif get_referencedata:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    GetReferenceData(SOAP_CLIENT,API_PARAMS,ecns,organism,fout,verbose)

  elif getnames:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetNames(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getsystematicname:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetSystematicName(SOAP_CLIENT,API_PARAMS,ecn,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getorganism:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetOrganism(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getsequence:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetSequence(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getpdb:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetPdb(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getkivalues:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.or --ecnfile.")
    rstr = GetKiValues(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    #print >>sys.stderr, 'DEBUG: rstr="%s"'%rstr  #DEBUG
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getkmvalues:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetKmValues(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getinhibitors:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetInhibitors(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getactivators:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetActivators(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getligands:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetLigands(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif getreferences:
    if not ecn: ErrorExit("requires --ecn or --ecnfile.")
    rstr = GetReferences(SOAP_CLIENT,API_PARAMS,ecn,organism,verbose)
    results=ParseResultDictString(rstr)
    OutputResultsDict(results,fout)

  elif list_all:
    rstr = ListECNumbers(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif list_fromsynonyms:
    rstr = ListECNumbersFromSynonyms(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif list_frominhibitors:
    rstr = ListECNumbersFromInhibitors(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif list_fromactivators:
    rstr = ListECNumbersFromActivators(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif list_fromkivalues:
    rstr = ListECNumbersFromKiValue(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif list_fromkmvalues:
    rstr = ListECNumbersFromKmValue(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif listorganisms:
    rstr = ListOrganisms(SOAP_CLIENT,API_PARAMS,verbose)
    results=ParseResultListString(rstr)
    OutputResultsList(results,fout)

  elif test:
    Test1(API_BASE_URL)

  else:
    ErrorExit("No operation specified.")

  if ofile:
    fout.close()

  if verbose:
    print >>sys.stderr, ('%s: elapsed time: %s'%(PROG,time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))

