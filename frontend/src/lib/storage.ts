// @ts-nocheck
const tg = window.Telegram?.WebApp

/**
 * Universal storage helper for Telegram CloudStorage and LocalStorage.
 */
export const storage = {
  get: (key: string): Promise<string | null> => {
    return new Promise((resolve) => {
      if (tg?.isVersionAtLeast && tg.isVersionAtLeast('6.9') && tg?.CloudStorage) {
        try {
          tg.CloudStorage.getItem(key, (err: Error | null, val: string | null) =>
            resolve(err ? null : (val ?? null))
          )
        } catch {
          resolve(localStorage.getItem(key))
        }
      } else {
        try {
          resolve(localStorage.getItem(key))
        } catch {
          resolve(null)
        }
      }
    })
  },

  set: (key: string, value: string): Promise<boolean> => {
    return new Promise((resolve) => {
      if (tg?.isVersionAtLeast && tg.isVersionAtLeast('6.9') && tg?.CloudStorage) {
        try {
          tg.CloudStorage.setItem(key, value, (err: Error | null) => resolve(!err))
        } catch {
          try {
            localStorage.setItem(key, value)
            resolve(true)
          } catch {
            resolve(false)
          }
        }
      } else {
        try {
          localStorage.setItem(key, value)
          resolve(true)
        } catch {
          resolve(false)
        }
      }
    })
  },
}
