# 담장너머교회 홈페이지

정적 HTML 사이트입니다. 서버·DB·로그인 없이 GitHub Pages로 공개됩니다.
https://www.damjangch.org/

## 구조
```
_src/                      ← 원본 (사이트에 직접 보이지 않음)
  build.py                 ← 원본으로 사이트 파일을 만드는 스크립트
  pages/*.html             ← 페이지 본문
  static/style.css, main.js
  data/bulletins/YYYY-MM-DD.json   ← 주보 한 주 = 파일 하나
  data/sermons.json        ← 유튜브 설교 목록 (최신이 위)

*.html, bulletins/, css/, js/   ← build.py가 만든 결과물 (직접 고치지 않기)
assets/                    ← 이미지
```

| 페이지 | 내용 |
|---|---|
| index.html | 홈. "이번 주 말씀"은 설교 목록 맨 위 영상 |
| about.html | 교회 소개 |
| worship.html | 예배와 모임. 예배 순서는 최신 주보에서 자동 |
| news.html | 교회 소식. 최신 주보 + 지난 주보 목록 |
| bulletins/YYYY-MM-DD.html | 주보별 전체 (소식, 일정, 예배 순서, 설교, 책, 경건생활) |
| bulletins/index.html | 지난 주보 전체 목록 |
| sermons.html | 설교 영상 + 요약. `sermons.html?v=영상ID`로 특정 설교 바로 열기 |

## 매주 주보 올리기
1. `_src/data/bulletins/`에 그 주 날짜로 파일 추가 (예: `2026-10-25.json`, 지난 파일을 복사해 고치면 편함)
2. 설교 영상이 올라오면
   - `_src/data/sermons.json` 맨 위에 영상 한 줄 추가
   - 그 주 주보 파일의 `"youtube"`에 영상 ID 입력 → 설교 페이지에 요약이 자동 연결
3. `python3 _src/build.py` 실행
4. 커밋 메시지 예: `주보 2026-10-25 반영` → GitHub에 올리면 1분 뒤 사이트 반영

- 지난 일정 체크 표시는 주보 날짜 기준으로 자동 계산됩니다.
- CSS/JS 파일 이름에 내용 해시가 붙어, 고칠 때마다 방문자 브라우저가 새 파일을 받습니다.
- 주보 원본 PDF는 개인정보(계좌·연락처 등)가 있어 이 저장소에 올리지 않습니다.

## 미리보기
```
python3 -m http.server 8765
```
이 폴더에서 실행 후 http://localhost:8765
