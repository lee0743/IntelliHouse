---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - 내장 객체

## Summary
JSP는 별도 선언 없이 바로 사용할 수 있는 9개의 내장 객체(Implicit Objects)를 제공한다. 스코프(범위)에 따라 데이터를 저장·공유하는 방식이 다르다.

## Key Points

- **내장 객체 9개**

| 객체 | 타입 | 설명 |
|------|------|------|
| `request` | HttpServletRequest | 클라이언트 요청 정보 (파라미터, 헤더 등) |
| `response` | HttpServletResponse | 서버 응답 설정 (리다이렉트, 헤더 등) |
| `out` | JspWriter | 출력 스트림 (HTML 출력) |
| `session` | HttpSession | 세션 데이터 저장 (사용자별) |
| `application` | ServletContext | 애플리케이션 전체 공유 데이터 |
| `pageContext` | PageContext | 현재 페이지 컨텍스트, 다른 내장 객체 접근 |
| `config` | ServletConfig | 서블릿 설정 정보 |
| `page` | Object | 현재 JSP 페이지 자신 (`this`) |
| `exception` | Throwable | 에러 페이지에서만 사용 가능 |

- **4가지 스코프 (좁은 → 넓은 순)**
  1. `page` — 현재 페이지 내에서만 유효 (`pageContext`)
  2. `request` — 하나의 요청 처리 동안 유효 (`request`)
  3. `session` — 브라우저 세션 동안 유효 (`session`)
  4. `application` — 서버 가동 동안 유효 (`application`)

- **자주 쓰는 메서드**
  - `request.getParameter("key")` — 폼 파라미터 읽기
  - `session.setAttribute("key", value)` / `session.getAttribute("key")` — 세션 저장/조회
  - `response.sendRedirect("url")` — 리다이렉트

## My Thoughts


## References

- [[JSP - 기본 문법]]
- [[JSP - EL (Expression Language)]]
