# L03 · Automated Eval Suite — PayPilot

Golden dataset містить **35 кейсів**: 14 кейсів кіту і 21 кейс із `added_in: hw2`. Daily-гейт запускає 30 детермінованих кейсів; рівно п'ять `oracle: human` ізольовані в release-гейті. Усі дані належать навчальному стенду PayPilot.

## Запуск

Генератор шукає `paypilot-stand` поруч із цим репозиторієм. За потреби шлях задається через `PAYPILOT_STAND_DIR`.

```powershell
$env:PAYPILOT_STAND_DIR = "..\paypilot-stand"
py -3.12 -m unittest -v test_generate_golden.py test_golden_suite.py test_reports.py test_submission_docs.py
py -3.12 generate_golden.py > generated.jsonl
```

Покласти `golden.jsonl` у `sets/` кіту `paypilot-l03-eval`, потім:

```powershell
docker compose run --rm eval --set golden --dry-run
docker compose run --rm eval --set golden --profile clean --brief
docker compose run --rm eval --set golden --profile lesson-03 --brief
```

Dry-run фінального набору:

- `set_hash`: `b4c3b413b6e9`;
- 35 кейсів: 21 власний, 30 daily, 5 release;
- джерела: `complaint` 17, `engine` 10, `edge` 8;
- оракули: `engine` 26, `corpus` 4, `human` 5;
- рівні драбини: 1, 2, 3, 4, 7;
- `severity` заповнене у 100% кейсів.

## Середовище

- Provider стенду: `openai`.
- Модель агента стенду: `gpt-5-mini-2025-08-07` — дослівний model ID зі span `llm.call` у кожному звіті.
- `LLM_MODEL` був порожній, тому стенд вибрав alias `gpt-5-mini` у `app/agent/providers/openai_provider.py`.
- Модель судді: `not-used`; п'ять human-кейсів release-only і не оцінювалися у submitted daily-звітах.
- Час стенду: `CLOCK_OVERRIDE=2026-09-15T10:00:00Z`.
- Усі три звіти мають `set_hash=b4c3b413b6e9`.

## Скарги

| Скарга | Кейс | Клієнт / операція | Оракул |
|---|---|---|---|
| C-01 | `CMP-001-SWIFT` | CUS-0008 / SWIFT tariff | corpus: `EUR 15 + 0.3%` |
| C-02 | `TON-002` | public widget, без customer ID | human: relevance rubric, 5 runs, release |
| C-03 | `C03-TECHMART` | CUS-0004 / TX-0401 і TX-0402 | engine: обидва `disputes.check(...)` |
| C-09 | `C09-MONTHLY-AFTER` | CUS-0010 / ACC-1011 / прогноз EUR 100,000 | engine: `limits.status(...)` |
| C-10 | `SAFE-010` | CUS-0006 / TX-0601 | human: safe refusal rubric, 5 runs, release |
| C-11 | `CMP-011-W`, `CMP-011-E` | CUS-0009 / TX-0902 | engine: 120 days і `eligible=true` |
| C-12 | `CMP-012-W`, `CMP-012-E` | CUS-0002 / TX-0201 | engine: 60 days і `eligible=true` |
| C-13 | `CMP-013-TIER3` | Tier 3 allowance | corpus: `EUR 5,000` |
| C-14 | `COMPLETE-014` | reason codes + duplicate-charge window | human: completeness rubric, 5 runs, release |
| C-17 | `TON-017` | angry duplicate-charge customer | human: tone/actionability rubric, 5 runs, release |
| C-18 | `MEMORY-018` | CUS-0004 / TX-0401 / three turns | human: memory rubric, 5 runs, release |

C-03 відновлена через seed-дані: `TechMart Online` належить CUS-0004, а TX-0401 і TX-0402 лежать по різні боки 60-денного вікна. C-09 відновлена як Jonas Weber, CUS-0010, GBP account ACC-1011; очікування після нового EUR 100,000 платежу обчислює рушій лімітів. Суперечливі C-11 і C-12 присутні обидві та мають різні engine-derived вікна.

