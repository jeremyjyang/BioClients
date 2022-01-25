# `BioClients.pubchem`

Tools for obtaining and processing PubChem data (REST, SOAP, FTP).

* <https://pubchem.ncbi.nlm.nih.gov>

## PUG-REST

* <https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest>
* <https://pubchem.ncbi.nlm.nih.gov/rest/pug>

```
python3 -m BioClients.pubchem.Client --name remdesivir name2sid
python3 -m BioClients.pubchem.Client --name remdesivir name2cid
```

## PUG-SOAP

The SOAP API was developed first, and includes functionality not available
via PUG-REST (e.g. Standardize, IDExchange).

PUG SOAP services include:

* PubChem Identifier Exchange Service (PIES), https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi
* PubChem Standardization Service, https://pubchem.ncbi.nlm.nih.gov/standardize/standardize.cgi
* PubChem Structure Search, <https://pubchem.ncbi.nlm.nih.gov/search/search.cgi>. See Save Query button for template XML.

* <https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap>
* <https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap-reference>
* <https://pubchem.ncbi.nlm.nih.gov/pug_soap/pug_soap.cgi?wsdl>


```
python3 -m BioClients.pubchem.soap.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--operator {same,parent,samepar}]
                 [--ids IDS] [--query_id QUERY_ID]
                 [--ifmt {smiles,smarts,inchi,inchikey,cid,sid,sdf}]
                 [--ofmt {smiles,smarts,inchi,inchikey,cid,sid,sdf}] [--gz]
                 [--sim_cutoff SIM_CUTOFF] [--active ACTIVE]
                 [--search_nmax SEARCH_NMAX] [--max_wait MAX_WAIT]
                 [--poll_wait POLL_WAIT] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [-v]
                 {search_exact,search_substructure,search_similarity,standardize,idexchange}

PubChem PUG SOAP client: idexchange, standardize, sub|sim|exact search

positional arguments:
  {search_exact,search_substructure,search_similarity,standardize,idexchange}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             Input file for batch IDs
  --o OFILE             Output SMILES|SDF|TSV file
  --operator {same,parent,samepar}
                        Request logic operator
  --ids IDS             Input ID[s] (comma-separated)
  --query_id QUERY_ID   Input ID (use for search operations)
  --ifmt {smiles,smarts,inchi,inchikey,cid,sid,sdf}
                        Input format
  --ofmt {smiles,smarts,inchi,inchikey,cid,sid,sdf}
                        Output format
  --gz                  Output gzipped [default via filename]
  --sim_cutoff SIM_CUTOFF
                        Similarity cutoff, Tanimoto
  --active ACTIVE       Active mols only (in any assay)
  --search_nmax SEARCH_NMAX
                        Max search hits returned
  --max_wait MAX_WAIT   Max wait for query
  --poll_wait POLL_WAIT
                        Polling wait interval
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Search operations accept one query CID, SMILES, SMARTS, or InChI; standardize and
idexchange accept batch input files. Standardize accepts and returns SMILES, SDF, or
InChI. IDExchange accepts CID, SID, SMILES, InChI, InChIKey, Synonym, and Registry ID
(for specified Source)
```

### Standardize

```
python3 -m BioClients.pubchem.soap.Client standardize --ids "CCN(=O)=O" --ifmt "smiles"
```

### IDExchange

```
python3 -m BioClients.pubchem.soap.Client idexchange --ids "CCN(=O)=O" --ifmt "smiles" --operator "same" --ofmt "cid"
python3 -m BioClients.pubchem.soap.Client idexchange --i foo.smiles --ifmt "smiles" --operator "same" --ofmt "cid"
python3 -m BioClients.pubchem.soap.Client idexchange --ids "6587" --ifmt "cid" --operator "same" --ofmt "sid"
python3 -m BioClients.pubchem.soap.Client idexchange --ids "374894925" --ifmt "sid" --operator "parent" --ofmt "cid"
python3 -m BioClients.pubchem.soap.Client idexchange --i foo.cid --ifmt "cid" --operator "same" --ofmt "inchi"
python3 -m BioClients.pubchem.soap.Client idexchange --i foo.cid --ifmt "cid" --operator "same" --ofmt "smiles"
python3 -m BioClients.pubchem.soap.Client idexchange --i foo.sid --ifmt "sid" --operator "same" --ofmt "smiles"
```

### Structural search

```
python3 -m BioClients.pubchem.soap.Client search_substructure --query_id "NCCC1=CC=C(O)C(O)=C1" --ifmt "smiles" --ofmt "smiles"
python3 -m BioClients.pubchem.soap.Client search_exact --query_id "NCCC1=CC=C(O)C(O)=C1" --ifmt "smiles" --ofmt "smiles" 
python3 -m BioClients.pubchem.soap.Client search_similarity --query_id "NCCC1=CC=C(O)C(O)=C1" --ifmt "smiles" --ofmt "smiles" 
python3 -m BioClients.pubchem.soap.Client search_exact --query_id "InChI=1S/C8H10N4O2/c1-10-4-9-6-5(10)7(13)12(3)8(14)11(6)2/h4H,1-3H3" --ifmt "inchi" --ofmt "smiles" 
```
