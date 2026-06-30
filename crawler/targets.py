# 크롤링 대상 사이트 정의 (Targets Definition)

CRAWL_TARGETS = [
    {
        "name": "중소벤처기업부 기업마당",
        "url": "https://www.bizinfo.go.kr/web/lay1/S1T17C18/board/allSupportList.do",
        "type": "gov",
        "sido": "전국",
        "sigungu": "전체",
        "default_org": "중소벤처기업부"
    },
    {
        "name": "경기도청 고시공고",
        "url": "https://www.gg.go.kr/menu.do?menuId=M00085",
        "type": "local_sido",
        "sido": "경기",
        "sigungu": "전체",
        "default_org": "경기도청"
    },
    {
        "name": "수원시청 고시공고",
        "url": "https://www.suwon.go.kr/web/board/BD_board.list.do?bbsCd=1043",
        "type": "local_sigungu",
        "sido": "경기",
        "sigungu": "수원시",
        "default_org": "수원시청"
    },
    {
        "name": "강남구청 고시공고",
        "url": "https://www.gangnam.go.kr/office/gnoffice/board/B_000001/list.do",
        "type": "local_sigungu",
        "sido": "서울",
        "sigungu": "강남구",
        "default_org": "강남구청"
    },
    {
        "name": "경상북도청 고시공고",
        "url": "https://www.gb.go.kr/Main/page.do?mnu_uid=2088",
        "type": "local_sido",
        "sido": "경북",
        "sigungu": "전체",
        "default_org": "경상북도청"
    },
    {
        "name": "울릉군청 고시공고",
        "url": "https://www.ulleung.go.kr/ko/page.htm?mnu_uid=151",
        "type": "local_sigungu",
        "sido": "경북",
        "sigungu": "울릉군",
        "default_org": "울릉군청"
    },
    {
        "name": "부안군청 고시공고",
        "url": "https://www.buan.go.kr/board/list.buan?boardId=B0000016",
        "type": "local_sigungu",
        "sido": "전북",
        "sigungu": "부안군",
        "default_org": "부안군청"
    },
    {
        "name": "해남군청 고시공고",
        "url": "https://www.haenam.go.kr/board/list.haenam?boardId=B0000021",
        "type": "local_sigungu",
        "sido": "전남",
        "sigungu": "해남군",
        "default_org": "해남군청"
    },
    {
        "name": "장성군청 고시공고",
        "url": "https://www.jangseong.go.kr/board/list.jang?boardId=B0000011",
        "type": "local_sigungu",
        "sido": "전남",
        "sigungu": "장성군",
        "default_org": "장성군청"
    },
    {
        "name": "의성군청 고시공고",
        "url": "https://www.usc.go.kr/board/list.usc?boardId=B0000010",
        "type": "local_sigungu",
        "sido": "경북",
        "sigungu": "의성군",
        "default_org": "의성군청"
    },
    {
        "name": "밀양시청 고시공고",
        "url": "https://www.miryang.go.kr/board/list.miry?boardId=B0000012",
        "type": "local_sigungu",
        "sido": "경남",
        "sigungu": "밀양시",
        "default_org": "밀양시청"
    },
    {
        "name": "원주시청 고시공고",
        "url": "https://www.wonju.go.kr/board/list.won?boardId=B0000015",
        "type": "local_sigungu",
        "sido": "강원",
        "sigungu": "원주시",
        "default_org": "원주시청"
    },
    {
        "name": "충주시청 고시공고",
        "url": "https://www.chungju.go.kr/board/list.chung?boardId=B0000022",
        "type": "local_sigungu",
        "sido": "충북",
        "sigungu": "충주시",
        "default_org": "충주시청"
    },
    {
        "name": "완도군청 고시공고",
        "url": "https://www.wando.go.kr/board/list.wando?boardId=B0000030",
        "type": "local_sigungu",
        "sido": "전남",
        "sigungu": "완도군",
        "default_org": "완도군청"
    },
    {
        "name": "진도군청 고시공고",
        "url": "https://www.jindo.go.kr/board/list.jindo?boardId=B0000033",
        "type": "local_sigungu",
        "sido": "전남",
        "sigungu": "진도군",
        "default_org": "진도군청"
    },
    {
        "name": "여수시청 고시공고",
        "url": "https://www.yeosu.go.kr/board/list.yeosu?boardId=B0000028",
        "type": "local_sigungu",
        "sido": "전남",
        "sigungu": "여수시",
        "default_org": "여수시청"
    },
    # --- 주요 광역 경제진흥원 타겟 ---
    {
        "name": "서울경제진흥원 사업공고",
        "url": "https://sba.seoul.kr/Pages/Contents/Business_Notice.aspx",
        "type": "agency",
        "sido": "서울",
        "sigungu": "전체",
        "default_org": "서울경제진흥원"
    },
    {
        "name": "부산경제진흥원 사업공고",
        "url": "https://www.bepa.kr/kor/html/sub04/sub04_01.php",
        "type": "agency",
        "sido": "부산",
        "sigungu": "전체",
        "default_org": "부산경제진흥원"
    },
    {
        "name": "경남투자경제진흥원 사업공고",
        "url": "https://www.gipa.or.kr/contents/business/business_notice.do",
        "type": "agency",
        "sido": "경남",
        "sigungu": "전체",
        "default_org": "경남투자경제진흥원"
    },
    {
        "name": "전북특별자치도 경제통상진흥원",
        "url": "https://www.jbba.kr/contents/business/business_notice.do",
        "type": "agency",
        "sido": "전북",
        "sigungu": "전체",
        "default_org": "전북특별자치도 경제통상진흥원"
    },
    {
        "name": "대전일자리경제진흥원 사업공고",
        "url": "https://www.djbea.or.kr/biz/notice.do",
        "type": "agency",
        "sido": "대전",
        "sigungu": "전체",
        "default_org": "대전일자리경제진흥원"
    },
    {
        "name": "경북경제진흥원 사업공고",
        "url": "https://www.gepa.kr/contents/business/business_notice.do",
        "type": "agency",
        "sido": "경북",
        "sigungu": "전체",
        "default_org": "경상북도경제진흥원"
    },
    {
        "name": "소상공인24 통합 공고",
        "url": "https://www.sbiz24.kr/co/main.do",
        "type": "gov",
        "sido": "전국",
        "sigungu": "전체",
        "default_org": "소상공인시장진흥공단"
    }
]

# 크롤링에 매칭시킬 키워드 목록
KEYWORDS = [
    "소상공인", "자영업자", "전통시장", "점포 개선", "마케팅 지원", "카드수수료", 
    "이차보전", "경영개선", "물류비", "온라인쇼핑", "온라인 판로", "쇼핑몰 입점", "e커머스",
    "소담스퀘어", "e경남몰", "라이브커머스", "상세페이지"
]
