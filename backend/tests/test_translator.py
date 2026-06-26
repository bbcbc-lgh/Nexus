from utils.translator import _is_bad_translation, _strip_model_preface


def test_strip_short_text_translation_preface():
    raw = "我注意到你提供的文本很短，但我会帮你翻译：\n\n**一个面向所有人的开源机器学习框架**"

    cleaned = _strip_model_preface(raw)

    assert cleaned == "一个面向所有人的开源机器学习框架"
    assert not _is_bad_translation(cleaned, "description")


def test_reject_model_self_talk_without_translation():
    raw = "I don't see a news summary provided in your message. Could you please share the text you'd like me to translate to Chinese?"

    assert _is_bad_translation(raw, "description")
