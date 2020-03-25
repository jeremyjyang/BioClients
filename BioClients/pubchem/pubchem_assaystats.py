#!/usr/bin/env python
#############################################################################
### pubchem_assaystats.py - From PubChem PUG REST API, determine
### activity stats for compounds.
### 
### Input: smiles and CIDs
### Output (1):
###   SMILES CID SID aTested aActive wTested wActive 
###     where:
###   aTested - how many assays where that cpd has been tested
###   aActive - how many assays where that cpd has been tested active
###   wTested - how many samples (wells) with that cpd have been tested
###   wActive - how many samples (wells) with that cpd have been tested active
### 
### Output (2): activity file, each line:
###   CID SID AID Outcome
###     where:
###   1 = inactive
###   2 = active
###   3 = inconclusive
###   4 = unspecified
###   5 = probe
###   multiple, differing 1, 2 or 3 = discrepant
###   not 4 = tested
###
### ref: http://pubchem.ncbi.nlm.nih.gov/pug_rest/
#############################################################################
### Problem: How can this find multiple SIDs for one CID?  PC REST API seems
### to disallow this possibility.
#############################################################################
### Jeremy Yang
### 13 Aug 2014
#############################################################################
import os,sys,re,getopt,time

import time_utils
import pubchem_utils

PROG=os.path.basename(sys.argv[0])
#
API_HOST='pubchem.ncbi.nlm.nih.gov'
API_BASE_PATH='/rest/pug'
#
#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - (PUG REST client)

required:
	--i INMOLS ................ mols w/ cids (smiles)
	--o OUTMOLS ............... output mols with data (smiles)
	--o_act OUTACTIVITY ....... output activity data (PubChem outcome codes)
      or
	--cid CID ................. report on one CID

options:
	--aids AIDS ............... list of AIDs to select
	--aidfile AIDFILE ......... file of AIDs to select
	--cidfile CIDFILE ......... file of CIDs to select
	--api_host HOST ........... [%(API_HOST)s]
	--api_base_path PATH ...... [%(API_BASE_PATH)s]
	--nmax NMAX ............... max N CIDs
	--nskip NSKIP ............. skip N CIDs
	--v[v[v]] ................. verbose [very [very]]
	--h ....................... this help