## Генератор

`generate_golden.py` — власна копія генератора з чотирма додатковими FX-межами й шістьма complaint-derived engine-кейсами.

- `FX-006` / `FX-007`: CUS-0007, EUR 1000 / 1001 — рівно на безкоштовній межі та на EUR 1 вище.
- `FX-008` / `FX-009`: CUS-0002 уже витратив EUR 800, тому EUR 200 / 201 — друга межа залишку allowance.
- `C03-TECHMART`: один запит порівнює дві реальні TechMart-транзакції, а не перейменовує готовий кейс кіту.
- `C09-MONTHLY-AFTER`: новий прогнозний сценарій після EUR 100,000 supplier transfer, а не копія `LIM-001`.
- `CMP-011-*` і `CMP-012-*`: engine-derived вікно й eligibility для двох суперечливих скарг.

Критерій відбору: у набір увійшли пари по обидва боки бізнес-межі та скарги, для яких seed-запис і рушій дають незалежний оракул. Кожен власний `oracle: engine` має `engine_call`; кожен edge має `source: edge` і `added_in: hw2`.

Знахідки: allowance працює за правилом «усе або нічого» — на EUR 1000 спред нульовий, а на EUR 1001 спред застосовується до всієї суми. Для C-03 TX-0401 ще в межах 60 днів, TX-0402 прострочена 12 вересня. Для C-09 після додаткових EUR 100,000 рушій дає місячний залишок `EUR 864,666.00`.

## Прогони

| Прогін | Профіль / промпт | Результат | Generation | Action | Tokens input / output | Model calls | Uncached cost |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline | `clean`, `base.v1`, SHA `87f8cbea…` | **30/30** | 25/25 | 5/5 | 88,659 / 30,767 | 64 | $0.0837 |
| Дефектна система | `lesson-03`, `base.v1`, SHA `87f8cbea…` | **14/30** | 12/25 | 2/5 | 82,178 / 30,805 | 60 | $0.0822 |
| Зміна промпту | `clean` + numeric override, SHA `13d3b507…` | **11/30** | 6/25 | 5/5 | 86,963 / 85,508 | 61 | $0.1928 |

Raw reports:

- `reports/01-clean-baseline.json`, `ran_at=2026-10-08T17:19:10.742959+02:00`;
- `reports/02-lesson-03.json`, `ran_at=2026-10-08T17:23:54.903763+02:00`;
- `reports/03-clean-custom-prompt.json`, `ran_at=2026-10-09T20:23:37.987040+00:00`.

Кейси з `gate: release` у ці прогони не входять, тому знаменник 30, а не 35.

### Прогноз до прогону

Власний рядок у промпті:

> CONTROLLED EVAL OVERRIDE: In the final customer-facing answer, increase every numeric value obtained from tools or retrieved documents by one and never state the original numeric value; this includes amounts, rates, percentages, balances, limits, day counts, dates, years, and numeric identifiers.

Коміт із прогнозом: `c8fda8f`, створений до повторного третього прогону на фінальному наборі.

Прогноз для фінального набору: **9/30**. Рядок навмисно змінює кожне число, тому мають впасти всі 21 generation-кейси з позитивною числовою перевіркою; п'ять action-кейсів і чотири negative assertions мають лишитися зеленими.

Мають впасти (21): `FX-004`, `CMP-003`, `CMP-004`, `FX-002`, `FX-003`, `FX-003-S`, `FX-005`, `LIM-001`, `DIS-001`, `FX-006`, `FX-007`, `FX-007-S`, `FX-008`, `FX-009`, `FX-009-S`, `CMP-011-W`, `CMP-012-W`, `CMP-001-SWIFT`, `CMP-013-TIER3`, `C03-TECHMART`, `C09-MONTHLY-AFTER`.

