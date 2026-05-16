import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints will be implemented in future phases
export const projectsApi = {
  getAll: () => api.get('/api/projects'),
  getById: (id: number) => api.get(`/api/projects/${id}`),
  create: (data: any) => api.post('/api/projects', data),
  analyze: (path: string, name?: string) => api.post('/api/projects/analyze', { path, name }),
  delete: (id: number) => api.delete(`/api/projects/${id}`),
};

export const analysisApi = {
  analyze: (projectId: number) => api.post(`/api/analysis/${projectId}`),
  getStatus: (projectId: number) => api.get(`/api/analysis/${projectId}/status`),
};

export const graphApi = {
  getGraph: (projectId: number) => api.get(`/api/projects/${projectId}/graph`),
  getReactFlowGraph: (projectId: number, layout: 'hierarchical' | 'force' = 'hierarchical') =>
    api.get(`/api/projects/${projectId}/graph/react-flow?layout=${layout}`),
  getNode: (projectId: number, nodeId: string) =>
    api.get(`/api/projects/${projectId}/graph/node/${encodeURIComponent(nodeId)}`),
  getNodeDetails: (projectId: number, nodeId: string) =>
    api.get(`/api/projects/${projectId}/graph/node/${encodeURIComponent(nodeId)}/details`),
  askAboutNode: (projectId: number, nodeId: string, question: string) =>
    api.post(`/api/projects/${projectId}/graph/node/${encodeURIComponent(nodeId)}/ask`, { question }),
};

export const docsApi = {
  getDocs: (projectId: number) => api.get(`/api/docs/projects/${projectId}`),
  getSection: (projectId: number, section: string) =>
    api.get(`/api/docs/projects/${projectId}/sections/${section}`),
  generateDocs: (projectId: number, section?: string) =>
    api.post(`/api/docs/projects/${projectId}/generate`, { section }),
  regenerateSection: (projectId: number, section: string) =>
    api.post(`/api/docs/projects/${projectId}/regenerate/${section}`),
  deleteDocs: (projectId: number) => api.delete(`/api/docs/projects/${projectId}`),
  testConnection: () => api.get('/api/docs/test-connection'),
};

export const qaApi = {
  ask: (projectId: number, question: string, include_history: boolean = true) =>
    api.post(`/api/projects/${projectId}/qa`, { question, include_history }),
  getHistory: (projectId: number, limit: number = 50) =>
    api.get(`/api/projects/${projectId}/qa/history?limit=${limit}`),
  getSuggestions: (projectId: number) =>
    api.get(`/api/projects/${projectId}/qa/suggestions`),
  generateEmbeddings: (projectId: number) =>
    api.post(`/api/projects/${projectId}/qa/embeddings`),
};

export const techDebtApi = {
  getItems: (projectId: number) => api.get(`/api/projects/${projectId}/tech-debt`),
};

// Made with Bob
