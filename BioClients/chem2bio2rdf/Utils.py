#!/usr/bin/python
### #!/usr/bin/env python	## on cheminfov, python2.4 has pgdb ; python 2.6 does not, alas.
'''
	Chem2Bio2RDF utility functions.

	[ ]	I think we need a function which will add a compound given 
		either
		  *  SMILES and CID 
		or
		  *  InChI and CID 
		The global table is c2b2r_compound.

		With a new ChEMBL compound, the molregno is added separately, and
		linked to the CID.  But this could be done in the same function.
		With SQL it is not so easy to check whether the CID etc. is already
		present.  The function should first check to avoid redundant rows.
		
		Do we also need Inchi2Smiles and Smiles2Inchi functions?
		Can we add the InChI only and get by without smiles?


	table: public.c2b2r_compound
		['CID', 'integer']
		['bio2rdf_URI', 'character varying']
		['pubchem_URL', 'character varying']
		['openeye_can_smiles', 'text']
		['openeye_iso_smiles', 'text']
		['std_inchi', 'text']

	Also note there is
	table: public.c2b2r_compound_new
		['cid', 'integer']
		['bio2rdf_URI', 'character varying']
		['pubchem_URL', 'character varying']
		['openeye_can_smiles', 'text']
		['openeye_iso_smiles', 'text']
		['std_inchi', 'text']
		['gfp', 'bit']
		['gfpbcnt', 'integer']

		??
	##################################################################
	Problems with c2b2r:
	 [ ] Use of schema "public".  Which tables are needed?

	##################################################################
	Jeremy Yang
	 13 Nov 2013
'''
import os,sys,getopt,re,time,math
import pgdb


DBSCHEMA='public'
#DBHOST='localhost'
DBHOST='cheminfov.informatics.indiana.edu'
DBNAME='chord'
DBUSR='cicc3'
DBPW=None

#############################################################################
def Connect(dbhost=DBHOST,dbname=DBNAME,dbusr=DBUSR,dbpw=DBPW):
  '''Connect to c2b2r.'''
  dsn='%s:%s:%s:%s'%(dbhost,dbname,dbusr,dbpw)
  db=pgdb.connect(dsn=dsn)
  cur=db.cursor()
  return db,cur

#############################################################################
def GetCpdBySmi(smi,iso,dbschema,db):
  '''Get compound[s] by smiles; return rows where each row tuple (cid,).'''
  cur=db.cursor()
  if re.search(r'\\',smi): smi=re.sub(r'\\',r'\\\\',smi)
  if iso:
    sql=('SELECT "CID",openeye_can_smiles,openeye_iso_smiles,std_inchi FROM %s.c2b2r_compound WHERE openeye_iso_smiles=gnova.isosmiles(\'%s\')'%(dbschema,smi))
  else:
    sql=('SELECT "CID",openeye_can_smiles,openeye_iso_smiles,std_inchi FROM %s.c2b2r_compound WHERE openeye_iso_smiles=gnova.cansmiles(\'%s\')'%(dbschema,smi))
  cur.execute(sql)
  rows=cur.fetchall()
  cur.close()
  return rows

#############################################################################
def Cids2Smis(cids,dbschema,db):
  '''Return list of SMILES for given list of CIDs.'''
  cur=db.cursor()
  smis=[]
  for cid in cids:
    #sql=('SELECT openeye_can_smiles FROM %s.c2b2r_compound WHERE "CID"=%d'%(dbschema,cid))
    sql=('SELECT openeye_iso_smiles FROM %s.c2b2r_compound WHERE "CID"=%d'%(dbschema,cid))
    #sql=('SELECT openeye_iso_smiles FROM %s.c2b2r_compound_new WHERE "cid"=%d'%(dbschema,cid))
    cur.execute(sql)
    rows=cur.fetchall()
    if not rows: smis.append(None)
    elif len(rows[0])<1:  smis.append(None)
    else: smis.append(rows[0][0])
  cur.close()
  return smis