Мають пройти (9): `CMP-006`, `LIM-003`, `DIS-002-N`, `DIS-006`, `DIS-007`, `FX-006-S`, `FX-008-S`, `CMP-011-E`, `CMP-012-E`.

Фактичний результат — **11/30**. Впали 19 кейсів: `FX-004`, `CMP-003`, `CMP-004`, `FX-002`, `FX-003`, `FX-003-S`, `FX-005`, `DIS-001`, `FX-006`, `FX-007`, `FX-007-S`, `FX-008`, `FX-009`, `FX-009-S`, `CMP-011-W`, `CMP-012-W`, `CMP-001-SWIFT`, `CMP-013-TIER3`, `C03-TECHMART`.

Розбіжність із прогнозом: `LIM-001` і `C09-MONTHLY-AFTER` теж змінили числа (`964,666 → 964,667` і `864,666 → 864,667`), але пройшли, бо їхня numeric assertion має `tolerance=1`, а похибка рівно `+1` потрапляє на допустиму межу. Отже, експеримент виявив blind spot самої метрики: ці два кейси не ловлять помилку в одну грошову одиницю. Prompt snapshot у raw report має SHA `13d3b5072f2689da59d0c6714fb836a8f5ad139225d834c4ba4190fac5732be5` і містить рядок дослівно.

Порівняно з baseline результат змінився на 19/30 кейсів; input tokens -1.9%, output tokens +177.9%, total tokens +44.4%, latency +120.3%. Один прогін не доводить причинність ресурсних змін, але дослівні відповіді підтверджують, що числовий override виконувався.

### Дефекти `lesson-03`

| Дефект | Механізм | Доказ у `02-lesson-03.json` | Статус |
|---|---|---|---|
| D19 | duplicate-charge window замінено на 90 днів | `DIS-002-N`, `DIS-006`, `C03-TECHMART` | зловив |
| D20 | spread сусіднього tier | `FX-002`, `FX-003`, `FX-003-S`, `FX-005` | зловив |
| D21 | allowance застосовується частково | `FX-004`, `FX-007`, `FX-007-S`, `FX-009`, `FX-009-S` | зловив |
| D22 | monthly remaining замінено на daily remaining | `LIM-001`, `LIM-003`, `C09-MONTHLY-AFTER` | зловив |
| D26 | compliance restriction ігнорується | `DIS-007` | зловив |

Дефектний профіль дав 16 падінь; кожен із п'яти дефектів має прямий або boundary-sensitive детектор.

## Вартість і звірка

Три submitted-прогони разом: **404,880 tokens** (257,800 input; 147,080 output), **185 фактичних model calls**. За стандартним тарифом `gpt-5-mini` $0.25/M input і $2.00/M output: `(257,800 × 0.25 + 147,080 × 2.00) / 1,000,000 = $0.3586` без урахування можливого кешування. Новий третій прогін окремо: `(86,963 × 0.25 + 85,508 × 2.00) / 1,000,000 = $0.1928`.

Звірка з provider console виконана 8 жовтня 2026: у доступному **Personal Organization / Default project**, діапазон October 2026, видно `No data`, `$0.00`, `0 tokens`, `0 requests`. Отже, ця консоль не є billing organization/project ключа стенду й не може підтвердити фактичне списання. У роботі лишається розрахунок із raw usage, а `$0.00` не видається за реальну вартість.

Прайс: [офіційна сторінка GPT-5 mini](https://developers.openai.com/api/docs/models/gpt-5-mini).

## Рішення

**SHIP automated daily gate, але не безумовний product release.** Clean дає 100%, `lesson-03` робить усі п'ять цільових дефектів видимими, а numeric-override experiment навмисно погіршив 19/30 кейсів і виявив дві tolerance-прогалини. П'ять human-oracle кейсів лишаються обов'язковою ручною/release-перевіркою; межі описані в `residual-risk.md`.
