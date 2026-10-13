import io
import re
import zipfile
from datetime import datetime, timedelta

def clean_filename(title):
    """Sanitizes titles for safe file system naming."""
    clean = re.sub(r'[\\/*?:"<>|]', "", str(title)).strip()
    clean = re.sub(r'\s+', "_", clean)
    return clean[:60]

def extract_notice_number(hwpx_parsed_text, default_year="2026", default_id=1):
    """Extracts official notice number from text or generates a realistic one."""
    if hwpx_parsed_text:
        match = re.search(r'제\s*(\d{4}[-~]\w+호|\d+[-~]\w+호|\w+호)', hwpx_parsed_text)
        if match:
            return match.group(0)
    return f"제{default_year}-{int(default_id):02d}호"

def get_product_context(title, hwpx_parsed_text):
    """Detects product type and derives appropriate specs and evaluation points."""
    combined = (str(title) + " " + str(hwpx_parsed_text)).lower()
    
    if '온누리' in combined:
        return {
            'category': '온누리상품권',
            'item_name': '전통시장 온누리상품권 (모바일/지류/카드형)',
            'qualification_extra': '소상공인시장진흥공단 및 중소벤처기업부 지정 온누리상품권 공식 취급·판매 수탁 금융기관 또는 공인 유통 대행 자격 보유사',
            'spec_detail': '임직원별 50,000원~100,000원 권종 맞춤형 지급, 지류형 상품권의 일련번호 보안 배송 및 모바일 충전 솔루션 무상 연계 지원',
            'packaging': '개별 고급 상품권 전용 봉투 및 감사 메시지 카드 동봉, 특수 보안 등기 배송',
            'cs_plan': '모바일 온누리상품권 등록 미숙자 전담 유선 상담 및 지류 상품권 수령 누락 시 24시간 이내 즉시 재배송'
        }
    elif any(k in combined for k in ('기프티콘', '쿠폰', '모바일 상품권', '모바일형')):
        return {
            'category': '모바일상품권',
            'item_name': '임직원 선택형 모바일 기프티콘 및 백화점·외식 상품권',
            'qualification_extra': '모바일 쿠폰 실시간 대량 발송 및 MMS 재발송 API 연동 서버 시스템을 보유한 전문 공급 사업자',
            'spec_detail': '신세계·롯데 등 주요 백화점, 베이커리(파리바게뜨 등), 커피(스타벅스 등) 15종 이상의 선택형 기프트 옵션 모바일 웹 주문 시스템 제공',
            'packaging': '모바일 MMS 브랜드 맞춤형 카드 템플릿(기업 로고 및 축하 문구 반영) 제작 및 발송',
            'cs_plan': '번호 변경, 스팸 차단에 따른 미수신자 대상 1:1 전담 CS 콜센터 운영 및 실시간 교환율 대시보드 리포팅 제공'
        }
    elif any(k in combined for k in ('한우', '육류', '갈비', '고기')):
        return {
            'category': '명품 한우/육류세트',
            'item_name': '1등급 이상 한우 명품 냉장/냉동 선물세트',
            'qualification_extra': '축산물가공업 및 식육포장처리업 영업허가 필, HACCP(식품안전관리인증) 인증 보유, 전국 콜드체인(냉장/냉동) 직배송망 보유 업체',
            'spec_detail': '국내산 1등급 이상 한우(등심, 안심, 불고기, 국거리 등 1.5kg~2.0kg 이상 구성), 도축검사증명서 및 등급판정확인서 원본 동봉',
            'packaging': '친환경 3중 보냉 가방, 특수 항균 진공 스킨 포장, 드라이아이스 및 아이스팩 완비',
            'cs_plan': '명절 배송 기간 중 해동/변질 시 100% 즉시 무상 맞교환 및 회수 보증, 24시간 실시간 배송 트래킹'
        }
    elif any(k in combined for k in ('사과', '배', '농산물', '과일', '버섯', '곶감')):
        return {
            'category': '농산물/과일세트',
            'item_name': '고당도 프리미엄 제철 과일 및 특산품 세트',
            'qualification_extra': '농산물 유통전문판매업 또는 산지 직송 농업회사법인, GAP(우수농산물관리) 인증 보유 및 당도 선별 시스템 구축 업체',
            'spec_detail': '사과(홍로/후지) 및 배(신고) 13브릭스(Brix) 이상 엄선 대과 세트(총 6kg~7.5kg 이상), 산지 직송 신선도 보증',
            'packaging': '충격 흡수 3중 에어캡 패드 및 고급 골판지 선물용 상자, 감사 리본 포장',
            'cs_plan': '운송 중 표면 흠집/뭉개짐 발생 시 사진 접수 즉시 당일 재발송 및 신속 보상 처리'
        }
    elif any(k in combined for k in ('수산물', '굴비', '생선', '옥돔', '김')):
        return {
            'category': '수산물/굴비세트',
            'item_name': '영광 법성포 굴비 및 프리미엄 수산물 세트',
            'qualification_extra': '수산물가공업 등록 및 원산지 이력 추적 시스템 연계 업체, 위생 급속 냉동 보관 인프라 보유 업체',
            'spec_detail': '100% 국내산 참조기/옥돔 엄선, 섶간 및 자연 해풍 건조, 10미 이상(두름) 규격 보장',
            'packaging': '친환경 보냉가방 및 진공 개별 지퍼백 포장, 보냉제 완비',
            'cs_plan': '신선도 유지 실패 및 냄새 클레임 발생 시 즉각 1대1 회수 및 교환 처리'
        }
    elif any(k in combined for k in ('청소기', '가전', '마사지기', '인덕션')):
        return {
            'category': '생활가전세트',
            'item_name': '프리미엄 소형 생활가전 및 헬스케어 기기',
            'qualification_extra': '국내 KC 안전인증 획득 제품 공급 자격 및 제조사/총판 공식 라이선스 보유 업체, 전국 A/S망 보유사',
            'spec_detail': '무선청소기, 공기청정기, 저주파 마사지기 등 임직원 선호 최신형 모델 (출시 1년 이내 정품)',
            'packaging': '완충 완비 선물 패키지 상자 및 전용 쇼핑백 동봉',
            'cs_plan': '1년 무상 품질보증(A/S) 제공 및 초기 불량 시 7일 이내 즉시 새 제품 맞교환'
        }
    else:
        return {
            'category': '종합선물세트',
            'item_name': '임직원 맞춤형 선택식 프리미엄 선물세트 (건강식품/특산물/생활)',
            'qualification_extra': '식품유통전문판매업 및 통신판매업 영업신고 필, 최근 3개년 공공기관 및 대기업 단체선물 납품 실적 보유 업체',
            'spec_detail': '6년근 홍삼농축액, 침향환, 프리미엄 쿡웨어, 특산 가공식품 등 5~8종 선택형 패키지 제공',
            'packaging': '고급 하드케이스 지함 선물 상자 및 친환경 포장재 적용',
            'cs_plan': '오배송 방지 2중 바코드 검수 시스템 적용 및 전담 콜센터 운영'
        }

