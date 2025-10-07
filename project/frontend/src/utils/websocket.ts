export interface WebSocketMessage {
  type: 'price_update' | 'market_status' | 'news' | 'error'
  data: any
  timestamp: number
}

export interface StockPriceUpdate {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: number
}

export interface MarketStatus {
  status: 'open' | 'closed' | 'pre_market' | 'after_hours'
  timestamp: number
}

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private listeners: Map<string, Set<Function>> = new Map()
  private isConnecting = false
  private heartbeatInterval: number | null = null

  constructor(url: string = 'ws://localhost:8080/ws') {
    this.url = url
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
        return
      }

      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      this.isConnecting = true

      try {
        // 在开发环境中模拟WebSocket连接
        if (import.meta.env.DEV) {
          this.simulateWebSocket()
          this.isConnecting = false
          resolve()
          return
        }

        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnecting = false
          this.stopHeartbeat()

          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  private simulateWebSocket() {
    console.log('Simulating WebSocket connection for development')

    // 模拟连接成功
    setTimeout(() => {
      this.emit('connected', null)
    }, 100)

    // 模拟定期价格更新
    const symbols = ['000001', '600519', '000858', '600036', '000002']

    setInterval(() => {
      const symbol = symbols[Math.floor(Math.random() * symbols.length)]
      const basePrice = this.getBasePrice(symbol)
      const change = (Math.random() - 0.5) * 2
      const price = basePrice + change
      const changePercent = (change / basePrice) * 100

      const update: StockPriceUpdate = {
        symbol,
        price: Number(price.toFixed(2)),
        change: Number(change.toFixed(2)),
        changePercent: Number(changePercent.toFixed(2)),
        volume: Math.floor(Math.random() * 100000000),
        timestamp: Date.now()
      }

      this.handleMessage({
        type: 'price_update',
        data: update,
        timestamp: Date.now()
      })
    }, 2000)

    // 模拟市场状态更新
    setInterval(() => {
      const marketStatus: MarketStatus = {
        status: this.getCurrentMarketStatus(),
        timestamp: Date.now()
      }

      this.handleMessage({
        type: 'market_status',
        data: marketStatus,
        timestamp: Date.now()
      })
    }, 30000)
  }

  private getBasePrice(symbol: string): number {
    const prices: Record<string, number> = {
      '000001': 12.45,
      '600519': 1650.00,
      '000858': 168.50,
      '600036': 42.18,
      '000002': 18.96
    }
    return prices[symbol] || 10.00
  }

  private getCurrentMarketStatus(): 'open' | 'closed' | 'pre_market' | 'after_hours' {
    const now = new Date()
    const hour = now.getHours()
    const minute = now.getMinutes()
    const time = hour * 100 + minute

    if (time >= 930 && time < 1130) return 'open'
    if (time >= 1300 && time < 1500) return 'open'
    if (time >= 900 && time < 930) return 'pre_market'
    if (time >= 1500 && time < 1600) return 'after_hours'
    return 'closed'
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
    this.stopHeartbeat()
  }

  private startHeartbeat() {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))
      }
    }, 30000)
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private scheduleReconnect() {
    setTimeout(() => {
      this.reconnectAttempts++
      console.log(`WebSocket reconnection attempt ${this.reconnectAttempts}`)
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      })
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts))
  }

  private handleMessage(message: WebSocketMessage) {
    this.emit(message.type, message.data)
    this.emit('message', message)
  }

  subscribe(symbol: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        symbol
      }))
    }
  }

  unsubscribe(symbol: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        symbol
      }))
    }
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)

    // 返回取消订阅函数
    return () => {
      this.off(event, callback)
    }
  }

  off(event: string, callback: Function) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.delete(callback)
      if (eventListeners.size === 0) {
        this.listeners.delete(event)
      }
    }
  }

  private emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error)
        }
      })
    }
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected'

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting'
      case WebSocket.OPEN:
        return 'connected'
      case WebSocket.CLOSING:
        return 'closing'
      case WebSocket.CLOSED:
        return 'disconnected'
      default:
        return 'unknown'
    }
  }
}

// 单例实例
export const websocketService = new WebSocketService()

export default WebSocketService