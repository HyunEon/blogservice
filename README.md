# blogservice
장고로 만들어 보는 간단한 블로그 서비스
- python
- pipenv
- django
- html
- css
- js

# 왜 django인가?
- Instargram, Pintrest 등 글로벌 기업에서 장고를 활용한 서비스를 제공하고 있다는 점에서 궁금하기도 했지만,
파이썬으로 작성할 수 있는 풀스택 웹 프레임워크라는 점이 매력적으로 다가왔었다.

- 또한 장고에서 다른 데이터베이스에서 쉽게 찾아볼 수 없는 강력한 보안 기능을 자체적으로 제공하고 있다는 사항도 눈에 띄었다. (csrf 토큰, SQL 인젝션, XSS 방지 등..)
  
-  저번에 MariaDB, ASP .net, 플러터를 서로 연동을 해봤는데 프레임워크 단/API 단/DB 단 이런 식으로 나눠져 있어서 좀 불편했는데, 이처럼 외부 프레임워크를 사용할 때 DRF라는 라이브러리를 지원해 굳이 API 단 환경을 별도로 만들지 않아도 된다는게 마음에 들었다.

# 궁극적인 목표?
- 최종 목표는 완성하여 클라우드 서비스에 배포해보는 것이지만, 개발 실력 증진과 코드에 더욱 친숙해지는 것이 주된 목표임

# TODO?
- base.html을 미리 작성 후 상속하여 템플릿 구조 최적화
- 로그인 기능
- 블로그 관리자 페이지 및 기능 구현
- 첨부 파일 & 비디오 플레이어 기능 구현

UI
- 포스트 리스트
![스크린샷 2025-03-28 180222](https://github.com/user-attachments/assets/ab50b1f4-afd8-47d9-8cd9-f1c3c8d4dd42)

- 포스트 상세
![스크린샷 2025-03-28 180209](https://github.com/user-attachments/assets/99277b6d-b52a-4252-b297-146f13bb04c0)

- 포스트 작성
![스크린샷 2025-03-28 180241](https://github.com/user-attachments/assets/77dce969-c266-4a4a-b0e8-18f98e05eff2)
