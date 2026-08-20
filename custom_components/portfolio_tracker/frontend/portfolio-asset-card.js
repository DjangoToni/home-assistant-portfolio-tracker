const CARD_TAG = "portfolio-asset-card";
const EDITOR_TAG = "portfolio-asset-card-editor";
const PORTFOLIO_CARD_TAG = "portfolio-overview-card";
const PORTFOLIO_EDITOR_TAG = "portfolio-overview-card-editor";
const CARD_VERSION = "1.4.1";

const LABELS = {
  de: {
    position: "Positionswert",
    today: "heute",
    range: "Kursverlauf",
    details: "Details",
    sourceYahoo: "Yahoo Finance",
    sourceCoinGecko: "CoinGecko",
    noHistory: "Noch keine historischen Daten verfügbar",
    selectEntity: "Asset",
    selectHint: "Wähle direkt die Aktie, Kryptowährung oder das andere Asset.",
    customName: "Eigener Kartenname (optional)",
    invalidEntity: "Bitte wähle einen Sensor eines Portfolio-Assets.",
    missingEntity: "Entität {entity} wurde nicht gefunden.",
    days: "Tage",
    tradingDays: "Handelstage",
    stock: "Aktie",
    crypto: "Crypto",
    index: "Marktindex",
    previousClose: "Vorheriger Schlussstand",
    open: "Markt offen",
    closed: "Markt geschlossen",
    active: "24/7 aktiv",
    transactions: "Transaktionshistorie",
    noTransactions: "Noch keine Transaktionen erfasst",
    realized: "Realisiert",
    fees: "Gebühren",
    taxes: "Steuern",
    quantity: "Menge",
    priceLabel: "Preis",
    unitPrice: "Preis pro Einheit",
    totalAmount: "Gesamtbetrag",
    marketRate: "Marktkurs beim Kauf",
    priceAxis: "Kurs",
    minutesAgo: "vor {minutes} Min.",
    transactionTypes: { opening: "Anfangsbestand", buy: "Kauf", sell: "Verkauf" },
    metrics: {
      dayRange: "Tagesbereich",
      weekRange: "52 Wochen",
      average50: "50-Tage-Ø",
      dividendYield: "Dividendenrendite",
      pe: "KGV",
      analysts: "Analysten",
      range24h: "24-h-Bereich",
      volume24h: "24-h-Volumen",
      marketCap: "Market Cap",
      rank: "Rang",
      ath: "Allzeithoch",
      circulating: "Umlaufmenge",
    },
  },
  en: {
    position: "Position value",
    today: "today",
    range: "Price history",
    details: "Details",
    sourceYahoo: "Yahoo Finance",
    sourceCoinGecko: "CoinGecko",
    noHistory: "Historical data is not available yet",
    selectEntity: "Asset",
    selectHint: "Select the stock, cryptocurrency, or other asset directly.",
    customName: "Custom card name (optional)",
    invalidEntity: "Please select a Portfolio Tracker asset sensor.",
    missingEntity: "Entity {entity} was not found.",
    days: "days",
    tradingDays: "trading days",
    stock: "Stock",
    crypto: "Crypto",
    index: "Market index",
    previousClose: "Previous close",
    open: "Market open",
    closed: "Market closed",
    active: "Active 24/7",
    transactions: "Transaction history",
    noTransactions: "No transactions recorded yet",
    realized: "Realized",
    fees: "Fees",
    taxes: "Taxes",
    quantity: "Quantity",
    priceLabel: "Price",
    unitPrice: "Price per unit",
    totalAmount: "Total amount",
    marketRate: "Market price at purchase",
    priceAxis: "Price",
    minutesAgo: "{minutes} min ago",
    transactionTypes: { opening: "Opening", buy: "Buy", sell: "Sell" },
    metrics: {
      dayRange: "Day range",
      weekRange: "52 weeks",
      average50: "50-day average",
      dividendYield: "Dividend yield",
      pe: "PE ratio",
      analysts: "Analysts",
      range24h: "24h range",
      volume24h: "24h volume",
      marketCap: "Market cap",
      rank: "Rank",
      ath: "All-time high",
      circulating: "Circulating supply",
    },
  },
};

LABELS.fr = {
  ...LABELS.en,
  position: "Valeur de la position",
  today: "aujourd'hui",
  range: "Historique du cours",
  details: "Détails",
  noHistory: "Les données historiques ne sont pas encore disponibles",
  selectEntity: "Actif",
  selectHint: "Sélectionnez directement l'action, la cryptomonnaie ou un autre actif.",
  customName: "Nom personnalisé de la carte (facultatif)",
  invalidEntity: "Veuillez sélectionner un capteur d'actif Portfolio Tracker.",
  missingEntity: "L'entité {entity} est introuvable.",
  days: "jours",
  tradingDays: "jours de bourse",
  stock: "Action",
  crypto: "Crypto",
  index: "Indice boursier",
  previousClose: "Clôture précédente",
  open: "Marché ouvert",
  closed: "Marché fermé",
  active: "Actif 24 h/24",
  transactions: "Historique des transactions",
  noTransactions: "Aucune transaction enregistrée",
  realized: "Réalisé",
  fees: "Frais",
  taxes: "Impôts",
  quantity: "Quantité",
  priceLabel: "Prix",
  unitPrice: "Prix unitaire",
  totalAmount: "Montant total",
  marketRate: "Cours du marché lors de l'achat",
  priceAxis: "Cours",
  minutesAgo: "il y a {minutes} min",
  transactionTypes: { opening: "Solde initial", buy: "Achat", sell: "Vente" },
  metrics: {
    dayRange: "Plage du jour",
    weekRange: "52 semaines",
    average50: "Moyenne sur 50 jours",
    dividendYield: "Rendement du dividende",
    pe: "Ratio cours/bénéfice",
    analysts: "Analystes",
    range24h: "Plage sur 24 h",
    volume24h: "Volume sur 24 h",
    marketCap: "Capitalisation",
    rank: "Rang",
    ath: "Plus haut historique",
    circulating: "Offre en circulation",
  },
};

LABELS.it = {
  ...LABELS.en,
  position: "Valore della posizione",
  today: "oggi",
  range: "Andamento del prezzo",
  details: "Dettagli",
  noHistory: "I dati storici non sono ancora disponibili",
  selectEntity: "Asset",
  selectHint: "Seleziona direttamente l'azione, la criptovaluta o un altro asset.",
  customName: "Nome personalizzato della scheda (facoltativo)",
  invalidEntity: "Seleziona un sensore asset di Portfolio Tracker.",
  missingEntity: "L'entità {entity} non è stata trovata.",
  days: "giorni",
  tradingDays: "giorni di negoziazione",
  stock: "Azione",
  crypto: "Crypto",
  index: "Indice di mercato",
  previousClose: "Chiusura precedente",
  open: "Mercato aperto",
  closed: "Mercato chiuso",
  active: "Attivo 24/7",
  transactions: "Cronologia delle transazioni",
  noTransactions: "Nessuna transazione registrata",
  realized: "Realizzato",
  fees: "Commissioni",
  taxes: "Imposte",
  quantity: "Quantità",
  priceLabel: "Prezzo",
  unitPrice: "Prezzo unitario",
  totalAmount: "Importo totale",
  marketRate: "Prezzo di mercato all'acquisto",
  priceAxis: "Prezzo",
  minutesAgo: "{minutes} min fa",
  transactionTypes: { opening: "Saldo iniziale", buy: "Acquisto", sell: "Vendita" },
  metrics: {
    dayRange: "Intervallo giornaliero",
    weekRange: "52 settimane",
    average50: "Media a 50 giorni",
    dividendYield: "Rendimento da dividendo",
    pe: "Rapporto P/E",
    analysts: "Analisti",
    range24h: "Intervallo 24 ore",
    volume24h: "Volume 24 ore",
    marketCap: "Capitalizzazione",
    rank: "Posizione",
    ath: "Massimo storico",
    circulating: "Offerta circolante",
  },
};

const PORTFOLIO_LABELS = {
  de: {
    title: "Mein Portfolio",
    portfolio: "Portfolio",
    totalValue: "Gesamtwert",
    cost: "Einstandswert",
    gain: "Gewinn / Verlust",
    return: "Rendite",
    realized: "Realisiert",
    fees: "Gebühren",
    taxes: "Steuern",
    daily: "Heute",
    allocation: "Asset-Aufteilung",
    currencies: "Währungen",
    marketIndices: "Marktindizes",
    professionalPerformance: "Professionelle Auswertung",
    portfolioLine: "Portfolio",
    benchmark: "Vergleichsindex",
    netInvested: "Netto investiert",
    totalResult: "Gesamtergebnis",
    totalReturn: "Gesamtrendite",
    timeWeighted: "Zeitgewichtet",
    excessReturn: "Überrendite",
    purchases: "Käufe",
    sales: "Verkäufe",
    noPerformance: "Noch nicht genügend historische Daten vorhanden",
    positions: "Positionen",
    noAssets: "Noch keine Positionen vorhanden",
    watchlist: "Beobachtete Assets",
    activeAssets: "Aktive Assets",
    managePortfolio: "Portfolio verwalten",
    watchPrice: "Kurs",
    alertBelow: "Alarm unter",
    alertAbove: "Alarm über",
    alarmStatus: "Status",
    monitoring: "Beobachtung aktiv",
    alarmActive: "Kursalarm aktiv",
    updated: "Aktualisiert",
    view: "Darstellung",
    overviewView: "Übersicht mit Diagramm",
    tableView: "Tabelle",
    asset: "Asset",
    type: "Typ",
    value: "Wert",
    share: "Anteil",
    closeDetails: "Detailkarte schließen",
    baseEquivalent: "Basiswert",
    fxConverted: "Fremdwährungen zum aktuellen Tageskurs umgerechnet",
    assetGroups: {
      stock: "Aktien",
      crypto: "Kryptowährungen",
      etf: "ETFs",
      fund: "Fonds",
      currency: "Währungen",
      other: "Sonstige",
    },
    assetTypes: {
      stock: "Aktie",
      crypto: "Kryptowährung",
      etf: "ETF",
      fund: "Fonds",
      currency: "Währung",
      other: "Sonstiges",
    },
  },
  en: {
    title: "My Portfolio",
    portfolio: "Portfolio",
    totalValue: "Total value",
    cost: "Cost basis",
    gain: "Gain / loss",
    return: "Return",
    realized: "Realized",
    fees: "Fees",
    taxes: "Taxes",
    daily: "Today",
    allocation: "Asset allocation",
    currencies: "Currencies",
    marketIndices: "Market indices",
    professionalPerformance: "Professional performance",
    portfolioLine: "Portfolio",
    benchmark: "Benchmark",
    netInvested: "Net invested",
    totalResult: "Total result",
    totalReturn: "Total return",
    timeWeighted: "Time weighted",
    excessReturn: "Excess return",
    purchases: "Purchases",
    sales: "Sales",
    noPerformance: "Not enough historical data available yet",
    positions: "Positions",
    noAssets: "No positions available yet",
    watchlist: "Watched assets",
    activeAssets: "Active assets",
    managePortfolio: "Manage portfolio",
    watchPrice: "Price",
    alertBelow: "Alert below",
    alertAbove: "Alert above",
    alarmStatus: "Status",
    monitoring: "Monitoring active",
    alarmActive: "Price alert active",
    updated: "Updated",
    view: "View",
    overviewView: "Overview with chart",
    tableView: "Table",
    asset: "Asset",
    type: "Type",
    value: "Value",
    share: "Share",
    closeDetails: "Close detail card",
    baseEquivalent: "Base value",
    fxConverted: "Foreign currencies converted at current market rates",
    assetGroups: {
      stock: "Stocks",
      crypto: "Cryptocurrencies",
      etf: "ETFs",
      fund: "Funds",
      currency: "Currencies",
      other: "Other",
    },
    assetTypes: {
      stock: "Stock",
      crypto: "Cryptocurrency",
      etf: "ETF",
      fund: "Fund",
      currency: "Currency",
      other: "Other",
    },
  },
};

