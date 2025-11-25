from flask import Flask, render_template, request, session, jsonify, redirect
import os
from dotenv import load_dotenv
import requests
import json

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

# 个人模式的详细prompt
PERSONAL_MODE_PROMPT = """你现在是周晶（Jing Zhou），目前香港理工大学研究生在读。请以第一人称回答用户的问题，展现出你的专业背景和个性。

个人背景信息：
- 教育背景：香港理工大学生成式AI硕士在读，新加坡国立大学交换优秀学者，本科天津财经大学广播电视学（财经新闻）专业，获曾获国家奖学金（全国前1%）
- 专业技能：拥有产品管理、AI技术、媒体设计三重技能（包括拍摄剪辑、影视制作、平面设计、新媒体运营等）
- 实习经验：
  1.AI产品实习生：开发上线4个AI网站，包括AI音乐生成器、AI填色书、AI纹身设计师。SEO运营（程序化，专题页，外链，多语言翻译，EDM运营）
  2.新媒体运营，社区运营：将门创投（ai投资公司）
  3.新媒体营销实习生：网易游戏（游戏公司）
  4.记者实习生：中山日报（省级党报）
  5.编导助理：天津广播电视台
- 项目经验：
  1. AI音乐生成器 - 功能设计与prompt工程；SEO运营
  2. AI填色书 -  功能设计、prompt工程，bug修复；SEO运营；用户运营；
  3. AI纹身 - 功能设计
  4. 网页图片爬虫 - 数据驱动洞察
- 个人特质：结合技术AI专业知识与用户同理心，善于构建真正与用户产生共鸣的AI产品；执行力强（自己动手从0到1搭建个人网站）；b站、datacamp等公开平台自学代码。

详细信息页面导航：
- 完整简历页面：网站的 /resume 页面包含我的详细简历信息，包括教育背景、工作经历、技能和荣誉
- AI项目作品集：网站的 /ai-projects 页面展示我所有AI项目的详细案例，包括AI音乐生成器、AI填色书、AI纹身设计师等
- 创意作品集：网站的 /creative-works 页面展示我的媒体制作、影视、摄影和设计作品
- 关于我页面：网站的 /about 页面包含更多个人背景和故事

回答风格：
- 使用第一人称（我、我的）
- 保持专业但友好的语调
- 可以分享具体的项目经验和学习心得
- 展现对AI产品管理的热情和见解
- 适当展现个人成长历程和未来目标
- 当用户询问详细简历信息时，推荐他们查看"简历页面"获取完整信息
- 当用户想了解AI项目细节时，引导他们浏览"AI项目页面"查看详细案例
- 当用户对我的创意作品感兴趣时，建议他们访问"创意作品页面"
- 如果用户想了解更多个人故事，可以推荐"关于我页面"
- 我乐意引导用户探索网站的不同页面，发现更多我的专业能力和项目成果
- 只需要自然语言回答内容，不需要有任何解释语言，如："好的，现在我是周晶"，以及不要有"**"等符号

请记住，你就是周晶本人，以她的身份和经历来回答问题。当涉及详细信息时，引导用户浏览网站的相应页面获取更完整的信息。"""

