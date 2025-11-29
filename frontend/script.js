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
      const entryId = entry.timestamp || entry.id; // Use timestamp as ID
      const escapedId = entryId.replace(/'/g, "&#39;");
      const escapedEntry = JSON.stringify(entry).replace(/"/g, '&quot;').replace(/'/g, "&#39;");
      return `
        <li class="history-item">
          <div class="history-item-content">
            <div class="history-item-info">
              <strong>${amount} ${entry.from} → ${result} ${entry.to}</strong>
              ${timestamp ? `<span>${timestamp}</span>` : ""}
            </div>
            <div class="history-item-actions">
              <button class="edit-button" onclick="showEditModal('${escapedId}', ${escapedEntry})" title="Editar conversión">✏️</button>
              <button class="delete-button" onclick="showDeleteConfirmation('${escapedId}')" title="Eliminar conversión">🗑️</button>
            </div>
          </div>
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

async function handleDeleteHistoryItem(id) {
  if (!id) {
    setStatus("ID de conversión inválido.", "error");
    return;
  }

  clearElement(historyError);

  // Deshabilitar todos los botones de eliminar durante la operación
  const deleteButtons = document.querySelectorAll('.delete-button');
  deleteButtons.forEach(button => {
    button.disabled = true;
  });

  try {
    await request(`/history/${id}`, {
      method: "DELETE"
    });
    
    setStatus("Conversión eliminada exitosamente.", "success");
    
    // Recargar el historial para mostrar los cambios
    await handleLoadHistory();
  } catch (error) {
    showError(historyError, error);
    setStatus("No fue posible eliminar la conversión.", "error");
    
    // Rehabilitar los botones en caso de error
    deleteButtons.forEach(button => {
      button.disabled = false;
    });
  }
}

function showDeleteConfirmation(id) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal">
      <h3 class="delete">⚠️ Confirmar eliminación</h3>
      <p>¿Estás seguro de que deseas eliminar esta conversión del historial?</p>
      <p><strong>Esta acción no se puede deshacer.</strong></p>
      <div class="modal-actions">
        <button class="modal-button cancel" onclick="closeModal()">Cancelar</button>
        <button class="modal-button confirm" onclick="confirmDelete('${id}')">Eliminar</button>
      </div>
    </div>
  `;
  
  // Cerrar modal al hacer clic en el overlay
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });
  
  // Cerrar modal con Escape
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      closeModal();
      document.removeEventListener('keydown', handleEscape);
    }
  };
  document.addEventListener('keydown', handleEscape);
  
  document.body.appendChild(modal);
}

function closeModal() {
  const modal = document.querySelector('.modal-overlay');
  if (modal) {
    modal.remove();
  }
}

function confirmDelete(id) {
  closeModal();
  handleDeleteHistoryItem(id);
}

function showEditModal(id, entryData) {
  const entry = typeof entryData === 'string' ? JSON.parse(entryData) : entryData;
  
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal">
      <h3>✏️ Editar Conversión</h3>
      <form id="edit-form" class="modal-form">
        <div class="modal-form-row">
          <div class="modal-form-group">
            <label for="edit-from">Moneda origen</label>
            <select id="edit-from" required>
              <option value="USD" ${entry.from === 'USD' ? 'selected' : ''}>USD</option>
              <option value="EUR" ${entry.from === 'EUR' ? 'selected' : ''}>EUR</option>
              <option value="COP" ${entry.from === 'COP' ? 'selected' : ''}>COP</option>
            </select>
          </div>
          <div class="modal-form-group">
            <label for="edit-to">Moneda destino</label>
            <select id="edit-to" required>
              <option value="USD" ${entry.to === 'USD' ? 'selected' : ''}>USD</option>
              <option value="EUR" ${entry.to === 'EUR' ? 'selected' : ''}>EUR</option>
              <option value="COP" ${entry.to === 'COP' ? 'selected' : ''}>COP</option>
            </select>
          </div>
        </div>
        <div class="modal-form-row">
          <div class="modal-form-group">
            <label for="edit-amount">Cantidad</label>
            <input type="number" id="edit-amount" step="any" min="0" value="${entry.amount}" required>
          </div>
          <div class="modal-form-group">
            <label for="edit-result">Resultado</label>
            <input type="number" id="edit-result" step="any" min="0" value="${entry.result}" required>
          </div>
        </div>
        <div class="modal-form-group full-width">
          <label for="edit-rate">Tasa de cambio</label>
          <input type="number" id="edit-rate" step="any" min="0" value="${entry.rate || ''}" placeholder="Opcional">
        </div>
      </form>
      <div class="modal-actions">
        <button class="modal-button cancel" onclick="closeModal()">Cancelar</button>
        <button class="modal-button save" onclick="saveEdit('${id}')">Guardar</button>
      </div>
    </div>
  `;
  
  // Cerrar modal al hacer clic en el overlay
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });
  
  // Cerrar modal con Escape
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      closeModal();
      document.removeEventListener('keydown', handleEscape);
    }
  };
  document.addEventListener('keydown', handleEscape);
  
  // Manejar submit del formulario
  modal.addEventListener('submit', (e) => {
    e.preventDefault();
    saveEdit(id);
  });
  
  document.body.appendChild(modal);
}

async function saveEdit(id) {
  const form = document.getElementById('edit-form');
  if (!form || !form.checkValidity()) {
    return;
  }
  
  const formData = {
    from: document.getElementById('edit-from').value,
    to: document.getElementById('edit-to').value,
    amount: parseFloat(document.getElementById('edit-amount').value),
    result: parseFloat(document.getElementById('edit-result').value)
  };
  
  const rateValue = document.getElementById('edit-rate').value;
  if (rateValue && rateValue.trim() !== '') {
    formData.rate = parseFloat(rateValue);
  }
  
  // Deshabilitar botones durante la operación
  const saveButton = document.querySelector('.modal-button.save');
  const cancelButton = document.querySelector('.modal-button.cancel');
  
  if (saveButton) {
    saveButton.disabled = true;
    saveButton.textContent = 'Guardando...';
  }
  if (cancelButton) {
    cancelButton.disabled = true;
  }
  
  try {
    const response = await request(`/history/${id}`, {
      method: 'PUT',
      body: JSON.stringify(formData)
    });
    
    closeModal();
    setStatus('Conversión actualizada exitosamente.', 'success');
    
    // Recargar el historial para mostrar los cambios
    await handleLoadHistory();
  } catch (error) {
    setStatus('No fue posible actualizar la conversión.', 'error');
    showError(historyError, error);
    
    // Rehabilitar botones en caso de error
    if (saveButton) {
      saveButton.disabled = false;
      saveButton.textContent = 'Guardar';
    }
    if (cancelButton) {
      cancelButton.disabled = false;
    }
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
