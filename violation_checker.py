#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
木森大舞台违规词检测工具
检测标题、字幕、语音转文字中的违规词，避免被限流/封号
"""

import os
import sys
import re

# 完整违规词库
VIOLATION_DICT = {
    "绝对化用语": ["最", "第一", "唯一", "首个", "顶级", "极品", "完美", "绝对", "100%"],
    "虚假宣传": ["免费", "赠送", "秒杀", "抢购", "限时", "最后一天", "清仓", "甩卖"],
    "诱导互动": ["不转不是", "转发发财", "点赞暴富", "关注领红包"],
    "营销引流": ["赚钱", "兼职", "日入", "月入", "暴富", "加微信", "私聊", "扫码"],
    "医疗健康": ["治愈", "根治", "药到病除", "神医", "偏方", "秘方", "包治"],
    "低俗色情": ["性感", "诱惑", "撩", "骚", "浪"],
    "暴力恐怖": ["杀", "死", "血", "恐怖", "暴力", "打架", "斗殴"],
    "违禁品": ["毒品", "冰毒", "海洛因", "大麻", "枪支", "弹药"],
    "版权风险": ["独家", "版权所有", "未经授权", "盗版", "侵权"],
}

# 谐音变体检测
HOMOPHONE_VARIANTS = {
    "薇信": "微信", "v信": "微信", "威信": "微信",
    "扣裙": "QQ群", "扣扣": "QQ",
}

def check_text_violation(text):
    """检测文本中的违规词"""
    results = {"has_violation": False, "violations": [], "categories": {}, "risk_level": "low"}
    if not text:
        return results
    
    for category, words in VIOLATION_DICT.items():
        found = [w for w in words if w in text]
        if found:
            results["violations"].extend(found)
            results["categories"][category] = found
    
    homophone_found = {k: v for k, v in HOMOPHONE_VARIANTS.items() if k in text}
    if homophone_found:
        results["categories"]["谐音变体"] = [f"{k}->{v}" for k, v in homophone_found.items()]
        results["violations"].extend(homophone_found.keys())
    
    if results["violations"]:
        results["has_violation"] = True
        high_risk = ["暴力恐怖", "违禁品", "低俗色情"]
        results["risk_level"] = "high" if any(c in results["categories"] for c in high_risk) else "medium"
    
    return results

def check_title(title):
    """检测标题违规"""
    print(f"\n=== 标题检测 ===")
    print(f"标题: {title}")
    result = check_text_violation(title)
    if result["has_violation"]:
        print(f"  ⚠ 发现违规词: {result['violations']}")
        print(f"  风险等级: {result['risk_level']}")
    else:
        print(f"  ✓ 标题安全，无违规词")
    return result

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--title":
        check_title(sys.argv[2])
    else:
        print("用法: python violation_checker.py --title '标题文字'")