#############################################################################
def DescribeSchema(substr,dbschema,db):
  '''Return human readable text describing the schema.'''
  cur=db.cursor()
  if substr:
    sql=("SELECT table_name FROM information_schema.tables WHERE table_schema='%s' AND table_name ILIKE '%%c2b2r_%%' AND table_name ILIKE '%%%s%%'"%(dbschema,substr))
  else:
    sql=("SELECT table_name FROM information_schema.tables WHERE table_schema='%s' AND table_name ILIKE '%%c2b2r_%%'"%dbschema)
  cur.execute(sql)
  rows=cur.fetchall()	##data rows
  n_table=len(rows)
  for row in rows:
    tablename=row[0]
    sql=("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='%s' AND table_name = '%s'"%(dbschema,tablename))
    cur.execute(sql)
    rows=cur.fetchall()	##data rows
    print ("table: %s.%s"%(dbschema,tablename))
    for row in rows:
      print ("\t%s"%str(row))
  cur.close()
  print >>sys.stderr, "table count: %d"%n_table
  return

#############################################################################
def DescribeCounts(dbschema,db):
  '''Return human readable text listing the table rowcounts.'''
  cur=db.cursor()
  sql=("SELECT table_name FROM information_schema.tables WHERE table_schema='%s' AND table_name ILIKE '%%c2b2r_%%' ORDER BY table_name"%dbschema)
  cur.execute(sql)
  rows=cur.fetchall()
  print ("table rowcounts:")
  for row in rows:
    tablename=row[0]
    sql=("SELECT count(*) FROM %s.\"%s\""%(dbschema,tablename))
    cur.execute(sql)
    rows=cur.fetchall()
    print "%-40s: %9d"%(tablename,rows[0][0])
  cur.close()
  return
 
#############################################################################
def AddNewCID(cid,smi,inchi,dbschema,db):
  cur=db.cursor()
  smi=re.sub(r'\\',r"'||E'\\\\'||'",smi)
  sql=("INSERT INTO %s.c2b2r_compound (\"CID\",openeye_can_smiles,openeye_iso_smiles,std_inchi) VALUES (%d,gnova.cansmiles('%s'),gnova.isosmiles('%s'),'%s')"%(dbschema,cid,smi,smi,inchi))
  ok=cur.execute(sql)
  cur.close()
  return ok

#############################################################################
def GetTarget(tids,fout,dbschema,db):
  cur=db.cursor()
  sql='''\
SELECT DISTINCT
	protein_accession,
	db_source,
	pref_name AS name
FROM
	%(DBSCHEMA)s.c2b2r_chembl_08_target_dictionary
WHERE
	target_type = 'PROTEIN'
	AND organism = 'Homo sapiens'
	AND db_source = 'SWISS-PROT'
	AND protein_accession IN ( %(TIDS)s )
ORDER BY protein_accession ASC
'''%{'DBSCHEMA':dbschema,'TIDS':','.join(map(lambda x:("'%s'"%x),tids))}
  ok=cur.execute(sql)
  rows=cur.fetchall()
  fout.write('"protein_accession","db_source","name"\n')
  for row in rows:
    fout.write('"%s","%s","%s"\n'%(row[0],row[1],row[2]))
  cur.close()
  return ok

#############################################################################
def ListTargets(fout,dbschema,db):
  cur=db.cursor()
  sql='''\
SELECT DISTINCT
	tid,
	protein_accession,
	chembl_id,
	tax_id,
	target_type,
	organism,
	db_source,
	gene_symbol,
	pref_name
FROM
	public.c2b2r_chembl_08_target_dictionary
WHERE
	target_type = 'PROTEIN'
'''%{'DBSCHEMA':dbschema}
  fout.write('"tid","protein_accession","chembl_id","tax_id","target_type","organism","db_source","gene_symbol","pref_name"\n')
  ok=cur.execute(sql)
  rows=cur.fetchall()
  for row in rows:
    for i,val in enumerate(row):
      if val==None: val=''
      fout.write('"%s"'%(val))
      if i<(len(row)-1): fout.write(',')
    fout.write('\n')
    fout.flush()
  cur.close()

