---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - 세션과 쿠키

## Summary
HTTP는 무상태(stateless) 프로토콜이다. 세션과 쿠키는 요청 간에 사용자 상태를 유지하는 두 가지 방식으로, 각각 서버와 클라이언트에 데이터를 저장한다.

## Key Points

- **쿠키 (Cookie)** — 클라이언트 저장
  - 서버가 `Set-Cookie` 헤더로 브라우저에 저장
  - 이후 요청마다 자동으로 서버에 전송
  - 생성: `response.addCookie(new Cookie("key", "value"))`
  - 읽기: `request.getCookies()` → 배열 순회
  - 만료: `cookie.setMaxAge(초)` (0이면 즉시 삭제)
  - 보안 취약 — 민감한 정보 저장 금지

- **세션 (Session)** — 서버 저장
  - 서버 메모리에 저장, 클라이언트는 JSESSIONID 쿠키만 보관
  - 생성/접근: `request.getSession()` (없으면 새로 생성)
  - 저장: `session.setAttribute("loginUser", userObj)`
  - 읽기: `session.getAttribute("loginUser")`
  - 삭제: `session.invalidate()` (로그아웃 시)
  - 기본 만료: 30분 (web.xml에서 설정 가능)

- **세션 vs 쿠키 비교**

  | | 세션 | 쿠키 |
  |--|------|------|
  | 저장 위치 | 서버 | 클라이언트 브라우저 |
  | 보안 | 높음 | 낮음 |
  | 용량 제한 | 서버 메모리 | 4KB |
  | 만료 | 브라우저 닫거나 타임아웃 | 설정한 시간 |
  | 사용 예 | 로그인 정보 | 자동 로그인, 장바구니 |

- **로그인 흐름 예시**
  ```java
  // 로그인 성공 시
  session.setAttribute("loginUser", user);
  response.sendRedirect("/main");

  // 페이지에서 로그인 확인
  User user = (User) session.getAttribute("loginUser");
  if (user == null) response.sendRedirect("/login");
  ```

## My Thoughts


## References

- [[JSP - 내장 객체]]
- [[JSP - MVC 패턴]]
