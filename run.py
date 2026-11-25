"""Point d'entrée : lance le serveur Flask."""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" est indispensable dans un conteneur (sinon inaccessible depuis l'hôte)
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