#############################################################################
def ListGenes(fout,dbschema,db):
  cur=db.cursor()
  sql='''\
SELECT DISTINCT
	tid,
	protein_accession,
	chembl_id,
	tax_id,
	target_type,
	organism,
	db_source,
	gene_symbol,
	pref_name
FROM
	public.c2b2r_chembl_08_target_dictionary
WHERE
	target_type = 'PROTEIN'
ORDER BY
	gene_symbol ASC
'''%{'DBSCHEMA':dbschema}
  fout.write('"tid","protein_accession","chembl_id","tax_id","target_type","organism","db_source","gene_symbol","pref_name"\n')
  ok=cur.execute(sql)
  rows=cur.fetchall()
  for row in rows:
    for i,val in enumerate(row):
      if val==None: val=''
      fout.write('"%s"'%(val))
      if i<(len(row)-1): fout.write(',')
    fout.write('\n')
    fout.flush()
  cur.close()

#############################################################################
### Very few synonyms in c2b2r_compound_synonym (506).
### But!  87615736 synonyms in:
### table: public.pubchem_synonym
###        ['ccid_synid', 'bigint']
###        ['cid', 'character varying']
###        ['synonym', 'text']
#############################################################################
def GetCompound(cid,fout,dbschema,db):
  cur=db.cursor()
  sql='''\
SELECT DISTINCT
	cpd.cid,
	syn.synonym AS name,
	cpd.openeye_iso_smiles AS isosmi
FROM
	%(DBSCHEMA)s.c2b2r_compound_new AS cpd
LEFT OUTER JOIN
	pubchem_synonym AS syn ON (syn.cid::INT = cpd.cid)
WHERE
	cpd.cid = %(CID)d
ORDER BY cid, name
'''%{'DBSCHEMA':dbschema,'CID':cid}
  cur.execute(sql)
  rows=cur.fetchall()
  if not rows: return False
  names=[]
  for row in rows:
    name=row[1]
    isosmi=row[2]
    if name: names.append(name)

  names = SortCompoundNamesForHumans(names)
  for i,name in enumerate(names):
    if i==10: break
    print 'DEBUG "%s"'%(name)
  if len(names)>10: names=names[:10]
  names_str=';'.join(names)
  fout.write('%d,"%s","%s"\n'%(cid,names_str,isosmi))
  fout.flush()
  cur.close()
  return True

#############################################################################
### Heuristic for human comprehensibility.
#############################################################################
def SortCompoundNamesForHumans(names):
  names_scored={n:0 for n in names}
  pat_proper = re.compile(r'^[A-Z][a-z]+$')
  pat_text = re.compile(r'^[A-Za-z ]+$')
  for name in names:
    if pat_proper.match(name): names_scored[name]+=100
    elif pat_text.match(name): names_scored[name]+=50
    elif re.match(r'^[A-z][A-z][A-z][A-z][A-z][A-z][A-z].*$',name): names_scored[name]+=10
    if re.search(r'[\[\]\{\}]',name): names_scored[name]-=50
    if re.search(r'[_/\(\)]',name): names_scored[name]-=10
    if re.search(r'\d',name): names_scored[name]-=10
    names_scored[name] -= math.fabs(7-len(name))    #7 is optimal!

  names_ranked = [[score,name] for name,score in names_scored.items()]
  names_ranked.sort()
  names_ranked.reverse()
  #for score,name in names_ranked:
  #  print 'DEBUG "%s" (%d)'%(name,score)
  return [name for score,name in names_ranked]

#############################################################################
def NiceTime(secs):
  '''Express time in human readable format.'''
  secs=int(secs)
  if secs<60: return '%ds'%secs
  s=secs%60
  m=((secs-s)%3600)/60
  if secs<3600: return '%dm:%02ds'%(m,s)
  h=((secs-s-m*60)%(24*3600))/3600
  if secs<3600*24: return '%dh:%02dm:%02ds'%(h,m,s)
  d=(secs-s-m*60-h*3600)/(3600*24)
  return '%dd:%02dh:%02dm:%02ds'%(d,h,m,s)

#############################################################################
