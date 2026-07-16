const BASE_URL = import.meta.env.VITE_API_URL || "";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${BASE_URL}/api/upload`, {
      method: "POST",
      body: formData,
    }).then(handle);
  },

  getTransactions: (flaggedOnly = false) =>
    fetch(`${BASE_URL}/api/transactions?flagged_only=${flaggedOnly}`).then(handle),

  getSummary: () => fetch(`${BASE_URL}/api/summary`).then(handle),

  deleteTransaction: (id) =>
    fetch(`${BASE_URL}/api/transactions/${id}`, { method: "DELETE" }).then(handle),
};
