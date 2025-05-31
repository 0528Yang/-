# Flask中医药膳推荐系统 - 代码逐行详解

## 1. 导入库部分

```python
from flask import Flask, request, jsonify, render_template
import requests
import json
```

### 解释：
- `from flask import...`: 从Flask框架导入需要的组件
  - `Flask`: 核心类，用于创建Web应用
  - `request`: 处理HTTP请求数据
  - `jsonify`: 将Python字典转为JSON响应
  - `render_template`: 渲染HTML模板
- `import requests`: 用于发送HTTP请求(调用API)
- `import json`: 处理JSON格式数据

## 2. 创建Flask应用

```python
app = Flask(__name__)
```

### 解释：
- 创建Flask应用实例
- `__name__`表示当前模块名
- 这是每个Flask应用必须的第一步

## 3. 配置API信息

```python
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "key"
```

### 解释：
- 定义两个常量(不变的变量)
- `DEEPSEEK_API_URL`: API的服务地址
- `DEEPSEEK_API_KEY`: 访问API的密钥(示例值，需替换)

## 4. 获取药膳推荐函数

```python
def get_herbal_recipes(user_input):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
```

### 解释：
- 定义函数`get_herbal_recipes`，接收用户输入
- `headers`: 准备API请求头信息
  - `Authorization`: 身份验证，使用Bearer token方式
  - `Content-Type`: 指定发送JSON格式数据

```python
    prompt = f"""
    根据以下用户的身体状况和需求，推荐适合的中医药膳方：
    用户描述：{user_input}
    
    请按照以下格式返回推荐：
    1. 药膳名称
    2. 主要功效
    3. 原料配方
    4. 制作方法
    5. 适用人群
    6. 注意事项
    """
```

### 解释：
- 构造提示词(prompt)，告诉AI如何回答
- 使用f-string格式化字符串(可以插入变量)
- 明确要求返回的格式和内容

```python
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
```

### 解释：
- 准备请求数据：
  - `model`: 指定使用的AI模型
  - `messages`: 对话消息列表
  - `temperature`: 控制回答随机性(0.7较平衡)
  - `max_tokens`: 限制回答长度

## 5. 调用API和处理响应

```python
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
```

### 解释：
- `try`: 尝试执行可能出错的代码
- `requests.post`: 发送POST请求到API
- `raise_for_status()`: 如果请求失败抛出异常
- `response.json()`: 解析返回的JSON数据
- 返回AI生成的内容

```python 
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("DeepSeek API认证失败，请检查API密钥是否正确")
        else:
            print(f"调用DeepSeek API出错: {e}")
        return None
```

### 解释：
- `except`: 捕获并处理异常
- 401错误：API密钥错误
- 其他错误：打印具体错误信息
- 返回None表示失败

## 6. 现代化改良函数

```python
def modernize_recipe(recipe):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 判断内容类型
    content_type = "其他"
    if "注意事项" in recipe:
        content_type = "注意事项"
    elif "制作方法" in recipe: 
        content_type = "制作方法" 
    elif "原料配方" in recipe:
        content_type = "原料配方"
```

### 解释：
- 定义现代化改良函数
- 自动识别药膳内容的类型
- 根据不同类型生成不同的改良建议

## 7. Flask路由

```python
@app.route('/')
def home():
    return render_template('index.html')
```

### 解释：
- `@app.route('/')`: 定义根路径路由
- 当访问网站首页时：
  - 渲染templates/index.html模板
  - 返回给用户浏览器显示

```python
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_input = data.get('input', '')
    
    if not user_input:
        return jsonify({"error": "请输入您的身体状况或需求"}), 400
```

### 解释：
- 定义/recommend路由，只接受POST请求
- `request.json`: 获取POST的JSON数据
- 检查用户输入是否为空
- 如果为空返回400错误

## 8. 主程序入口

```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 解释：
- 判断是否是直接运行此脚本
- `app.run()`: 启动Flask开发服务器
- `debug=True`: 启用调试模式
- `port=5000`: 使用5000端口

## 学习建议

1. 先尝试修改提示词(prompt)，观察AI返回变化
2. 练习添加新的路由，如/about
3. 尝试处理更多类型的错误
4. 修改端口号，了解端口概念

## 常见问题

Q: 如何更换API密钥？
A: 修改DEEPSEEK_API_KEY的值

Q: 如何添加新的药膳类型？
A: 在prompt中修改要求格式

Q: 为什么我的修改不生效？
A: 需要重启Flask服务器(Ctrl+C停止后重新运行)
