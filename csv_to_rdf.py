import csv
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from rdflib.namespace import XSD

COVER = Namespace("https://w3id.org/controverse#")

# Graph
g = Graph()
g.parse("C:\\Users\\ilari\\Desktop\\PYTHON\\GANGEMI\\CoVer_Ontology.ttl", format="turtle")

g.bind("cover", COVER)

# handling Literals and Object properties 
def as_node(value: str):
    value = value.strip()
    if not value:
        return None

    if value.startswith("http://") or value.startswith("https://"):
        return URIRef(value)

    if value.startswith("cover:"):
        local_name = value.replace("cover:", "").strip()
        return COVER[local_name]
    
    return Literal(value)

# read the csv
with open("C:\\Users\\ilari\\Desktop\\PYTHON\\GANGEMI\\creative_works.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        work_id = row["ID"].strip()
        work_uri = COVER[work_id] 

        
        g.add((work_uri, RDF.type, COVER.CreativeWork))

        mapping = {
            "Creative Work" : COVER.hasTitle,
            "hasLyricalType": COVER.hasLyricalType,
            "hasGenre": COVER.hasGenre,
            "hasPoeticForm": COVER.hasPoeticForm,
            "hasEvent": COVER.hasEvent,
            "Epistemic Scenario description": COVER.hasEpistemicDescription,  
            "Observable Scenario description": COVER.hasObservableDescription,
            "Ironic instance": COVER.hasInstance,
            "Sincerity Instance": COVER.hasInstance,
            "Instance Translation": COVER.hasDescription,
            "ironic type - muecke": COVER.hasIronyType,
            "ironic subtype- muecke": COVER.hasIronySubtype,
            "target type": COVER.hasTarget,
            "(target) description": COVER.hasDescription,
            "interpreter type": COVER.hasInterpreter,
            "Creator - ironist": COVER.hasCreatorName,
            "creation date": COVER.hasCreationDate,
            "creation location": COVER.hasCreationLocation,
            "language": COVER.hasLanguage,
            "performer": COVER.hasPerformerName,
        }

        # triples
        for col, prop in mapping.items(): 
            val = row.get(col, "").strip()
            if not val:
                continue

            # for the date
            if col == "creation date":
                try:
                    g.add((work_uri, prop, Literal(int(val), datatype=XSD.gYear)))
                except ValueError:
                    g.add((work_uri, prop, Literal(val)))
            else:
                g.add((work_uri, prop, as_node(val)))

# save
g.serialize(destination="C:\\Users\\ilari\\Desktop\\PYTHON\\GANGEMI\\creative_works.ttl", format="turtle")
print("RDF file successfully saved as 'creative_works_cover.ttl'")
