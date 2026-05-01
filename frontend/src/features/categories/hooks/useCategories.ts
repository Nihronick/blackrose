import { useSuspenseQuery } from '@tanstack/react-query'
import { categoriesApi } from '../api'

export const keys = {
  all: ['categories'] as const,
}

export const useCategories = () => {
  return useSuspenseQuery({
    queryKey: keys.all,
    queryFn: async () => {
      const result = await categoriesApi.list()()
      if (result._tag === 'Left') throw result.left
      return result.right
    },
    staleTime: 60_000,
  })
}
