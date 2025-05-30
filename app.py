from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)

# 配置DeepSeek API
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-51e26da14be24be4967e202ef70121d1"  # 请替换为实际API key

def get_herbal_recipes(user_input):
    """调用DeepSeek API获取药膳推荐"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
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
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("DeepSeek API认证失败，请检查API密钥是否正确")
        else:
            print(f"调用DeepSeek API出错: {e}")
        return None
    except Exception as e:
        print(f"调用DeepSeek API出错: {e}")
        return None

def modernize_recipe(recipe):
    """使用AI生成现代化改进建议"""
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
    
    prompt = f"""
    根据以下药膳内容的{content_type}部分，提供针对性的现代化改良建议：
    {recipe}
    
    要求：
    1. 建议必须与{content_type}直接相关
    2. 每条建议简洁明确(10字以内)
    3. 用中文分号分隔不同建议
    4. 若无相关建议则返回"无"
    
    示例：
    {content_type}相关建议：使用电压力锅；选用新鲜食材
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        suggestions = [s.strip() for s in content.split("；") if s.strip()]
        # 过滤掉无意义的默认建议
        if not suggestions or "暂无改良建议" in content:
            return []
        return suggestions
    except Exception as e:
        print(f"获取现代化改进建议出错: {e}")
        return ["无法获取AI改进建议，请稍后再试"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_input = data.get('input', '')
    
    if not user_input:
        return jsonify({"error": "请输入您的身体状况或需求"}), 400
    
    # 获取原始药膳推荐
    raw_recipes = get_herbal_recipes(user_input)
    if not raw_recipes:
        return jsonify({"error": "获取药膳推荐失败"}), 500
    
    # 解析并现代化改进
    recipes = []
    recipe_blocks = raw_recipes.split("\n\n")  # 假设每个药膳方用空行分隔
    for block in recipe_blocks:
        if not block.strip():
            continue
            
        # 简单解析药膳方
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        title = lines[0] if lines else "未命名药膳"
        description = "\n".join(lines[1:]) if len(lines) > 1 else "无详细描述"
        
        # 现代化改进
        improvements = modernize_recipe(block)
        
        recipes.append({
            "title": title,
            "description": description,
            "modernized": "；".join(improvements)
        })
    
    return jsonify({"recipes": recipes})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
