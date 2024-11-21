import streamlit as st
import json

# Carregar o JSON
with open("json-test-ontologies/OntoStone.json", "r") as file:
    data = json.load(file)

# Função para listar entidades com categorias
def get_entidades():
    entidades = [item for item in data["model"]["contents"] if item["type"] == "Class"]
    categorias = {}
    for entidade in entidades:
        stereotype = entidade.get("stereotype", "Sem Categoria")
        if stereotype not in categorias:
            categorias[stereotype] = []
        categorias[stereotype].append(entidade)
    return categorias

# Função para obter detalhes de uma entidade
def get_entidade_details(entidade_id):
    entidade = next((item for item in data["model"]["contents"] if item["id"] == entidade_id), None)
    if not entidade:
        return None

    filhos = [
        next((item for item in data["model"]["contents"] if item["id"] == gen["specific"]["id"]), None)
        for gen in data["model"]["contents"] if gen["type"] == "Generalization" and gen["general"]["id"] == entidade_id
    ]

    pais = [
        next((item for item in data["model"]["contents"] if item["id"] == gen["general"]["id"]), None)
        for gen in data["model"]["contents"] if gen["type"] == "Generalization" and gen["specific"]["id"] == entidade_id
    ]

    relations = []
    for rel in data["model"]["contents"]:
        if rel["type"] == "Relation":
            for prop in rel.get("properties", []):
                connected_entity = next((item for item in data["model"]["contents"] if item["id"] == prop["propertyType"]["id"]), None)
                if connected_entity and (prop["propertyType"]["id"] == entidade_id or entidade_id in [p["propertyType"]["id"] for p in rel["properties"]]):
                    relations.append({
                        "relation_name": rel["name"],
                        "relation_stereotype": rel.get("stereotype", "No stereotype"),
                        "connected_entity": connected_entity,
                        "connected_entity_stereotype": connected_entity.get("stereotype", "No stereotype")
                    })

    return {
        "entidade": entidade,
        "filhos": [classe for classe in filhos if classe],
        "pais": [classe for classe in pais if classe],
        "relations": relations
    }

# Ler query params
pagina = st.query_params.get("pagina", "Entidades")
entidade_id = st.query_params.get("entidade_id", None)

# Função para atualizar query params
def update_query_params(**params):
    st.query_params.clear()  # Remove os parâmetros existentes
    for key, value in params.items():
        st.query_params[key] = value

# Página de entidades
if pagina == "Entidades":
    st.title("Entidades OntoStone")
    categorias = get_entidades()
    for categoria, entidades in categorias.items():
        with st.expander(f"<<{categoria}>> ({len(entidades)})"):
            for entidade in entidades:
                if st.button(entidade["name"], key=entidade["id"]):
                    update_query_params(pagina="Detalhes", entidade_id=entidade["id"])
                    st.rerun()
# Página de detalhes da entidade
elif pagina == "Detalhes" and entidade_id:
    details = get_entidade_details(entidade_id)
    if details:
        st.title(f"Detalhes da Entidade: {details['entidade']['name']}")
        st.write(f"**Descrição:** {details['entidade'].get('description', 'Nenhuma descrição disponível')}")
        st.write(f"**Estereótipo:** {details['entidade'].get('stereotype', 'Sem estereótipo')}")

        st.write("### Filhos")
        if details["filhos"]:
            for filho in details["filhos"]:
                st.markdown(f"- {filho['name']} (<<{filho.get('stereotype', 'Sem estereótipo')}>>)")
        else:
            st.write("Nenhum filho encontrado.")

        st.write("### Pais")
        if details["pais"]:
            for pai in details["pais"]:
                st.markdown(f"- {pai['name']} (<<{pai.get('stereotype', 'Sem estereótipo')}>>)")
        else:
            st.write("Nenhum pai encontrado.")

        st.write("### Relacionamentos")
        if details["relations"]:
            for relation in details["relations"]:
                st.markdown(
                    f"- <<{relation['relation_stereotype']}>> {relation['relation_name']} "
                    f"com [{relation['connected_entity']['name']}] (<<{relation['connected_entity_stereotype']}>>)"
                )
        else:
            st.write("Nenhum relacionamento encontrado.")

        if st.button("Voltar para Entidades"):
            update_query_params(pagina="Entidades")
            st.rerun()
    else:
        st.write("Entidade não encontrada. Verifique o ID.")
