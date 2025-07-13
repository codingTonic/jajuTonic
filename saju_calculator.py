from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar

HEAVENLY_STEMS = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
EARTHLY_BRANCHES = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
GANJI_60 = [HEAVENLY_STEMS[i % 10] + EARTHLY_BRANCHES[i % 12] for i in range(60)]

def get_day_ganji(target_date):
    calendar = KoreanLunarCalendar()
    # 시간 정보는 일주에 영향 없으므로 날짜만 사용
    calendar.setSolarDate(target_date.year, target_date.month, target_date.day)
    gapja_string = calendar.getGapJaString() # 예: "정유년 병오월 임오일"
    # 문자열에서 일주 부분(앞 2글자)만 추출
    day_ganji = gapja_string.split()[-1][:2] # '일' 제외하고 앞 2글자만 추출
    return day_ganji # 예: "임오"


def get_hour_ganji(day_gan, birth_datetime):
    hour = birth_datetime.hour
    minute = birth_datetime.minute
    time_decimal = hour + minute / 60.0

    # 서울 기준(KST, UTC+9) 시주 경계 (근사치)
    # 자시: 23.5 ~ 1.5 / 축시: 1.5 ~ 3.5 / ... / 해시: 21.5 ~ 23.5
    if 23.5 <= time_decimal or time_decimal < 1.5: hour_branch_index = 0 # 자시
    elif 1.5 <= time_decimal < 3.5: hour_branch_index = 1  # 축시
    elif 3.5 <= time_decimal < 5.5: hour_branch_index = 2  # 인시
    elif 5.5 <= time_decimal < 7.5: hour_branch_index = 3  # 묘시
    elif 7.5 <= time_decimal < 9.5: hour_branch_index = 4  # 진시
    elif 9.5 <= time_decimal < 11.5: hour_branch_index = 5 # 사시
    elif 11.5 <= time_decimal < 13.5: hour_branch_index = 6 # 오시
    elif 13.5 <= time_decimal < 15.5: hour_branch_index = 7 # 미시
    elif 15.5 <= time_decimal < 17.5: hour_branch_index = 8 # 신시
    elif 17.5 <= time_decimal < 19.5: hour_branch_index = 9 # 유시
    elif 19.5 <= time_decimal < 21.5: hour_branch_index = 10 # 술시
    elif 21.5 <= time_decimal < 23.5: hour_branch_index = 11 # 해시
    else:
         # 이론상 도달 불가
         hour_branch_index = 0 

    hour_branch = EARTHLY_BRANCHES[hour_branch_index]

    # 시간 계산 (두강법과 유사)
    day_gan_index = HEAVENLY_STEMS.index(day_gan)
    # 시간 간지 계산을 위한 시작 인덱스 (자시 기준)
    start_hour_gan_map = { 0:0, 1:2, 2:4, 3:6, 4:8 } # 갑/기->갑자, 을/경->병자 ... 무/계->임자
    hour_start_gan_index = start_hour_gan_map[day_gan_index % 5]

    hour_gan_index = (hour_start_gan_index + hour_branch_index) % 10
    hour_gan = HEAVENLY_STEMS[hour_gan_index]

    return hour_gan + hour_branch


def get_lunar_date_info(year, month, day):
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)
    lunar_info = {
        "lunar_year": calendar.lunarYear,
        "lunar_month": calendar.lunarMonth,
        "lunar_day": calendar.lunarDay,
        "is_leap_month": calendar.isIntercalation
    }
    return lunar_info


def get_year_ganji(birth_datetime):
    year = birth_datetime.year
    month = birth_datetime.month
    day = birth_datetime.day

    # 입춘 시점 계산 (대략 2월 4일) - 정확한 계산을 위해서는 해당 년도의 입춘 시각 필요
    ipchun_day = 4 # Approximation
    if month < 2 or (month == 2 and day < ipchun_day):
        year -= 1

    # 년주 간지 계산 (기원후 4년 = 갑자년 기준)
    year_gan_index = (year - 4) % 10
    year_ji_index = (year - 4) % 12
    year_gan = HEAVENLY_STEMS[year_gan_index]
    year_ji = EARTHLY_BRANCHES[year_ji_index]

    return year_gan + year_ji # 예: '갑자'


