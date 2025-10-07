/**
 * WebSocket 连接服务
 */
import { io, Socket } from 'socket.io-client'
import { message } from 'antd'
import { type StockInfo, type MarketIndex } from './api'
import authService from './auth'

export interface WebSocketConfig {
  url?: string
  autoReconnect?: boolean
  reconnectAttempts?: number
  reconnectDelay?: number
}

export interface StockDataUpdate {
  type: 'current' | 'update'
  data: { [symbol: string]: StockInfo }
  timestamp: string
}

export interface MarketDataUpdate {
  type: 'current' | 'update'
  data: MarketIndex[]
  timestamp: string
}

export interface SubscriptionStatus {
  status: 'subscribed' | 'unsubscribed'
  symbols?: string[]
  type?: string
  timestamp: string
}

export interface ConnectionStatus {
  status: 'connected' | 'disconnected'
  client_id?: string
  timestamp: string
}

export interface ClientInfo {
  client_id: string
  connected_at: string
  subscriptions: string[]
  timestamp: string
}

class WebSocketService {
  private socket: Socket | null = null
  private config: WebSocketConfig
  private reconnectAttempts = 0
  private isConnected = false
  private eventHandlers: { [event: string]: Function[] } = {}

  constructor(config: WebSocketConfig = {}) {
    this.config = {
      url: config.url || 'http://localhost:5000',
      autoReconnect: config.autoReconnect !== false,
      reconnectAttempts: config.reconnectAttempts || 5,
      reconnectDelay: config.reconnectDelay || 3000,
      ...config
    }
  }

  /**
   * 连接WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket && this.isConnected) {
        resolve()
        return
      }

      const auth: any = {}
      const token = authService.getAccessToken()
      if (token) {
        auth.token = token
      }

      this.socket = io(this.config.url!, {
        auth,
        transports: ['websocket', 'polling'],
        upgrade: true,
        rememberUpgrade: true
      })

      // 连接事件
      this.socket.on('connect', () => {
        console.log('WebSocket连接成功')
        this.isConnected = true
        this.reconnectAttempts = 0
        resolve()
      })

      // 连接错误事件
      this.socket.on('connect_error', (error: any) => {
        console.error('WebSocket连接错误:', error)
        this.isConnected = false

        if (this.reconnectAttempts < this.config.reconnectAttempts!) {
          console.log(`尝试重连... (${this.reconnectAttempts + 1}/${this.config.reconnectAttempts})`)
          this.reconnectAttempts++
          setTimeout(() => {
            this.socket?.connect()
          }, this.config.reconnectDelay)
        } else {
          message.error('WebSocket连接失败，请检查网络')
          reject(error)
        }
      })

      // 断开连接事件
      this.socket.on('disconnect', (reason: any) => {
        console.log('WebSocket断开连接:', reason)
        this.isConnected = false

        if (reason === 'io server disconnect') {
          // 服务器主动断开，尝试重连
          if (this.config.autoReconnect) {
            setTimeout(() => {
              this.connect()
            }, this.config.reconnectDelay)
          }
        }
      })

      // 连接状态事件
      this.socket.on('connection_status', (data: ConnectionStatus) => {
        console.log('连接状态:', data)
        this.emit('connection_status', data)
      })

      // 股票数据更新事件
      this.socket.on('stock_data', (data: StockDataUpdate) => {
        this.emit('stock_data', data)
      })

      // 市场数据更新事件
      this.socket.on('market_data', (data: MarketDataUpdate) => {
        this.emit('market_data', data)
      })

      // 订阅状态事件
      this.socket.on('subscription_status', (data: SubscriptionStatus) => {
        console.log('订阅状态:', data)
        this.emit('subscription_status', data)
      })

      // 客户端信息事件
      this.socket.on('client_info', (data: ClientInfo) => {
        this.emit('client_info', data)
      })

      // 错误事件
      this.socket.on('error', (data: { message: string }) => {
        console.error('WebSocket错误:', data.message)
        message.error(data.message)
      })

      // Pong事件（心跳响应）
      this.socket.on('pong', (data: { timestamp: string }) => {
        console.debug('收到心跳响应:', data.timestamp)
      })

      // 设置连接超时
      setTimeout(() => {
        if (!this.isConnected) {
          reject(new Error('连接超时'))
        }
      }, 10000)
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
    }
  }

  /**
   * 订阅股票实时数据
   */
  subscribeStock(symbols: string[]): void {
    if (!this.isConnected || !this.socket) {
      message.warning('WebSocket未连接，请先连接')
      return
    }

    this.socket.emit('subscribe_stock', { symbols })
  }

  /**
   * 取消订阅股票实时数据
   */
  unsubscribeStock(symbols: string[]): void {
    if (!this.isConnected || !this.socket) {
      return
    }

    this.socket.emit('unsubscribe_stock', { symbols })
  }

  /**
   * 订阅市场指数数据
   */
  subscribeMarket(): void {
    if (!this.isConnected || !this.socket) {
      message.warning('WebSocket未连接，请先连接')
      return
    }

    this.socket.emit('subscribe_market', {})
  }

  /**
   * 取消订阅市场指数数据
   */
  unsubscribeMarket(): void {
    if (!this.isConnected || !this.socket) {
      return
    }

    this.socket.emit('unsubscribe_market')
  }

  /**
   * 获取客户端信息
   */
  getClientInfo(): void {
    if (!this.isConnected || !this.socket) {
      return
    }

    this.socket.emit('get_client_info')
  }

  /**
   * 发送心跳
   */
  ping(): void {
    if (!this.isConnected || !this.socket) {
      return
    }

    this.socket.emit('ping')
  }

  /**
   * 添加事件监听器
   */
  on(event: string, handler: Function): void {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = []
    }
    this.eventHandlers[event].push(handler)
  }

  /**
   * 移除事件监听器
   */
  off(event: string, handler?: Function): void {
    if (!this.eventHandlers[event]) {
      return
    }

    if (handler) {
      const index = this.eventHandlers[event].indexOf(handler)
      if (index > -1) {
        this.eventHandlers[event].splice(index, 1)
      }
    } else {
      this.eventHandlers[event] = []
    }
  }

  /**
   * 触发事件
   */
  private emit(event: string, data: any): void {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`事件处理器执行错误 (${event}):`, error)
        }
      })
    }
  }

  /**
   * 检查连接状态
   */
  isSocketConnected(): boolean {
    return this.isConnected && this.socket?.connected === true
  }

  /**
   * 获取连接状态
   */
  getConnectionState(): {
    connected: boolean
    socket_id?: string
    transport?: string
  } {
    return {
      connected: this.isConnected,
      socket_id: this.socket?.id,
      transport: this.socket?.io.engine?.transport?.name
    }
  }
}

// 创建全局实例
export const webSocketService = new WebSocketService()

// 自动连接（可选）
// webSocketService.connect().catch(console.error)

export default webSocketService