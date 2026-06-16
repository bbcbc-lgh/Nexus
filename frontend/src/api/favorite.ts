import { apiClient } from './client'
import type { NewsItem } from './news'

export interface FavoriteItem extends NewsItem {
  favoriteTime: string
  folderId: number | null
}

export interface FavoriteList {
  list: FavoriteItem[]
  total: number
  hasMore: boolean
}

export const favoriteApi = {
  check: (newsId: number) =>
    apiClient.get<{ isFavorite: boolean }>(`/api/favorite/check?newsId=${newsId}`, true),

  add: (newsId: number) =>
    apiClient.post<null>('/api/favorite/add', { newsId }, true),

  remove: (newsId: number) =>
    apiClient.delete<null>(`/api/favorite/remove?newsId=${newsId}`, true),

  getList: (page = 1, pageSize = 10, folder: string = 'all') =>
    apiClient.get<FavoriteList>(`/api/favorite/list?page=${page}&pageSize=${pageSize}&folder=${folder}`, true),

  clear: () =>
    apiClient.delete<null>('/api/favorite/clear', true)
}
