import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const api = {
  // Customers & Personas
  getCustomers: async () => {
    const res = await client.get('/customers');
    return res.data;
  },

  getCustomerProfile: async (customerId) => {
    const res = await client.get(`/customers/${customerId}`);
    return res.data;
  },

  // Products
  getProducts: async (category = null, search = null) => {
    const params = {};
    if (category) params.category = category;
    if (search) params.search = search;
    const res = await client.get('/products', { params });
    return res.data;
  },

  // Recommendations
  getRecommendations: async (customerId, season = 'Winter', modelType = 'hybrid', topK = 6) => {
    const res = await client.get('/recommendations', {
      params: {
        customer_id: customerId,
        season,
        model_type: modelType,
        top_k: topK,
      },
    });
    return res.data;
  },

  // Interaction Telemetry
  recordInteraction: async (customerId, productId, eventType, rating = null, dwellTimeSec = 0) => {
    const res = await client.post('/interact', {
      customer_id: customerId,
      product_id: productId,
      event_type: eventType,
      rating,
      dwell_time_sec: dwellTimeSec,
    });
    return res.data;
  },

  // Conversational Assistant
  sendChatMessage: async (customerId, message, chatHistory = []) => {
    const res = await client.post('/chat', {
      customer_id: customerId,
      message,
      chat_history: chatHistory,
    });
    return res.data;
  },

  // Governance & Responsible AI
  getFairnessAudit: async () => {
    const res = await client.get('/governance/fairness');
    return res.data;
  },

  getAuditLogs: async (limit = 30) => {
    const res = await client.get('/governance/audit-logs', { params: { limit } });
    return res.data;
  },

  getHITLQueue: async () => {
    const res = await client.get('/governance/hitl');
    return res.data;
  },

  takeHITLAction: async (entryId, decision, notes = '') => {
    const res = await client.post(`/governance/hitl/${entryId}/action`, {
      decision,
      reviewed_by: 'Admin Specialist',
      notes,
    });
    return res.data;
  },

  // ML Benchmarks & Seasonal Signals
  getModelBenchmarks: async () => {
    const res = await client.get('/metrics/benchmark');
    return res.data;
  },

  getSeasonalSignals: async () => {
    const res = await client.get('/seasonal');
    return res.data;
  },
};