def get_month_ganji(year_ganji_str, birth_datetime):
    month = birth_datetime.month
    day = birth_datetime.day

    # 월주 간지 계산 (절기 기준 필요 - 여기서는 단순화)
    # 절기 시작일(대략 매월 5일) 이전 출생 시 이전 달 월지 사용
    solar_term_day_approx = 5 # Approximation
    adjusted_month = month
    if day < solar_term_day_approx:
         adjusted_month = month -1 if month > 1 else 12

    # 월지 결정 (인월=2, 묘월=3 ... 자월=0, 축월=1)
    # 실제로는 월별 절기 날짜를 정확히 계산해야 함
    month_branch_index_map = {
        1: 1,  # Jan -> 축 (1)
        2: 2,  # Feb -> 인 (2)
        3: 3,  # Mar -> 묘 (3)
        4: 4,  # Apr -> 진 (4)
        5: 5,  # May -> 사 (5)
        6: 6,  # Jun -> 오 (6)
        7: 7,  # Jul -> 미 (7)
        8: 8,  # Aug -> 신 (8)
        9: 9,  # Sep -> 유 (9)
        10: 10, # Oct -> 술 (10)
        11: 11, # Nov -> 해 (11)
        12: 0  # Dec -> 자 (0)
    }
    month_branch_index = month_branch_index_map[adjusted_month]
    month_branch = EARTHLY_BRANCHES[month_branch_index]

    # 월간 계산 (두강법 - 년간 기준 월의 시작 천간 결정)
    year_gan = year_ganji_str[0]
    # 년간 기준 월간 시작 인덱스 (인월[index 2] 기준)
    month_start_gan_index = -1
    if year_gan in ['갑', '기']: month_start_gan_index = 2 # 병(丙)
    elif year_gan in ['을', '경']: month_start_gan_index = 4 # 무(戊)
    elif year_gan in ['병', '신']: month_start_gan_index = 6 # 경(庚)
    elif year_gan in ['정', '임']: month_start_gan_index = 8 # 임(壬)
    elif year_gan in ['무', '계']: month_start_gan_index = 0 # 갑(甲)

    # 인월(index 2)부터 시작하므로, 해당 월까지의 오프셋 계산
    month_offset = (month_branch_index - 2 + 12) % 12 # Offset from 寅 (index 2)

    month_gan_index = (month_start_gan_index + month_offset) % 10
    month_gan = HEAVENLY_STEMS[month_gan_index]

    return month_gan + month_branch # 예: '병인'


def calculate_saju(birth_datetime):
    year = birth_datetime.year
    month = birth_datetime.month
    day = birth_datetime.day

    lunar_info = get_lunar_date_info(year, month, day)

    # 일주 - 수정된 함수 호출
    day_ganji = get_day_ganji(birth_datetime)
    day_gan = day_ganji[0]

    # 시주 - birth_datetime 객체 전체 전달
    hour_ganji = get_hour_ganji(day_gan, birth_datetime)

    # 년주 (입춘 기준) - Corrected call
    year_ganji_str = get_year_ganji(birth_datetime)

    # 월주 (간지 보정 포함, 단순화) - Corrected call
    month_ganji = get_month_ganji(year_ganji_str, birth_datetime)

    return {
        "solar": birth_datetime.strftime("%Y-%m-%d %H:%M"),
        "lunar": f"{lunar_info['lunar_year']}년 {lunar_info['lunar_month']}월 {lunar_info['lunar_day']}일" +
                  (" (윤달)" if lunar_info['is_leap_month'] else ""),
        "년주": year_ganji_str,
        "월주": month_ganji,
        "일주": day_ganji,
        "시주": hour_ganji
    }


# 사용 예시
if __name__ == "__main__":
    try:
        year = int(input("출생년도를 입력하세요 (예: 1992): "))
        month = int(input("출생월을 입력하세요 (예: 4): "))
        day = int(input("출생일을 입력하세요 (예: 20): "))
        hour = int(input("출생시를 입력하세요 (0-23시): "))
        minute = int(input("출생분을 입력하세요 (0-59분): "))

        birth_datetime = datetime(year, month, day, hour, minute)
        
        result = calculate_saju(birth_datetime)
        print("\n--- 사주 결과 ---")
        for k, v in result.items():
            print(f"{k}: {v}")

    except ValueError:
        print("잘못된 형식의 입력입니다. 숫자를 입력해주세요.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")