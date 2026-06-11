---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - Servlet 기초

## Summary
Servlet은 Java로 HTTP 요청/응답을 처리하는 서버 사이드 프로그램이다. JSP는 Servlet 위에서 동작하므로 Servlet의 기본 구조와 생명주기를 이해해야 JSP를 제대로 쓸 수 있다.

## Key Points

- **Servlet이란?**
  - `javax.servlet.http.HttpServlet`을 상속한 Java 클래스
  - WAS(Tomcat)가 인스턴스를 생성·관리
  - URL 매핑: `@WebServlet("/경로")` 어노테이션으로 지정

- **Servlet 생명주기**
  1. `init()` — 최초 1회 (서블릿 인스턴스 생성 시)
  2. `service()` → `doGet()` / `doPost()` — 요청마다 실행
  3. `destroy()` — 서버 종료 시 1회

- **doGet vs doPost**
  - `doGet`: URL 파라미터로 데이터 전달, 조회에 적합
  - `doPost`: HTTP Body로 데이터 전달, 로그인·폼 제출에 적합

- **기본 구조**
  ```java
  @WebServlet("/hello")
  public class HelloServlet extends HttpServlet {
      @Override
      protected void doGet(HttpServletRequest req, HttpServletResponse res)
              throws ServletException, IOException {
          res.setContentType("text/html; charset=UTF-8");
          PrintWriter out = res.getWriter();
          out.println("<h1>Hello Servlet</h1>");
      }
  }
  ```

- **JSP와의 역할 분담**
  - Servlet = Controller (요청 수신 → 비즈니스 로직 → JSP로 포워딩)
  - JSP = View (데이터를 HTML로 출력)

## My Thoughts


## References

- [[JSP - 개요]]
- [[JSP - MVC 패턴]]
