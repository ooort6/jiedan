// 获取Element Plus组件
const { ElMessage, ElTabs, ElTabPane } = ElementPlus;

// 创建Vue应用
const { createApp, ref, onMounted, watch } = Vue;

const app = createApp({
  setup() {
    // 状态数据
    const specificCoins = [
      { symbol: 'BTCUSDT', name: 'Bitcoin', baseAsset: 'BTC' },
      { symbol: 'ETHUSDT', name: 'Ethereum', baseAsset: 'ETH' },
      // { symbol: 'OKBUSDT', name: 'OKB', baseAsset: 'OKB' },
      { symbol: 'SOLUSDT', name: 'Solana', baseAsset: 'SOL' },
      { symbol: 'TONUSDT', name: 'TON', baseAsset: 'TON' },
      { symbol: 'DOGEUSDT', name: 'DOGE', baseAsset: 'DOGE' },
      { symbol: 'XRPUSDT', name: 'XRP', baseAsset: 'XRP' },
      { symbol: 'TRUMPUSDT', name: 'TRUMP', baseAsset: 'TRUMP' }
    ];
    
    const coins = ref([]);
    const coinData = ref({});
    const timeRange = ref('7'); // 默认选择7天
    const chartInstances = {};
    const loadingCharts = ref({});
    const error = ref({});

    // 获取K线间隔
    const getKlineInterval = (days) => {
      switch(days) {
        case '1': return '15m';  // 15分钟
        case '7': return '4h';   // 4小时
        case '30': return '1d';  // 1天
        default: return '4h';
      }
    };

    // 获取K线数据数量
    const getKlineLimit = (days) => {
      switch(days) {
        case '1': return 96;    // 24h/15m = 96
        case '7': return 42;    // 7d/4h = 42
        case '30': return 30;   // 30天
        default: return 42;
      }
    };

    // 获取币种最新价格
    const fetchLatestPrice = async (symbol) => {
      try {
        const response = await axios.get('https://api.binance.com/api/v3/ticker/24hr', {
          params: { symbol }
        });
        
        if (response.data) {
          coinData.value[symbol] = {
            price: parseFloat(response.data.lastPrice),
            priceChange: parseFloat(response.data.priceChangePercent),
            volume: parseFloat(response.data.volume)
          };
        }
      } catch (err) {
        console.error(`获取${symbol}最新价格失败:`, err);
      }
    };

    // 获取K线数据
    const fetchKlineData = async (symbol) => {
      try {
        loadingCharts.value[symbol] = true;
        error.value[symbol] = false;

        const interval = getKlineInterval(timeRange.value);
        const limit = getKlineLimit(timeRange.value);
        
        const response = await axios.get('https://api.binance.com/api/v3/klines', {
          params: {
            symbol: symbol,
            interval: interval,
            limit: limit
          }
        });

        if (!response.data || response.data.length === 0) {
          throw new Error('数据为空');
        }

        // 更新图表
        updateKlineChart(symbol, response.data);
        
        // 获取最新价格
        await fetchLatestPrice(symbol);
      } catch (err) {
        console.error(`获取${symbol}K线数据失败:`, err);
        error.value[symbol] = true;
        ElMessage.error(`获取${symbol}数据失败，将在下次刷新时重试`);
      } finally {
        loadingCharts.value[symbol] = false;
      }
    };

    // 更新K线图表
    const updateKlineChart = (symbol, klineData) => {
      if (chartInstances[symbol]) {
        chartInstances[symbol].destroy();
      }

      const canvasId = `chart-${symbol}`;
      const ctx = document.getElementById(canvasId);
      if (!ctx) return;

      const data = klineData.map(item => {
        const time = new Date(item[0]).toLocaleDateString('zh-CN');
        const [timestamp, open, high, low, close] = item;
        return {
          time,
          open: parseFloat(open),
          high: parseFloat(high),
          low: parseFloat(low),
          close: parseFloat(close)
        };
      });

      const labels = data.map(item => item.time);
      const prices = data.map(item => item.close);

      const startPrice = prices[0];
      const endPrice = prices[prices.length - 1];
      const isPositive = startPrice <= endPrice;

      const upColor = 'rgb(16, 185, 129)';
      const downColor = 'rgb(239, 68, 68)';
      const backgroundColor = isPositive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)';

      const coin = specificCoins.find(c => c.symbol === symbol);

      chartInstances[symbol] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: `${coin.name} (${coin.baseAsset}/USDT)`,
            data: prices,
            borderColor: isPositive ? upColor : downColor,
            backgroundColor: backgroundColor,
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: data.length > 50 ? 0 : 2,
            pointHoverRadius: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  if (context.parsed.y !== null) {
                    label += '$' + context.parsed.y.toFixed(2);
                  }
                  return label;
                }
              }
            }
          },
          scales: {
            x: {
              grid: {
                display: false
              },
              ticks: {
                maxTicksLimit: 10,
                autoSkip: true
              }
            },
            y: {
              beginAtZero: false,
              grid: {
                color: 'rgba(200, 200, 200, 0.2)'
              },
              ticks: {
                callback: function(value) {
                  return '$' + value.toFixed(2);
                }
              }
            }
          },
          interaction: {
            intersect: false,
            mode: 'index'
          }
        }
      });
    };

    // 初始化数据
    const initData = async () => {
      for (const coin of specificCoins) {
        try {
          await fetchKlineData(coin.symbol);
        } catch (err) {
          console.error(`初始化${coin.symbol}失败:`, err);
        }
        // 添加延迟以避免触发限制
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    };

    // 刷新所有图表
    const refreshAllCharts = async () => {
      for (const coin of specificCoins) {
        try {
          await fetchKlineData(coin.symbol);
        } catch (err) {
          console.error(`刷新${coin.symbol}失败:`, err);
        }
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    };

    // 处理时间范围变化
    const handleTimeRangeChange = async () => {
      await refreshAllCharts();
    };

    // 设置自动刷新
    let refreshInterval;
    const setupAutoRefresh = () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }

      let refreshTime;
      if (timeRange.value === '1') {
        refreshTime = 30000;  // 30秒
      } else if (timeRange.value === '7') {
        refreshTime = 60000;  // 1分钟
      } else {
        refreshTime = 300000; // 5分钟
      }

      refreshInterval = setInterval(refreshAllCharts, refreshTime);
    };

    // 初始化
    onMounted(async () => {
      await initData();
      setupAutoRefresh();
    });

    // 监听时间范围变化
    watch(timeRange, async () => {
      await handleTimeRangeChange();
      setupAutoRefresh();
    });

    // 组件卸载时清除定时器
    const onUnmounted = () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };

    return {
      specificCoins,
      coinData,
      timeRange,
      loadingCharts,
      error,
      handleTimeRangeChange
    };
  }
});

app.mount('#app'); 