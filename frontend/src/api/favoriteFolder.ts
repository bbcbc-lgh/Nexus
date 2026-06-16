import { apiClient } from './client'

export interface FolderItem {
  id: number
  name: string
  createdAt: string
  count: number
}

export interface FolderList {
  list: FolderItem[]
  unfiledCount: number
}

export const folderApi = {
  list: () =>
    apiClient.get<FolderList>('/api/favorite/folder/list', true),

  create: (name: string) =>
    apiClient.post<{ id: number; name: string; createdAt: string }>(
      '/api/favorite/folder/create', { name }, true,
    ),

  rename: (folderId: number, name: string) =>
    apiClient.put<null>(`/api/favorite/folder/${folderId}/rename`, { name }, true),

  remove: (folderId: number) =>
    apiClient.delete<null>(`/api/favorite/folder/${folderId}`, true),

  move: (newsId: number, folderId: number | null) =>
    apiClient.post<null>('/api/favorite/folder/move', { newsId, folderId }, true),
}
