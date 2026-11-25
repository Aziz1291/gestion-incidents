"""Tests de la modification du statut et de la suppression d'un incident."""


def test_modifier_statut(client, incident):
    response = client.post(f"/incidents/{incident}/statut", data={"statut": "En cours"})
    assert response.status_code == 302
    assert client.get(f"/api/incidents/{incident}").json["statut"] == "En cours"


def test_modifier_statut_invalide(client, incident):
    response = client.post(f"/incidents/{incident}/statut", data={"statut": "Annulé"})
    assert response.status_code == 400
    assert client.get(f"/api/incidents/{incident}").json["statut"] == "Nouveau"


def test_supprimer_incident(client, incident):
    response = client.post(f"/incidents/{incident}/supprimer")
    assert response.status_code == 302
    assert client.get(f"/api/incidents/{incident}").status_code == 404
    assert client.get("/api/incidents").json == []
