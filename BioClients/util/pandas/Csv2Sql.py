#!/usr/bin/env python3
"""
Convert CSV to INSERTS for a specified table, with
control over column names, datatypes, and database systems (dbsystem).
"""
###
import sys,os,argparse,re,gzip,logging
import pandas as pd
#
CHUNKSIZE=100;
DBSYSTEMS=['postgres', 'mysql', 'oracle', 'derby']
DBSYSTEM='postgres'
KEYWORDS='procedure,function,column,table'
MAXCHAR=1024
CHARTYPES = 'CHAR,CHARACTER,VARCHAR,TEXT'
NUMTYPES = 'INT,BIGINT,FLOAT,NUM'
DEFTYPE='CHAR'
TIMETYPES = 'DATE,TIMESTAMP'
NULLWORDS = "NULL,UNSPECIFIED,MISSING,UNKNOWN,NA,NAN"
SCHEMA='public'
QUOTECHAR='"'
#
#############################################################################
def CsvCheck(fin, dbsystem, noheader, maxchar, delim, qc, keywords):
  colnames=None; n_in=0; n_err=0; i_chunk=0;
  with pd.read_csv(fin, chunksize=CHUNKSIZE, sep=delim) as reader:
    for df_this in reader:
      i_chunk+=1
      logging.debug(f"chunk: {i_chunk}; nrows: {df_this.shape[0]}")
      for i in range(df_this.shape[0]):
        row = df_this.iloc[i,] #Series
        if i_chunk==1 or colnames is None:
          if noheader:
            prefix = re.sub(r'\..*$', '', os.path.basename(fin.name))
            colnames = [f"{prefix}_{j}" for j in range(1, 1+len(row))]
          else:
            colnames = list(df_this.columns)
          colnames_clean = CleanNames(colnames, '', keywords)
          colnames_clean = DedupNames(colnames_clean)
          for j in range(len(colnames)):
            tag = colnames[j]
            tag_clean = colnames_clean[j]
            logging.debug(f"column tag {j+1}: {tag:>24}"+(f" -> {tag_clean}" if tag_clean!=tag else ""))
          nval = {colname:0 for colname in colnames}
          maxlen = {colname:0 for colname in colnames}
          dtypes = {colname:type(row.values[j]) for j,colname in enumerate(colnames)}
        for j in range(len(row)):
          val = list(row.values)[j]
          if j<=len(colnames):
            colname = colnames[j]
          else:
            logging.error(f"[{n_in+i+1}] row j_col>len(colnames) {j}>{len(colnames)}")
            n_err+=1
          if type(val) is str:
            try:
              #val = val.encode('utf-8', 'replace')
              if len(val.strip())>0: nval[colname]+=1
              val = EscapeString(val, dbsystem)
              maxlen[colname] = max(maxlen[colname], len(val))
              if len(val)>maxchar:
                logging.debug(f"WARNING: [{n_in+i+1}] len>MAX ({len(val)}>{maxchar})")
                val = val[:maxchar]
            except Exception as e:
              logging.error(f"[{n_in+i+1}] {str(e)}")
              val = f"CSV2SQL:ENCODING_ERROR"
              n_err+=1
          else:
              if val is not None: nval[colname]+=1
        n_in+=df_this.shape[0]
  for j,tag in enumerate(colnames):
    logging.info(f"""{j+1}. {tag:>24}: nval: {nval[tag]:6d}; type: {dtypes[tag]}; maxlen: {maxlen[tag]:6d}""")
  logging.info(f"n_in: {n_in}; n_err: {n_err}")