PORTFOLIO_LABELS.fr = {
  ...PORTFOLIO_LABELS.en,
  title: "Mon portefeuille",
  totalValue: "Valeur totale",
  cost: "Prix de revient",
  gain: "Gain / perte",
  return: "Rendement",
  realized: "Réalisé",
  fees: "Frais",
  taxes: "Impôts",
  daily: "Aujourd'hui",
  allocation: "Répartition des actifs",
  currencies: "Devises",
  marketIndices: "Indices boursiers",
  professionalPerformance: "Analyse professionnelle",
  benchmark: "Indice de référence",
  netInvested: "Capital net investi",
  totalResult: "Résultat total",
  totalReturn: "Rendement total",
  timeWeighted: "Pondéré dans le temps",
  excessReturn: "Surperformance",
  purchases: "Achats",
  sales: "Ventes",
  noPerformance: "Les données historiques sont encore insuffisantes",
  positions: "Positions",
  noAssets: "Aucune position disponible",
  watchlist: "Actifs surveillés",
  activeAssets: "Actifs actifs",
  managePortfolio: "Gérer le portefeuille",
  watchPrice: "Cours",
  alertBelow: "Alerte sous",
  alertAbove: "Alerte au-dessus",
  monitoring: "Surveillance active",
  alarmActive: "Alerte de cours active",
  updated: "Actualisé",
  view: "Affichage",
  overviewView: "Aperçu avec graphique",
  tableView: "Tableau",
  type: "Type",
  value: "Valeur",
  share: "Part",
  closeDetails: "Fermer la fiche détaillée",
  baseEquivalent: "Valeur de base",
  fxConverted: "Devises étrangères converties aux cours actuels",
  assetGroups: {
    stock: "Actions",
    crypto: "Cryptomonnaies",
    etf: "ETF",
    fund: "Fonds",
    currency: "Devises",
    other: "Autres",
  },
  assetTypes: {
    stock: "Action",
    crypto: "Cryptomonnaie",
    etf: "ETF",
    fund: "Fonds",
    currency: "Devise",
    other: "Autre",
  },
};

PORTFOLIO_LABELS.it = {
  ...PORTFOLIO_LABELS.en,
  title: "Il mio portafoglio",
  totalValue: "Valore totale",
  cost: "Costo di acquisto",
  gain: "Guadagno / perdita",
  return: "Rendimento",
  realized: "Realizzato",
  fees: "Commissioni",
  taxes: "Imposte",
  daily: "Oggi",
  allocation: "Allocazione degli asset",
  currencies: "Valute",
  marketIndices: "Indici di mercato",
  professionalPerformance: "Analisi professionale",
  benchmark: "Indice di riferimento",
  netInvested: "Capitale netto investito",
  totalResult: "Risultato totale",
  totalReturn: "Rendimento totale",
  timeWeighted: "Ponderato nel tempo",
  excessReturn: "Sovraperformance",
  purchases: "Acquisti",
  sales: "Vendite",
  noPerformance: "I dati storici non sono ancora sufficienti",
  positions: "Posizioni",
  noAssets: "Nessuna posizione disponibile",
  watchlist: "Asset osservati",
  activeAssets: "Asset attivi",
  managePortfolio: "Gestisci portafoglio",
  watchPrice: "Prezzo",
  alertBelow: "Allarme sotto",
  alertAbove: "Allarme sopra",
  monitoring: "Osservazione attiva",
  alarmActive: "Allarme prezzo attivo",
  updated: "Aggiornato",
  view: "Vista",
  overviewView: "Panoramica con grafico",
  tableView: "Tabella",
  type: "Tipo",
  value: "Valore",
  share: "Quota",
  closeDetails: "Chiudi scheda dettagli",
  baseEquivalent: "Valore base",
  fxConverted: "Valute estere convertite ai tassi correnti",
  assetGroups: {
    stock: "Azioni",
    crypto: "Criptovalute",
    etf: "ETF",
    fund: "Fondi",
    currency: "Valute",
    other: "Altro",
  },
  assetTypes: {
    stock: "Azione",
    crypto: "Criptovaluta",
    etf: "ETF",
    fund: "Fondo",
    currency: "Valuta",
    other: "Altro",
  },
};

const LANGUAGE_LOCALES = {
  de: "de-CH",
  en: "en-US",
  fr: "fr-CH",
  it: "it-CH",
};

function normalizeLanguage(value) {
  const language = String(value || "en")
    .toLowerCase()
    .split(/[-_]/, 1)[0];
  return Object.hasOwn(LANGUAGE_LOCALES, language) ? language : "en";
}

function languageFromHass(hass) {
  return normalizeLanguage(hass?.locale?.language);
}

function localeFromHass(hass) {
  return LANGUAGE_LOCALES[languageFromHass(hass)];
}

const CARD_CATALOG_LABELS = {
  de: {
    assetName: "Portfolio-Asset-Detailkarte",
    assetDescription: "Detailkarte für Aktien, Kryptowährungen und andere Portfolio-Assets.",
    overviewName: "Portfolio-Übersichtskarte",
    overviewDescription: "Portfolioübersicht mit Performance, Aufteilung und Watchlist.",
  },
  en: {
    assetName: "Portfolio Asset Card",
    assetDescription: "Detail card for stocks, cryptocurrencies, and other portfolio assets.",
    overviewName: "Portfolio Overview Card",
    overviewDescription: "Portfolio overview with performance, allocation, and watchlist.",
  },
  fr: {
    assetName: "Fiche détaillée d'actif",
    assetDescription: "Fiche détaillée pour les actions, cryptomonnaies et autres actifs du portefeuille.",
    overviewName: "Aperçu du portefeuille",
    overviewDescription: "Aperçu avec performance, répartition des actifs et liste de surveillance.",
  },
  it: {
    assetName: "Scheda dettagli asset",
    assetDescription: "Scheda dettagliata per azioni, criptovalute e altri asset del portafoglio.",
    overviewName: "Panoramica portafoglio",
    overviewDescription: "Panoramica con performance, allocazione e lista di osservazione.",
  },
};

const METRIC_KEYS = {
  stock: [
    ["dayRange", "stock_day_low", "stock_day_high", "range"],
    ["weekRange", "stock_fifty_two_week_low", "stock_fifty_two_week_high", "range"],
    ["average50", "stock_fifty_day_average"],
    ["dividendYield", "stock_dividend_yield"],
    ["pe", "stock_price_earnings_ratio"],
    ["analysts", "stock_average_analyst_rating"],
  ],
  crypto: [
    ["range24h", "crypto_low_24h", "crypto_high_24h", "range"],
    ["volume24h", "crypto_volume_24h"],
    ["marketCap", "crypto_market_cap"],
    ["rank", "crypto_market_cap_rank", null, "rank"],
    ["ath", "crypto_ath"],
    ["circulating", "crypto_circulating_supply"],
  ],
  index: [
    ["dayRange", "stock_day_low", "stock_day_high", "range"],
    ["weekRange", "stock_fifty_two_week_low", "stock_fifty_two_week_high", "range"],
    ["average50", "stock_fifty_day_average"],
  ],
};

class PortfolioAssetCard extends HTMLElement {
  static getStubConfig(hass, entities = [], entitiesFallback = []) {
    const candidates = [
      ...entities,
      ...entitiesFallback,
      ...Object.keys(hass?.states || {}),
    ];
    const entity = candidates.find(
      (entityId) => hass?.states?.[entityId]?.attributes?.metric_key === "holding_price",
    ) || candidates.find(
      (entityId) => hass?.states?.[entityId]?.attributes?.asset_id,
    );
    return { entity: entity || "" };
  }

  static getConfigElement() {
    return document.createElement(EDITOR_TAG);
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._renderSignature = "";
  }

  setConfig(config) {
    this._config = { ...(config || {}) };
    this._renderSignature = "";
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 6;
  }

  _language() {
    return languageFromHass(this._hass);
  }

  _assetEntities() {
    if (!this._hass || !this._config?.entity) return {};
    const selectedRegistry = this._hass.entities?.[this._config.entity];
    const selectedState = this._hass.states?.[this._config.entity];
    const deviceId = selectedRegistry?.device_id;
    const assetId = selectedState?.attributes?.asset_id;
    const entries = Object.entries(this._hass.states).filter(([entityId, state]) => {
      if (!state.attributes?.asset_id) return false;
      if (deviceId) return this._hass.entities?.[entityId]?.device_id === deviceId;
      return state.attributes.asset_id === assetId;
    });
    const result = {};
    for (const [entityId, state] of entries) {
      const key = this._entityKey(entityId, state);
      if (key) result[key] = state;
    }
    return result;
  }

  _entityKey(entityId, state) {
    if (state?.attributes?.metric_key) return state.attributes.metric_key;
    const registry = this._hass?.entities?.[entityId];
    if (registry?.translation_key) return registry.translation_key;
    const knownKeys = [
      "holding_daily_change", "holding_gain_percent", "holding_purchase_price",
      "holding_previous_close", "holding_quantity", "holding_price", "holding_value",
      "holding_gain", "holding_cost", "holding_realized_gain", "holding_fees",
      "holding_taxes", "holding_transactions", "stock_history", "crypto_history",
      ...METRIC_KEYS.stock.flat().filter((key) => typeof key === "string" && key.startsWith("stock_")),
      ...METRIC_KEYS.crypto.flat().filter((key) => typeof key === "string" && key.startsWith("crypto_")),
      "stock_market_state",
    ];
    return knownKeys.find((key) => entityId.endsWith(key.replaceAll("holding_", ""))) || null;
  }

  _formatState(state, options = {}) {
    if (!state || ["unknown", "unavailable", "none", "null"].includes(state.state)) return "—";
    const numeric = Number(state.state);
    if (!Number.isFinite(numeric)) return state.state;
    const language = localeFromHass(this._hass);
    const unit = state.attributes.unit_of_measurement || "";
    const maximumFractionDigits = options.decimals ?? (Math.abs(numeric) < 10 ? 2 : 2);
    const compact = options.compact ?? Math.abs(numeric) >= 1_000_000;
    const value = new Intl.NumberFormat(language, {
      notation: compact ? "compact" : "standard",
      maximumFractionDigits,
    }).format(numeric);
    return `${options.prefix || ""}${value}${unit ? ` ${unit}` : ""}`;
  }

