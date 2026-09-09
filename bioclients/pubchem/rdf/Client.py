#!/usr/bin/env python
##############################################################################
### pubchem_rdf.py - utility app for the PubChem RDF REST API.
### (Apparently no public Sparql endpoint exists.)
### https://pubchem.ncbi.nlm.nih.gov/rdf
##############################################################################
import sys,os,re,getopt,types,codecs
#
from ...util import rest
#
PROG=os.path.basename(sys.argv[0])
#
API_HOST='rdf.ncbi.nlm.nih.gov'
API_BASE_PATH='/pubchem'
#
OFMTS={
     'CSV': {'ext':'csv',      'mime':'text/csv'},
    'HTML': {'ext':'html',     'mime':'text/html'},
    'JSON': {'ext':'json',     'mime':'application/json'},
     'RDF': {'ext':'rdf',      'mime':'text/rdf'},
  'RDFXML': {'ext':'rdfxml',   'mime':'application/rdf+xml'},
  'TURTLE': {'ext':'ttl',      'mime':'application/x-turtle'}
}
#
#       'NTRIPLES': {'ext':'ntriples',     'mime':'text/plain'},
#             'N3': {'ext':'n3',           'mime':'text/rdf+n3'},
#  'RDFXML-ABBREV': {'ext':'rdfxml-abbrev','mime':'application/rdf+xml+abbrev'},
#############################################################################
### Problem: since each request returns headers, how do we request RDF
### for multiple IDs?  (Hence kludge here.)
#
def GetData(base_uri,pfx,ids,ofmt,fout,verbose):
  i=0;
  for id_query in ids:
    url=(base_uri+'/%s%d.%s'%(pfx,id_query,OFMTS[ofmt.upper()]['ext']))
    res=rest.Utils.GetURL(url,headers={'Accept':'%s'%OFMTS[ofmt.upper()]['mime']},verbose=verbose)
    if not res:
      break
    elif type(res) in types.StringTypes:
      if i>0: #Kludge
        for line in res.splitlines():
          if not line.startswith('@'):
            fout.write(line+'\n')
      else:
        fout.write(res)
      i+=1
    else:
      print >>sys.stderr, 'ERROR: "%s"'%str(res)

#############################################################################
def GetCompound(base_uri,ids,ofmt,fout,verbose):
  GetData(base_uri,'compound/CID',ids,ofmt,fout,verbose)

#############################################################################
def GetSubstance(base_uri,ids,ofmt,fout,verbose):
  GetData(base_uri,'substance/SID',ids,ofmt,fout,verbose)

#############################################################################
def GetProtein(base_uri,ids,ofmt,fout,verbose):
  GetData(base_uri,'protein/GI',ids,ofmt,fout,verbose)

#############################################################################
def GetGene(base_uri,ids,ofmt,fout,verbose):
  GetData(base_uri,'gene/GID',ids,ofmt,fout,verbose)

#############################################################################
def GetBiosystem(base_uri,ids,ofmt,fout,verbose):
  GetData(base_uri,'biosystem/BSID',ids,ofmt,fout,verbose)

#############################################################################
def GetBioassay(base_uri,ids,ofmt,fout,verbose):
  GetData(base_uri,'bioassay/AID',ids,ofmt,fout,verbose)

#############################################################################
def GetEndpoint(base_uri,sids,aids,ofmt,fout,verbose):
  i=0;
  for sid in sids:
    for aid in aids:
      url=(base_uri+'/endpoint/SID%d_AID%d.%s'%(sid,aid,OFMTS[ofmt.upper()]['ext']))
      res=rest.Utils.GetURL(url,headers={'Accept':'%s'%OFMTS[ofmt.upper()]['mime']},verbose=verbose)
      if not res:
        break
      elif type(res) in types.StringTypes:
        if i>0: #Kludge
          for line in res.splitlines():
            if not line.startswith('@'):
              fout.write(line+'\n')
        else:
          fout.write(res)
        i+=1
      else:
        print >>sys.stderr, 'ERROR: "%s"'%str(res)

