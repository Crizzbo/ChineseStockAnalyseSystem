/**
 * 内存缓存工具类
 * 用于缓存API响应数据，提高应用性能
 */

interface CacheItem<T> {
  data: T
  timestamp: number
  ttl: number
}

class MemoryCache {
  private cache: Map<string, CacheItem<any>> = new Map()
  private maxSize: number = 100 // 最大缓存条目数
  private defaultTTL: number = 5 * 60 * 1000 // 默认5分钟过期

  constructor(maxSize?: number, defaultTTL?: number) {
    if (maxSize) this.maxSize = maxSize
    if (defaultTTL) this.defaultTTL = defaultTTL

    // 定期清理过期缓存
    setInterval(() => {
      this.cleanup()
    }, 60 * 1000) // 每分钟清理一次
  }

  /**
   * 设置缓存
   * @param key 缓存键
   * @param data 缓存数据
   * @param ttl 过期时间（毫秒），可选
   */
  set<T>(key: string, data: T, ttl?: number): void {
    // 如果缓存已满，删除最旧的项
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    }

    this.cache.set(key, item)
  }

  /**
   * 获取缓存
   * @param key 缓存键
   * @returns 缓存数据或null
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key)

    if (!item) {
      return null
    }

    // 检查是否过期
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data as T
  }

  /**
   * 删除缓存
   * @param key 缓存键
   */
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * 检查是否存在有效缓存
   * @param key 缓存键
   */
  has(key: string): boolean {
    const item = this.cache.get(key)

    if (!item) {
      return false
    }

    // 检查是否过期
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  /**
   * 获取缓存统计信息
   */
  getStats(): { size: number; maxSize: number; keys: string[] } {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      keys: Array.from(this.cache.keys())
    }
  }

  /**
   * 清理过期缓存
   */
  private cleanup(): void {
    const now = Date.now()

    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key)
      }
    }
  }
}

// 创建全局缓存实例
export const apiCache = new MemoryCache(200, 5 * 60 * 1000) // 200个项目，5分钟过期
export const stockDataCache = new MemoryCache(100, 30 * 1000) // 100个项目，30秒过期（实时数据）
export const userDataCache = new MemoryCache(50, 10 * 60 * 1000) // 50个项目，10分钟过期

/**
 * 缓存装饰器函数，用于包装API调用
 * @param cache 缓存实例
 * @param keyGenerator 键生成函数
 * @param ttl 过期时间
 */
export function withCache<TArgs extends any[], TReturn>(
  cache: MemoryCache,
  keyGenerator: (...args: TArgs) => string,
  ttl?: number
) {
  return function (
    target: any,
    propertyName: string,
    descriptor: TypedPropertyDescriptor<(...args: TArgs) => Promise<TReturn>>
  ) {
    const method = descriptor.value!

    descriptor.value = async function (...args: TArgs): Promise<TReturn> {
      const cacheKey = keyGenerator(...args)

      // 尝试从缓存获取
      const cached = cache.get<TReturn>(cacheKey)
      if (cached !== null) {
        return cached
      }

      // 调用原方法
      const result = await method.apply(this, args)

      // 缓存结果
      cache.set(cacheKey, result, ttl)

      return result
    }
  }
}

/**
 * 简单的缓存包装函数
 * @param fn 要缓存的异步函数
 * @param cache 缓存实例
 * @param keyGenerator 键生成函数
 * @param ttl 过期时间
 */
export function cacheWrapper<TArgs extends any[], TReturn>(
  fn: (...args: TArgs) => Promise<TReturn>,
  cache: MemoryCache,
  keyGenerator: (...args: TArgs) => string,
  ttl?: number
) {
  return async (...args: TArgs): Promise<TReturn> => {
    const cacheKey = keyGenerator(...args)

    // 尝试从缓存获取
    const cached = cache.get<TReturn>(cacheKey)
    if (cached !== null) {
      return cached
    }

    // 调用原函数
    const result = await fn(...args)

    // 缓存结果
    cache.set(cacheKey, result, ttl)

    return result
  }
}

export default MemoryCache