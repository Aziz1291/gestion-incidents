# Questions de synthèse

**1. Différence entre Git et GitHub ?**
Git est un **outil** de gestion de versions installé sur la machine (commits, branches,
fusions, historique). GitHub est une **plateforme en ligne** qui héberge des dépôts Git et
ajoute la collaboration (Pull Requests, revues), l'automatisation (GitHub Actions) et un
registre d'images (GHCR).

**2. Rôle d'un Dockerfile ?**
C'est la **recette** de construction d'une image : image de base, répertoire de travail,
fichiers à copier, dépendances à installer, port, commande de démarrage. Il rend la
construction reproductible sur n'importe quelle machine.

**3. Image Docker vs conteneur ?**
L'image est un **modèle figé**, en lecture seule (comme une classe). Le conteneur est une
**instance en cours d'exécution** de cette image (comme un objet). Une image peut lancer
plusieurs conteneurs.

**4. Intérêt de Docker Compose ?**
Décrire dans **un seul fichier YAML** toute la configuration d'exécution (services, ports,
volumes, variables, politique de redémarrage) et tout démarrer / arrêter avec une seule
commande (`docker compose up -d` / `down`). C'est de l'*infrastructure as code* : versionné,
relisible, rejouable à l'identique.

**5. Quel événement déclenche le workflow CI ?**
Un **push sur `main`** et une **Pull Request vers `main`** (section `on:` de `ci.yml`).

**6. Pourquoi les tests doivent-ils réussir avant la publication ?**
Pour ne jamais publier une image défectueuse : ce qui est dans le registre est ce qui sera
déployé. Avec `needs: test`, le job de publication ne démarre que si les tests sont verts —
une erreur est bloquée **avant** d'atteindre les utilisateurs.

**7. Rôle de GHCR ?**
GitHub Container Registry est un **registre d'images** : il stocke les images publiées,
avec leurs tags, et permet de les récupérer (`docker pull`) depuis n'importe quelle machine.
Il est intégré à GitHub (authentification par `GITHUB_TOKEN`, lien avec le dépôt).

**8. Pourquoi un tag correspondant au SHA du commit ?**
`latest` change à chaque publication ; le SHA est **unique et immuable**. Il permet de
savoir exactement quel code se trouve dans une image (traçabilité), de déployer une version
précise et de **revenir en arrière** (rollback) vers une version antérieure.

**9. Différence entre `docker build` et `docker pull` ?**
`docker build` **fabrique** une image localement à partir d'un Dockerfile et du code source.
`docker pull` **télécharge** une image déjà construite depuis un registre — pas besoin du
code ni du Dockerfile sur la machine.

**10. Étapes supplémentaires pour un déploiement automatique sur un serveur distant ?**
- Disposer d'un serveur (VM cloud) avec Docker installé.
- Stocker l'accès au serveur dans les **secrets GitHub** (clé SSH, hôte, utilisateur).
- Ajouter un job `deploy` dans `cd.yml` avec `needs: publish` qui se connecte en SSH et
  exécute `docker compose -f compose.deploy.yaml pull && docker compose -f compose.deploy.yaml up -d`.
- Authentifier le serveur auprès de GHCR si l'image est privée.
- Vérifier le déploiement (appel de `/health`), prévoir un rollback vers un tag SHA
  précédent, et éventuellement des environnements (staging / production) avec approbation.
