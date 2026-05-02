<template>
  <div
    :dir="isArabicUi ? 'rtl' : 'ltr'"
    :lang="uiLanguage"
    class="flex min-h-screen flex-col overflow-x-hidden bg-[#F4EFE4] text-[#1F2F2A] antialiased"
  >
    <div class="app-texture" aria-hidden="true"></div>

    <header class="sticky top-0 z-50 border-b border-[#D9D1BF]/80 bg-[#F9F6EE]/88 backdrop-blur-2xl">
      <div class="mx-auto flex w-full max-w-7xl flex-wrap items-center gap-3 px-4 py-4 md:flex-nowrap md:justify-between md:px-6">
        <button type="button" class="flex min-w-0 flex-1 items-center gap-3 text-start md:flex-none" @click="goTo('home')">
          <span class="logo-mark">ح</span>
          <span class="min-w-0">
            <span class="block truncate text-lg font-semibold text-[#20352E]">HadithSearch</span>
            <span class="block text-sm text-[#6C7B72]">{{ t.brandSub }}</span>
          </span>
        </button>

        <nav class="order-3 grid w-full grid-cols-4 gap-1 rounded-lg border border-[#DED6C5] bg-white/70 p-1 shadow-sm md:order-none md:w-auto md:flex">
          <button
            v-for="item in navItems"
            :key="item.id"
            type="button"
            class="min-w-0 rounded-lg px-2 py-2 text-sm font-semibold transition md:shrink-0 md:px-4"
            :class="currentPage === item.id ? 'bg-[#26493B] text-white shadow-sm' : 'text-[#53665C] hover:bg-[#EAF2EA] hover:text-[#20352E]'"
            @click="goTo(item.id)"
          >
            <span class="hidden sm:inline">{{ item.label }}</span>
            <span class="sm:hidden">{{ item.shortLabel }}</span>
          </button>
        </nav>

        <div class="flex items-center gap-2 md:flex-none">
          <span class="hidden text-sm font-medium text-[#6C7B72] sm:inline">{{ t.language }}</span>
          <div class="flex rounded-lg border border-[#DED6C5] bg-white/70 p-1 shadow-sm">
            <button
              type="button"
              class="rounded-lg px-3 py-2 text-sm font-bold transition"
              :class="uiLanguage === 'en' ? 'bg-[#7A9BAE] text-white' : 'text-[#53665C] hover:bg-[#EAF2EA]'"
              @click="setUiLanguage('en')"
            >
              EN
            </button>
            <button
              type="button"
              class="rounded-lg px-3 py-2 text-sm font-bold transition"
              :class="uiLanguage === 'ar' ? 'bg-[#7A9BAE] text-white' : 'text-[#53665C] hover:bg-[#EAF2EA]'"
              @click="setUiLanguage('ar')"
            >
              AR
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="relative z-10 flex-1">
      <section v-if="currentPage === 'home'" class="page-fade">
        <div class="mx-auto grid w-full max-w-7xl gap-6 px-4 py-8 md:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.9fr)] md:px-6 md:py-12">
          <section class="search-command overflow-hidden rounded-lg border border-[#DCD4C1] bg-[#FCFAF5]/88 shadow-[0_24px_80px_rgba(49,68,58,0.13)]">
            <div dir="ltr" class="grid gap-8 overflow-hidden p-5 md:grid-cols-[minmax(0,1fr)_280px] md:p-8 lg:p-10">
              <div :dir="isArabicUi ? 'rtl' : 'ltr'" class="flex min-h-[390px] min-w-0 flex-col justify-center">
                <p class="eyebrow">{{ t.heroEyebrow }}</p>
                <h1 class="mt-5 max-w-3xl text-3xl font-semibold leading-[1.1] text-[#1E332B] sm:text-4xl md:text-5xl lg:text-6xl">
                  {{ t.heroTitle }}
                </h1>
                <p class="mt-5 max-w-2xl text-lg leading-8 text-[#5B6E64]">
                  {{ t.heroSubtitle }}
                </p>

                <form class="mt-8" dir="ltr" @submit.prevent="submitSearch">
                  <div class="search-shell">
                    <input
                      v-model="searchQuery"
                      type="search"
                      dir="auto"
                      :placeholder="t.searchPlaceholder"
                      class="min-h-14 min-w-0 flex-1 bg-transparent px-4 text-base text-[#1F2F2A] outline-none placeholder:text-[#87958D]"
                    />
                    <button
                      type="submit"
                      :disabled="isLoading"
                      class="h-12 rounded-lg bg-[#26493B] px-5 text-sm font-bold text-white transition hover:bg-[#1D3A2F] disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {{ isLoading ? t.searching : t.search }}
                    </button>
                  </div>
                </form>

                <div class="mt-4 flex flex-wrap gap-2">
                  <button
                    v-for="chip in quickSearches"
                    :key="chip.query"
                    type="button"
                    class="rounded-lg border border-[#D8D0BE] bg-white/72 px-4 py-2 text-sm font-semibold text-[#53665C] transition hover:border-[#26493B] hover:bg-[#EEF5EE] hover:text-[#20352E]"
                    :dir="chip.lang === 'ar' ? 'rtl' : 'ltr'"
                    @click="runQuickSearch(chip.query)"
                  >
                    {{ chip.label }}
                  </button>
                </div>
              </div>

              <div class="manuscript-panel hidden min-w-0 overflow-hidden md:grid" aria-hidden="true">
                <div class="manuscript-page">
                  <span class="line wide"></span>
                  <span class="line"></span>
                  <p dir="rtl">قال رسول الله صلى الله عليه وسلم</p>
                  <span class="line short"></span>
                  <span class="line wide blue"></span>
                  <span class="line"></span>
                </div>
                <div class="source-tile">
                  <span class="min-w-0 truncate">{{ t.collectionLabel }}</span>
                  <strong class="shrink-0">7,277</strong>
                </div>
              </div>
            </div>
          </section>

          <aside class="grid gap-6">
            <section class="rounded-lg border border-[#DCD4C1] bg-white/78 p-6 shadow-sm">
              <div class="flex items-center justify-between gap-4">
                <p class="eyebrow">{{ t.dailyTitle }}</p>
                <span class="rounded-lg bg-[#E9F1E7] px-3 py-1 text-sm font-semibold text-[#315B45]">Bukhari 1</span>
              </div>
              <p class="mt-6 font-arabic-display text-3xl leading-[2.05] text-[#1E332B]" dir="rtl">
                {{ dailyHadith.ar }}
              </p>
              <div class="my-5 h-px bg-[#E8DFCF]"></div>
              <p class="text-base leading-8 text-[#53665C]" dir="ltr">{{ dailyHadith.en }}</p>
              <p class="mt-5 text-sm text-[#78877F]">{{ dailyHadith.meta }}</p>
            </section>

            <section class="grid grid-cols-2 gap-3">
              <div v-for="stat in stats" :key="stat.label" class="rounded-lg border border-[#DCD4C1] bg-[#FCFAF5]/82 p-4 shadow-sm">
                <p class="text-2xl font-semibold text-[#1E332B]">{{ stat.value }}</p>
                <p class="mt-1 text-sm text-[#6C7B72]">{{ stat.label }}</p>
              </div>
            </section>
          </aside>
        </div>

        <section class="mx-auto grid w-full max-w-7xl gap-5 px-4 pb-12 md:grid-cols-3 md:px-6">
          <article
            v-for="panel in calmPanels"
            :key="panel.title"
            class="rounded-lg border border-[#DCD4C1] bg-white/72 p-6 shadow-sm"
          >
            <p class="eyebrow">{{ panel.kicker }}</p>
            <h2 class="mt-3 text-xl font-semibold text-[#1E332B]">{{ panel.title }}</h2>
            <p class="mt-3 leading-7 text-[#5B6E64]">{{ panel.body }}</p>
          </article>
        </section>
      </section>

      <section v-if="currentPage === 'search'" class="page-fade mx-auto w-full max-w-7xl overflow-x-hidden px-4 py-8 md:px-6 md:py-12 min-h-[calc(100vh-156px)]">
        <div class="grid min-w-0 gap-6 lg:grid-cols-[330px_minmax(0,1fr)]">
          <aside class="min-w-0 lg:sticky lg:top-28 lg:self-start">
            <div class="min-w-0 rounded-lg border border-[#DCD4C1] bg-[#FCFAF5]/86 p-5 shadow-sm">
              <p class="eyebrow">{{ t.searchKicker }}</p>
              <h1 class="mt-3 break-words text-2xl font-semibold leading-tight text-[#1E332B] sm:text-3xl">{{ t.searchTitle }}</h1>
              <p class="mt-3 break-words leading-7 text-[#5B6E64]">{{ t.searchSubtitle }}</p>

              <form class="mt-6" @submit.prevent="submitSearch">
                <div class="grid gap-3">
                  <input
                    v-model="searchQuery"
                    type="search"
                    dir="auto"
                    :placeholder="t.searchPlaceholder"
                    class="h-14 w-full min-w-0 rounded-lg border border-[#D8D0BE] bg-white px-4 text-[#1F2F2A] outline-none placeholder:text-[#87958D] focus:border-[#315B45]"
                  />
                  <button
                    type="submit"
                    :disabled="isLoading"
                    class="h-12 rounded-lg bg-[#26493B] text-sm font-bold text-white transition hover:bg-[#1D3A2F] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {{ isLoading ? t.searching : t.search }}
                  </button>
                </div>
              </form>

              <div class="mt-6 grid gap-4 border-t border-[#E8DFCF] pt-5">
                <label class="grid gap-2">
                  <span class="text-sm font-semibold text-[#53665C]">{{ t.filterBook }}</span>
                  <select v-model="bookFilter" class="h-12 w-full min-w-0 rounded-lg border border-[#D8D0BE] bg-white px-3 text-[#1F2F2A] outline-none focus:border-[#315B45]">
                    <option value="">{{ t.allBooks }}</option>
                    <option v-for="book in bookOptions" :key="book" :value="book">{{ book }}</option>
                  </select>
                </label>
                <label class="grid gap-2">
                  <span class="text-sm font-semibold text-[#53665C]">{{ t.filterNarrator }}</span>
                  <input
                    v-model="narratorFilter"
                    type="search"
                    :placeholder="t.narratorPlaceholder"
                    class="h-12 w-full min-w-0 rounded-lg border border-[#D8D0BE] bg-white px-3 text-[#1F2F2A] outline-none placeholder:text-[#87958D] focus:border-[#315B45]"
                  />
                </label>
                <button type="button" class="h-11 rounded-lg border border-[#CADBCB] text-sm font-bold text-[#315B45] transition hover:bg-[#EAF2EA]" @click="clearFilters">
                  {{ t.clear }}
                </button>
              </div>
            </div>
          </aside>

          <section class="min-w-0">
            <div class="mb-5 rounded-lg border border-[#DCD4C1] bg-white/74 p-4 shadow-sm">
              <div v-if="hasSearched && !isLoading && !error" class="flex min-w-0 flex-col gap-2 text-sm text-[#5B6E64] md:flex-row md:items-center md:justify-between">
                <span class="font-semibold text-[#1E332B]">{{ filteredResults.length }} / {{ totalResults }} {{ t.resultsFound }}</span>
                <span class="break-words">{{ t.mode }}: {{ searchMode || 'bm25_only' }} · {{ detectedSearchLanguageLabel }}</span>
              </div>
              <p v-else class="text-sm text-[#5B6E64]">{{ t.emptySearchState }}</p>
            </div>

            <div v-if="error" class="rounded-lg border border-[#E1ABA6] bg-[#FFF3F0] p-4 text-[#8B332C]">
              {{ error }}
            </div>

            <div v-if="isLoading" class="grid gap-5">
              <div v-for="n in 3" :key="n" class="h-52 animate-pulse rounded-lg bg-white/70 ring-1 ring-[#DCD4C1]"></div>
            </div>

            <div v-else-if="hasSearched && results.length === 0 && !error" class="rounded-lg border border-[#DCD4C1] bg-white/78 p-10 text-center text-[#5B6E64] shadow-sm">
              {{ t.noResults }} "{{ searchQuery }}".
            </div>

            <div v-else-if="hasSearched && filteredResults.length === 0 && !error" class="rounded-lg border border-[#DCD4C1] bg-white/78 p-10 text-center text-[#5B6E64] shadow-sm">
              {{ t.noFilteredResults }}
            </div>

            <div v-else class="grid min-w-0 gap-5">
              <HadithCard
                v-for="hadith in filteredResults"
                :key="hadith.id"
                :hadith="hadith"
                :query="searchQuery"
                :ui-language="uiLanguage"
              />
            </div>
          </section>
        </div>
      </section>

      <section v-if="currentPage === 'books'" class="page-fade mx-auto w-full max-w-7xl px-4 py-10 md:px-6 md:py-14 min-h-[calc(100vh-140px)]">
        <div class="mb-8 max-w-3xl">
          <p class="eyebrow">{{ t.booksKicker }}</p>
          <h1 class="mt-3 text-4xl font-semibold text-[#1E332B]">{{ t.booksTitle }}</h1>
          <p class="mt-4 text-lg leading-8 text-[#5B6E64]">{{ t.booksSubtitle }}</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <article v-for="book in books" :key="book.name" class="book-card">
            <p class="font-arabic-body text-3xl leading-[1.7] text-[#315B45]" dir="rtl">{{ book.arabic }}</p>
            <h2 class="mt-4 text-xl font-semibold text-[#1E332B]">{{ book.name }}</h2>
            <p class="mt-3 min-h-14 leading-7 text-[#5B6E64]">{{ book.description }}</p>
            <div class="mt-6 flex items-center justify-between gap-3 text-sm">
              <span class="text-[#6C7B72]">{{ book.count }}</span>
              <span class="rounded-lg px-3 py-1 font-bold" :class="book.active ? 'bg-[#EAF2EA] text-[#315B45]' : 'bg-[#EEF2F3] text-[#647985]'">
                {{ book.active ? t.available : t.planned }}
              </span>
            </div>
          </article>
        </div>
      </section>

      <section v-if="currentPage === 'ai'" class="page-fade grid min-h-[calc(100vh-156px)] place-items-center px-4 py-16">
        <div class="coming-card max-w-2xl text-center">
          <div class="ai-orbit mx-auto mb-8">AI</div>
          <p class="eyebrow">{{ t.aiKicker }}</p>
          <h1 class="mt-4 text-4xl font-semibold text-[#1E332B]">{{ t.aiTitle }}</h1>
          <p class="mt-4 text-lg leading-8 text-[#5B6E64]">{{ t.aiSubtitle }}</p>
        </div>
      </section>
    </main>

    <footer class="relative z-10 border-t border-[#D9D1BF] bg-[#EAE2D2]">
      <div class="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-8 text-sm text-[#5B6E64] md:flex-row md:items-center md:justify-between md:px-6">
        <p class="font-semibold text-[#1E332B]">HadithSearch</p>
        <div class="flex flex-wrap gap-5">
          <button type="button" class="transition hover:text-[#315B45]" @click="goTo('home')">{{ t.about }}</button>
          <a class="transition hover:text-[#315B45]" href="mailto:230205913@ostimteknik.edu.tr,230205928@ostimteknik.edu.tr">{{ t.contact }}</a>
          <button type="button" class="transition hover:text-[#315B45]" @click="setUiLanguage(isArabicUi ? 'en' : 'ar')">{{ t.language }}</button>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import HadithCard from './components/HadithCard.vue';
