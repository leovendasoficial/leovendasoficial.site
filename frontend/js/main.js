const grid = document.getElementById("grid");
const empty = document.getElementById("empty");
const searchInput = document.getElementById("searchInput");
const categorySelect = document.getElementById("categorySelect");
const reloadBtn = document.getElementById("reloadBtn");

const cartBtn = document.getElementById("cartBtn");
const cartDrawer = document.getElementById("cartDrawer");
const closeCart = document.getElementById("closeCart");
const cartItems = document.getElementById("cartItems");
const cartTotalEl = document.getElementById("cartTotal");
const cartCountEl = document.getElementById("cartCount");
const checkoutWhats = document.getElementById("checkoutWhats");
const checkoutPix = document.getElementById("checkoutPix");

const pixModal = document.getElementById("pixModal");
const closePix = document.getElementById("closePix");
const copyPix = document.getElementById("copyPix");
const openWhatsFromPix = document.getElementById("openWhatsFromPix");

const brandTitle = document.getElementById("brandTitle");
const brandSub = document.getElementById("brandSub");
const pixKeyInput = document.getElementById("pixKey");

let productsCache = [];
let settingsCache = null;

function setAccent(color) {
  if (!color) return;
  document.documentElement.style.setProperty("--accent", color);
}

function setCartBadge() {
  cartCountEl.textContent = String(cartCount());
}

function openCart() {
  renderCart();
  cartDrawer.classList.remove("hidden");
}
function closeCartDrawer() {
  cartDrawer.classList.add("hidden");
}

function openPix() { pixModal.classList.remove("hidden"); }
function closePixModal() { pixModal.classList.add("hidden"); }

function productCard(p) {
  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `
    <img src="${p.image_url || "https://picsum.photos/seed/placeholder/800/600"}" alt="">
    <div class="card-body">
      <div>
        <div class="card-cat">${p.category || "Geral"}</div>
        <div class="card-title">${p.title}</div>
      </div>
      <div class="card-row">
        <div class="price">${formatBRL(p.price)}</div>
        <div class="card-actions">
          <button class="btn btn-ghost" data-action="details">Detalhes</button>
          <button class="btn btn-primary" data-action="add">Adicionar</button>
        </div>
      </div>
    </div>
  `;

  div.querySelector('[data-action="add"]').addEventListener("click", () => {
    addToCart(p);
    setCartBadge();
  });

  div.querySelector('[data-action="details"]').addEventListener("click", () => {
    alert(`${p.title}\n\n${p.description || ""}\n\nPreço: ${formatBRL(p.price)}`);
  });

  return div;
}

function renderProducts(list) {
  grid.innerHTML = "";
  if (!list.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");
  list.forEach(p => grid.appendChild(productCard(p)));
}

function filterProducts() {
  const q = (searchInput.value || "").trim().toLowerCase();
  const cat = categorySelect.value || "";

  const filtered = productsCache.filter(p => {
    const okQ = !q || p.title.toLowerCase().includes(q);
    const okC = !cat || p.category === cat;
    return okQ && okC;
  });

  renderProducts(filtered);
}

async function loadCategories() {
  const data = await apiGet("/categories");
  const cats = data.categories || [];
  categorySelect.innerHTML = `<option value="">Todas as categorias</option>` +
    cats.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function loadProducts() {
  productsCache = await apiGet("/products");
  renderProducts(productsCache);
}

async function loadSettings() {
  settingsCache = await apiGet("/public/settings");
  brandTitle.textContent = settingsCache.store_name || "SUA LOJA";
  brandSub.textContent = settingsCache.store_subtitle || "";
  setAccent(settingsCache.accent_color);
  pixKeyInput.value = settingsCache.pix_key || "SUA_CHAVE_PIX_AQUI";
}

function renderCart() {
  const cart = readCart();
  cartItems.innerHTML = "";

  if (!cart.length) {
    cartItems.innerHTML = `<div class="empty">Seu carrinho está vazio.</div>`;
    cartTotalEl.textContent = formatBRL(0);
    setCartBadge();
    return;
  }

  cart.forEach(item => {
    const row = document.createElement("div");
    row.className = "cart-item";
    row.innerHTML = `
      <img src="${item.image_url || "https://picsum.photos/seed/cart/200/200"}" alt="">
      <div class="meta">
        <strong>${item.title}</strong>
        <span>${formatBRL(item.price)} • ${formatBRL(item.price * item.qty)}</span>
      </div>
      <div class="qty">
        <button data-act="dec">-</button>
        <strong>${item.qty}</strong>
        <button data-act="inc">+</button>
        <button data-act="rm">🗑️</button>
      </div>
    `;

    row.querySelector('[data-act="dec"]').addEventListener("click", () => {
      setQty(item.id, item.qty - 1);
      renderCart();
    });
    row.querySelector('[data-act="inc"]').addEventListener("click", () => {
      setQty(item.id, item.qty + 1);
      renderCart();
    });
    row.querySelector('[data-act="rm"]').addEventListener("click", () => {
      removeItem(item.id);
      renderCart();
    });

    cartItems.appendChild(row);
  });

  cartTotalEl.textContent = formatBRL(cartTotal());
  setCartBadge();
}

function setupEvents() {
  searchInput.addEventListener("input", filterProducts);
  categorySelect.addEventListener("change", filterProducts);
  reloadBtn.addEventListener("click", async () => {
    await loadProducts();
    filterProducts();
  });

  cartBtn.addEventListener("click", openCart);
  closeCart.addEventListener("click", closeCartDrawer);
  cartDrawer.querySelector(".drawer-backdrop").addEventListener("click", closeCartDrawer);

  checkoutWhats.addEventListener("click", () => {
    const cart = readCart();
    if (!cart.length) return alert("Carrinho vazio.");
    const phone = (settingsCache && settingsCache.whatsapp_phone) ? settingsCache.whatsapp_phone : "55SEUNUMEROAQUI";
    const total = cartTotal();
    const msg = buildWhatsAppMessage(cart, total);
    window.open(`https://wa.me/${phone}?text=${msg}`, "_blank");
  });

  checkoutPix.addEventListener("click", openPix);
  closePix.addEventListener("click", closePixModal);
  pixModal.querySelector(".modal-backdrop").addEventListener("click", closePixModal);

  copyPix.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(pixKeyInput.value.trim());
      alert("Chave Pix copiada!");
    } catch {
      alert("Não consegui copiar automaticamente. Copie manualmente.");
    }
  });

  openWhatsFromPix.addEventListener("click", () => {
    const phone = (settingsCache && settingsCache.whatsapp_phone) ? settingsCache.whatsapp_phone : "55SEUNUMEROAQUI";
    window.open(`https://wa.me/${phone}`, "_blank");
  });
}

async function init() {
  setCartBadge();
  setupEvents();
  await loadSettings();
  await loadCategories();
  await loadProducts();
}
init().catch(err => {
  console.error(err);
  alert("Erro ao carregar API. Verifique se o backend está rodando em 127.0.0.1:8000");
});
