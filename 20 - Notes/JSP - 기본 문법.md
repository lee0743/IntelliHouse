---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - 기본 문법

## Summary
JSP는 4가지 핵심 문법 요소로 Java 코드를 HTML에 삽입한다. 스크립틀릿·표현식·선언은 Java 코드 삽입 방식이고, 지시어는 페이지 설정을 담당한다.

## Key Points

- **스크립틀릿 (Scriptlet)** `<% %>`
  - 일반 Java 코드 작성 (변수 선언, 제어문 등)
  - `_jspService()` 메서드 안에 삽입됨
  - 예: `<% int a = 10; out.print(a); %>`

- **표현식 (Expression)** `<%= %>`
  - 값을 바로 출력. 세미콜론 없음
  - 예: `<%= request.getParameter("name") %>`

- **선언 (Declaration)** `<%! %>`
  - 멤버 변수 또는 메서드 선언 (`_jspService()` 밖에 위치)
  - 예: `<%! int count = 0; %>`

- **지시어 (Directive)** `<%@ %>`
  - 페이지 설정 정보 지정
  - `page`: `<%@ page language="java" contentType="text/html; charset=UTF-8" %>`
  - `include`: `<%@ include file="header.jsp" %>`
  - `taglib`: `<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>`

- **주석**
  - JSP 주석: `<%-- 이 내용은 클라이언트에 전송 안 됨 --%>`
  - HTML 주석: `<!-- 이 내용은 전송됨 -->`

## My Thoughts


## References

- [[JSP - 개요]]
- [[JSP - 내장 객체]]