import { searchHadiths } from './services/api';

const currentPage = ref('home');
const uiLanguage = ref('en');
const searchQuery = ref('');
const results = ref([]);
const totalResults = ref(0);
const searchMode = ref('');
const isLoading = ref(false);
const error = ref(null);
const hasSearched = ref(false);
const bookFilter = ref('');
const narratorFilter = ref('');
const detectedSearchLanguage = ref('en');

const translations = {
  en: {
    brandSub: 'Arabic and English',
    nav: { home: 'Home', search: 'Search Hadith', books: 'Books', ai: 'HadithAI (Coming Soon)' },
    language: 'Language',
    heroEyebrow: 'Hadith research workspace',
    heroTitle: 'A quieter way to search authentic hadith.',
    heroSubtitle: 'Search Sahih Bukhari in Arabic or English through a focused reading interface built for long texts, careful comparison, and calm study.',
    searchPlaceholder: 'Search in English or Arabic...',
    search: 'Search',
    searching: 'Searching',
    collectionLabel: 'Available hadiths',
    dailyTitle: 'Daily Hadith',
    searchKicker: 'Search Hadith',
    searchTitle: 'Search by topic, wording, book, or narrator',
    searchSubtitle: 'Arabic and English queries are routed to the matching text index and shown with highlighted terms.',
    filterBook: 'Book',
    filterNarrator: 'Narrator',
    allBooks: 'All books',
    narratorPlaceholder: 'Narrator name',
    clear: 'Clear filters',
    resultsFound: 'results',
    mode: 'Mode',
    emptySearchState: 'Run a search to begin reading results.',
    noResults: 'No results found for',
    noFilteredResults: 'No results match the selected filters.',
    booksKicker: 'Library',
    booksTitle: 'Hadith books',
    booksSubtitle: 'A calm library view for available collections and future sources.',
    available: 'Available',
    planned: 'Planned',
    aiKicker: 'Coming Soon',
    aiTitle: 'HadithAI is Coming Soon',
    aiSubtitle: 'AI-powered Hadith insights will be available soon.',
    about: 'About',
    contact: 'Contact',
  },
  ar: {
    brandSub: 'العربية والإنجليزية',
    nav: { home: 'الرئيسية', search: 'بحث الحديث', books: 'الكتب', ai: 'HadithAI' },
    language: 'اللغة',
    heroEyebrow: 'مساحة بحث حديثية',
    heroTitle: 'طريقة أكثر هدوءا للبحث في الحديث الصحيح.',
    heroSubtitle: 'ابحث في صحيح البخاري بالعربية أو الإنجليزية ضمن واجهة قراءة مركزة للنصوص الطويلة والمقارنة الهادئة.',
    searchPlaceholder: 'ابحث بالعربية أو الإنجليزية...',
    search: 'بحث',
    searching: 'جاري البحث',
    collectionLabel: 'الأحاديث المتاحة',
    dailyTitle: 'حديث اليوم',
    searchKicker: 'بحث الحديث',
    searchTitle: 'ابحث بالموضوع أو اللفظ أو الكتاب أو الراوي',
    searchSubtitle: 'توجه الاستعلامات العربية والإنجليزية إلى فهرس النص المناسب مع إبراز الكلمات المطابقة.',
    filterBook: 'الكتاب',
    filterNarrator: 'الراوي',
    allBooks: 'كل الكتب',
    narratorPlaceholder: 'اسم الراوي',
    clear: 'مسح الفلاتر',
    resultsFound: 'نتيجة',
    mode: 'النمط',
    emptySearchState: 'ابدأ البحث لعرض النتائج.',
    noResults: 'لا توجد نتائج لـ',
    noFilteredResults: 'لا توجد نتائج تطابق الفلاتر المحددة.',
    booksKicker: 'المكتبة',
    booksTitle: 'كتب الحديث',
    booksSubtitle: 'عرض مكتبي هادئ للمجموعات المتاحة والمصادر القادمة.',
    available: 'متاح',
    planned: 'مخطط',
    aiKicker: 'قريبا',
    aiTitle: 'HadithAI قادم قريبا',
    aiSubtitle: 'ستتوفر قريبا رؤى مدعومة بالذكاء الاصطناعي حول الأحاديث.',
    about: 'حول',
    contact: 'تواصل',
  },
};

