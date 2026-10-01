// Prices are shown the same way across the shop, e.g. "4.20 €".
export const formatEuro = (value) => `${Number(value || 0).toFixed(2)} €`
