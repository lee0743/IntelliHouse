---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - EL (Expression Language)

## Summary
EL(Expression Language)은 `${}` 문법으로 스크립틀릿 없이 데이터를 간결하게 출력하는 표현 언어다. JSP 2.0부터 기본 지원되며, 스코프 객체에서 값을 자동으로 탐색한다.

## Key Points

- **기본 문법**: `${표현식}`
  - 예: `${name}`, `${user.age}`, `${list[0]}`

- **스코프 자동 탐색 순서**
  - `pageScope` → `requestScope` → `sessionScope` → `applicationScope`
  - 명시적 지정: `${sessionScope.username}`

- **EL 내장 객체**
  - `param` — `request.getParameter()` 대체. 예: `${param.id}`
  - `paramValues` — 다중 값 파라미터
  - `header` — HTTP 헤더 접근
  - `cookie` — 쿠키 접근
  - `initParam` — 초기화 파라미터

- **연산자**
  - 산술: `+`, `-`, `*`, `/` (`div`), `%` (`mod`)
  - 비교: `==` (`eq`), `!=` (`ne`), `<` (`lt`), `>` (`gt`), `<=` (`le`), `>=` (`ge`)
  - 논리: `&&` (`and`), `||` (`or`), `!` (`not`)
  - 삼항: `${조건 ? 참 : 거짓}`
  - null 체크: `${empty value}` — null이거나 빈 문자열/컬렉션이면 true

- **Java 빈 접근**: `${user.name}` → `user.getName()` 자동 호출

## My Thoughts


## References

- [[JSP - 내장 객체]]
- [[JSP - JSTL]]
