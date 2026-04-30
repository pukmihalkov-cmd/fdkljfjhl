# Currency Converter — Конвертер валют

**Автор:** Николай Сорокин  
**Файл:** Main.py  
**Версия:** 1.0  
**Дата:** 2026

---

## Описание

GUI-приложение для конвертации валют с использованием внешнего API, историей конвертаций и сохранением данных в JSON.

---

## Как получить API-ключ

В данном приложении используется **бесплатный API без ключа**:

### Используемый API:
- **Сервис:** exchangerate-api.com  
- **Эндпоинт:** `https://api.exchangerate-api.com/v4/latest/USD`  
- **Лимиты:** 1500 запросов в месяц (бесплатно)  
- **Ключ не требуется**

> Почему без ключа?  
> `exchangerate-api.com` предоставляет открытый эндпоинт для базового использования. Для production-рекомендуется зарегистрироваться и получить ключ на `exchangerate-api.com` (бесплатный тариф до 1500 запросов/месяц).

### Альтернативные API (с ключом):
Если захотите заменить API:

1. **OpenExchangeRates** — `https://openexchangerates.org/api/latest.json?app_id=YOUR_APP_ID`  
   Ключ: получить на [openexchangerates.org](https://openexchangerates.org) (бесплатный тариф)

2. **CurrencyAPI** — `https://api.currencyapi.com/v3/latest?apikey=YOUR_API_KEY`  
   Ключ: получить на [currencyapi.com](https://currencyapi.com) (300 запросов/месяц бесплатно)

3. **Fixer.io** — `http://data.fixer.io/api/latest?access_key=YOUR_ACCESS_KEY`  
   Ключ: получить на [fixer.io](https://fixer.io) (бесплатный тариф)

### Изменение API в коде:
В файле `Main.py` замените в методе `fetch_currencies()`:
```python
self.api_url = "https://api.exchangerate-api.com/v4/latest/"
