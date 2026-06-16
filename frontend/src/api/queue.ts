import { apiClient } from './client'
import type { NewsItem } from './news'

export interface QueueItem extends NewsItem {
  queueTime: string
}

export interface QueueList {
  list: QueueItem[]
  total: number
  hasMore: boolean
}

export const queueApi = {
  check: (newsId: number) =>
    apiClient.get<{ inQueue: boolean }>(`/api/queue/check?newsId=${newsId}`, true),

  add: (newsId: number) =>
    apiClient.post<null>('/api/queue/add', { newsId }, true),

  remove: (newsId: number) =>
    apiClient.delete<null>(`/api/queue/remove?newsId=${newsId}`, true),

  getList: (page = 1, pageSize = 10) =>
    apiClient.get<QueueList>(`/api/queue/list?page=${page}&pageSize=${pageSize}`, true),

  clear: () =>
    apiClient.delete<null>('/api/queue/clear', true),
}
