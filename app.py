from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


with open("json-test-ontologies/OntoStone.json", "r") as file:
    data = json.load(file)
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/entidades")
def entidades():
    # Filtrar entidades com "type": "Class"
    entidades = [item for item in data["model"]["contents"] if item["type"] == "Class"]

    # Categorizar entidades por "stereotype"
    categorias = {}
    for entidade in entidades:
        stereotype = entidade.get("stereotype", "Sem Categoria")
        if stereotype not in categorias:
            categorias[stereotype] = []
        categorias[stereotype].append(entidade)

    return render_template("entidades.html", categorias=categorias)


@app.route("/entidade/<id>")
def entidade(id):
    # Encontrar a entidade pelo ID
    entidade = next((item for item in data["model"]["contents"] if item["id"] == id), None)
    if not entidade:
        return "<h1>Entidade não encontrada</h1>", 404

    # Classes Filhas (specifics)
    filhos = [
        next((item for item in data["model"]["contents"] if item["id"] == gen["specific"]["id"]), None)
        for gen in data["model"]["contents"] if gen["type"] == "Generalization" and gen["general"]["id"] == id
    ]

    # Classes Pais (generals)
    pais = [
        next((item for item in data["model"]["contents"] if item["id"] == gen["general"]["id"]), None)
        for gen in data["model"]["contents"] if gen["type"] == "Generalization" and gen["specific"]["id"] == id
    ]

    # Relacionamentos (Relations)
    relations = []
    for rel in data["model"]["contents"]:
        if rel["type"] == "Relation":
            for prop in rel.get("properties", []):
                connected_entity = next((item for item in data["model"]["contents"] if item["id"] == prop["propertyType"]["id"]), None)
                if connected_entity and (prop["propertyType"]["id"] == id or id in [p["propertyType"]["id"] for p in rel["properties"]]):
                    relations.append({
                        "relation_name": rel["name"],
                        "relation_stereotype": rel.get("stereotype", "No stereotype"),
                        "connected_entity": connected_entity,
                        "connected_entity_stereotype": connected_entity.get("stereotype", "No stereotype")
                    })

    # Filtrar classes válidas (para evitar None)
    filhos = [classe for classe in filhos if classe]
    pais = [classe for classe in pais if classe]

    return render_template("entidade.html", entidade=entidade, filhos=filhos, pais=pais, relations=relations)



if __name__ == "__main__":
    app.run(debug=True)