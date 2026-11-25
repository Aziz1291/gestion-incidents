# Gestion des incidents informatiques — Mini-projet DevOps (DSI3)

Application web **Flask + SQLite** pour signaler et suivre les incidents informatiques
(étudiants et enseignants). Elle est livrée par une chaîne DevOps complète :
**Git → GitHub Actions (CI) → GHCR (CD) → déploiement avec Docker Compose**.

> Binôme : _Nom Prénom 1_ — _Nom Prénom 2_

---

## 1. Fonctionnalités

Chaque incident contient : **identifiant**, **titre**, **description**, **lieu** (salle / labo),
**priorité** (Faible, Moyenne, Élevée) et **statut** (Nouveau, En cours, Résolu).

| # | Fonctionnalité | Route |
|---|----------------|-------|
| 1 | Ajouter un incident | `GET/POST /incidents/nouveau` |
| 2 | Afficher la liste des incidents | `GET /` (page) — `GET /api/incidents` (JSON) |
| 3 | Consulter les détails | `GET /incidents/<id>` — `GET /api/incidents/<id>` |
| 4 | Modifier le statut | `POST /incidents/<id>/statut` |
| 5 | Supprimer un incident | `POST /incidents/<id>/supprimer` |
| – | Vérification de santé | `GET /health` → `{"status": "OK"}` |

La version déployée (SHA du commit) s'affiche en bas de chaque page.

## 2. Structure du dépôt

```
gestion-incidents/
├── app/
│   ├── __init__.py          # création de l'application Flask (factory)
│   ├── db.py                # accès SQLite + opérations CRUD
│   ├── routes.py            # pages web et API JSON
│   ├── templates/           # pages HTML (Jinja2)
│   └── static/style.css
├── tests/
│   ├── conftest.py          # base SQLite temporaire pour chaque test
│   ├── test_home.py
│   ├── test_incidents.py
│   └── test_statut_suppression.py
├── run.py                   # point d'entrée (python run.py)
├── Dockerfile
├── .dockerignore
├── compose.yaml             # développement : CONSTRUIT l'image
├── compose.deploy.yaml      # déploiement : RÉCUPÈRE l'image depuis GHCR
├── requirements.txt
├── pytest.ini
├── .gitignore
└── .github/workflows/
    ├── ci.yml               # intégration continue
    └── cd.yml               # publication dans GHCR
```

---

## 3. Construction, publication, déploiement : la différence

C'est le point central du projet :

```
   CONSTRUCTION (build)          PUBLICATION (push)             DÉPLOIEMENT (pull + run)
 ┌──────────────────────┐     ┌─────────────────────────┐     ┌──────────────────────────┐
 │ Dockerfile + code    │     │ image locale            │     │ registre GHCR            │
 │        │             │     │        │                │     │        │ docker pull     │
 │  docker build        │ ──▶ │  docker push            │ ──▶ │        ▼                 │
 │        ▼             │     │        ▼                │     │ conteneur en marche      │
 │ image (sur 1 machine)│     │ image dans GHCR         │     │ (docker compose up -d)   │
 └──────────────────────┘     │ (accessible partout)    │     └──────────────────────────┘
                              └─────────────────────────┘
```

| Étape | Commande | Ce qui se passe | Où |
|-------|----------|-----------------|----|
| **Construction** | `docker build` / `docker compose build` | Docker lit le **Dockerfile** et fabrique une **image** (modèle figé) couche par couche. L'image n'existe que sur la machine qui l'a construite. | Machine du développeur, ou runner GitHub Actions |
| **Publication** | `docker push ghcr.io/...` | L'image est **envoyée dans un registre** (GHCR) avec un ou plusieurs **tags**. Elle devient téléchargeable depuis n'importe quelle machine autorisée. | GitHub Actions (cd.yml) → GHCR |
| **Déploiement** | `docker compose -f compose.deploy.yaml pull` puis `up -d` | Le serveur **télécharge** l'image publiée (sans rien reconstruire) et **lance un conteneur** à partir d'elle. | Serveur / machine cible |

👉 `compose.yaml` contient `build: .` (on construit). `compose.deploy.yaml` contient seulement
`image: ghcr.io/...` (on récupère une image déjà construite **et testée**).

---

