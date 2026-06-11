---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - MVC 패턴

## Summary
JSP 개발에서 MVC 패턴은 역할을 Model(데이터), View(화면), Controller(제어)로 분리한다. Model 1은 JSP가 모든 역할을 맡고, Model 2는 Servlet이 Controller를 담당해 유지보수가 용이하다.

## Key Points

- **Model 1 구조** (간단한 프로젝트)
  - JSP가 Controller + View 역할을 동시에 수행
  - 소규모에는 빠르지만, 로직과 화면이 뒤섞여 유지보수 어려움
  ```
  클라이언트 → JSP (로직 + 화면) → DB
  ```

- **Model 2 구조 (MVC)** (권장)
  ```
  클라이언트 → Servlet (Controller)
                  ↓
              JavaBean (Model) ← DB
                  ↓
               JSP (View)
                  ↓
             클라이언트
  ```
  - **Controller (Servlet)**: 요청 수신 → 파라미터 처리 → Model 호출 → View로 포워딩
  - **Model (JavaBean/DAO)**: 비즈니스 로직, DB 접근
  - **View (JSP)**: EL + JSTL로 데이터 출력만 담당, Java 코드 최소화

- **핵심 메서드**
  - 포워딩(forward): URL 변경 없이 JSP로 이동
    ```java
    request.setAttribute("list", dataList);
    request.getRequestDispatcher("/list.jsp").forward(request, response);
    ```
  - 리다이렉트: URL 변경, 새 요청 발생
    ```java
    response.sendRedirect("/home");
    ```

- **forward vs redirect 선택 기준**
  - forward: 데이터를 `request`에 담아 JSP에 전달할 때
  - redirect: 로그인 후 메인 이동, POST 후 GET 방지(PRG 패턴) 등

## My Thoughts


## References

- [[JSP - JSTL]]
- [[JSP - 내장 객체]]
