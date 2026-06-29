import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'smallbiz_programs.db')

# Detect if we should use PostgreSQL (Render environment) or SQLite (Local environment)
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None and (DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://'))

def get_db_connection():
    if IS_POSTGRES:
        import psycopg2
        url = DATABASE_URL
        # Python's psycopg2 expects postgresql:// instead of postgres:// which Render sometimes sets
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(url)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        return conn

def get_dict_result(cursor, rows):
    """
    Utility helper to convert query result tuples into dictionary lists.
    Guarantees cross-database compatibility without row_factory dependency.
    """
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]

def init_db():
    if not IS_POSTGRES:
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables based on database type
    if IS_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id SERIAL PRIMARY KEY,
                sido VARCHAR(50) NOT NULL,
                sigungu VARCHAR(50) NOT NULL,
                organization VARCHAR(255) NOT NULL,
                announcement_date VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                link TEXT NOT NULL,
                deadline VARCHAR(50) NOT NULL,
                budget_size VARCHAR(255) NOT NULL,
                target_audience TEXT NOT NULL,
                participation_method TEXT NOT NULL,
                budget_delivery_type VARCHAR(100) NOT NULL,
                apply_method VARCHAR(255) NOT NULL,
                documents TEXT NOT NULL,
                contact_info VARCHAR(255) NOT NULL,
                hwpx_parsed_text TEXT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT '모집중'
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sido TEXT NOT NULL,
                sigungu TEXT NOT NULL,
                organization TEXT NOT NULL,
                announcement_date TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                link TEXT NOT NULL,
                deadline TEXT NOT NULL,
                budget_size TEXT NOT NULL,
                target_audience TEXT NOT NULL,
                participation_method TEXT NOT NULL,
                budget_delivery_type TEXT NOT NULL,
                apply_method TEXT NOT NULL,
                documents TEXT NOT NULL,
                contact_info TEXT NOT NULL,
                hwpx_parsed_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT '모집중'
            )
        ''')
    
    # Check if table has data. If less than 22 items, re-seed to apply new regions and economic agencies.
    cursor.execute("SELECT COUNT(*) FROM programs")
    count = cursor.fetchone()[0]
    
    if count < 22:
        # Clear existing to prevent duplicate IDs and seed fresh list
        cursor.execute("DELETE FROM programs")
        if IS_POSTGRES:
            cursor.execute("ALTER SEQUENCE programs_id_seq RESTART WITH 1")
            
        seed_data = [
            (
                "경기", "수원시", "수원시청 기업일자리정책과", "2026-06-10",
                "2026년 수원시 소상공인 새바람 패키지 지원사업",
                "점포 경영환경 개선(간판 정비, 인테리어 개선, 시스템 도입 등)을 위해 업체당 최대 200만 원 지원",
                "https://www.suwon.go.kr", "2026-07-20", "업체당 최대 200만 원 (자부담 10% 포함)",
                "수원시 내 창업 6개월 이상의 소상공인",
                "신청서 및 계획서 온라인 또는 방문 제출 -> 서류 심사 -> 점포 개선 완료 후 보조금 지급",
                "지자체 직접 지급", "온라인 접수 또는 수원시청 방문 접수",
                "사업자등록증, 소상공인확인서, 국세/지방세 납세증명서, 임대차계약서",
                "031-228-3224 / 소상공인지원팀",
                "【수원시 공고 제2026-1102호】\n수원시 소상공인 활성화 조례에 의거하여, 경영 환경이 열악한 관내 영세 소상공인의 자생력 및 경쟁력 강화를 위한 '2026년 소상공인 새바람 패키지 지원사업'의 신청 요령을 다음과 같이 공고합니다.\n\n1. 지원대상: 수원시 내 영업 중인 상시근로자 5인 미만 소상공인\n2. 지원내용: 옥외 간판 교체, 점포 인테리어 개선, POS 시스템 도입 등 점포 환경 개선비용\n3. 지원금액: 업체당 공급가액의 90% 한도 내 최고 200만 원 (부가가치세 및 초과분은 본인 부담)",
                "모집중"
            ),
            (
                "경기", "가평군", "가평군청 일자리경제과", "2026-06-18",
                "가평군 관광특화 소상공인 환경 개선 지원사업",
                "가평군 내 관광지 인근 소상공인을 대상으로 영문 간판 제작 및 키오스크 설치 비용 지원",
                "https://www.gp.go.kr", "2026-07-15", "업체당 최대 150만 원",
                "가평군 내 관광 상권 구역 내 위치한 소상공인",
                "신청 및 접수 -> 가평군 심의위원회 평가 -> 선정 통보 및 사업 진행 -> 정산 후 보조금 지급",
                "지자체 직접 지급", "가평군청 일자리경제과 방문 접수 또는 우편 접수",
                "신청서, 사업계획서, 소상공인확인서, 최근 1년 부가가치세과세표준증명",
                "031-580-2275 / 지역경제팀",
                "【가평군 공고 제2026-85호】\n가평군의 주요 관광지 인근에서 영업 중인 소상공인의 외국인 관광객 편의 증진 및 매장 디지털화를 위한 지원사업을 공고하오니 소상공인 여러분의 많은 신청 바랍니다.\n\n- 지원 분야: 영어/다국어 간판 제작 지원, 다국어 지원 키오스크(주문기) 구매 및 대여비 일부 보조.",
                "모집중"
            ),
            (
                "서울", "강남구", "강남구청 지역경제과", "2026-06-12",
                "강남구 소상공인 모바일 마케팅 및 SNS 광고비 지원",
                "인스타그램, 네이버 스마트플레이스, 카카오톡 채널 등 온라인 마케팅 비용을 실비 기준 사후 환급",
                "https://www.gangnam.go.kr", "2026-07-10", "업체당 최대 100만 원",
                "강남구에 사업자등록을 두고 영업 중인 소상공인",
                "광고 실행 및 영수증 증빙 수집 -> 온라인 신청서 작성 및 증빙 첨부 -> 매달 말일 검토 후 환급",
                "지자체 직접 지급", "강남구청 소상공인 지원 플랫폼 온라인 신청",
                "사업자등록증, 부가가치세 신고서, 광고비 지출 세금계산서 또는 카드 영수증, 통장 사본",
                "02-3423-5502",
                "【강남구 고시 제2026-441호】\n모바일 및 온라인 중심의 소비 환경 변화에 능동적으로 대처할 수 있도록 강남구 소재 소상공인의 홍보/마케팅 활동 비용을 지원하는 사업을 공고합니다.\n\n* 신청자격: 신청일 현재 강남구에 사업장을 두고 6개월 이상 영업 중인 소상공인\n* 지원제외: 대기업 프랜차이즈 직영점, 유흥 및 사행성 업종",
                "모집중"
            ),
            (
                "경북", "울릉군", "울릉군청 일자리경제팀", "2026-06-25",
                "울릉군 도서지역 소상공인 택배비 추가 지원사업",
                "도서지역 소상공인의 물류비 부담 완화를 위해 발생한 추가 택배 실비를 건당 최대 3,000원 환급",
                "https://www.ulleung.go.kr", "2026-11-30", "연간 업체당 최대 80만 원 한도",
                "울릉군에 사업장을 둔 전체 소상공인",
                "택배 발송 증빙 및 운송장 영수증 모아서 매 분기별 관할 읍·면사무소에 접수",
                "지자체 직접 지급", "관할 읍/면사무소 경제팀 방문 신청",
                "지원 신청서, 택배 발송 내역서, 택배비 영수증(사업자용), 통장사본",
                "054-790-6221",
                "【울릉군 공고 제2026-180호】\n육지와 떨어져 도서 물류 비용의 이중 부담을 겪는 관내 소상공인들을 위해 정부 및 울릉군 예산으로 추가 택배 비용을 일부 지원하오니 대상 업체의 적극적인 신청을 바랍니다.",
                "모집중"
            ),
            (
                "경북", "포항시", "포항시청 일자리경제국", "2026-06-05",
                "포항시 영세 소상공인 카드수수료 지원사업",
                "전년도 연매출 3억 원 이하 영세 소상공인을 대상으로 카드 수수료 발생액의 0.5% (최대 50만 원) 지원",
                "https://www.pohang.go.kr", "2026-07-31", "업체당 최대 50만 원 (예산 소진 시 조기 마감)",
                "포항시 관내 연매출 3억 원 이하 카드 가맹 소상공인",
                "온라인 접수 창구에 사업자등록번호 입력 -> 매출액 조회 동의 -> 지원금 확정 후 대표자 계좌 입금",
                "지자체 직접 지급", "포항 카드수수료 지원 시스템 온라인 접수 (www.pohang-card.kr)",
                "사업자등록증, 대표자 통장사본 (매출 정보는 자동 수집 및 스크래핑 동의)",
                "054-270-2415 / 소상공인 지원 콜센터",
                "【포항시 공고 제2026-92호】\n경기침체 및 카드 결제 비중 증가에 따른 영세 소상공인의 경영 부담 경감을 위하여 '카드수수료 지원사업'을 시행하오니 많은 신청 바랍니다.",
                "모집중"
            ),
            (
                "경북", "경주시", "경주컨벤션뷰로", "2026-06-01",
                "2026 경주시 소상공인 전시회/박람회 참가 지원",
                "전시회 및 박람회 부스 임차료, 장치비, 홍보물 제작비 등 참가 비용의 80% 지원",
                "https://www.gyeongju.go.kr", "2026-06-30", "업체당 최대 250만 원",
                "경주시에 소재한 제조업 및 특산물 판매 소상공인",
                "참가 지원 신청 -> 심사 후 예비 선정 -> 전시회 참가 완료 -> 결과보고서 제출 및 정산 청구",
                "관리기관 위탁 지급", "이메일 접수 (gj_expo@db.or.kr) 또는 우편 접수",
                "신청서, 전시회 참가계획서, 소상공인확인서, 부스 계약서 사본",
                "054-702-1000",
                "【경주시 공고 제2026-55호】\n관내 소상공인의 신규 판로 개척과 브랜드 홍보 기회를 넓히기 위해 국내 유망 전시회 및 박람회 참가를 지원하고자 다음과 같이 공고합니다.",
                "마감완료"
            ),
            (
                "전국", "전체", "중소벤처기업부 / 소상공인시장진흥공단", "2026-06-03",
                "2026년 소상공인 스마트상점 기술보급사업 (1차)",
                "스마트오더, 키오스크, 테이블오더, 스마트미러 등 소상공인 점포의 디지털 기술 도입 비용 지원 (50%~70% 보조)",
                "https://www.semas.or.kr", "2026-07-15", "국비 최대 500만 원 (일반형) / 1,000만 원 (선도형)",
                "전국 소상공인 보호 및 지원에 관한 법률상 소상공인",
                "스마트상점 홈페이지 신청 -> 서류 심사 및 현장 진단 -> 기술 공급기업 계약 -> 설치 후 국비 정산",
                "관리기관 위탁 지급", "소상공인 스마트상점 홈페이지(smart.sbiz.or.kr) 온라인 접수",
                "사업자등록증, 소상공인확인서, 국세/지방세 납세증명서, 임대차계약서 또는 자가 건물 증빙",
                "1357 (중소기업 통합 콜센터) / 스마트상점 전용 콜센터 1600-6185",
                "【중소벤처기업부 공고 제2026-191호】\n소상공인의 자생력 및 경쟁력 강화를 위한 2026년도 소상공인 스마트상점 기술보급사업 대상 상점 모집 계획을 다음과 같이 공고합니다.",
                "모집중"
            ),
            (
                "부산", "해운대구", "해운대구청 일자리경제과", "2026-06-20",
                "해운대구 소상공인 지식재산권(상표권) 출원 지원",
                "독창적인 레시피, 브랜드, 디자인 도용 방지를 위해 상표 및 특허 출원 비용(변리사 수임료 포함) 지원",
                "https://www.haeundae.go.kr", "2026-08-31", "업체당 최대 60만 원 (상표권 기준)",
                "해운대구에 사업장을 두고 영업 중인 소상공인",
                "신청 접수 -> 지식재산 세미나 이수(필수) -> 전문 변리사 매칭 및 출원 -> 비용 사후 정산",
                "지자체 직접 지급", "이메일 접수 및 구청 방문 접수",
                "사업자등록증, 소상공인확인서, 상표 디자인 이미지 안, 특허/상표 출원 동의서",
                "051-749-4472 / 지식재산팀",
                "【해운대구 공고 제2026-48호】\n해운대구의 우수한 소상공인 브랜드 자산을 보호하고 지식재산권 경쟁력을 제고하고자 소상공인 지식재산권 출원 비용 지원 사업을 공고합니다.",
                "모집중"
            ),
            (
                "전북", "부안군", "부안군청 미래전략담당관", "2026-06-21",
                "2026년 부안군 소상공인 카드수수료 지원사업",
                "부안군 내 영세 소상공인을 대상으로 전년도 카드 결제 수수료 발생액의 0.5% (최대 50만 원) 지원",
                "https://www.buan.go.kr", "2026-08-31", "업체당 최대 50만 원",
                "부안군 관내 연매출 3억 원 이하 카드 가맹 소상공인",
                "온라인 또는 군청 방문 접수 -> 심사 후 대표자 계좌 입금",
                "지자체 직접 지급", "부안군청 홈페이지 소상공인 카드수수료 신청 배너",
                "사업자등록증, 부가가치세 과세표준증명원, 대표자 명의 통장사본",
                "063-580-4224 / 소상공인지원팀",
                "【부안군 공고 제2026-402호】\n관내 소상공인의 경영 부담 경감을 위하여 '2026년 소상공인 카드수수료 지원사업'을 시행하오니 대상 업체의 적극적인 신청을 바랍니다.",
                "모집중"
            ),
            (
                "전남", "해남군", "해남군청 일자리경제과", "2026-06-15",
                "해남군 소상공인 점포 경영환경 개선사업",
                "노후 점포 인테리어 개선, 옥외 간판 교체, 안전 설비 설치 등 경영환경 개선비의 90% 지원",
                "https://www.haenam.go.kr", "2026-07-25", "업체당 최대 200만 원",
                "해남군 내 6개월 이상 영업 중인 상시근로자 5인 미만 소상공인",
                "신청서 제출 -> 해남군 선정 심의 -> 점포 개선 공사 완료 -> 정산 증빙 제출 후 보조금 지급",
                "지자체 직접 지급", "해남군청 일자리경제과 방문 신청",
                "신청서 및 계획서, 소상공인확인서, 시설개선 비교(전/후) 견적서, 임대차계약서",
                "061-530-5353",
                "【해남군 공고 제2026-115호】\n경기 침체로 어려움을 겪고 있는 관내 영세 소상공인의 자생력 및 경쟁력 강화를 위한 '소상공인 점포 경영환경 개선사업'의 신청 요령을 다음과 같이 공고합니다.",
                "모집중"
            ),
            (
                "전남", "장성군", "장성군청 일자리경제과", "2026-06-12",
                "장성군 소상공인 융자금 대출이자 차액보전(이차보전) 지원",
                "금융기관 소상공인 대출금에 대해 대출이자율 중 연 3% 이내의 차액을 최대 3년간 예산 보조",
                "https://www.jangseong.go.kr", "2026-12-31", "융자 한도 최대 5,000만 원 (연 이자 3% 보조)",
                "장성군 내 사업장을 둔 소상공인 중 전남신용보증재단 특례보증 승인자",
                "전남신용보증재단 보증 신청 -> 은행 대출 실행 -> 군청 이자 보조 신청",
                "지자체 직접 지급", "농협/광주은행 등 장성군 내 협약 금융기관 방문 신청",
                "융자신청서, 사업자등록증, 전남신용보증재단 보증서 사본, 통장 사본",
                "061-390-7352 / 상권활성화팀",
                "【장성군 고시 제2026-88호】\n장성군 소상공인 보호 및 지원에 관한 조례에 의거하여 소상공인의 자금난 해소 및 경영 안정을 유도하기 위한 '대출이자 차액보전사업'을 공고합니다.",
                "모집중"
            ),
            (
                "경북", "의성군", "의성군청 일자리경제과", "2026-06-22",
                "의성군 소상공인 역량강화 맞춤형 1:1 컨설팅",
                "세무, 노무, 경영컨설팅, 마케팅 분야 전문가가 직접 매장을 방문하여 1:1 맞춤형 피드백 제공",
                "https://www.usc.go.kr", "2026-08-20", "전액 무료 (업체당 3회 무료 방문 컨설팅)",
                "의성군 내 사업장을 둔 소상공인 및 창업 예비 상인",
                "컨설팅 신청 접수 -> 업종별 전문 컨설턴트 매칭 -> 매장 방문 컨설팅 완료 및 피드백 보고",
                "관리기관 위탁 지급", "의성군청 경제과 또는 읍면사무소 방문 신청",
                "지원 신청서, 컨설팅 사전 진단 설문지, 사업자등록증",
                "054-830-6604",
                "【의성군 공고 제2026-210호】\n골목 상권 상인들의 자생력 회복과 디지털 대응 역량 향상을 유도하기 위하여 '소상공인 1:1 맞춤 진단 컨설팅 지원사업'을 공고합니다.",
                "모집중"
            ),
            (
                "경남", "밀양시", "밀양시청 일자리경제과", "2026-06-08",
                "2026 밀양시 소상공인 소규모 점포 경영환경 개선사업",
                "점포 간판 제작, 인테리어 개선, POS 단말기 및 서빙 키오스크 구매 비용의 80% 지원",
                "https://www.miryang.go.kr", "2026-07-15", "업체당 최대 150만 원 (자부담 20%)",
                "밀양시에 주소와 사업장을 둔 창업 6개월 이상의 소상공인",
                "시청 방문 서류 제출 -> 서류 심사 -> 점포 개선 진행 및 영수증 증빙 정산 -> 계좌 입금",
                "지자체 직접 지급", "밀양시청 일자리경제과 소상공인팀 방문 접수",
                "사업자등록증, 소상공인확인서, 지방세 완납증명서, 인테리어 견적 및 시안",
                "055-359-5733",
                "【밀양시 공고 제2026-1182호】\n경기침체로 어려움을 겪는 관내 영세 소상공인들의 노후 매장 환경을 현대화하여 매출 증대를 지원하고자 '소규모 점포 개선 지원사업' 참여 대상을 모집합니다.",
                "모집중"
            ),
            (
                "강원", "원주시", "원주시청 기업지원일자리과", "2026-06-18",
                "원주시 1인 자영업자 사회보험료(고용/산재) 지원",
                "자영업자 고용보험 및 산재보험에 가입한 근로자 없는 1인 소상공인 대상 보험료 50% 지원",
                "https://www.wonju.go.kr", "2026-11-30", "보험료 of 50% 분기별 환급",
                "원주시에 사업자등록을 두고 영업 중인 상시근로자 없는 1인 소상공인",
                "보험료 납부 후 원주시청 온라인 접수 -> 가입 및 납부 확인 후 계좌 입금",
                "지자체 직접 지급", "원주시청 홈페이지 내 자영업자 사회보험 지원 포털 접수",
                "지원 신청서, 고용/산재보험 가입증명원, 보험료 납부 확인서, 통장 사본",
                "033-737-2914 / 사회보험지원팀",
                "【원주시 공고 제2026-95호】\n영세 소상공인의 사회 안전망을 확보하고 부도 및 재해 위험에 대한 자생력을 도모하고자 '자영업자 고용/산재 보험료 지원사업'을 공고합니다.",
                "모집중"
            ),
            (
                "충북", "충주시", "충주시청 일자리종합지원센터", "2026-06-14",
                "충주시 청년 소상공인 점포 임차료 한시 지원",
                "창업 초기 청년 소상공인의 임차료 부담을 경감하고자 월 최대 30만 원씩 6개월간 점포 임차비 보조",
                "https://www.chungju.go.kr", "2026-07-20", "최대 180만 원 (월 30만 원 x 6개월)",
                "충주시에 주소를 두고 창업 3년 이내인 만 39세 이하 청년 소상공인",
                "시청 방문 접수 -> 청년 연령 및 창업 연차 심사 -> 매월 임차료 이체 증빙 제출 후 보조금 지급",
                "지자체 직접 지급", "충주시청 일자리종합지원센터 우편 및 방문 접수",
                "신청서, 임대차계약서 사본, 월세 이체 영수증(직전 3개월), 소상공인확인서",
                "043-850-6015 / 청년지원팀",
                "【충주시 공고 제2026-44호】\n충주시 청년 소상공인의 안정적인 상권 정착과 초기 창업 생존율을 높이기 위한 '청년 점포 임차비 한시 지원사업'을 다음과 같이 모집 공고합니다.",
                "모집중"
            ),
            (
                "전남", "완도군", "완도군청 경제교통과", "2026-06-23",
                "완도 해양특산물 소상공인 택배 및 물류비 지원",
                "완도 해산물 특산물 배송 시 발생하는 추가 택배 물류비를 건당 최대 3,000원씩 정액 지원",
                "https://www.wando.go.kr", "2026-10-31", "업체당 연간 최대 60만 원 한도",
                "완도군 내 사업장을 두고 전복, 미역 등 완도 해산물을 판매/유통하는 소상공인",
                "주소지 읍/면 사무소 방문 접수 -> 매 분기별 택배 송장 확인 후 계좌 입금",
                "지자체 직접 지급", "주소지 관할 읍·면사무소 산업팀(경제팀) 방문 접수",
                "지원 신청서, 택배 발송 대장, 택배 영수증(세금계산서 또는 신용카드 승인 전표), 통장사본",
                "061-550-5755",
                "【완도군 공고 제2026-33호】\n해상 교통 여건으로 과도한 물류비용 부담을 지고 있는 완도군 관내 해양 수산 소상공인 경쟁력 확보를 위한 '특산물 물류비 지원사업'을 공고합니다.",
                "모집중"
            ),
            (
                "전남", "진도군", "진도군청 세무회계과", "2026-06-19",
                "진도군 소상공인 노란우산공제 가입장려금 지원",
                "진도군 내 영세 소상공인의 폐업/노령 대비를 돕기 위해 노란우산 신규 가입자에게 매월 2만 원 장려금 지급",
                "https://www.jindo.go.kr", "2026-12-31", "매월 2만 원씩 최대 1년 지원 (총 24만 원)",
                "진도군 관내 연매출 2억 원 이하 영세 소상공인 중 노란우산 신규 가입자",
                "중소기업중앙회 또는 금융기관 가입 신청 시 장려금 신청서 동시 제출",
                "지자체 직접 지급", "진도군 내 시중 금융기관(농협, 수협 등) 또는 중소기업중앙회 가입",
                "가입신청서, 사업자등록증, 매출증빙서류(부가가치세과세표준증명 등)",
                "061-540-3344",
                "【진도군 고시 제2026-102호】\n영세 소상공인의 생활 안정을 도모하고 사회안전망 구축을 촉진하기 위한 '진도 소상공인 노란우산 공제 가입 장려금 사업'을 안내 공고합니다.",
                "모집중"
            ),
            (
                "전남", "여수시", "여수시청 관광과", "2026-06-25",
                "여수시 관광상권 소상공인 다국어 메뉴판 보급사업",
                "외국인 관광객 편의 제공을 위해 다국어(영/중/일) 인쇄 메뉴판 및 태블릿 QR 오더 번역 디자인비 지원",
                "https://www.yeosu.go.kr", "2026-08-31", "전액 무료 지원 (메뉴판 인쇄 및 번역 전액 시비 보조)",
                "여수시 관내 주요 관광 지구(낭만포차, 이순신광장 인근 등) 내 요식업 소상공인",
                "신청서 및 메뉴 구성표 제출 -> 여수시 다국어 디자인 심사 -> 메뉴판 무료 제작 및 현장 설치",
                "지자체 직접 지급", "여수시청 관광과 방문 및 이메일 신청",
                "참가 신청서, 기존 메뉴판 사진, 사업자등록증, 영업신고증 사본",
                "061-659-3873",
                "【여수시 공고 제2026-552호】\n국제 해양관광 휴양도시 여수를 방문하는 외국인 관광객들의 음식점 편의 증대 및 요식업주 글로벌 역량 제고를 위한 '다국어 메뉴판 설치 보급 사업'을 공고합니다.",
                "모집중"
            ),
            # --- 주요 광역 경제진흥원 신규 특화 사업 씨드 데이터 ---
            (
                "서울", "전체", "서울경제진흥원 (SBA)", "2026-06-18",
                "2026 서울 소상공인 소담스퀘어 상암/당산 라이브커머스 제작 지원",
                "라이브커머스 무료 스튜디오/장비 대여, 전문 숏폼 촬영 실습 및 네이버 쇼핑라이브 스타 쇼호스트 매칭 전폭 지원",
                "https://sba.seoul.kr", "2026-08-31", "전액 무료 (스튜디오 대여 및 쇼호스트 매칭 매달 지원)",
                "서울시에 사업자등록을 둔 라이브커머스 진출 희망 소상공인",
                "SBA 홈페이지 신청 -> 적격 심사 -> 스튜디오 예약 및 쇼호스트 일정 조율 -> 라이브 방송 송출",
                "관리기관 위탁 지급", "서울경제진흥원 홈페이지 내 지원사업 신청 배너",
                "사업자등록증, 통신판매업 신고증, 상품 기술서(소개서)",
                "02-2222-3788 / 디지털커머스팀",
                "【SBA 공고 제2026-112호】\n서울시 소상공인의 온라인 판로 다각화 및 미디어 커머스 경쟁력 제고를 위한 '소담스퀘어 상암/당산 라이브커머스 지원사업'의 참여 대상을 공고합니다.",
                "모집중"
            ),
            (
                "부산", "전체", "부산경제진흥원 (BEPA)", "2026-06-14",
                "2026 부산 소상공인 소담스퀘어 온라인 판로지원 사업",
                "전문 디자이너 매칭을 통한 오픈마켓 상세페이지 무료 제작 및 온라인 SNS 홍보 마케팅비 환급 지원",
                "https://www.bepa.kr", "2026-07-31", "상세페이지 무료 제작 + 업체당 홍보 마케팅비 최대 100만 원 환급",
                "부산광역시 내에 주소와 영업장을 둔 온라인 쇼핑몰 입점 희망 소상공인",
                "진흥원 접수 -> 선정 통보 -> 상세페이지 제작 지원 -> 자부담 마케팅 광고 실행 -> 영수증 정산 환급",
                "관리기관 위탁 지급", "부산 소상공인 종합지원센터 온라인 지원사업 신청란",
                "사업자등록증, 소상공인확인서, 국세/지방세 납세증명서, 마케팅 수행계획서",
                "051-600-1792 / 온라인판로팀",
                "【부산경제진흥원 공고 제2026-80호】\n지역 영세 소상공인들의 성공적인 e커머스 입점 및 온라인 자생력 확보를 유도하고자 상세페이지 무료 제작 및 마케팅 실비 보전 사업을 추진합니다.",
                "모집중"
            ),
            (
                "경남", "전체", "경남투자경제진흥원", "2026-06-20",
                "경상남도 공식 종합쇼핑몰 e경남몰 입점 및 할인 마케팅 지원",
                "e경남몰 신규 입점 도내 소상공인 대상 진흥원 예산 전액 지원으로 상시 20%~30% 할인쿠폰 발행 및 전용 기획전 노출",
                "https://www.gipa.or.kr", "2026-09-30", "기획전 특별 구좌 노출 및 쿠폰 발행 전액 도비 보조",
                "경상남도 내에 사업장을 둔 농축수산물 및 공산품 생산 소상공인",
                "e경남몰 입점 신청 -> 경남투자경제진흥원 서류/품질 검토 -> 몰 입점 완료 및 전용 기획전 매칭",
                "관리기관 위탁 지급", "e경남몰 공식 파트너센터 온라인 접수",
                "사업자등록증, 소상공인확인서, 통신판매업 신고증 사본, 제품 상세 소개서 및 견본 사진",
                "055-230-2900 / 쇼핑몰운영팀",
                "【경남투자경제진흥원 고시 제2026-44호】\n도내 소상공인과 농어민의 매출 안정화를 도모하고 직거래 활성화를 유도하기 위한 'e경남몰 특별 기획전 참가업체 모집'을 공고합니다.",
                "모집중"
            ),
            (
                "전북", "전체", "전북특별자치도 경제통상진흥원", "2026-06-22",
                "전북 소상공인 온라인 판매 기반(상세페이지 & 숏폼) 조성사업",
                "온라인 쇼핑몰 판매 진출 예정인 도내 소상공인을 위해 전문 영상 촬영진이 매장을 방문하여 숏폼 및 제품 상세페이지 제작 전액 보조",
                "https://www.jbba.kr", "2026-07-28", "상세페이지 디자인 1건 및 숏폼 홍보영상 1편 무료 제작 지원",
                "전북특별자치도 내에 주소와 사업장을 둔 소상공인 전체",
                "경진원 홈페이지 신청 -> 심사 -> 전문 촬영/제작 대행사 방문 -> 상세페이지 및 숏폼 제작 완료 및 인도",
                "관리기관 위탁 지급", "전북특별자치도 경제통상진흥원 사업공고 포털 접수",
                "참가 신청서, 사업자등록증, 소상공인확인서, 제품 소개서",
                "063-711-2000 / 소상공인팀",
                "【전북경진원 공고 제2026-155호】\ne커머스 시장 진출을 희망하지만 상세페이지와 영상 콘텐츠 제작에 어려움을 겪고 있는 관내 영세 상인들을 위한 인프라 조성사업을 공고합니다.",
                "모집중"
            ),
            (
                "대전", "전체", "대전일자리경제진흥원", "2026-06-19",
                "대전 소상공인 전용 모바일 홈쇼핑 라이브대장 방송 제작 지원",
                "자체 라이브커머스 플랫폼 '라이브대장' 및 네이버 쇼핑라이브 채널을 통해 대전 소상공인 제품의 1시간 특별 방송 제작 및 전액 무료 송출",
                "https://www.djbea.or.kr", "2026-08-15", "쇼호스트 매칭, 대본 구성, 방송 연출 및 전용 쿠폰 전액 무료 지원",
                "대전광역시에 사업장을 두고 온라인 판매가 가능한 완제품을 보유한 소상공인",
                "진흥원 신청 -> 방송 상품 선정위원회 평가 -> 대본 작성 및 쇼호스트 매칭 -> 라이브방송 실행",
                "관리기관 위탁 지급", "대전일자리경제진흥원(대전비즈) 온라인 신청",
                "지원 신청서, 사업자등록증, 통신판매업 신고증, 상세 제품 안내서 및 맛보기 샘플 제출",
                "042-380-3000 / 기업지원팀",
                "【대전일자리경제진흥원 공고 제2026-92호】\n우수한 지역 소상공인 제품의 미디어 노출 기회를 확대하고 실질적인 단기 매출 증대를 도모하기 위해 '모바일 라이브커머스 방송 지원사업'을 공고합니다.",
                "모집중"
            ),
            (
                "경북", "전체", "경상북도경제진흥원", "2026-06-15",
                "2026 경북 소상공인 온라인 판로개척 및 e커머스 입점 지원",
                "네이버 스마트스토어, 쿠팡 등 주요 e커머스 입점 실무 컨설팅, 상세페이지 제작, 키워드 광고비 100만 원 매칭 지원",
                "https://www.gepa.kr", "2026-07-31", "업체당 광고 마케팅 매칭 펀드 최대 100만 원 보조",
                "경상북도 내 사업자등록을 두고 영업 중인 소상공인",
                "진흥원 홈페이지 지원사업 접수 -> 선정 통보 -> 온라인 판로 교육 및 상세페이지 제작 -> 광고 집행 후 정산",
                "관리기관 위탁 지급", "경북경제진흥원 홈페이지 온라인 지원사업 신청 탭",
                "사업자등록증, 소상공인확인서, 지방세 납세증명서, 통신판매업 신고증 사본",
                "054-470-8500 / 소상공인팀",
                "【경북경제진흥원 공고 제2026-105호】\n도내 우수 소상공인의 온라인 시장 진출 활성화와 홍보 자생력 배양을 위하여 경상북도 예산으로 시행하는 e커머스 입점 마케팅 지원사업 공고입니다.",
                "모집중"
            )
        ]
        
        placeholder = '%s' if IS_POSTGRES else '?'
        placeholders = ', '.join([placeholder] * 17)
        cursor.executemany(f'''
            INSERT INTO programs (
                sido, sigungu, organization, announcement_date, title, content,
                link, deadline, budget_size, target_audience, participation_method,
                budget_delivery_type, apply_method, documents, contact_info, hwpx_parsed_text, status
            ) VALUES ({placeholders})
        ''', seed_data)
        
        conn.commit()
    conn.close()

def get_all_programs(filters=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = '%s' if IS_POSTGRES else '?'
    query = "SELECT * FROM programs WHERE 1=1"
    params = []
    
    if filters:
        if filters.get('sido') and filters.get('sido') != '전체':
            query += f" AND sido = {placeholder}"
            params.append(filters['sido'])
        if filters.get('sigungu') and filters.get('sigungu') != '전체':
            query += f" AND sigungu = {placeholder}"
            params.append(filters['sigungu'])
        if filters.get('delivery_type') and filters.get('delivery_type') != '전체':
            like_keyword = 'ILIKE' if IS_POSTGRES else 'LIKE'
            query += f" AND budget_delivery_type {like_keyword} {placeholder}"
            params.append(f"%{filters['delivery_type']}%")
        if filters.get('status') and filters.get('status') != '전체':
            query += f" AND status = {placeholder}"
            params.append(filters['status'])
        if filters.get('keyword'):
            like_keyword = 'ILIKE' if IS_POSTGRES else 'LIKE'
            query += f" AND (title {like_keyword} {placeholder} OR content {like_keyword} {placeholder} OR organization {like_keyword} {placeholder})"
            keyword_param = f"%{filters['keyword']}%"
            params.extend([keyword_param, keyword_param, keyword_param])
            
    query += " ORDER BY announcement_date DESC, id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = get_dict_result(cursor, rows)
    conn.close()
    return result

def get_program_by_id(program_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if IS_POSTGRES else '?'
    
    # Cast to integer for PostgreSQL
    val = int(program_id) if IS_POSTGRES else program_id
    cursor.execute(f"SELECT * FROM programs WHERE id = {placeholder}", (val,))
    row = cursor.fetchone()
    
    result = None
    if row:
        result = get_dict_result(cursor, [row])[0]
    conn.close()
    return result

def get_distinct_regions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT sido FROM programs ORDER BY sido")
    sidos = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT sido, sigungu FROM programs ORDER BY sido, sigungu")
    rows = cursor.fetchall()
    mapping = {}
    for row in rows:
        sido = row[0]
        sigungu = row[1]
        if sido not in mapping:
            mapping[sido] = []
        if sigungu not in mapping[sido]:
            mapping[sido].append(sigungu)
            
    conn.close()
    return sidos, mapping

def insert_program(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = '%s' if IS_POSTGRES else '?'
    cursor.execute(f"SELECT id FROM programs WHERE title = {placeholder} AND organization = {placeholder}", (data['title'], data['organization']))
    exist = cursor.fetchone()
    if exist:
        conn.close()
        return False
        
    placeholders = ', '.join([placeholder] * 17)
    cursor.execute(f'''
        INSERT INTO programs (
            sido, sigungu, organization, announcement_date, title, content,
            link, deadline, budget_size, target_audience, participation_method,
            budget_delivery_type, apply_method, documents, contact_info, hwpx_parsed_text, status
        ) VALUES ({placeholders})
    ''', (
        data['sido'], data['sigungu'], data['organization'], data['announcement_date'], data['title'],
        data['content'], data['link'], data['deadline'], data['budget_size'], data['target_audience'],
        data['participation_method'], data['budget_delivery_type'], data['apply_method'], data['documents'],
        data['contact_info'], data['hwpx_parsed_text'], data.get('status', '모집중')
    ))
    conn.commit()
    conn.close()
    return True
