#!/usr/bin/env python3
"""
TCRD db client utility (see also REST API client)
In general, return data as lists and dicts, readily convertible to JSON.
See https://dev.mysql.com/doc/connector-python/en/
regarding mysql-connector-python package.
"""
import os,sys,argparse,re,time,json,logging
import mysql.connector as mysql

#############################################################################
def ListTables(dbcon):
  cur=dbcon.cursor()
  cur.execute('SHOW TABLES')
  rows=cur.fetchall()
  tables=[]
  for row in rows:
    tables.append(row[0])
  tables.sort()
  return tables

#############################################################################
def Info(dbcon):
  cur=dbcon.cursor(dictionary=True)
  cur.execute('SELECT * FROM dbinfo')
  row=cur.fetchone()
  return row

#############################################################################
def Describe(dbcon):
  cur=dbcon.cursor()
  outtxt=''
  for table in ListTables(dbcon):
    outtxt+=('%s:\n'%table)
    cur.execute('DESCRIBE '+table)
    row=cur.fetchone()
    cols=[]
    while row:
      cols.append(row[0])
      row=cur.fetchone()
    cols.sort()
    outtxt+=('\t'+(', '.join(cols))+'\n')
  return outtxt

#############################################################################
def Counts(dbcon):
  tables=ListTables(dbcon)
  cur=dbcon.cursor()
  outtxt=''
  for table in tables:
    cur.execute('SELECT count(*) FROM '+table)
    row=cur.fetchone()
    outtxt+=('%18s: %8d rows\n'%(table,row[0]))
  return outtxt

#############################################################################
def AttributeCounts(dbcon):
  cur=dbcon.cursor()
  sql='SELECT ga.type, COUNT(ga.id) FROM gene_attribute ga GROUP BY ga.type'
  cur.execute(sql)
  row=cur.fetchone()
  attrcounts={}
  while row:
    attrcounts[row[0]]=row[1]
    row=cur.fetchone()

  outtxt='Attribute counts:\n'
  for attr_type in sorted(attrcounts.keys()):
    outtxt+=('%13s: %8d\n'%(attr_type,attrcounts[attr_type]))
  return outtxt

#############################################################################
def XrefCounts(dbcon):
  '''Synonyms, aliases, and Xrefs.'''
  cur=dbcon.cursor()
  outtxt=''

  f,t = 'name','synonym'
  cur.execute('SELECT COUNT(DISTINCT %s) FROM %s'%(f,t))
  row=cur.fetchone()
  outtxt+=('%s_count: %8d\n'%(t,row[0]))

  f,t = 'name','alias'
  cur.execute('SELECT COUNT(DISTINCT %s) FROM %s'%(f,t))
  row=cur.fetchone()
  outtxt+=('%s_count: %8d\n'%(t,row[0]))

  f,t = 'value','xref'
  cur.execute('SELECT COUNT(DISTINCT %s) FROM %s'%(f,t))
  row=cur.fetchone()
  outtxt+=('%s_count: %8d\n'%(t,row[0]))

  cur.execute('SELECT xtype, COUNT(DISTINCT value) FROM xref GROUP BY xtype ORDER BY xtype')
  rows=cur.fetchall()
  for row in rows:
    outtxt+=('%18s: %8d\n'%(row[0],row[1]))

  return outtxt

#############################################################################
def TDLCounts(dbcon):
  cur=dbcon.cursor()
  sql='''\
SELECT tdl,COUNT(id)
FROM target
WHERE tdl in (%(TDLS)s)
GROUP BY tdl
'''%{'TDLS':"'"+("','".join(TDLS))+"'"}
  cur.execute(sql)
  rows=cur.fetchall()
  #outtxt=''
  rdata={}
  n_total=0
  for row in rows:
    #outtxt+=('%8s: %6d\n'%(row[0],row[1]))
    rdata[row[0]] = row[1]
    n_total+=row[1]
  rdata['total'] = n_total
  #outtxt+=('   Total: %6d\n'%(n_total))
  return rdata

