"""
AI 关键词过滤器，用于从综合技术源（如 Hacker News）中筛选 AI 相关内容
"""
import re

AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'deep learning',
    'LLM', 'GPT', 'Claude', 'Gemini', 'neural network', 'transformer',
    'diffusion', 'stable diffusion', 'reinforcement learning',
    'computer vision', 'NLP', 'natural language processing',
    'OpenAI', 'Anthropic', 'HuggingFace', 'fine-tuning', 'fine-tune',
    'RAG', 'retrieval augmented', 'agent', 'multimodal', 'large language',
    'foundation model', 'generative AI', 'ChatGPT', 'Llama', 'Mistral',
    'image generation', 'text generation', 'embedding', 'vector',
    '人工智能', '大模型', '大语言模型', '机器学习', '深度学习',
    '智能体', '多模态', '生成式', '生成式AI', '开源模型',
    '算力', '推理', '训练', '微调', '向量数据库',
]


def is_ai_related(title: str, description: str = '') -> bool:
    """判断标题或摘要是否与 AI 相关（大小写不敏感）"""
    text = (title + ' ' + (description or '')).lower()
    for kw in AI_KEYWORDS:
        needle = kw.lower()
        if re.fullmatch(r"[a-z0-9]{1,4}", needle):
            if re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", text):
                return True
        elif needle in text:
            return True
    return False
