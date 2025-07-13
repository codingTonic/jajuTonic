from typing import Dict, List, Any
from datetime import datetime
import os
import jinja2

class SajuHTMLGenerator:
    def __init__(self, template_path='templates/integrated_analysis.html'):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath='.'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Flask의 url_for 함수를 모킹하여 추가
        def mock_url_for(endpoint, **kwargs):
            if endpoint == 'static':
                filename = kwargs.get('filename', '')
                return f"static/{filename}"
            return "#"
        
        self.env.globals['url_for'] = mock_url_for
        
        # format_content 필터를 먼저 등록
        def format_content_filter(content):
            import re
            if not content:
                return content
            # 문장 끝에서 줄바꿈 추가
            content = re.sub(r'([.!?])\s*([가-힣A-Za-z0-9])', r'\1\n\2', content)
            # 특정 키워드 앞에서 줄바꿈 추가
            keywords = ['그런데', '하지만', '또한', '특히', '중요한 건', '무엇보다', '예를 들어', '실제로', '그리고', '따라서']
            for keyword in keywords:
                content = re.sub(f'({keyword})', r'\n\1', content)
            # 연속된 줄바꿈 정리
            content = re.sub(r'\n{2,}', '\n', content)
            return content.strip()

        self.env.filters['format_content'] = format_content_filter
        
        # 필터 등록 후 템플릿 로드
        self.template = self.env.get_template(template_path)
        self.current_date = datetime.now().strftime('%Y년 %m월 %d일')
    
    def generate_standalone_html(self, user_info: dict, saju_result: dict, analysis_parts: list) -> str:
        """
        템플릿과 모든 데이터를 사용하여 독립적인 HTML 파일을 생성합니다.
        CSS가 인라인으로 포함되어 있어 단일 파일로 모든 스타일이 유지됩니다.
        """
        # CSS 파일 읽기
        css_content = ""
        try:
            with open('static/css/analysis_style.css', 'r', encoding='utf-8') as f:
                css_content = f.read()
        except FileNotFoundError:
            pass
        
        # 마크다운 **강조**를 <strong>으로 변환
        from ai_saju_analyzer import AISajuAnalyzer
        analyzer = AISajuAnalyzer()
        for part in analysis_parts:
            if 'content' in part and isinstance(part['content'], str):
                part['content'] = analyzer.convert_markdown_bold_to_html(part['content'])
            if 'sections' in part and isinstance(part['sections'], dict):
                for k, v in part['sections'].items():
                    if isinstance(v, str):
                        part['sections'][k] = analyzer.convert_markdown_bold_to_html(v)
        
        rendered_html = self.template.render(
            user_info=user_info,
            saju_result=saju_result,
            analysis_parts=analysis_parts,
            is_download=True,
            inline_css=css_content
        )
        
        # CSS를 인라인으로 포함
        if css_content:
            rendered_html = rendered_html.replace(
                '<link rel="stylesheet" href="static/css/analysis_style.css">',
                f'<style>{css_content}</style>'
            )
        
        # 다운로드 버전에서는 광고 관련 요소들 제거
        import re
        
        # 쿠팡 광고 섹션 제거
        rendered_html = re.sub(
            r'<!-- 쿠팡 파트너스 광고 -->.*?</div>\s*</div>',
            '',
            rendered_html,
            flags=re.DOTALL
        )
        
        # 광고차단기 감지 모달 제거
        rendered_html = re.sub(
            r'<!-- 광고차단기 감지 모달 -->.*?</script>',
            '',
            rendered_html,
            flags=re.DOTALL
        )
        
        return rendered_html 