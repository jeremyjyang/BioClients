#!/usr/bin/env python
##############################################################################
### slap_query.py - utility for SLAP REST API.
### 
### See: http://slapfordrugtargetprediction.wikispaces.com/API
### 
### Jeremy Yang
### 31 Mar 2017
##############################################################################
import sys,os,re,getopt,time
#
import slap_utils
#
API_HOST='cheminfov.informatics.indiana.edu'
API_BASE_PATH='/rest/Chem2Bio2RDF/slap'
#
##############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  usage='''\
%(PROG)s
required (one of):
	--d2t ....................... drug-to-target associations
	--t2d ....................... target-to-drug associations
	--dtp ....................... drug-target paths, subnet
	--dss ....................... drug-to-bio-similar-drugs search
	--dds ....................... drug-drug similarity
input:
	--cid CID ................... compound ID
	--tid TID ................... target ID (e.g. gene symbol)
	--cid2 CID2 ................. compound ID #2
	--cidfile CIDFILE ........... input file of query CIDs
	--tidfile TIDFILE ........... input file of query TIDs
output:
	--o OFILE ................... output file (CSV)
	--odir ODIR ................. output dir (for auto-named GraphML subnets)
options:
	--cid_skip SKIP ............. 
	--cid_nmax NMAX ............. 
	--tid_skip SKIP ............. 
	--tid_nmax NMAX ............. 
	--api_host HOST ............. [%(API_HOST)s]
	--api_base_path BASEPATH .... [%(API_BASE_PATH)s]
        --v[v[v]] ................... verbose [very [very]]
        --h ......................... this help

examples:
	--cid=5591 --tid=PPARG

'''%{'PROG':PROG,'API_HOST':API_HOST,'API_BASE_PATH':API_BASE_PATH}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  cid=''; cid2=''; cidfile=''; cid_skip=0; cid_nmax=0;
  tid=''; tidfile=''; tid_skip=0; tid_nmax=0;
  ofile=None; odir=None;
  ifile_graphml=None;
  ifile_csv=None;
  dtp=False; dds=False; dss=False; 
  d2t=False; 
  t2d=False; 
  info=False; 
  verbose=0;
  opts,pargs=getopt.getopt(sys.argv[1:],'',[
    'o=',
    'cid=', 'cidfile=',
    'cid_skip=', 'cid_nmax=',
    'tid=', 'tidfile=',
    'tid_skip=', 'tid_nmax=',
    'cid2=',
    'ofile=', 'odir=',
    'dtp', 'dds', 'dss', 'd2t', 't2d',
    'api_host=', 'api_base_path=',
    'help','v','vv','vvv'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--cid': cid=val
    elif opt=='--cid2': cid2=val
    elif opt=='--cidfile': cidfile=val
    elif opt=='--cid_skip': cid_skip=int(val)
    elif opt=='--cid_nmax': cid_nmax=int(val)
    elif opt=='--tid': tid=val
    elif opt=='--tidfile': tidfile=val
    elif opt=='--tid_skip': tid_skip=int(val)
    elif opt=='--tid_nmax': tid_nmax=int(val)
    elif opt=='--o': ofile=val
    elif opt=='--odir': odir=val
    elif opt=='--dtp': dtp=True
    elif opt=='--d2t': d2t=True
    elif opt=='--t2d': t2d=True
    elif opt=='--dds': dds=True
    elif opt=='--dss': dss=True
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s\n%s'%(opt,usage))

  API_BASE_URI='http://'+API_HOST+API_BASE_PATH

  cids=[]
  if cidfile:
    fin=open(cidfile)
    if not fin: ErrorExit('ERROR: failed to open input file: %s'%cidfile)
    while True:
      line=fin.readline()
      if not line: break
      cids.append(line.strip())
  elif cid:
    cids=[cid]

  tids=[]
  if tidfile:
    fin=open(tidfile)
    if not fin: ErrorExit('ERROR: failed to open input file: %s'%tidfile)
    while True:
      line=fin.readline()
      if not line: break
      tids.append(line.strip())
  elif tid:
    tids=[tid]

  if ofile:
    fout=open(ofile,"w+")
    if not fout: ErrorExit('ERROR: failed to open output file: %s'%ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if d2t:
    if not cids: ErrorExit('CID[s] required.\n%s'%usage)
    slap_utils.Drug2Targets(cids,API_BASE_URI,fout,verbose)

  elif t2d:
    if not tids: ErrorExit('TID[s] required.\n%s'%usage)
    slap_utils.Target2Drugs(tids,API_BASE_URI,fout,verbose)

  elif dtp:
    if not (cids and tids): ErrorExit('CID[s] and TID[s] required.\n%s'%usage)
    slap_utils.DrugTargetPaths(cids,tids,API_BASE_URI,cid_skip,cid_nmax,tid_skip,tid_nmax,fout,odir,verbose)

  elif dss:
    slap_utils.Drug2BioSimilarDrugs(cids,API_BASE_URI,fout,verbose)

  elif dds:
    if not cid2: ErrorExit('--cid2 required.\n%s'%usage)
    slap_utils.DDSimilarity(cid,cid2,API_BASE_URI,fout,verbose)

  else:
    ErrorExit('No operation specified.\n%s'%(usage))
    

  if verbose:
    print >>sys.stderr, ('%s: elapsed time: %s'%(PROG,time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))

  if ofile: fout.close()
