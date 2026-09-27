/**
 * API client. Same-origin fetches with cookie auth, JSON handling and
 * friendly errors (including an offline message, which matters on phones).
 */

export class ApiError extends Error {
  constructor(status, message, details) {
    super(message);
    this.status = status;
    this.details = details;
    this.offline = status === 0;
  }
}

let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn; };

async function request(method, path, body, opts = {}) {
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: body === undefined ? {} : { 'content-type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: 'same-origin',
      cache: 'no-store',
    });
  } catch {
    throw new ApiError(0, 'No connection to the server. Check your internet and try again.');
  }

  if (res.status === 401 && !opts.allow401) {
    onUnauthorized();
    throw new ApiError(401, 'Your session has ended — please sign in again.');
  }

  const text = await res.text();
  let data = null;
  if (text) {
    try { data = JSON.parse(text); }
    catch { data = { error: text.slice(0, 200) }; }
  }
  if (!res.ok) {
    throw new ApiError(res.status, data?.error || `Request failed (${res.status})`, data?.details);
  }
  return data;
}

const qs = (params = {}) => {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue;
    usp.set(k, String(v));
  }
  const s = usp.toString();
  return s ? `?${s}` : '';
};

export const api = {
  get: (path, params, opts) => request('GET', path + qs(params), undefined, opts),
  post: (path, body, opts) => request('POST', path, body ?? {}, opts),
  put: (path, body, opts) => request('PUT', path, body ?? {}, opts),
  del: (path, opts) => request('DELETE', path, undefined, opts),

  /* --- auth --- */
  login: (phone, password) => request('POST', '/api/login', { phone, password }, { allow401: true }),
  logout: () => request('POST', '/api/logout', {}),
  me: () => request('GET', '/api/me', undefined, { allow401: true }),
  setup: (payload) => request('POST', '/api/setup', payload, { allow401: true }),
  seedDemo: () => request('POST', '/api/seed-demo', {}),
  changePassword: (current, next) => request('POST', '/api/change-password', { current, next }),

  /* --- data --- */
  bootstrap: () => request('GET', '/api/bootstrap'),
  meta: () => request('GET', '/api/meta'),
  saveSettings: (payload) => request('PUT', '/api/settings', payload),

  products: (params) => api.get('/api/products', params),
  product: (id) => api.get(`/api/products/${id}`),
  saveProduct: (id, payload) => (id ? api.put(`/api/products/${id}`, payload) : api.post('/api/products', payload)),
  deleteProduct: (id) => api.del(`/api/products/${id}`),
  saveRecipe: (id, lines) => api.put(`/api/products/${id}/recipe`, { lines }),

  categories: () => api.get('/api/categories'),
  saveCategory: (id, payload) => (id ? api.put(`/api/categories/${id}`, payload) : api.post('/api/categories', payload)),
  deleteCategory: (id) => api.del(`/api/categories/${id}`),

  ingredients: (params) => api.get('/api/ingredients', params),
  saveIngredient: (id, payload) => (id ? api.put(`/api/ingredients/${id}`, payload) : api.post('/api/ingredients', payload)),
  deleteIngredient: (id) => api.del(`/api/ingredients/${id}`),
  stockMove: (id, payload) => api.post(`/api/ingredients/${id}/stock`, payload),
  stockMoves: (params) => api.get('/api/stock-moves', params),

  suppliers: () => api.get('/api/suppliers'),
  saveSupplier: (id, payload) => (id ? api.put(`/api/suppliers/${id}`, payload) : api.post('/api/suppliers', payload)),
  deleteSupplier: (id) => api.del(`/api/suppliers/${id}`),

  customers: (params) => api.get('/api/customers', params),
  saveCustomer: (id, payload) => (id ? api.put(`/api/customers/${id}`, payload) : api.post('/api/customers', payload)),
  deleteCustomer: (id) => api.del(`/api/customers/${id}`),

  sales: (params) => api.get('/api/sales', params),
  sale: (id) => api.get(`/api/sales/${id}`),
  createSale: (payload) => api.post('/api/sales', payload),
  voidSale: (id) => api.post(`/api/sales/${id}/void`, {}),
  paySale: (id, payload) => api.post(`/api/sales/${id}/payment`, payload),

  expenses: (params) => api.get('/api/expenses', params),
  saveExpense: (id, payload) => (id ? api.put(`/api/expenses/${id}`, payload) : api.post('/api/expenses', payload)),
  deleteExpense: (id) => api.del(`/api/expenses/${id}`),

  users: () => api.get('/api/users'),
  saveUser: (id, payload) => (id ? api.put(`/api/users/${id}`, payload) : api.post('/api/users', payload)),
  deleteUser: (id) => api.del(`/api/users/${id}`),
  resetUserPassword: (id, password) => api.post(`/api/users/${id}/password`, { password }),

  /* --- reports (owner) --- */
  report: (name, params) => api.get(`/api/reports/${name}`, params),
  exportUrl: (type, params) => `/api/reports/export${qs({ type, ...params })}`,
};
