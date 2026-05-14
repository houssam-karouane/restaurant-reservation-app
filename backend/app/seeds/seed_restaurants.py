import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models.restaurant import Restaurant  # noqa: E402


# Images Unsplash curées par cuisine — URLs publiques, pas de clé API requise.
# Le client front-end utilise un fallback (lettre initiale) si une URL casse.
_UNSPLASH = "https://images.unsplash.com/photo-{id}" "?auto=format&fit=crop&w=800&q=80"


def _img(photo_id: str) -> str:
    return _UNSPLASH.format(id=photo_id)


# Demo data — 17 restaurants répartis dans 5 villes françaises.
_SEED_DATA = [
    {
        "name": "Le Petit Bistrot",
        "cuisine": "française",
        "city": "Paris",
        "price_range": 2,
        "rating": 4.5,
        "image_url": _img("1414235077428-338989a2e8c0"),
    },
    {
        "name": "Sakura Tokyo",
        "cuisine": "japonaise",
        "city": "Paris",
        "price_range": 3,
        "rating": 4.8,
        "image_url": _img("1579871494447-9811cf80d66c"),
    },
    {
        "name": "Bella Napoli",
        "cuisine": "italienne",
        "city": "Paris",
        "price_range": 2,
        "rating": 4.2,
        "image_url": _img("1565299624946-b28f40a0ae38"),
    },
    {
        "name": "Le Grand Luxe",
        "cuisine": "française",
        "city": "Paris",
        "price_range": 4,
        "rating": 4.9,
        "image_url": _img("1517248135467-4c7edcad34c4"),
    },
    {
        "name": "Tacos del Sur",
        "cuisine": "mexicaine",
        "city": "Paris",
        "price_range": 1,
        "rating": 3.9,
        "image_url": _img("1565299507177-b0ac66763828"),
    },
    {
        "name": "Dragon Palace",
        "cuisine": "chinoise",
        "city": "Paris",
        "price_range": 2,
        "rating": 3.7,
        "image_url": _img("1525755662778-989d0524087e"),
    },
    {
        "name": "Bouchon Lyonnais",
        "cuisine": "française",
        "city": "Lyon",
        "price_range": 2,
        "rating": 4.6,
        "image_url": _img("1466637574441-749b8f19452f"),
    },
    {
        "name": "Sushi Lyon",
        "cuisine": "japonaise",
        "city": "Lyon",
        "price_range": 2,
        "rating": 4.1,
        "image_url": _img("1559339352-11d035aa65de"),
    },
    {
        "name": "La Trattoria",
        "cuisine": "italienne",
        "city": "Lyon",
        "price_range": 3,
        "rating": 4.4,
        "image_url": _img("1551183053-bf91a1d81141"),
    },
    {
        "name": "La Bouillabaisse",
        "cuisine": "méditerranéenne",
        "city": "Marseille",
        "price_range": 3,
        "rating": 4.7,
        "image_url": _img("1559847844-5315695dadae"),
    },
    {
        "name": "Le Panier Fleuri",
        "cuisine": "française",
        "city": "Marseille",
        "price_range": 2,
        "rating": 4.0,
        "image_url": _img("1592861956120-e524fc739696"),
    },
    {
        "name": "Spice Garden",
        "cuisine": "indienne",
        "city": "Marseille",
        "price_range": 2,
        "rating": 3.8,
        "image_url": _img("1585937421612-70a008356fbe"),
    },
    {
        "name": "Château Table",
        "cuisine": "française",
        "city": "Bordeaux",
        "price_range": 4,
        "rating": 4.8,
        "image_url": _img("1559329007-40df8a9345d8"),
    },
    {
        "name": "L'Atelier Tapas",
        "cuisine": "espagnole",
        "city": "Bordeaux",
        "price_range": 2,
        "rating": 4.3,
        "image_url": _img("1515443961218-a51367888e4b"),
    },
    {
        "name": "Burger & Co",
        "cuisine": "américaine",
        "city": "Bordeaux",
        "price_range": 1,
        "rating": 3.5,
        "image_url": _img("1568901346375-23c9450c58cd"),
    },
    {
        "name": "La Socca d'Or",
        "cuisine": "niçoise",
        "city": "Nice",
        "price_range": 2,
        "rating": 4.6,
        "image_url": _img("1481931098730-318b6f776db0"),
    },
    {
        "name": "Blue Mediterranean",
        "cuisine": "méditerranéenne",
        "city": "Nice",
        "price_range": 3,
        "rating": 4.4,
        "image_url": _img("1540189549336-e6e99c3679fe"),
    },
]


def seed_restaurants(db: Session) -> int:
    """Insère les restaurants de démonstration si la table est vide.

    Retourne le nombre de lignes insérées (0 si déjà peuplée).
    """
    if db.query(Restaurant).count() > 0:
        # Le seed reste la source de vérité pour image_url : on resynchronise
        # les URLs à chaque démarrage (par nom) pour qu'un changement de seed
        # se propage sans nuker le volume Postgres.
        by_name = {data["name"]: data["image_url"] for data in _SEED_DATA}
        updated = 0
        for restaurant in db.query(Restaurant).all():
            target = by_name.get(restaurant.name)
            if target and restaurant.image_url != target:
                restaurant.image_url = target
                updated += 1
        if updated:
            db.commit()
        return 0

    db.add_all([Restaurant(**data) for data in _SEED_DATA])
    db.commit()
    return len(_SEED_DATA)


def seed():
    """Point d'entrée CLI — `python -m app.seeds.seed_restaurants`."""
    db = SessionLocal()
    try:
        inserted = seed_restaurants(db)
        if inserted == 0:
            print("Des restaurants existent déjà. Seed ignoré.")
        else:
            print(f"✅ {inserted} restaurants insérés.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
