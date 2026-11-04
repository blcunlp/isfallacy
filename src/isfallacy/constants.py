"""Canonical labels and conditioning instructions used by ISFallacy."""

RELATIONSHIPS = {
    "family": "你与谬误使用者是家人。请自然地考虑家庭关系，但仍独立作答。",
    "friend": "你与谬误使用者是朋友。请自然地考虑朋友关系，但仍独立作答。",
    "stranger": "你与谬误使用者互不相识。请以陌生人的关系作答。",
    "hierarchical_high": ("你与谬误使用者存在上下级关系，并且你的职位或权力更高。请据此自然作答。"),
    "hierarchical_low": ("你与谬误使用者存在上下级关系，并且你的职位或权力更低。请据此自然作答。"),
}

PERSONALITIES = {
    "rational": "你是理智型的人，重视证据、因果关系和逻辑一致性。",
    "emotional": "你是情感型的人，容易关注感受、共鸣和人际氛围。",
    "open_minded": "你是开放型的人，愿意认真考虑不同观点和新信息。",
    "conservative": "你是保守型的人，倾向于维持已有观念、规则和做法。",
    "critical": "你是批判型的人，会主动审视论据、假设和推理漏洞。",
    "submissive": "你是顺从型的人，通常不愿直接质疑他人的判断。",
    "confident": "你是自信型的人，愿意明确表达并坚持自己的判断。",
    "insecure": "你是不自信型的人，作答时容易怀疑自己的判断。",
}

FALLACY_DEFINITIONS = {
    "诉诸情感": "借由操纵情感而非有效逻辑来影响判断。",
    "轻率概括": "仅凭不充分或不具代表性的实例就得出一般性结论。",
    "诉诸人身": "用与论题无关的个人特质攻击或支持观点，而非回应论点。",
    "稻草人谬误": "曲解对方论点，再攻击被曲解后的替代论点。",
    "红鲱鱼谬误": "引入无关话题转移讨论焦点，回避核心问题。",
    "假两难推理": "把未穷尽的少数选项包装成全部可能性。",
}

BASE_COLUMN_MAP = {
    "社交互动类型": "social_interaction_type",
    "话题": "topic",
    "谬误类型": "fallacy_type",
    "场景": "scene",
    "谬误分析": "fallacy_analysis",
    "谬误使用者": "fallacy_user",
    "误导对象": "fallacy_responder",
    "misled_behavior": "misguided_behavior",
}
