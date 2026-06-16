import { apiClient } from './client'

export interface CommentUser {
  id: number
  nickname: string
  avatar: string
}

export interface CommentItem {
  id: number
  parentId: number | null
  content: string
  createdAt: string
  user: CommentUser
}

export interface CommentList {
  list: CommentItem[]
  total: number
  hasMore: boolean
}

export const commentApi = {
  list: (newsId: number, page = 1, pageSize = 20) =>
    apiClient.get<CommentList>(`/api/comments?news_id=${newsId}&page=${page}&pageSize=${pageSize}`),

  create: (newsId: number, content: string, parentId?: number) =>
    apiClient.post<CommentItem>('/api/comments', { news_id: newsId, content, parent_id: parentId ?? null }, true),

  remove: (commentId: number) =>
    apiClient.delete<null>(`/api/comments/${commentId}`, true),
}