#############################################################################
def ListXreftypes(dbcon):
  cur=dbcon.cursor(mysql.cursors.DictCursor)
  sql='SELECT DISTINCT xtype FROM xref ORDER BY xtype'
  cur.execute(sql)
  rows=cur.fetchall()
  xreftypes=[]
  for row in rows:
    if 'xtype' in row: xreftypes.append(row['xtype'])
  return xreftypes

#############################################################################
def ListXrefs(dbcon,qtype,fout):
  cur=dbcon.cursor(mysql.cursors.DictCursor)
  fout.write('"%s","target_id","protein_id"\n'%(qtype))
  cols=['value','target_id','protein_id']
  sql='''\
SELECT DISTINCT %(COLS)s
FROM xref
WHERE xtype = '%(QTYPE)s'
'''%{	'COLS':(','.join(cols)),
	'QTYPE':qtype }
  cur.execute(sql)
  row=cur.fetchone()
  n_xref=0;
  while row:
    tid = row['target_id'] if ('target_id' in row and row['target_id']!=None) else ''
    pid = row['protein_id'] if ('protein_id' in row and row['protein_id']!=None) else ''
    fout.write('"%s",%s,%s\n'%(row['value'],tid,pid))
    n_xref+=1
    row=cur.fetchone()
  logging.info('Xrefs count: %d'%(n_xref))

#############################################################################
def ListTargets(dbcon, tdl, pfam, fout):
  cur = dbcon.cursor(dictionary=True)
  sql='''
SELECT
	target.id AS "tcrdTargetId",
	target.name AS "tcrdTargetName",
	target.fam AS "tcrdTargetFamily",
	target.tdl AS "TDL",
	target.ttype AS "tcrdTargetType",
	target.idg AS "idgList",
	protein.id AS "tcrdProteinId",
	protein.sym AS "tcrdGeneSymbol",
	protein.family AS "tcrdProteinFamily",
	protein.geneid AS "ncbiGeneId",
	protein.uniprot AS "uniprotId",
	protein.up_version AS "uniprotVersion",
	protein.chr,
	protein.description AS "tcrdProteinDescription",
	protein.dtoid AS "dtoId",
	protein.dtoclass AS "dtoClass",
	protein.stringid AS "ensemblProteinId",
	xref.value AS "ensemblGeneId"
FROM
	target
JOIN
	t2tc ON t2tc.target_id = target.id
JOIN
	protein ON protein.id = t2tc.protein_id
JOIN
	xref ON xref.protein_id = protein.id
'''
  wheres=["xref.xtype = 'Ensembl'", "xref.value REGEXP '^ENSG'"]
  if tdl:
    wheres.append('target.tdl = \'%s\''%tdl)
  if pfam:
    wheres.append('target.fam = \'%s\''%pfam)
  if wheres:
    sql+=(' WHERE '+(' AND '.join(wheres)))
  cur.execute(sql)
  row = cur.fetchone()
  i_row=0;
  tids=set(); pids=set(); uniprots=set(); ensps=set(); ensgs=set(); symbs=set();
  while row:
    i_row+=1
    if i_row==1:
      colnames = list(row.keys())
      fout.write('\t'.join(colnames)+'\n')
    if 'tcrdTargetId' in row: tids.add(row['tcrdTargetId'])
    if 'tcrdProteinId' in row: pids.add(row['tcrdProteinId'])
    if 'uniprotId' in row: uniprots.add(row['uniprotId'])
    if 'ensemblProteinId' in row: ensps.add(row['ensemblProteinId'])
    if 'ensemblGeneId' in row: ensgs.add(row['ensemblGeneId'])
    if 'tcrdGeneSymbol' in row: symbs.add(row['tcrdGeneSymbol'])
    fout.write('\t'.join([(str(row[tag]) if tag in row else '') for tag in colnames])+'\n')
    row = cur.fetchone()
  logging.info('TDL: %s'%(tdl if tdl else 'all'))
  logging.info('rows: %d'%(i_row))
  logging.info('Target count: %d'%(len(tids)))
  logging.info('Protein count: %d'%(len(pids)))
  logging.info('Uniprot count: %d'%(len(uniprots)))
  logging.info('ENSP count: %d'%(len(ensps)))
  logging.info('ENSG count: %d'%(len(ensgs)))
  logging.info('GeneSymbol count: %d'%(len(symbs)))

