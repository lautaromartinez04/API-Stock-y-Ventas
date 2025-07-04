// 1) Pedimos el token al usuario
const TOKEN = prompt("Pega aquí tu JWT:");
const AUTH_HEADER = { "Authorization": `Bearer ${TOKEN}` };

// 2) Configuración de URLs
const host     = location.hostname;
const port     = 8000;
const API_URL  = `http://${host}:${port}`;
const WS_SALES = `ws://${host}:${port}/ws/ventas?token=${encodeURIComponent(TOKEN)}`;
const WS_STOCK = `ws://${host}:${port}/ws/stock?token=${encodeURIComponent(TOKEN)}`;

// 3) Referencias al DOM
const stockContainer = document.getElementById("stock-container");
const salesList      = document.getElementById("sales-list");

// 4) Funciones de renderizado

// Crea una tarjeta para un producto
function createCard(p) {
  const card = document.createElement("div");
  card.className = "card";
  card.id = `stock-${p.id}`;
  const imgSrc = p.image_url
    ? `${API_URL}${p.image_url}`
    : "https://via.placeholder.com/180x120?text=Sin+Imagen";
  card.innerHTML = `
    <img src="${imgSrc}" alt="${p.nombre}">
    <div class="info">
      <h3>${p.nombre}</h3>
      <p>Código: ${p.codigo}</p>
      <p>Stock: <span class="stock-qty">${p.stock_actual}</span></p>
    </div>
  `;
  return card;
}

// Renderiza todas las tarjetas iniciales
function renderInitialStock(products) {
  stockContainer.innerHTML = "";
  products.forEach(p => {
    stockContainer.appendChild(createCard(p));
  });
}

// Actualiza solo el stock de un producto existente
function updateStock({ producto_id, new_stock }) {
  const card = document.getElementById(`stock-${producto_id}`);
  if (!card) return;
  const qty = card.querySelector(".stock-qty");
  qty.textContent = new_stock;
}

// Crea y añade una venta a la lista
function renderSale(v) {
  const li = document.createElement("li");
  let html = `<strong>Venta #${v.venta_id || v.id}</strong> — Total: $${v.total.toFixed(2)}`;
  if (Array.isArray(v.detalles)) {
    v.detalles.forEach(d => {
      html += `<div class="detalle">
        • Producto #${d.producto_id} — Cantidad: ${d.cantidad} — Subtotal: $${d.subtotal.toFixed(2)}
      </div>`;
    });
  }
  li.innerHTML = html;
  salesList.prepend(li);
  if (salesList.children.length > 20) {
    salesList.removeChild(salesList.lastChild);
  }
}

// 5) Carga inicial de productos
fetch(`${API_URL}/productos`, { headers: AUTH_HEADER })
  .then(res => {
    if (!res.ok) throw new Error("Error cargando productos: " + res.status);
    return res.json();
  })
  .then(renderInitialStock)
  .catch(console.error);

// 6) Carga inicial de ventas
fetch(`${API_URL}/ventas`, { headers: AUTH_HEADER })
  .then(res => {
    if (!res.ok) throw new Error("Error cargando ventas: " + res.status);
    return res.json();
  })
  .then(data => data.forEach(v => renderSale({ id: v.id, total: v.total, detalles: [] })))
  .catch(console.error);

// 7) WebSocket para actualizaciones de stock
const wsStock = new WebSocket(WS_STOCK);
wsStock.addEventListener("open", () => console.log("🔌 Conectado a ws/stock"));
wsStock.addEventListener("message", evt => {
  const msg = JSON.parse(evt.data);
  if (msg.event === "stock_update") {
    updateStock(msg);
  }
});
wsStock.addEventListener("error", e => console.error("WS Stock error:", e));
wsStock.addEventListener("close", () => console.log("❌ Desconectado de ws/stock"));

// 8) WebSocket para nuevas ventas
const wsSales = new WebSocket(WS_SALES);
wsSales.addEventListener("open", () => console.log("🔌 Conectado a ws/ventas"));
wsSales.addEventListener("message", evt => {
  const msg = JSON.parse(evt.data);
  if (msg.event === "new_sale") {
    renderSale(msg);
  }
});
wsSales.addEventListener("error", e => console.error("WS Ventas error:", e));
wsSales.addEventListener("close", () => console.log("❌ Desconectado de ws/ventas"));
