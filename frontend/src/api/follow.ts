import { apiClient } from './client'

export interface FollowedAuthor {
  author: string
  createdAt: string
}

export const followApi = {
  listAuthors: () =>
    apiClient.get<{ list: FollowedAuthor[] }>('/api/follow/authors', true),

  checkAuthor: (author: string) =>
    apiClient.get<{ following: boolean }>(`/api/follow/author/check?author=${encodeURIComponent(author)}`, true),

  followAuthor: (author: string) =>
    apiClient.post<null>('/api/follow/author', { author }, true),

  unfollowAuthor: (author: string) =>
    apiClient.delete<null>(`/api/follow/author?author=${encodeURIComponent(author)}`, true),
}
