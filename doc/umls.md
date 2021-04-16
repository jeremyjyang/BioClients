# `BioClients.umls`

##  UMLS

### Dependencies

* Python packages: `lxml`, `pyyaml`, `pyquery` 

UMLS REST API client
UTS = UMLS Technology Services

From the NIH National Library of Medicine (NLM).

* Registration is required for both browser and API access.  See
<https://www.nlm.nih.gov/research/umls/>. To use
[BioClients.umls.Client](BioClients/umls/Client.py), create `~/.umls.yaml` with
format:

```
API_KEY: "===REPLACE-WITH-KEY-HERE==="
```

 <https://documentation.uts.nlm.nih.gov/rest/home.html>
 <https://documentation.uts.nlm.nih.gov/rest/authentication.html>
 <https://documentation.uts.nlm.nih.gov/rest/concept/>
 <https://documentation.uts.nlm.nih.gov/rest/source-asserted-identifiers/>
 <https://documentation.uts.nlm.nih.gov/rest/search/>
 <https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html>

 TGT = Ticket Granting Ticket
 (API requires one ticket per request.)
 CUI = Concept Unique Identifier
 Atom is a term in a source.
 Term-to-concept is many to one.

 Retrieves information for a known Semantic Type identifier (TUI)
 /semantic-network/{version}/TUI/{id}
 (DOES NOT SEARCH FOR INSTANCES OF THIS TYPE -- RETURNS METADATA ONLY.)
 Example TUIs:
 CHEM|Chemicals & Drugs|T116|Amino Acid, Peptide, or Protein
 CHEM|Chemicals & Drugs|T195|Antibiotic
 CHEM|Chemicals & Drugs|T123|Biologically Active Substance
 CHEM|Chemicals & Drugs|T122|Biomedical or Dental Material
 CHEM|Chemicals & Drugs|T103|Chemical
 CHEM|Chemicals & Drugs|T120|Chemical Viewed Functionally
 CHEM|Chemicals & Drugs|T104|Chemical Viewed Structurally
 CHEM|Chemicals & Drugs|T200|Clinical Drug
 CHEM|Chemicals & Drugs|T126|Enzyme
 CHEM|Chemicals & Drugs|T125|Hormone
 CHEM|Chemicals & Drugs|T129|Immunologic Factor
 CHEM|Chemicals & Drugs|T130|Indicator, Reagent, or Diagnostic Aid
 CHEM|Chemicals & Drugs|T114|Nucleic Acid, Nucleoside, or Nucleotide
 CHEM|Chemicals & Drugs|T109|Organic Chemical
 CHEM|Chemicals & Drugs|T121|Pharmacologic Substance
 CHEM|Chemicals & Drugs|T192|Receptor
 CHEM|Chemicals & Drugs|T127|Vitamin
 DISO|Disorders|T020|Acquired Abnormality
 DISO|Disorders|T190|Anatomical Abnormality
 DISO|Disorders|T049|Cell or Molecular Dysfunction
 DISO|Disorders|T019|Congenital Abnormality
 DISO|Disorders|T047|Disease or Syndrome
 DISO|Disorders|T050|Experimental Model of Disease
 DISO|Disorders|T033|Finding
 DISO|Disorders|T037|Injury or Poisoning
 DISO|Disorders|T048|Mental or Behavioral Dysfunction
 DISO|Disorders|T191|Neoplastic Process
 DISO|Disorders|T046|Pathologic Function
 DISO|Disorders|T184|Sign or Symptom
 GENE|Genes & Molecular Sequences|T087|Amino Acid Sequence
 GENE|Genes & Molecular Sequences|T088|Carbohydrate Sequence
 GENE|Genes & Molecular Sequences|T028|Gene or Genome
 GENE|Genes & Molecular Sequences|T085|Molecular Sequence
 GENE|Genes & Molecular Sequences|T086|Nucleotide Sequence

 <https://github.com/HHS/uts-rest-api>
 <https://utslogin.nlm.nih.gov>
 <https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html>
 
 Some term types:
 
  CE : Entry term for a Supplementary Concept
  ET : Entry term
  FN : Full form of descriptor
  HG : High Level Group Term
  HT : Hierarchical term
  LLT : Lower Level Term
  MH : Main heading
  MTH\_FN : MTH Full form of descriptor
  MTH\_HG : MTH High Level Group Term
  MTH\_HT : MTH Hierarchical term
  MTH\_LLT : MTH Lower Level Term
  MTH\_OS : MTH System-organ class
  MTH\_PT : Metathesaurus preferred term
  MTH\_SY : MTH Designated synonym
  NM : Name of Supplementary Concept
  OS : System-organ class
  PCE : Preferred entry term for Supplementary Concept
  PEP : Preferred entry term
  PM : Machine permutation
  PT : Designated preferred name
  PTGB : British preferred term
  SY : Designated synonym
  SYGB : British synonym
  
 Some relationships:

  RB : has a broader relationship
  RL : the relationship is similar or "alike". 
  RN : has a narrower relationship
  RO : has relationship other than synonymous, narrower, or broader
  RQ : related and possibly synonymous.
  RU : Related, unspecified
  SY : source asserted synonymy.

