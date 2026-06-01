const CART_KEY = "loja_cart_v2";

function readCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY) || "[]"); }
  catch { return []; }
}

function writeCart(items) {
  localStorage.setItem(CART_KEY, JSON.stringify(items));
}

function addToCart(product) {
  const cart = readCart();
  const existing = cart.find(i => i.id === product.id);
  if (existing) existing.qty += 1;
  else cart.push({ id: product.id, title: product.title, price: product.price, image_url: product.image_url, qty: 1 });
  writeCart(cart);
}

function setQty(id, qty) {
  let cart = readCart();
  cart = cart.map(i => i.id === id ? { ...i, qty: Math.max(1, qty) } : i);
  writeCart(cart);
}

function removeItem(id) {
  const cart = readCart().filter(i => i.id !== id);
  writeCart(cart);
}

function cartCount() {
  return readCart().reduce((a, i) => a + i.qty, 0);
}

function cartTotal() {
  return readCart().reduce((a, i) => a + (i.price * i.qty), 0);
}

function formatBRL(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function buildWhatsAppMessage(cart, total) {
  const lines = [];
  lines.push("Olá! Quero comprar:");
  lines.push("");
  cart.forEach(i => lines.push(`• ${i.title} (x${i.qty}) — ${formatBRL(i.price * i.qty)}`));
  lines.push("");
  lines.push(`Total: ${formatBRL(total)}`);
  lines.push("");
  lines.push("Pode me enviar as instruções de pagamento/entrega?");
  return encodeURIComponent(lines.join("\n"));
}
