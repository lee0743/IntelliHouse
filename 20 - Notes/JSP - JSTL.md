---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - JSTL

## Summary
JSTL(JSP Standard Tag Library)은 조건문·반복문·포맷팅 등을 커스텀 태그로 제공해 스크립틀릿 사용을 줄여주는 표준 태그 라이브러리다.

## Key Points

- **설정**: `<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>`
  - Maven/Gradle 의존성 또는 `jstl.jar` 추가 필요

- **Core 태그** (`prefix="c"`)

| 태그 | 설명 | 예시 |
|------|------|------|
| `<c:out>` | 값 출력 (XSS 방지) | `<c:out value="${name}"/>` |
| `<c:set>` | 변수 설정 | `<c:set var="x" value="10"/>` |
| `<c:remove>` | 변수 제거 | `<c:remove var="x"/>` |
| `<c:if>` | 조건문 (else 없음) | `<c:if test="${age >= 18}">성인</c:if>` |
| `<c:choose>` | switch문 | `<c:choose><c:when test="...">` |
| `<c:forEach>` | 반복문 | `<c:forEach items="${list}" var="item">` |
| `<c:forTokens>` | 구분자로 분리 반복 | `<c:forTokens items="a,b,c" delims=",">` |
| `<c:redirect>` | 리다이렉트 | `<c:redirect url="/home"/>` |
| `<c:import>` | 외부 리소스 포함 | `<c:import url="header.jsp"/>` |

- **fmt 태그** (`prefix="fmt"`) — 날짜·숫자 포맷
  - `<fmt:formatDate value="${date}" pattern="yyyy-MM-dd"/>`
  - `<fmt:formatNumber value="${price}" type="currency"/>`

- **`<c:forEach>` 상세**
  ```jsp
  <c:forEach items="${userList}" var="user" varStatus="status">
    ${status.index + 1}. ${user.name}
  </c:forEach>
  ```
  - `varStatus` 속성: `index`(0부터), `count`(1부터), `first`, `last`

## My Thoughts


## References

- [[JSP - EL (Expression Language)]]
- [[JSP - MVC 패턴]]
