from backend.db import Base, engine, SessionLocal
from backend.models import Product

Base.metadata.create_all(bind=engine)

products = [
    Product(
        title="Pack Texturas Premium",
        slug="pack-texturas-premium",
        description="Coleção de texturas para artes e designs.",
        price=19.90,
        image_url="https://picsum.photos/seed/textura1/800/600",
        category="Texturas",
    ),
    Product(
        title="Kit Fundos e Patterns",
        slug="kit-fundos-patterns",
        description="Fundos e padrões para suas criações.",
        price=14.90,
        image_url="https://picsum.photos/seed/patterns/800/600",
        category="Patterns",
    ),
    Product(
        title="Bundle Criativo Completo",
        slug="bundle-criativo-completo",
        description="Bundle com recursos variados (mockups, texturas, etc).",
        price=49.90,
        image_url="https://picsum.photos/seed/bundle/800/600",
        category="Bundles",
    ),
]

db = SessionLocal()
try:
    existing = db.query(Product).count()
    if existing == 0:
        db.add_all(products)
        db.commit()
        print("Seed concluído.")
    else:
        print("Banco já tem produtos, seed ignorado.")
finally:
    db.close()
