# `BioClients.util`

Miscellaneous utilities for web service clients.

##  `pandas`

Processing CSV/TSV files.

##  `rest`

Convenience functions for REST APIs.

##  `sparql`

For Sparql endpoints.

### Dependencies

* Python packages: `SPARQLWrapper`

##  `xml`

Processing XML with `xml.etree.ElementTree`.

##  `hdf`

[HDF5](https://www.hdfgroup.org/) (hierarchical data format)
file processing, using [h5py, HDF5 for Python](https://docs.h5py.org/).

##  `igraph`

Graph analytics with igraph, and with GraphML and CyJS formats.

```
$ python3 -m BioClients.util.igraph.App -h
usage: App.py [-h] --i IFILE [--o OFILE] [--selectfield SELECTFIELD]
              [--selectquery SELECTQUERY] [--selectval SELECTVAL]
              [--select_exact SELECT_EXACT] [--select_equal] [--select_lt] [--select_gt]
              [--select_negate] [--display] [--depth DEPTH] [--nidA NIDA] [--nidB NIDB]
              [--quiet] [-v]
              {summary,degree_distribution,rootnodes,topnodes,graph2cyjs,shortest_path,show_ancestry,connectednodes,disconnectednodes,node_select,edge_select}

IGraph (python-igraph API) utility, graph processingand display

positional arguments:
  {summary,degree_distribution,rootnodes,topnodes,graph2cyjs,shortest_path,show_ancestry,connectednodes,disconnectednodes,node_select,edge_select}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input file or URL (e.g. GraphML)
  --o OFILE             output file
  --selectfield SELECTFIELD
                        field (attribute) to select
  --selectquery SELECTQUERY
                        string query
  --selectval SELECTVAL
                        numerical query
  --select_exact SELECT_EXACT
                        exact string match (else substring/regex)
  --select_equal        numerical equality select
  --select_lt           numerical less-than select
  --select_gt           numerical greater-than select
  --select_negate       negate select criteria
  --display             display graph interactively
  --depth DEPTH         depth for --topnodes
  --nidA NIDA           nodeA ID
  --nidB NIDB           nodeB ID
  --quiet
  -v, --verbose

OPERATIONS: summary: summary of graph; degree_distribution: degree distribution;
node_select: select for nodes by criteria; edge_select: select for edges by criteria;
connectednodes: connected node[s]; disconnectednodes: disconnected node[s]; rootnodes:
root node[s] of DAG; topnodes: root node[s] & children of DAG; shortest_paths: shortest
paths, nodes A ~ B; show_ancestry: show ancestry, node A; graph2cyjs: CytoscapeJS JSON;
NOTE: select also deletes non-matching for modified output.
```

```
 python3 -m BioClients.util.igraph.InfoContent -h
usage: InfoContent.py [-h] --i IFILE [--o OFILE] [--nidA NIDA] [--nidB NIDB]
                      [--nmax NMAX] [--skip SKIP] [-v]
                      {computeIC,findMICA,simMatrix,simMatrixNodelist,test}

Info content (IC) and most informative common ancestor (MICA) for directed acyclic graph
(DAG)

positional arguments:
  {computeIC,findMICA,simMatrix,simMatrixNodelist,test}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input graph (GraphML)
  --o OFILE             output graph (GraphML)
  --nidA NIDA           nodeA ID
  --nidB NIDB           nodeB ID
  --nmax NMAX
  --skip SKIP
  -v, --verbose

simMatrixNodelist outputs vertex indices with node IDs. simMatrix with --nidA to compute
one row.
```
