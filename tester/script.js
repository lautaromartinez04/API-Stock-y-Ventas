// Ajusta estos valores si tu API corre en otro host/puerto
const HTTP_HOST = location.hostname;
const HTTP_PORT = 8000;
const API_URL   = `http://${HTTP_HOST}:${HTTP_PORT}`;
const WS_URL    = `ws://${HTTP_HOST}:${HTTP_PORT}/ws/ventas`;

// Referencia al <ul>
const salesList = document.getElementById("sales-list");

// 1) Función que dibuja una venta en la lista
function renderSale(v) {
  const li = document.createElement("li");
  li.innerHTML = `
    <strong>Venta #${v.id}</strong> — Total: $${v.total.toFixed(2)}
    <div class="detalle">Cliente: ${v.cliente_id ?? '—'}</div>
    ${Array.isArray(v.detalles)
      ? v.detalles.map(d =>
          `<div class="detalle">• Producto #${d.producto_id} — Cantidad: ${d.cantidad} — Subtotal: $${d.subtotal.toFixed(2)}</div>`
        ).join("")
      : ""
    }
  `;
  salesList.prepend(li);
  // Mantener solo las últimas 20
  if (salesList.children.length > 20) {
    salesList.removeChild(salesList.lastChild);
  }
}

// 2) Carga inicial de ventas
fetch(`${API_URL}/ventas`)
  .then(res => {
    if (!res.ok) throw new Error("Error cargando ventas");
    return res.json();
  })
  .then(data => {
    // data es array de { id, total, cliente_id, fecha }
    // Si querés detalles, podrías fetchear /detalle_ventas?venta_id=...
    data.forEach(v => {
      // para el front básico sin detalles, pasamos un array vacío
      renderSale({ id: v.id, total: v.total, cliente_id: v.cliente_id, detalles: [] });
    });
  })
  .catch(err => console.error(err));

// 3) WebSocket para ventas nuevas
const ws = new WebSocket(WS_URL);
ws.onopen = () => console.log("🔌 Conectado a ws/ventas");
ws.onmessage = event => {
  try {
    const msg = JSON.parse(event.data);
    if (msg.event === "new_sale") {
      // msg viene con venta_id, total, cliente_id y detalles[]
      renderSale({
        id: msg.venta_id,
        total: msg.total,
        cliente_id: msg.cliente_id,
        detalles: msg.detalles
      });
    }
  } catch (e) {
    console.error("WS venta parse error:", e);
  }
};
ws.onclose = () => console.log("❌ Desconectado de ws/ventas");
