---
tags: moc, JSP
date: 2026-06-11
---

# JSP MOC

> JSP(JavaServer Pages) 학습 노트 모음 — Servlet 기초부터 MVC 패턴, DB 연동까지

---

## 학습 로드맵

```
① Servlet 기초        → JSP가 무엇 위에서 도는지 이해
② JSP 개요            → JSP 정의, Servlet 변환 과정
③ JSP 기본 문법       → 4가지 문법 요소 숙지
④ JSP 내장 객체       → 9개 객체 + 4가지 스코프
⑤ EL                  → ${}로 스크립틀릿 대체
⑥ JSTL               → 태그로 조건/반복 처리
⑦ 세션과 쿠키         → 상태 유지 메커니즘
⑧ MVC 패턴            → Servlet + JSP 역할 분담
⑨ JDBC 연동           → DB 데이터를 화면에 출력
```

---

## 핵심 개념
- Servlet = Controller, JSP = View — 역할 분리가 핵심
- 4가지 문법: 스크립틀릿 `<% %>`, 표현식 `<%= %>`, 선언 `<%! %>`, 지시어 `<%@ %>`
- 9개 내장 객체: request, response, out, session, application, pageContext, config, page, exception
- 4가지 스코프 (좁은→넓은): page → request → session → application
- EL `${}`: Java 코드 없이 데이터 출력, 스코프 자동 탐색
- JSTL: `<c:if>`, `<c:choose>`, `<c:forEach>` 로 로직을 태그로 처리
- 세션: 서버 저장, 로그인 정보 관리 / 쿠키: 클라이언트 저장, 자동 로그인
- MVC Model 2: Servlet(Controller) → DAO(Model) → JSP(View)

## 노트 목록

### 기초
- [[JSP - Servlet 기초]] — HttpServlet 구조, doGet/doPost, 생명주기
- [[JSP - 개요]] — JSP 정의, Servlet 변환 과정, 라이프사이클
- [[JSP - 기본 문법]] — 스크립틀릿·표현식·선언·지시어 4가지 요소
- [[JSP - 내장 객체]] — 9개 내장 객체 역할 및 스코프

### 핵심
- [[JSP - EL (Expression Language)]] — `${}` 문법, 스코프 접근, 연산자
- [[JSP - JSTL]] — Core·fmt 태그 라이브러리 사용법
- [[JSP - 세션과 쿠키]] — 상태 유지, 로그인 흐름, 보안 차이

### 심화
- [[JSP - MVC 패턴]] — Model 1 vs Model 2, forward vs redirect
- [[JSP - JDBC 연동]] — JDBC 4단계, PreparedStatement, DAO 패턴, 커넥션 풀

### 점검문제
- [[JSP - 점검문제 (기본)]] — 개념 확인 10문항
- [[JSP - 점검문제 (심화)]] — 적용·코드 작성 10문항

## 관련 주제
- Java (기본 문법, OOP)
- HTML/CSS (JSP의 출력 대상)
- JDBC / SQL (DB 연동)
- Spring MVC (JSP MVC 패턴의 발전형)

## 참고 자료
- Apache Tomcat 공식 사이트 (tomcat.apache.org)
- Oracle Java EE 공식 문서
