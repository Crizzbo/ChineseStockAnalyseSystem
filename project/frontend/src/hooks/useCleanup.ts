import { useEffect, useRef, useCallback } from 'react'

/**
 * 清理Hook - 用于防止内存泄漏和清理资源
 */

type CleanupFunction = () => void

export function useCleanup() {
  const cleanupFunctions = useRef<CleanupFunction[]>([])
  const isUnmountedRef = useRef(false)

  /**
   * 添加清理函数
   * @param cleanup 清理函数
   */
  const addCleanup = useCallback((cleanup: CleanupFunction) => {
    cleanupFunctions.current.push(cleanup)
  }, [])

  /**
   * 检查组件是否已卸载
   */
  const isUnmounted = useCallback(() => {
    return isUnmountedRef.current
  }, [])

  /**
   * 安全的状态更新 - 仅在组件未卸载时执行
   * @param updateFunction 状态更新函数
   */
  const safeUpdate = useCallback((updateFunction: () => void) => {
    if (!isUnmountedRef.current) {
      updateFunction()
    }
  }, [])

  /**
   * 手动执行所有清理函数
   */
  const cleanup = useCallback(() => {
    cleanupFunctions.current.forEach(fn => {
      try {
        fn()
      } catch (error) {
        console.error('清理函数执行失败:', error)
      }
    })
    cleanupFunctions.current = []
  }, [])

  // 组件卸载时执行清理
  useEffect(() => {
    return () => {
      isUnmountedRef.current = true
      cleanup()
    }
  }, [cleanup])

  return {
    addCleanup,
    isUnmounted,
    safeUpdate,
    cleanup
  }
}

/**
 * 定时器Hook - 自动清理定时器
 * @param callback 回调函数
 * @param delay 延迟时间（毫秒）
 * @param immediate 是否立即执行
 */
export function useInterval(
  callback: () => void,
  delay: number | null,
  immediate = false
) {
  const { addCleanup, isUnmounted } = useCleanup()
  const callbackRef = useRef(callback)

  // 更新回调函数引用
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  useEffect(() => {
    if (delay === null) return

    const wrappedCallback = () => {
      if (!isUnmounted()) {
        callbackRef.current()
      }
    }

    if (immediate) {
      wrappedCallback()
    }

    const interval = setInterval(wrappedCallback, delay)

    addCleanup(() => {
      clearInterval(interval)
    })

    return () => {
      clearInterval(interval)
    }
  }, [delay, immediate, addCleanup, isUnmounted])
}

/**
 * 超时Hook - 自动清理超时器
 * @param callback 回调函数
 * @param delay 延迟时间（毫秒）
 */
export function useTimeout(callback: () => void, delay: number | null) {
  const { addCleanup, isUnmounted } = useCleanup()
  const callbackRef = useRef(callback)

  // 更新回调函数引用
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  useEffect(() => {
    if (delay === null) return

    const timeout = setTimeout(() => {
      if (!isUnmounted()) {
        callbackRef.current()
      }
    }, delay)

    addCleanup(() => {
      clearTimeout(timeout)
    })

    return () => {
      clearTimeout(timeout)
    }
  }, [delay, addCleanup, isUnmounted])
}

/**
 * 事件监听器Hook - 自动清理事件监听器
 * @param target 目标元素
 * @param eventType 事件类型
 * @param listener 事件监听器
 * @param options 选项
 */
export function useEventListener<T extends EventTarget>(
  target: T | null,
  eventType: string,
  listener: EventListener,
  options?: AddEventListenerOptions
) {
  const { addCleanup, isUnmounted } = useCleanup()
  const listenerRef = useRef(listener)

  // 更新监听器引用
  useEffect(() => {
    listenerRef.current = listener
  }, [listener])

  useEffect(() => {
    if (!target) return

    const wrappedListener: EventListener = (event) => {
      if (!isUnmounted()) {
        listenerRef.current(event)
      }
    }

    target.addEventListener(eventType, wrappedListener, options)

    addCleanup(() => {
      target.removeEventListener(eventType, wrappedListener, options)
    })

    return () => {
      target.removeEventListener(eventType, wrappedListener, options)
    }
  }, [target, eventType, options, addCleanup, isUnmounted])
}

/**
 * WebSocket Hook - 自动清理WebSocket连接
 * @param url WebSocket URL
 * @param onMessage 消息处理函数
 * @param onError 错误处理函数
 */
export function useWebSocket(
  url: string | null,
  onMessage?: (event: MessageEvent) => void,
  onError?: (event: Event) => void
) {
  const { addCleanup, isUnmounted } = useCleanup()
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!url) return

    const ws = new WebSocket(url)
    wsRef.current = ws

    const handleMessage = (event: MessageEvent) => {
      if (!isUnmounted() && onMessage) {
        onMessage(event)
      }
    }

    const handleError = (event: Event) => {
      if (!isUnmounted() && onError) {
        onError(event)
      }
    }

    ws.addEventListener('message', handleMessage)
    ws.addEventListener('error', handleError)

    addCleanup(() => {
      ws.removeEventListener('message', handleMessage)
      ws.removeEventListener('error', handleError)
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    })

    return () => {
      ws.removeEventListener('message', handleMessage)
      ws.removeEventListener('error', handleError)
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    }
  }, [url, onMessage, onError, addCleanup, isUnmounted])

  const sendMessage = useCallback((message: string | ArrayBufferLike | Blob | ArrayBufferView) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && !isUnmounted()) {
      wsRef.current.send(message)
    }
  }, [isUnmounted])

  return {
    sendMessage,
    readyState: wsRef.current?.readyState
  }
}

/**
 * 异步操作Hook - 防止在组件卸载后更新状态
 * @param asyncOperation 异步操作
 */
export function useAsyncOperation<T>(
  asyncOperation: () => Promise<T>
): [() => Promise<T | null>, boolean] {
  const { isUnmounted } = useCleanup()

  const execute = useCallback(async (): Promise<T | null> => {
    try {
      const result = await asyncOperation()
      if (isUnmounted()) {
        return null
      }
      return result
    } catch (error) {
      if (!isUnmounted()) {
        throw error
      }
      return null
    }
  }, [asyncOperation, isUnmounted])

  return [execute, isUnmounted()]
}

export default useCleanup