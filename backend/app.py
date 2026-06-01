from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from db import SessionLocal, Base, engine
from models import Product
from auth import login as admin_login, require_admin
from utils import slugify
from settings import load_settings, save_settings, DEFAULT_SETTINGS

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loja API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, troque pelo seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    price: float
    image_url: str
    category: str
    is_active: bool
    class Config:
        from_attributes = True

class ProductIn(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    slug: str | None = None
    description: str = ""
    price: float = Field(gt=0)
    image_url: str = ""
    category: str = "Geral"
    is_active: bool = True

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    token: str

@app.get("/health")
def health():
    return {"ok": True}

# Public settings used by frontend
@app.get("/public/settings")
def public_settings():
    s = load_settings()
    # remove secrets
    s.pop("mercadopago_access_token", None)
    return s

@app.get("/products", response_model=list[ProductOut])
def list_products(q: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.is_active == True)
    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(Product.category == category)
    return query.order_by(Product.id.desc()).all()

@app.get("/products/{slug}", response_model=ProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.slug == slug, Product.is_active == True).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return p

@app.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).filter(Product.is_active == True).distinct().all()
    return {"categories": sorted([r[0] for r in rows if r[0]])}

# ---------------- ADMIN ----------------

@app.post("/admin/login", response_model=TokenOut)
def admin_login_route(data: LoginIn):
    token = admin_login(data.username, data.password)
    return {"token": token}

@app.get("/admin/settings")
def admin_get_settings(_admin: str = Depends(require_admin)):
    return load_settings()

@app.put("/admin/settings")
def admin_put_settings(payload: dict, _admin: str = Depends(require_admin)):
    current = load_settings()
    merged = {**current, **payload}
    # fill missing defaults
    for k, v in DEFAULT_SETTINGS.items():
        merged.setdefault(k, v)
    save_settings(merged)
    return {"ok": True, "settings": merged}

@app.get("/admin/products", response_model=list[ProductOut])
def admin_list_products(db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    return db.query(Product).order_by(Product.id.desc()).all()

@app.post("/admin/products", response_model=ProductOut)
def admin_create_product(data: ProductIn, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    slug = (data.slug or "").strip() or slugify(data.title)
    p = Product(
        title=data.title.strip(),
        slug=slug,
        description=data.description or "",
        price=float(data.price),
        image_url=data.image_url or "",
        category=data.category or "Geral",
        is_active=bool(data.is_active),
    )
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # add random suffix
        p.slug = f"{slug}-{p.title[:3].lower()}-{p.price}".replace(".", "").replace(" ", "")
        db.add(p)
        db.commit()
    db.refresh(p)
    return p

@app.put("/admin/products/{product_id}", response_model=ProductOut)
def admin_update_product(product_id: int, data: ProductIn, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    p.title = data.title.strip()
    p.slug = (data.slug or "").strip() or slugify(p.title)
    p.description = data.description or ""
    p.price = float(data.price)
    p.image_url = data.image_url or ""
    p.category = data.category or "Geral"
    p.is_active = bool(data.is_active)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slug já existe. Troque o slug.")
    db.refresh(p)
    return p

@app.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(p)
    db.commit()
    return {"ok": True}

# ---------------- CHECKOUT HELPERS ----------------
class CartItem(BaseModel):
    id: int
    qty: int = Field(gt=0)

class CheckoutIn(BaseModel):
    items: list[CartItem]
    customer_name: str | None = None
    customer_email: str | None = None

@app.post("/checkout/summary")
def checkout_summary(payload: CheckoutIn, db: Session = Depends(get_db)):
    # Summarize items with prices from DB (trust server-side)
    ids = [i.id for i in payload.items]
    products = db.query(Product).filter(Product.id.in_(ids)).all()
    pmap = {p.id: p for p in products}
    lines = []
    total = 0.0
    for it in payload.items:
        p = pmap.get(it.id)
        if not p:
            continue
        subtotal = float(p.price) * int(it.qty)
        total += subtotal
        lines.append({"id": p.id, "title": p.title, "qty": it.qty, "unit_price": p.price, "subtotal": subtotal})
    return {"items": lines, "total": total}