  _signedState(state, suffix) {
    if (!state || !Number.isFinite(Number(state.state))) return "—";
    const value = Number(state.state);
    const arrow = value >= 0 ? "▲" : "▼";
    const formatted = new Intl.NumberFormat(localeFromHass(this._hass), {
      maximumFractionDigits: 2,
      minimumFractionDigits: 2,
      signDisplay: "never",
    }).format(Math.abs(value));
    return `${arrow} ${formatted}% ${suffix}`;
  }

  _history(entities, assetType) {
    const state = entities[assetType === "crypto" ? "crypto_history" : "stock_history"];
    const history = state?.attributes?.history;
    if (!Array.isArray(history)) return [];
    return history
      .map((point) => ({
        timestamp: point.timestamp,
        value: Number(assetType === "crypto" ? point.price : point.close),
      }))
      .filter((point) => Number.isFinite(point.value));
  }

  _chart(history) {
    if (history.length < 2) return null;
    const values = history.map((point) => point.value);
    const minimum = Math.min(...values);
    const maximum = Math.max(...values);
    const span = maximum - minimum || 1;
    const left = 16;
    const right = 670;
    const top = 28;
    const bottom = 168;
    const points = values.map((value, index) => {
      const x = left + (index / (values.length - 1)) * (right - left);
      const y = bottom - ((value - minimum) / span) * (bottom - top);
      return [x, y];
    });
    const line = points.map(([x, y], index) => `${index ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
    const area = `${line} L${right} ${bottom} L${left} ${bottom} Z`;
    const last = points.at(-1);
    const yTickCount = 9;
    const yTicks = Array.from({ length: yTickCount }, (_, index) => ({
      y: top + ((bottom - top) * index) / (yTickCount - 1),
      value: maximum - (span * index) / (yTickCount - 1),
      major: index % 2 === 0,
    }));
    const xTickCount = Math.min(9, history.length);
    const xIndexes = [...new Set(Array.from(
      { length: xTickCount },
      (_, index) => Math.round((index * (history.length - 1)) / (xTickCount - 1)),
    ))];
    const xTicks = xIndexes.map((index) => ({
      x: left + (index / (history.length - 1)) * (right - left),
      timestamp: history[index].timestamp,
      anchor: index === 0 ? "start" : index === history.length - 1 ? "end" : "middle",
    }));
    const xMinorTicks = xTicks.slice(0, -1).map((tick, index) => (
      (tick.x + xTicks[index + 1].x) / 2
    ));
    return { line, area, last, minimum, maximum, yTicks, xTicks, xMinorTicks, left, right, top, bottom };
  }

  _metricValue(definition, entities) {
    const [, firstKey, secondKey, mode] = definition;
    const first = entities[firstKey];
    if (mode === "range") {
      const second = entities[secondKey];
      if (!first || !second || first.state === "unavailable" || second.state === "unavailable") return "—";
      return `${this._formatState(first)} – ${this._formatState(second)}`;
    }
    if (mode === "rank") {
      return first && Number.isFinite(Number(first.state)) ? `#${Number(first.state)}` : "—";
    }
    return this._formatState(first, { compact: Math.abs(Number(first?.state)) >= 1_000_000 });
  }

  _assetIcon(assetType) {
    const icons = {
      stock: "mdi:chart-line",
      etf: "mdi:chart-areaspline",
      fund: "mdi:bank-outline",
      crypto: "mdi:currency-btc",
      currency: "mdi:swap-horizontal",
      index: "mdi:chart-timeline-variant",
      other: "mdi:finance",
    };
    return icons[assetType] || icons.other;
  }

  _render() {
    if (!this._hass) return;
    if (!this._config?.entity) {
      const entity = Object.entries(this._hass.states).find(
        ([, state]) => state.attributes?.metric_key === "holding_price",
      )?.[0];
      if (!entity) return;
      this._config = { ...(this._config || {}), entity };
    }
    const entities = this._assetEntities();
    const selected = this._hass.states[this._config.entity];
    if (!selected) {
      const labels = LABELS[this._language()];
      const message = labels.missingEntity.replace("{entity}", this._config.entity);
      this.shadowRoot.innerHTML = `<ha-card><div class="missing">${this._escape(message)}</div></ha-card>`;
      return;
    }
    const attributes = selected.attributes;
    const labels = LABELS[this._language()];
    if (!attributes.asset_id) {
      this.shadowRoot.innerHTML = `<ha-card><div class="missing">${labels.invalidEntity}</div></ha-card>`;
      return;
    }
    const configuredAssetType = attributes.asset_type || "other";
    const assetType = configuredAssetType === "crypto"
      ? "crypto"
      : configuredAssetType === "index" ? "index" : "stock";
    const assetIcon = this._assetIcon(configuredAssetType);
    const price = entities.holding_price || selected;
    const value = entities.holding_value;
    const gain = entities.holding_gain;
    const gainPercent = entities.holding_gain_percent;
    const daily = entities.holding_daily_change;
    const history = this._history(entities, assetType);
    const chart = this._chart(history);
    const symbol = attributes.symbol || price?.attributes?.symbol || "Asset";
    const deviceId = this._hass.entities?.[this._config.entity]?.device_id;
    const device = deviceId ? this._hass.devices?.[deviceId] : null;
    const name = this._config.name || device?.name_by_user || device?.name || attributes.friendly_name || symbol;
    const stateEntity = entities.stock_market_state;
    const state = assetType === "crypto"
      ? labels.active
      : stateEntity?.state === "REGULAR" ? labels.open : labels.closed;
    const statusClass = assetType === "crypto" || stateEntity?.state === "REGULAR" ? "positive" : "neutral";
    const changeValue = Number(daily?.state);
    const direction = Number.isFinite(changeValue) && changeValue < 0 ? "negative" : "positive";
    const source = assetType === "crypto" ? labels.sourceCoinGecko : labels.sourceYahoo;
    const assetTypeName = configuredAssetType === "index"
      ? labels.index
      : PORTFOLIO_LABELS[this._language()].assetTypes[configuredAssetType]
        || configuredAssetType;
    const metricDefinitions = METRIC_KEYS[assetType];
    const transactionEntity = entities.holding_transactions;
    const transactions = Array.isArray(transactionEntity?.attributes?.transactions)
      ? transactionEntity.attributes.transactions
      : [];
    const signature = JSON.stringify([
      this._config, Object.values(entities).map((entity) => [
        entity.entity_id,
        entity.state,
        entity.last_updated,
        entity.attributes?.metric_key === "holding_transactions" ? entity.attributes.transactions : null,
      ]),
    ]);
    if (signature === this._renderSignature) return;
    this._renderSignature = signature;

    const metricHtml = metricDefinitions.map((definition) => `
      <div class="metric">
        <div class="metric-label">${labels.metrics[definition[0]]}</div>
        <div class="metric-value">${this._escape(this._metricValue(definition, entities))}</div>
      </div>`).join("");
    const chartHtml = chart ? `
      <svg viewBox="0 0 760 218" role="img" aria-label="${labels.range}">
        <text class="axis-title" x="752" y="10" text-anchor="end">${this._escape(labels.priceAxis)} (${this._escape(price?.attributes?.unit_of_measurement || "")})</text>
        ${chart.yTicks.map((tick) => `<line class="grid horizontal ${tick.major ? "major" : "minor"}" x1="${chart.left}" y1="${tick.y}" x2="${chart.right}" y2="${tick.y}"></line><text class="axis price-axis ${tick.major ? "major" : "minor"}" x="680" y="${tick.y + 3}" text-anchor="start">${this._escape(this._compactNumber(tick.value))}</text>`).join("")}
        ${chart.xMinorTicks.map((x) => `<line class="grid vertical minor" x1="${x}" y1="${chart.top}" x2="${x}" y2="${chart.bottom}"></line>`).join("")}
        ${chart.xTicks.map((tick) => `<line class="grid vertical major" x1="${tick.x}" y1="${chart.top}" x2="${tick.x}" y2="${chart.bottom}"></line><text class="axis date-axis" x="${tick.x}" y="192" text-anchor="${tick.anchor}"><tspan x="${tick.x}">${this._escape(this._date(tick.timestamp))}</tspan><tspan x="${tick.x}" dy="11">${this._escape(this._time(tick.timestamp))}</tspan></text>`).join("")}
        <line class="chart-border" x1="${chart.left}" y1="${chart.bottom}" x2="${chart.right}" y2="${chart.bottom}"></line>
        <path class="area ${direction}" d="${chart.area}"></path>
        <path class="line ${direction}" d="${chart.line}"></path>
        <circle class="dot ${direction}" cx="${chart.last[0]}" cy="${chart.last[1]}" r="5"></circle>
      </svg>` : `<div class="no-history">${labels.noHistory}</div>`;
    const transactionRows = transactions.map((transaction) => {
      const type = transaction.transaction_type || "buy";
      const currency = transaction.transaction_currency || "";
      const priceText = `${this._compactNumber(Number(transaction.transaction_price) || 0)}${currency ? ` ${currency}` : ""}`;
      const priceLabel = transaction.transaction_price_mode === "total" ? labels.totalAmount : labels.unitPrice;
      const marketPrice = Number(transaction.transaction_market_price) || 0;
      const marketCurrency = transaction.transaction_market_currency || "";
      const marketPriceHtml = marketPrice > 0
        ? `<small>${labels.marketRate}</small><strong>${this._escape(`${this._compactNumber(marketPrice)}${marketCurrency ? ` ${marketCurrency}` : ""}`)}</strong>`
        : "";
      const expenses = (Number(transaction.transaction_fees) || 0) + (Number(transaction.transaction_taxes) || 0);
      return `<div class="transaction-row">
        <span class="transaction-date">${this._escape(transaction.transaction_date || "—")}</span>
        <span class="transaction-type ${type}">${this._escape(labels.transactionTypes[type] || type)}</span>
        <span><small>${labels.quantity}</small><strong>${this._escape(this._compactNumber(Number(transaction.quantity) || 0))}</strong></span>
        <span><small>${priceLabel}</small><strong>${this._escape(priceText)}</strong>${marketPriceHtml}</span>
        <span><small>${labels.fees} + ${labels.taxes}</small><strong>${this._escape(`${this._compactNumber(expenses)}${currency ? ` ${currency}` : ""}`)}</strong></span>
        ${transaction.transaction_note ? `<span class="transaction-note">${this._escape(transaction.transaction_note)}</span>` : ""}
      </div>`;
    }).join("");
    const transactionHtml = configuredAssetType === "index" ? "" : transactions.length ? `
      <section class="transaction-section">
        <div class="transaction-heading"><strong>${labels.transactions}</strong><span>${transactions.length}</span></div>
        <div class="transaction-summary">
          <div><small>${labels.realized}</small><strong class="${Number(entities.holding_realized_gain?.state) < 0 ? "negative" : "positive"}">${this._escape(this._formatState(entities.holding_realized_gain))}</strong></div>
          <div><small>${labels.fees}</small><strong>${this._escape(this._formatState(entities.holding_fees))}</strong></div>
          <div><small>${labels.taxes}</small><strong>${this._escape(this._formatState(entities.holding_taxes))}</strong></div>
        </div>
        <div class="transaction-list">${transactionRows}</div>
      </section>` : `<section class="transaction-section"><div class="transaction-heading"><strong>${labels.transactions}</strong></div><div class="no-transactions">${labels.noTransactions}</div></section>`;

    this.shadowRoot.innerHTML = `
      <style>${this._styles()}</style>
      <ha-card>
        <article>
          <header>
            <div class="identity">
              <div class="mark"><ha-icon icon="${assetIcon}"></ha-icon></div>
              <div class="identity-text">
                <div class="name">${this._escape(name)}</div>
                <div class="symbol">${this._escape(symbol)} · ${this._escape(assetTypeName)}</div>
              </div>
            </div>
            <div class="status ${statusClass}"><span></span>${state}</div>
          </header>
          <section class="hero">
            <div>
              <div class="price">${this._escape(this._formatState(price))}</div>
              <div class="change ${direction}">${this._escape(this._signedState(daily, labels.today))}</div>
            </div>
            <div class="position">
              <div class="muted">${assetType === "index" ? labels.previousClose : labels.position}</div>
              <div class="position-value">${this._escape(this._formatState(assetType === "index" ? entities.holding_previous_close : value))}</div>
              ${assetType === "index" ? "" : `<div class="profit ${Number(gain?.state) < 0 ? "negative" : "positive"}">${this._escape(this._formatState(gain))} · ${this._escape(this._formatState(gainPercent))}</div>`}
            </div>
          </section>
          <section class="chart-section">
            <div class="chart-heading">
              <span>${labels.range} · ${history.length} ${assetType === "crypto" ? labels.days : labels.tradingDays}</span>
              <span>${chart ? `${this._compactNumber(chart.minimum)} – ${this._compactNumber(chart.maximum)} ${price?.attributes?.unit_of_measurement || ""}` : ""}</span>
            </div>
            ${chartHtml}
          </section>
          <section class="metrics">${metricHtml}</section>
          ${transactionHtml}
          <footer>
            <span>${source} · ${this._relativeTime(price?.last_updated)} · v${CARD_VERSION}</span>
            <button type="button" id="details">${labels.details}<ha-icon icon="mdi:chevron-right"></ha-icon></button>
          </footer>
        </article>
      </ha-card>`;
    this.shadowRoot.getElementById("details")?.addEventListener("click", () => this._showDetails());
  }

