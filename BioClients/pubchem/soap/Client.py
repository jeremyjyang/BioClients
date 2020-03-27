#!/usr/bin/env python3
"""	pug_search.py - PubChem/PUG sub|sim|exact search
	Jeremy Yang (2010)
"""
import sys,os,re,urllib,time,argparse,tempfile,logging

from ... import pubchem


def QueryPug_qkey(qkey,webenv,fmt='smiles',gzip=False):
  if gzip: compres='gzip'
  else: compres='none'
  qxml='''\
<PCT-Data><PCT-Data_input><PCT-InputData>
  <PCT-InputData_download><PCT-Download> 
    <PCT-Download_uids><PCT-QueryUids>
      <PCT-QueryUids_entrez><PCT-Entrez>
        <PCT-Entrez_db>pccompound</PCT-Entrez_db>
        <PCT-Entrez_query-key>%(QKEY)s</PCT-Entrez_query-key>
        <PCT-Entrez_webenv>%(WEBENV)s</PCT-Entrez_webenv>
      </PCT-Entrez></PCT-QueryUids_entrez>
    </PCT-QueryUids></PCT-Download_uids>
    <PCT-Download_format value="%(FMT)s"/>
    <PCT-Download_compression value="%(COMPRES)s"/>
  </PCT-Download></PCT-InputData_download>
</PCT-InputData></PCT-Data_input></PCT-Data>
'''%{'QKEY':qkey,'WEBENV':webenv,'FMT':fmt,'COMPRES':compres}
  logging.info('connecting %s...'%PUGURL)
  logging.info('submitting query for qkey: %s ...'%qkey)
  f=pubchem.soap.Utils.UrlOpenTry(PUGURL,qxml)
  pugxml=f.read()
  f.close()
  status,reqid,url,qkey,wenv,error=pubchem.soap.Utils.ParsePugXml(pugxml)
  return status,reqid,url,qkey,wenv,error

