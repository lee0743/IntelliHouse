---
tags: JSP, 점검문제
date: 2026-06-11
source: 
---

# JSP - 점검문제 (심화)

> 적용·분석 문제. 코드 작성 포함.

---

**Q1.** JSP의 `<%= value %>`는 Servlet으로 변환될 때 어떤 코드로 바뀌는가? `_jspService()` 메서드 내 코드로 작성하시오.

**Q2.** 다음 코드의 실행 결과를 설명하고, `page` 스코프가 소멸되는 시점을 쓰시오.
```jsp
<% pageContext.setAttribute("x", "hello"); %>
${pageScope.x}
```

**Q3.** `<c:forEach varStatus="s">` 에서 `s`로 접근할 수 있는 속성 4가지와 각 의미를 쓰시오.

**Q4.** MVC Model 2 패턴에서 Servlet이 `userList`를 JSP에 전달하고, JSP에서 출력하는 전체 코드 흐름을 작성하시오. (Servlet의 forward 코드 + JSP의 JSTL 출력 코드)

**Q5.** 다음 EL 표현식의 차이를 설명하시오.
```
${user.name}
${user["name"]}
```
언제 `[]` 표기법이 필수인가?

**Q6.** 쿠키와 세션의 보안 차이를 설명하고, 로그인 정보를 세션에 저장하는 이유를 쓰시오.

**Q7.** 다음 JSTL `<c:choose>` 구문을 완성하시오. 점수(score)가 90 이상이면 "A", 80 이상이면 "B", 나머지는 "C"를 출력.
```jsp
<c:choose>
  ___
</c:choose>
```

**Q8.** PreparedStatement가 Statement보다 권장되는 이유 2가지를 쓰시오.

**Q9.** 커넥션 풀을 사용하는 이유와 Tomcat에서 DataSource를 얻는 코드를 쓰시오.

**Q10.** POST 요청 후 redirect를 사용하는 이유(PRG 패턴)를 설명하시오. forward를 사용하면 어떤 문제가 생기는가?
