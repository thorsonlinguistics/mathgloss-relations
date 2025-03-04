"""
Constructs a graph in neo4j containing the definitions in mathgloss and their
relations. 
"""

import requests
import os

from csv import DictReader
from dotenv import load_dotenv
from neo4j import GraphDatabase
from urllib.parse import urlparse

load_dotenv()

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    'User-Agent': 'parmesan/0.3',
}
QUERY = """
select distinct ?itemLabel ?subject ?subjectLabel ?propertyLabel {
  {wd:%s owl:sameAs ?item} UNION { VALUES (?item) {(wd:%s)}}
  ?item ?predicate ?subject .
  ?property wikibase:directClaim ?predicate .
  service wikibase:label { bd:serviceParam wikibase:language "en" }
}
"""

class GraphBuilder:

    def __init__(self, uri, user, password):

        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):

        self.driver.close()

    def build(self, filename):

        with self.driver.session() as session:
            with open(filename, newline='') as infile:
                reader = DictReader(infile)
                for row in reader:
                    session.execute_write(self._create_term, row)

    @staticmethod
    def get_wikidata_relations(identifier):
        while True:
            result = requests.post(
                ENDPOINT,
                data={'query': QUERY % (identifier, identifier), 'format': 'json'},
                headers=HEADERS,
            )
            if result.status_code == 429:
                print("Retrying...")
                time.sleep(result.headers['retry-after'])
                continue
            break

        json = result.json()
        relations = []
        properties = []
        for binding in json['results']['bindings']:
            subject = binding['subject']
            subjectLabel = binding['subjectLabel']
            label = binding['propertyLabel']
            new_label = binding['itemLabel']['value']
            if subject['type'] == 'uri':
                parsed = urlparse(subject['value'])
                relations.append({
                    'target': parsed.path.rpartition('/')[2],
                    'label': label['value'],
                    'name': subjectLabel['value'],
                })
            else:
                properties.append({
                    'key': label['value'],
                    'value': subject['value'],
                })

        return (relations, properties, new_label)

    @staticmethod
    def _create_term(tx, row):

        (relations, new_props, new_label) = GraphBuilder.get_wikidata_relations(row["Wikidata ID"])

        term = tx.run("CREATE (term:Term) "
               "SET term.wikidata = $wikidata, "
               "term.chicago = $chicago, "
               "term.lean = $lean, "
               "term.mulima = $mulima, "
               "term.nlab = $nlab, "
               "term.wikidata_label = $wikidata_label "
               "RETURN term",
            wikidata=row["Wikidata ID"],
            wikidata_label=new_label,
            chicago=row["Chicago"],
            lean=row["Lean 4 Undergrad"],
            mulima=row["MuLiMa"],
            nlab=row["nLab"],
        ).single()
        term_id = term['term'].element_id

        for relation in relations:
            tx.run("""
                MATCH (term:Term {wikidata: $wikidata})
                MERGE (target {wikidata_label: $name})
                ON CREATE
                    SET target:External, target.wikidata = $target
                MERGE (term)-[:REL {label: $label}]->(target)
                """,
                wikidata=row['Wikidata ID'],
                target=relation['target'],
                label=relation['label'],
                name=relation['name'],
                wikidata_label=new_label,
            )
        for prop in new_props:
            tx.run("""
                MATCH (term:Term {wikidata: $wikidata})
                SET term.`%s` = $value""" % prop['key'],
                wikidata=row['Wikidata ID'],
                value=prop['value'],
            )

if __name__ == "__main__":

    builder = GraphBuilder(os.environ['DATABASE_HOST'],
            os.environ['DATABASE_NAME'], os.environ['DATABASE_PASSWORD'])
    builder.build("database_clean.csv")
