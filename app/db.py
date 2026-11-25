"""Accès à la base de données SQLite."""
import os
import sqlite3

from flask import current_app, g

PRIORITES = ["Faible", "Moyenne", "Élevée"]
STATUTS = ["Nouveau", "En cours", "Résolu"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    titre       TEXT NOT NULL,
    description TEXT NOT NULL,
    lieu        TEXT NOT NULL,
    priorite    TEXT NOT NULL,
    statut      TEXT NOT NULL DEFAULT 'Nouveau',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    """Retourne la connexion SQLite de la requête en cours (créée si besoin)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Crée le dossier et la table si elles n'existent pas encore."""
    path = app.config["DATABASE"]
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)


def init_app(app):
    init_db(app)
    app.teardown_appcontext(close_db)


# --- Opérations CRUD -------------------------------------------------------

def lister_incidents():
    return get_db().execute(
        "SELECT * FROM incidents ORDER BY id DESC"
    ).fetchall()


def obtenir_incident(incident_id):
    return get_db().execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()


def ajouter_incident(titre, description, lieu, priorite):
    db = get_db()
    cur = db.execute(
        "INSERT INTO incidents (titre, description, lieu, priorite) VALUES (?, ?, ?, ?)",
        (titre, description, lieu, priorite),
    )
    db.commit()
    return cur.lastrowid


def modifier_statut(incident_id, statut):
    db = get_db()
    cur = db.execute(
        "UPDATE incidents SET statut = ? WHERE id = ?", (statut, incident_id)
    )
    db.commit()
    return cur.rowcount > 0


def supprimer_incident(incident_id):
    db = get_db()
    cur = db.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
    db.commit()
    return cur.rowcount > 0
