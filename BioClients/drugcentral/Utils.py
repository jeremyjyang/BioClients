#!/usr/bin/env python3
"""
DrugCentral db utility functions.
"""
import os,sys,re,json,logging,yaml,tqdm
import pandas as pd
import psycopg2,psycopg2.extras

NCHUNK=100

#############################################################################
def Connect(dbhost, dbport, dbname, dbusr, dbpw):
  """Connect to db; specify default cursor type DictCursor."""
  dsn = (f"host='{dbhost}' port='{dbport}' dbname='{dbname}' user='{dbusr}' password='{dbpw}'")
  dbcon = psycopg2.connect(dsn)
  dbcon.cursor_factory = psycopg2.extras.DictCursor
  return dbcon

#############################################################################
def Version(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT * FROM {dbschema}.dbversion")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

#############################################################################
def MetaListdbs(dbcon, fout=None):
  """Pg meta-command: list dbs from pg_database."""
  sql = ("SELECT pg_database.datname, pg_shdescription.description FROM pg_database LEFT OUTER JOIN pg_shdescription on pg_shdescription.objoid = pg_database.oid WHERE pg_database.datname ~ '^drug'")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

#############################################################################
def ListColumns(dbcon, dbschema="public", fout=None):
  df=None;
  sql1 = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dbschema}'")
  df1 = pd.read_sql(sql1, dbcon)
  for tname in df1.table_name:
    sql2 = (f"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema = '{dbschema}' AND table_name = '{tname}'")
    df_this = pd.read_sql(sql2, dbcon)
    df_this["schema"] = dbschema
    df_this["table"] = tname
    df = df_this if df is None else pd.concat([df, df_this])
  df = df[["schema", "table", "column_name", "data_type"]]
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListTables(dbcon, dbschema="public", fout=None):
  '''Listing the tables.'''
  sql = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dbschema}'")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListTablesRowCounts(dbcon, dbschema="public", fout=None):
  '''Listing the table rowcounts.'''
  df=None;
  sql1 = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dbschema}'")
  df1 = pd.read_sql(sql1, dbcon)
  for tname in df1.table_name:
    sql2 = (f"SELECT COUNT(*) AS rowcount FROM {dbschema}.{tname}")
    df_this = pd.read_sql(sql2, dbcon)
    df_this["schema"] = dbschema
    df_this["table"] = tname
    df = df_this if df is None else pd.concat([df, df_this])
  df = df[["schema", "table", "rowcount"]]
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListStructures(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT id,name,cas_reg_no,smiles,inchikey,inchi,cd_formula AS formula,cd_molweight AS molweight FROM {dbschema}.structures")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListStructures2Smiles(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT smiles, id, name FROM {dbschema}.structures WHERE smiles IS NOT NULL")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListStructures2Xref(dbcon, xref_type, dbschema="public", fout=None):
  df=None; n_out=0;
  sql = f"""\
SELECT
	structures.id struct_id,
	structures.smiles,
	structures.name dc_struct_name,
	identifier.identifier {xref_type.lower()}
FROM
	structures
	JOIN identifier ON identifier.struct_id = structures.id 
WHERE
	identifier.id_type = '{xref_type}'
"""
  logging.debug(f"SQL: {sql}")
  df_itr = pd.read_sql(sql, dbcon, chunksize=NCHUNK)
  for df_this in df_itr:
    if fout is not None: df_this.to_csv(fout, sep="\t", index=False)
    else: df = pd.concat([df, df_this])
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListStructures2Pubchem(dbcon, dbschema="public", fout=None):
  return ListStructures2Xref(dbcon, "PUBCHEM_CID", dbschema, fout)

#############################################################################
def ListStructures2Chembl(dbcon, dbschema="public", fout=None):
  return ListStructures2Xref(dbcon, "ChEMBL_ID", dbschema, fout)

