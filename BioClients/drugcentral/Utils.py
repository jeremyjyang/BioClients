#!/usr/bin/env python3
"""
DrugCentral db utility functions.
"""
import os,sys,re,logging,yaml
import pandas,pandas.io.sql
import psycopg2,psycopg2.extras

#############################################################################
def ReadParamFile(fparam):
  params={};
  with open(fparam, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  return params

#############################################################################
def Connect(dbhost, dbport, dbname, dbusr, dbpw):
  """Connect to db; specify default cursor type DictCursor."""
  dsn = ("host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(dbhost, dbport, dbname, dbusr, dbpw))
  dbcon = psycopg2.connect(dsn)
  dbcon.cursor_factory = psycopg2.extras.DictCursor
  return dbcon

#############################################################################
def Version(dbcon, dbschema="public", fout=None):
  sql = ("SELECT * FROM {0}.dbversion".format(dbschema))
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  cur = dbcon.cursor()
  cur.execute(sql)
  row = cur.fetchone()
  tags = list(row.keys())
  fout.write("\t".join(tags)+"\n")
  fout.write("\t".join([str(row[tag]) for tag in tags])+"\n")

#############################################################################
def MetaListdbs(dbcon, fout=None):
  """Pg meta-command: list dbs from pg_database."""
  sql = ("SELECT pg_database.datname, pg_shdescription.description FROM pg_database LEFT OUTER JOIN pg_shdescription on pg_shdescription.objoid = pg_database.oid WHERE pg_database.datname ~ '^drug'")
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    fout.write("\t".join([str(row[tag]) for tag in tags])+"\n")

#############################################################################
def Describe(dbcon, dbschema="public", fout=None):
  '''Describing the schema.'''
  if fout:
    cur = dbcon.cursor()
    cur.execute(("SELECT table_name FROM information_schema.tables WHERE table_schema = %s"), (dbschema,))
    fout.write("schema\ttable\tcolumn\tdatatype\n")
    for row in cur:
      cur2 = dbcon.cursor()
      cur2.execute(("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema = %s AND table_name = %s"), (dbschema, row[0]))
      for row2 in cur2:
        fout.write("\t".join([dbschema, row[0], row2[0], row2[1]])+"\n")
      cur2.close()
    cur.close()
  else:
    df_out=None;
    sql1 = ("SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(dbschema))
    df1 = pandas.io.sql.read_sql_query(sql1, dbcon)
    for tname in df1.table_name:
      sql2 = ("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema = '{}' AND table_name = '{}'".format(dbschema, tname))
      df_this = pandas.io.sql.read_sql_query(sql2, dbcon)
      df_this["schema"] = dbschema
      df_this["table"] = tname
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
    df_out = df_out[["schema", "table", "column_name", "data_type"]]
    return df_out

#############################################################################
def Counts(dbcon, dbschema="public", fout=None):
  '''Listing the table rowcounts.'''
  if fout:
    n_table=0; n_row=0;
    cur = dbcon.cursor()
    cur.execute(("SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name"), (dbschema,))
    fout.write("schema\ttable\trowcount\n")
    cur2 = dbcon.cursor()
    for row in cur:
      n_table+=1
      cur2.execute("SELECT COUNT(*) FROM {}.{}".format(dbschema, row[0]))
      row2 = cur2.fetchone()
      n_row+=row2[0]
      fout.write("\t".join([dbschema, row[0], str(row2[0])])+"\n")
    cur2.close()
    cur.close()
    logging.info("Totals: tables: {}; rows: {}".format(n_table, n_row))
  else:
    df_out=None;
    sql1 = ("SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(dbschema))
    df1 = pandas.io.sql.read_sql_query(sql1, dbcon)
    for tname in df1.table_name:
      sql2 = ("SELECT COUNT(*) AS rowcount FROM {}.{}".format(dbschema, tname))
      df_this = pandas.io.sql.read_sql_query(sql2, dbcon)
      df_this["schema"] = dbschema
      df_this["table"] = tname
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
    df_out = df_out[["schema", "table", "rowcount"]]
    return df_out

#############################################################################
def ListStructures(dbcon, dbschema="public", fout=None):
  sql = ("SELECT id,name,cas_reg_no,smiles,inchikey,inchi,cd_formula AS formula,cd_molweight AS molweight FROM {}.structures".format(dbschema))
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {}".format(n_out))

#############################################################################
def ListStructures2Smiles(dbcon, dbschema="public", fout=None):
  sql = ("SELECT smiles, id, name FROM {0}.structures WHERE smiles IS NOT NULL".format(dbschema))
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; 
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    vals = [row["smiles"], str(row["id"]), row["name"]]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListStructures2Molfile(dbcon, dbschema="public", fout=None):
  n_out=0;
  cur = dbcon.cursor()
  cur.execute("SELECT molfile, id, name FROM {0}.structures WHERE molfile IS NOT NULL".format(dbschema))
  for row in cur:
    molfile = re.sub(r'^[\s]*\n', str(row["id"])+"\n", row["molfile"])
    fout.write(molfile)
    fout.write("> <DRUGCENTRAL_STRUCT_ID>\n"+str(row["id"])+"\n\n")
    fout.write("> <NAME>\n"+row["name"]+"\n\n")
    fout.write("$$$$\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListProducts(dbcon, dbschema="public", fout=None):
  sql = ("SELECT * FROM {0}.product".format(dbschema))
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListActiveIngredients(dbcon, dbschema="public", fout=None):
  sql = ("SELECT * FROM {0}.active_ingredient".format(dbschema))
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListXrefTypes(dbcon, fout=None):
  sql="""\
SELECT DISTINCT
	id AS "dc_xref_type_id",
	type AS "dc_xref_type",
	description AS "dc_xref_type_description"
FROM
	id_type
ORDER BY
	dc_xref_type
"""
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {}".format(n_out))

#############################################################################
def ListIndications(dbcon, fout=None):
  sql="""\
SELECT DISTINCT
	omop.concept_id omop_concept_id,
	omop.concept_name omop_concept_name,
	omop.umls_cui,
	omop.cui_semantic_type umls_semantic_type,
	omop.snomed_conceptid,
	omop.snomed_full_name
FROM
	omop_relationship omop
JOIN
	structures s ON omop.struct_id = s.id
WHERE
	omop.relationship_name = 'indication'
"""
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {}".format(n_out))

#############################################################################
def ListIndicationTargets(dbcon, fout=None):
  sql="""\
SELECT DISTINCT
	omop.concept_name AS omop_concept,
	omop.umls_cui,
	atf.struct_id,
	s.name AS struct_name,
	atf.target_id,
	atf.target_name,
	atf.gene,
	atf.action_type,
	atf.act_source,
	atf.act_type,
	atf.act_comment,
	atf.relation,
	atf.moa,
	atf.moa_source,
	atf.moa_source_url,
	r.pmid AS ref_pmid,
	r.doi AS ref_doi,
	r.title AS ref_title,
	r.dp_year AS ref_year
FROM
	act_table_full atf
	JOIN structures s ON s.id = atf.struct_id
	JOIN omop_relationship omop ON omop.struct_id = s.id
	LEFT OUTER JOIN reference r ON r.id = atf.moa_ref_id
WHERE
	omop.relationship_name = 'indication'
"""
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {}".format(n_out))

#############################################################################
def ListDrugdruginteractions(dbcon, fout=None):
  sql="""\
SELECT
	ddi.id AS ddi_id,
	ddi.drug_class1,
	ddi.drug_class2,
	ddi.source_id,
	drug_class1.id drug_class_id1,
	drug_class1.source source1,
	drug_class1.is_group is_group1,
	drug_class2.id drug_class_id2,
	drug_class2.source source2,
	drug_class2.is_group is_group2
FROM
	ddi
JOIN drug_class drug_class1 ON drug_class1.name = ddi.drug_class1
JOIN drug_class drug_class2 ON drug_class2.name = ddi.drug_class2
"""
  if not fout: return pandas.io.sql.read_sql_query(sql, dbcon)
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute(sql)
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {}".format(n_out))

#############################################################################
def SearchIndications(dbcon, terms, fout=None):
  """Search names via Pg regular expression (SIMILAR TO)."""
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  for term in terms:
    sql="""\
SELECT DISTINCT
	omop.concept_id omop_concept_id,
	omop.concept_name omop_concept_name,
	omop.umls_cui,
	omop.cui_semantic_type umls_semantic_type,
	omop.snomed_conceptid,
	omop.snomed_full_name
FROM
	omop_relationship omop
JOIN
	structures s ON omop.struct_id = s.id
WHERE
	omop.relationship_name = 'indication'
	AND (omop.concept_name ~* '{0}' OR omop.snomed_full_name ~* '{0}')
""".format(term)
    if fout:
      cur.execute(sql)
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql, dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])

  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetIndicationStructures(dbcon, ids, fout=None):
  """Input OMOP conceptIds."""
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql="""\
SELECT DISTINCT
	omop.concept_id omop_concept_id,
	omop.concept_name omop_concept_name,
	s.id struct_id,
	s.name struct_name,
	s.smiles,
	s.inchikey,
	s.inchi,
	s.cd_formula,
	s.cd_molweight
FROM
	omop_relationship omop
JOIN
	structures s ON omop.struct_id = s.id
WHERE
	omop.relationship_name = 'indication'
	AND omop.concept_id = '{}'
"""
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructure(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql = ("""SELECT id,name,cas_reg_no,smiles,inchikey,inchi,cd_formula AS formula,cd_molweight AS molweight FROM structures WHERE id = '{}'""")
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructureByXref(dbcon, xref_type, ids, fout=None):
  if not xref_type:
    logging.error("xref_type required.")
    return None
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql = ("""SELECT idn.identifier xref, idn.id_type xref_type, s.id dc_struct_id, s.name dc_struct_name FROM structures AS s JOIN identifier AS idn ON idn.struct_id=s.id WHERE idn.id_type = '"""+xref_type+"""' AND idn.identifier = '{}'""")
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructureBySynonym(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql = ("""SELECT str.id, str.name structure_name, syn.name synonym FROM structures AS str JOIN synonyms AS syn ON syn.id=str.id WHERE syn.name = '{}'""")
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructureIds(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql = ("""SELECT struct_id, id_type, identifier AS id FROM identifier WHERE struct_id = '{}'""")
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructureProducts(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql="""\
SELECT DISTINCT
	s.id struct_id,
	s.name struct_name,
	s.smiles,
	s.inchikey,
	p.id product_id,
	p.ndc_product_code,
	p.form product_form,
	p.generic_name product_generic_name,
	p.product_name,
	p.route product_route,
	p.marketing_status product_marketing_status,
	p.active_ingredient_count product_active_ingredient_count
FROM
	structures AS s
JOIN 
	active_ingredient ai ON ai.struct_id = s.id
JOIN 
	product p ON p.ndc_product_code = ai.ndc_product_code
WHERE 
	s.id = '{}'
"""
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructureOBProducts(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql="""\
SELECT DISTINCT
	s.id struct_id,
	s.name struct_name,
	s.smiles,
	s.inchikey,
	ob.id ob_id,
	ob.product_no ob_product_no,
	ob.ingredient,
	ob.dose_form,
	ob.route,
	ob.strength,
	ob.appl_type,
	ob.appl_no
FROM
	structures s
	JOIN struct2obprod s2ob ON s2ob.struct_id = s.id
	JOIN ob_product ob ON ob.id = s2ob.prod_id
WHERE 
	s.id = '{}'
"""
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetStructureAtcs(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql="""\
SELECT DISTINCT
	s.id struct_id,
	s.name struct_name,
	s.smiles,
	s.inchikey,
	atc.code AS atc_code,
	atc.l1_code AS atc_l1_code,
	atc.l1_name AS atc_l1_name,
	atc.l2_code AS atc_l2_code,
	atc.l2_name AS atc_l2_name,
	atc.l3_code AS atc_l3_code,
	atc.l3_name AS atc_l3_name,
	atc.l4_code AS atc_l4_code,
	atc.l4_name AS atc_l4_name,
	atc.chemical_substance AS atc_substance
FROM
	structures AS s
JOIN 
	struct2atc ON struct2atc.struct_id = s.id
JOIN 
	atc ON atc.id = struct2atc.id
WHERE 
	s.id = '{}'
"""
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
def GetProductStructures(dbcon, ids, fout=None):
  n_out=0; tags=None; df_out=None;
  cur = dbcon.cursor()
  sql="""\
SELECT DISTINCT
	p.id product_id,
	p.product_name,
	s.id struct_id,
	s.name struct_name,
	s.smiles,
	s.inchikey,
	s.inchi,
	s.cd_formula,
	s.cd_molweight
FROM
	product p
JOIN 
	active_ingredient ai ON p.ndc_product_code = ai.ndc_product_code
JOIN 
	structures s ON ai.struct_id = s.id
WHERE 
	p.id = '{}'
"""
  for id_this in ids:
    if fout:
      cur.execute(sql.format(id_this))
      for row in cur:
        if not tags:
          tags = list(row.keys())
          fout.write("\t".join(tags)+"\n")
        vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
    else:
      df_this = pandas.io.sql.read_sql_query(sql.format(id_this), dbcon)
      df_out = df_this if df_out is None else pandas.concat([df_out, df_this])
  if fout: logging.info("n_out: {}".format(n_out))
  else: return df_out

#############################################################################
