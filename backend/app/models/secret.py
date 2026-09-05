"""Entité SECRET — CDC chapitre 7.2.8. Le chiffrement Fernet lui-même (clé maîtresse,
service de chiffrement/déchiffrement) est traité au prompt 3.3, pas ici : ce modèle
ne fait que porter la colonne binaire destinée à recevoir le jeton chiffré."""
from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import RoleUtilisateur, TypeAcces


class Secret(BaseModel):
    __tablename__ = "secret"

    libelle: Mapped[str] = mapped_column(String(120), nullable=False)
    equipement_id: Mapped[int | None] = mapped_column(ForeignKey("equipement.id"), nullable=True)
    type_acces: Mapped[TypeAcces] = mapped_column(enum_column(TypeAcces, "type_acces"), nullable=False)
    identifiant: Mapped[str | None] = mapped_column(String(80), nullable=True)
    valeur_chiffree: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    # Dictionnaire : "Énuméré" sans détail. Interprété comme le même rôle minimal
    # que RoleUtilisateur (référent SHEQ exclu par construction, règle 5.2.4).
    role_requis: Mapped[RoleUtilisateur] = mapped_column(
        enum_column(RoleUtilisateur, "role_requis_secret"), nullable=False
    )
