"""Minimal UI localization helpers.

Internal research taxonomy stays stable; this module only controls display labels.
"""

LANGUAGE_LABELS = {
    "zh-CN": "中文",
    "en": "English",
}

DOMAIN_LABELS = {
    "公司概览": {"zh-CN": "公司概览", "en": "Company Overview"},
    "商业化与竞争": {"zh-CN": "商业化与竞争", "en": "Commercialization & Competition"},
    "财务与融资": {"zh-CN": "财务与融资", "en": "Financials & Financing"},
    "团队与组织": {"zh-CN": "团队与组织", "en": "Team & Organization"},
    "产品与技术": {"zh-CN": "产品与技术", "en": "Product & Technology"},
    "知识产权": {"zh-CN": "知识产权", "en": "Intellectual Property"},
    "其他重要事项": {"zh-CN": "其他重要事项", "en": "Other Material Matters"},
}

REVIEW_STATUS_LABELS = {
    "unreviewed": {"zh-CN": "○ 未复核", "en": "○ Unreviewed"},
    "cleared": {"zh-CN": "✓ 已复核 / 暂无异议", "en": "✓ Reviewed / no current objection"},
    "follow_up": {"zh-CN": "⚑ 需进一步跟进", "en": "⚑ Follow up"},
}

FLAG_TYPE_LABELS = {
    "unresolved_conflict": {"zh-CN": "信息冲突待确认", "en": "Unresolved information conflict"},
    "unresolved_version": {"zh-CN": "版本口径待确认", "en": "Version / scope to reconcile"},
    "scope_or_definition_gap": {"zh-CN": "口径 / 定义待确认", "en": "Scope / definition gap"},
    "material_evidence_gap": {"zh-CN": "关键证据缺口", "en": "Material evidence gap"},
}


def choose(language, zh_text, en_text):
    return en_text if language == "en" else zh_text


def language_label(language):
    return LANGUAGE_LABELS.get(language, language)


def domain_label(value, language):
    item = DOMAIN_LABELS.get(value)
    return item.get(language, item["zh-CN"]) if item else value


def review_status_label(status, language):
    item = REVIEW_STATUS_LABELS.get(status, REVIEW_STATUS_LABELS["unreviewed"])
    return item.get(language, item["zh-CN"])


def flag_type_label(flag_type, language):
    item = FLAG_TYPE_LABELS.get(flag_type)
    return item.get(language, item["zh-CN"]) if item else flag_type
