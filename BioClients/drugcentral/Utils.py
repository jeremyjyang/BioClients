#!/usr/bin/env python3
"""
DrugCentral db utility functions.
"""
import os,sys,re,logging
import psycopg2,psycopg2.extras

#############################################################################
def Connect(dbhost, dbport, dbname, dbusr, dbpw):
  """Connect to db; specify default cursor type DictCursor."""
  dsn = ("host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(dbhost, dbport, dbname, dbusr, dbpw))
  dbcon = psycopg2.connect(dsn)
  dbcon.cursor_factory = psycopg2.extras.DictCursor
  return dbcon

#############################################################################
def Version(dbcon, dbschema, fout):
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM {0}.dbversion".format(dbschema))
  row = cur.fetchone()
  tags = list(row.keys())
  fout.write("\t".join(tags)+"\n")
  fout.write("\t".join([str(row[tag]) for tag in tags])+"\n")

#############################################################################
def Describe(dbcon, dbschema, fout):
  '''Describing the schema.'''
  cur = dbcon.cursor()
  cur.execute(("SELECT table_name FROM information_schema.tables WHERE table_schema = %s"), (dbschema,))
  fout.write("schema\ttable\tcolumn\tdatatype\n")
  cur2 = dbcon.cursor()
  for row in cur:
    cur2.execute(("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema = %s AND table_name = %s"), (dbschema, row[0]))
    for row2 in cur2:
      fout.write("\t".join([dbschema, row[0], row2[0], row2[1]])+"\n")
  cur2.close()
  cur.close()

#############################################################################
def Counts(dbcon, dbschema, fout):
  '''Listing the table rowcounts.'''
  n_table=0; n_row=0;
  cur = dbcon.cursor()
  cur.execute(("SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name"), (dbschema,))
  fout.write("schema\ttable\trowcount\n")
  cur2 = dbcon.cursor()
  for row in cur:
    n_table+=1
    cur2.execute("SELECT count(*) FROM {0}.{1}".format(dbschema, row[0]))
    row2 = cur2.fetchone()
    n_row+=row2[0]
    fout.write("\t".join([dbschema, row[0], str(row2[0])])+"\n")
  cur2.close()
  cur.close()
  logging.info("Totals: tables: {0}; rows: {1}".format(n_table, n_row))

#############################################################################
def ListStructures(dbcon, dbschema, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM {0}.structures".format(dbschema))
  for row in cur:
    if not tags:
      tags = list(row.keys())
      tags.remove("molfile")
      tags.remove("molimg")
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListStructures2Smiles(dbcon, dbschema, fout):
  n_out=0; 
  cur = dbcon.cursor()
  cur.execute("SELECT smiles, id, name FROM {0}.structures WHERE smiles IS NOT NULL".format(dbschema))
  for row in cur:
    vals = [row["smiles"], str(row["id"]), row["name"]]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListStructures2Molfile(dbcon, dbschema, fout):
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
def ListProducts(dbcon, dbschema, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM {0}.product".format(dbschema))
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListActiveIngredients(dbcon, dbschema, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM {0}.active_ingredient".format(dbschema))
  for row in cur:
    if not tags:
      tags = list(row.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def ListIndications(dbcon, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
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
def SearchIndications(dbcon, terms, fout):
  """Search names via Pg regular expression (SIMILAR TO)."""
  n_out=0; tags=None;
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
def GetIndicationStructures(dbcon, ids, fout):
  """Input OMOP conceptIds."""
  n_out=0; tags=None;
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
	AND omop.concept_id = %s
"""
  for id_this in ids:
    cur.execute(sql, (id_this,))
    for row in cur:
      if not tags:
        tags = list(row.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def GetStructure(dbcon, ids, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
  for id_this in ids:
    cur.execute(("SELECT * FROM structures WHERE id = %s"), (id_this,))
    for row in cur:
      if not tags:
        tags = list(row.keys())
        tags.remove("molfile")
        tags.remove("molimg")
        fout.write("\t".join(tags)+"\n")
      vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def GetStructureBySynonym(dbcon, ids, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
  for id_this in ids:
    cur.execute(("SELECT str.id, str.name structure_name, syn.name synonym FROM structures AS str JOIN synonyms AS syn ON syn.id=str.id WHERE syn.name = %s"), (id_this,))
    for row in cur:
      if not tags:
        tags = list(row.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def GetStructureIds(dbcon, ids, fout):
  n_out=0; tags=None;
  cur = dbcon.cursor()
  sql="""\
SELECT
	struct_id,
	id_type,
	identifier AS id
FROM
	identifier
WHERE 
	struct_id = %s
"""
  for id_this in ids:
    cur.execute(sql, (id_this,))
    for row in cur:
      if not tags:
        tags = list(row.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def GetStructureProducts(dbcon, ids, fout):
  n_out=0; tags=None;
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
	s.id = %s
"""
  for id_this in ids:
    cur.execute(sql, (id_this,))
    for row in cur:
      if not tags:
        tags = list(row.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
def GetProductStructures(dbcon, ids, fout):
  n_out=0; tags=None;
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
	p.id = %s
"""
  for id_this in ids:
    cur.execute(sql, (id_this,))
    for row in cur:
      if not tags:
        tags = list(row.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [("{:.3f}".format(row[tag]) if type(row[tag]) is float else '' if row[tag] is None else str(row[tag])) for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: {0}".format(n_out))

#############################################################################