#############################################################################
def GetTargets(dbcon, qs, qtype, fout):
  '''Write data to CSV file, and return as list of dict-rows.'''
  if not qs:
    logging.info('ERROR: no query ID.')
    return
  cur = dbcon.cursor(dictionary=True)
  cols=[
	'target.description',
	'target.id',
	'target.fam',
	'target.name',
	'target.tdl',
	'target.ttype',
	'protein.chr',
	'protein.description',
	'protein.family',
	'protein.geneid',
	'protein.id',
	'protein.name',
	'protein.sym',
	'protein.uniprot'
	]
  if fout: fout.write('query,qtype,'+('%s\n'%(','.join(cols))))

  n_hit=0;
  tids_all=set();
  for qid in qs:
    sql='''\
SELECT
	%(COLS)s
FROM
	target
JOIN
	t2tc ON target.id = t2tc.target_id
JOIN
	protein ON protein.id = t2tc.protein_id
'''%{'COLS':(','.join(map(lambda s: '%s AS %s'%(s, s.replace('.', '_')), cols)))}
    wheres=[]
    if qtype.lower()=='tid':
      wheres.append('target.id = %d'%int(qid))
    elif qtype.lower()=='uniprot':
      wheres.append('protein.uniprot = \'%s\''%qid)
    elif qtype.lower() in ('gid', 'geneid'):
      wheres.append('protein.geneid = \'%s\''%qid)
    elif qtype.lower() in ('genesymb', 'genesymbol'):
      wheres.append('protein.sym = \'%s\''%qid)
    elif qtype.lower() == 'ensp':
      wheres.append('protein.stringid = \'%s\''%qid)
    elif qtype.lower() == 'ncbi_gi':
      sql+=('\nJOIN\n\txref ON xref.protein_id = protein.id')
      wheres.append('xref.xtype = \'NCBI GI\'')
      wheres.append('xref.value = \'%s\''%qid)
      wheres.append('xref.protein_id = protein.id')
    else:
      logging.info('ERROR: unknown query type: %s'%qtype)
      return
    sql+=(' WHERE '+(' AND '.join(wheres)))
    logging.debug('"%s"'%sql)
    logging.debug('query: %s = "%s" ...'%(qtype, qid))
    cur.execute(sql)
    rows=cur.fetchall()
    if not rows:
      logging.info('Not found: %s = %s'%(qtype, qid))
      continue
    n_hit+=1
    tids_this=set();
    colnames=map(lambda s: s.replace('.', '_'), cols)
    for row in rows:
      if 'target_id' in row: tids_this.add(row['target_id'])
      if fout: fout.write('"%s","%s"'%(qid, qtype))
      for j,tag in enumerate(colnames):
        val = row[tag] if tag in row else ''
        if fout: fout.write(',"%s"'%(val))
      if fout: fout.write('\n')
    tids_all |= tids_this

  logging.info('%ss queries: %d, found: %d, not found: %d'%(qtype, len(qs), n_hit, (len(qs)-n_hit)))
  logging.info('Targets found: %d'%(len(tids_all)))
  return list(tids_all)

#############################################################################
def GetPathways(dbcon, tids, fout):
  cur=dbcon.cursor(mysql.cursors.DictCursor)
  cols=[
	't2p.target_id',
	't2p.id',
	't2p.source',
	't2p.id_in_source',
	't2p.name',
	't2p.description',
	't2p.url'
	]
  if fout: fout.write('%s\n'%(','.join(cols)))

  n_hit=0;
  pids_all=set();
  for tid in tids:
    sql='''\
SELECT
	%(COLS)s
FROM
	target2pathway t2p
JOIN
	target t ON t.id = t2p.target_id
WHERE
	t.id = %(TID)s
ORDER BY
	t2p.target_id,
	t2p.id
'''%{	'COLS':(','.join(map(lambda s: '%s AS %s'%(s,s.replace('.','_')),cols))),
	'TID':str(tid)
	}

    logging.debug('"%s"'%sql)
    logging.debug('query: %s ...'%(tid))
    cur.execute(sql)
    rows=cur.fetchall()
    if not rows:
      logging.info('Not found: %s'%(str(tid)))
      continue
    n_hit+=1
    pids_this=set();
    colnames=map(lambda s: s.replace('.','_'),cols)
    for row in rows:
      if 'id' in row: pids_this.add(row['id'])
      for j,tag in enumerate(colnames):
        val = row[tag] if tag in row else ''
        if type(val) is str: val = val.encode('string-escape')
        if fout: fout.write(',"%s"'%(val))
      if fout: fout.write('\n')
    pids_all |= pids_this

  logging.info('queries: %d, found: %d, not found: %d'%(len(tids),n_hit,(len(tids)-n_hit)))
  logging.info('Pathways found: %d'%(len(pids_all)))
  return list(pids_all)

