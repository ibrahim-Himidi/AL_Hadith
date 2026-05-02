import axios from 'axios';

// API temel URL'ini ayarla (Localhost FastAPI sunucusu)
const API_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Arama Endpoint'i
export const searchHadiths = async (query, language = 'auto', page = 1, limit = 10) => {
  try {
    const response = await apiClient.get('/ara', {
      params: {
        q: query,
        dil: language,
        sayfa: page,
        limit: limit
      }
    });
    return response.data;
  } catch (error) {
    console.error('Arama sırasında hata oluştu:', error);
    throw error;
  }
};

export default apiClient;
