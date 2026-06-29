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
    
    # Check if table has data. If empty, insert rich seed data.
    cursor.execute("SELECT COUNT(*) FROM programs")
    count = cursor.fetchone()[0]
    
    if count == 0:
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
