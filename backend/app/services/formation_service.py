"""Logique métier du module Formations (prompt 4.2, section 5.3.3 du CDC)."""
from datetime import date, datetime, timezone

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competence import Competence
from app.models.emargement import Emargement
from app.models.enums import StatutSeance
from app.models.habilitation import Habilitation
from app.models.question_quiz import QuestionQuiz
from app.models.seance import Seance
from app.models.tentative_quiz import TentativeQuiz
from app.schemas.formation import (
    CompetenceCreation,
    EmargementEntree,
    HabilitationCreation,
    SeanceCreation,
    TentativeQuizEntree,
)

# Règle 5.3.3 du CDC : "Le seuil de réussite du quiz est paramétrable, fixé par
# défaut à sept sur dix" — exprimé en proportion pour s'appliquer quel que soit
# le nombre réel de questions actives (FOR-SHEQ-015 en compte 10 aujourd'hui,
# mais le référentiel est géré par le référent SHEQ et peut évoluer).
SEUIL_REUSSITE_QUIZ_DEFAUT = 0.7

# Horizon par défaut pour signaler une habilitation "bientôt expirée" dans
# l'écran d'alerte — le CDC ne donne pas de valeur, choisi par cohérence avec
# les horizons déjà retenus ailleurs (EPI : 30 jours).
HORIZON_ALERTE_JOURS = 30


def creer_competence(db: Session, donnees: CompetenceCreation, cree_par_id: int) -> Competence:
    competence = Competence(
        libelle=donnees.libelle, periodicite_mois=donnees.periodicite_mois, cree_par_id=cree_par_id
    )
    db.add(competence)
    db.commit()
    db.refresh(competence)
    return competence


def lister_competences(db: Session) -> list[Competence]:
    return list(db.scalars(select(Competence).where(Competence.archive.is_(False)).order_by(Competence.libelle)))


def creer_habilitation(db: Session, donnees: HabilitationCreation, cree_par_id: int) -> Habilitation:
    competence = db.get(Competence, donnees.competence_id)
    if competence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compétence introuvable")
    habilitation = Habilitation(
        utilisateur_id=donnees.utilisateur_id,
        competence_id=donnees.competence_id,
        date_obtention=donnees.date_obtention,
        date_expiration=donnees.date_obtention + relativedelta(months=competence.periodicite_mois),
        cree_par_id=cree_par_id,
    )
    db.add(habilitation)
    db.commit()
    db.refresh(habilitation)
    return habilitation


def _dernieres_habilitations(db: Session, utilisateur_id: int | None = None) -> list[Habilitation]:
    """Une ligne par (utilisateur, compétence) : la plus récente par date
    d'obtention — un recyclage ajoute une nouvelle ligne, il ne réécrit jamais
    l'ancienne (même principe que les cotations de risque, prompt 4.1)."""
    from sqlalchemy import func

    sous_requete = select(
        Habilitation.utilisateur_id, Habilitation.competence_id, func.max(Habilitation.id).label("dernier_id")
    ).group_by(Habilitation.utilisateur_id, Habilitation.competence_id)
    if utilisateur_id is not None:
        sous_requete = sous_requete.where(Habilitation.utilisateur_id == utilisateur_id)
    sous_requete = sous_requete.subquery()
    return list(
        db.scalars(select(Habilitation).join(sous_requete, Habilitation.id == sous_requete.c.dernier_id))
    )


def matrice_competences(db: Session, utilisateur_id: int | None = None) -> list[Habilitation]:
    """Section 5.3.3 : "matrice de compétences". Ne montre que les couples
    (utilisateur, compétence) où une habilitation existe au moins une fois —
    pas une case vide pour chaque combinaison théorique (contrairement à la
    matrice de criticité des risques, dont les 25 cases ont un sens même
    vides : ici une case vide ne signifierait qu'une absence de données)."""
    return _dernieres_habilitations(db, utilisateur_id)


def alertes_recyclage(db: Session, horizon_jours: int = HORIZON_ALERTE_JOURS) -> list[Habilitation]:
    aujourdhui = date.today()
    habilitations = _dernieres_habilitations(db)
    dues = [h for h in habilitations if (h.date_expiration - aujourdhui).days <= horizon_jours]
    return sorted(dues, key=lambda h: h.date_expiration)


def creer_seance(db: Session, donnees: SeanceCreation, cree_par_id: int) -> Seance:
    seance = Seance(
        theme=donnees.theme,
        date=donnees.date,
        lieu=donnees.lieu,
        animateur_id=donnees.animateur_id,
        competence_id=donnees.competence_id,
        statut=StatutSeance.PLANIFIEE,
        cree_par_id=cree_par_id,
    )
    db.add(seance)
    db.commit()
    db.refresh(seance)
    return seance