const t = computed(() => translations[uiLanguage.value]);
const isArabicUi = computed(() => uiLanguage.value === 'ar');

const navItems = computed(() => [
  { id: 'home', label: t.value.nav.home, shortLabel: uiLanguage.value === 'ar' ? 'الرئيسية' : 'Home' },
  { id: 'search', label: t.value.nav.search, shortLabel: uiLanguage.value === 'ar' ? 'بحث' : 'Search' },
  { id: 'books', label: t.value.nav.books, shortLabel: uiLanguage.value === 'ar' ? 'كتب' : 'Books' },
  { id: 'ai', label: t.value.nav.ai, shortLabel: uiLanguage.value === 'ar' ? 'AI' : 'AI' },
]);

const quickSearches = [
  { label: 'Prayer', query: 'prayer', lang: 'en' },
  { label: 'Fasting', query: 'fasting', lang: 'en' },
  { label: 'الصلاة', query: 'الصلاة', lang: 'ar' },
  { label: 'الصبر', query: 'الصبر', lang: 'ar' },
];

const dailyHadith = {
  ar: 'إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى',
  en: 'Actions are judged by intentions, and every person will receive according to what they intended.',
  meta: 'Sahih al-Bukhari, Hadith 1',
};

const stats = computed(() => [
  { value: '7,277', label: isArabicUi.value ? 'حديث' : 'Hadiths' },
  { value: '2', label: isArabicUi.value ? 'لغتان' : 'Languages' },
  { value: 'AR', label: isArabicUi.value ? 'اتجاه RTL' : 'RTL ready' },
  { value: 'EN', label: isArabicUi.value ? 'اتجاه LTR' : 'LTR ready' },
]);