def generate_full_bid_bundle(item, tab='b2b_gift'):
    """
    Generates complete multi-page authoritative documents and attachments bundle
    for a bid or support program.
    """
    is_gift = (tab == 'b2b_gift')
    
    # Common metadata extraction
    org = item.get('institution') if is_gift else item.get('organization', '해당기관')
    title = item.get('title', '공고문')
    ann_date = item.get('announcement_date', '2026-06-01')
    deadline = item.get('deadline', '2026-07-01')
    budget = item.get('budget') if is_gift else item.get('budget_size', '예산 범위 내')
    dept = item.get('department') if is_gift else '소상공인지원팀'
    manager = item.get('manager') if is_gift else '사업담당자'
    contact = item.get('contact') if is_gift else item.get('contact_info', '02-0000-0000')
    raw_hwpx = item.get('hwpx_parsed_text', '')
    doc_id = item.get('id', 1)
    
    notice_no = extract_notice_number(raw_hwpx, "2026", doc_id)
    ctx = get_product_context(title, raw_hwpx)
    clean_t = clean_filename(title)
    
    # Calculate delivery/completion estimated date
    try:
        d_obj = datetime.strptime(str(deadline).split()[0].replace('.', '-').replace('/', '-'), '%Y-%m-%d')
        delivery_date = (d_obj + timedelta(days=25)).strftime('%Y년 %m월 %d일')
    except Exception:
        delivery_date = "계약 체결일로부터 30일 이내"

    # =========================================================================
    # 1. 입찰공고문 전문 (Announcement Document)
    # =========================================================================
    announcement_text = f"""【{org} 공고 {notice_no}】

{title}

{org} 임직원의 사기 진작과 복리후생 향상 및 지역 상생 가치 실현을 위하여 추진하는 『{title}』의 공급 협력 사업자 선정을 위하여 다음과 같이 입찰 공고합니다.

2026년 {ann_date.split('-')[1]}월 {ann_date.split('-')[2]}일
{org} 계약담당관

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 입찰에 부치는 사항
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 사 업 명: {title}
  나. 발주기관: {org} ({dept})
  다. 사업예산: {budget} (부가가치세, 포장비, 전국 개별 배송비 일체 포함)
  라. 품목구분: {ctx['category']} ({ctx['item_name']})
  마. 납품기한: {delivery_date}까지
  바. 납품장소: 본사/지사 지정 장소 또는 임직원 개별 자택(가호) 직배송
  사. 계약방법: 일반경쟁입찰 (협상에 의한 계약)
      - 국가를 당사자로 하는 계약에 관한 법률 시행령 제43조 준용
  아. 입찰방식: 전자입찰 (나라장터 G2B 및 발주사 전자조달시스템 연동)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. 입찰 참가 자격 (모두 충족하여야 함)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 『국가를 당사자로 하는 계약에 관한 법률 시행령』 제12조 및 동법 시행규칙 제14조의 규정에 의한 유자격자
  나. 국가종합전자조달시스템(나라장터 G2B)에 입찰참가자격 등록을 필한 업체
  다. 『중소기업기본법』 제2조에 따른 중·소기업자 또는 『소상공인기본법』 제2조에 따른 소상공인확인서를 보유한 자
  라. 품목별 특별 참가자격:
      - {ctx['qualification_extra']}
  마. 입찰공고일 기준 부정당업자로 지정되어 입찰 참가자격 제한 기간 중에 있지 아니한 자
  바. 공동수급(공동이행방식)은 불허합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. 입찰참가등록 및 제안서 접수
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 공고기간: {ann_date} ~ {deadline}
  나. 제안서 접수마감: {deadline} 18:00까지
  다. 제출방법: 전자입찰서(G2B) 및 제안서 전자파일(PDF) 온라인 제출
  라. 제출서류 목록:
      1) 입찰참가신청서 1부 [서식 제1호]
      2) 제안서 및 요약본 전자파일 각 1부
      3) 가격제안서 및 품목별 세부단가산출내역서 1부 [서식 제4호] (전자 밀봉)
      4) 사업자등록증 사본, 법인등기부등본, 인감증명서 각 1부
      5) 중·소기업 또는 소상공인확인서 1부
      6) 신용평가등급확인서 및 최근 3년간 유사 납품 실적증명원 각 1부
      7) 청렴계약이행서약서 및 개인정보 수집·이용 동의서 각 1부

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. 낙찰자 결정 방법 (협상에 의한 계약)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 기술능력평가(80점)와 입찰가격평가(20점)를 종합 합산하여 고득점 순으로 협상 적격자를 선정합니다.
  나. 기술능력평가 분야 배점한도의 85%(68점) 이상인 자를 협상적격자로 선정합니다.
  다. 합산점수가 동일한 경우 기술능력평가 고득점자를 우선협상자로 지정하며, 기술평가 점수도 동일한 경우 정성평가 고배점 항목 순으로 결정합니다.
  라. 1차 서류 평가 상위 업체를 대상으로 견본품(샘플) 실물 품평회를 개최하며, 임직원 블라인드 선호도 투표 점수가 정성평가에 반영됩니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. 입찰보증금 납부 및 국고귀속
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 입찰보증금은 국가계약법 시행령 제37조에 따라 입찰참가신청서 상의 보증금 지급확약으로 갈음합니다.
  나. 낙찰자가 정당한 이유 없이 계약을 체결하지 아니할 때에는 입찰금액의 100분의 5에 해당하는 금액을 당사에 현금 납부하여야 합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. 입찰의 무효 및 청렴계약 준수
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 국가계약법 시행령 제39조 제4항 및 동법 시행규칙 제44조의 규정에 해당하는 입찰은 무효로 합니다.
  나. 본 입찰에 참가하는 모든 업체는 담합 및 금품 수수 금지 청렴계약이행서약서를 제출하여야 합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. 문의처 및 안내
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  가. 입찰 및 계약 관련 문의: {dept} 계약담당 ({manager}, ☎ {contact})
  나. 과업내용 및 제안서 관련 문의: {dept} 복리후생지원파트 (☎ {contact})
"""

    # =========================================================================
    # 2. 제안요청서 (RFP - Request for Proposal)
    # =========================================================================
    rfp_text = f"""【제안요청서 (RFP)】

사업명: {title}
발주기관: {org}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I. 사업 개요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 사업 목적:
   - {org} 임직원의 노고를 격려하고 명절 및 기념일 만족도를 극대화할 수 있는 우수 품질의 선물을 공정하고 투명하게 조달
   - 임직원의 선택권을 존중하고 안전한 배송망과 신속한 사후 CS를 통해 무결점 복지 서비스 구현

2. 사업 개요:
   - 사 업 명: {title}
   - 사업예산: {budget} (VAT, 배송비 일체 포함)
   - 소요수량: 전사 임직원 배부 기준 (단가 및 수량 분할 계약 가능)
   - 주요품목: {ctx['item_name']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
II. 세부 과업 제안 요구사항
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 상품 구성 및 품질 요건:
   - 세부규격: {ctx['spec_detail']}
   - 원자재의 신선도 및 정품 보증, 유효기간 넉넉한 최신 생산품 공급 원칙
   - 품질 검사 성적서, 원산지 증명서, 안전 인증 서류 필수 제출

2. 포장 및 물류 배송 기준:
   - 패키징: {ctx['packaging']}
   - 전국 임직원 개별 자택(가호) 택배 발송 및 실시간 송장 추적 SMS/알림톡 발송
   - 명절 특수기 택배 물류 대란 대비 사전 물량 확보 및 3단계 분산 출고 계획 수립

3. CS(고객지원) 및 사후 관리 계획:
   - CS 전담: {ctx['cs_plan']}
   - 불량, 오배송, 파손 발생 시 접수 후 24시간 이내 즉시 무상 맞교환 및 회수 프로세스 가동

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
III. 제안서 작성 요령
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 규격 및 분량: A4 횡/종 규격, 본문 50페이지 이내 (요약본 10페이지 별도)
2. 작성 목차:
   제1장: 제안 개요 (추진 배경, 목표, 기대 효과)
   제2장: 제안사 일반 역량 (회사 소개, 재무상태, 최근 3개년 주요 납품 실적)
   제3장: 상품 기획 및 품질 보증 (품목 구성, 단가 적정성, 원재료 관리, 패키지 디자인)
   제4장: 배송 및 물류 관리 (전국 배송망, 보냉/콜드체인, 납품 일정표)
   제5장: CS 센터 운영 및 비상 대응 대책 (교환/환불 처리, 하자 대응 체계)
   제6장: 상생협력 및 추가 제안 (ESG 공헌, 친환경 포장 등)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IV. 제안서 평가 항목 및 상세 배점표 (총 100점)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1. 정량적 평가 분야 (20점)]
  ① 경영상태 (신용평가등급): 10점
     - AAA ~ AA: 10점 | A: 9.5점 | BBB: 9.0점 | BB: 8.5점 | B: 8.0점 | CCC 이하: 7.0점
  ② 최근 3개년 유사 납품 수행실적: 10점
     - 5억원 이상: 10점 | 3억원 ~ 5억원 미만: 9.0점 | 1억원 ~ 3억원 미만: 8.0점 | 1억원 미만: 7.0점

[2. 정성적 평가 분야 (60점)]
  ① 상품 구성의 우수성 및 가격 적정성: 20점
  ② 원재료 품질 신뢰성 및 위생안전관리 체계: 15점
  ③ 전국 배송 물류 인프라 및 일정 준수 계획: 15점
  ④ 전담 CS 콜센터 운영 및 사후 보증 대응책: 10점

[3. 입찰가격 평가 분야 (20점)]
  - 기획재정부 계약예규 『협상에 의한 계약체결기준』 입찰가격 평점산식 적용

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V. 실물 견본품(샘플) 품평회 안내
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 제출 대상: 1차 서류 심사 통과 상위 업체 (개별 통보)
2. 제출 품목: 제안서에 명시된 실제 완제품 및 포장 박스 견본품 각 1세트
3. 심사 방식: 임직원 품평 평가단 블라인드 현장 심사 및 선호도 투표 (정성평가에 반영)
"""

    # =========================================================================
    # 3. 과업지시서 및 물품규격서 (Specification)
    # =========================================================================
    spec_text = f"""【과업지시서 및 물품규격서】

건명: {title}
발주처: {org}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 총칙 및 과업 목적
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
본 과업지시서는 {org}가 시행하는 『{title}』에 대하여 계약상대자가 이행하여야 할 물품 조달, 포장, 물류 배송, 고객 상담, 사후 품질보증 등에 관한 세부 사항을 규정함을 목적으로 한다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. 물품 사양 및 규격
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
가. 품목명: {ctx['item_name']}
나. 물품 사양: {ctx['spec_detail']}
다. 포장 사양: {ctx['packaging']}
라. 모든 제품은 최근 생산된 정품이어야 하며 위생 법규 및 안전 기준을 완벽히 충족하여야 한다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. 배송 및 납품 조건
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
가. 계약상대자는 {org}로부터 제공받은 임직원 배송지 목록을 바탕으로 안전하게 개별 직배송하여야 한다.
나. 배송 완료 기한은 {delivery_date}까지로 하며, 발송 후 송장번호를 시스템에 등록하여야 한다.
다. 배송 중 파손, 분실, 변질이 발생할 경우 계약상대자의 비용으로 24시간 이내 즉시 재배송하여야 한다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. 검수 및 대금 지급
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
가. 납품 완료 후 전수 검수 및 배송 완료 증빙 보고서를 제출하여야 한다.
나. 검수 합격 후 계약상대자의 전자세금계산서 청구일로부터 14일 이내에 계약금액을 지급한다.
다. 정당한 사유 없이 납품을 지연할 경우 지체 1일당 계약금액의 1,000분의 0.75에 해당하는 지체상금을 부과한다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. 보안 및 개인정보 보호
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
계약상대자는 제공받은 임직원의 성명, 주소, 연락처 등 개인정보를 배송 목적 외에 절대 유출 또는 사용하여서는 아니 되며, 과업 종료 즉시 전량 파기하고 파기확인서를 제출하여야 한다.
"""

    # =========================================================================
    # 4. 입찰참가 제출서식 모음 (Application Forms)
    # =========================================================================
    forms_text = f"""【입찰참가 제출서식 모음집】

사업명: {title}
발주기관: {org}

[서식 제1호] 입찰참가신청서
────────────────────────────────────────────────────────────
1. 신청인 정보
  - 상호(법인명):                           - 사업자등록번호:
  - 대표자 성명:                           - 법인등록번호:
  - 주        소:
  - 전 화 번 호:                           - 담당자/휴대폰:

2. 입찰개요
  - 입찰공고번호: {notice_no}
  - 입 찰 건 명: {title}
  - 입찰보증금: 국가계약법 시행령 제37조에 의거 지급확약서 제출로 갈음함

본인은 귀 사의 입찰공고, 제안요청서 및 계약조건을 전적으로 수락하고 상기 입찰에 참가하고자 신청서를 제출합니다.

2026년    월    일
신청인 (대표자):                   (인/직인)
{org} 귀중
────────────────────────────────────────────────────────────

[서식 제2호] 제안사 일반현황 및 주요 연혁
────────────────────────────────────────────────────────────
  - 회사명:                               - 설립년월일:
  - 대표자:                               - 종업원 수:       명
  - 주요 사업분야:                        - 자본금:          백만원
  - 최근 3개년 매출액: 2023년(     백만원) / 2024년(     백만원) / 2025년(     백만원)
  - 주요 보유 면허/인증: (HACCP, ISO, 우수농산물, 통신판매업 등)
────────────────────────────────────────────────────────────

[서식 제3호] 최근 3개년 주요 사업 납품 실적 집계표
────────────────────────────────────────────────────────────
연번 | 발주기관(기업명) | 사업명(품목) | 계약금액(원) | 계약기간 | 비고
 1   |                  |              |              |          |
 2   |                  |              |              |          |
 3   |                  |              |              |          |
────────────────────────────────────────────────────────────

[서식 제4호] 가격제안서 및 품목별 세부단가산출내역서
────────────────────────────────────────────────────────────
품목명: {ctx['item_name']}
제안금액(총액): 금                      원 (VAT 포함)
세부 내역:
  - 품목 단가:            원 x 수량:        개 = 금            원
  - 포장비 및 부자재:                           = 금            원
  - 전국 개별 택배배송비:                       = 금            원
  - 부가가치세(VAT):                            = 금            원
────────────────────────────────────────────────────────────

[서식 제5호] 청렴계약이행서약서
────────────────────────────────────────────────────────────
당사는 부패 없는 투명한 기업경영과 공정한 입찰 질서 확립을 위하여 {org}가 발주하는 『{title}』 입찰에 참가함에 있어 어떠한 불공정 행위나 금품·향응 제공을 하지 않을 것을 서약합니다.
────────────────────────────────────────────────────────────

[서식 제6호] 개인정보 수집·이용 및 제3자 제공 동의서
────────────────────────────────────────────────────────────
본 입찰과 관련하여 {org}가 본인의 개인정보(성명, 생년월일, 연락처 등)를 수집 및 이용하는 것에 동의합니다.
"""

    # Combined Full Text
    full_combined_text = f"""================================================================================
【전체 입찰 공고문 통합본】
발주기관: {org} | 공고번호: {notice_no}
사업명: {title}
공고일자: {ann_date} | 접수마감일자: {deadline}
예산규모: {budget}
================================================================================

[목차]
제1편. 입찰공고문 전문
제2편. 제안요청서 (RFP) 전문
제3편. 과업지시서 및 물품규격서
제4편. 입찰참가 제출서식 모음 (서식 1호~6호)

================================================================================
[제1편. 입찰공고문 전문]
================================================================================
{announcement_text}

================================================================================
[제2편. 제안요청서 (RFP) 전문]
================================================================================
{rfp_text}

================================================================================
[제3편. 과업지시서 및 물품규격서]
================================================================================
{spec_text}

================================================================================
[제4편. 입찰참가 제출서식 모음]
================================================================================
{forms_text}
"""

    # =========================================================================
    # HTML Formatted Sections for Premium Rendering in Viewers
    # =========================================================================
    def text_to_html(raw):
        lines = raw.split('\n')
        out = []
        for l in lines:
            s = l.strip()
            if not s:
                out.append('<div class="py-1"></div>')
            elif s.startswith('【') or s.startswith('['):
                out.append(f'<div class="hwp-section-title mt-4 mb-2">{l}</div>')
            elif s.startswith('━') or s.startswith('═') or s.startswith('─'):
                out.append('<hr style="border-top: 1px dashed #9ca3af; margin: 12px 0;">')
            elif any(s.startswith(prefix) for prefix in ('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', 'I.', 'II.', 'III.', 'IV.', 'V.')):
                out.append(f'<h5 class="fw-bold text-dark mt-3 mb-2">{l}</h5>')
            elif any(s.startswith(prefix) for prefix in ('가.', '나.', '다.', '라.', '마.', '바.', '사.', '아.', '-', '①', '②', '③', '④')):
                out.append(f'<p class="mb-1 ms-3" style="line-height: 1.7;">{l}</p>')
            elif s.startswith('연번') or '|' in s:
                cols = [c.strip() for c in s.split('|')]
                tds = ''.join([f'<td class="border p-2">{c}</td>' for c in cols])
                out.append(f'<table class="table table-bordered table-sm my-2"><tr class="bg-light">{tds}</tr></table>')
            else:
                out.append(f'<p class="mb-1" style="line-height: 1.7;">{l}</p>')
        return '\n'.join(out)

    html_announcement = text_to_html(announcement_text)
    html_rfp = text_to_html(rfp_text)
    html_spec = text_to_html(spec_text)
    html_forms = text_to_html(forms_text)
    html_full = f"""
    <div class="hwp-doc-unified">
        <div class="alert alert-info border-info d-flex align-items-center justify-content-between mb-4">
            <div>
                <i class="fa-solid fa-file-shield text-primary me-2 fs-5"></i>
                <strong>공고문 통합 뷰어</strong>: 입찰공고문, 제안요청서(RFP), 과업지시서, 입찰서식이 통합 수록된 표준 문서입니다.
            </div>
            <a href="/download_doc/{doc_id}?tab={tab}&file_type=zip" class="btn btn-sm btn-success fw-semibold text-white">
                <i class="fa-solid fa-file-zipper me-1"></i> 전체 ZIP 다운로드
            </a>
        </div>
        <div class="border-bottom pb-3 mb-4">
            <h4 class="fw-bold text-primary mb-2">📑 제1편. 입찰공고문 전문</h4>
            {html_announcement}
        </div>
        <div class="border-bottom pb-3 mb-4">
            <h4 class="fw-bold text-primary mb-2">📋 제2편. 제안요청서 (RFP) 전문</h4>
            {html_rfp}
        </div>
        <div class="border-bottom pb-3 mb-4">
            <h4 class="fw-bold text-primary mb-2">📦 제3편. 과업지시서 및 물품규격서</h4>
            {html_spec}
        </div>
        <div class="pb-3">
            <h4 class="fw-bold text-primary mb-2">📝 제4편. 입찰참가 제출서식 모음</h4>
            {html_forms}
        </div>
    </div>
    """

    # Attachments Metadata List
    attachments_list = [
        {
            "id": "zip",
            "name": f"[전체첨부파일]_{org}_{clean_t}.zip",
            "display_name": "전체 첨부파일 일괄 압축팩 (ZIP)",
            "type": "zip",
            "size": "240 KB",
            "badge": "일괄다운로드",
            "badge_class": "bg-success",
            "desc": "입찰공고문, 제안요청서(RFP), 과업지시서, 서식집 전체 패키지",
            "download_url": f"/download_doc/{doc_id}?tab={tab}&file_type=zip"
        },
        {
            "id": "announcement",
            "name": f"[입찰공고문]_{org}_{clean_t}.hwpx",
            "display_name": "01. 입찰공고문 전문",
            "type": "hwpx",
            "size": "45 KB",
            "badge": "HWPX",
            "badge_class": "bg-primary",
            "desc": "입찰참가자격, 마감일정, 낙찰자 결정방법 등 공고 전문",
            "download_url": f"/download_doc/{doc_id}?tab={tab}&file_type=announcement"
        },
        {
            "id": "rfp",
            "name": f"[제안요청서]_{org}_{clean_t}_RFP.hwpx",
            "display_name": "02. 제안요청서 (RFP)",
            "type": "hwpx",
            "size": "118 KB",
            "badge": "HWPX",
            "badge_class": "bg-primary",
            "desc": "세부과업규격, 제안서 작성지침, 평가항목 및 상세 배점표",
            "download_url": f"/download_doc/{doc_id}?tab={tab}&file_type=rfp"
        },
        {
            "id": "spec",
            "name": f"[과업지시서]_{org}_{clean_t}_과업지시서.hwpx",
            "display_name": "03. 과업지시서 및 물품규격서",
            "type": "hwpx",
            "size": "52 KB",
            "badge": "HWPX",
            "badge_class": "bg-primary",
            "desc": "물품 규격서, 전국 배송 및 보냉 기준, 사후 CS 기준",
            "download_url": f"/download_doc/{doc_id}?tab={tab}&file_type=spec"
        },
        {
            "id": "forms",
            "name": f"[입찰서식]_{org}_{clean_t}_제출서식모음.hwpx",
            "display_name": "04. 입찰참가 제출서식집",
            "type": "hwpx",
            "size": "36 KB",
            "badge": "HWPX",
            "badge_class": "bg-primary",
            "desc": "입찰참가신청서, 실적증명원, 가격제안서 등 서식 1호~6호",
            "download_url": f"/download_doc/{doc_id}?tab={tab}&file_type=forms"
        },
        {
            "id": "txt",
            "name": f"[통합전문]_{org}_{clean_t}_전체공고문.txt",
            "display_name": "05. 공고문 전체 통합본 (TXT)",
            "type": "txt",
            "size": "18 KB",
            "badge": "TXT",
            "badge_class": "bg-secondary",
            "desc": "공고문 및 제안요청서 전체가 포함된 통합 텍스트 파일",
            "download_url": f"/download_doc/{doc_id}?tab={tab}&file_type=txt"
        }
    ]

    return {
        'announcement': announcement_text,
        'rfp': rfp_text,
        'specification': spec_text,
        'forms': forms_text,
        'full_text': full_combined_text,
        'html_sections': {
            'full': html_full,
            'announcement': html_announcement,
            'rfp': html_rfp,
            'specification': html_spec,
            'forms': html_forms
        },
        'attachments_list': attachments_list
    }

