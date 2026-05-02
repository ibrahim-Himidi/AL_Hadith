<template>
  <article class="min-w-0 overflow-hidden rounded-lg border border-[#E1D8C7] bg-white/84 p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md sm:p-5">
    <header class="flex min-w-0 flex-col gap-4 border-b border-[#ECE4D6] pb-4 sm:flex-row sm:items-start sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-bold text-[#597C63]">{{ hadith.kitap || 'Sahih Bukhari' }}</p>
        <h2 class="mt-1 text-xl font-semibold text-[#24342F]">{{ hadith.hadis_no }}</h2>
        <p v-if="hadith.ravi" class="mt-1 truncate text-sm text-[#6E7D73]">{{ hadith.ravi }}</p>
      </div>

      <div class="flex min-w-0 shrink-0 items-center gap-3">
        <span class="text-xs font-bold uppercase text-[#6E7D73]">{{ relevanceLabel }}</span>
        <div class="h-2 w-24 overflow-hidden rounded-lg bg-[#E6EDE3]">
          <div class="h-full rounded-lg bg-[#7E9FB1]" :style="{ width: scorePercentage }"></div>
        </div>
        <span class="text-sm font-semibold text-[#6E7D73]">{{ formatScore(hadith.skor) }}</span>
      </div>
    </header>

    <details v-if="hasSanad" class="mt-4 min-w-0 rounded-lg border border-[#EEE5D5] bg-[#FCFAF5]/82 px-4 py-3 text-sm text-[#6E7D73]">
      <summary class="cursor-pointer select-none font-semibold text-[#486E52]">{{ sanadLabel }}</summary>
      <div class="mt-3 grid gap-3">
        <p v-if="arabicSanad" class="font-arabic-body leading-8" dir="rtl" v-html="highlightText(arabicSanad, 'ar')"></p>
        <p v-if="englishSanad" class="leading-7" dir="ltr" v-html="highlightText(englishSanad, 'en')"></p>
      </div>
    </details>

    <div class="grid min-w-0 gap-5 py-5">
      <section v-if="hadith.arapca" class="text-right" dir="rtl">
        <p
          class="break-words font-arabic-display text-[22px] leading-[2.05] text-[#24342F] sm:text-[25px]"
          v-html="highlightText(displayArabicText, 'ar')"
        ></p>
      </section>

      <div v-if="hadith.arapca && hadith.ingilizce" class="h-px bg-[#ECE4D6]"></div>

      <section v-if="hadith.ingilizce" class="text-left" dir="ltr">
        <p class="break-words text-base leading-8 text-[#4F6158]" v-html="highlightText(displayEnglishText, 'en')"></p>
      </section>
    </div>

    <footer class="flex flex-col gap-3 border-t border-[#ECE4D6] pt-4 sm:flex-row sm:items-center sm:justify-between">
      <button
        v-if="isLong"
        type="button"
        class="rounded-lg border border-[#CADBCB] px-4 py-2 text-sm font-bold text-[#315B45] transition hover:bg-[#EAF2EA]"
        @click="expanded = !expanded"
      >
        {{ expanded ? collapseLabel : expandLabel }}
      </button>

      <a
        v-if="hadith.kaynak_link"
        :href="hadith.kaynak_link"
        target="_blank"
        rel="noreferrer"
        class="text-sm font-bold text-[#486E52] transition hover:text-[#24342F]"
      >
        {{ sourceLabel }}
      </a>
    </footer>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  hadith: {
    type: Object,
    required: true,
  },
  query: {
    type: String,
    default: '',
  },
  uiLanguage: {
    type: String,
    default: 'en',
  },
});

const expanded = ref(false);

const ARABIC_DIACRITICS_RE = /[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]/g;
const ARABIC_CHAR_RE = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/;
const ARABIC_VARIANTS = {
  صيام: ['صوم', 'صائم'],
  صوم: ['صيام', 'صائم'],
  صبر: ['صابر'],
  صدقه: ['تصدق', 'صدقات'],
};

const isArabicUi = computed(() => props.uiLanguage === 'ar');
const relevanceLabel = computed(() => (isArabicUi.value ? 'الصلة' : 'Relevance'));
const sanadLabel = computed(() => (isArabicUi.value ? 'سند الرواية' : 'Narration chain'));
const sourceLabel = computed(() => (isArabicUi.value ? 'عرض المصدر' : 'View source'));
const expandLabel = computed(() => (isArabicUi.value ? 'عرض النص الكامل' : 'Show full text'));
const collapseLabel = computed(() => (isArabicUi.value ? 'اختصار النص' : 'Collapse text'));

const formatScore = (score) => {
  const value = Number(score) || 0;
  return value.toFixed(value >= 10 ? 1 : 3);
};

const cleanMarkup = (text) => {
  if (!text) return '';
  return String(text)
    .replace(/\[\s*\/?\s*(?:name|verse|poem)(?:\s+[^\]]*)?\]/gi, '')
    .replace(/\[\s*\?+\s*\]/g, '')
    .replace(/\s+([،؛؟,.!?:;])/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();
};

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text;
  const slice = text.slice(0, maxLength);
  const lastSpace = slice.lastIndexOf(' ');
  return `${slice.slice(0, lastSpace > maxLength * 0.65 ? lastSpace : maxLength).trim()}...`;
};