#############################################################################
def Csv2Create(fin, fout, dbsystem, dtypes, schema, tablename, colnames, coltypes, prefix, noheader, fixtags, delim, qc, keywords):
  n_in=0; n_err=0; i_chunk=0;
  with pd.read_csv(fin, chunksize=CHUNKSIZE, sep=delim, dtype=str) as reader:
    for df_this in reader:
      i_chunk+=1
      logging.debug(f"chunk: {i_chunk}; nrows: {df_this.shape[0]}")
      for i in range(df_this.shape[0]):
        row = df_this.iloc[i,] #Series
        if i_chunk==1:
          if colnames is None:
            if noheader:
              prefix = re.sub(r'\..*$', '', os.path.basename(fin.name))
              colnames = [f"{prefix}_{j}" for j in range(1, 1+len(row))]
            else:
              colnames = list(df_this.columns)
          else:
            if len(colnames) != len(df_this.columns):
              logging.error("#colnames)!=#df_this.columns ({len(colnames)}!={len(df_this.columns)})")
              return
          if fixtags:
            colnames_orig = colnames[:]
            colnames_clean = CleanNames(colnames, '', keywords)
            colnames = DedupNames(colnames_clean)
            for j in range(len(colnames)):
              logging.debug(f"column {j+1}: {colnames_orig[j]:>24}"+(f" -> {colnames[j]}" if colnames[j]!=colnames_orig[j] else ""))
          nval = {colname:0 for colname in colnames}
          maxlen = {colname:0 for colname in colnames}
        if coltypes is None:
          coltypes = [dtypes['deftype'] for i in range(len(colnames))]
        else:
          if len(coltypes) != len(df_this.columns):
            logging.error("#coltypes!=#df_this.columns ({len(coltypes)}!={len(df_this.columns)})")
            return
          for j in range(len(coltypes)):
            if coltypes[j] is None: coltypes[j] = 'CHAR'
  sql = f"CREATE TABLE {tablename} (\n\t" if dbsystem=='mysql' else f"CREATE TABLE {schema}.{tablename} (\n\t"
  sql+=(",\n\t".join([f"{colnames[j]} {dtypes[dbsystem][coltypes[j]]}" for j in range(len(colnames))]))
  sql+=("\n);")
  if dbsystem=='postgres':
    sql += f"\nCOMMENT ON TABLE {schema}.{tablename} IS 'Created by CSV2SQL.';"
  fout.write(sql+'\n')
  logging.info(f"{tablename}: output SQL CREATE written, columns: {len(colnames)}")

#############################################################################
def Csv2Insert(fin, fout, dbsystem, dtypes, schema, tablename, colnames, coltypes, prefix, noheader, nullwords, nullify, fixtags, maxchar, chartypes, numtypes, timetypes, delim, qc, keywords, skip, nmax):
  n_in=0; n_err=0; i_chunk=0; n_out=0;
  with pd.read_csv(fin, chunksize=CHUNKSIZE, sep=delim, dtype=str) as reader:
    for df_this in reader:
      i_chunk+=1
      logging.debug(f"chunk: {i_chunk}; nrows: {df_this.shape[0]}")
      for i in range(df_this.shape[0]):
        n_in+=1
        if i_chunk==1:
          if colnames is None:
            if noheader:
              prefix = re.sub(r'\..*$', '', os.path.basename(fin.name))
              colnames = [f"{prefix}_{j}" for j in range(1, 1+df_this.shape[1])]
            else:
              colnames = list(df_this.columns)
            logging.debug(f"columns: {colnames}")
          else:
            if len(colnames) != len(df_this.columns):
              logging.error("#colnames)!=#df_this.columns ({len(colnames)}!={len(df_this.columns)})")
              return
          if coltypes is None:
            coltypes = [dtypes['deftype'] for i in range(len(colnames))]
          else:
            if len(coltypes)!=len(colnames):
              logging.error(f"#coltypes!=#colnames ({len(coltypes)}!={len(colnames)})")
              return
          if fixtags:
            colnames_orig = colnames[:]
            colnames_clean = CleanNames(colnames, '', keywords)
            colnames = DedupNames(colnames_clean)
            for j in range(len(colnames)):
              logging.debug(f"column {j+1}: {colnames_orig[j]:>24}"+(f" -> {colnames[j]}" if colnames[j]!=colnames_orig[j] else ""))
            logging.debug(f"columns: {colnames}")
        if n_in<=skip: continue
        line = (f"INSERT INTO {tablename} ({','.join(colnames)}) VALUES (") if dbsystem=='mysql' else (f"INSERT INTO {schema}.{tablename} ({','.join(colnames)}) VALUES (")
        df_this.columns = colnames
        row = df_this.iloc[i,] #Series
        logging.debug(f"row.keys(): {row.keys()}")
        for j,colname in enumerate(colnames):
          val = str(row[colname])
          if coltypes[j].upper() in chartypes:
            val = EscapeString(str(val), dbsystem)
            if len(val)>maxchar:
              val = val[:maxchar]
              logging.info(f"WARNING: [row={n_in}] string truncated to {maxchar} chars: '{val}'")
            val = "NULL" if (nullify and val.upper() in nullwords) else f"'{val}'"
          elif coltypes[j].upper() in numtypes:
            val = "NULL" if (val.upper() in nullwords or val=='') else f"{val}"
          elif coltypes[j].upper() in timetypes:
            val = (f"to_timestamp('{val}')")
          else:
            logging.error(f"No type specified or implied: (col={j+1})")
            continue
          line+=(f"{',' if j>0 else ''}{val}")
        line +=(') ;')
        fout.write(line+'\n')
        n_out+=1
        if n_in==nmax: break
  logging.info(f"{tablename}: input CSV lines: {n_in}; output SQL inserts: {n_out}")

