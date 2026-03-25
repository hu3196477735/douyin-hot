# Cloudflare Worker 部署教程

## 概述

使用 Cloudflare Worker 搭建免费的后端服务，实时获取微博热搜数据。

**优点：**
- 完全免费（每天10万次请求）
- 全球CDN加速，访问快
- 支持爬虫，绕过跨域限制
- 数据更准更实时

---

## 步骤一：注册 Cloudflare 账号

1. 打开 https://dash.cloudflare.com/sign-up
2. 用邮箱注册（可以用QQ邮箱、163邮箱等）
3. 验证邮箱

---

## 步骤二：创建 Worker

1. 登录后点击左侧菜单 **"Workers & Pages"**
2. 点击 **"Create application"**
3. 点击 **"Create Worker"**
4. 给Worker起个名字，比如 `hot-api`
5. 点击 **"Deploy"**（先部署默认代码）

---

## 步骤三：修改代码

1. 部署成功后，点击 **"Edit code"**
2. 删除默认代码，把下面这段代码粘贴进去：

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
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

  if (path === '/weibo') {
    return await getWeiboHot(corsHeaders)
  } else if (path === '/') {
    return new Response(JSON.stringify({
      message: '热榜API服务',
      endpoints: { weibo: '/weibo' }
    }), { headers: corsHeaders })
  }

  return new Response(JSON.stringify({ error: 'Not Found' }), {
    status: 404,
    headers: corsHeaders
  })
}

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
    // 爬取失败用XXAPI备用
    try {
      const res = await fetch('https://v2.xxapi.cn/api/weibohot')
      const data = await res.json()
      return new Response(JSON.stringify({
        code: 200,
        msg: 'success (fallback)',
        data: data.data,
        source: 'xxapi_fallback',
        updateTime: new Date().toISOString()
      }), { headers: corsHeaders })
    } catch (e) {
      return new Response(JSON.stringify({
        code: 500,
        msg: '获取失败',
        error: error.message
      }), { status: 500, headers: corsHeaders })
    }
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
        hot: hot > 0 ? (hot >= 10000 ? (hot/10000).toFixed(1)+'万' : hot.toString()) : '',
        url: url
      })
    }
  }
  
  return hotList
}
```

3. 点击 **"Save and deploy"**

---

## 步骤四：获取API地址

1. 部署成功后，你会看到一个网址，比如：
   ```
   https://hot-api.yourname.workers.dev
   ```

2. 你的微博热搜API地址就是：
   ```
   https://hot-api.yourname.workers.dev/weibo
   ```

3. 在浏览器里访问这个地址，看看有没有返回数据

---

## 步骤五：修改前端代码

把 `index.html` 里的微博API地址改成你的Worker地址：

```javascript
weibo: {
    name: '微博',
    emoji: '🔥',
    apis: [
        'https://hot-api.yourname.workers.dev/weibo'  // 改成你的地址
    ],
    api: 'https://hot-api.yourname.workers.dev/weibo',
    searchUrl: 'https://s.weibo.com/weibo?q='
},
```

---

## 完成！

现在你的GitHub Pages会调用你自己的Cloudflare Worker，数据直接从微博官方页面爬取，更准确更实时。

如果爬取失败，Worker会自动回退到XXAPI，保证服务可用。

---

## 注意事项

1. **免费额度**：Cloudflare Worker 免费版每天10万次请求，完全够用
2. **如果被封**：如果微博封了Worker的IP，代码会自动回退到XXAPI
3. **自定义域名**：可以在Cloudflare里绑定自己的域名
