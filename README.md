# mathgloss-relations

Extraction of relations and other statistics from MathGloss.

This package builds a Neo4j graph from the mathgloss database. To build a
cleaned version of the database, run `scripts/clean_csv.py`. To build the graph,
run `scripts/build_graph.py`.

To build the graph database, it is necessary to have a few environment variables
set:

    DATABASE_HOST="bolt://localhost:7687" // The running database instance
    DATABASE_NAME="neo4j" // The database username
    DATABASE_PASSWORD="12345" // The user's password

## Statistics

Some statistics about the dataset:

- There are *683* MathGloss terms
- These are related to *2079* external (WikiData) entities
- There are:
    - 587 terms with Freebase IDs
    - 443 terms with Chicago labels
    - 232 terms with Lean labels
    - 157 terms with mulima labels
    - 409 terms with nLab labels
    - 683 terms with Wikidata IDs

The following files provide some additional statistics about the database:

- `stats/disconnected.json`: MathGloss nodes which have no incoming or outgoing relations (9)
- `stats/isolated.json': MathGloss nodes which are not related to other
  MathGloss concepts (333)
- `stats/labels.csv`: All relation labels, with their frequencies