def lister_seances(db: Session) -> list[Seance]:
    return list(db.scalars(select(Seance).where(Seance.archive.is_(False)).order_by(Seance.date.desc())))


def obtenir_seance(db: Session, seance_id: int) -> Seance:
    seance = db.get(Seance, seance_id)
    if seance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Séance introuvable")
    return seance


def emarger(db: Session, seance: Seance, donnees: EmargementEntree, cree_par_id: int) -> Emargement:
    """Section 5.3.3 : "Émarger une présence depuis un mobile ou une tablette".
    Idempotent par (séance, participant) : un second émargement corrige le
    premier plutôt que de dupliquer la ligne — une présence n'est pas un
    historique à conserver point par point, contrairement à une cotation."""
    existant = db.scalar(
        select(Emargement).where(
            Emargement.seance_id == seance.id, Emargement.participant_id == donnees.participant_id
        )
    )
    maintenant = datetime.now(timezone.utc)
    if existant is not None:
        existant.present = donnees.present
        existant.signe_le = maintenant
        existant.modifie_par_id = cree_par_id
        db.commit()
        db.refresh(existant)
        return existant

    emargement = Emargement(
        seance_id=seance.id,
        participant_id=donnees.participant_id,
        present=donnees.present,
        signe_le=maintenant,
        cree_par_id=cree_par_id,
    )
    db.add(emargement)
    db.commit()
    db.refresh(emargement)
    return emargement


def cloturer_seance(db: Session, seance: Seance, modifie_par_id: int) -> Seance:
    """Une séance clôturée dont la compétence est renseignée renouvelle
    l'habilitation de chaque participant présent (données gérées, 5.3.3 : les
    séances et la matrice de compétences sont explicitement liées)."""
    if seance.statut != StatutSeance.PLANIFIEE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Seule une séance planifiée peut être clôturée"
        )
    seance.statut = StatutSeance.REALISEE
    seance.modifie_par_id = modifie_par_id

    if seance.competence_id is not None:
        competence = db.get(Competence, seance.competence_id)
        presents = db.scalars(
            select(Emargement).where(Emargement.seance_id == seance.id, Emargement.present.is_(True))
        )
        for emargement in presents:
            db.add(
                Habilitation(
                    utilisateur_id=emargement.participant_id,
                    competence_id=seance.competence_id,
                    date_obtention=seance.date,
                    date_expiration=seance.date + relativedelta(months=competence.periodicite_mois),
                    cree_par_id=modifie_par_id,
                )
            )

    db.commit()
    db.refresh(seance)
    return seance


def creer_question(db: Session, enonce: str, choix: list[dict], reponse_correcte: str, cree_par_id: int) -> QuestionQuiz:
    lettres = {c["lettre"] for c in choix}
    if reponse_correcte not in lettres:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La réponse correcte doit correspondre à l'une des lettres proposées",
        )
    question = QuestionQuiz(enonce=enonce, choix=choix, reponse_correcte=reponse_correcte, cree_par_id=cree_par_id)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def lister_questions(db: Session) -> list[QuestionQuiz]:
    return list(db.scalars(select(QuestionQuiz).where(QuestionQuiz.archive.is_(False)).order_by(QuestionQuiz.id)))


def passer_quiz(db: Session, seance: Seance, donnees: TentativeQuizEntree, participant_id: int) -> tuple[TentativeQuiz, list[dict]]:
    questions_actives = lister_questions(db)
    ids_attendus = {q.id for q in questions_actives}
    ids_recus = {r.question_id for r in donnees.reponses}
    if ids_recus != ids_attendus:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le quiz doit être répondu intégralement : une réponse par question active, ni plus ni moins",
        )

    reponses_par_question = {r.question_id: r.reponse for r in donnees.reponses}
    questions_par_id = {q.id: q for q in questions_actives}
    score = 0
    details = []
    for question_id, reponse_donnee in reponses_par_question.items():
        correcte = reponse_donnee == questions_par_id[question_id].reponse_correcte
        if correcte:
            score += 1
        details.append({"question_id": question_id, "correcte": correcte})

    total = len(questions_actives)
    reussi = (score / total) >= SEUIL_REUSSITE_QUIZ_DEFAUT if total else False

    tentative = TentativeQuiz(
        seance_id=seance.id,
        participant_id=participant_id,
        reponses=[r.model_dump() for r in donnees.reponses],
        score=score,
        total_questions=total,
        reussi=reussi,
        date_passation=datetime.now(timezone.utc),
        cree_par_id=participant_id,
    )
    db.add(tentative)
    db.commit()
    db.refresh(tentative)
    return tentative, details
