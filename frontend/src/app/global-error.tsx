"use client";

// Запасной экран на случай ошибки в самом каркасе сайта. Стили встроены, потому что глобальные могут не загрузиться.
export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="ru">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#f4f7f9", color: "#0f1418" }}>
        <div style={{ maxWidth: 560, margin: "60px auto", padding: "0 16px" }}>
          <h1 style={{ fontSize: 26, marginBottom: 10 }}>Что-то пошло не так</h1>
          <p style={{ color: "#5d6b77", marginBottom: 20 }}>
            Мы уже знаем об ошибке. Попробуйте обновить страницу, а если не поможет, позвоните нам.
          </p>
          <button
            type="button"
            onClick={() => reset()}
            style={{
              background: "#f04e23",
              color: "#fff",
              border: 0,
              borderRadius: 8,
              padding: "13px 20px",
              fontWeight: 600,
              minHeight: 48,
              cursor: "pointer",
            }}
          >
            Обновить страницу
          </button>
        </div>
      </body>
    </html>
  );
}
