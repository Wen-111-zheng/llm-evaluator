# ============================================================
# LLM 输出质量自动评测工具 — 报告生成器
# ============================================================

import json
import matplotlib
matplotlib.use("Agg")  # 非GUI后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from config import JSON_RESULT_FILE, REPORT_FILE

# 设置中文字体
try:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass


def generate_html_report(summary):
    """生成HTML可视化报告"""
    results = summary.get("results", [])
    bad_cases = summary.get("bad_cases", [])
    meta = summary.get("meta", {})

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>LLM 评测报告 - {meta.get('model', 'N/A')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #f5f7fa; color: #333; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 30px 20px; }}
        h1 {{ text-align: center; color: #1a1a2e; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; }}
        .card .value {{ font-size: 36px; font-weight: bold; color: #4a6cf7; }}
        .card .label {{ color: #888; margin-top: 8px; font-size: 14px; }}
        .card.bad .value {{ color: #e74c3c; }}
        
        .chart-section {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .chart-section h2 {{ margin-bottom: 15px; color: #1a1a2e; font-size: 18px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9ff; color: #4a6cf7; font-weight: 600; }}
        tr:hover {{ background: #f8f9ff; }}
        
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
        .badge-pass {{ background: #d4edda; color: #155724; }}
        .badge-fail {{ background: #f8d7da; color: #721c24; }}
        
        .bad-case-box {{ background: #fff5f5; border: 1px solid #fecaca; border-radius: 8px; padding: 15px; margin-bottom: 12px; }}
        .bad-case-box .q {{ font-weight: bold; color: #991b1b; margin-bottom: 6px; }}
        .bad-case-box .a {{ color: #666; font-size: 14px; }}
        .bad-case-box .scores {{ color: #e74c3c; font-size: 12px; margin-top: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 LLM 输出质量评测报告</h1>
        <p class="subtitle">模型: {meta.get('model', 'N/A')} | 评测时间: {meta.get('timestamp', 'N/A')[:19]}</p>
        
        <div class="summary-cards">
            <div class="card">
                <div class="value">{meta.get('total_questions', 0)}</div>
                <div class="label">评测题目数</div>
            </div>
            <div class="card">
                <div class="value">{meta.get('average_score', 0):.1f}</div>
                <div class="label">平均得分</div>
            </div>
            <div class="card bad">
                <div class="value">{meta.get('bad_case_count', 0)}</div>
                <div class="label">Bad Case 数</div>
            </div>
        </div>
"""

    # 评分分布表
    html += """
        <div class="chart-section">
            <h2>📋 评测详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>问题</th>
                        <th>关键词覆盖</th>
                        <th>长度合理性</th>
                        <th>格式规范</th>
                        <th>安全性</th>
                        <th>总分</th>
                        <th>判定</th>
                    </tr>
                </thead>
                <tbody>
"""
    for i, r in enumerate(results, 1):
        scores = r.get("scores", {})
        total = scores.get("总分", 0)
        is_bad = r.get("is_bad_case", False)
        badge = '<span class="badge badge-fail">Bad Case</span>' if is_bad else '<span class="badge badge-pass">通过</span>'
        question_text = r.get("question", "")[:50] + "..." if len(r.get("question", "")) > 50 else r.get("question", "")
        html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{question_text}</td>
                        <td>{scores.get('关键词覆盖', 0):.1f}</td>
                        <td>{scores.get('长度合理性', 0):.1f}</td>
                        <td>{scores.get('格式规范', 0):.1f}</td>
                        <td>{scores.get('安全性', 0):.1f}</td>
                        <td><strong>{total:.1f}</strong></td>
                        <td>{badge}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>
        </div>
"""

    # Bad Case 详情
    if bad_cases:
        html += """
        <div class="chart-section">
            <h2>🔴 Bad Case 分析</h2>
"""
        for bc in bad_cases:
            scores = bc.get("scores", {})
            html += f"""
            <div class="bad-case-box">
                <div class="q">❓ {bc.get('question', 'N/A')[:100]}</div>
                <div class="a">💬 {bc.get('answer', 'N/A')[:200]}</div>
                <div class="scores">得分: {scores.get('总分', 0):.1f} | 关键词: {scores.get('关键词覆盖', 0):.1f} | 长度: {scores.get('长度合理性', 0):.1f} | 格式: {scores.get('格式规范', 0):.1f} | 安全: {scores.get('安全性', 0):.1f}</div>
            </div>"""
        html += """
        </div>
"""

    html += """
    </div>
</body>
</html>"""

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📁 报告已生成: {REPORT_FILE}")


def generate_score_chart(results):
    """生成评分雷达图 PNG"""
    if not results:
        print("⚠️ 无评测数据，跳过图表生成")
        return

    dimensions = ["关键词覆盖", "长度合理性", "格式规范", "安全性"]
    avg_scores = []
    for dim in dimensions:
        dim_scores = [r["scores"].get(dim, 0) for r in results if r.get("scores")]
        avg_scores.append(sum(dim_scores) / len(dim_scores) if dim_scores else 0)

    # 条形图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    colors = ["#4a6cf7", "#34d399", "#f59e0b", "#ef4444"]
    bars = ax1.bar(dimensions, avg_scores, color=colors)
    ax1.set_title("各维度平均得分", fontsize=14, fontweight="bold")
    ax1.set_ylim(0, 30)
    ax1.set_ylabel("平均分")
    for bar, val in zip(bars, avg_scores):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=11)

    # 总分分布
    total_scores = [r["scores"].get("总分", 0) for r in results if r.get("scores")]
    ax2.hist(total_scores, bins=10, color="#4a6cf7", edgecolor="white", alpha=0.8)
    ax2.set_title("总分分布", fontsize=14, fontweight="bold")
    ax2.set_xlabel("总分")
    ax2.set_ylabel("频次")
    ax2.axvline(x=60, color="red", linestyle="--", label="Bad Case 线 (60分)")
    ax2.legend()

    plt.tight_layout()
    chart_path = "./output/score_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 图表已保存: {chart_path}")


if __name__ == "__main__":
    # 加载评测结果
    with open(JSON_RESULT_FILE, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # 生成图表
    generate_score_chart(summary.get("results", []))

    # 生成HTML报告
    generate_html_report(summary)
