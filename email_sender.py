import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional
from datetime import datetime

class EmailSender:
    def __init__(self):
        """
        Gmail SMTP를 사용한 이메일 전송 클래스
        """
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('GMAIL_ADDRESS')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
    def send_html_email(self, recipient_email: str, user_info: dict, html_content: str) -> bool:
        """
        HTML 형식으로 사주 분석 결과를 이메일로 전송
        
        Args:
            recipient_email: 수신자 이메일 주소
            user_info: 사용자 정보 (생년월일, 성별 등)
            html_content: 전송할 HTML 내용
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"🌟 {user_info.get('birthdate', '')} 님의 사주 분석 결과 (HTML)"
            
            # HTML 본문 첨부
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Gmail SMTP 서버에 연결하여 이메일 전송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            print(f"[EMAIL] HTML 이메일 전송 성공: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] HTML 이메일 전송 실패: {e}")
            return False

    def send_saju_analysis_email(self, recipient_email: str, user_info: dict, pdf_files: List[str]) -> bool:
        """
        사주 분석 결과를 이메일로 전송
        
        Args:
            recipient_email: 수신자 이메일 주소
            user_info: 사용자 정보 (생년월일, 성별 등)
            pdf_files: 전송할 PDF 파일 경로 리스트
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"🌟 {user_info.get('birthdate', '')} 님의 AI 사주 분석 결과"
            
            # 이메일 본문 생성
            body = self._create_email_body(user_info)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # PDF 파일들 첨부
            for pdf_file in pdf_files:
                if os.path.exists(pdf_file):
                    with open(pdf_file, "rb") as attachment:
                        pdf_data = attachment.read()
                        
                        # MIMEApplication으로 PDF 첨부
                        part = MIMEApplication(pdf_data, _subtype='pdf')
                        
                        # 파일명을 영어로 변경하여 호환성 개선
                        filename = os.path.basename(pdf_file)
                        if 'Part1-4' in filename:
                            safe_filename = f"Saju_Analysis_Part1-4_{user_info.get('birthdate', 'unknown')}.pdf"
                        elif 'Part5-8' in filename:
                            safe_filename = f"Saju_Analysis_Part5-8_{user_info.get('birthdate', 'unknown')}.pdf"
                        else:
                            safe_filename = f"Saju_Analysis_{user_info.get('birthdate', 'unknown')}.pdf"
                        
                        part.add_header('Content-Disposition', 'attachment', filename=safe_filename)
                        part.add_header('Content-Type', 'application/pdf')
                        
                        # 파일 크기 확인 로그
                        print(f"[EMAIL] 첨부 파일 크기: {len(pdf_data)} bytes, 파일명: {safe_filename}")
                        
                        msg.attach(part)
            
            # Gmail SMTP 서버에 연결하여 이메일 전송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            print(f"[EMAIL] 이메일 전송 성공: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] 이메일 전송 실패: {e}")
            return False
    
    def _create_email_body(self, user_info: dict) -> str:
        """이메일 본문 HTML 생성"""
        birthdate = user_info.get('birthdate', '')
        gender = '남성' if user_info.get('gender') == 'male' else '여성'
        relationship = {
            'single': '솔로',
            'dating': '연애 중',
            'married': '기혼'
        }.get(user_info.get('relationship', ''), '')
        
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')
        
        return f"""
        <html>
        <body style="font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <h1 style="color: #e94560; text-align: center; margin-bottom: 30px;">🌟 AI 사주 분석 결과</h1>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                        <h3 style="color: #495057; margin-top: 0;">📋 분석 정보</h3>
                        <p><strong>생년월일:</strong> {birthdate}</p>
                        <p><strong>성별:</strong> {gender}</p>
                        <p><strong>연애 상태:</strong> {relationship}</p>
                        <p><strong>분석 완료:</strong> {current_time}</p>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                        <h3 style="color: #1976d2; margin-top: 0;">📎 첨부 파일</h3>
                        <p>• <strong>Part 1-4:</strong> 사주팔자, 성격분석, 커리어/연애 운세</p>
                        <p>• <strong>Part 5-8:</strong> 인생흐름, 타이밍, 라이프해킹, 종합조언</p>
                    </div>
                    
                    <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                        <h3 style="color: #f57c00; margin-top: 0;">💡 이용 안내</h3>
                        <p>• PDF 파일을 다운로드하여 언제든지 확인하실 수 있습니다</p>
                        <p>• 분석 결과는 참고용으로만 활용해 주세요</p>
                        <p>• 추가 문의사항이 있으시면 언제든지 연락주세요</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 14px;">
                            이 이메일은 AI 사주 분석 서비스에서 자동 발송되었습니다.<br>
                            분석 결과가 도움이 되셨기를 바랍니다! 🙏
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def validate_email_config(self) -> bool:
        """이메일 설정 검증"""
        if not self.sender_email or not self.sender_password:
            print("[EMAIL ERROR] Gmail 계정 정보가 설정되지 않았습니다.")
            print("환경변수 GMAIL_ADDRESS와 GMAIL_APP_PASSWORD를 설정해주세요.")
            return False
        return True
    
    def is_available(self) -> bool:
        """이메일 서비스 사용 가능 여부 확인"""
        return self.validate_email_config()
    
    def send_test_pdf(self, recipient_email: str, pdf_file_path: str) -> bool:
        """테스트용 PDF 전송"""
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "🧪 PDF 테스트 전송"
            
            # 이메일 본문 생성
            body = """
            안녕하세요!
            
            이것은 PDF 전송 테스트 이메일입니다.
            첨부된 PDF 파일이 정상적으로 열리는지 확인해주세요.
            
            감사합니다.
            """
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # PDF 파일 첨부
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as attachment:
                    pdf_data = attachment.read()
                    
                    # MIMEApplication으로 PDF 첨부
                    part = MIMEApplication(pdf_data, _subtype='pdf')
                    
                    filename = os.path.basename(pdf_file_path)
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    part.add_header('Content-Type', 'application/pdf')
                    
                    print(f"[TEST] 첨부 파일 크기: {len(pdf_data)} bytes, 파일명: {filename}")
                    
                    msg.attach(part)
            else:
                print(f"[ERROR] 테스트 파일이 존재하지 않음: {pdf_file_path}")
                return False
            
            # Gmail SMTP 서버에 연결하여 이메일 전송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            print(f"[TEST] 테스트 이메일 전송 성공: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"[TEST ERROR] 테스트 이메일 전송 실패: {e}")
            return False

    def send_user_info_email(self, recipient_email: str, user_info: dict, saju_result: dict) -> bool:
        """
        사용자 정보를 관리자 이메일로 전송
        
        Args:
            recipient_email: 수신자 이메일 주소 (관리자)
            user_info: 사용자 정보 (이름, 생년월일 등)
            saju_result: 사주 계산 결과
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 이메일 설정 검증
            if not self.validate_email_config():
                return False
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"🌟 새로운 사주 분석 요청 - {user_info.get('name', 'Unknown')}"
            
            # 이메일 본문 생성
            body = self._create_user_info_email_body(user_info, saju_result)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Gmail SMTP 서버에 연결하여 이메일 전송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            print(f"[EMAIL] 사용자 정보 이메일 전송 성공: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] 사용자 정보 이메일 전송 실패: {e}")
            return False
    
    def _create_user_info_email_body(self, user_info: dict, saju_result: dict) -> str:
        """사용자 정보 이메일 본문 HTML 생성"""
        name = user_info.get('name', 'Unknown')
        birthdate = user_info.get('birthdate', '')
        birthtime = user_info.get('birthtime', '')
        gender = '남성' if user_info.get('gender') == 'male' else '여성'
        relationship = {
            'single': '솔로',
            'dating': '연애 중',
            'married': '기혼'
        }.get(user_info.get('relationship', ''), '')
        mbti = user_info.get('mbti', '')
        
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')
        
        # 사주 정보 포맷팅
        saju_info = ""
        if saju_result:
            saju_info = f"""
            <h4>🔮 사주팔자 정보</h4>
            <p><strong>연주:</strong> {saju_result.get('year_pillar', 'N/A')}</p>
            <p><strong>월주:</strong> {saju_result.get('month_pillar', 'N/A')}</p>
            <p><strong>일주:</strong> {saju_result.get('day_pillar', 'N/A')}</p>
            <p><strong>시주:</strong> {saju_result.get('hour_pillar', 'N/A')}</p>
            <p><strong>일간:</strong> {saju_result.get('day_master', 'N/A')}</p>
            """
        
        return f"""
        <html>
        <body style="font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <h1 style="color: #e94560; text-align: center; margin-bottom: 30px;">🌟 새로운 사주 분석 요청</h1>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                        <h3 style="color: #495057; margin-top: 0;">👤 사용자 정보</h3>
                        <p><strong>이름:</strong> {name}</p>
                        <p><strong>생년월일:</strong> {birthdate}</p>
                        <p><strong>출생시간:</strong> {birthtime}</p>
                        <p><strong>성별:</strong> {gender}</p>
                        <p><strong>연애 상태:</strong> {relationship}</p>
                        <p><strong>MBTI:</strong> {mbti}</p>
                        <p><strong>요청 시간:</strong> {current_time}</p>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                        <h3 style="color: #1976d2; margin-top: 0;">🔮 사주 계산 결과</h3>
                        {saju_info}
                    </div>
                    
                    <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                        <h3 style="color: #f57c00; margin-top: 0;">📋 관리 메모</h3>
                        <p>• 새로운 사주 분석 요청이 접수되었습니다.</p>
                        <p>• 사용자가 분석을 시작하면 추가 알림을 받게 됩니다.</p>
                        <p>• 분석 결과는 웹사이트에서 확인할 수 있습니다.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 14px;">
                            이 이메일은 AI 사주 분석 서비스에서 자동 발송되었습니다.<br>
                            사용자 정보 관리를 위해 전송되었습니다. 🙏
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

# 전역 이메일 전송자 인스턴스
email_sender = EmailSender() 