import { defineStore } from 'pinia'
import { ref } from 'vue'
import { newsApi, type Category, type NewsItem } from '@/api/news'

export const useNewsStore = defineStore('news', () => {
  const categories = ref<Category[]>([])
  const activeSource = ref('all')
  const newsList = ref<NewsItem[]>([])
  const page = ref(1)
  const hasMore = ref(true)
  const loading = ref(false)

  async function loadCategories() {
    if (categories.value.length) return
    categories.value = await newsApi.getCategories()
    if (categories.value.length) activeSource.value = categories.value[0].id
  }

  async function loadNews(source: string, reset = false) {
    if (loading.value) return
    if (reset) {
      newsList.value = []
      page.value = 1
      hasMore.value = true
    }
    if (!hasMore.value) return
    loading.value = true
    try {
      const res = await newsApi.getList(source, page.value)
      newsList.value = reset ? res.list : [...newsList.value, ...res.list]
      hasMore.value = res.hasMore
      page.value++
    } finally {
      loading.value = false
    }
  }

  function setCategory(id: string) {
    activeSource.value = id
    loadNews(id, true)
  }

  return { categories, activeSource, newsList, page, hasMore, loading, loadCategories, loadNews, setCategory }
})
