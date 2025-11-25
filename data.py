
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

