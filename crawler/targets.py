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
    }
]

# 크롤링에 매칭시킬 키워드 목록
KEYWORDS = ["소상공인", "자영업자", "전통시장", "점포 개선", "마케팅 지원", "카드수수료", "이차보전", "경영개선", "물류비"]
