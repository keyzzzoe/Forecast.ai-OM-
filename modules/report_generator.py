from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_report(self, session_state, best_model, forecast_result, forecast_df):
        """Wrapper matching Page 4 call signature"""
        return self.generate_pdf_report(
            dict(session_state) if hasattr(session_state, '__iter__') else session_state,
            forecast_result,
            [best_model]
        )

    def generate_pdf_report(self, session_state, forecast_data, model_results):
        """Generate comprehensive PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E88E5'),
            spaceAfter=30,
            alignment=1  # Center
        )

        story.append(Paragraph("需求预测分析报告", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Report metadata
        meta_data = [
            ['报告生成时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['公司名称', session_state.get('company_name', 'N/A')],
            ['预测目标', session_state.get('forecast_target', 'N/A')],
            ['行业', session_state.get('industry', 'N/A')],
            ['预测周期', f"{session_state.get('planning_horizon', 30)} 天"]
        ]

        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F7FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(meta_table)
        story.append(Spacer(1, 0.5*inch))

        # Executive Summary
        story.append(Paragraph("一、执行摘要", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        best_model = model_results[0]
        summary_text = f"""
        本报告基于历史数据，使用多种预测模型进行需求预测分析。
        经过模型对比，<b>{best_model['model_name']}</b> 表现最优，
        测试集MAPE为 <b>{best_model['metrics']['MAPE']:.2f}%</b>。

        预测未来{session_state.get('planning_horizon', 30)}天的平均需求量为
        <b>{forecast_data['forecast'].mean():.0f}</b>，
        建议提前做好资源配置和运营规划。
        """

        story.append(Paragraph(summary_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Model Comparison
        story.append(Paragraph("二、模型性能对比", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        model_data = [['模型名称', 'MAE', 'RMSE', 'MAPE (%)', 'R²']]
        for result in model_results:
            model_data.append([
                result['model_name'],
                f"{result['metrics']['MAE']:.2f}",
                f"{result['metrics']['RMSE']:.2f}",
                f"{result['metrics']['MAPE']:.2f}",
                f"{result['metrics']['R²']:.4f}"
            ])

        model_table = Table(model_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        model_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFF8E1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(model_table)
        story.append(Spacer(1, 0.3*inch))

        # Forecast Results
        story.append(Paragraph("三、预测结果", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        forecast_summary = f"""
        未来{len(forecast_data['forecast'])}期预测统计：
        <br/>• 平均预测值: {forecast_data['forecast'].mean():.2f}
        <br/>• 最大预测值: {forecast_data['forecast'].max():.2f}
        <br/>• 最小预测值: {forecast_data['forecast'].min():.2f}
        <br/>• 95%置信区间: [{forecast_data['lower_bound'].mean():.2f}, {forecast_data['upper_bound'].mean():.2f}]
        """

        story.append(Paragraph(forecast_summary, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Business Recommendations
        story.append(Paragraph("四、业务建议", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        recommendations = f"""
        基于预测结果，建议：
        <br/>• 根据预测趋势合理配置资源
        <br/>• 关注95%置信区间，为极端情况做好准备
        <br/>• 定期监控实际值与预测值的偏差
        <br/>• 当MAPE超过20%时，考虑重新训练模型
        """

        story.append(Paragraph(recommendations, self.styles['BodyText']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
