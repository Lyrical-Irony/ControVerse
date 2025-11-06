import csv
from rdflib import Graph, Namespace, Literal, RDF, URIRef, RDFS, OWL
from rdflib.namespace import XSD

COVER = Namespace("https://w3id.org/controverse#")
COVERCORE = Namespace("https://w3id.org/controverse/")

# Graph
g = Graph()
g.parse("CoVer_Ont_v2.ttl", format="turtle")

g.bind("cover", COVER)
g.bind("covercore", COVERCORE)

# handling Literals and Object properties 
def as_node(value: str):
    value = value.strip()
    if value == "N/A":
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
        inst_uri = COVERCORE[row["ID"].strip()]
        event_uri = COVERCORE["event"+row["ID"]] 
        work_uri = COVERCORE[row["Creative Work"].strip()]
        creator_uri = COVERCORE[row["Creator"].strip()]

        ironicTypes = {
            "cover:DramatizedIrony":COVER.DramatizedIrony,
            "cover:ImpersonalIrony": COVER.ImpersonalIrony,
            "cover:IngenuIrony":COVER.IngenuIrony,
            "cover:IronyOfDilemma":COVER.IronyOfDilemma,
            "cover:IronyOfDrama":COVER.IronyOfDrama,
            "cover:IronyOfEvents":COVER.IronyOfEvents,
            "cover:IronyOfSelfBetrayal":COVER.IronyOfSelfBetrayal,
            "cover:IronyOfSimpleIncongruency":COVER.IronyOfSimpleIncongruency,
            "cover:SelfDisparagingIrony":COVER.SelfDisparagingIrony
        }

        targetTypes = {
            "cover:Community":COVER.Community,
            "cover:Concept":COVER.Concept,
            "cover:Institution":COVER.Institution,
            "cover:Person":COVER.Person,
            "cover:Self":COVER.Self,
            "cover:StateOfAffair":COVER.StateOfAffair,
            "cover:Thing":COVER.Thing,
        }

        #checking for ironic or sincere instances
        if row["Instance Type"] == "Irony":
            g.add((inst_uri, RDF.type, COVER.Irony))
            g.add((inst_uri, COVER.hasIronyType, ironicTypes[row["Ironic Type"]]))
            g.add((event_uri, RDF.type, COVER.IronicEvent))
            g.add((creator_uri, RDF.type, COVER.Ironist))
            g.add((event_uri, COVER.hasIronist, creator_uri))
        else:
            g.add((inst_uri, RDF.type, COVER.Sincerity))
            g.add((event_uri, RDF.type, COVER.SincereEvent))
            g.add((event_uri, COVER.hasActor, creator_uri))

        #triples for instance   
        g.add((inst_uri, COVER.hasText, Literal(row["Text"]))) #should we add language tags?
        g.add((inst_uri, COVER.hasTranslation, Literal(row["hasTranslation"])))
        g.add((inst_uri, COVER.createdFrom, event_uri))
        g.add((inst_uri, COVER.foundIn, work_uri))
        g.add((inst_uri, COVER.hasTarget, targetTypes[row["Target Type"]]))
        g.add((inst_uri, COVER.hasTargetDescription, Literal(row["Target Description"])))
        g.add((inst_uri, RDFS.label, Literal(f'Creative Instance {row["ID"]}')))

        #triples for event
        g.add((event_uri, COVER.createdDuring, as_node(row["Event"])))
        g.add((event_uri, COVER.hasInterpreter, as_node(row["Interpreter Type"])))

        g.add((event_uri, COVER.hasEpistemicScenario, Literal(row["Epistemic Scenario"])))
        g.add((event_uri, COVER.hasObservableScenario, Literal(row["Observable Scenario"])))
        g.add((event_uri, RDFS.label, Literal(f'Event {row["ID"]}')))
             
        #triple for work
        g.add((work_uri, RDF.type, as_node(row["Lyrical Type"])))
        g.add((work_uri, COVER.hasCreator, creator_uri))
        g.add((work_uri, COVER.hasCreationLocation, Literal(row["Creation Location"])))
        g.add((work_uri, COVER.hasLanguage, Literal(row["Language"])))
        if row["hasPoeticForm"] != "N/A":
            g.add((work_uri, COVER.hasPoeticForm, Literal(row["hasPoeticForm"])))
        if row["hasGenre"] != "N/A":
            g.add((work_uri, COVER.hasGenre, Literal(row["hasGenre"])))
        g.add((work_uri, COVER.hasTitle, Literal(row["hasTitle"])))
        g.add((work_uri, RDFS.label, Literal(row["hasTitle"])))

        try:
            g.add((work_uri, COVER.hasCreationDate, Literal(int(row["Creation Date"]), datatype=XSD.gYear)))
        except ValueError:
            g.add((work_uri, COVER.hasCreationDate, Literal(row["Creation Date"])))

        #triple for creator
        g.add((creator_uri, RDF.type, COVER.Author))
        g.add((creator_uri, COVER.hasName, Literal(row["Creator Name"])))
        g.add((creator_uri, RDFS.label, Literal(row["Creator Name"])))
        g.add((creator_uri, OWL.sameAs, URIRef(row["CreatorURI"])))

        #triples for performer
        if row["Performer"] != "N/A":
            if row["Performer"] == row["Creator"]:
                g.add((creator_uri, RDF.type, COVER.Performer))
                g.add((work_uri, COVER.hasPerformer, creator_uri))
            else:
                performer_uri = COVERCORE[row["Performer"].strip()]
                g.add((performer_uri, RDF.type, COVER.Performer))
                g.add((performer_uri, COVER.hasName, Literal(row["Performer Name"])))
                g.add((performer_uri, RDFS.label, Literal(row["Performer Name"])))
                g.add((performer_uri, OWL.sameAs, URIRef(row["PerformerURI"])))

# save
g.serialize(destination="IronicCreativity_Data.ttl", format="turtle")
print("RDF file successfully saved as 'IronicCreativity_Data.ttl'")
