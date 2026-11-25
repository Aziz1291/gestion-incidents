"""Tests des fonctionnalités principales de gestion des incidents."""


def test_ajout_incident(client):
    response = client.post("/incidents/nouveau", data={
        "titre": "Projecteur HS",
        "description": "Le vidéoprojecteur ne s'allume pas",
        "lieu": "Salle B12",
        "priorite": "Moyenne",
    })
    assert response.status_code == 302  # redirection vers la page de détail
    incidents = client.get("/api/incidents").json
    assert len(incidents) == 1
    assert incidents[0]["titre"] == "Projecteur HS"
    assert incidents[0]["statut"] == "Nouveau"  # statut par défaut


def test_ajout_incident_invalide(client):
    response = client.post("/incidents/nouveau", data={"titre": "", "priorite": "Urgente"})
    assert response.status_code == 400
    assert client.get("/api/incidents").json == []


def test_liste_incidents(client, incident):
    response = client.get("/api/incidents")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0]["lieu"] == "Labo 3"
    assert "PC en panne" in client.get("/").get_data(as_text=True)


def test_details_incident(client, incident):
    response = client.get(f"/incidents/{incident}")
    assert response.status_code == 200
    assert "Le poste 12 ne démarre plus" in response.get_data(as_text=True)


def test_incident_inexistant(client):
    assert client.get("/incidents/999").status_code == 404
