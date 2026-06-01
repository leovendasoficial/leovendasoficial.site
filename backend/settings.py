import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "store_name": "SUA LOJA",
    "store_subtitle": "Recursos digitais • Texturas • Packs",
    "accent_color": "#ff2d2d",
    "whatsapp_phone": "55SEUNUMEROAQUI",  # ex: 5571999999999
    "pix_key": "SUA_CHAVE_PIX_AQUI",
    "pix_holder": "SEU NOME",
    "pix_city": "SUA CIDADE",
    "pix_description": "Pagamento Loja",
    "mercadopago_public_key": "",
    "mercadopago_access_token": ""
}

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(data: dict) -> None:
    SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
