---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - 개요

## Summary
JSP(JavaServer Pages)는 HTML 문서 안에 Java 코드를 삽입하여 동적 웹 페이지를 만드는 서버사이드 기술이다. 서블릿(Servlet)을 기반으로 동작하며, JSP 파일은 최초 요청 시 서블릿 코드로 변환·컴파일된다.

## Key Points

- **JSP란?** HTML + Java 혼합 파일(`.jsp`). 웹 서버(Tomcat 등)에서 실행
- **Servlet과의 관계**: JSP는 내부적으로 `HttpServlet`을 상속한 서블릿으로 변환됨
  - `.jsp` → `.java` (변환) → `.class` (컴파일) → 실행
- **JSP 라이프사이클**
  1. `jspInit()` — 최초 1회 초기화
  2. `_jspService()` — 요청마다 실행 (핵심 로직)
  3. `jspDestroy()` — 서버 종료 시 정리
- **JSP vs Servlet 사용 구분**
  - JSP: View (화면 출력) 담당
  - Servlet: Controller (요청 처리, 로직) 담당
- **컨테이너**: Tomcat 등의 WAS(Web Application Server)가 JSP 실행 환경 제공

## My Thoughts


## References

- [[JSP MOC]]
- [[JSP - 기본 문법]]
