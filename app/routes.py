"""Routes (pages web + API JSON) de l'application."""
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)

from . import db

bp = Blueprint("incidents", __name__)


def _valider(form):
    """Vérifie les champs du formulaire et retourne la liste des erreurs."""
    erreurs = []
    for champ in ("titre", "description", "lieu"):
        if not form.get(champ, "").strip():
            erreurs.append(f"Le champ « {champ} » est obligatoire.")
    if form.get("priorite") not in db.PRIORITES:
        erreurs.append("La priorité doit être Faible, Moyenne ou Élevée.")
    return erreurs


# --- Pages web -------------------------------------------------------------

@bp.route("/")
def accueil():
    incidents = db.lister_incidents()
    stats = {s: sum(1 for i in incidents if i["statut"] == s) for s in db.STATUTS}
    return render_template("index.html", incidents=incidents, stats=stats)


@bp.route("/incidents/nouveau", methods=["GET", "POST"])
def nouveau():
    if request.method == "POST":
        erreurs = _valider(request.form)
        if erreurs:
            for e in erreurs:
                flash(e, "erreur")
            return render_template("nouveau.html", priorites=db.PRIORITES,
                                   form=request.form), 400
        incident_id = db.ajouter_incident(
            request.form["titre"].strip(),
            request.form["description"].strip(),
            request.form["lieu"].strip(),
            request.form["priorite"],
        )
        flash("Incident ajouté avec succès.", "succes")
        return redirect(url_for("incidents.detail", incident_id=incident_id))
    return render_template("nouveau.html", priorites=db.PRIORITES, form={})


@bp.route("/incidents/<int:incident_id>")
def detail(incident_id):
    incident = db.obtenir_incident(incident_id) or abort(404)
    return render_template("detail.html", incident=incident, statuts=db.STATUTS)


@bp.route("/incidents/<int:incident_id>/statut", methods=["POST"])
def changer_statut(incident_id):
    statut = request.form.get("statut")
    if statut not in db.STATUTS:
        abort(400)
    if not db.modifier_statut(incident_id, statut):
        abort(404)
    flash(f"Statut mis à jour : {statut}.", "succes")
    return redirect(url_for("incidents.detail", incident_id=incident_id))


@bp.route("/incidents/<int:incident_id>/supprimer", methods=["POST"])
def supprimer(incident_id):
    if not db.supprimer_incident(incident_id):
        abort(404)
    flash("Incident supprimé.", "succes")
    return redirect(url_for("incidents.accueil"))


# --- API JSON (utile pour les tests et la vérification du déploiement) ------

@bp.route("/health")
def health():
    return jsonify(status="OK")


@bp.route("/api/incidents")
def api_liste():
    return jsonify([dict(i) for i in db.lister_incidents()])


@bp.route("/api/incidents/<int:incident_id>")
def api_detail(incident_id):
    incident = db.obtenir_incident(incident_id) or abort(404)
    return jsonify(dict(incident))
