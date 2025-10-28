const BASE_URL = document.body.dataset.apiBase || "";

const converterForm = document.getElementById("converter-form");
const convertButton = document.getElementById("convert-button");
const conversionResult = document.getElementById("conversion-result");
const conversionError = document.getElementById("conversion-error");

const baseCurrencySelect = document.getElementById("base-currency");
const loadRatesButton = document.getElementById("load-rates");
const ratesResult = document.getElementById("rates-result");
const ratesMeta = document.getElementById("rates-meta");
const ratesError = document.getElementById("rates-error");

const loadHistoryButton = document.getElementById("load-history");
const historyResult = document.getElementById("history-result");
const historyError = document.getElementById("history-error");
const historyMeta = document.getElementById("history-meta");

const globalStatus = document.getElementById("global-status");

const numberFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

const rateFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 4,
  maximumFractionDigits: 4,
});

function formatTimestamp(value) {
  if (!value) {
    return "";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString("es-CO", {
    hour12: false,
    timeZoneName: "short",
  });
}

function setStatus(message, type = "info") {
  if (!globalStatus) {
    return;
  }

  globalStatus.textContent = message || "";
  globalStatus.dataset.state = type;
}

function showError(target, error) {
  if (!target) {
    return;
  }
  target.textContent = error instanceof Error ? error.message : String(error);
}

function clearElement(el) {
  if (el) {
    el.textContent = "";
  }
}

async function request(path, options = {}) {
  if (!BASE_URL) {
    throw new Error("No se definió la URL del backend.");
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  let data;
  try {
    data = await response.json();
  } catch (error) {
    throw new Error(`No fue posible interpretar la respuesta (${response.status}).`);
  }

  if (!response.ok || (data && data.success === false)) {
    const message = data && data.message ? data.message : `Error ${response.status}`;
    const detail = data && data.error ? `: ${data.error}` : "";
    throw new Error(`${message}${detail}`);
  }

  return data;
}

function renderConversion(data) {
  if (!conversionResult) {
    return;
  }

  const amount = data.amount ?? 0;
  const result = data.result ?? 0;
  const rate = data.rate;
  const updated = formatTimestamp(data.last_updated);

  conversionResult.innerHTML = `
    <div>${numberFormatter.format(amount)} ${data.from} = <strong>${numberFormatter.format(result)} ${data.to}</strong></div>
    ${rate ? `<div>Tasa: ${rateFormatter.format(rate)}</div>` : ""}
    ${updated ? `<div class="meta">Actualizado: ${updated}</div>` : ""}
  `;
}

function renderRates(data) {
  if (!ratesResult) {
    return;
  }

  const rates = data.rates || {};
  const entries = Object.entries(rates).sort((a, b) => a[0].localeCompare(b[0]));

  if (!entries.length) {
    ratesResult.textContent = "No se encontraron tasas disponibles.";
    return;
  }

  const rows = entries
    .map(([currency, value]) => `
      <tr>
        <td>${currency}</td>
        <td>${rateFormatter.format(Number(value))}</td>
      </tr>
    `)
    .join("");

  ratesResult.innerHTML = `
    <table class="rates-table" aria-label="Tasas de cambio">
      <thead>
        <tr>
          <th>Moneda</th>
          <th>Valor</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;

  const updated = formatTimestamp(data.last_updated);
  const nextUpdate = formatTimestamp(data.next_update);

  if (ratesMeta) {
    const parts = [`Base: ${data.base}`];
    if (updated) {
      parts.push(`Actualizado: ${updated}`);
    }
    if (nextUpdate) {
      parts.push(`Próxima actualización: ${nextUpdate}`);
    }
    ratesMeta.textContent = parts.join(" · ");
  }
}

function renderHistory(data) {
  if (!historyResult) {
    return;
  }

  const history = Array.isArray(data.history) ? data.history : [];
  if (!history.length) {
    historyResult.textContent = "No hay conversiones registradas.";
    return;
  }

  const items = history
    .map((entry) => {
      const amount = numberFormatter.format(entry.amount);
      const result = numberFormatter.format(entry.result);
      const timestamp = formatTimestamp(entry.timestamp);
      return `
        <li class="history-item">
          <strong>${amount} ${entry.from} → ${result} ${entry.to}</strong>
          ${timestamp ? `<span>${timestamp}</span>` : ""}
        </li>
      `;
    })
    .join("");

  historyResult.innerHTML = `<ul class="history-list">${items}</ul>`;

  if (historyMeta) {
    const source = data.source === "dynamodb" ? "Almacenado en DynamoDB" : "Datos de ejemplo";
    historyMeta.textContent = `Origen: ${source}`;
  }
}

async function handleConversion(event) {
  event.preventDefault();
  if (!converterForm || !convertButton) {
    return;
  }

  clearElement(conversionResult);
  clearElement(conversionError);

  const from = document.getElementById("from-currency").value;
  const to = document.getElementById("to-currency").value;
  const amount = document.getElementById("amount").value;

  if (!amount) {
    showError(conversionError, "La cantidad es obligatoria.");
    return;
  }

  convertButton.disabled = true;
  convertButton.textContent = "Convirtiendo...";

  try {
    const data = await request("/convert", {
      method: "POST",
      body: JSON.stringify({ from, to, amount }),
    });
    renderConversion(data);
    setStatus("Conversión exitosa.", "success");
  } catch (error) {
    showError(conversionError, error);
    setStatus("No fue posible convertir la divisa.", "error");
  } finally {
    convertButton.disabled = false;
    convertButton.textContent = "Convertir";
  }
}

async function handleLoadRates() {
  if (!loadRatesButton) {
    return;
  }

  clearElement(ratesResult);
  clearElement(ratesError);

  loadRatesButton.disabled = true;
  loadRatesButton.textContent = "Cargando...";

  const base = baseCurrencySelect ? baseCurrencySelect.value : "USD";

  try {
    const data = await request(`/rates?base=${encodeURIComponent(base)}`);
    renderRates(data);
    setStatus("Tasas actualizadas.", "success");
  } catch (error) {
    showError(ratesError, error);
    setStatus("No fue posible obtener las tasas.", "error");
  } finally {
    loadRatesButton.disabled = false;
    loadRatesButton.textContent = "Actualizar";
  }
}

async function handleLoadHistory() {
  if (!loadHistoryButton) {
    return;
  }

  clearElement(historyResult);
  clearElement(historyError);
  clearElement(historyMeta);

  loadHistoryButton.disabled = true;
  loadHistoryButton.textContent = "Cargando...";

  try {
    const data = await request("/history");
    renderHistory(data);
    setStatus("Historial cargado.", "success");
  } catch (error) {
    showError(historyError, error);
    setStatus("No fue posible obtener el historial.", "error");
  } finally {
    loadHistoryButton.disabled = false;
    loadHistoryButton.textContent = "Cargar historial";
  }
}

if (converterForm) {
  converterForm.addEventListener("submit", handleConversion);
}

if (loadRatesButton) {
  loadRatesButton.addEventListener("click", handleLoadRates);
}

if (loadHistoryButton) {
  loadHistoryButton.addEventListener("click", handleLoadHistory);
}

if (BASE_URL) {
  setStatus(`Usando backend en ${BASE_URL}`);
} else {
  setStatus("Configura la URL del backend en el atributo data-api-base del <body>.", "error");
  if (convertButton) {
    convertButton.disabled = true;
  }
  if (loadRatesButton) {
    loadRatesButton.disabled = true;
  }
  if (loadHistoryButton) {
    loadHistoryButton.disabled = true;
  }
}

// Cargar información inicial
handleLoadRates().catch(() => {
  // Silenciamos el error porque ya se maneja en handleLoadRates
});
handleLoadHistory().catch(() => {
  // Silenciamos el error porque ya se maneja en handleLoadHistory
});
