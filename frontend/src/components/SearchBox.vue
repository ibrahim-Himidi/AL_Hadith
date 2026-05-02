<template>
  <div class="search-container">
    <form @submit.prevent="handleSearch" class="search-form glass-card">
      <div class="input-group">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input 
          type="text" 
          v-model="query" 
          placeholder="Ara... (Örn: fasting in ramadan)"
          class="search-input"
          autofocus
        />
        <select v-model="language" class="lang-select">
          <option value="auto">🌍 Otomatik</option>
          <option value="ar">🇸🇦 Arapça</option>
          <option value="en">🇬🇧 İngilizce</option>
        </select>
        <button type="submit" class="search-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loader"></span>
          <span v-else>Ara</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isLoading: Boolean
});

const emit = defineEmits(['search']);

const query = ref('');
const language = ref('auto');

const handleSearch = () => {
  if (query.value.trim() !== '') {
    emit('search', { query: query.value, language: language.value });
  }
};
</script>

<style scoped>
.search-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.search-form {
  padding: 0.5rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.85);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.search-form:focus-within {
  transform: scale(1.02);
  box-shadow: 0 12px 40px rgba(45, 90, 39, 0.2);
  border-color: var(--color-primary-light);
}

.input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.search-icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-muted);
  margin-left: 1rem;
}

.search-input {
  flex: 1;
  background: transparent;
  padding: 1rem 0.5rem;
  font-size: 1.125rem;
  color: var(--color-text-main);
  border: none;
}

.search-input::placeholder {
  color: #99A394;
}

.lang-select {
  background: var(--color-surface-dim);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-pill);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.lang-select:hover {
  background: #E8EBE3;
  border-color: var(--color-primary-light);
}

.search-btn {
  background: var(--color-primary);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: var(--radius-pill);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(45, 90, 39, 0.3);
}

.search-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Mobile responsive */
@media (max-width: 600px) {
  .search-form {
    border-radius: var(--radius-md);
    padding: 1rem;
  }
  .input-group {
    flex-direction: column;
  }
  .search-icon {
    display: none;
  }
  .search-input {
    width: 100%;
    padding: 0.5rem;
    text-align: center;
  }
  .lang-select, .search-btn {
    width: 100%;
  }
}
</style>
