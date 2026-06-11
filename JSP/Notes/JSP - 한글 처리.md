---
tags: JSP
date: 2026-06-11
source: JSP 교재 5장
---

# JSP - 한글 처리

## Summary
HTTP로 한글 데이터를 전송할 때 인코딩 불일치로 깨짐이 발생한다. 전송 방식(GET/POST)에 따라 처리 방법이 다르다.

## Key Points

- **POST 방식 한글 처리**
  - 폼 데이터가 HTTP Body로 전송 → JSP에서 직접 인코딩 지정 필요
  - `request.setCharacterEncoding()` 을 **파라미터를 읽기 전에** 반드시 호출
  ```jsp
  <% request.setCharacterEncoding("euc-kr"); %>
  ```
  - UTF-8 환경(현재 표준):
  ```jsp
  <% request.setCharacterEncoding("UTF-8"); %>
  ```

- **GET 방식 한글 처리**
  - 파라미터가 URL에 포함 → 서버(Tomcat) 설정에서 처리
  - `server.xml` Connector에 `URIEncoding="UTF-8"` 추가
  ```xml
  <Connector URIEncoding="UTF-8" ... />
  ```

- **page 지시어 인코딩 설정**
  ```jsp
  <%@ page language="java" contentType="text/html; charset=UTF-8"
           pageEncoding="UTF-8" %>
  ```
  - `contentType` — 브라우저에 전달하는 응답의 인코딩
  - `pageEncoding` — JSP 파일 자체의 인코딩

- **euc-kr vs UTF-8**
  | | euc-kr | UTF-8 |
  |--|--------|-------|
  | 한글 | 지원 | 지원 |
  | 다국어 | 미지원 | 지원 |
  | 현재 표준 | 구형 | ✅ 권장 |

- **전체 흐름 예시 (POST + UTF-8)**
  ```jsp
  <%-- postrequest.jsp --%>
  <%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
  <% request.setCharacterEncoding("UTF-8"); %>
  한글 성명 : <%= request.getParameter("korname") %>
  ```

## My Thoughts


## References

- [[JSP - 기본 문법]]
- [[JSP - 내장 객체]]
