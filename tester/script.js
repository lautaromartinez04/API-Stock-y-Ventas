// 1) Pedimos el token al usuario
const TOKEN = prompt("Pega aquí tu JWT:");
const AUTH_HEADER = { "Authorization": `Bearer ${TOKEN}` };

// 2) Configuración de URLs
const host    = location.hostname;
const port    = 8000;
const API_URL = `http://${host}:${port}`;
const WS_SALES  = `ws://${host}:${port}/ws/ventas?token=${encodeURIComponent(TOKEN)}`;
const WS_STOCK  = `ws://${host}:${port}/ws/stock?token=${encodeURIComponent(TOKEN)}`;

// 3) Referencias al DOM
const stockList = document.getElementById("stock-list");
const salesList = document.getElementById("sales-list");

// 4) Funciones de renderizado

// Renderizar lista inicial de productos
function renderInitialStock(products) {
  stockList.innerHTML = "";
  products.forEach(p => {
    const li = document.createElement("li");
    li.id = `stock-${p.id}`;
    li.innerHTML = `
      Producto #${p.id} — ${p.nombre}: 
      <strong class="cantidad">${p.stock_actual}</strong>
    `;
    stockList.appendChild(li);
  });
}

// Actualizar un único producto
function updateStock({ producto_id, new_stock }) {
  const li = document.getElementById(`stock-${producto_id}`);
  if (li) {
    li.querySelector(".cantidad").textContent = new_stock;
  }
}

// Renderizar una venta nueva
function renderSale(v) {
  const li = document.createElement("li");
  li.innerHTML = `
    <strong>Venta #${v.venta_id || v.id}</strong> — Total: $${v.total.toFixed(2)}
    ${Array.isArray(v.detalles)
      ? v.detalles.map(d =>
          `<div class="detalle">
             • Producto #${d.producto_id} — Cantidad: ${d.cantidad} — Subtotal: $${d.subtotal.toFixed(2)}
           </div>`
        ).join("")
      : ""
    }
  `;
  salesList.prepend(li);
  if (salesList.children.length > 20) {
    salesList.removeChild(salesList.lastChild);
  }
}

// 5) Carga inicial de productos
fetch(`${API_URL}/productos`, {
  headers: AUTH_HEADER
})
  .then(res => {
    if (!res.ok) throw new Error("Error cargando productos: " + res.status);
    return res.json();
  })
  .then(data => renderInitialStock(data))
  .catch(console.error);

// 6) Carga inicial de ventas
fetch(`${API_URL}/ventas`, {
  headers: AUTH_HEADER
})
  .then(res => {
    if (!res.ok) throw new Error("Error cargando ventas: " + res.status);
    return res.json();
  })
  .then(data => {
    data.forEach(v => renderSale({ id: v.id, total: v.total, detalles: [] }));
  })
  .catch(console.error);

// 7) Conexión WS para actualizaciones de stock
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

// 8) Conexión WS para nuevas ventas
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
