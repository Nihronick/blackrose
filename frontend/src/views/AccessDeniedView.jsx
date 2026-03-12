export function AccessDeniedView({ message }) {
  return (
    <div className="access-denied">
      <div className="access-denied-icon">🔒</div>
      <h2>Доступ запрещён</h2>
      <p>{message || <>Откройте бота <b>@blackrosesl1_bot</b>, нажмите /start и используйте кнопку <b>«📖 Открыть гайды»</b>.</>}</p>
    </div>
  )
}
