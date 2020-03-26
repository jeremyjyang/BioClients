#!/usr/bin/env python
#############################################################################
### pubchem_assaydata.py - From PubChem PUG REST API, get
### activity data for specified assays and compounds.
### 
### Input: CIDs and AIDs
### 
### Output (2): activity file, each line:
###   CID SID AID ...
###     where:
###
### ref: http://pubchem.ncbi.nlm.nih.gov/pug_rest/
#############################################################################
### Problem: How can this find multiple SIDs for one CID?  PC REST API seems
### to disallow this possibility.
#############################################################################
### OUTCOME_CODES = { 'inactive':1, 'active':2, 'inconclusive':3, 'unspecified':4, 'probe':5 }
#############################################################################
import os,sys,re,getopt,time

from .. import pubchem

PROG=os.path.basename(sys.argv[0])
#
API_HOST='pubchem.ncbi.nlm.nih.gov'
API_BASE_PATH='/rest/pug'
#
#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - PUG REST client

required (one of):
  --cids CIDS ............... list of CIDs to select
  --cidfile CIDFILE ......... file of CIDs to select

required (one of):
  --aids AIDS ............... list of AIDs to select
  --aidfile AIDFILE ......... file of AIDs to select

options:
  --o OUTFILE ............... output activity data
  --nmax NMAX
  --nskip NSKIP
  --api_host HOST ................. [%(API_HOST)s]
  --api_base_path PATH ............ [%(API_BASE_PATH)s]
  --v[v[v]] ................. verbose [very] 
  --h ....................... this help
'''%{'PROG':PROG,'API_HOST':API_HOST,'API_BASE_PATH':API_BASE_PATH}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  verbose=0;
  ofile=None; 
  aids=[];
  aidfile=None;
  cids=[];
  cidfile=None;
  nmax=0; nskip=0;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','vvv',
  'aids=','aidfile=','o=',
  'api_host=','api_base_path=',
  'cids=','cidfile=','nmax=','nskip='])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile_mol=val
    elif opt=='--o': ofile=val
    elif opt=='--aids': aids=map(lambda x:int(x),re.split('[\s,]+',val))
    elif opt=='--cids': cids=map(lambda x:int(x),re.split('[\s,]+',val))
    elif opt=='--aidfile': aidfile=val
    elif opt=='--cidfile': cidfile=val
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--nskip': nskip=int(val)
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s'%val)

  BASE_URI='http://'+API_HOST+API_BASE_PATH

  print >>sys.stderr, time.asctime()

  if ofile:
    fout=file(ofile,'w')
    if not fout: ErrorExit('cannot open: %s'%ofile)
  else:
    fout=sys.stdout

  aidset = set(aids) if aids else set()
  if aidfile:
    f=file(aidfile)
    if not f:
      ErrorExit('cannot open: %s'%aidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      aid=int(line.strip())
      aidset.add(aid)

  if cidfile:
    f=file(cidfile)
    if not f:
      ErrorExit('cannot open: %s'%cidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      cid=int(line.strip())
      cids.append(cid)

  if not (aidset and cids):
    ErrorExit('CIDs and AIDs required: \n'+usage)

  if verbose:
    print >>sys.stderr, 'AID count: %d'%len(aidset)
    print >>sys.stderr, 'CID count: %d'%len(cids)

  t0=time.time()

  ### For each CID, query using URI like:
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1001/assaysummary/CSV
  ### which returns CSV with fields:
  ### AID,"Panel Member ID","SID","CID","Activity Outcome","Activity Value [uM]","Activity Type","Assay Name","Target GI","Target Name","Assay Type","PubMed ID"

  ### For each cid, get activity data.
  fout.write("CID,SID,AID,ActivityOutcome,ActivityValue\n")

  n_mol=0;
  n_cid_notfound=0;
  for cid in cids:
    n_mol+=1
    if nskip>0 and n_mol<=nskip:
      continue

    mol_found = pubchem.Utils.GetCpdAssayData(BASE_URI,cid,aidset,fout,verbose)

    n_cid_notfound += 0 if mol_found else 1

    if 0==(n_mol%100):
      if nskip>0: print >>sys.stderr, ("n = %d ;"%(n_mol-nskip)),
      print >>sys.stderr, ("n_mol = %d ; elapsed time: %s\t[%s]"%(n_mol, (time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))), time.asctime()))
    if nmax>0 and n_mol-nskip>=nmax:
      break

  fout.close()

  print >>sys.stderr, 'AID count: %d'%(len(aidset))
  print >>sys.stderr, 'CID count: %d'%(len(cids))
  print >>sys.stderr, '%s: number of CIDs not found in any assay: %d'%(PROG,n_cid_notfound)
  print >>sys.stderr, ("%s: total elapsed time: %s"%(PROG, (time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
  print >>sys.stderr, time.asctime()

