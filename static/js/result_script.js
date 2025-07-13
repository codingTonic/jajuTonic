let analysisInProgress = false; // 분석 진행 상태 플래그

function showLoading() {
    // 중복 분석 요청 방지
    if (analysisInProgress) {
        console.log('이미 분석이 진행 중입니다.');
        return;
    }
    
    // 분석 시작 플래그 설정
    analysisInProgress = true;
    
    // 로딩 화면 표시
    const loadingOverlay = document.getElementById('loadingOverlay');
    const analysisForm = document.getElementById('analysisForm');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
    
    // 폼 데이터 수집
    const formData = new FormData(analysisForm);
    
    // 백그라운드 분석 시작
    fetch('/start-background-analysis', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'started') {
            console.log('사주 분석이 시작되었습니다.');
            startProgressCheck();
        } else {
            throw new Error(data.message || '분석 시작에 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('분석 시작 오류:', error);
        alert('분석 시작에 실패했습니다: ' + error.message);
        // 오류 발생 시 분석 플래그 리셋
        analysisInProgress = false;
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    });
}

function resetAnalysisState() {
    analysisInProgress = false;
    
    // 버튼 다시 활성화
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        if (btn.onclick && btn.onclick.toString().includes('showLoading')) {
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    });
}

function startProgressCheck() {
    const interval = setInterval(() => {
        fetch('/analysis-progress')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Progress data:', data); // 디버깅용
                
                // 오류 처리
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // 프로그레스 바 업데이트 (8개 파트 기준)
                const progressBar = document.querySelector('.progress-fill');
                if (progressBar) {
                    const progress = (data.last_completed_part / 8) * 100;
                    progressBar.style.width = `${progress}%`;
                }

                // 단계별 상태 업데이트
                const steps = document.querySelectorAll('.loading-steps li');
                steps.forEach((step, index) => {
                    const partNum = index + 1;
                    if (data.completed_parts && data.completed_parts.includes(partNum)) {
                        step.className = 'completed';
                    } else if (data.last_completed_part === partNum - 1) {
                        step.className = 'in-progress';
                    } else {
                        step.className = '';
                    }
                });

                // 완료 시 (status가 "completed"이거나 8개 파트 모두 완료)
                if (data.status === "completed" || data.last_completed_part >= 8) {
                    clearInterval(interval);
                    resetAnalysisState();
                    // 잠시 후 결과 페이지로 리디렉션
                    setTimeout(() => {
                        window.location.href = `/analysis-result?reload=true`;
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('Error polling progress:', error);
                clearInterval(interval);
                resetAnalysisState();
                alert('진행 상태 확인 중 오류가 발생했습니다: ' + error.message);
                document.getElementById('loadingOverlay').style.display = 'none';
            });
    }, 2000); // 2초마다 확인
} 