const calmPanels = computed(() => [
  {
    kicker: isArabicUi.value ? 'قراءة' : 'Reading',
    title: isArabicUi.value ? 'نص عربي واسع' : 'Spacious Arabic text',
    body: isArabicUi.value ? 'خط واضح ومسافات مريحة للقراءة الطويلة.' : 'Generous line-height and Arabic-aware type for long passages.',
  },
  {
    kicker: isArabicUi.value ? 'بحث' : 'Search',
    title: isArabicUi.value ? 'إبراز الكلمات' : 'Matched terms highlighted',
    body: isArabicUi.value ? 'تظهر مواضع المطابقة مباشرة داخل بطاقة الحديث.' : 'Matches appear directly inside each hadith card.',
  },
  {
    kicker: isArabicUi.value ? 'مصادر' : 'Sources',
    title: isArabicUi.value ? 'روابط المصدر' : 'Source links included',
    body: isArabicUi.value ? 'تبقى الإحالة ظاهرة عند توفر رابط المصدر.' : 'Each result keeps its source reference available.',
  },
]);

const books = computed(() => [
  {
    name: 'Sahih Bukhari',
    arabic: 'صحيح البخاري',
    count: '7,277 hadiths',
    active: true,
    description: isArabicUi.value ? 'المجموعة المتاحة حاليا في البحث.' : 'The active searchable collection in this release.',
  },
  {
    name: 'Sahih Muslim',
    arabic: 'صحيح مسلم',
    count: isArabicUi.value ? 'قريبا' : 'Coming soon',
    active: false,
    description: isArabicUi.value ? 'مخطط لإضافته في مرحلة لاحقة.' : 'Prepared for a later collection expansion.',
  },
  {
    name: 'Sunan Collections',
    arabic: 'كتب السنن',
    count: isArabicUi.value ? 'قريبا' : 'Coming soon',
    active: false,
    description: isArabicUi.value ? 'مساحة جاهزة للمصادر المستقبلية.' : 'A future space for additional source libraries.',
  },
]);

