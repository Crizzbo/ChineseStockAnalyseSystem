import { useState, useEffect, useRef } from 'react'

/**
 * 防抖Hook - 用于延迟执行函数，常用于搜索输入等场景
 * @param value 需要防抖的值
 * @param delay 延迟时间（毫秒）
 * @returns 防抖后的值
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * 防抖回调Hook - 用于防抖函数调用
 * @param callback 需要防抖的函数
 * @param delay 延迟时间（毫秒）
 * @param deps 依赖数组
 * @returns 防抖后的函数
 */
export function useDebounceCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): T {
  const callbackRef = useRef(callback)
  const timerRef = useRef<NodeJS.Timeout>()

  // 更新回调函数引用
  useEffect(() => {
    callbackRef.current = callback
  }, [callback, ...deps])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [])

  const debouncedCallback = ((...args: any[]) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }

    timerRef.current = setTimeout(() => {
      callbackRef.current(...args)
    }, delay)
  }) as T

  return debouncedCallback
}

export default useDebounce