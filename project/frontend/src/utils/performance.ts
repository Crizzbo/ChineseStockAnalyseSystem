/**
 * 性能监控工具
 * 用于监控组件渲染性能、API调用性能等
 */
import React from 'react'

interface PerformanceMetric {
  name: string
  startTime: number
  endTime?: number
  duration?: number
  metadata?: Record<string, any>
}

class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetric> = new Map()
  private isEnabled: boolean = process.env.NODE_ENV === 'development'

  constructor(enabled?: boolean) {
    if (enabled !== undefined) {
      this.isEnabled = enabled
    }
  }

  /**
   * 开始性能测量
   * @param name 测量名称
   * @param metadata 附加元数据
   */
  start(name: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return

    const metric: PerformanceMetric = {
      name,
      startTime: performance.now(),
      metadata
    }

    this.metrics.set(name, metric)
  }

  /**
   * 结束性能测量
   * @param name 测量名称
   * @returns 测量时长
   */
  end(name: string): number | null {
    if (!this.isEnabled) return null

    const metric = this.metrics.get(name)
    if (!metric) {
      console.warn(`Performance metric "${name}" not found`)
      return null
    }

    const endTime = performance.now()
    const duration = endTime - metric.startTime

    metric.endTime = endTime
    metric.duration = duration

    // 输出性能信息
    this.logMetric(metric)

    return duration
  }

  /**
   * 测量函数执行时间
   * @param name 测量名称
   * @param fn 要测量的函数
   * @param metadata 附加元数据
   */
  async measure<T>(
    name: string,
    fn: () => Promise<T> | T,
    metadata?: Record<string, any>
  ): Promise<T> {
    this.start(name, metadata)

    try {
      const result = await fn()
      this.end(name)
      return result
    } catch (error) {
      this.end(name)
      throw error
    }
  }

  /**
   * 输出性能指标
   * @param metric 性能指标
   */
  private logMetric(metric: PerformanceMetric): void {
    const { name, duration, metadata } = metric

    if (duration === undefined) return

    const level = this.getLogLevel(duration)
    const color = this.getColor(level)

    console.log(
      `%c⚡ Performance: ${name} - ${duration.toFixed(2)}ms`,
      `color: ${color}; font-weight: bold;`,
      metadata ? metadata : ''
    )

    // 如果性能较差，输出警告
    if (level === 'warning' || level === 'error') {
      console.warn(`Performance warning: ${name} took ${duration.toFixed(2)}ms`)
    }
  }

  /**
   * 根据执行时间获取日志级别
   * @param duration 执行时间
   */
  private getLogLevel(duration: number): 'info' | 'warning' | 'error' {
    if (duration < 100) return 'info'
    if (duration < 500) return 'warning'
    return 'error'
  }

  /**
   * 根据日志级别获取颜色
   * @param level 日志级别
   */
  private getColor(level: string): string {
    switch (level) {
      case 'info':
        return '#52c41a'
      case 'warning':
        return '#faad14'
      case 'error':
        return '#ff4d4f'
      default:
        return '#1890ff'
    }
  }

  /**
   * 获取所有性能指标
   */
  getMetrics(): PerformanceMetric[] {
    return Array.from(this.metrics.values())
  }

  /**
   * 清除所有性能指标
   */
  clear(): void {
    this.metrics.clear()
  }

  /**
   * 获取性能统计
   */
  getStats(): {
    total: number
    average: number
    min: number
    max: number
    metrics: PerformanceMetric[]
  } {
    const completed = Array.from(this.metrics.values()).filter(m => m.duration !== undefined)
    const durations = completed.map(m => m.duration!).filter(d => d > 0)

    if (durations.length === 0) {
      return {
        total: 0,
        average: 0,
        min: 0,
        max: 0,
        metrics: []
      }
    }

    return {
      total: durations.length,
      average: durations.reduce((a, b) => a + b, 0) / durations.length,
      min: Math.min(...durations),
      max: Math.max(...durations),
      metrics: completed
    }
  }
}

// 创建全局性能监控实例
export const performanceMonitor = new PerformanceMonitor()

/**
 * 性能监控装饰器
 * @param name 监控名称
 * @param metadata 附加元数据
 */
export function measurePerformance(name?: string, metadata?: Record<string, any>) {
  return function (
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
  ) {
    const method = descriptor.value
    const metricName = name || `${target.constructor.name}.${propertyName}`

    descriptor.value = async function (...args: any[]) {
      return performanceMonitor.measure(
        metricName,
        () => method.apply(this, args),
        metadata
      )
    }
  }
}

/**
 * React组件性能监控Hook
 * @param componentName 组件名称
 */
export function usePerformanceMonitor(componentName: string) {
  const renderStart = React.useRef<number>()

  // 渲染开始
  React.useLayoutEffect(() => {
    renderStart.current = performance.now()
  })

  // 渲染完成
  React.useEffect(() => {
    if (renderStart.current) {
      const duration = performance.now() - renderStart.current
      performanceMonitor.logMetric({
        name: `${componentName} Render`,
        startTime: renderStart.current,
        endTime: performance.now(),
        duration
      } as any)
    }
  })
}

/**
 * 监控API调用性能
 * @param apiName API名称
 * @param apiCall API调用函数
 * @param metadata 附加元数据
 */
export async function measureApiCall<T>(
  apiName: string,
  apiCall: () => Promise<T>,
  metadata?: Record<string, any>
): Promise<T> {
  return performanceMonitor.measure(
    `API: ${apiName}`,
    apiCall,
    metadata
  )
}

/**
 * 获取页面性能指标
 */
export function getPagePerformance(): {
  navigationTiming: PerformanceNavigationTiming | null
  paintMetrics: PerformanceEntry[]
  resourceTimings: PerformanceEntry[]
} {
  if (typeof window === 'undefined' || !window.performance) {
    return {
      navigationTiming: null,
      paintMetrics: [],
      resourceTimings: []
    }
  }

  return {
    navigationTiming: performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming,
    paintMetrics: performance.getEntriesByType('paint'),
    resourceTimings: performance.getEntriesByType('resource')
  }
}

export default performanceMonitor