const bookOptions = computed(() => {
  const names = results.value.map((item) => item.kitap).filter(Boolean);
  return [...new Set(names)].sort();
});

const filteredResults = computed(() => {
  const narrator = narratorFilter.value.trim().toLowerCase();
  return results.value.filter((item) => {
    const bookMatches = !bookFilter.value || item.kitap === bookFilter.value;
    const narratorMatches = !narrator || String(item.ravi || '').toLowerCase().includes(narrator);
    return bookMatches && narratorMatches;
  });
});

const detectedSearchLanguageLabel = computed(() => (
  detectedSearchLanguage.value === 'ar' ? 'Arabic' : 'English'
));

const detectSearchLanguage = (query) => (
  /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/.test(query) ? 'ar' : 'en'
);

const goTo = (page) => {
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const setUiLanguage = (language) => {
  uiLanguage.value = language;
};

const runQuickSearch = async (query) => {
  searchQuery.value = query;
  await submitSearch();
};

const clearFilters = () => {
  bookFilter.value = '';
  narratorFilter.value = '';
};

const submitSearch = async () => {
  const query = searchQuery.value.trim();
  if (!query) return;

  detectedSearchLanguage.value = detectSearchLanguage(query);
  currentPage.value = 'search';
  isLoading.value = true;
  error.value = null;
  hasSearched.value = true;
  clearFilters();

  try {
    const data = await searchHadiths(query, detectedSearchLanguage.value);
    results.value = data.sonuclar || [];
    totalResults.value = data.toplam || 0;
    searchMode.value = data.mod || 'bm25_only';

    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    results.value = [];
    totalResults.value = 0;
    error.value = err?.message || 'Could not reach the API.';
  } finally {
    isLoading.value = false;
  }
};

const syncDocumentDirection = () => {
  document.documentElement.lang = uiLanguage.value;
  document.documentElement.dir = isArabicUi.value ? 'rtl' : 'ltr';
};

watch(uiLanguage, syncDocumentDirection);
onMounted(syncDocumentDirection);
</script>

<style scoped>
.app-texture {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  height: 0;
  flex: none;
  background:
    radial-gradient(circle at 12% 10%, rgba(122, 155, 174, 0.20), transparent 28%),
    radial-gradient(circle at 88% 4%, rgba(78, 123, 92, 0.18), transparent 24%),
    linear-gradient(115deg, rgba(243, 235, 216, 0.96), rgba(235, 242, 232, 0.72) 46%, rgba(238, 245, 246, 0.82));
}

.app-texture::after {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0.42;
  background-image:
    linear-gradient(90deg, rgba(38, 73, 59, 0.045) 1px, transparent 1px),
    linear-gradient(0deg, rgba(122, 155, 174, 0.045) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: linear-gradient(to bottom, #000, transparent 82%);
}

.logo-mark {
  display: grid;
  height: 2.75rem;
  width: 2.75rem;
  place-items: center;
  border-radius: 0.5rem;
  background: linear-gradient(145deg, #26493B, #537760);
  color: white;
  font: 700 1.45rem/1 "Noto Naskh Arabic", serif;
  box-shadow: 0 12px 28px rgba(38, 73, 59, 0.22);
}

.eyebrow {
  display: inline-flex;
  width: fit-content;
  border-radius: 0.5rem;
  background: rgba(234, 242, 234, 0.88);
  padding: 0.45rem 0.7rem;
  color: #315B45;
  font-size: 0.78rem;
  font-weight: 800;
}

.search-command {
  position: relative;
}

.search-command::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.70), transparent 42%),
    radial-gradient(circle at 82% 20%, rgba(122, 155, 174, 0.18), transparent 30%);
}

.search-command > * {
  position: relative;
}

.search-shell {
  display: flex;
  min-height: 4.25rem;
  align-items: center;
  gap: 0.75rem;
  border: 1px solid #D8D0BE;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.92);
  padding: 0.5rem;
  box-shadow: 0 18px 50px rgba(53, 78, 65, 0.15);
}

.manuscript-panel {
  display: grid;
  align-content: center;
  gap: 1rem;
}

.manuscript-page {
  min-height: 300px;
  border: 1px solid rgba(185, 172, 145, 0.6);
  border-radius: 0.5rem;
  background:
    linear-gradient(145deg, rgba(255, 252, 244, 0.94), rgba(239, 231, 213, 0.88)),
    repeating-linear-gradient(0deg, transparent 0 28px, rgba(91, 110, 100, 0.07) 29px 30px);
  padding: 1.25rem;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7), 0 18px 48px rgba(65, 81, 71, 0.14);
}

