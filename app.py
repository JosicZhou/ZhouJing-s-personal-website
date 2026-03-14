from flask import Flask, render_template, request, session, jsonify, redirect
import os
from dotenv import load_dotenv
import requests
from data import PERSONAL_MODE_PROMPT, translations
from rag_engine import init_rag, search as rag_search, format_context

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

# 初始化 RAG 系统（启动时自动加载向量库，如不存在则自动构建）
try:
    init_rag()
    RAG_ENABLED = True
    print("[APP] RAG 系统已启用。")
except Exception as e:
    RAG_ENABLED = False
    print(f"[APP] RAG 系统初始化失败，将使用纯 prompt 模式: {e}")

# Render 重定向到 CloudBase（仅在 Render 环境生效）
CLOUDBASE_URL = "https://personal-website-233349-7-1312753510.sh.run.tcloudbase.com"
RENDER_HOST = "zhoujing-s-personal-website.onrender.com"

@app.before_request
def redirect_to_cloudbase():
    """如果是从 Render 访问，重定向到 CloudBase"""
    if request.host == RENDER_HOST:
        return redirect(CLOUDBASE_URL + request.full_path, code=301)

# 多语言支持
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
    mode = data.get('mode', 'personal')
    model = data.get('model', 'gpt-4o')
    
    conversation_key = f'conversation_{mode}'
    if conversation_key not in session:
        session[conversation_key] = []
    
    conversation_history = session[conversation_key]
    
    if len(conversation_history) >= MAX_CONVERSATIONS * 2:
        return jsonify({
            'error': f'对话已达到最大轮次限制（{MAX_CONVERSATIONS}轮），请刷新页面开始新对话',
            'max_reached': True
        }), 429
    
    messages = []
    
    if mode == 'personal':
        # RAG 检索：用用户问题搜索相关个人资料
        rag_context = ""
        if RAG_ENABLED:
            try:
                results = rag_search(user_message, top_k=5)
                rag_context = format_context(results)
                print(f"[RAG] 检索到 {len(results)} 条相关资料")
            except Exception as e:
                print(f"[RAG] 检索失败，回退到纯 prompt 模式: {e}")
                rag_context = ""

        # 构建 system prompt：基础人设 + RAG 检索到的上下文
        if rag_context:
            system_content = (
                PERSONAL_MODE_PROMPT
                + "\n\n"
                + "以下是与用户问题相关的详细个人资料（RAG检索结果），请优先参考这些资料来回答：\n\n"
                + rag_context
            )
        else:
            system_content = PERSONAL_MODE_PROMPT

        messages.append({
            "role": "system",
            "content": system_content
        })
    
    for msg in conversation_history:
        messages.append(msg)
    
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    response = call_apicore_ai(messages, model)
    
    if not response:
        return jsonify({'error': 'AI服务暂时不可用，请稍后重试'}), 500
    
    if 'choices' not in response or not response['choices']:
        return jsonify({'error': 'AI响应格式错误'}), 500
    
    ai_message = response['choices'][0]['message']['content']
    
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

# ============ 页面路由 ============

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

# Projects 主页面（原 AI Projects）
@app.route('/projects')
def projects():
    return render_template('projects.html')

# AI Product 子页面
@app.route('/projects/musiccreator-ai')
def musiccreator_ai():
    return render_template('projects/musiccreator_ai.html')

@app.route('/projects/coloringbook-ai')
def coloringbook_ai():
    return render_template('projects/coloringbook_ai.html')

@app.route('/projects/inker-ai')
def inker_ai():
    return render_template('projects/inker_ai.html')

@app.route('/projects/nanobanana-ai')
def nanobanana_ai():
    return render_template('projects/nanobanana_ai.html')

# Momenta
@app.route('/projects/momenta')
def momenta():
    return render_template('projects/momenta.html')

# Simple Tools 子页面
@app.route('/projects/web-picture-scraper')
def web_picture_scraper():
    return render_template('projects/web_picture_scraper.html')

@app.route('/projects/veo3-video-generator')
def veo3_generator():
    return render_template('projects/veo3_generator.html')

@app.route('/projects/link2qrcode')
def link2qrcode():
    return render_template('projects/link2qrcode.html')

@app.route('/projects/code2html')
def code2html():
    return render_template('projects/code2html.html')

# 兼容旧路由的重定向
@app.route('/ai-projects')
def ai_projects_redirect():
    return redirect('/projects', code=301)

@app.route('/ai-projects/<path:subpath>')
def ai_projects_sub_redirect(subpath):
    return redirect(f'/projects/{subpath}', code=301)

@app.route('/creative-works')
def creative_works_redirect():
    return redirect('/', code=301)

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
            'name': '项目页面',
            'url': '/projects',
            'description': 'AI产品和小工具项目详情，包含AI音乐生成器、AI填色书、AI纹身设计师等'
        }
    ]
    return jsonify({'pages': pages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