## 4. Lancer le projet en local (sans Docker)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS : source .venv/bin/activate)
pip install -r requirements.txt
python run.py                   # http://localhost:5000
```

### Tests automatisés

```bash
python -m pytest -v
```

10 tests : page d'accueil, `/health`, ajout (valide et invalide), liste, détails,
incident inexistant (404), modification du statut (valide et invalide), suppression.
Chaque test utilise sa **propre base SQLite temporaire** (fixture `tmp_path`) : les tests
ne touchent jamais aux vraies données.

---

## 5. Mission 3 — Docker

### Le Dockerfile

| Instruction | Rôle |
|-------------|------|
| `FROM python:3.12-slim` | Image de base |
| `WORKDIR /app` | Répertoire de travail dans le conteneur |
| `COPY requirements.txt .` puis `RUN pip install ...` | Dépendances installées **avant** de copier le code → la couche `pip install` reste en **cache** si seul le code change |
| `COPY . .` | Copie du code (filtré par `.dockerignore`) |
| `EXPOSE 5000` | Documente le port de l'application |
| `CMD ["python", "run.py"]` | Commande lancée au démarrage du conteneur |
| `ARG/ENV APP_VERSION` | Le pipeline CD y injecte le SHA du commit (affiché dans le pied de page) |

### Commandes

```bash
docker build -t gestion-incidents:1.0 .                                   # 1. construire
docker run -d -p 5000:5000 --name incidents gestion-incidents:1.0         # 2. lancer
docker ps                                                                  # 3. vérifier
docker logs incidents
# 4. ouvrir http://localhost:5000
docker stop incidents && docker rm incidents
```

## 6. Mission 4 — Docker Compose

`compose.yaml` définit le service `web`, la construction (`build: .`), le port `5000:5000`,
la politique `restart: unless-stopped` et le volume nommé `incidents_data` monté sur
`/app/data` (où se trouve le fichier SQLite) pour que les données survivent à la suppression
du conteneur.

```bash
docker compose up -d --build     # 1. démarrer
docker compose ps                # 2. vérifier les services
docker compose logs -f web       # 3. consulter les journaux
docker compose down              # 4. arrêter (le volume est conservé)
docker compose down -v           #    arrêter ET supprimer les données
```

## 7. Mission 5 — Intégration continue (`ci.yml`)

Déclenchée à chaque **push sur `main`** et à chaque **Pull Request vers `main`**.

1. `actions/checkout` — récupérer le code
2. `actions/setup-python` + `pip install` — installer Python 3.12 et les dépendances
3. `python -m pytest -v` — exécuter les tests
4. `docker compose config -q` — valider `compose.yaml` et `compose.deploy.yaml`
5. `docker compose build` — construire l'image

Si une étape échoue, les suivantes ne sont pas exécutées et le pipeline est marqué ❌.

### Expérimentation : provoquer une erreur

```bash
# Dans app/routes.py, route /health : remplacer status="OK" par status="ERROR"
git commit -am "Test : provoquer l'echec du pipeline"
git push
# → Onglet Actions : l'étape "Executer les tests" échoue sur test_health
# Remettre status="OK"
git commit -am "Correction de la route /health"
git push
# → le pipeline repasse au vert
```

## 8. Mission 6 — Publication dans GHCR (`cd.yml`)

Déclenché à chaque push sur `main` (ou manuellement via *Run workflow*).

- **Job `test`** : checkout, Python, dépendances, tests.
- **Job `publish`** (`needs: test` → ne s'exécute **que si les tests ont réussi**) :
  1. construit l'image avec deux tags : `latest` et `${{ github.sha }}` ;
  2. se connecte à `ghcr.io` avec le `GITHUB_TOKEN` (aucun mot de passe stocké) ;
  3. publie (`docker push`) les deux tags.
- Permissions : `packages: write` pour écrire dans GHCR, `contents: read` pour lire le code.

Image publiée : **`ghcr.io/aziz1291/gestion-incidents`** (GHCR impose des minuscules).

Vérification :

```bash
docker pull ghcr.io/aziz1291/gestion-incidents:latest
docker images ghcr.io/aziz1291/gestion-incidents
```

> Par défaut, un package GHCR est **privé**. Pour pouvoir le récupérer sans
> authentification : GitHub → *Packages* → `gestion-incidents` → *Package settings* →
> *Change visibility* → **Public**. Sinon : `docker login ghcr.io` avec un jeton personnel
> (scope `read:packages`). Ne jamais partager ce jeton.

## 9. Mission 7 — Déploiement (`compose.deploy.yaml`)

Ce fichier **n'a pas de `build:`** : il utilise directement l'image publiée.
L'application déployée est exposée sur le port **8000** (pour ne pas entrer en conflit
avec la version de développement sur 5000).

```bash
docker compose -f compose.deploy.yaml pull       # 1. récupérer l'image
docker compose -f compose.deploy.yaml up -d      # 2. démarrer
docker compose -f compose.deploy.yaml ps         # 3. vérifier
docker compose -f compose.deploy.yaml logs       # 4. journaux
# http://localhost:8000
```

### Mettre à jour l'application

```bash
# 1. modifier une fonctionnalité, 2. commit + push
git commit -am "Amelioration : ..."
git push
# 3-4. attendre que ci.yml et cd.yml soient verts, vérifier le nouveau tag dans Packages
docker compose -f compose.deploy.yaml pull       # 5. nouvelle image
docker compose -f compose.deploy.yaml up -d      # 6. recrée le conteneur avec la nouvelle image
# 7. le pied de page affiche le nouveau SHA de commit ; les incidents sont conservés (volume)
```

---

## 10. Chaîne DevOps complète

```
Développement → Git/GitHub → push / PR → GitHub Actions
   → Tests (CI) → Validation Compose → Construction Docker
   → Publication GHCR (CD) → docker compose pull → docker compose up -d
   → Application opérationnelle
```

## 11. Captures d'écran

Voir le dossier [`docs/captures/`](docs/captures/) :

1. Pipeline CI réussi
2. Pipeline en échec (test `test_health`) puis corrigé
3. Package `gestion-incidents` dans GHCR avec les tags `latest` et SHA
4. Application déployée via `compose.deploy.yaml` (http://localhost:8000)

## 12. Questions de synthèse

Voir [`docs/questions-synthese.md`](docs/questions-synthese.md).
