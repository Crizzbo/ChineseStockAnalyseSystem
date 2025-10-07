import { useEffect, useState, useCallback, useRef } from 'react'
import { websocketService, type StockPriceUpdate, type MarketStatus, type WebSocketMessage } from '@utils/websocket'

export interface UseWebSocketOptions {
  autoConnect?: boolean
  reconnectOnClose?: boolean
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const { autoConnect = true, reconnectOnClose = true } = options
  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState('disconnected')
  const [lastError, setLastError] = useState<Error | null>(null)

  useEffect(() => {
    const updateConnectionState = () => {
      const state = websocketService.getConnectionState()
      setConnectionState(state)
      setIsConnected(state === 'connected')
    }

    const handleConnect = () => {
      updateConnectionState()
      setLastError(null)
    }

    const handleDisconnect = () => {
      updateConnectionState()
    }

    const handleError = (error: Error) => {
      setLastError(error)
      updateConnectionState()
    }

    // 监听连接状态变化
    const unsubscribeConnect = websocketService.on('connected', handleConnect)
    const unsubscribeDisconnect = websocketService.on('disconnected', handleDisconnect)
    const unsubscribeError = websocketService.on('error', handleError)

    // 自动连接
    if (autoConnect) {
      websocketService.connect().catch(handleError)
    }

    // 定期更新连接状态
    const stateInterval = setInterval(updateConnectionState, 1000)

    return () => {
      unsubscribeConnect()
      unsubscribeDisconnect()
      unsubscribeError()
      clearInterval(stateInterval)
    }
  }, [autoConnect, reconnectOnClose])

  const connect = useCallback(async () => {
    try {
      await websocketService.connect()
      setLastError(null)
    } catch (error) {
      setLastError(error instanceof Error ? error : new Error(String(error)))
      throw error
    }
  }, [])

  const disconnect = useCallback(() => {
    websocketService.disconnect()
  }, [])

  const subscribe = useCallback((symbol: string) => {
    websocketService.subscribe(symbol)
  }, [])

  const unsubscribe = useCallback((symbol: string) => {
    websocketService.unsubscribe(symbol)
  }, [])

  return {
    isConnected,
    connectionState,
    lastError,
    connect,
    disconnect,
    subscribe,
    unsubscribe
  }
}

export const useStockPrice = (symbol?: string) => {
  const [priceData, setPriceData] = useState<StockPriceUpdate | null>(null)
  const [allPrices, setAllPrices] = useState<Map<string, StockPriceUpdate>>(new Map())
  const { isConnected, subscribe, unsubscribe } = useWebSocket()

  useEffect(() => {
    const handlePriceUpdate = (update: StockPriceUpdate) => {
      setAllPrices(prev => new Map(prev.set(update.symbol, update)))

      if (!symbol || update.symbol === symbol) {
        setPriceData(update)
      }
    }

    const unsubscribePriceUpdate = websocketService.on('price_update', handlePriceUpdate)

    // 如果指定了股票代码，订阅该股票的价格更新
    if (symbol && isConnected) {
      subscribe(symbol)
    }

    return () => {
      unsubscribePriceUpdate()
      if (symbol && isConnected) {
        unsubscribe(symbol)
      }
    }
  }, [symbol, isConnected, subscribe, unsubscribe])

  const getPrice = useCallback((stockSymbol: string) => {
    return allPrices.get(stockSymbol) || null
  }, [allPrices])

  const getPrices = useCallback((symbols: string[]) => {
    return symbols.map(s => allPrices.get(s)).filter(Boolean) as StockPriceUpdate[]
  }, [allPrices])

  return {
    priceData,
    allPrices,
    getPrice,
    getPrices,
    isConnected
  }
}

export const useMarketStatus = () => {
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null)
  const { isConnected } = useWebSocket()

  useEffect(() => {
    const handleMarketStatus = (status: MarketStatus) => {
      setMarketStatus(status)
    }

    const unsubscribeMarketStatus = websocketService.on('market_status', handleMarketStatus)

    return () => {
      unsubscribeMarketStatus()
    }
  }, [isConnected])

  return {
    marketStatus,
    isConnected
  }
}

export const useWebSocketMessages = () => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const [latestMessage, setLatestMessage] = useState<WebSocketMessage | null>(null)
  const messagesRef = useRef<WebSocketMessage[]>([])

  useEffect(() => {
    const handleMessage = (message: WebSocketMessage) => {
      const newMessages = [...messagesRef.current, message].slice(-100) // 只保留最近100条消息
      messagesRef.current = newMessages
      setMessages(newMessages)
      setLatestMessage(message)
    }

    const unsubscribeMessage = websocketService.on('message', handleMessage)

    return () => {
      unsubscribeMessage()
    }
  }, [])

  const clearMessages = useCallback(() => {
    messagesRef.current = []
    setMessages([])
    setLatestMessage(null)
  }, [])

  return {
    messages,
    latestMessage,
    clearMessages
  }
}

export default useWebSocket