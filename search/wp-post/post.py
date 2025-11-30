import base64
import requests
import json

# ======================================
# 配置区域（修改成你自己的信息）
# ======================================
WP_URL = "https://domain.com/wp-json/wp/v2"
USERNAME = "domain"
APP_PASSWORD = "xxx"

# --------------------------------------
# 构建认证 Header
# --------------------------------------
credentials = f"{USERNAME}:{APP_PASSWORD}"
token = base64.b64encode(credentials.encode()).decode()
HEADERS = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}


# ======================================
# 获取所有分类
# ======================================
def get_categories():
    url = f"{WP_URL}/categories?per_page=100"
    resp = requests.get(url, headers=HEADERS)

    if resp.status_code != 200:
        print("获取分类失败:", resp.status_code, resp.text)
        return None

    return resp.json()


def upload_image(image_path):
    url = f"{WP_URL}/media"
    headers = {
        "Authorization": f"Basic {token}",
    }
    
    # 读取文件并上传
    try:
        with open(image_path, "rb") as img_file:
            media = {
                'file': img_file,  # 直接传入文件
                'caption': '我的特色图'
            }
            # 发送请求时使用 files，而不是 json
            response = requests.post(url, headers=headers, files=media)
            if response.status_code == 201:
                return response.json()  # 返回上传成功的图片的 JSON 数据
            else:
                print("图片上传失败:", response.status_code, response.text)
                return None
    except Exception as e:
        print(f"上传图片失败: {str(e)}")
        return None

# ======================================
# 发布文章
# ======================================
def create_post(title, html_content, featured_media_id=None):
    url = f"{WP_URL}/posts"

    # Blog (201) + PCB-Blog (202)
    category_ids = [201, 202]

    # 如果有特色图，则将其添加到发布数据中
    data = {
        "title": title,
        "content": html_content,
        "status": "draft",
        "categories": category_ids,
        "excerpt": '这是Meta'
    }

    if featured_media_id:
        data["featured_media"] = featured_media_id  # 设置特色图

    resp = requests.post(url, headers=HEADERS, json=data)

    if resp.status_code not in (200, 201):
        print("发布失败:", resp.status_code, resp.text)
        return None

    return resp.json()

# ======================================
# DEMO 演示
# ======================================
if __name__ == "__main__":
    # 1. 上传图片
    image_response = upload_image("./pcb.jpg")  # 替换为你图片的路径
    if image_response:
        featured_media_id = image_response.get('id')
        print(f"图片上传成功，ID: {featured_media_id}")
        
        # 2. 发布文章并设置特色图
        print("\n=== 发布测试文章 ===")
        post = create_post(
            title="这是 Python 自动发布的文章",
            html_content="<h1>Hello WordPress</h1><p>这是通过 Python REST API 发布的文章。</p>",
            featured_media_id=featured_media_id  # 设置特色图
        )
        print(json.dumps(post, indent=2, ensure_ascii=False))
    else:
        print("图片上传失败，无法发布文章。")