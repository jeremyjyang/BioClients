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
