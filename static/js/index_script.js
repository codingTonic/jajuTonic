document.addEventListener('DOMContentLoaded', function() {

    // 쿠키 관련 함수들
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
        }
        return null;
    }

    function saveFormData() {
        const formData = {
            name: document.getElementById('name')?.value || '',
            birth_date: document.getElementById('birth_date')?.value || '',
            calendar: document.querySelector('input[name="calendar"]:checked')?.value || 'solar',
            birth_time: document.getElementById('birth_time')?.value || '',
            time_unknown: document.getElementById('time_unknown')?.checked || false,
            gender: document.querySelector('input[name="gender"]:checked')?.value || '',
            relationship: document.getElementById('relationship')?.value || '',
            mbti: document.getElementById('mbti')?.value || ''
        };
        setCookie('sajuFormData', JSON.stringify(formData), 365);
    }

    function loadFormData() {
        const savedData = getCookie('sajuFormData');
        if (savedData) {
            try {
                const formData = JSON.parse(savedData);
                
                // 안전한 DOM 접근으로 값 설정
                const nameEl = document.getElementById('name');
                if (nameEl) nameEl.value = formData.name || '';
                
                const birthDateEl = document.getElementById('birth_date');
                if (birthDateEl) birthDateEl.value = formData.birth_date || '';
                
                if (formData.calendar) {
                    const calendarEl = document.querySelector(`input[name="calendar"][value="${formData.calendar}"]`);
                    if (calendarEl) calendarEl.checked = true;
                }
                
                const birthTimeEl = document.getElementById('birth_time');
                if (birthTimeEl) birthTimeEl.value = formData.birth_time || '';
                
                const timeUnknownEl = document.getElementById('time_unknown');
                if (timeUnknownEl) timeUnknownEl.checked = formData.time_unknown || false;
                
                if (formData.gender) {
                    const genderEl = document.querySelector(`input[name="gender"][value="${formData.gender}"]`);
                    if (genderEl) genderEl.checked = true;
                }
                
                const relationshipEl = document.getElementById('relationship');
                if (relationshipEl) relationshipEl.value = formData.relationship || '';
                
                const mbtiEl = document.getElementById('mbti');
                if (mbtiEl) mbtiEl.value = formData.mbti || '';
                
                // 출생시간 모름 체크박스 상태에 따라 시간 입력 필드 활성화/비활성화
                if (birthTimeEl && timeUnknownEl) {
                    birthTimeEl.disabled = timeUnknownEl.checked;
                }
                
            } catch (e) {
                console.error('저장된 데이터를 불러오는 중 오류가 발생했습니다:', e);
            }
        }
    }

    // 페이지 로드 시 저장된 데이터 불러오기
    loadFormData();

    // 모든 입력 필드에 실시간 저장 기능 추가 (안전한 접근)
    const fieldsToSave = ['name', 'birth_date', 'birth_time', 'relationship', 'mbti', 'time_unknown'];
    fieldsToSave.forEach(id => {
        const element = document.getElementById(id);
        if(element) {
            element.addEventListener('input', saveFormData);
            element.addEventListener('change', saveFormData);
        }
    });
    
    // 라디오 버튼들에 이벤트 리스너 추가
    document.querySelectorAll('input[name="calendar"], input[name="gender"]').forEach(radio => {
        radio.addEventListener('change', saveFormData);
    });

    // 출생시간 모름 체크박스 이벤트
    const timeInput = document.getElementById('birth_time');
    const timeUnknownCheckbox = document.getElementById('time_unknown');
    
    if (timeInput && timeUnknownCheckbox) {
        timeUnknownCheckbox.addEventListener('change', function() {
            timeInput.disabled = this.checked;
            if (this.checked) {
                timeInput.value = '';
            }
            saveFormData();
        });
    }

    // 폼 제출 이벤트
    const sajuForm = document.getElementById('sajuForm');
    if (sajuForm) {
        sajuForm.addEventListener('submit', function(event) {
            event.preventDefault(); // 기본 제출 동작 막기

            const submitButton = sajuForm.querySelector('button[type="submit"]');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const loadingMessage = document.getElementById('loadingMessage');
            
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '사주 계산 중... ⏳';
                submitButton.disabled = true;

                // 로딩 오버레이 표시
                if (loadingOverlay) {
                    loadingOverlay.classList.add('show');
                    loadingOverlay.style.display = 'flex';
                    if (loadingMessage) {
                        loadingMessage.textContent = '당신의 우주를 분석하고 있어요...';
                    }
                }

                // 일반 폼 제출 방식 사용 (서버에서 result.html 렌더링)
                const formData = new FormData(sajuForm);
                
                // 폼을 직접 제출하여 서버에서 렌더링된 페이지로 이동
                sajuForm.submit();
            }
        });
    }



    // 개인정보 삭제 함수 (푸터에서 사용)
    window.clearPrivacyData = function() {
        if (!confirm('정말로 모든 개인정보와 분석 결과를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
            return;
        }
        
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
        if (!csrfToken) {
            alert('보안 토큰을 찾을 수 없습니다. 페이지를 새로고침해주세요.');
            return;
        }

        fetch('/clear-privacy-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert(data.message);
                // 쿠키 삭제 및 페이지 새로고침
                setCookie('sajuFormData', '', -1);
                window.location.reload();
            } else {
                alert('삭제 중 오류가 발생했습니다: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('요청 중 오류가 발생했습니다.');
        });
    }
}); 