#############################################################################
def ListStructures2Molfile(dbcon, dbschema="public", fout=None):
  """fout is required arg."""
  n_out=0;
  cur = dbcon.cursor()
  cur.execute(f"SELECT molfile, id, name FROM {dbschema}.structures WHERE molfile IS NOT NULL")
  for row in cur:
    molfile = re.sub(r'^[\s]*\n', str(row["id"])+"\n", row["molfile"])
    fout.write(molfile)
    fout.write("> <DRUGCENTRAL_STRUCT_ID>\n"+str(row["id"])+"\n\n")
    fout.write("> <NAME>\n"+row["name"]+"\n\n")
    fout.write("$$$$\n")
    n_out+=1
  logging.info(f"n_out: {n_out}")

#############################################################################
def ListProducts(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT * FROM {dbschema}.product")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListActiveIngredients(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT * FROM {dbschema}.active_ingredient")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListXrefTypes(dbcon, fout=None):
  sql="""\
SELECT DISTINCT
	id AS xref_type_id,
	type AS xref_type,
	description AS xref_type_description
FROM
	id_type
ORDER BY
	xref_type
"""
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListXrefs(dbcon, fout=None):
  df=None; n_out=0; tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  N_row = pd.read_sql("SELECT COUNT(*) FROM identifier", dbcon).iloc[0,0]
  sql="""\
SELECT
	identifier.struct_id,
	identifier.id_type xref_type,
	identifier.identifier xref,
	s.name dc_struct_name
FROM
	identifier
	JOIN structures s ON s.id=identifier.struct_id
"""
  df_itr = pd.read_sql(sql, dbcon, chunksize=NCHUNK)
  for df_this in df_itr:
    if not quiet and tq is None: tq = tqdm.tqdm(total=N_row)
    if fout is not None: df_this.to_csv(fout, sep="\t", header=bool(n_out==0), index=False)
    else: df = pd.concat([df, df_this])
    if tq is not None: tq.update(df_this.shape[0])
    n_out += df_this.shape[0]
  if tq is not None: tq.close()
  logging.info(f"rows: {n_out}")
  return df

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
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureIndications(dbcon, ids, fout=None):
  df=None;
  sql = ("""\
SELECT omop.struct_id,
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
	omop.struct_id = '{}'
AND
	omop.relationship_name = 'indication'
""")
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

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
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

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
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def SearchProducts(dbcon, terms, fout=None):
  """Search names via Pg regular expression (SIMILAR TO)."""
  df=None;
  for term in terms:
    sql= f"""\
SELECT DISTINCT
	s.id struct_id,
	s.name struct_name,
	p.id product_id,
	p.ndc_product_code,
	p.form product_form,
	p.generic_name product_generic_name,
	p.product_name,
	p.route product_route
FROM
	structures AS s
JOIN 
	active_ingredient ai ON ai.struct_id = s.id
JOIN 
	product p ON p.ndc_product_code = ai.ndc_product_code
WHERE
	p.product_name.name ~* '{term}' OR p.generic_name product_generic_name ~* '{term}' 
"""
    logging.debug(f"SQL: {sql}")
    df_this = pd.read_sql(sql, dbcon)
    df = pd.concat([df, df_this])
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def SearchIndications(dbcon, terms, fout=None):
  """Search names via Pg regular expression (SIMILAR TO)."""
  df=None;
  for term in terms:
    sql=f"""\
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
	AND (omop.concept_name ~* '{term}' OR omop.snomed_full_name ~* '{term}')
"""
    logging.debug(f"SQL: {sql}")
    df_this = pd.read_sql(sql, dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetIndicationStructures(dbcon, ids, fout=None):
  """Input OMOP conceptIds (INTEGER)."""
  df=None;
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
	AND omop.concept_id = {}
"""
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructure(dbcon, ids, fout=None):
  df=None;
  sql = ("""SELECT id,name,cas_reg_no,smiles,inchikey,inchi,cd_formula AS formula,cd_molweight AS molweight FROM structures WHERE id = '{}'""")
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetDrugPage(dbcon, struct_id, fout=None):
  """Structure, with IDs, names, xrefs, and ATCs, products; JSON output."""
  df_struct = GetStructure(dbcon, [struct_id], None) # Should return one row.
  if df_struct.empty: return None
  drug = df_struct.to_dict(orient='records')[0]

  #Add xrefs
  df_xrefs = GetStructureXrefs(dbcon, [struct_id], None)
  drug["xrefs"] = df_xrefs[["xref_type", "xref"]].to_dict(orient='records')

  #Add names
  df_names = GetStructureSynonyms(dbcon, [struct_id], None)
  drug["synonyms"] = df_names["synonym"].tolist()

  #Add ATCs 
  df_atcs = GetStructureAtcs(dbcon, [struct_id], None)
  if not df_atcs.empty:
    drug["atcs"] = df_atcs[["atc_code","atc_l1_code","atc_l1_name","atc_l2_code","atc_l2_name","atc_l3_code","atc_l3_name","atc_l4_code","atc_l4_name","atc_substance"]].to_dict(orient='records')

  #Add products 
  df_products = GetStructureProducts(dbcon, [struct_id], None)
  if not df_products.empty:
    drug["products"] = df_products[["product_id","ndc_product_code","product_form","product_generic_name","product_name","product_route","product_marketing_status","product_active_ingredient_count"]].to_dict(orient='records')

  #Add targets 
  df_targets = GetStructureTargets(dbcon, [struct_id], None)
  if not df_targets.empty:
    drug["targets"] = df_targets[["target_id","target_name","gene","action_type","act_source","act_type","act_comment","relation","moa","moa_source","moa_source_url","ref_pmid","ref_doi","ref_title","ref_year"]].to_dict(orient='records')

  #Add indications
  df_indications = GetStructureIndications(dbcon, [struct_id], None)
  if not df_indications.empty:
    drug["indications"] = df_indications[["omop_concept_id","omop_concept_name","umls_cui","umls_semantic_type","snomed_conceptid","snomed_full_name"]].to_dict(orient='records')
 
  if fout is not None:
    fout.write(json.dumps(drug, indent=2))
  return drug

#############################################################################
def GetDrugSummary(dbcon, ids, fout):
  """Structure, with IDs, names, xrefs, and ATCs, products; TSV output."""
  n_out=0; df=None;
  for id_this in ids:
    drug = GetDrugPage(dbcon, id_this)
    pubchem_cid=None; chembl_id=None; drugbank_id=None;
    xrefs = drug["xrefs"] if "xrefs" in drug else []
    for xref in xrefs:
      if xref["xref_type"] == "PUBCHEM_CID": pubchem_cid = xref["xref"]
      if xref["xref_type"] == "ChEMBL_ID": chembl_id = xref["xref"]
      if xref["xref_type"] == "DRUGBANK_ID": drugbank_id = xref["xref"]
    synonyms_str = ";".join(drug["synonyms"] if "synonyms" in drug else [])
    atcs = drug["atcs"] if "atcs" in drug else []
    atc_l3s = set();
    for j,atc in enumerate(atcs):
      l3_code = atc["atc_l3_code"] if "atc_l3_code" in atc else ""
      l3_name = atc["atc_l3_name"] if "atc_l3_name" in atc else ""
      atc_l3s.add(f"{l3_code}:{l3_name}")
    atcs_str = ";".join(list(atc_l3s))
    products = drug["products"] if "products" in drug else []
    targets = drug["targets"] if "targets" in drug else []
    indications = drug["indications"] if "indications" in drug else []
    dcid = drug["id"] if "id" in drug else None
    df = pd.concat([df, pd.DataFrame({
	"drugcentral_id":[dcid],
	"drugcentral_url":[f"https://drugcentral.org/drugcard/{dcid}"],
	"name":[drug["name"] if "name" in drug else None],
	"cas_reg_no":[drug["cas_reg_no"] if "cas_reg_no" in drug else None],
	"smiles":[drug["smiles"] if "smiles" in drug else None],
	"inchi":[drug["inchi"] if "inchi" in drug else None],
	"inchikey":[drug["inchikey"] if "inchikey" in drug else None],
	"formula":[drug["formula"] if "formula" in drug else None],
	"pubchem_cid":[pubchem_cid],
	"chembl_id":[chembl_id],
	"drugbank_id":[drugbank_id],
	"synonyms":[synonyms_str],
	"atcs":[atcs_str],
	"product_count":pd.Series([len(products)]).astype(int),
	"target_count":pd.Series([len(targets)]).astype(int),
	"indication_count":pd.Series([len(indications)]).astype(int),
	})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureByXref(dbcon, ids, xref_type=None, fout=None):
  if not xref_type:
    logging.error("xref_type required.")
    return None
  df=None;
  sql = ("""\
SELECT
	identifier.identifier xref,
	identifier.id_type xref_type,
	s.id dc_struct_id,
	s.name dc_struct_name
FROM
	structures AS s
	JOIN identifier ON identifier.struct_id=s.id
WHERE
	identifier.identifier = '{0}'
""")
  if xref_type is not None:
    sql += f" AND identifier.id_type = '{xref_type}'"
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureBySynonym(dbcon, ids, fout=None):
  df=None;
  sql = ("""SELECT str.id, str.name structure_name, syn.name synonym FROM structures AS str JOIN synonyms AS syn ON syn.id=str.id WHERE syn.name = '{}'""")
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureXrefs(dbcon, ids, fout=None):
  df=None;
  sql = ("""SELECT struct_id, id_type AS xref_type, identifier AS xref FROM identifier WHERE struct_id = '{}'""")
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureProducts(dbcon, ids, fout=None):
  df=None;
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
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureOBProducts(dbcon, ids, fout=None):
  df=None;
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
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureTargets(dbcon, ids, fout=None):
  df=None; n_out=0;
  sql="""\
SELECT DISTINCT
	atf.struct_id,
	atf.target_id,
	atf.target_name,
	atf.accession,
	atf.tdl,
	atf.gene,
	atf.action_type,
	atf.act_source,
	atf.act_value,
	atf.act_unit,
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
	LEFT OUTER JOIN reference r ON r.id = atf.moa_ref_id
WHERE
	atf.struct_id = {}
"""
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListAtcs(dbcon, fout=None):
  """List ATC codes and drug count for which drugs exist."""
  sql="""\
SELECT DISTINCT
	atc.l1_code atc_l1_code, atc.l1_name atc_l1_name,
	atc.l2_code atc_l2_code, atc.l2_name atc_l2_name,
	atc.l3_code atc_l3_code, atc.l3_name atc_l3_name,
	atc.l4_code atc_l4_code, atc.l4_name atc_l4_name,
	COUNT(DISTINCT s.id) drug_count
FROM
	atc
JOIN 
	struct2atc ON struct2atc.id = atc.id
JOIN 
	structures s ON s.id = struct2atc.struct_id
GROUP BY
	atc.l1_code, atc.l1_name,
	atc.l2_code, atc.l2_name,
	atc.l3_code, atc.l3_name,
	atc.l4_code, atc.l4_name
ORDER BY
	atc.l1_name, atc.l2_name, atc.l3_name, atc.l4_name
"""
  logging.debug(sql)
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListSynonyms(dbcon, fout=None):
  df=None; n_out=0; tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  N_row = pd.read_sql("SELECT COUNT(*) FROM synonyms", dbcon).iloc[0,0]
  sql="""\
SELECT
	id struct_id,
	synonyms.name AS synonym
FROM
	synonyms
ORDER BY
	id
"""
  df_itr = pd.read_sql(sql, dbcon, chunksize=NCHUNK)
  for df_this in df_itr:
    if not quiet and tq is None: tq = tqdm.tqdm(total=N_row)
    if fout is not None: df_this.to_csv(fout, sep="\t", header=bool(n_out==0), index=False)
    else: df = pd.concat([df, df_this])
    if tq is not None: tq.update(df_this.shape[0])
    n_out += df_this.shape[0]
  if tq is not None: tq.close()
  logging.info(f"rows: {n_out}")
  return df

#############################################################################
def GetStructureSynonyms(dbcon, ids, fout=None):
  df=None;
  sql="""\
SELECT DISTINCT
	s.id struct_id,
	s.name struct_name,
	synonyms.name AS synonym
FROM
	structures AS s
JOIN 
	synonyms ON synonyms.id = s.id
WHERE 
	s.id = '{}'
"""
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructureAtcs(dbcon, ids, fout=None):
  df=None;
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
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = df_this if df is None else pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetProductStructures(dbcon, ids, fout=None):
  df=None;
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
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
