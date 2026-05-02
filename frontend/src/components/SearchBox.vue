<template>
  <div class="w-full flex flex-col items-center">
    <form @submit.prevent="handleSearch" class="w-full max-w-3xl relative mb-6 group">
      <input 
        v-model="query"
        type="text"
        dir="auto"
        placeholder="Niyet hakkında hadis ara... أو ابحث بالعربية"
        class="w-full h-16 bg-surface-container-high border border-outline-variant rounded-full pl-6 pr-16 text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all duration-300 font-body-main text-body-main"
      />
      <button 
        type="submit" 
        :disabled="isLoading"
        class="absolute right-2 top-2 h-12 w-12 bg-primary rounded-full flex items-center justify-center text-[#0F1923] hover:bg-primary-fixed transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isLoading" class="loader"></span>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </button>
    </form>

    <div class="flex items-center justify-center gap-2 mb-6 w-full max-w-3xl">
      <div class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider bg-surface-container-high px-3 py-1 rounded-full border border-outline-variant flex items-center">
        <span class="mr-2">DİL:</span>
        <select v-model="language" class="bg-transparent text-on-surface-variant outline-none cursor-pointer">
          <option value="auto">Otomatik</option>
          <option value="ar">Arapça</option>
          <option value="en">İngilizce</option>
        </select>
      </div>
    </div>
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
.loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(15, 25, 35, 0.3);
  border-radius: 50%;
  border-top-color: #0F1923;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