#############################################################################
def CleanName(name, keywords):
  '''Clean table or col name for use without escaping.
1. Downcase.
2. Replace spaces and colons with underscores.
3. Remove punctuation and special chars.
4. Prepend leading numeral.
5. Truncate to 50 chars.
6. Fix if in keyword list, e.g. "procedure".
'''
  name = re.sub(r'[\s:-]+','_',name.lower())
  name = re.sub(r'[^\w]','',name)
  name = re.sub(r'^([\d])',r'col_\1',name)
  name = name[:50]
  if name in keywords:
    name+='_name'
  return name

#############################################################################
def CleanNames(colnames, prefix, keywords):
  for j in range(len(colnames)):
    colnames[j] = CleanName(prefix+colnames[j] if prefix else colnames[j], keywords)
  return colnames

#############################################################################
def DedupNames(colnames):
  unames = set()
  for j in range(len(colnames)):
    if colnames[j] in unames:
      colname_orig = colnames[j]
      k=1
      while colnames[j] in unames:
        k+=1
        colnames[j] = f"{colname_orig}_{k}"
    unames.add(colnames[j])
  return colnames

#############################################################################
def EscapeString(val, dbsystem):
  val=re.sub(r"'", '', val)
  if dbsystem=='postgres':
    val=re.sub(r'\\', r"'||E'\\\\'||'", val)
  elif dbsystem=='mysql':
    val=re.sub(r'\\', r'\\\\', val)
  return val