#############################################################################
if __name__=='__main__':
  DBHOST='tcrd.kmc.io'
  DBNAME='tcrd'
  DBUSR='tcrd'
  DBPW=''
  TDLS=['Tdark', 'Tbio', 'Tchem', 'Tclin']
  qtypes=[ 'TID', 'GENEID', 'UNIPROT', 'GENESYMB', 'NCBI_GI', 'ENSP']
  parser = argparse.ArgumentParser(description='TCRD MySql client utility')
  ops = ['info', 'describe', 'counts', 'tdlCounts', 'xrefCounts', 'attrCounts', 'listTargets', 'listXreftypes', 'listXrefs', 'getTargets', 'getTargetpathways']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="query ID or symbol")
  parser.add_argument("--qfile", help="input query file")
  parser.add_argument("--qtype", choices=qtypes, default='TID', help='query type')
  parser.add_argument("--id", help="query ID or symbol")
  parser.add_argument("--tdl", help="Target Development Level (TDL) %s"%('|'.join(TDLS)))
  parser.add_argument("--fam", help="target family GPCR|Kinase|IC|NR|...|Unknown")
  parser.add_argument("--dbname", default=DBNAME)
  parser.add_argument("--dbhost", default=DBHOST)
  parser.add_argument("--dbusr", default=DBUSR)
  parser.add_argument("--dbpw", default=DBPW)
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  qs=[]
  if args.qfile:
    fin = open(args.qfile)
    while True:
      line = fin.readline()
      if not line: break
      qs.append(line.rstrip())
    logging.info('Input IDs: %d'%(len(qs)))
    fin.close()
  elif args.query:
    qs.append(args.query)

  if args.dbusr is not None and args.dbpw is not None:
    dbcon = mysql.connect(host=args.dbhost, user=args.dbusr, passwd=args.dbpw, db=args.dbname)
  else:
    dbcon = mysql.connect(host=args.dbhost, db=args.dbname)

  if args.op=='describe':
    print(Describe(dbcon))

  elif args.op=='info':
    rdata = Info(dbcon)
    print(json.dumps(rdata, indent=2, sort_keys=True))

  elif args.op=='counts':
    print(Counts(dbcon))

  elif args.op=='xrefCounts':
    print(XrefCounts(dbcon))

  elif args.op=='attrCounts':
    print(AttributeCounts(dbcon))

  elif args.op=='tdlCounts':
    rdata = TDLCounts(dbcon)
    print(json.dumps(rdata, indent=2, sort_keys=True))

  elif args.op=='listTargets':
    ListTargets(dbcon, args.tdl, args.fam, fout)

  elif args.op=='getTargets':
    GetTargets(dbcon, qs, args.qtype, fout)

  elif args.op=='getTargetpathways':
    tids = GetTargets(dbcon, qs, args.qtype, None)
    GetPathways(dbcon, tids, fout)

  elif args.op=='listXreftypes':
    xreftypes = ListXreftypes(dbcon)
    print(str(xreftypes))

  elif args.op=='listXrefs':
    xreftypes = ListXreftypes(dbcon)
    if qtype not in xreftypes:
      ErrorExit('ERROR: qtype "%s" invalid.  Available xref types: %s'%(qtype, str(xreftypes)))
    ListXrefs(dbcon, args.qtype, fout)

  else:
    parser.print_help()

  dbcon.close()