.manuscript-page p {
  margin: 1.8rem 0;
  color: #315B45;
  font-family: "Noto Naskh Arabic", serif;
  font-size: 1.6rem;
  line-height: 2.05;
}

.line {
  display: block;
  height: 0.6rem;
  width: 74%;
  border-radius: 0.4rem;
  background: rgba(49, 91, 69, 0.16);
  margin-block: 0.95rem;
}

.line.wide {
  width: 100%;
}

.line.short {
  width: 48%;
}

.line.blue {
  background: rgba(122, 155, 174, 0.22);
}

.source-tile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-radius: 0.5rem;
  background: #26493B;
  color: white;
  padding: 1rem;
  direction: ltr;
  box-shadow: 0 16px 36px rgba(38, 73, 59, 0.18);
  overflow: hidden;
}

.source-tile span {
  color: rgba(255, 255, 255, 0.74);
  font-size: 0.86rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.source-tile strong {
  font-size: 1.55rem;
  flex-shrink: 0;
}

.book-card,
.coming-card {
  border: 1px solid #DCD4C1;
  border-radius: 0.5rem;
  background: rgba(252, 250, 245, 0.86);
  padding: 1.5rem;
  box-shadow: 0 12px 34px rgba(65, 81, 71, 0.09);
}

.book-card {
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.book-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 42px rgba(65, 81, 71, 0.13);
}

.ai-orbit {
  display: grid;
  height: 5rem;
  width: 5rem;
  place-items: center;
  border-radius: 0.5rem;
  background: linear-gradient(145deg, #EAF2EA, #E8F0F3);
  color: #315B45;
  font-weight: 800;
  box-shadow: 0 18px 42px rgba(49, 91, 69, 0.16);
  animation: pulseSoft 2.8s ease-in-out infinite;
}

.page-fade {
  animation: fadeIn 220ms ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulseSoft {
  0%, 100% {
    transform: scale(1);
    opacity: 0.84;
  }
  50% {
    transform: scale(1.045);
    opacity: 1;
  }
}

@media (max-width: 760px) {
  .search-shell {
    align-items: stretch;
    flex-direction: column;
  }

  .search-shell input,
  .search-shell button {
    width: 100%;
  }

  .manuscript-page {
    min-height: 230px;
  }
}
</style>