  _date(value) {
    if (!value) return "";
    const date = new Date(value);
    return new Intl.DateTimeFormat(localeFromHass(this._hass), { day: "2-digit", month: "short" }).format(date);
  }

  _time(value) {
    if (!value) return "";
    return new Intl.DateTimeFormat(
      localeFromHass(this._hass),
      { hour: "2-digit", minute: "2-digit" },
    ).format(new Date(value));
  }

  _relativeTime(value) {
    if (!value) return "";
    const minutes = Math.max(0, Math.round((Date.now() - new Date(value).getTime()) / 60000));
    return LABELS[this._language()].minutesAgo.replace("{minutes}", String(minutes));
  }

  _compactNumber(value) {
    return new Intl.NumberFormat(localeFromHass(this._hass), { maximumFractionDigits: 2 }).format(value);
  }

  _escape(value) {
    const element = document.createElement("span");
    element.textContent = String(value ?? "");
    return element.innerHTML;
  }

  _showDetails() {
    this.dispatchEvent(new CustomEvent("hass-more-info", {
      bubbles: true,
      composed: true,
      detail: { entityId: this._config.entity },
    }));
  }

  _styles() {
    return `
      :host { display: block; }
      ha-card { overflow: hidden; background: var(--ha-card-background, var(--card-background-color)); }
      article { padding: 22px; color: var(--primary-text-color); }
      header, .identity, .hero, .chart-heading, footer, footer button { display: flex; align-items: center; }
      header, .hero, .chart-heading, footer { justify-content: space-between; gap: 14px; }
      header, .hero { flex-wrap: wrap; }
      .identity { gap: 12px; min-width: 0; }
      .identity-text { min-width: 0; }
      .mark { display: grid; place-items: center; width: 44px; height: 44px; flex: 0 0 44px; border-radius: 50%; background: color-mix(in srgb, var(--primary-color) 13%, transparent); color: var(--primary-color); }
      .mark ha-icon { --mdc-icon-size: 24px; }
      .name { font-size: 18px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .symbol, .muted, .chart-heading, footer { color: var(--secondary-text-color); }
      .symbol { margin-top: 3px; font-size: 13px; }
      .status { display: inline-flex; align-items: center; gap: 7px; border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600; }
      .status span { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
      .status.positive { color: var(--success-color, #2eaa65); background: color-mix(in srgb, var(--success-color, #2eaa65) 13%, transparent); }
      .status.neutral { color: var(--secondary-text-color); background: color-mix(in srgb, var(--secondary-text-color) 12%, transparent); }
      .hero { align-items: flex-end; margin-top: 24px; }
      .price { font-size: clamp(32px, 8vw, 46px); line-height: 1; letter-spacing: -0.035em; font-weight: 600; }
      .change, .profit { margin-top: 8px; font-size: 14px; font-weight: 600; }
      .positive { color: var(--success-color, #2eaa65); }
      .negative { color: var(--error-color, #d95c5c); }
      .position { text-align: right; }
      .position-value { margin-top: 4px; font-size: 22px; font-weight: 600; }
      .muted { font-size: 13px; }
      .chart-section { margin-top: 26px; }
      .chart-heading { margin-bottom: 10px; font-size: 12px; }
      svg { display: block; width: 100%; height: auto; overflow: visible; }
      .grid { stroke: var(--divider-color); stroke-width: 1; opacity: .72; }
      .grid.horizontal.major { stroke-width: 1.15; opacity: .86; }
      .grid.horizontal.minor { stroke-width: .7; stroke-dasharray: 2 4; opacity: .58; }
      .grid.vertical.major { stroke-dasharray: 3 5; opacity: .56; }
      .grid.vertical.minor { stroke-dasharray: 1 6; opacity: .34; }
      .chart-border { stroke: var(--secondary-text-color); stroke-width: 1; opacity: .65; }
      .line { fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
      .line.positive, .dot.positive { stroke: var(--success-color, #2eaa65); }
      .line.negative, .dot.negative { stroke: var(--error-color, #d95c5c); }
      .area.positive { fill: color-mix(in srgb, var(--success-color, #2eaa65) 13%, transparent); }
      .area.negative { fill: color-mix(in srgb, var(--error-color, #d95c5c) 13%, transparent); }
      .dot { fill: var(--ha-card-background, var(--card-background-color)); stroke-width: 3; }
      .axis { fill: var(--secondary-text-color); font-size: 10px; font-variant-numeric: tabular-nums; }
      .price-axis { font-size: 9px; }
      .price-axis.minor { opacity: .82; }
      .axis-title { fill: var(--secondary-text-color); font-size: 9px; font-weight: 650; }
      .no-history { display: grid; place-items: center; min-height: 150px; color: var(--secondary-text-color); border-block: 1px solid var(--divider-color); }
      .metrics { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 22px; border-block: 1px solid var(--divider-color); }
      .metric { min-width: 0; padding: 14px 10px 14px 0; }
      .metric:nth-child(n + 4) { border-top: 1px solid var(--divider-color); }
      .metric-label { color: var(--secondary-text-color); font-size: 12px; }
      .metric-value { margin-top: 5px; font-size: 14px; font-weight: 600; overflow-wrap: anywhere; }
      .transaction-section { margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--divider-color); }
      .transaction-heading { display: flex; align-items: center; gap: 8px; font-size: 14px; }
      .transaction-heading span { display: grid; place-items: center; min-width: 20px; height: 20px; border-radius: 10px; color: var(--secondary-text-color); background: color-mix(in srgb, var(--secondary-text-color) 10%, transparent); font-size: 10px; }
      .transaction-summary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 12px; }
      .transaction-summary div { display: grid; gap: 4px; padding: 10px 12px; border: 1px solid var(--divider-color); border-radius: 10px; }
      .transaction-summary small, .transaction-row small { color: var(--secondary-text-color); font-size: 10px; }
      .transaction-summary strong { font-size: 13px; }
      .transaction-list { max-height: 330px; margin-top: 10px; overflow: auto; border: 1px solid var(--divider-color); border-radius: 10px; }
      .transaction-row { display: grid; grid-template-columns: 92px 95px repeat(3, minmax(90px, 1fr)); align-items: center; gap: 10px; min-width: 650px; padding: 10px 12px; font-size: 12px; }
      .transaction-row + .transaction-row { border-top: 1px solid var(--divider-color); }
      .transaction-row > span:not(.transaction-type):not(.transaction-date):not(.transaction-note) { display: grid; gap: 3px; }
      .transaction-date { color: var(--secondary-text-color); font-variant-numeric: tabular-nums; }
      .transaction-type { justify-self: start; padding: 4px 8px; border-radius: 999px; font-size: 10px; font-weight: 700; }
      .transaction-type.buy, .transaction-type.opening { color: var(--success-color, #2eaa65); background: color-mix(in srgb, var(--success-color, #2eaa65) 12%, transparent); }
      .transaction-type.sell { color: var(--error-color, #d95c5c); background: color-mix(in srgb, var(--error-color, #d95c5c) 12%, transparent); }
      .transaction-note { grid-column: 3 / -1; color: var(--secondary-text-color); font-size: 11px; }
      .no-transactions { margin-top: 10px; color: var(--secondary-text-color); font-size: 12px; }
      footer { margin-top: 16px; font-size: 12px; }
      footer button { gap: 2px; border: 0; padding: 6px 0 6px 10px; color: var(--primary-color); background: transparent; font: inherit; font-weight: 600; cursor: pointer; }
      footer button:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
      footer ha-icon { --mdc-icon-size: 18px; }
      .missing { padding: 20px; color: var(--error-color); }
      @media (max-width: 520px) {
        article { padding: 18px; }
        .position { text-align: left; }
        .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .metric:nth-child(n + 3) { border-top: 1px solid var(--divider-color); }
        .transaction-summary { grid-template-columns: 1fr; }
      }
    `;
  }
}

class PortfolioAssetCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  _language() {
    return languageFromHass(this._hass);
  }

  _assetOptions() {
    const assets = new Map();
    for (const [entityId, state] of Object.entries(this._hass?.states || {})) {
      const {
        asset_id: assetId,
        asset_type: assetType,
        metric_key: metricKey,
        symbol,
      } = state.attributes || {};
      if (!assetId) continue;
      const existing = assets.get(assetId);
      if (!existing || metricKey === "holding_price") {
        assets.set(assetId, {
          entityId,
          symbol: symbol || state.attributes.friendly_name || entityId,
          assetType: assetType || "other",
        });
      }
    }
    return [...assets.values()].sort((left, right) =>
      left.symbol.localeCompare(right.symbol),
    );
  }

  _emitConfig(config) {
    this._config = config;
    this.dispatchEvent(new CustomEvent("config-changed", {
      bubbles: true,
      composed: true,
      detail: { config },
    }));
  }

  _escape(value) {
    const element = document.createElement("span");
    element.textContent = String(value ?? "");
    return element.innerHTML;
  }

  _render() {
    if (!this._hass) return;
    const labels = LABELS[this._language()];
    const options = this._assetOptions();
    const optionsHtml = options.map((asset) => `
      <option value="${this._escape(asset.entityId)}" ${asset.entityId === this._config.entity ? "selected" : ""}>
        ${this._escape(asset.symbol)} · ${this._escape(PORTFOLIO_LABELS[this._language()].assetTypes[asset.assetType] || asset.assetType)}
      </option>`).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; width: 100%; }
        .editor { display: grid; gap: 14px; padding: 8px 0; }
        label { display: grid; gap: 6px; color: var(--primary-text-color); font-size: 13px; }
        select, input { box-sizing: border-box; width: 100%; min-height: 44px; border: 1px solid var(--divider-color); border-radius: 10px; padding: 0 12px; color: var(--primary-text-color); background: var(--card-background-color); font: inherit; }
        select:focus, input:focus { border-color: var(--primary-color); outline: 1px solid var(--primary-color); }
        .hint { color: var(--secondary-text-color); font-size: 12px; }
      </style>
      <div class="editor">
        <label>${labels.selectEntity}
          <select id="asset" ${options.length ? "" : "disabled"}>
            ${options.length ? optionsHtml : `<option>${labels.invalidEntity}</option>`}
          </select>
        </label>
        <div class="hint">${labels.selectHint}</div>
        <label>${labels.customName}
          <input id="name" type="text" value="${this._escape(this._config.name || "")}">
        </label>
      </div>`;

    this.shadowRoot.getElementById("asset")?.addEventListener("change", (event) => {
      this._emitConfig({ ...this._config, entity: event.target.value });
    });
    this.shadowRoot.getElementById("name")?.addEventListener("change", (event) => {
      const name = event.target.value.trim();
      const config = { ...this._config };
      if (name) config.name = name;
      else delete config.name;
      this._emitConfig(config);
    });
  }
}

class PortfolioOverviewCard extends HTMLElement {
  static getStubConfig(hass, entities = [], entitiesFallback = []) {
    const candidates = [
      ...entities,
      ...entitiesFallback,
      ...Object.keys(hass?.states || {}),
    ];
    const entity = candidates.find(
      (entityId) => hass?.states?.[entityId]?.attributes?.metric_key === "portfolio_value",
    );
    return { entity: entity || "" };
  }

  static getConfigElement() {
    return document.createElement(PORTFOLIO_EDITOR_TAG);
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._signature = "";
    this._selectedAssetEntity = null;
  }

  setConfig(config) {
    this._config = { ...(config || {}) };
    this._signature = "";
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 5;
  }

  _language() {
    return languageFromHass(this._hass);
  }

  _escape(value) {
    const element = document.createElement("span");
    element.textContent = String(value ?? "");
    return element.innerHTML;
  }

  _format(state, percent = false) {
    if (!state || !Number.isFinite(Number(state.state))) return "—";
    const value = Number(state.state);
    const formatted = new Intl.NumberFormat(localeFromHass(this._hass), {
      maximumFractionDigits: 2,
      minimumFractionDigits: 2,
    }).format(value);
    const unit = percent ? "%" : state.attributes.unit_of_measurement || "";
    return `${formatted}${unit ? ` ${unit}` : ""}`;
  }

  _formatAmount(value, unit) {
    if (!Number.isFinite(value)) return "—";
    const formatted = new Intl.NumberFormat(localeFromHass(this._hass), {
      maximumFractionDigits: 2,
      minimumFractionDigits: 2,
    }).format(value);
    return `${formatted}${unit ? ` ${unit}` : ""}`;
  }

  _formatPercent(value, digits = 1) {
    if (!Number.isFinite(value)) return "—";
    return new Intl.NumberFormat(localeFromHass(this._hass), {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits,
      style: "percent",
    }).format(value / 100);
  }

  _performanceChart(history) {
    if (!Array.isArray(history) || history.length < 2) return null;
    const points = history.filter((point) => Number.isFinite(Number(point.portfolio_percent)));
    if (points.length < 2) return null;
    const values = points.flatMap((point) => [
      Number(point.portfolio_percent),
      point.benchmark_percent !== null && point.benchmark_percent !== undefined && Number.isFinite(Number(point.benchmark_percent))
        ? Number(point.benchmark_percent)
        : null,
    ]).filter((value) => value !== null);
    const minimum = Math.min(0, ...values);
    const maximum = Math.max(0, ...values);
    const span = maximum - minimum || 1;
    const left = 52;
    const right = 706;
    const top = 14;
    const bottom = 164;
    const coordinates = (key) => points
      .map((point, index) => {
        if (point[key] === null || point[key] === undefined) return null;
        const value = Number(point[key]);
        if (!Number.isFinite(value)) return null;
        const x = left + (index / (points.length - 1)) * (right - left);
        const y = bottom - ((value - minimum) / span) * (bottom - top);
        return [x, y];
      })
      .filter(Boolean);
    const path = (coordinatesList) => coordinatesList
      .map(([x, y], index) => `${index ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`)
      .join(" ");
    const zeroY = bottom - ((0 - minimum) / span) * (bottom - top);
    const yTicks = Array.from({ length: 5 }, (_, index) => {
      const value = maximum - (span * index) / 4;
      return {
        y: top + ((bottom - top) * index) / 4,
        label: `${new Intl.NumberFormat(localeFromHass(this._hass), { maximumFractionDigits: 1 }).format(value)} %`,
      };
    });
    const xIndexes = [...new Set([0, Math.floor((points.length - 1) / 2), points.length - 1])];
    const xTicks = xIndexes.map((index) => ({
      x: left + (index / (points.length - 1)) * (right - left),
      label: points[index].date,
      anchor: index === 0 ? "start" : index === points.length - 1 ? "end" : "middle",
    }));
    const dailyGrid = points.map((_point, index) => ({
      x: left + (index / (points.length - 1)) * (right - left),
      major: index % 5 === 0 || index === points.length - 1,
    }));
    return {
      portfolio: path(coordinates("portfolio_percent")),
      benchmark: path(coordinates("benchmark_percent")),
      zeroY,
      start: points[0].date,
      end: points.at(-1).date,
      minimum,
      maximum,
      yTicks,
      xTicks,
      dailyGrid,
      left,
      right,
      top,
      bottom,
    };
  }

  _render() {
    if (!this._hass) return;
    if (!this._config?.entity) {
      const entity = Object.entries(this._hass.states).find(
        ([, state]) => state.attributes?.metric_key === "portfolio_value",
      )?.[0];
      if (!entity) return;
      this._config = { ...(this._config || {}), entity };
    }
    const selected = this._hass.states[this._config.entity];
    if (!selected) return;
    const portfolioId = selected.attributes.portfolio_id;
    if (!portfolioId) return;
    const labels = PORTFOLIO_LABELS[this._language()];
    const metrics = {};
    const assets = new Map();
    for (const [entityId, state] of Object.entries(this._hass.states)) {
      if (state.attributes?.portfolio_id !== portfolioId) continue;
      const metricKey = state.attributes.metric_key;
      if (metricKey?.startsWith("portfolio_")) metrics[metricKey] = state;
      const assetId = state.attributes?.asset_id;
      if (!assetId) continue;
      const asset = assets.get(assetId) || {
        assetId,
        symbol: state.attributes.symbol || state.attributes.friendly_name || entityId,
        assetType: state.attributes.asset_type || "other",
        watchOnly: Boolean(state.attributes.watch_only),
        metrics: {},
      };
      asset.watchOnly = asset.watchOnly || Boolean(state.attributes.watch_only);
      asset.metrics[metricKey] = state;
      if (metricKey === "holding_price") asset.priceEntityId = entityId;
      if (metricKey === "holding_value") asset.entityId = entityId;
      if (asset.assetType === "index" && metricKey === "holding_price") asset.entityId = entityId;
      assets.set(assetId, asset);
    }
    const marketIndexes = [...assets.values()]
      .filter((asset) => asset.assetType === "index" && asset.metrics.holding_price)
      .sort((left, right) => left.symbol.localeCompare(right.symbol));
    const positions = [...assets.values()]
      .filter((asset) => asset.entityId && Number(asset.metrics.holding_value?.state) > 0)
      .map((asset) => ({
        ...asset,
        value: Number(asset.metrics.holding_value.state),
        unit: asset.metrics.holding_value.attributes.unit_of_measurement || "",
        displayValue: Number(asset.metrics.holding_price?.state) * Number(asset.metrics.holding_quantity?.state),
        displayUnit: asset.metrics.holding_price?.attributes?.unit_of_measurement || "",
      }));
    positions.sort((left, right) => right.value - left.value);
    const watchlist = [...assets.values()]
      .filter((asset) => asset.watchOnly && asset.metrics.holding_price)
      .sort((left, right) => left.symbol.localeCompare(right.symbol));
    const total = Number(metrics.portfolio_value?.state) || positions.reduce((sum, item) => sum + item.value, 0);
    const performanceHistory = metrics.portfolio_performance_history?.attributes?.history || [];
    const performanceChart = this._performanceChart(performanceHistory);
    const benchmarkSymbol = metrics.portfolio_performance_history?.attributes?.benchmark_symbol || "";
    const benchmarkLegend = benchmarkSymbol
      ? `<span class="benchmark-dot"></span>${labels.benchmark} ${this._escape(benchmarkSymbol)}`
      : "";
    const signature = JSON.stringify([
      this._config,
      this._selectedAssetEntity,
      Object.values(metrics).map((state) => [state.state, state.last_updated]),
      performanceHistory,
      marketIndexes.map((index) => [
        index.symbol,
        index.metrics.holding_price?.state,
        index.metrics.holding_daily_change?.state,
        index.metrics.holding_price?.last_updated,
      ]),
      positions.map((position) => [
        position.entityId,
        position.value,
        position.displayValue,
        position.displayUnit,
        position.metrics.holding_gain?.state,
        position.metrics.holding_daily_change?.state,
      ]),
      watchlist.map((asset) => [
        asset.priceEntityId,
        asset.metrics.holding_price?.state,
        asset.metrics.holding_daily_change?.state,
        asset.metrics.price_alert_below?.state,
        asset.metrics.price_alert_below?.attributes?.threshold,
        asset.metrics.price_alert_above?.state,
        asset.metrics.price_alert_above?.attributes?.threshold,
      ]),
    ]);
    if (signature === this._signature) return;
    this._signature = signature;

    const deviceId = this._hass.entities?.[this._config.entity]?.device_id;
    const device = deviceId ? this._hass.devices?.[deviceId] : null;
    const title = this._config.name || device?.name_by_user || device?.name || labels.title;
    const gainValue = Number(metrics.portfolio_gain?.state);
    const dailyValue = Number(metrics.portfolio_daily_change?.state);
    const colors = ["#5b8def", "#35b779", "#f4a340", "#a56de2", "#e56767", "#38a7b8"];
    const groupOrder = ["stock", "crypto", "etf", "fund", "currency", "other"];
    const currencyGroups = new Map();
    for (const position of positions) {
      if (!position.displayUnit || !Number.isFinite(position.displayValue)) continue;
      const group = currencyGroups.get(position.displayUnit) || {
        displayValue: 0,
        baseValue: 0,
        baseUnit: position.unit,
      };
      group.displayValue += position.displayValue;
      group.baseValue += position.value;
      currencyGroups.set(position.displayUnit, group);
    }
    const currencySummary = [...currencyGroups.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([currency, group]) => `<div class="currency-item"><span>${this._escape(currency)}</span><strong>${this._escape(this._formatAmount(group.displayValue, currency))}</strong>${currency !== group.baseUnit ? `<small>≈ ${this._escape(this._formatAmount(group.baseValue, group.baseUnit))}</small>` : ""}</div>`)
      .join("");
    const hasForeignCurrencies = positions.some(
      (position) => position.displayUnit && position.displayUnit !== position.unit,
    );
    let offset = 0;
    const stops = positions.map((position, index) => {
      const start = offset;
      offset += total > 0 ? (position.value / total) * 100 : 0;
      return `${colors[index % colors.length]} ${start.toFixed(2)}% ${offset.toFixed(2)}%`;
    }).join(", ");
    const legend = groupOrder.map((group) => {
      const groupPositions = positions
        .map((position, index) => ({ position, index }))
        .filter(({ position }) => {
          const normalizedType = groupOrder.includes(position.assetType)
            ? position.assetType
            : "other";
          return normalizedType === group;
        });
      if (!groupPositions.length) return "";
      const rows = groupPositions.map(({ position, index }) => {
        const share = total > 0 ? (position.value / total) * 100 : 0;
        return `<button class="allocation-row" data-entity="${this._escape(position.entityId)}">
          <span class="color" style="background:${colors[index % colors.length]}"></span>
          <span class="allocation-name">${this._escape(position.symbol)}</span>
          <strong>${this._escape(this._formatPercent(share))}</strong>
        </button>`;
      }).join("");
      return `<section class="legend-group"><div class="legend-group-title"><span>${this._escape(labels.assetGroups[group])}</span><small>${groupPositions.length}</small></div>${rows}</section>`;
    }).join("");
    const renderTableRow = (position) => {
      const share = total > 0 ? (position.value / total) * 100 : 0;
      const gain = Number(position.metrics.holding_gain?.state);
      const daily = Number(position.metrics.holding_daily_change?.state);
      const selectedClass = position.entityId === this._selectedAssetEntity ? " selected" : "";
      const hasSeparateCurrency = position.displayUnit && position.displayUnit !== position.unit;
      const displayedValue = Number.isFinite(position.displayValue)
        ? this._formatAmount(position.displayValue, position.displayUnit)
        : this._format(position.metrics.holding_value);
      return `<button class="position-row${selectedClass}" data-entity="${this._escape(position.entityId)}">
        <span class="position-main"><strong>${this._escape(position.symbol)}</strong><small>${this._escape(labels.assetTypes[position.assetType] || position.assetType)}</small></span>
        <span class="position-value-cell"><strong>${this._escape(displayedValue)}</strong>${hasSeparateCurrency ? `<small>≈ ${this._escape(this._format(position.metrics.holding_value))}</small>` : ""}</span>
        <span>${this._escape(this._formatPercent(share))}</span>
        <span class="${gain < 0 ? "negative" : "positive"}">${this._escape(this._format(position.metrics.holding_gain))}</span>
        <span class="${daily < 0 ? "negative" : "positive"}">${this._escape(this._format(position.metrics.holding_daily_change, true))}</span>
        <ha-icon icon="mdi:chevron-${position.entityId === this._selectedAssetEntity ? "up" : "down"}"></ha-icon>
      </button>`;
    };
    const tableRows = groupOrder.map((group) => {
      const groupPositions = positions.filter((position) => {
        const normalizedType = groupOrder.includes(position.assetType)
          ? position.assetType
          : "other";
        return normalizedType === group;
      });
      if (!groupPositions.length) return "";
      return `<section class="asset-group"><div class="asset-group-title"><span>${this._escape(labels.assetGroups[group])}</span><small>${groupPositions.length}</small></div>${groupPositions.map(renderTableRow).join("")}</section>`;
    }).join("");
    const allocationContent = positions.length
      ? `<div class="allocation-content"><div class="donut"></div><div class="allocation-list">${legend}</div></div>`
      : `<div class="empty">${labels.noAssets}</div>`;
    const tableContent = positions.length
      ? `<div class="position-table"><div class="table-head"><span>${labels.asset}</span><span>${labels.value}</span><span>${labels.share}</span><span>${labels.gain}</span><span>${labels.daily}</span><span></span></div>${tableRows}</div><div id="asset-detail"></div>`
      : `<div class="empty">${labels.noAssets}</div>`;
    const watchlistRows = watchlist.map((asset) => {
      const daily = Number(asset.metrics.holding_daily_change?.state);
      const below = asset.metrics.price_alert_below;
      const above = asset.metrics.price_alert_above;
      const alarmActive = below?.state === "on" || above?.state === "on";
      const selectedClass = asset.priceEntityId === this._selectedAssetEntity ? " selected" : "";
      const unit = asset.metrics.holding_price?.attributes?.unit_of_measurement || "";
      const threshold = (state) => state
        ? this._formatAmount(Number(state.attributes.threshold), state.attributes.currency || unit)
        : "—";
      return `<button class="watchlist-row${selectedClass}" data-entity="${this._escape(asset.priceEntityId)}">
        <span class="position-main"><strong>${this._escape(asset.symbol)}</strong><small>${this._escape(labels.assetTypes[asset.assetType] || asset.assetType)}</small></span>
        <strong>${this._escape(this._format(asset.metrics.holding_price))}</strong>
        <span class="${daily < 0 ? "negative" : "positive"}">${this._escape(this._format(asset.metrics.holding_daily_change, true))}</span>
        <span>${this._escape(threshold(below))}</span>
        <span>${this._escape(threshold(above))}</span>
        <span class="watch-status ${alarmActive ? "alarm" : ""}"><ha-icon icon="mdi:${alarmActive ? "bell-alert" : "eye-outline"}"></ha-icon>${alarmActive ? labels.alarmActive : labels.monitoring}</span>
      </button>`;
    }).join("");
    const watchlistContent = watchlist.length ? `
      <section class="watchlist-section">
        <div class="section-title">${labels.watchlist}</div>
        <div class="watchlist-table">
          <div class="watchlist-head"><span>${labels.asset}</span><span>${labels.watchPrice}</span><span>${labels.daily}</span><span>${labels.alertBelow}</span><span>${labels.alertAbove}</span><span>${labels.alarmStatus}</span></div>
          ${watchlistRows}
        </div>
        <div id="watchlist-detail"></div>
      </section>` : "";
    const indexContent = marketIndexes.map((index) => {
      const change = Number(index.metrics.holding_daily_change?.state);
      const shortName = index.symbol.replace("^", "").replace("SSMI", "SMI").replace("GDAXI", "DAX").replace("GSPC", "S&P 500").replace("DJI", "Dow Jones").replace("IXIC", "NASDAQ").replace("STOXX50E", "EURO STOXX 50");
      return `<button class="index-tile" data-entity="${this._escape(index.entityId)}">
        <span>${this._escape(shortName)}</span>
        <strong>${this._escape(this._format(index.metrics.holding_price))}</strong>
        <small class="${change < 0 ? "negative" : "positive"}">${change >= 0 ? "▲" : "▼"} ${this._escape(this._format(index.metrics.holding_daily_change, true))}</small>
      </button>`;
    }).join("");
    const performanceContent = performanceChart ? `
      <section class="performance-section">
        <div class="performance-header">
          <div><div class="section-title">${labels.professionalPerformance}</div><div class="performance-legend"><span class="portfolio-dot"></span>${labels.portfolioLine}${benchmarkLegend}</div></div>
          <div class="performance-period">${this._escape(performanceChart.start)} – ${this._escape(performanceChart.end)}</div>
        </div>
        <div class="performance-kpis">
          <div><small>${labels.netInvested}</small><strong>${this._escape(this._format(metrics.portfolio_net_invested))}</strong></div>
          <div><small>${labels.totalResult}</small><strong class="${Number(metrics.portfolio_total_gain?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_total_gain))}</strong></div>
          <div><small>${labels.totalReturn}</small><strong class="${Number(metrics.portfolio_total_return?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_total_return, true))}</strong></div>
          <div><small>${labels.timeWeighted}</small><strong class="${Number(metrics.portfolio_time_weighted_return?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_time_weighted_return, true))}</strong></div>
          ${benchmarkSymbol ? `<div><small>${labels.benchmark}</small><strong class="${Number(metrics.portfolio_benchmark_return?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_benchmark_return, true))}</strong></div><div><small>${labels.excessReturn}</small><strong class="${Number(metrics.portfolio_excess_return?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_excess_return, true))}</strong></div>` : ""}
        </div>
        <svg class="performance-chart" viewBox="0 0 720 205" role="img" aria-label="${labels.professionalPerformance}">
          ${performanceChart.dailyGrid.map((tick) => `<line class="performance-day-grid ${tick.major ? "major" : "minor"}" x1="${tick.x}" y1="${performanceChart.top}" x2="${tick.x}" y2="${performanceChart.bottom}"></line>`).join("")}
          ${performanceChart.yTicks.map((tick) => `<line class="performance-grid" x1="${performanceChart.left}" y1="${tick.y}" x2="${performanceChart.right}" y2="${tick.y}"></line><text class="performance-axis performance-y-axis" x="46" y="${tick.y + 3}" text-anchor="end">${this._escape(tick.label)}</text>`).join("")}
          <line class="performance-zero" x1="${performanceChart.left}" y1="${performanceChart.zeroY}" x2="${performanceChart.right}" y2="${performanceChart.zeroY}"></line>
          <path class="performance-portfolio" d="${performanceChart.portfolio}"></path>
          <path class="performance-benchmark" d="${performanceChart.benchmark}"></path>
          ${performanceChart.xTicks.map((tick) => `<text class="performance-axis" x="${tick.x}" y="195" text-anchor="${tick.anchor}">${this._escape(tick.label)}</text>`).join("")}
        </svg>
        <div class="cashflow-row"><span>${labels.purchases}: <strong>${this._escape(this._format(metrics.portfolio_purchases))}</strong></span><span>${labels.sales}: <strong>${this._escape(this._format(metrics.portfolio_sales))}</strong></span></div>
      </section>` : `<section class="performance-section"><div class="section-title">${labels.professionalPerformance}</div><div class="empty">${labels.noPerformance}</div></section>`;
    const viewMode = this._config.view_mode === "table" ? "table" : "overview";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; }
        ha-card { overflow:hidden; background:var(--ha-card-background,var(--card-background-color)); }
        article { padding:22px; color:var(--primary-text-color); }
        header,.portfolio-title,.headline,.summary,.allocation-content,.allocation-row { display:flex; align-items:center; }
        header,.headline { justify-content:space-between; gap:16px; }
        .portfolio-title { gap:12px; min-width:0; }
        .portfolio-settings { display:flex; align-items:center; flex:0 0 auto; gap:7px; min-height:36px; border:1px solid var(--divider-color); border-radius:8px; padding:0 11px; color:var(--primary-text-color); background:color-mix(in srgb,var(--secondary-text-color) 5%,transparent); font-size:12px; font-weight:600; text-decoration:none; }
        .portfolio-settings:hover { color:var(--primary-color); background:color-mix(in srgb,var(--primary-color) 9%,transparent); }
        .portfolio-settings ha-icon { --mdc-icon-size:18px; }
        h2 { margin:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:19px; }
        .subtitle,.label,.allocation-type,footer { color:var(--secondary-text-color); }
        .subtitle { margin-top:3px; font-size:12px; }
        .index-section { margin-top:18px; }
        .index-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:8px; }
        .index-tile { display:grid; gap:4px; min-width:0; border:1px solid var(--divider-color); border-radius:11px; padding:10px 12px; color:var(--primary-text-color); background:color-mix(in srgb,var(--secondary-text-color) 4%,transparent); font:inherit; text-align:left; cursor:pointer; }
        .index-tile:hover { background:color-mix(in srgb,var(--primary-color) 8%,transparent); }
        .index-tile span { overflow:hidden; color:var(--secondary-text-color); font-size:10px; font-weight:700; text-overflow:ellipsis; white-space:nowrap; }
        .index-tile strong { font-size:15px; font-variant-numeric:tabular-nums; }
        .index-tile small { font-size:11px; font-weight:650; }
        .top-overview { display:grid; grid-template-columns:minmax(430px,1.35fr) minmax(250px,.65fr); align-items:start; gap:28px; margin-top:22px; }
        .top-allocation { min-width:0; }
        .headline { align-items:flex-start; min-width:0; margin:0; padding:8px 0 8px 26px; border-left:1px solid var(--divider-color); }
        .value { margin-top:4px; font-size:clamp(34px,8vw,48px); line-height:1; letter-spacing:-.04em; font-weight:650; }
        .daily { margin-top:9px; font-size:14px; font-weight:600; }
        .conversion-note { margin-top:6px; color:var(--secondary-text-color); font-size:11px; }
        .positive { color:var(--success-color,#2eaa65); }
        .negative { color:var(--error-color,#d95c5c); }
        .summary { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); margin-top:24px; border-block:1px solid var(--divider-color); }
        .summary-item { padding:14px 10px 14px 0; }
        .label { font-size:12px; }
        .summary-value { margin-top:5px; font-size:15px; font-weight:600; }
        .performance-section { margin-top:24px; padding:18px; border:1px solid var(--divider-color); border-radius:14px; background:color-mix(in srgb,var(--secondary-text-color) 3%,transparent); }
        .performance-header { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }
        .performance-header .section-title { margin-bottom:7px; }
        .performance-legend { display:flex; align-items:center; gap:7px; color:var(--secondary-text-color); font-size:10px; }
        .portfolio-dot,.benchmark-dot { width:16px; height:3px; border-radius:2px; }
        .portfolio-dot { background:var(--primary-color); }
        .benchmark-dot { margin-left:8px; background:var(--warning-color,#e3a73f); }
        .performance-period { color:var(--secondary-text-color); font-size:10px; }
        .performance-kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:1px; margin:14px 0; overflow:hidden; border:1px solid var(--divider-color); border-radius:10px; background:var(--divider-color); }
        .performance-kpis div { display:grid; gap:4px; padding:9px 10px; background:var(--ha-card-background,var(--card-background-color)); }
        .performance-kpis small { color:var(--secondary-text-color); font-size:9px; }
        .performance-kpis strong { font-size:12px; font-variant-numeric:tabular-nums; }
        .performance-chart { display:block; width:100%; height:auto; overflow:visible; }
        .performance-zero { stroke:var(--divider-color); stroke-width:1; stroke-dasharray:4 4; }
        .performance-grid { stroke:var(--divider-color); stroke-width:.7; opacity:.55; }
        .performance-day-grid { stroke:var(--divider-color); }
        .performance-day-grid.minor { stroke-width:.55; stroke-dasharray:2 5; opacity:.34; }
        .performance-day-grid.major { stroke-width:.9; opacity:.62; }
        .performance-portfolio,.performance-benchmark { fill:none; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
        .performance-portfolio { stroke:var(--primary-color); }
        .performance-benchmark { stroke:var(--warning-color,#e3a73f); stroke-width:2; }
        .performance-axis { fill:var(--secondary-text-color); font-size:9px; }
        .cashflow-row { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:16px; color:var(--secondary-text-color); font-size:10px; }
        .cashflow-row strong { color:var(--primary-text-color); }
        .currency-summary { margin-top:18px; }
        .currency-list { display:flex; flex-wrap:wrap; gap:8px; }
        .currency-item { display:grid; gap:3px; min-width:120px; padding:9px 12px; border:1px solid var(--divider-color); border-radius:10px; background:color-mix(in srgb,var(--secondary-text-color) 4%,transparent); }
        .currency-item span { color:var(--secondary-text-color); font-size:10px; font-weight:650; }
        .currency-item strong { font-size:13px; font-variant-numeric:tabular-nums; }
        .currency-item small { color:var(--secondary-text-color); font-size:10px; font-variant-numeric:tabular-nums; }
        .allocation { margin-top:22px; }
        .section-title { margin-bottom:14px; font-size:13px; font-weight:650; }
        .allocation-content { display:grid; grid-template-columns:132px minmax(0,1fr); align-items:start; gap:24px; }
        .donut { position:relative; width:132px; height:132px; flex:0 0 132px; border-radius:50%; background:${stops ? `conic-gradient(${stops})` : "var(--divider-color)"}; }
        .donut::after { content:""; position:absolute; inset:25px; border-radius:50%; background:var(--ha-card-background,var(--card-background-color)); }
        .allocation-list { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); align-content:start; width:100%; min-width:0; gap:12px 18px; }
        .legend-group { min-width:0; padding:7px 10px; border:1px solid var(--divider-color); border-radius:10px; background:color-mix(in srgb,var(--secondary-text-color) 3%,transparent); }
        .legend-group-title { display:flex; align-items:center; gap:7px; margin-bottom:2px; color:var(--secondary-text-color); font-size:10px; font-weight:700; letter-spacing:.03em; }
        .legend-group-title small { display:grid; place-items:center; min-width:17px; height:17px; border-radius:9px; background:color-mix(in srgb,var(--secondary-text-color) 10%,transparent); font-size:9px; }
        .allocation-row { width:100%; gap:8px; border:0; padding:6px 0; color:var(--primary-text-color); background:transparent; font:inherit; text-align:left; cursor:pointer; }
        .color { width:9px; height:9px; flex:0 0 9px; border-radius:50%; }
        .allocation-name { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:13px; }
        .allocation-name { margin-right:auto; }
        .allocation-row strong { min-width:45px; text-align:right; font-size:12px; }
        .position-table { overflow-x:auto; border:1px solid var(--divider-color); border-radius:12px; }
        .table-head,.position-row { display:grid; grid-template-columns:minmax(150px,1fr) max-content 72px max-content max-content 24px; align-items:center; min-width:650px; column-gap:clamp(8px,1.2vw,18px); padding:10px 14px; }
        .table-head { color:var(--secondary-text-color); background:color-mix(in srgb,var(--secondary-text-color) 6%,transparent); font-size:11px; font-weight:600; text-align:center; }
        .table-head > span:first-child { text-align:left; }
        .asset-group + .asset-group { border-top:1px solid var(--divider-color); }
        .asset-group-title { display:flex; align-items:center; gap:8px; min-width:650px; padding:8px 14px; color:var(--primary-text-color); background:color-mix(in srgb,var(--primary-color) 7%,transparent); font-size:11px; font-weight:700; letter-spacing:.02em; }
        .asset-group-title small { display:grid; place-items:center; min-width:19px; height:19px; border-radius:10px; color:var(--secondary-text-color); background:color-mix(in srgb,var(--secondary-text-color) 10%,transparent); font-size:10px; }
        .position-row { width:100%; border:0; border-top:1px solid var(--divider-color); color:var(--primary-text-color); background:transparent; font:inherit; font-size:12px; text-align:center; cursor:pointer; }
        .position-row > span:not(.position-main) { justify-self:stretch; text-align:center; white-space:nowrap; font-variant-numeric:tabular-nums; }
        .position-row:hover,.position-row.selected { background:color-mix(in srgb,var(--primary-color) 8%,transparent); }
        .position-main { display:grid; min-width:0; text-align:left; }
        .position-main strong { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:13px; }
        .position-main small { margin-top:2px; color:var(--secondary-text-color); text-transform:capitalize; }
        .position-value-cell { display:grid; gap:2px; font-weight:600; }
        .position-value-cell small { color:var(--secondary-text-color); font-size:10px; font-weight:400; }
        .position-row ha-icon { --mdc-icon-size:18px; justify-self:center; color:var(--secondary-text-color); }
        .watchlist-section { margin-top:24px; }
        .watchlist-table { overflow-x:auto; border:1px solid var(--divider-color); border-radius:12px; }
        .watchlist-head,.watchlist-row { display:grid; grid-template-columns:minmax(140px,1fr) repeat(4,minmax(88px,max-content)) minmax(145px,max-content); align-items:center; min-width:760px; column-gap:14px; padding:10px 14px; }
        .watchlist-head { color:var(--secondary-text-color); background:color-mix(in srgb,var(--secondary-text-color) 6%,transparent); font-size:11px; font-weight:600; text-align:center; }
        .watchlist-head > span:first-child { text-align:left; }
        .watchlist-row { width:100%; border:0; border-top:1px solid var(--divider-color); color:var(--primary-text-color); background:transparent; font:inherit; font-size:12px; text-align:center; cursor:pointer; }
        .watchlist-row:hover,.watchlist-row.selected { background:color-mix(in srgb,var(--primary-color) 8%,transparent); }
        .watchlist-row > span:not(.position-main),.watchlist-row > strong { white-space:nowrap; font-variant-numeric:tabular-nums; }
        .watch-status { display:flex; align-items:center; justify-content:flex-start; gap:6px; color:var(--success-color,#2eaa65); font-size:11px; font-weight:600; }
        .watch-status.alarm { color:var(--error-color,#d95c5c); }
        .watch-status ha-icon { --mdc-icon-size:17px; }
        #asset-detail { margin-top:18px; }
        .detail-toolbar { display:flex; justify-content:flex-end; margin-bottom:8px; }
        .detail-toolbar button { display:flex; align-items:center; gap:5px; border:0; padding:7px 10px; border-radius:8px; color:var(--primary-color); background:color-mix(in srgb,var(--primary-color) 9%,transparent); font:inherit; font-size:12px; cursor:pointer; }
        .detail-toolbar ha-icon { --mdc-icon-size:17px; }
        .empty { color:var(--secondary-text-color); font-size:13px; }
        footer { margin-top:16px; font-size:11px; }
        @media(max-width:850px){.top-overview{grid-template-columns:1fr}.headline{padding:18px 0 0;border-top:1px solid var(--divider-color);border-left:0}.performance-kpis{grid-template-columns:repeat(3,minmax(0,1fr))}}
        @media(max-width:520px){ article{padding:18px}.portfolio-settings{width:36px;padding:0;justify-content:center}.portfolio-settings span{display:none}.headline{align-items:flex-start;flex-direction:column}.summary{grid-template-columns:1fr}.summary-item+ .summary-item{border-top:1px solid var(--divider-color)}.allocation-content{grid-template-columns:1fr}.donut{width:118px;height:118px;justify-self:start}.allocation-list{grid-template-columns:1fr;width:100%}.allocation{margin-inline:-6px}.section-title{margin-inline:6px}.performance-section{padding:13px}.performance-header{display:grid}.performance-kpis{grid-template-columns:repeat(2,minmax(0,1fr))} }
      </style>
      <ha-card><article>
        <header>
          <div class="portfolio-title"><div><h2>${this._escape(title)}</h2><div class="subtitle">${positions.length} ${labels.positions}</div></div></div>
          <a class="portfolio-settings" href="/config/integrations/integration/portfolio_tracker#config_entry=${encodeURIComponent(portfolioId)}" title="${this._escape(labels.managePortfolio)}" aria-label="${this._escape(labels.managePortfolio)}"><ha-icon icon="mdi:cog-outline"></ha-icon><span>${this._escape(labels.managePortfolio)}</span></a>
        </header>
        ${indexContent ? `<section class="index-section"><div class="section-title">${labels.marketIndices}</div><div class="index-grid">${indexContent}</div></section>` : ""}
        <section class="top-overview">
          <div class="top-allocation"><div class="section-title">${labels.allocation}</div>${allocationContent}</div>
          <section class="headline"><div><div class="label">${labels.totalValue}</div><div class="value">${this._escape(this._format(metrics.portfolio_value))}</div><div class="daily ${dailyValue < 0 ? "negative" : "positive"}">${dailyValue >= 0 ? "▲" : "▼"} ${this._escape(this._format(metrics.portfolio_daily_change, true))} · ${labels.daily}</div>${hasForeignCurrencies ? `<div class="conversion-note">${labels.fxConverted}</div>` : ""}</div></section>
        </section>
        <section class="summary">
          <div class="summary-item"><div class="label">${labels.cost}</div><div class="summary-value">${this._escape(this._format(metrics.portfolio_cost))}</div></div>
          <div class="summary-item"><div class="label">${labels.gain}</div><div class="summary-value ${gainValue < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_gain))}</div></div>
          <div class="summary-item"><div class="label">${labels.return}</div><div class="summary-value ${Number(metrics.portfolio_gain_percent?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_gain_percent, true))}</div></div>
          <div class="summary-item"><div class="label">${labels.realized}</div><div class="summary-value ${Number(metrics.portfolio_realized_gain?.state) < 0 ? "negative" : "positive"}">${this._escape(this._format(metrics.portfolio_realized_gain))}</div></div>
          <div class="summary-item"><div class="label">${labels.fees}</div><div class="summary-value">${this._escape(this._format(metrics.portfolio_fees))}</div></div>
          <div class="summary-item"><div class="label">${labels.taxes}</div><div class="summary-value">${this._escape(this._format(metrics.portfolio_taxes))}</div></div>
        </section>
        ${performanceContent}
        ${currencySummary ? `<section class="currency-summary"><div class="section-title">${labels.currencies}</div><div class="currency-list">${currencySummary}</div></section>` : ""}
        ${viewMode === "table" ? `<section class="allocation"><div class="section-title">${labels.activeAssets}</div>${tableContent}</section>` : ""}
        ${watchlistContent}
        <footer>${labels.updated}: ${new Intl.DateTimeFormat(localeFromHass(this._hass), { hour:"2-digit", minute:"2-digit" }).format(new Date(metrics.portfolio_value?.last_updated || Date.now()))} · Portfolio Card v${CARD_VERSION}</footer>
      </article></ha-card>`;
    this.shadowRoot.querySelectorAll(".allocation-row").forEach((row) => {
      row.addEventListener("click", () => this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles:true, composed:true, detail:{ entityId:row.dataset.entity } })));
    });
    this.shadowRoot.querySelectorAll(".index-tile").forEach((tile) => {
      tile.addEventListener("click", () => this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles:true, composed:true, detail:{ entityId:tile.dataset.entity } })));
    });
    this.shadowRoot.querySelectorAll(".position-row").forEach((row) => {
      row.addEventListener("click", () => {
        this._selectedAssetEntity = this._selectedAssetEntity === row.dataset.entity
          ? null
          : row.dataset.entity;
        this._signature = "";
        this._render();
      });
    });
    this.shadowRoot.querySelectorAll(".watchlist-row").forEach((row) => {
      row.addEventListener("click", () => {
        this._selectedAssetEntity = this._selectedAssetEntity === row.dataset.entity
          ? null
          : row.dataset.entity;
        this._signature = "";
        this._render();
      });
    });
    const selectedWatchAsset = watchlist.find(
      (asset) => asset.priceEntityId === this._selectedAssetEntity,
    );
    if (selectedWatchAsset) {
      const detailHost = this.shadowRoot.getElementById("watchlist-detail");
      const toolbar = document.createElement("div");
      toolbar.className = "detail-toolbar";
      toolbar.innerHTML = `<button type="button"><ha-icon icon="mdi:close"></ha-icon>${labels.closeDetails}</button>`;
      toolbar.querySelector("button").addEventListener("click", () => {
        this._selectedAssetEntity = null;
        this._signature = "";
        this._render();
      });
      const detailCard = document.createElement(CARD_TAG);
      detailCard.setConfig({ entity: selectedWatchAsset.priceEntityId });
      detailCard.hass = this._hass;
      detailHost?.append(toolbar, detailCard);
    }
    if (viewMode === "table" && this._selectedAssetEntity) {
      const detailHost = this.shadowRoot.getElementById("asset-detail");
      const toolbar = document.createElement("div");
      toolbar.className = "detail-toolbar";
      toolbar.innerHTML = `<button type="button"><ha-icon icon="mdi:close"></ha-icon>${labels.closeDetails}</button>`;
      toolbar.querySelector("button").addEventListener("click", () => {
        this._selectedAssetEntity = null;
        this._signature = "";
        this._render();
      });
      const detailCard = document.createElement(CARD_TAG);
      detailCard.setConfig({ entity: this._selectedAssetEntity });
      detailCard.hass = this._hass;
      detailHost?.append(toolbar, detailCard);
    }
  }
}

class PortfolioOverviewCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
  }
  set hass(hass) { this._hass = hass; this._render(); }
  setConfig(config) { this._config = { ...config }; this._render(); }
  _escape(value) {
    const element = document.createElement("span");
    element.textContent = String(value ?? "");
    return element.innerHTML;
  }
  _render() {
    if (!this._hass) return;
    const language = languageFromHass(this._hass);
    const labels = PORTFOLIO_LABELS[language];
    const portfolios = Object.entries(this._hass.states)
      .filter(([, state]) => state.attributes?.metric_key === "portfolio_value")
      .map(([entityId, state]) => ({ entityId, name:state.attributes.friendly_name || labels.title }));
    this.shadowRoot.innerHTML = `<style>:host{display:block;width:100%}.editor{display:grid;gap:14px}label{display:grid;gap:7px;color:var(--primary-text-color);font-size:13px}select{box-sizing:border-box;width:100%;min-height:44px;border:1px solid var(--divider-color);border-radius:10px;padding:0 12px;color:var(--primary-text-color);background:var(--card-background-color);font:inherit}</style><div class="editor"><label>${labels.portfolio}<select id="portfolio">${portfolios.map((portfolio) => `<option value="${this._escape(portfolio.entityId)}" ${portfolio.entityId === this._config.entity ? "selected" : ""}>${this._escape(portfolio.name)}</option>`).join("")}</select></label><label>${labels.view}<select id="view"><option value="overview" ${this._config.view_mode !== "table" ? "selected" : ""}>${labels.overviewView}</option><option value="table" ${this._config.view_mode === "table" ? "selected" : ""}>${labels.tableView}</option></select></label></div>`;
    this.shadowRoot.getElementById("portfolio")?.addEventListener("change", (event) => {
      this._config = { ...this._config, entity:event.target.value };
      this.dispatchEvent(new CustomEvent("config-changed", { bubbles:true, composed:true, detail:{ config:this._config } }));
    });
    this.shadowRoot.getElementById("view")?.addEventListener("change", (event) => {
      this._config = { ...this._config, view_mode:event.target.value };
      this.dispatchEvent(new CustomEvent("config-changed", { bubbles:true, composed:true, detail:{ config:this._config } }));
    });
  }
}

