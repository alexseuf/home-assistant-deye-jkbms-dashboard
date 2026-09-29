class PVHistoryRangeCard extends HTMLElement {
  static getStubConfig() {
    return { charts: [] };
  }

  setConfig(config) {
    if (!config || !Array.isArray(config.charts) || !config.charts.length) {
      throw new Error("pv-history-range-card requires a non-empty charts array");
    }
    this._config = config;
    this._storageKey = config.storage_key || "pv_battery_dashboard_history_range";
    this._buildShell();
    this._loadRange();
    this._renderCharts();
  }

  set hass(hass) {
    this._hass = hass;
    for (const card of this._chartEls || []) {
      card.hass = hass;
    }
  }

  getCardSize() {
    return 20;
  }

  _buildShell() {
    this.innerHTML = `
      <style>
        .pvhr-controls {
          display: grid;
          grid-template-columns: minmax(180px, 1fr) minmax(180px, 1fr) auto auto;
          gap: 12px;
          align-items: end;
          padding: 16px;
        }
        .pvhr-field {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        .pvhr-field label {
          font-size: 13px;
          font-weight: 600;
          color: var(--primary-text-color);
        }
        .pvhr-field input {
          min-height: 40px;
          box-sizing: border-box;
          border: 1px solid var(--divider-color);
          border-radius: 10px;
          padding: 7px 10px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font: inherit;
        }
        .pvhr-button {
          min-height: 40px;
          border: 0;
          border-radius: 18px;
          padding: 0 18px;
          cursor: pointer;
          font: inherit;
          font-weight: 600;
        }
        .pvhr-apply {
          background: var(--primary-color);
          color: var(--text-primary-color, white);
        }
        .pvhr-reset {
          background: var(--secondary-background-color);
          color: var(--primary-text-color);
        }
        .pvhr-status {
          padding: 0 16px 14px;
          color: var(--secondary-text-color);
          font-size: 13px;
        }
        .pvhr-error {
          color: var(--error-color);
          font-weight: 600;
        }
        .pvhr-charts {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 12px;
        }
        .pvhr-chart-wide {
          grid-column: 1 / -1;
        }
        @media (max-width: 699px) {
          .pvhr-controls {
            grid-template-columns: 1fr;
          }
          .pvhr-charts {
            grid-template-columns: 1fr;
          }
          .pvhr-chart-wide {
            grid-column: 1;
          }
        }
      </style>
      <ha-card>
        <div class="pvhr-controls">
          <div class="pvhr-field">
            <label>Von</label>
            <input class="pvhr-start" type="datetime-local">
          </div>
          <div class="pvhr-field">
            <label>Bis</label>
            <input class="pvhr-end" type="datetime-local">
          </div>
          <button class="pvhr-button pvhr-apply">Anzeigen</button>
          <button class="pvhr-button pvhr-reset">Letzte 24 h</button>
        </div>
        <div class="pvhr-status"></div>
      </ha-card>
      <div class="pvhr-charts"></div>
    `;

    this.querySelector(".pvhr-apply").addEventListener("click", () => this._applyRange());
    this.querySelector(".pvhr-reset").addEventListener("click", () => {
      const end = new Date();
      const start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
      this.querySelector(".pvhr-start").value = this._toLocalInput(start);
      this.querySelector(".pvhr-end").value = this._toLocalInput(end);
      this._applyRange();
    });
  }

  _loadRange() {
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem(this._storageKey) || "null");
    } catch (_err) {
      saved = null;
    }

    const end = saved?.end ? new Date(saved.end) : new Date();
    const start = saved?.start
      ? new Date(saved.start)
      : new Date(end.getTime() - 24 * 60 * 60 * 1000);

    this.querySelector(".pvhr-start").value = this._toLocalInput(start);
    this.querySelector(".pvhr-end").value = this._toLocalInput(end);
  }

  _toLocalInput(date) {
    const pad = (value) => String(value).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }

  _getRange() {
    const start = new Date(this.querySelector(".pvhr-start").value);
    const end = new Date(this.querySelector(".pvhr-end").value);
    if (!Number.isFinite(start.getTime()) || !Number.isFinite(end.getTime())) {
      throw new Error("Bitte Start- und Endzeit vollständig auswählen.");
    }
    if (end <= start) {
      throw new Error("Die Endzeit muss nach der Startzeit liegen.");
    }
    return { start, end };
  }

  _applyRange() {
    const status = this.querySelector(".pvhr-status");
    try {
      const { start, end } = this._getRange();
      localStorage.setItem(
        this._storageKey,
        JSON.stringify({ start: start.toISOString(), end: end.toISOString() })
      );
      status.classList.remove("pvhr-error");
      this._renderCharts();
    } catch (err) {
      status.textContent = err.message;
      status.classList.add("pvhr-error");
    }
  }

  _bucketFor(durationMs) {
    const day = 24 * 60 * 60 * 1000;
    if (durationMs <= 2 * day) return "5min";
    if (durationMs <= 14 * day) return "30min";
    if (durationMs <= 60 * day) return "2h";
    return "1d";
  }

  _patchGrouping(value, duration) {
    if (Array.isArray(value)) {
      value.forEach((item) => this._patchGrouping(item, duration));
      return;
    }
    if (!value || typeof value !== "object") return;

    if (value.group_by && typeof value.group_by === "object") {
      value.group_by.duration = duration;
    }
    Object.values(value).forEach((item) => this._patchGrouping(item, duration));
  }

  _deepClone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  async _renderCharts() {
    if (!this._config || !this.querySelector(".pvhr-charts")) return;

    const status = this.querySelector(".pvhr-status");
    let range;
    try {
      range = this._getRange();
    } catch (err) {
      status.textContent = err.message;
      status.classList.add("pvhr-error");
      return;
    }

    const durationMs = range.end.getTime() - range.start.getTime();
    const durationMinutes = Math.max(1, Math.round(durationMs / 60000));
    const endOfCurrentMinute = Math.ceil(Date.now() / 60000) * 60000;
    const offsetMinutes = Math.round((range.end.getTime() - endOfCurrentMinute) / 60000);
    const bucket = this._bucketFor(durationMs);

    status.classList.remove("pvhr-error");
    status.textContent =
      `Zeitraum: ${range.start.toLocaleString()} – ${range.end.toLocaleString()} · Gruppierung: ${bucket}`;

    const helpers = await window.loadCardHelpers();
    const container = this.querySelector(".pvhr-charts");
    container.replaceChildren();
    this._chartEls = [];

    this._config.charts.forEach((sourceConfig, index) => {
      const cardConfig = this._deepClone(sourceConfig);
      cardConfig.graph_span = `${durationMinutes}min`;
      cardConfig.span = { end: "minute" };
      if (offsetMinutes !== 0) {
        cardConfig.span.offset = `${offsetMinutes > 0 ? "+" : ""}${offsetMinutes}min`;
      }
      this._patchGrouping(cardConfig, bucket);

      const wrapper = document.createElement("div");
      if (index < 2) wrapper.className = "pvhr-chart-wide";

      const card = helpers.createCardElement(cardConfig);
      if (this._hass) card.hass = this._hass;
      wrapper.appendChild(card);
      container.appendChild(wrapper);
      this._chartEls.push(card);
    });
  }
}

if (!customElements.get("pv-history-range-card")) {
  customElements.define("pv-history-range-card", PVHistoryRangeCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "pv-history-range-card",
  name: "PV History Range Card",
  description: "Custom selectable history range for PV & Battery Dashboard",
});