'''%{'PROG':PROG,'API_HOST':API_HOST,'API_BASE_PATH':API_BASE_PATH}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  verbose=0;
  ifile_mol=None; ofile_mol=None; ofile_act=None; 
  aids=None; aidfile=None; cidfile=None; cid_query=None;
  use_sids=False;
  nmax=0; nskip=0;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','vvv',
  'aids=','aidfile=','o=','o_act=','i=',
  'api_host=','api_base_path=',
  'cid=','cidfile=','use_sids','nmax=','nskip='])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile_mol=val
    elif opt=='--o': ofile_mol=val
    elif opt=='--o_act': ofile_act=val
    elif opt=='--aids': aids=val
    elif opt=='--aidfile': aidfile=val
    elif opt=='--cidfile': cidfile=val
    elif opt=='--cid': cid_query=int(val)
    elif opt=='--use_sids': use_sids=True
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
  aidhash={};

  aidset=None
  if aids:
    aidset={}
    for val in re.split('[\s,]+',aids):
      if not val.strip(): continue
      try:
        aid=int(val.strip())
        aidset[aid]=True
      except:
        ErrorExit(('--aids arg not parseable: "%s"\n'%val)+usage)
  if aidfile:
    aidset={}
    f=file(aidfile)
    if not f:
      ErrorExit('cannot open: %s'%aidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      try:
        aid=int(line.strip())
        aidset[aid]=True
      except:
        print >>sys.stderr, 'Warning: skipping unparseable AID file line: "%s"'%(line)
        continue

  if cid_query:
    smiles=pubchem_utils.Cid2Smiles(BASE_URI,cid_query,0)
    mol_found,mol_active,n_sam,n_sam_active = pubchem_utils.GetCpdAssayStats(BASE_URI,cid_query,smiles,aidset,sys.stderr,sys.stdout,aidhash,verbose)
    sys.exit()

  if not (ifile_mol):
    ErrorExit('--i file required\n'+usage)
  if not ofile_mol:
    ErrorExit('--o output file required\n'+usage)

  fin_mol=file(ifile_mol)
  if not fin_mol: ErrorExit('cannot open: %s'%ifile_mol)
  fout_mol=file(ofile_mol,'w')
  if not fout_mol: ErrorExit('cannot open: %s'%ofile_mol)

  if ofile_act:
    fout_act=file(ofile_act,'w')
    if not fout_act: ErrorExit('cannot open: %s'%ofile_act)
  else:
    fout_act=sys.stdout

  cidset={}	## use a hash for speed (could be many cids)
  if cidfile:
    f=file(cidfile)
    if not f:
      ErrorExit('cannot open: %s'%cidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      line=re.sub('\s.*$','',line)
      cidset[int(line.strip())]=True
  if len(cidset.keys())==0: cidset=None

  t0=time.time()

  fout_mol.write("#smiles cid sid aTested aActive sTested sActive\n")
  fout_act.write("cid,sid,aid,outcome\n")

  ### For each CID, query using URI like:
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1001/assaysummary/CSV
  ### which returns CSV with fields:
  ### AID,"Panel Member ID","SID","CID","Activity Outcome","Activity Value [uM]","Activity Type","Assay Name","Target GI","Target Name","Assay Type","PubMed ID"

  ### For each cid, generate stats.

  n_mol=0; cid2smi={}; 
  n_mol_active=0;
  n_sam_total=0;
  n_sam_total_active=0;
  n_cid_notfound=0
  #http_errs={};
  while True:
    line=fin_mol.readline()
    if not line: break
    n_mol+=1
    if nskip>0 and n_mol<=nskip:
      continue
    line=line.rstrip()
    fields=line.split()
    if len(fields)<2:
      print >>sys.stderr, 'Warning: skipping mol without CID [%d]:'%(n_mol,line)
      fout_mol.write("%s\n"%line)
      continue
    smiles=fields[0]
    cid=int(fields[1])

    mol_found,mol_active,n_sam,n_sam_active = pubchem_utils.GetCpdAssayStats(BASE_URI,cid,smiles,aidset,fout_mol,fout_act,aidhash,verbose)
    if mol_found:
      if mol_active:
        n_mol_active+=1
      n_sam_total+=n_sam
      n_sam_total_active+=n_sam_active
    else:
      n_cid_notfound+=1

    if 0==(n_mol%100):
      if nskip>0: print >>sys.stderr, ("n = %d ;"%(n_mol-nskip)),
      print >>sys.stderr, ("n_mol = %d ; elapsed time: %s\t[%s]"%(n_mol,time_utils.NiceTime(time.time()-t0),time.asctime()))
    if nmax>0 and n_mol-nskip>=nmax:
      break

  fout_mol.close()
  fout_act.close()

  print >>sys.stderr, 'mols read: %d'%(n_mol)
  print >>sys.stderr, 'total active mols: %d'%(n_mol_active)
  print >>sys.stderr, 'total samples: %d'%(n_sam_total)
  print >>sys.stderr, 'total active samples: %d'%(n_sam_total_active)
  id='CID'
#  if use_sids: id='SID'
  print >>sys.stderr, '%s: number of assays: %d'%(PROG,len(aidhash))
  if aidset:
    print >>sys.stderr, 'assays in allowed set: %d'%(len(aidset))
  print >>sys.stderr, '%s: number of %ss not found in any assay: %d'%(PROG,id,n_cid_notfound)
  #errcodes=http_errs.keys()
  #errcodes.sort()
  #for code in errcodes:
  #  print >>sys.stderr, 'count, http error code %d: %3d'%(code,http_errs[code])
  print >>sys.stderr, ("total elapsed time: %s"%(time_utils.NiceTime(time.time()-t0)))
  print >>sys.stderr, time.asctime()