#############################################################################
def QueryPug_struct(smi,searchtype='sub',sim_cutoff=0.8,active=False,mlsmr=False,nmax=10000):
  """	 <PCT-CSIdentity value="same-isotope">4</PCT-CSIdentity>
  """
  qxml='''\
<PCT-Data><PCT-Data_input><PCT-InputData><PCT-InputData_query><PCT-Query>
  <PCT-Query_type><PCT-QueryType><PCT-QueryType_css>
    <PCT-QueryCompoundCS>
    <PCT-QueryCompoundCS_query>
      <PCT-QueryCompoundCS_query_data>%(SMILES)s</PCT-QueryCompoundCS_query_data>
    </PCT-QueryCompoundCS_query>
    <PCT-QueryCompoundCS_type>
'''%{'SMILES':smi}
  if searchtype=='sim':
    qxml+='''\
      <PCT-QueryCompoundCS_type_similar><PCT-CSSimilarity>
        <PCT-CSSimilarity_threshold>%(SIM_CUTOFF)d</PCT-CSSimilarity_threshold>
      </PCT-CSSimilarity></PCT-QueryCompoundCS_type_similar>
'''%{'SIM_CUTOFF':sim_cutoff*100}
  elif searchtype=='exact':
    qxml+='''\
      <PCT-QueryCompoundCS_type_identical>
        <PCT-CSIdentity value="same-stereo-isotope">5</PCT-CSIdentity>
      </PCT-QueryCompoundCS_type_identical>
'''
  else:
    qxml+='''\
      <PCT-QueryCompoundCS_type_subss><PCT-CSStructure>
        <PCT-CSStructure_isotopes value="false"/>
        <PCT-CSStructure_charges value="false"/>
        <PCT-CSStructure_tautomers value="false"/>
        <PCT-CSStructure_rings value="false"/>
        <PCT-CSStructure_bonds value="true"/>
        <PCT-CSStructure_chains value="true"/>
        <PCT-CSStructure_hydrogen value="false"/>
      </PCT-CSStructure></PCT-QueryCompoundCS_type_subss>
'''
  qxml+='''\
    </PCT-QueryCompoundCS_type>
    <PCT-QueryCompoundCS_results>%(NMAX)d</PCT-QueryCompoundCS_results>
    </PCT-QueryCompoundCS>
  </PCT-QueryType_css></PCT-QueryType>
'''%{'NMAX':nmax}
  if active:
    qxml+='''\
  <PCT-QueryType><PCT-QueryType_cel><PCT-QueryCompoundEL>
    <PCT-QueryCompoundEL_activity>
      <PCT-CLByBioActivity value="active">2</PCT-CLByBioActivity>
    </PCT-QueryCompoundEL_activity>
  </PCT-QueryCompoundEL></PCT-QueryType_cel></PCT-QueryType>
'''
  if mlsmr:
    qxml+='''\
  <PCT-QueryType><PCT-QueryType_cel><PCT-QueryCompoundEL>
    <PCT-QueryCompoundEL_source><PCT-CLByString>
      <PCT-CLByString_qualifier value="must">1</PCT-CLByString_qualifier>
      <PCT-CLByString_category>MLSMR</PCT-CLByString_category>
    </PCT-CLByString></PCT-QueryCompoundEL_source>
  </PCT-QueryCompoundEL></PCT-QueryType_cel></PCT-QueryType>
'''
  qxml+='''\
  </PCT-Query_type></PCT-Query>
</PCT-InputData_query></PCT-InputData></PCT-Data_input></PCT-Data>
'''
  logging.info('connecting %s...'%PUGURL)
  if sim:
    logging.info('query (%f): %s ...'%(sim_cutoff,smiles))
  else:
    logging.info('substructure query: %s ...'%smiles)
  f=pubchem.soap.Utils.UrlOpenTry(PUGURL,qxml)
  pugxml=f.read()
  f.close()

  status,reqid,url,qkey,wenv,error=pubchem.soap.Utils.ParsePugXml(pugxml)
  return status,reqid,qkey,wenv,error

#############################################################################
def ElapsedTime(t_start):
  t_elapsed=time.time()-t_start
  tsec=t_elapsed%60
  tmin=t_elapsed/60
  return ("%d:%02d"%(tmin,tsec))

