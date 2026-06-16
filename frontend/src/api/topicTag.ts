import { apiClient } from './client'

export interface TopicTag {
  id: number
  name: string
  slug: string
  color: string
}

export const tagApi = {
  listAll: () => apiClient.get<TopicTag[]>('/api/tags', false),
  forNews: (newsId: number) => apiClient.get<TopicTag[]>(`/api/tags/news/${newsId}`, true),
}
