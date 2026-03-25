// Cloudflare Worker - 全网热榜API服务
// 支持：微博(官方爬取)、百度(官方爬取)、知乎(官方爬取)、抖音/B站/小红书(第三方API)

export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, HEAD, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json; charset=utf-8'
    }

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders })
    }

    const url = new URL(request.url)
    const path = url.pathname

    // 路由分发
    switch (path) {
      case '/weibo':
        return await getWeiboHot(corsHeaders)
      case '/baidu':
        return await getBaiduHot(corsHeaders)
      case '/zhihu':
        return await getZhihuHot(corsHeaders)
      case '/douyin':
        return await getDouyinHot(corsHeaders)
      case '/bilibili':
        return await getBilibiliHot(corsHeaders)
      case '/xiaohongshu':
        return await getXiaohongshuHot(corsHeaders)
      case '/':
        return new Response(JSON.stringify({
          message: '全网热榜API服务',
          endpoints: {
            weibo: '/weibo - 微博热搜（官方爬取）',
            baidu: '/baidu - 百度热搜（官方爬取）',
            zhihu: '/zhihu - 知乎热榜（官方爬取）',
            douyin: '/douyin - 抖音热榜（第三方API）',
            bilibili: '/bilibili - B站热搜（第三方API）',
            xiaohongshu: '/xiaohongshu - 小红书热榜（第三方API）'
          }
        }), { headers: corsHeaders })
      default:
        return new Response(JSON.stringify({ error: 'Not Found' }), {
          status: 404,
          headers: corsHeaders
        })
    }
  }
}

// ==================== 微博热搜（官方爬取）====================
async function getWeiboHot(corsHeaders) {
  try {
    const response = await fetch('https://s.weibo.com/top/summary', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
      }
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    
    const html = await response.text()
    const hotList = parseWeiboHtml(html)
    
    if (hotList.length === 0) throw new Error('解析为空')

    return new Response(JSON.stringify({
      code: 200,
      msg: 'success',
      data: hotList,
      source: 'weibo_official',
      updateTime: new Date().toISOString()
    }), { headers: corsHeaders })

  } catch (error) {
    console.error('微博爬取失败:', error)
    return await fallbackToXXAPI('weibohot', corsHeaders, error.message)
  }
}