#############################################################################
if __name__=='__main__':

  parser = argparse.ArgumentParser(description="CSV to SQL CREATEs or INSERTs", epilog='')
  ops = ["insert", "create", "check"]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file (CSV|TSV) [stdin]")
  parser.add_argument("--o", dest="ofile", help="output SQL INSERTs [stdout]")
  parser.add_argument("--schema", default=SCHEMA, help="(Postgres schema, or MySql db)")
  parser.add_argument("--tablename", help="table [convert filename]")
  parser.add_argument("--prefix_tablename", help="prefix + [convert filename]")
  parser.add_argument("--dbsystem", default=DBSYSTEM, help="")
  parser.add_argument("--colnames", help="comma-separated [default: CSV tags]")
  parser.add_argument("--noheader", action="store_true", help="auto-name columns")
  parser.add_argument("--prefix_colnames", help="prefix CSV tags")
  parser.add_argument("--coltypes", help="comma-separated [default: all CHAR]")
  parser.add_argument("--nullify", action="store_true", help="CSV missing CHAR value converts to NULL")
  parser.add_argument("--nullwords", default=NULLWORDS, help="words synonymous with NULL (comma-separated list)")
  parser.add_argument("--keywords", default=KEYWORDS, help="keywords, disallowed tablenames (comma-separated list)")
  parser.add_argument("--char_types", default=CHARTYPES, help="character types (comma-separated list)")
  parser.add_argument("--num_types", default=NUMTYPES, help="numeric types (comma-separated list)")
  parser.add_argument("--time_types", default=TIMETYPES, help="time types (comma-separated list)")
  parser.add_argument("--maxchar", type=int, default=MAXCHAR, help="max string length")
  parser.add_argument("--fixtags", action="store_true", help="tags to colnames (downcase/nopunct/nospace)")
  parser.add_argument("--tsv", action="store_true", help="input file TSV")
  parser.add_argument("--igz", action="store_true", help="input file GZ")
  parser.add_argument("--delim", default=",", help="use if not comma or tab")
  parser.add_argument("--default_type", default=DEFTYPE, help="")
  parser.add_argument("--quotechar", default=QUOTECHAR, help="")
  parser.add_argument("--skip", type=int, default=0, help="skip N records (--insert only)")
  parser.add_argument("--nmax", type=int, default=0, help="max N records (--insert only)")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  DELIM = '\t' if args.tsv else args.delim

  NULLWORDS = re.split(r'[\s,]', args.nullwords)
  KEYWORDS = re.split(r'[\s,]', args.keywords)
  CHARTYPES = re.split(r'[\s,]', args.char_types)
  NUMTYPES = re.split(r'[\s,]', args.num_types)
  TIMETYPES = re.split(r'[\s,]', args.time_types)

  fin = (gzip.open(args.ifile) if args.igz else open(args.ifile)) if args.ifile else sys.stdin
  fout = open(args.ofile,'w') if args.ofile else sys.stdout

  if args.tablename:
    TABLENAME = args.tablename
  else:
    if not args.ifile: parser.error('--tablename or --i required.')
    TABLENAME = CleanName(args.prefix_tablename+re.sub(r'\..*$','', os.path.basename(args.ifile)), KEYWORDS)
    logging.debug(f"""tablename = '{TABLENAME}'""")

  DTYPES = {
	"postgres": {
		"CHAR":f"VARCHAR({args.maxchar})",
		"CHARACTER":f"VARCHAR({args.maxchar})",
		"VARCHAR":f"VARCHAR({args.maxchar})",
		"INT":"INTEGER",
		"BIGINT":"BIGINT",
		"FLOAT":"FLOAT",
		"NUM":"FLOAT",
		"BOOL":"BOOLEAN"
		},
	"mysql": {
		"CHAR":f"TEXT({args.maxchar})",
		"CHARACTER":f"TEXT({args.maxchar})",
		"VARCHAR":f"TEXT({args.maxchar})",
		"INT":"INTEGER",
		"BIGINT":"BIGINT",
		"FLOAT":"FLOAT",
		"NUM":"FLOAT",
		"BOOL":"BOOLEAN"
		}
	}
  DTYPES["deftype"] = args.default_type

  if args.op=="create":
    Csv2Create(fin, fout, args.dbsystem,
	DTYPES,
	args.schema,
	TABLENAME,
	re.split(r'[,\s]+', args.colnames) if args.colnames else None,
	re.split(r'[,\s]+', args.coltypes) if args.coltypes else None,
	args.prefix_colnames, args.noheader, args.fixtags, DELIM, args.quotechar,
	KEYWORDS)

  elif args.op=="insert":
    Csv2Insert(fin, fout, args.dbsystem,
	DTYPES,
	args.schema,
	TABLENAME,
	re.split(r'[,\s]+', args.colnames) if args.colnames else None,
	re.split(r'[,\s]+', args.coltypes) if args.coltypes else None,
	args.prefix_colnames, args.noheader,
	NULLWORDS, args.nullify, args.fixtags, args.maxchar,
	CHARTYPES, NUMTYPES, TIMETYPES,
	DELIM, args.quotechar, KEYWORDS, args.skip, args.nmax)

  elif args.op=="check":
    CsvCheck(fin, args.dbsystem, args.noheader, args.maxchar, DELIM, args.quotechar, KEYWORDS)

  else:
    parser.error(f"Invalid operation: {args.op}")