def create_hwpx_bytes(title, text):
    """
    Constructs a standard, compliant Hancom HWPX file container in memory.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. mimetype (must be uncompressed)
        z.writestr('mimetype', 'application/hwp+zip', compress_type=zipfile.ZIP_STORED)
        
        # 2. META-INF/container.xml
        container_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container">
    <ocf:rootfiles>
        <ocf:rootfile ocf:full-path="Contents/content.hpf" ocf:media-type="application/hwp+zip"/>
    </ocf:rootfiles>
</ocf:container>'''
        z.writestr('META-INF/container.xml', container_xml)
        
        # 3. version.xml
        version_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<hh:version xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" major="1" minor="0" micro="0" buildNumber="0" os="1"/>'''
        z.writestr('version.xml', version_xml)
        
        # 4. Contents/content.hpf
        clean_t = str(title).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        content_hpf = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<opf:package xmlns:opf="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
    <opf:metadata>
        <opf:title>{clean_t}</opf:title>
        <opf:language>ko</opf:language>
    </opf:metadata>
    <opf:manifest>
        <opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>
    </opf:manifest>
    <opf:spine>
        <opf:itemref idref="section0"/>
    </opf:spine>
</opf:package>'''
        z.writestr('Contents/content.hpf', content_hpf)
        
        # 5. Contents/section0.xml
        paras = []
        for line in text.split('\n'):
            line_esc = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            paras.append(f'<hp:p><hp:run><hp:t>{line_esc}</hp:t></hp:run></hp:p>')
        
        section0_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<hp:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
''' + '\n'.join(paras) + '''
</hp:sec>'''
        z.writestr('Contents/section0.xml', section0_xml)
        
    buf.seek(0)
    return buf

def create_bid_zip_bytes(item, tab='b2b_gift'):
    """
    Creates a ZIP archive containing all attached documents:
    - 01_입찰공고문.hwpx
    - 02_제안요청서.hwpx
    - 03_과업지시서.hwpx
    - 04_입찰서식.hwpx
    - 05_전체공고문_통합전문.txt
    - 06_공고_개요_안내.txt
    """
    bundle = generate_full_bid_bundle(item, tab=tab)
    is_gift = (tab == 'b2b_gift')
    org = item.get('institution') if is_gift else item.get('organization', '기관')
    clean_t = clean_filename(item.get('title', '공고'))
    
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
        # Write HWPX files
        z.writestr(f"01_[입찰공고문]_{org}_{clean_t}.hwpx", create_hwpx_bytes(f"입찰공고문 - {clean_t}", bundle['announcement']).getvalue())
        z.writestr(f"02_[제안요청서]_{org}_{clean_t}_RFP.hwpx", create_hwpx_bytes(f"제안요청서 - {clean_t}", bundle['rfp']).getvalue())
        z.writestr(f"03_[과업지시서]_{org}_{clean_t}_과업지시서.hwpx", create_hwpx_bytes(f"과업지시서 - {clean_t}", bundle['specification']).getvalue())
        z.writestr(f"04_[제출서식]_{org}_{clean_t}_입찰참가서식.hwpx", create_hwpx_bytes(f"입찰참가서식 - {clean_t}", bundle['forms']).getvalue())
        
        # Write TXT files
        z.writestr(f"05_[통합전문]_{org}_{clean_t}_전체공고문.txt", bundle['full_text'].encode('utf-8'))
        
        # Readme / Guide
        readme = f"""================================================================================
