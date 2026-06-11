---
tags: moc, JSP
date: 2026-06-11
---

# JSP MOC

> JSP(JavaServer Pages) 학습 노트 모음 — 문법, 내장 객체, EL/JSTL, MVC 패턴

---

## 핵심 개념
- JSP = HTML 안에 Java 코드를 삽입하는 서버사이드 템플릿 기술 (Servlet으로 변환·컴파일됨)
- 4가지 기본 문법 요소: 스크립틀릿 `<% %>`, 표현식 `<%= %>`, 선언 `<%! %>`, 지시어 `<%@ %>`
- 9개 내장 객체: request, response, out, session, application, pageContext, config, page, exception
- EL(Expression Language): `${}` 문법으로 Java 코드 없이 데이터 출력
- JSTL: 조건문·반복문을 커스텀 태그로 처리 (`<c:if>`, `<c:forEach>` 등)
- MVC 패턴: Servlet이 Controller, JSP가 View, JavaBean이 Model 역할

## 노트 목록
- [[JSP - 개요]] — JSP 정의, Servlet과의 관계, 라이프사이클
- [[JSP - 기본 문법]] — 스크립틀릿·표현식·선언·지시어 4가지 요소
- [[JSP - 내장 객체]] — 9개 내장 객체 역할 및 스코프
- [[JSP - EL (Expression Language)]] — `${}` 문법, 스코프 접근, 연산자
- [[JSP - JSTL]] — Core·fmt 태그 라이브러리 사용법
- [[JSP - MVC 패턴]] — Model 1 vs Model 2, JSP+Servlet MVC 구조

## 관련 주제
- Java
- Servlet
- HTML/CSS
- JDBC (DB 연동)

## 참고 자료
- Oracle Java EE 공식 문서
- Apache Tomcat 공식 사이트 (tomcat.apache.org)
