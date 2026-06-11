---
tags: JSP
date: 2026-06-11
source: 
---

# JSP - JDBC 연동

## Summary
JSP/Servlet에서 JDBC(Java Database Connectivity)를 사용해 DB와 데이터를 주고받는 방법. DAO 패턴으로 DB 접근 코드를 분리하는 것이 표준이다.

## Key Points

- **JDBC 연결 4단계**
  1. 드라이버 로드: `Class.forName("com.mysql.cj.jdbc.Driver")`
  2. 연결 획득: `DriverManager.getConnection(url, user, pw)`
  3. SQL 실행: `PreparedStatement` 사용
  4. 연결 해제: `close()` (finally 또는 try-with-resources)

- **기본 흐름 (SELECT)**
  ```java
  String sql = "SELECT * FROM users WHERE id = ?";
  PreparedStatement pstmt = conn.prepareStatement(sql);
  pstmt.setInt(1, userId);
  ResultSet rs = pstmt.executeQuery();
  while (rs.next()) {
      String name = rs.getString("name");
  }
  ```

- **PreparedStatement vs Statement**
  - `PreparedStatement` 권장: SQL 인젝션 방지, 재사용 가능
  - `Statement`: 동적 SQL 불가, 보안 취약

- **DAO 패턴 (MVC의 Model)**
  ```
  Servlet (Controller)
    → UserDAO.findById(id)  ← DB 접근 전담 클래스
      → UserVO (데이터 객체)
    → JSP (View)
  ```

- **커넥션 풀 (Connection Pool)**
  - 매 요청마다 연결 생성/해제 비용이 크므로 풀 사용
  - Tomcat: `context.xml`에 DBCP 설정, `DataSource`로 획득
  ```java
  DataSource ds = (DataSource) new InitialContext().lookup("java:comp/env/jdbc/myDB");
  Connection conn = ds.getConnection();
  ```

## My Thoughts


## References

- [[JSP - MVC 패턴]]
- [[JSP - Servlet 기초]]