【입찰 공고문 첨부파일 안내】
발주기관: {org}
공고명: {item.get('title')}
공고일자: {item.get('announcement_date')} | 마감일자: {item.get('deadline')}
================================================================================

본 압축 파일에는 다음 5개 첨부문서가 포함되어 있습니다:
1. 01_[입찰공고문]_{org}_{clean_t}.hwpx
   - 입찰참가자격, 마감일시, 낙찰자 결정방법 등 입찰공고문 전문
2. 02_[제안요청서]_{org}_{clean_t}_RFP.hwpx
   - 제안요청 세부내용, 제안서 작성지침, 평가항목 및 상세 배점표
3. 03_[과업지시서]_{org}_{clean_t}_과업지시서.hwpx
   - 물품 사양, 배송 및 납품 조건, 검수 절차 및 CS 기준
4. 04_[제출서식]_{org}_{clean_t}_입찰참가서식.hwpx
   - 입찰참가신청서(서식1호), 실적증명원(서식3호), 가격제안서(서식4호), 청렴계약서약서 등
5. 05_[통합전문]_{org}_{clean_t}_전체공고문.txt
   - 모든 공고문 및 제안요청서가 수록된 통합 텍스트 파일

※ 본 파일은 Smallbiz & Gift-monitor 통합 시스템에서 생성되었습니다.
"""
        z.writestr(f"00_[첨부파일목록안내]_{clean_t}.txt", readme.encode('utf-8'))
        
    zip_buf.seek(0)
    return zip_buf
