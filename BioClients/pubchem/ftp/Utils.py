#!/usr/bin/env python
#############################################################################
### pubchem_ftp_utils.py - For processing PubChem FTP files.
### 
### PUBCHEM_ACTTIVITY_OUTCOME values:
###  Inactive:1, Active:2, Inconclusive:3, Unspecified:4, Probe:5
### 
### Jeremy J Yang
###  14 Feb 2017
#############################################################################
import sys,os,re,time,getopt,csv
import urllib,urllib2,tempfile


FTPURL='ftp://ftp.ncbi.nlm.nih.gov/pubchem'
POLL_WAIT=10
MAX_WAIT=600

OUTCOME_CODES = {'inactive':1,'active':2,'inconclusive':3,'unspecified':4,'probe':5}

#############################################################################
def UrlOpen(url,ntries=20,poll_wait=10,verbose=0):
  ### To recover from FTP timeouts:
  fin=None
  for i in range(ntries):
    try:
      fin=urllib2.urlopen(url)
      break
    except IOError, e:
      print >>sys.stderr,'IOError: %s'%e
      time.sleep(poll_wait)
  if not fin:
    print >>sys.stderr,'ERROR: failed download, %d tries, quitting...'%ntries
    sys.exit(1)
  return fin

#############################################################################
def GetUrl(url,fout,ntries=20,poll_wait=10,verbose=0):
  if verbose>1: 
    print >>sys.stderr,'%s'%url
  fin=UrlOpen(url,ntries,poll_wait,verbose)
  nbytes=0
  while True:
    buff=fin.read(1024)
    if not buff: break
    fout.write(buff)
    nbytes+=len(buff)
  fin.close()
  return nbytes

#############################################################################
def GetUrlSDF2SMI(url,fout,ntries=20,poll_wait=10,verbose=0):
  '''Get PubChem SDF.GZ, convert to SMILES using the SD tag PUBCHEM_OPENEYE_CAN_SMILES
or PUBCHEM_OPENEYE_ISO_SMILES, and PUBCHEM_COMPOUND_CID or PUBCHEM_COMPOUND_SID for name.'''
  import openeye.oechem as oechem

  def HandleOEErrors(oeerrs,nowarn):
    errstr=oeerrs.str()
    for line in errstr.split('\n'):
      if not line.rstrip(): continue
      if re.search('Warning',line,re.I) and nowarn: continue
      sys.stderr.write("%s\n"%line)
    oeerrs.clear()

  fout_tmp = tempfile.NamedTemporaryFile(prefix='pubchem_ftp_',suffix='.sdf.gz',delete=False)
  GetUrl(url,fout_tmp,ntries,poll_wait,verbose)
  fpath_tmp=fout_tmp.name
  #print >>sys.stderr,'DEBUG: fpath_tmp = %s'%fpath_tmp
  fout_tmp.close()

  ims=oechem.oemolistream(fpath_tmp)
  ims.SetFormat(oechem.OEFormat_SDF)
  ims.Setgz(True)

  mol=oechem.OEGraphMol()
  nbytes=0
  oeerrs=oechem.oeosstream()
  oechem.OEThrow.SetOutputStream(oeerrs)
  while oechem.OEReadMolecule(ims,mol):
    cid = oechem.OEGetSDData(mol,'PUBCHEM_COMPOUND_CID')
    cansmi = oechem.OEGetSDData(mol,'PUBCHEM_OPENEYE_CAN_SMILES')
    isosmi = oechem.OEGetSDData(mol,'PUBCHEM_OPENEYE_ISO_SMILES')
    buff=("%s %s\n"%(isosmi,cid))
    fout.write(buff)
    nbytes+=len(buff)
    HandleOEErrors(oeerrs,True)
  os.remove(fpath_tmp)
  return nbytes


