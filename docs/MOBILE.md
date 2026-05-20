# Сборка мобильных приложений BlackRose

## Технология

Проект использует **Capacitor v6** для оборачивания веб-приложения в нативные Android и iOS контейнеры. Весь фронтенд-код остаётся общим — Capacitor просто загружает собранный `dist/` в нативный WebView.

> **Авторизация не требуется** — приложение открывается сразу, как обычный сайт. Telegram авторизация нужна только администраторам.

---

## Вариант 1: PWA (Самый быстрый)

BlackRose поддерживает технологию **PWA**. Это позволяет «установить» сайт как приложение без скачивания `.apk` или `.ipa`.

1. Откройте [blackrose.me](https://blackrose.me) в мобильном браузере.
2. **iOS (Safari)**: Нажмите кнопку «Поделиться» (квадрат со стрелкой) -> **«На экран Домой»**.
3. **Android (Chrome)**: Нажмите на три точки -> **«Установить приложение»**.

Теперь иконка BlackRose появится на вашем рабочем столе и будет открываться в отдельном окне без адресной строки.

---

## Вариант 2: Нативные приложения (Capacitor)


### Android
- **Android Studio** (Hedgehog или новее)
- **JDK 17+**
- **Android SDK** (API Level 33+)

### iOS (только на macOS)
- **Xcode 15+**
- **CocoaPods** (`sudo gem install cocoapods`)
- **Apple Developer Account** (для тестирования на устройстве)

---

## Быстрый старт

### 1. Сборка фронтенда

```bash
cd frontend
npm install
npm run build
```

### 2. Синхронизация с нативными проектами

```bash
npx cap sync
```

Эта команда:
- Копирует `dist/` в `android/app/src/main/assets/public/`
- Копирует `dist/` в `ios/App/App/public/`
- Устанавливает нативные зависимости плагинов

### 3. Открытие в IDE

**Android:**
```bash
npx cap open android
```
Откроется Android Studio. Нажмите ▶ Run для запуска на эмуляторе или устройстве.

**iOS:**
```bash
npx cap open ios
```
Откроется Xcode. Выберите устройство/симулятор и нажмите ▶ Run.

---

## Настройка API URL

По умолчанию приложение использует локальный `dist/` и переменные среды из `vite build`.

### Для production:
Убедитесь, что перед `npm run build` в `.env` или `.env.production` прописано:

```env
VITE_API_URL=https://blackrose-XXXX.onrender.com
VITE_BOT_NAME=blackrosesl1_bot
VITE_HONEYBADGER_API_KEY=...
```

### Для разработки (Live Reload):
Раскомментируйте `server.url` в `capacitor.config.ts`:

```ts
server: {
  url: 'http://192.168.1.XXX:5173', // ваш локальный IP
  cleartext: true,
}
```

Затем:
```bash
npm run dev   # запускает Vite dev server
npx cap sync  # обновляет конфиг в нативных проектах
npx cap open android  # или ios
```

---

## Конфигурация приложения

Файл: `frontend/capacitor.config.ts`

| Параметр | Значение | Описание |
|---|---|---|
| `appId` | `com.blackrose.slayerlegend` | Bundle ID приложения |
| `appName` | `BlackRose` | Название в лаунчере |
| `webDir` | `dist` | Папка со сборкой Vite |

---

## Плагины

| Плагин | Назначение |
|---|---|
| `@capacitor/haptics` | Вибрация при нажатиях |
| `@capacitor/status-bar` | Тёмный стиль статус-бара |
| `@capacitor/push-notifications` | Push-уведомления (требует настройки FCM/APN) |
| `@capacitor/app` | Deep links (`blackrose://guide/slug`) |

---

## Подписание и публикация

### Android (Google Play)

1. Создайте keystore:
   ```bash
   keytool -genkey -v -keystore blackrose.keystore -alias blackrose -keyalg RSA -keysize 2048 -validity 10000
   ```

2. В `android/app/build.gradle` добавьте signing config

3. Соберите APK/AAB:
   ```bash
   cd android
   ./gradlew assembleRelease   # APK
   ./gradlew bundleRelease     # AAB для Google Play
   ```

### iOS (App Store)

1. Откройте `ios/App/App.xcworkspace` в Xcode
2. Установите Team в Signing & Capabilities
3. Product → Archive → Distribute App → App Store Connect

---

## Обновление приложения

При любых изменениях фронтенда:

```bash
cd frontend
npm run build
npx cap sync
# Затем запустите в Android Studio / Xcode
```

---

## Иконка приложения

Исходная иконка: `frontend/public/app-icon.png` (1024×1024)

### Установка иконок:

**Android** — замените файлы в:
- `android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` (192×192)
- `android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png` (144×144)
- `android/app/src/main/res/mipmap-xhdpi/ic_launcher.png` (96×96)
- `android/app/src/main/res/mipmap-hdpi/ic_launcher.png` (72×72)
- `android/app/src/main/res/mipmap-mdpi/ic_launcher.png` (48×48)

Или используйте [Android Asset Studio](https://romannurik.github.io/AndroidAssetStudio/icons-launcher.html).

**iOS** — откройте `ios/App/App/Assets.xcassets/AppIcon.appiconset/` в Xcode Asset Catalog и загрузите иконку 1024×1024.
