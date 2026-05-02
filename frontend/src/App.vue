<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-bg"></div>
      <div class="header-content">
        <h1>Hadis Semantik Arama</h1>
        <p class="subtitle">Yapay zeka destekli, çift dilli (Arapça & İngilizce) hadis arama motoru.</p>
        <SearchBox :isLoading="isLoading" @search="onSearch" />
      </div>
    </header>

    <main class="main-content">
      <!-- Durum Mesajları -->
      <div v-if="error" class="error-msg glass-card">
        🚨 Bir hata oluştu: {{ error }}
      </div>
      
      <div v-if="!isLoading && searchResults.length === 0 && hasSearched" class="empty-msg glass-card">
        "{ { lastQuery } }" için hiçbir sonuç bulunamadı. Lütfen farklı kelimeler deneyin.
      </div>

      <!-- Sonuç İstatistikleri -->
      <div v-if="searchResults.length > 0 && !isLoading" class="results-stats">
        <strong>{{ totalResults }}</strong> hadis bulundu. 
        <span class="mode-badge">{{ searchMode === 'hybrid' ? 'Hibrit Arama (AI + Metin)' : 'Klasik Arama' }}</span>
      </div>

      <!-- Hadis Kartları -->
      <div class="cards-layout" v-if="searchResults.length > 0">
        <HadithCard 
          v-for="hadith in searchResults" 
          :key="hadith.id" 
          :hadith="hadith" 
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SearchBox from './components/SearchBox.vue';
import HadithCard from './components/HadithCard.vue';
import { searchHadiths } from './services/api';

const searchResults = ref([]);
const totalResults = ref(0);
const searchMode = ref('');
const isLoading = ref(false);
const error = ref(null);
const hasSearched = ref(false);
const lastQuery = ref('');

const onSearch = async ({ query, language }) => {
  if (!query) return;
  
  isLoading.value = true;
  error.value = null;
  hasSearched.value = true;
  lastQuery.value = query;

  try {
    const data = await searchHadiths(query, language);
    searchResults.value = data.sonuclar;
    totalResults.value = data.toplam;
    searchMode.value = data.mod;
    
    // Yumuşak kaydırma
    window.scrollTo({ top: 300, behavior: 'smooth' });
  } catch (err) {
    error.value = err.message || 'Sunucuya ulaşılamadı. Lütfen API\'nin çalıştığından emin olun.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  position: relative;
  padding: 6rem 2rem 4rem;
  text-align: center;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: -50%;
  left: -10%;
  width: 120%;
  height: 200%;
  background: radial-gradient(circle, var(--color-primary-light) 0%, transparent 60%);
  opacity: 0.1;
  z-index: 0;
  pointer-events: none;
}

.header-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 3.5rem;
  font-weight: 800;
  color: var(--color-primary-dark);
  margin-bottom: 1rem;
  letter-spacing: -0.03em;
}

.subtitle {
  font-size: 1.25rem;
  color: var(--color-text-muted);
  margin-bottom: 3rem;
}

.main-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
}

.results-stats {
  margin-bottom: 1.5rem;
  color: var(--color-text-muted);
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mode-badge {
  background: var(--color-gold-light);
  color: var(--color-text-main);
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.error-msg {
  padding: 1.5rem;
  color: #93000a;
  background: #ffdad6;
  border-color: #ffb4ab;
  text-align: center;
  font-weight: 500;
}

.empty-msg {
  padding: 3rem;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 1.1rem;
}

.cards-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (max-width: 768px) {
  h1 {
    font-size: 2.5rem;
  }
  .app-header {
    padding: 4rem 1rem 2rem;
  }
}
</style>
