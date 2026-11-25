"""Fixtures partagées : chaque test utilise sa propre base SQLite temporaire."""
import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def incident(client):
    """Crée un incident de test et retourne son identifiant."""
    client.post("/incidents/nouveau", data={
        "titre": "PC en panne",
        "description": "Le poste 12 ne démarre plus",
        "lieu": "Labo 3",
        "priorite": "Élevée",
    })
    return client.get("/api/incidents").json[0]["id"]
