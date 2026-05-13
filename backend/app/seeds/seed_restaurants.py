import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal  # noqa: E402
from app.models.restaurant import Restaurant  # noqa: E402


def seed():
    db = SessionLocal()

    if db.query(Restaurant).count() > 0:
        print("Des restaurants existent déjà. Seed ignoré.")
        db.close()
        return

    restaurants = [
        Restaurant(name="Le Petit Bistrot", cuisine="française", city="Paris", price_range=2, rating=4.5),
        Restaurant(name="Sakura Tokyo", cuisine="japonaise", city="Paris", price_range=3, rating=4.8),
        Restaurant(name="Bella Napoli", cuisine="italienne", city="Paris", price_range=2, rating=4.2),
        Restaurant(name="Le Grand Luxe", cuisine="française", city="Paris", price_range=4, rating=4.9),
        Restaurant(name="Tacos del Sur", cuisine="mexicaine", city="Paris", price_range=1, rating=3.9),
        Restaurant(name="Dragon Palace", cuisine="chinoise", city="Paris", price_range=2, rating=3.7),
        Restaurant(name="Bouchon Lyonnais", cuisine="française", city="Lyon", price_range=2, rating=4.6),
        Restaurant(name="Sushi Lyon", cuisine="japonaise", city="Lyon", price_range=2, rating=4.1),
        Restaurant(name="La Trattoria", cuisine="italienne", city="Lyon", price_range=3, rating=4.4),
        Restaurant(
            name="La Bouillabaisse", cuisine="méditerranéenne", city="Marseille", price_range=3, rating=4.7
        ),
        Restaurant(name="Le Panier Fleuri", cuisine="française", city="Marseille", price_range=2, rating=4.0),
        Restaurant(name="Spice Garden", cuisine="indienne", city="Marseille", price_range=2, rating=3.8),
        Restaurant(name="Château Table", cuisine="française", city="Bordeaux", price_range=4, rating=4.8),
        Restaurant(
            name="L'Atelier Tapas", cuisine="espagnole", city="Bordeaux", price_range=2, rating=4.3
        ),
        Restaurant(name="Burger & Co", cuisine="américaine", city="Bordeaux", price_range=1, rating=3.5),
        Restaurant(name="La Socca d'Or", cuisine="niçoise", city="Nice", price_range=2, rating=4.6),
        Restaurant(
            name="Blue Mediterranean", cuisine="méditerranéenne", city="Nice", price_range=3, rating=4.4
        ),
    ]

    db.add_all(restaurants)
    db.commit()
    print(f"✅ {len(restaurants)} restaurants insérés.")
    db.close()


if __name__ == "__main__":
    seed()