"""Package repositories : acces PostgreSQL encapsule (P0).

Les repositories sont les seuls composants metier autorises a encapsuler les
acces persistants (consigne section 4). Chaque acces applique le scope
institution (multi-tenancy, etape 20). Les sous-modules sont importes
directement pour eviter toute chaine d'import circulaire.
"""