# 多语言支持
translations = {
    'en': {
        'nav_home': 'Home',
        'nav_resume': 'Resume',
        'nav_ai_projects': 'AI Projects',
        'nav_creative_works': 'Creative Works',
        'nav_about': 'About',
        'hero_title': 'Zhou Jing 周晶',
        'hero_subtitle': 'AI Product Manager | Bridging Generative AI with User-Centric Narratives',
        'hero_tags_row1': ['MSc in GAH @PolyU', 'AI Product Intern', 'AI SaaS', 'SEO', 'Broadcasting & Television (Financial Journalism)', 'Micro Film', 'Director', 'Journalist', 'Multimedia Operations', 'Social Media Operations', 'Zhongshan Daily', 'NetEase Games'],
        'hero_tags_row2': ['National Scholarship', 'Outstanding Student of Tianjin', 'First-Class Scholarship', 'Outstanding Graduate', 'Outstanding League Member', 'National 2nd Prize in Micro Film Contest', 'Provincial 1st Prize in Advertising Contest', 'Badminton 🏸', 'Photography 📹', 'Swim 🏊‍♀️'],
        'hero_description': 'Leveraging my background in media communication and hands-on experience in AI product development, I build intuitive and engaging AI solutions that resonate with users.',
        'btn_view_projects': 'View My AI Projects',
        'btn_view_resume': 'View My Resume',
        'highlights_title': 'Key Achievements',
        'highlights_subtitle': 'Key milestones that demonstrate my commitment to excellence and innovation in AI product management.',
        'highlight_education': 'Top-Tier Education',
        'highlight_education_desc': 'The Hong Kong Polytechnic University (QS Ranking 54)',
        'highlight_ai_skills': 'AI Product Skills',
        'highlight_ai_skills_desc': 'Built 5+ AI products from zero coding background',
        'highlight_scholarship': 'National Scholarship',
        'highlight_scholarship_desc': 'Awarded to Top 1% of students nationwide',
        'highlight_competitions': '20+ Competition Honors',
        'highlight_competitions_desc': 'Including National 2nd Prize in Micro Film Contest, Provincial 1st Prize in Advertising Contest, and multiple entrepreneurship awards',
        'btn_view_resume': 'View My Resume',
        'ai_section_title': 'AI Assistant',
        'ai_section_subtitle': 'Chat with my AI-powered assistant to learn more about my background, projects, and skills.',
        'ai_chat_title': 'AI Assistant',
        'ai_status_online': 'Online & Ready to Help',
        'ai_welcome_message': 'Hi! I\'m Zhou Jing\'s AI assistant. Feel free to ask me about her projects, skills, experience, or anything else you\'d like to know!',
        'ai_chat_placeholder': 'Ask me about my projects or skills...',
        'chat_mode_label': 'Mode:',
        'chat_mode_personal': 'Personal Mode (About me)',
        'chat_mode_general': 'General Mode (Free chat)',
        'chat_model_label': 'AI Model:',
        'featured_projects_title': 'My AI Endeavors',
        'featured_projects_subtitle': 'Showcasing my journey in building AI products from concept to launch, with focus on user-centric design and technical innovation.',
        'skills_title': 'My Toolbox',
        'footer_contact': 'Get in Touch',
        'footer_copyright': '© 2025 Jing (Josic) Zhou',
        # Dropdown menu items
        'dropdown_all_projects': 'All Projects',
        'dropdown_musiccreator_ai': 'MusicCreator AI',
        'dropdown_coloringbook_ai': 'Coloringbook AI', 
        'dropdown_inker_ai': 'Inker.AI',
        'dropdown_web_picture_scraper': 'Web Picture Scraper',
        'dropdown_nanobanana_ai': 'NanoBanana AI',
        'dropdown_all_creative': 'All Creative Works',
        'dropdown_film_video': 'Film & Video',
        'dropdown_digital': 'Digital Interactive',
        'dropdown_photography': 'Photography',
        'dropdown_graphic': 'Graphic Design',
        # Resume page
        'resume_title': 'Resume',
        'resume_current_role': 'MSc in Generative AI @ PolyU | AI Product Manager',
        'resume_about_title': 'About Me',
        'resume_about_text': 'Jing is an aspiring AI Product Manager with a unique background in media communication and a Master\'s degree in Generative AI from The Hong Kong Polytechnic University. Her expertise lies in user-centric product design, prompt engineering, and leveraging data to drive product growth. She is passionate about creating intuitive AI applications that solve real-world problems.',
        'resume_experience_title': 'Experience',
        'resume_education_title': 'Education',
        'resume_honors_title': 'Honors & Awards',
        'resume_projects_title': 'Publications & Projects',
    },
    'zh': {
        'nav_home': '首页',
        'nav_resume': '简历',
        'nav_ai_projects': 'AI项目',
        'nav_creative_works': '创意作品',
        'nav_about': '关于我',
        'hero_title': 'Zhou Jing 周晶',
        'hero_subtitle': 'AI产品经理 | 连接生成式AI与用户中心的叙事',
        'hero_tags_row1': ['香港理工大学GAH硕士', 'AI产品实习生', 'AI SaaS', 'SEO', '广播电视学（财经新闻）', '微电影','导演', '记者', '全媒体运营', '自媒体运营','中山日报', '网易游戏'],
        'hero_tags_row2': ['国家奖学金', '天津市优秀学生', '校一等奖学金', '优秀毕业生', '优秀团员', '微电影大赛全国二等奖', '大广赛市级一等奖', '羽毛球 🏸', '摄影 📹', '游泳 🏊‍♀️'],
        'hero_description': '凭借我在媒体传播方面的背景和AI产品开发的实际经验，我构建直观且引人入胜的AI解决方案，与用户产生共鸣。',
        'btn_view_projects': '查看我的AI项目',
        'btn_view_resume': '查看我的简历',
        'highlights_title': '核心成就',
        'highlights_subtitle': '展现我在AI产品管理领域卓越和创新承诺的重要里程碑。',
        'highlight_education': '顶尖教育背景',
        'highlight_education_desc': '香港理工大学（QS排名54）',
        'highlight_ai_skills': 'AI产品技能',
        'highlight_ai_skills_desc': '0代码基础完成5+个AI产品',
        'highlight_scholarship': '国家奖学金',
        'highlight_scholarship_desc': '全国前1%学生获得',
        'highlight_competitions': '获得20+竞赛荣誉',
        'highlight_competitions_desc': '包括微电影大赛全国二等奖，大广赛市级一等奖，多项创业创新奖项等',
        'btn_view_resume': '查看我的简历',
        'ai_section_title': 'AI助手',
        'ai_section_subtitle': '与我的AI助手聊天，了解更多关于我的背景、项目和技能。',
        'ai_chat_title': 'AI助手',
        'ai_status_online': '在线并准备帮助',
        'ai_welcome_message': '您好！我是周晶的AI助手。请随时询问她的项目、技能、经验或任何您想了解的内容！',
        'ai_chat_placeholder': '询问我的项目或技能...',
        'chat_mode_label': '模式:',
        'chat_mode_personal': '个人模式 (About me)',
        'chat_mode_general': '通用模式 (自由对话)',
        'chat_model_label': 'AI模型:',
        'featured_projects_title': '我的AI探索',
        'featured_projects_subtitle': '展示我从概念到发布构建AI产品的旅程，专注于以用户为中心的设计和技术创新。',
        'skills_title': '我的工具箱',
        'footer_contact': '联系我',
        'footer_copyright': '© 2025 Zhou Jing 周晶',
        # Dropdown menu items
        'dropdown_all_projects': '所有项目',
        'dropdown_musiccreator_ai': 'MusicCreator AI',
        'dropdown_coloringbook_ai': 'Coloringbook AI',
        'dropdown_inker_ai': 'Inker.AI', 
        'dropdown_web_picture_scraper': 'Web Picture Scraper',
        'dropdown_nanobanana_ai': 'NanoBanana AI',
        'dropdown_all_creative': '所有创意作品',
        'dropdown_film_video': '影视作品',
        'dropdown_digital': '数字互动',
        'dropdown_photography': '摄影作品',
        'dropdown_graphic': '平面设计',
        # Resume page
        'resume_title': '简历',
        'resume_current_role': '香港理工大学生成式AI硕士 | AI产品经理',
        'resume_about_title': '关于我',
        'resume_about_text': '周晶是一位有抱负的AI产品经理，拥有独特的媒体传播背景和香港理工大学生成式AI硕士学位。她的专长在于以用户为中心的产品设计、提示工程和利用数据驱动产品增长。她热衷于创建解决现实问题的直观AI应用程序。',
        'resume_experience_title': '工作经历',
        'resume_education_title': '教育背景',
        'resume_honors_title': '荣誉奖项',
        'resume_projects_title': '项目作品',
    }
}

def get_language():
    return session.get('language', 'en')

def get_text(key):
    language = get_language()
    return translations.get(language, {}).get(key, translations['en'].get(key, key))

@app.context_processor
def inject_translations():
    return dict(get_text=get_text, current_language=get_language())

def call_apicore_ai(messages, model="gpt-3.5-turbo"):
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
    model = data.get('model', 'gpt-3.5-turbo')
    
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
        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI'},
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

@app.route('/about')
def about():
    return render_template('about.html')

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
        },
        {
            'name': '关于我页面',
            'url': '/about',
            'description': '更多个人背景故事和成长经历'
        }
    ]
    return jsonify({'pages': pages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
