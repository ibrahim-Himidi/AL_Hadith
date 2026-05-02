<template>
  <div class="hadith-card glass-card">
    <div class="card-header">
      <div class="source-badge">
        <svg class="book-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
        {{ hadith.kitap || 'Sahih Bukhari' }} - Bab {{ hadith.bab || hadith.hadis_no }}
      </div>
      
      <div class="score-badge" title="RRF Hibrit Arama Skoru">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        Score: {{ formatScore(hadith.skor) }}
      </div>
    </div>

    <!-- Arapça Metin -->
    <div class="arabic-section" v-if="hadith.arapca">
      <div class="narrator ar-narrator" v-if="hadith.arapca.sanad">
        {{ hadith.arapca.sanad }}
      </div>
      <p class="arabic-text" dir="rtl">
        {{ hadith.arapca.hadith_detail || 'Arapça metin bulunamadı.' }}
      </p>
    </div>

    <div class="divider" v-if="hadith.arapca && hadith.ingilizce"></div>

    <!-- İngilizce Metin -->
    <div class="english-section" v-if="hadith.ingilizce">
      <div class="narrator en-narrator" v-if="hadith.ingilizce.sanad">
        {{ hadith.ingilizce.sanad }}
      </div>
      <p class="english-text">
        {{ hadith.ingilizce.hadith_detail || 'English text not available.' }}
      </p>
    </div>

    <div class="card-footer">
      <a v-if="hadith.kaynak_link" :href="hadith.kaynak_link" target="_blank" class="source-link">
        Sunnah.com'da Görüntüle
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
          <polyline points="15 3 21 3 21 9"></polyline>
          <line x1="10" y1="14" x2="21" y2="3"></line>
        </svg>
      </a>
      <span class="hadith-no">Hadis No: {{ hadith.hadis_no }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  hadith: {
    type: Object,
    required: true
  }
});

const formatScore = (score) => {
  return Number(score).toFixed(4);
};
</script>

<style scoped>
.hadith-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
}

.source-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.book-icon {
  width: 18px;
  height: 18px;
}

.score-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--color-primary-light);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-pill);
  font-size: 0.8rem;
  font-weight: 500;
}

.score-badge svg {
  width: 14px;
  height: 14px;
}

/* Arapça Bölüm */
.arabic-section {
  text-align: right;
}

.ar-narrator {
  color: var(--color-gold);
  font-family: var(--font-arabic);
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.arabic-text {
  font-family: var(--font-arabic);
  font-size: 1.75rem; /* Büyük font okunaklılık için */
  line-height: 2;
  color: var(--color-text-main);
}

.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, var(--color-border), transparent);
  margin: 0.5rem 0;
}

/* İngilizce Bölüm */
.english-section {
  text-align: left;
}

.en-narrator {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.english-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: var(--color-text-main);
}

/* Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--color-border);
}

.source-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-primary-light);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.source-link:hover {
  color: var(--color-primary-dark);
}

.source-link svg {
  width: 16px;
  height: 16px;
}

.hadith-no {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

@media (max-width: 600px) {
  .arabic-text {
    font-size: 1.5rem;
  }
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .score-badge {
    align-self: flex-start;
  }
}
</style>
