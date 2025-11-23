import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import os

# 模拟 User-Agent，防止被 DuckDuckGo 拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def query_ddg(keyword):
    """
    对应 JS 中的 queryDdg 函数
    逻辑：请求 html.duckduckgo.com -> 解析 HTML -> 提取前5个结果 -> 解析 uddg 参数获取真实 URL
    """
    url = f"https://html.duckduckgo.com/html/?q={keyword}"
    
    try:
        print(f"[*] 正在搜索: {keyword} ...")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # 对应 JS: const $ = cheerio.load(text);
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # 对应 JS: $(".result__a").slice(0, 5)
        links = soup.select(".result__a")[:5]
        
        for link in links:
            title = link.get_text(strip=True)
            raw_href = link.get('href')
            
            # 对应 JS: const urlObj = new URL(...) 和 urlObj.searchParams.get("uddg")
            # DuckDuckGo 的链接通常是 /l/?kh=-1&uddg=https%3A%2F%2F...
            real_url = raw_href
            if "uddg=" in raw_href:
                parsed = urllib.parse.urlparse(raw_href)
                query_params = urllib.parse.parse_qs(parsed.query)
                real_url = query_params.get('uddg', [raw_href])[0]
            
            results.append({
                "title": title,
                "url": real_url
            })
            
        return results

    except Exception as e:
        print(f"[!] 搜索出错: {e}")
        return []

def scrape_content(url):
    """
    对应 JS 中的 summarizeContent 函数的前半部分（数据抓取）
    逻辑：fetch(url) -> cheerio 加载 -> 提取 h1-h6, p -> 截取前 14000 字符
    """
    try:
        print(f"[*] 正在爬取: {url} ...")
        # 对应 JS: html = await fetch(url)
        response = requests.get(url, headers=HEADERS, timeout=10) # 加上超时防止卡死
        response.raise_for_status()
        
        # 对应 JS: const $ = cheerio.load(text);
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 对应 JS: const body = $("h1, h2, h3, h4, h5, h6, p");
        tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        
        # 提取文本并合并
        text_content = "\n".join([tag.get_text(strip=True) for tag in tags if tag.get_text(strip=True)])
        
        # 对应 JS: body.text().slice(0, 14000)
        return text_content[:14000]
        
    except Exception as e:
        print(f"[!] 爬取失败 {url}: {e}")
        return None

def main():
    keyword = "PCB thickness" # 你可以修改这里的关键词
    
    # 1. 搜索
    search_results = query_ddg(keyword)
    
    final_data = []
    
    # 2. 遍历并爬取内容
    for item in search_results:
        content = scrape_content(item['url'])
        
        if content:
            # 组装数据结构
            entry = {
                "title": item['title'],
                "url": item['url'],
                # 这里原本是发给 OpenAI 的，现在直接保存下来给你看格式
                "extracted_content": content 
            }
            final_data.append(entry)
    
    # 3. 保存为 JSON
    output_file = os.path.join(os.path.dirname(__file__), 'scraped_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n[OK] 抓取完成，结果已保存至: {output_file}")
    print(f"共成功抓取 {len(final_data)} 篇文章。")

if __name__ == "__main__":
    main()