#############################################################################
### ExtractOutcomes() - return hash of all SIDs/CIDs to list of
### activity values [1-4] (may be multiple and discrepant).
### Also return hash of outcomes from this assay.
### If sidset exists this is a subset of interest.
### If use_cids is true, all ids are CIDs.
#############################################################################
def ExtractOutcomes(ftxt,sidset,use_cids=False):
  sids={} 
  sids_inactive=[]; sids_active=[]; sids_inconclusive=[];
  sids_unspecified=[]; sids_discrepant=[];
  lines=ftxt.splitlines()
  if len(lines)<2:
    return sids
  ##print >>sys.stderr, 'tag line: %s'%(lines[0])
  if use_cids:
    id_tag='PUBCHEM_CID'
  else:
    id_tag='PUBCHEM_SID'
  tags=lines[0].split(',')
  j_sid,j_cid,j_act=None,None,None
  for j,tag in enumerate(tags):
    if re.match('"?%s"?$'%id_tag,tag): j_sid=j
    if re.match('"?PUBCHEM_ACTIVITY_OUTCOME"?$',tag): j_act=j
  if j_sid==None or j_act==None:
    print >>sys.stderr, 'cannot find sid and activity tags: %s'%(lines[0])
    return sids
  for line in lines[1:]:
    try:
      vals=line.split(',')
      ## sid may be absent; report?
      sid=re.sub('"','',vals[j_sid])
      if not sid: continue
      sid=int(sid)
      act=int(vals[j_act])	## should be [1-4]
    except:
      print >>sys.stderr, 'Warning: problem with line: %s'%(line)
      #break	#DEBUG
      continue
    if sidset and not sidset.has_key(sid): continue

    if sids.has_key(sid):
      sids[sid]['acts'].append(act)
    else:
      sids[sid]={'acts':[act],'outcome':0}

  for sid in sids.keys():
    acts=sids[sid]['acts']
    acts.sort()
    while 4 in acts and len(acts)>1: acts.remove(4)
    if len(acts)==1 or acts[0]==acts[-1]:
      sids[sid]['outcome']=acts[0]
    else:
      sids[sid]['outcome']=5
      if not ( (1 in acts and 2 in acts)
        or (1 in acts and 3 in acts)
        or (2 in acts and 3 in acts)): print >>sys.stderr, 'ERROR: Doh! acts=%s'%(str(acts))

  return sids
    
#############################################################################
### Input file is assay CSV.  For specified SIDs, output CSV with outcomes.
### 4 header lines expected.  Maybe 10 fields.
#############################################################################
def ExtractResults(fin,aid,sids,fout,verbose):
  n_in=0; n_out=0; n_active=0;
  tags = None;
  j_sid = None; j_actout = None; j_actsco = None;
  fout.write('AID,SID,ACTIVITY_OUTCOME\n')
  while True:
    line = fin.readline()
    if not line: break
    n_in+=1
    if n_in==1 or not tags:
      tags = re.split(',',line)
      #print >>sys.stderr, 'DEBUG: %s'%line
      for j,tag in enumerate(tags):
        #print >>sys.stderr, '\t"%s"'%tag
        if tag == 'PUBCHEM_SID': j_sid = j
        elif tag == 'PUBCHEM_ACTIVITY_OUTCOME': j_actout = j
        elif tag == 'PUBCHEM_ACTIVITY_SCORE': j_actsco = j
      continue
    elif n_in<5: continue
    if not j_sid:
      print >>sys.stderr, 'ERROR: PUBCHEM_SID column not found.'
      break
    if not j_actout:
      print >>sys.stderr, 'ERROR: PUBCHEM_ACTIVITY_OUTCOME column not found.'
      break
    vals = re.split(',',line.rstrip())
    sid = vals[j_sid]
    if not sid: continue
    sid = int(sid)
    if sid not in sids: continue
    actout = vals[j_actout]
    if actout=='Active': n_active+=1
    if OUTCOME_CODES.has_key(actout.lower()):
      actout = OUTCOME_CODES[actout.lower()]
    fout.write('%d,%d,%s\n'%(aid,sid,actout))
    n_out+=1

  print >>sys.stderr, '%s: n_in = %d ; n_out = %d ; n_active = %d'%(aid,n_in,n_out,n_active)

#############################################################################
def Str2Ints(str):
  if not re.search('\S',str): return []
  return map(lambda x:int(x),str.split(','))

#############################################################################
def Ints2Str(intlist):
  if not intlist: return ''
  return (','.join(map(lambda x:('%d'%x),intlist)))

#############################################################################