## Example commands

```
python3 -m BioClients.umls.Client -h
usage: Client.py [-h] [--id ID] [--idfile IDFILE] [--o OFILE] [--idsrc IDSRC]
                 [--searchType {exact,words,leftTruncation,rightTruncation,approximate,normalizedString}]
                 [--inputType {atom,code,sourceConcept,sourceDescriptor,sourceUi,tty}]
                 [--returnIdType {aui,concept,code,sourceConcept,sourceDescriptor,sourceUi}]
                 [--srcs SRCS] [--searchQuery SEARCHQUERY] [--skip SKIP]
                 [--nmax NMAX] [--api_version API_VERSION]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH]
                 [--api_auth_host API_AUTH_HOST]
                 [--api_auth_endpoint API_AUTH_ENDPOINT]
                 [--api_auth_service API_AUTH_SERVICE]
                 [--param_file PARAM_FILE] [--api_key API_KEY] [-v]
                 {getCodes,getAtoms,getRelations,listSources,xrefConcept,search,searchByTUI}

UMLS REST API client utility

positional arguments:
  {getCodes,getAtoms,getRelations,listSources,xrefConcept,search,searchByTUI}
                        OPERATION (select one)

optional arguments:
  -h, --help            show this help message and exit
  --id ID               ID (ex:C0018787)
  --idfile IDFILE       input IDs
  --o OFILE             output (TSV)
  --idsrc IDSRC         query ID source (default: CUI)
  --searchType {exact,words,leftTruncation,rightTruncation,approximate,normalizedString}
                        [words]
  --inputType {atom,code,sourceConcept,sourceDescriptor,sourceUi,tty}
                        [atom]
  --returnIdType {aui,concept,code,sourceConcept,sourceDescriptor,sourceUi}
                        [concept]
  --srcs SRCS           sources to include in response [ATC,HPO,ICD10,ICD10CM,I
                        CD9CM,MDR,MSH,MTH,NCI,OMIM,RXNORM,SNOMEDCT_US,WHO]
  --searchQuery SEARCHQUERY
                        string or code
  --skip SKIP
  --nmax NMAX
  --api_version API_VERSION
                        API version current
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --api_auth_host API_AUTH_HOST
  --api_auth_endpoint API_AUTH_ENDPOINT
  --api_auth_service API_AUTH_SERVICE
  --param_file PARAM_FILE
  --api_key API_KEY     API key
  -v, --verbose

All get* operations require --idsrc CUI, CUIs as inputs; CUI = Concept Unique
Identifier.
```

```
python3 -m BioClients.umls.Client getCodes --id C0018787
CUI	src	atom_code	atom_name
C0018787	MSH	D006321	Heart
C0018787	MSH	D006321	Hearts
C0018787	MTH	NOCODE	Heart
C0018787	NCI	C12727	Cardiac
C0018787	NCI	C12727	Heart
C0018787	NCI	TCGA	Heart
C0018787	OMIM	MTHU000110	Heart
C0018787	SNOMEDCT_US	80891009	Cardiac structure
C0018787	SNOMEDCT_US	80891009	Heart structure
C0018787	SNOMEDCT_US	80891009	Heart
C0018787	SNOMEDCT_US	80891009	Heart structure (body structure)
INFO:n_cui: 1
INFO:n_out: 11
```

```
python3 -m BioClients.umls.Client getAtoms --id C0018787
```

```
python3 -m BioClients.umls.Client search --searchType words --searchQuery "Parkinson"
python3 -m BioClients.umls.Client search --searchType leftTruncation --searchQuery "Alzheimer"
```
