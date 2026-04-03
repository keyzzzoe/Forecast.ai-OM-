"""
AI Assistant Component for ForecastAI
Provides contextual guidance and help throughout the application
"""

def get_ai_assistant_html(step, context=None):
    """
    Generate AI assistant HTML for each step

    Args:
        step: Current step number (1-5)
        context: Optional dict with additional context

    Returns:
        HTML string for AI assistant component
    """

    assistants = {
        1: {
            "title": "👋 欢迎使用 ForecastAI",
            "message": """
                <p>我是您的 AI 预测助手，将全程协助您完成需求预测。</p>
                <p><strong>当前步骤：</strong>选择您的行业并填写基本信息</p>
                <ul>
                    <li>✨ 选择最符合您业务的行业类型</li>
                    <li>📝 填写公司名称和预测目标（如"日销售额"）</li>
                    <li>📅 设置预测周期（建议 30-90 天）</li>
                    <li>🔄 如果数据有明显周期性（如周末高峰），请勾选</li>
                </ul>
                <p class="ai-tip">💡 <strong>小提示：</strong>预测目标要具体明确，如"门店日销售额"比"销售情况"更好</p>
            """,
            "type": "guide"
        },
        2: {
            "title": "📊 准备上传数据",
            "message": """
                <p><strong>数据要求：</strong></p>
                <ul>
                    <li>📁 CSV 格式文件</li>
                    <li>📅 必须包含日期列（如 2024-01-01）</li>
                    <li>📈 必须包含数值列（您的预测目标）</li>
                    <li>⏱️ 建议至少 60 天历史数据，越多越准确</li>
                </ul>
                <p class="ai-tip">💡 <strong>没有数据？</strong>可以先用示例数据体验完整流程</p>
            """,
            "type": "guide"
        },
        3: {
            "title": "🤖 AI 正在为您训练模型",
            "message": """
                <p>系统将自动训练多个预测模型并选出最优方案：</p>
                <ul>
                    <li>📊 移动平均 (MA) - 简单快速</li>
                    <li>📈 指数平滑 (ETS) - 适合趋势数据</li>
                    <li>🎯 ARIMA - 经典时间序列</li>
                    <li>🚀 XGBoost - 机器学习算法</li>
                    <li>🧠 LSTM - 深度学习（数据量大时）</li>
                </ul>
                <p class="ai-tip">💡 <strong>评估指标：</strong>MAPE 越小越好，低于 10% 为优秀，10-20% 为良好</p>
            """,
            "type": "info"
        },
        4: {
            "title": "📈 查看预测结果",
            "message": """
                <p><strong>如何解读预测报告：</strong></p>
                <ul>
                    <li>📊 蓝色线：历史真实数据</li>
                    <li>🔴 红色线：模型预测值</li>
                    <li>🎯 阴影区域：95% 置信区间（预测范围）</li>
                </ul>
                <p class="ai-tip">💡 <strong>下一步：</strong>下载预测数据或生成完整 PDF 报告</p>
            """,
            "type": "success"
        },
        5: {
            "title": "🔄 持续优化预测",
            "message": """
                <p><strong>录入实际值以评估模型表现：</strong></p>
                <ul>
                    <li>📝 选择日期并输入实际发生的数值</li>
                    <li>📊 系统自动计算预测误差</li>
                    <li>⚠️ 如果误差超过 20%，建议重新训练</li>
                </ul>
                <p class="ai-tip">💡 <strong>最佳实践：</strong>每周录入实际值，每月重新训练一次模型</p>
            """,
            "type": "guide"
        }
    }

    assistant = assistants.get(step, assistants[1])

    type_colors = {
        "guide": "#1e88e5",
        "info": "#43a047",
        "success": "#8e24aa",
        "warning": "#fb8c00"
    }

    color = type_colors.get(assistant["type"], "#1e88e5")

    html = f"""
    <div class="ai-assistant-card" style="border-left-color: {color}">
        <div class="ai-assistant-header">
            <span class="ai-icon">🤖</span>
            <span class="ai-title">{assistant["title"]}</span>
        </div>
        <div class="ai-assistant-body">
            {assistant["message"]}
        </div>
    </div>
    """

    return html


def get_progress_html(current_step, completed_steps=None):
    """
    Generate enhanced progress bar HTML

    Args:
        current_step: Current step number (1-5)
        completed_steps: List of completed step numbers

    Returns:
        HTML string for progress bar
    """

    if completed_steps is None:
        completed_steps = list(range(1, current_step))

    steps = [
        {"num": 1, "label": "行业设定", "icon": "🏢"},
        {"num": 2, "label": "数据上传", "icon": "📊"},
        {"num": 3, "label": "模型训练", "icon": "🤖"},
        {"num": 4, "label": "预测报告", "icon": "📈"},
        {"num": 5, "label": "反馈迭代", "icon": "🔄"}
    ]

    progress_percent = (current_step / 5) * 100

    html = f"""
    <div class="enhanced-progress-container">
        <div class="progress-header">
            <div class="progress-title">
                <span class="progress-icon">🎯</span>
                <span>预测流程进度</span>
            </div>
            <div class="progress-stats">
                <span class="progress-percent">{progress_percent:.0f}%</span>
                <span class="progress-text">已完成 {current_step-1}/5 步</span>
            </div>
        </div>
        <div class="progress-bar-track">
            <div class="progress-bar-fill" style="width: {progress_percent}%"></div>
        </div>
        <div class="step-progress-enhanced">
    """

    for i, step in enumerate(steps):
        is_completed = step["num"] in completed_steps
        is_current = step["num"] == current_step

        status_class = "completed" if is_completed else ("active" if is_current else "pending")

        # Add connecting line except for last step
        if i > 0:
            line_class = "completed" if steps[i-1]["num"] in completed_steps else ""
            html += f'<div class="step-line-enhanced {line_class}"></div>'

        html += f"""
        <div class="step-item-enhanced">
            <div class="step-circle-enhanced {status_class}">
                <span class="step-icon">{step["icon"]}</span>
                <span class="step-number">{step["num"]}</span>
            </div>
            <div class="step-label-enhanced {status_class}">{step["label"]}</div>
        </div>
        """

    html += """
        </div>
    </div>
    """

    return html