#############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  PUGURL='http://pubchem.ncbi.nlm.nih.gov/pug/pug.cgi'
  POLL_WAIT=10
  MAX_WAIT=300
  SIM_CUTOFF=0.80

  parser = argparse.ArgumentParser(description="PubChem PUG SOAP client: sub|sim|exact search, fetch smiles|sdfs")
  parser.add_argument("--o", dest="ofile", help="output smiles|sdf file (w/ CIDs)")
  parser.add_argument("--qsmi", help="input query smiles (or smarts)")
  parser.add_argument("--fmt", help="smiles|sdf [default via filename]")
  parser.add_argument("--gz", help="output gzipped [default via filename]")
  parser.add_argument("--out_cids", dest="out_cids_file", help="output CIDs (only w/ smiles output)")
  parser.add_argument("--similarity", help="similarity search [default is substructure]")
  parser.add_argument("--exact", help="exact search [default is substructure]")
  parser.add_argument("--sim_cutoff", type=float, default=SIM_CUTOFF, help="similarity cutoff, Tanimoto")
  parser.add_argument("--active", help="active mols only (in any assay)")
  parser.add_argument("--mlsmr", help="MLSMR mols only")
  parser.add_argument("--nmax", type=int, help="max hits returned")
  parser.add_argument("--max_wait", type=int, default=MAX_WEIGHT, help="max wait for query")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if not args.qsmi:
    parser.error('smiles required\n'+usage)
  logging.info('query: "%s"'%args.qsmi)

  if args.ofile:
    fout=open(args.ofile,'wb')
    if (args.ofile[-3:]=='.gz'):
      gzip=True
      ext=re.sub('^.*\.','',args.ofile[:-3])
    else:
      ext=re.sub('^.*\.','',args.ofile)
    if not args.fmt: fmt=ext
    if fmt=='smi': fmt='smiles'
    if fmt not in ('smiles','sdf'):
      parser.error('format "smiles" or "sdf" required')

  if args.out_cids_file:
    if fmt=='sdf':
      parser.error('--out_cids not allowed with SDF output.')

    fout_cids=open(args.out_cids_file,'wb')

  t0=time.time()	## start timer

  status,reqid,qkey,wenv,error=QueryPug_struct(args.qsmi,args.searchtype,args.sim_cutoff,args.active,args.mlsmr,args.nmax)

  if status not in ('success','queued','running'):
    parser.error('query failed; quitting (status=%s,error="%s").'%(status,error))
  logging.info('query status: %s'%status)

  if not reqid and not qkey:
    parser.error('query ok but no ID; quitting.')

  i_poll=0
  while not qkey:
    if time.time()-t0>args.max_wait:
      pubchem.soap.Utils.PollPug(reqid,'cancel')
      parser.error('max wait exceeded (%d sec); quitting.'%args.max_wait)
    logging.info('polling PUG [ID=%d]...'%reqid)
    status,reqid_new,url,qkey,wenv,error=pubchem.soap.Utils.PollPug(reqid,'status')
    if reqid_new: reqid=reqid_new
    if qkey: break
    logging.info('%s elapsed; %d sec wait; status=%s'%(ElapsedTime(t0),POLL_WAIT,status))
    logging.info('%s'%(error))
    if re.search('No result found',error,re.I):
      parser.error(error)
    time.sleep(POLL_WAIT)
    i_poll+=1


  status,reqid,url,qkey,wenv,error=QueryPug_qkey(qkey,wenv,fmt,gzip)
  i_poll=0
  while not url:
    if time.time()-t0>args.max_wait:
      pubchem.soap.Utils.PollPug(reqid,'cancel')
      parser.error('max wait exceeded (%d sec); quitting.'%args.max_wait)
    logging.info('polling PUG [ID=%d]...'%reqid)
    status,reqid,url,qkey,wenv,error=pubchem.soap.Utils.PollPug(reqid,'status')
    if url: break
 
    logging.info('%s elapsed; %d sec wait; status=%s'%(ElapsedTime(t0),POLL_WAIT,status))
    time.sleep(POLL_WAIT)
    i_poll+=1

  logging.info('query elapsed time: %s'%(ElapsedTime(t0)))
  if args.ofile:
    logging.info('URL: %s'%url)
    logging.info('downloading to %s...'%args.ofile)

  fd,tmpfile=tempfile.mkstemp('.txt', PROG)
  f=os.fdopen(fd,"w")
  nbytes=pubchem.soap.Utils.DownloadUrl(url,f)
  f.close()

  if fmt=='smiles':
    ftmp=open(tmpfile)
    n=0
    while True:
      line=ftmp.readline()
      if not line: break
      fields=line.split()
      if args.ofile: fout.write("%s %s\n"%(fields[1],fields[0]))
      if args.out_cids_file: fout_cids.write("%s\n"%(fields[0]))
      n+=1
    logging.info('compounds: %d'%(n))
    ftmp.close()
  else:
    os.system("cp %s %s"%(tmpfile,args.ofile))
  os.unlink(tmpfile)

  sys.stderr.write('%s: format: %s'%(PROG,fmt))
  if args.gzip: sys.stderr.write('(gzipped)')
  sys.stderr.write('\n')

  if args.ofile:
    fout.close()
    nbytes=os.stat(args.ofile).st_size
    logging.info('%s (%.2fMB)'%(args.ofile,nbytes/1e6))

  if args.out_cids_file:
    fout_cids.close()
    nbytes=os.stat(args.out_cids_file).st_size
    logging.info('%s (%.2fMB)'%(args.out_cids_file,nbytes/1e6))

