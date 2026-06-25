<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { newsApi, type NewsItem } from '@/api/news'
import { followApi } from '@/api/follow'
import { useAuthStore } from '@/stores/authStore'
import { sourceMeta } from '@/utils/sourceMeta'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const author = ref(decodeURIComponent(route.params.name as string))
const items = ref<NewsItem[]>([])
const total = ref(0)
const page = ref(1)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const following = ref(false)
const followLoading = ref(false)

function formatDate(t: string) {
  return new Date(t).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}

const canFollow = computed(() => auth.isLoggedIn && !!author.value)

async function loadFollowState() {
  if (!canFollow.value) {
    following.value = false
    return
  }
  try {
    const res = await followApi.checkAuthor(author.value)
    following.value = res.following
  } catch {
    following.value = false
  }
}

async function toggleFollow() {
  if (!canFollow.value || followLoading.value) return
  followLoading.value = true
  try {
    if (following.value) await followApi.unfollowAuthor(author.value)
    else await followApi.followAuthor(author.value)
    following.value = !following.value
  } finally {
    followLoading.value = false
  }
}

async function load(reset = false) {
  if (reset) { page.value = 1; items.value = [] }
  loading.value = reset
  loadingMore.value = !reset
  try {
    const data = await newsApi.getByAuthor(author.value, page.value)
    if (reset) items.value = data.list
    else items.value.push(...data.list)
    total.value = data.total
    hasMore.value = data.hasMore
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value) return
  page.value++
  await load(false)
}

onMounted(() => load(true))
watch(() => auth.isLoggedIn, () => loadFollowState(), { immediate: true })
watch(() => route.params.name, (v) => {
  author.value = decodeURIComponent(v as string)
  load(true)
  loadFollowState()
})
</script>

<template>
  <div class="author-page">
    <header class="author-header">
      <button class="back-btn" aria-label="返回" title="返回" @click="router.back()">←</button>
      <div class="author-info">
        <div class="author-avatar">{{ author.charAt(0).toUpperCase() }}</div>
        <div>
          <div class="author-name">{{ author }}</div>
          <div class="author-count">{{ total }} 篇文章</div>
        </div>
      </div>
      <button v-if="canFollow" class="follow-btn" :class="{ active: following }" :disabled="followLoading"
        :aria-label="following ? '取消关注作者' : '关注作者'"
        :title="following ? '取消关注作者' : '关注作者'"
        @click="toggleFollow">
        {{ followLoading ? '处理中…' : (following ? '已关注' : '关注作者') }}
      </button>
    </header>

    <div class="article-list">
      <div v-if="loading" class="loading-tip">加载中…</div>

      <template v-else>
        <RouterLink
          v-for="item in items"
          :key="item.id"
          class="article-card"
          :to="`/news/detail/${item.id}`"
        >
          <div class="card-main">
            <div
              class="source-tag"
              :style="{ color: sourceMeta(item.source_platform).color, borderColor: sourceMeta(item.source_platform).color }"
            >{{ sourceMeta(item.source_platform).label }}</div>
            <div class="card-title">{{ item.title_zh || item.title }}</div>
            <div class="card-meta">
              <span>{{ formatDate(item.publish_time) }}</span>
              <span class="sep">·</span>
              <span>{{ item.views }} 阅读</span>
            </div>
          </div>
          <img v-if="item.image" class="card-img" :src="item.image" :alt="item.title" loading="lazy" />
        </RouterLink>

        <div v-if="items.length === 0" class="empty-tip">该作者暂无文章</div>

        <button v-if="hasMore" class="load-more" :disabled="loadingMore" @click="loadMore">
          {{ loadingMore ? '加载中…' : '加载更多' }}
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.author-page { max-width: 720px; margin: 0 auto; padding: 0 16px 40px; }

.author-header {
  display: flex; align-items: center; gap: 14px;
  padding: 20px 0 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.back-btn {
  background: none; border: none; cursor: pointer;
  font-size: 20px; color: var(--text-secondary); padding: 0 4px;
  line-height: 1;
}
.back-btn:hover { color: var(--text-primary); }
.author-info { display: flex; align-items: center; gap: 14px; }
.author-avatar {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--accent); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Libre Baskerville', serif;
  font-size: 20px; font-weight: 700; flex-shrink: 0;
}
.author-name { font-family: 'Libre Baskerville', serif; font-size: 18px; font-weight: 700; color: var(--text-primary); }
.author-count { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
.follow-btn {
  margin-left: auto;
  padding: 8px 14px;
  border-radius: 18px;
  border: 1px solid var(--brand);
  background: var(--brand);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}
.follow-btn.active {
  background: var(--bg-card);
  color: var(--brand);
}

.article-card {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 14px 0; border-bottom: 1px solid var(--border);
  text-decoration: none; color: inherit;
}
.article-card:hover .card-title { color: var(--accent); }
.card-main { flex: 1; }
.source-tag {
  display: inline-block; font-family: 'JetBrains Mono', monospace;
  font-size: 9px; font-weight: 600; letter-spacing: .04em;
  border: 1px solid; border-radius: 3px;
  padding: 1px 5px; margin-bottom: 6px;
}
.card-title { font-size: 15px; font-weight: 600; color: var(--text-primary); line-height: 1.4; }
.card-meta { font-size: 11px; color: var(--text-muted); margin-top: 6px; }
.sep { margin: 0 5px; }
.card-img { width: 80px; height: 56px; object-fit: cover; border-radius: var(--radius-sm); flex-shrink: 0; }

.loading-tip, .empty-tip { text-align: center; color: var(--text-muted); padding: 60px 0; font-size: 14px; }
.load-more {
  display: block; width: 100%; margin-top: 20px;
  padding: 10px; border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--bg-card); color: var(--text-secondary);
  font-size: 13px; cursor: pointer;
}
.load-more:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.load-more:disabled { opacity: .5; cursor: not-allowed; }
</style>