function parseWeiboHtml(html) {
  const hotList = []
  const trRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/g
  let trMatch
  
  while ((trMatch = trRegex.exec(html)) !== null) {
    const trContent = trMatch[1]
    const rankMatch = trContent.match(/<td[^>]*class=["']td-01["'][^>]*>(.*?)<\/td>/)
    const rank = rankMatch ? rankMatch[1].trim() : ''
    
    const titleMatch = trContent.match(/<a[^>]*href=["']([^"']+)["'][^>]*>([^<]+)<\/a>/)
    if (titleMatch && rank) {
      const url = titleMatch[1].startsWith('http') ? titleMatch[1] : 'https://s.weibo.com' + titleMatch[1]
      const title = titleMatch[2].trim()
      const hotMatch = trContent.match(/<span[^>]*>(\d+)<\/span>/)
      const hot = hotMatch ? parseInt(hotMatch[1]) : 0
      
      hotList.push({
        index: parseInt(rank) || hotList.length + 1,
        title: title,
        hot: hot > 0 ? formatHot(hot) : '',
        url: url
      })
    }
  }
  
  return hotList
}

// ==================== 百度热搜（官方爬取）====================
async function getBaiduHot(corsHeaders) {
  try {
    const response = await fetch('https://top.baidu.com/board?tab=realtime', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'BAIDUID=' + Math.random().toString(36).substring(2) + ':FG=1'
      }
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    
    const html = await response.text()
    
    // 尝试从页面中提取JSON数据（百度页面内嵌JSON）
    const jsonMatch = html.match(/<script[^>]*id="sanRoot"[^>]*>([\s\S]*?)<\/script>/)
    if (jsonMatch) {
      try {
        const jsonStr = jsonMatch[1].replace(/^\s*<!--/, '').replace(/-->\s*$/, '')
        const data = JSON.parse(jsonStr)
        if (data && data.data && data.data.cards && data.data.cards[0] && data.data.cards[0].content) {
          const hotList = data.data.cards[0].content.map((item, index) => ({
            index: index + 1,
            title: item.query,
            hot: item.hotScore ? formatHot(item.hotScore) : '',
            url: item.url || `https://www.baidu.com/s?wd=${encodeURIComponent(item.query)}`
          }))
          return new Response(JSON.stringify({
            code: 200,
            msg: 'success',
            data: hotList,
            source: 'baidu_official_json',
            updateTime: new Date().toISOString()
          }), { headers: corsHeaders })
        }
      } catch (e) {
        console.log('百度JSON解析失败，尝试HTML解析:', e.message)
      }
    }
    
    // HTML解析作为备用
    const hotList = parseBaiduHtml(html)
    if (hotList.length === 0) throw new Error('解析为空')

    return new Response(JSON.stringify({
      code: 200,
      msg: 'success',
      data: hotList,
      source: 'baidu_official_html',
      updateTime: new Date().toISOString()
    }), { headers: corsHeaders })

  } catch (error) {
    console.error('百度爬取失败:', error)
    return await fallbackToXXAPI('baiduhot', corsHeaders, error.message)
  }
}

function parseBaiduHtml(html) {
  const hotList = []
  
  // 尝试多种百度热搜的HTML结构
  // 结构1: 新版百度热搜
  let itemRegex = /<div[^>]*class=["']content_\w+["'][^>]*>([\s\S]*?)<\/div>/g
  let match
  let index = 1
  
  while ((match = itemRegex.exec(html)) !== null && index <= 50) {
    const content = match[1]
    const titleMatch = content.match(/<div[^>]*class=["']c-single-text-ellipsis["'][^>]*>(.*?)<\/div>/)
    const hotMatch = content.match(/\d+/) // 简单匹配数字
    
    if (titleMatch) {
      const title = titleMatch[1].replace(/<[^>]+>/g, '').trim()
      const hot = hotMatch ? parseInt(hotMatch[0]) : 0
      
      if (title && title.length > 1) {
        hotList.push({
          index: index++,
          title: title,
          hot: hot > 1000 ? formatHot(hot) : '',
          url: `https://www.baidu.com/s?wd=${encodeURIComponent(title)}`
        })
      }
    }
  }
  
  // 如果第一种没解析到，尝试第二种结构
  if (hotList.length === 0) {
    itemRegex = /<a[^>]*class=["']title_["'][^>]*>(.*?)<\/a>/g
    index = 1
    while ((match = itemRegex.exec(html)) !== null && index <= 50) {
      const title = match[1].replace(/<[^>]+>/g, '').trim()
      if (title && title.length > 1) {
        hotList.push({
          index: index++,
          title: title,
          hot: '',
          url: `https://www.baidu.com/s?wd=${encodeURIComponent(title)}`
        })
      }
    }
  }
  
  return hotList
}

// ==================== 知乎热榜（官方爬取）====================
async function getZhihuHot(corsHeaders) {
  try {
    // 知乎需要特殊的Cookie才能访问API
    const response = await fetch('https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.zhihu.com/hot',
        'x-requested-with': 'fetch',
        'Cookie': '_zap=' + Math.random().toString(36).substring(2)
      }
    })

    if (!response.ok) {
      // 如果API失败，尝试爬HTML页面
      return await getZhihuFromHtml(corsHeaders)
    }
    
    const data = await response.json()
    
    if (data && data.data && data.data.length > 0) {
      const hotList = data.data.map((item, index) => ({
        index: index + 1,
        title: item.target.title,
        hot: item.detail_text ? item.detail_text.replace(/\s/g, '') : '',
        url: `https://www.zhihu.com/question/${item.target.id}`
      }))

      return new Response(JSON.stringify({
        code: 200,
        msg: 'success',
        data: hotList,
        source: 'zhihu_official',
        updateTime: new Date().toISOString()
      }), { headers: corsHeaders })
    }
    
    throw new Error('数据格式错误或为空')

  } catch (error) {
    console.error('知乎API失败:', error)
    // 尝试HTML解析
    return await getZhihuFromHtml(corsHeaders)
  }
}

// 知乎HTML备用解析
async function getZhihuFromHtml(corsHeaders) {
  try {
    const response = await fetch('https://www.zhihu.com/hot', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
      }
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    
    const html = await response.text()
    const hotList = parseZhihuHtml(html)
    
    if (hotList.length === 0) throw new Error('HTML解析为空')

    return new Response(JSON.stringify({
      code: 200,
      msg: 'success',
      data: hotList,
      source: 'zhihu_html',
      updateTime: new Date().toISOString()
    }), { headers: corsHeaders })

  } catch (error) {
    console.error('知乎HTML解析失败:', error)
    return await fallbackToXXAPI('zhihu', corsHeaders, error.message)
  }
}

function parseZhihuHtml(html) {
  const hotList = []
  // 匹配知乎热榜的标题和链接
  const regex = /<a[^>]*href="\/question\/(\d+)"[^>]*>.*?<h2[^>]*class="[^"]*HotItem-title[^"]*"[^>]*>(.*?)<\/h2>/g
  let match
  let index = 1
  
  while ((match = regex.exec(html)) !== null && index <= 50) {
    const questionId = match[1]
    // 清理HTML标签
    const title = match[2].replace(/<[^>]+>/g, '').trim()
    
    if (title && questionId) {
      hotList.push({
        index: index++,
        title: title,
        hot: '',
        url: `https://www.zhihu.com/question/${questionId}`
      })
    }
  }
  
  return hotList
}

// ==================== 抖音热榜（第三方API）====================
async function getDouyinHot(corsHeaders) {
  try {
    const res = await fetch('https://v2.xxapi.cn/api/douyinhot')
    const data = await res.json()
    
    if (data.code === 200 && data.data) {
      return new Response(JSON.stringify({
        code: 200,
        msg: 'success',
        data: data.data,
        source: 'xxapi',
        updateTime: new Date().toISOString()
      }), { headers: corsHeaders })
    }
    throw new Error('API返回错误')
  } catch (error) {
    return new Response(JSON.stringify({
      code: 500,
      msg: '获取失败',
      error: error.message
    }), { status: 500, headers: corsHeaders })
  }
}

// ==================== B站热搜（第三方API）====================
async function getBilibiliHot(corsHeaders) {
  try {
    const res = await fetch('https://v2.xxapi.cn/api/bilibilihot')
    const data = await res.json()
    
    if (data.code === 200 && data.data) {
      return new Response(JSON.stringify({
        code: 200,
        msg: 'success',
        data: data.data,
        source: 'xxapi',
        updateTime: new Date().toISOString()
      }), { headers: corsHeaders })
    }
    throw new Error('API返回错误')
  } catch (error) {
    return new Response(JSON.stringify({
      code: 500,
      msg: '获取失败',
      error: error.message
    }), { status: 500, headers: corsHeaders })
  }
}

// ==================== 小红书热榜（第三方API）====================
async function getXiaohongshuHot(corsHeaders) {
  try {
    // 小红书用oioweb的API
    const res = await fetch('https://api.oioweb.cn/api/social/xiaohongshu-hot-search')
    const data = await res.json()
    
    if (data.code === 200 && data.result) {
      const hotList = data.result.map((item, index) => ({
        index: index + 1,
        title: item.title,
        hot: item.hot || '',
        url: item.url || `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(item.title)}`
      }))
      
      return new Response(JSON.stringify({
        code: 200,
        msg: 'success',
        data: hotList,
        source: 'oioweb',
        updateTime: new Date().toISOString()
      }), { headers: corsHeaders })
    }
    throw new Error('API返回错误')
  } catch (error) {
    return new Response(JSON.stringify({
      code: 500,
      msg: '获取失败',
      error: error.message
    }), { status: 500, headers: corsHeaders })
  }
}

// ==================== 工具函数 ====================

// 格式化热度值
function formatHot(num) {
  if (typeof num === 'string') return num
  if (num >= 100000000) {
    return (num / 100000000).toFixed(1) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

// 备用方案：使用XXAPI
async function fallbackToXXAPI(endpoint, corsHeaders, originalError) {
  try {
    const res = await fetch(`https://v2.xxapi.cn/api/${endpoint}`)
    const data = await res.json()
    
    if (data.code === 200 && data.data) {
      return new Response(JSON.stringify({
        code: 200,
        msg: 'success (fallback)',
        data: data.data,
        source: 'xxapi_fallback',
        updateTime: new Date().toISOString()
      }), { headers: corsHeaders })
    }
    throw new Error('备用API也失败了')
  } catch (fallbackError) {
    return new Response(JSON.stringify({
      code: 500,
      msg: '获取失败',
      error: originalError,
      fallbackError: fallbackError.message
    }), { status: 500, headers: corsHeaders })
  }
}