##############################################################################
if __name__=='__main__':
  ofmt='RDF';
  USAGE='''\
%(PROG)s - (REST client)
required (one of):
        --get_compound ..................(requires CIDs)
        --get_substance .................(requires SIDs)
        --get_protein ...................(requires GIs)
        --get_gene ......................(requires GIDs)
        --get_biosystem .................(requires BSIDs)
        --get_bioassay ..................(requires AIDs)
        --get_endpoint ..................(requires SIDs, AIDs)
options:
	--i IFILE ....................... input IDs file
	--id ID ......................... input ID
	--aidfile AIDFILE ............... input AIDs file
	--aid AID ....................... input AID
	--o OFILE ....................... output file [stdout]
        --ofmt FMT ...................... output formats [%(OFMT)s]
	--api_host HOST ................. [%(API_HOST)s]
	--api_base_path PATH ............ [%(API_BASE_PATH)s]
        --skip N ........................ skip (input IDs)
        --nmax N ........................ max count (input IDs)
        --v ............................. verbose
        --h ............................. this help

Example IDs:
	2244 (compound)
	144206602 (substance)
	124375976 (protein)
	367 (gene)
	82991 (biosystem)
	1117354 (bioassay)

Output formats:
	%(OFMTS)s
'''%{
	'PROG':PROG,
	'API_HOST':API_HOST,
	'API_BASE_PATH':API_BASE_PATH,
	'OFMT':ofmt,
	'OFMTS':('|'.join(OFMTS.keys()))
	}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  id_query=None; ifile=None;
  aid_query=None; aidfile=None;
  name_query=None;
  ofile='';
  verbose=0;
  get_compound=False;
  get_substance=False;
  get_protein=False;
  get_gene=False;
  get_biosystem=False;
  get_bioassay=False;
  get_endpoint=False;
  skip=None; nmax=None;
  dbusr=None; dbpw=None;
  opts,pargs=getopt.getopt(sys.argv[1:],'',['i=','o=',
	'id=',
	'aid=',
	'aidfile=',
	'ofmt=',
	'get_compound',
	'get_substance',
	'get_protein',
	'get_gene',
	'get_biosystem',
	'get_bioassay',
	'get_endpoint',
	'api_host=','api_base_path=','dbusr=','dbpw=',
	'skip=', 'nmax=','version=','help','v','vv','vvv'])
  if not opts: ErrorExit(USAGE)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(USAGE)
    elif opt=='--o': ofile=val
    elif opt=='--i': ifile=val
    elif opt=='--id': id_query=int(val)
    elif opt=='--aidfile': aidfile=val
    elif opt=='--aid': aid_query=int(val)
    elif opt=='--ofmt': ofmt=val
    elif opt=='--dbusr': dbusr=val
    elif opt=='--dbpw': DBPW=val
    elif opt=='--get_compound': get_compound=True
    elif opt=='--get_substance': get_substance=True
    elif opt=='--get_protein': get_protein=True
    elif opt=='--get_gene': get_gene=True
    elif opt=='--get_biosystem': get_biosystem=True
    elif opt=='--get_bioassay': get_bioassay=True
    elif opt=='--get_endpoint': get_endpoint=True
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--skip': skip=int(val)
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s'%(opt))

  BASE_URL='http://'+API_HOST+API_BASE_PATH

  if ofile:
    fout=open(ofile,"w+")
    #fout=codecs.open(ofile,"w","utf8","replace")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=sys.stdout
    #fout=codecs.getwriter('utf8')(sys.stdout,errors="replace")

  if ofmt.upper() not in OFMTS.keys():
    ErrorExit('ERROR: --ofmt "%s" not allowed.s'%ofmt)

  ids=[]
  if ifile:
    fin=open(ifile)
    if not fin: ErrorExit('ERROR: cannot open ifile: %s'%ifile)
    while True:
      line=fin.readline()
      if not line: break
      try:
        ids.append(int(line.rstrip()))
      except:
        print >>sys.stderr, 'ERROR: bad input ID: %s'%line
        continue
    if verbose:
      print >>sys.stderr, '%s: input IDs: %d'%(PROG,len(ids))
    fin.close()
    id_query=ids[0]
  elif id_query:
    ids=[id_query]

  aids=[]
  if aidfile:
    fin=open(aidfile)
    if not fin: ErrorExit('ERROR: cannot open aidfile: %s'%aidfile)
    while True:
      line=fin.readline()
      if not line: break
      try:
        aids.append(int(line.rstrip()))
      except:
        print >>sys.stderr, 'ERROR: bad input AID: %s'%line
        continue
    if verbose:
      print >>sys.stderr, '%s: input AIDs: %d'%(PROG,len(aids))
    fin.close()
    aid_query=aids[0]
  elif aid_query:
    aids=[aid_query]

  if get_compound:
    if not ids: ErrorExit('ERROR: ID required\n'+USAGE)
    GetCompound(BASE_URL,ids,ofmt,fout,verbose)

  elif get_substance:
    if not ids: ErrorExit('ERROR: ID required\n'+USAGE)
    GetSubstance(BASE_URL,ids,ofmt,fout,verbose)

  elif get_protein:
    if not ids: ErrorExit('ERROR: ID required\n'+USAGE)
    GetProtein(BASE_URL,ids,ofmt,fout,verbose)

  elif get_gene:
    if not ids: ErrorExit('ERROR: ID required\n'+USAGE)
    GetGene(BASE_URL,ids,ofmt,fout,verbose)

  elif get_biosystem:
    if not ids: ErrorExit('ERROR: ID required\n'+USAGE)
    GetBiosystem(BASE_URL,ids,ofmt,fout,verbose)

  elif get_bioassay:
    if not aids: ErrorExit('ERROR: AID required\n'+USAGE)
    GetBioassay(BASE_URL,aids,ofmt,fout,verbose)

  elif get_endpoint:
    if not ids: ErrorExit('ERROR: ID required\n'+USAGE)
    if not aids: ErrorExit('ERROR: AID required\n'+USAGE)
    GetEndpoint(BASE_URL,ids,aids,ofmt,fout,verbose)

  else:
    ErrorExit('ERROR: no operation specified.\n'+USAGE)

