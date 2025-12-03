from flask import Flask, render_template, request, session, jsonify, redirect
import os
from dotenv import load_dotenv
import requests
from data import PERSONAL_MODE_PROMPT, translations

# 加载本地环境变量（如果有 .env 文件）
load_dotenv()

app = Flask(__name__)
# 从环境变量获取 SECRET_KEY，如果没有则使用默认值（生产环境必须设置环境变量）
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

# APICore.ai 配置
API_BASE_URL = "https://api.apicore.ai"
# 从环境变量获取 API_KEY
API_KEY = os.environ.get('API_KEY')

# 对话轮次限制
MAX_CONVERSATIONS = 5

# 个人模式的详细prompt (moved to data.py)

# 多语言支持
# translations data moved to data.py

def get_language():
    return session.get('language', 'en')

def get_text(key):
    language = get_language()
    return translations.get(language, {}).get(key, translations['en'].get(key, key))

@app.context_processor
def inject_translations():
    return dict(get_text=get_text, current_language=get_language())

def call_apicore_ai(messages, model="gpt-4o"):
    """调用APICore.ai API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        print(f"正在调用API，模型: {data['model']}")
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        print(f"API响应状态码: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误响应内容: {e.response.text}")
        return None

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """AI聊天API端点"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': '消息不能为空'}), 400
    
    user_message = data['message']
    mode = data.get('mode', 'personal')  # personal 或 general
    model = data.get('model', 'gpt-4o')
    
    # 获取当前会话的对话历史
    conversation_key = f'conversation_{mode}'
    if conversation_key not in session:
        session[conversation_key] = []
    
    conversation_history = session[conversation_key]
    
    # 检查对话轮次限制
    if len(conversation_history) >= MAX_CONVERSATIONS * 2:  # 每轮包含用户和AI的消息
        return jsonify({
            'error': f'对话已达到最大轮次限制（{MAX_CONVERSATIONS}轮），请刷新页面开始新对话',
            'max_reached': True
        }), 429
    
    # 构建消息历史
    messages = []
    
    # 添加系统prompt（仅个人模式）
    if mode == 'personal':
        messages.append({
            "role": "system",
            "content": PERSONAL_MODE_PROMPT
        })
    
    # 添加对话历史
    for msg in conversation_history:
        messages.append(msg)
    
    # 添加当前用户消息
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # 调用API
    response = call_apicore_ai(messages, model)
    
    if not response:
        return jsonify({'error': 'AI服务暂时不可用，请稍后重试'}), 500
    
    if 'choices' not in response or not response['choices']:
        return jsonify({'error': 'AI响应格式错误'}), 500
    
    ai_message = response['choices'][0]['message']['content']
    
    # 保存到会话历史
    conversation_history.extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_message}
    ])
    session[conversation_key] = conversation_history
    
    return jsonify({
        'response': ai_message,
        'conversation_count': len(conversation_history) // 2,
        'max_conversations': MAX_CONVERSATIONS,
        'mode': mode
    })

@app.route('/api/chat/reset/<mode>')
def reset_chat(mode):
    """重置对话历史"""
    if mode in ['personal', 'general']:
        conversation_key = f'conversation_{mode}'
        if conversation_key in session:
            del session[conversation_key]
        return jsonify({'success': True, 'message': f'{mode}模式对话已重置'})
    return jsonify({'error': '无效的模式'}), 400

@app.route('/api/chat/models')
def get_available_models():
    """获取可用的AI模型列表"""
    models = [
        {'id': 'gpt-4o', 'name': 'GPT-4o', 'provider': 'OpenAI'},
        {'id': 'gpt-4o-mini', 'name': 'GPT-4o Mini', 'provider': 'OpenAI'},
        {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'provider': 'Anthropic'},
        {'id': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash', 'provider': 'Google'},
        {'id': 'o1-mini', 'name': 'OpenAI o1-mini', 'provider': 'OpenAI'}
    ]
    return jsonify({'models': models})

@app.route('/set_language/<language>')
def set_language(language):
    if language in ['en', 'zh']:
        session['language'] = language
    return redirect(request.referrer or '/')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/ai-projects')
def ai_projects():
    return render_template('ai_projects.html')

@app.route('/creative-works')
def creative_works():
    return render_template('creative_works.html')


# AI Projects sub-pages
@app.route('/ai-projects/musiccreator-ai')
def musiccreator_ai():
    return render_template('ai_projects/musiccreator_ai.html')

@app.route('/ai-projects/coloringbook-ai')
def coloringbook_ai():
    return render_template('ai_projects/coloringbook_ai.html')

@app.route('/ai-projects/inker-ai')
def inker_ai():
    return render_template('ai_projects/inker_ai.html')

@app.route('/ai-projects/web-picture-scraper')
def web_picture_scraper():
    return render_template('ai_projects/web_picture_scraper.html')

@app.route('/ai-projects/nanobanana-ai')
def nanobanana_ai():
    return render_template('ai_projects/nanobanana_ai.html')

# Creative Works sub-pages
@app.route('/creative-works/film-video')
def film_video():
    return render_template('creative_works/film_video.html')

@app.route('/creative-works/digital-interactive')
def digital_interactive():
    return render_template('creative_works/digital_interactive.html')

@app.route('/creative-works/photography')
def photography():
    return render_template('creative_works/photography.html')

@app.route('/creative-works/graphic-design')
def graphic_design():
    return render_template('creative_works/graphic_design.html')

# 页面导航API（用于AI助手推荐页面）
@app.route('/api/pages')
def get_available_pages():
    """获取网站页面信息，供AI助手推荐"""
    pages = [
        {
            'name': '简历页面',
            'url': '/resume',
            'description': '完整的教育背景、工作经历、技能和荣誉信息'
        },
        {
            'name': 'AI项目页面',
            'url': '/ai-projects',
            'description': 'AI音乐生成器、AI填色书、AI纹身设计师等项目详情'
        },
        {
            'name': '创意作品页面',
            'url': '/creative-works',
            'description': '媒体制作、影视、摄影和设计作品展示'
        }
    ]
    return jsonify({'pages': pages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