const arabicSanad = computed(() => cleanMarkup(props.hadith?.arapca?.sanad));
const englishSanad = computed(() => cleanMarkup(props.hadith?.ingilizce?.sanad));
const arabicText = computed(() => cleanMarkup(props.hadith?.arapca?.hadith_detail) || 'النص العربي غير متوفر');
const englishText = computed(() => cleanMarkup(props.hadith?.ingilizce?.hadith_detail) || 'English text not available.');
const hasSanad = computed(() => Boolean(arabicSanad.value || englishSanad.value));
const isLong = computed(() => arabicText.value.length > 520 || englishText.value.length > 760);
const displayArabicText = computed(() => (expanded.value ? arabicText.value : truncateText(arabicText.value, 520)));
const displayEnglishText = computed(() => (expanded.value ? englishText.value : truncateText(englishText.value, 760)));

const escapeHtml = (text) => String(text)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

const escapeRegExp = (text) => String(text).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const normalizeArabicChar = (char) => {
  if (ARABIC_DIACRITICS_RE.test(char)) {
    ARABIC_DIACRITICS_RE.lastIndex = 0;
    return '';
  }
  ARABIC_DIACRITICS_RE.lastIndex = 0;
  if (/[\u0625\u0623\u0622\u0671]/.test(char)) return 'ا';
  if (char === 'ة') return 'ه';
  return char;
};

const normalizeArabic = (text) => String(text || '')
  .replace(ARABIC_DIACRITICS_RE, '')
  .replace(/[\u0625\u0623\u0622\u0671]/g, 'ا')
  .replace(/ة/g, 'ه')
  .replace(/[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s]+/g, ' ')
  .replace(/\s+/g, ' ')
  .trim();

const buildArabicTerms = (query) => {
  const terms = [];
  const add = (term) => {
    if (term.length >= 3 && !terms.includes(term)) terms.push(term);
  };

  normalizeArabic(query).split(' ').forEach((token) => {
    add(token);
    const withoutArticle = token.startsWith('ال') && token.length > 4 ? token.slice(2) : token;
    add(withoutArticle);
    (ARABIC_VARIANTS[withoutArticle] || []).forEach(add);
  });

  return terms;
};

const buildArabicIndex = (text) => {
  let normalized = '';
  const map = [];

  Array.from(text).forEach((char, index) => {
    const next = normalizeArabicChar(char);
    if (!next) return;
    normalized += next;
    map.push(index);
  });

  return { normalized, map };
};

const mergeRanges = (ranges) => {
  if (!ranges.length) return [];
  const sorted = ranges.sort((a, b) => a[0] - b[0]);
  const merged = [sorted[0]];

  for (const range of sorted.slice(1)) {
    const last = merged[merged.length - 1];
    if (range[0] <= last[1]) {
      last[1] = Math.max(last[1], range[1]);
    } else {
      merged.push(range);
    }
  }

  return merged;
};

const applyRanges = (text, ranges) => {
  if (!ranges.length) return escapeHtml(text);
  let output = '';
  let cursor = 0;

  mergeRanges(ranges).forEach(([start, end]) => {
    output += escapeHtml(text.slice(cursor, start));
    output += `<mark>${escapeHtml(text.slice(start, end))}</mark>`;
    cursor = end;
  });

  output += escapeHtml(text.slice(cursor));
  return output;
};

const highlightEnglish = (text, query) => {
  const terms = [...new Set(String(query).toLowerCase().split(/\s+/).filter((term) => term.length > 1))];
  if (!terms.length) return escapeHtml(text);

  const ranges = [];
  terms.forEach((term) => {
    const regex = new RegExp(escapeRegExp(term), 'gi');
    let match;
    while ((match = regex.exec(text)) !== null) {
      ranges.push([match.index, match.index + match[0].length]);
    }
  });

  return applyRanges(text, ranges);
};

const highlightArabic = (text, query) => {
  const terms = buildArabicTerms(query);
  if (!terms.length) return escapeHtml(text);

  const { normalized, map } = buildArabicIndex(text);
  const ranges = [];

  terms.forEach((term) => {
    let index = normalized.indexOf(term);
    while (index !== -1) {
      const start = map[index];
      const end = map[index + term.length - 1] + 1;
      ranges.push([start, end]);
      index = normalized.indexOf(term, index + term.length);
    }
  });

  return applyRanges(text, ranges);
};

const highlightText = (text, language) => {
  if (!props.query) return escapeHtml(text);
  if (language === 'ar' || ARABIC_CHAR_RE.test(props.query)) {
    return highlightArabic(text, props.query);
  }
  return highlightEnglish(text, props.query);
};

const scorePercentage = computed(() => {
  const score = Number(props.hadith.skor) || 0;
  const percent = Math.max(8, Math.min(100, score >= 10 ? score : score * 14));
  return `${percent}%`;
});
</script>

<style scoped>
:deep(mark) {
  border-radius: 0.35rem;
  background: #E8D8A8;
  color: inherit;
  padding: 0.08rem 0.18rem;
}
</style>