if (!customElements.get(CARD_TAG)) customElements.define(CARD_TAG, PortfolioAssetCard);
if (!customElements.get(EDITOR_TAG)) customElements.define(EDITOR_TAG, PortfolioAssetCardEditor);
if (!customElements.get(PORTFOLIO_CARD_TAG)) customElements.define(PORTFOLIO_CARD_TAG, PortfolioOverviewCard);
if (!customElements.get(PORTFOLIO_EDITOR_TAG)) customElements.define(PORTFOLIO_EDITOR_TAG, PortfolioOverviewCardEditor);

window.PORTFOLIO_ASSET_CARD_VERSION = CARD_VERSION;

window.customCards = window.customCards || [];
const catalogLabels = CARD_CATALOG_LABELS[
  normalizeLanguage(globalThis.navigator?.language)
];
if (!window.customCards.some((card) => card.type === CARD_TAG)) {
  window.customCards.push({
    type: CARD_TAG,
    name: catalogLabels.assetName,
    description: catalogLabels.assetDescription,
    preview: false,
    getEntitySuggestion: (hass, entityId) => {
      if (!hass?.states?.[entityId]?.attributes?.asset_id) return null;
      return {
        config: { type: `custom:${CARD_TAG}`, entity: entityId },
      };
    },
    documentationURL: "https://github.com/DjangoToni/home-assistant-portfolio-tracker#readme",
  });
}
if (!window.customCards.some((card) => card.type === PORTFOLIO_CARD_TAG)) {
  window.customCards.push({
    type: PORTFOLIO_CARD_TAG,
    name: catalogLabels.overviewName,
    description: catalogLabels.overviewDescription,
    preview: false,
    getEntitySuggestion: (hass, entityId) => {
      if (hass?.states?.[entityId]?.attributes?.metric_key !== "portfolio_value") return null;
      return {
        config: { type: `custom:${PORTFOLIO_CARD_TAG}`, entity: entityId },
      };
    },
    documentationURL: "https://github.com/DjangoToni/home-assistant-portfolio-tracker#readme",
  });
}

console.info(`%c PORTFOLIO TRACKER %c Dashboard Cards v${CARD_VERSION} `, "color:#fff;background:#3b6ee8;font-weight:600", "color:#3b6ee8;background:#eef3ff");
