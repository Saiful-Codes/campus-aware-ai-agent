# Campus-Aware AI Agent — Manual Chat Test Suite

**Purpose:** Pre-demo and pre-submission validation checklist.  
**How to use:** Send each question to the running chatbot, observe the response, and tick Pass or Fail.  
**Backend route reference:** `POST /api/chat` with `{ "query": "...", "debug": true }`

---

## Legend

| Symbol | Meaning |
|--------|---------|
| `sensor_live` | Syncs live sensor → InfluxDB last reading → Gemini format |
| `sensor_history` | Text-to-Flux → InfluxDB aggregate/range → Gemini format |
| `exact_current_info` | RAG URL extraction → guardrail response (no invented facts) |
| `rag_specific` | Vector search PostgreSQL → Gemini with context |
| `general_conceptual` | RAG optional → Gemini hybrid |
| `normal_llm` | Plain Gemini response |

---

## Section 1 — Live Sensor Questions

### LIVE-01 — Current temperature
**Question:** `What is the current temperature?`  
**Intent:** `sensor_live`  
**Flow:** Sync live sensor API → InfluxDB last reading → Gemini format  
**Expected response:** States current temperature in °C with brief comfort interpretation. 1–3 sentences. No JSON, no system names.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### LIVE-02 — Latest humidity
**Question:** `What is the latest humidity?`  
**Intent:** `sensor_live`  
**Flow:** Same as LIVE-01  
**Expected response:** States current humidity percentage. 1–3 sentences. No technical jargon.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### LIVE-03 — Current conditions (pressure + dew point)
**Question:** `What is the pressure sensor reading now?`  
**Intent:** `sensor_live`  
**Flow:** Sync live sensor API → InfluxDB last reading → Gemini format  
**Expected response:** States current pressure in hPa. Brief answer. Must not mention "IoT", "backend", or sensor system names.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 2 — Historical Sensor Questions (previously buggy)

### HIST-01 — Show all readings (was routing to live — now fixed)
**Question:** `Show all temperature readings`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux → Flux query with `limit(n: 20)` → Gemini summary  
**Expected response:** Summarises the readings found. If no data, says "No matching sensor data was found for the last 30 days."  
- [ ] **Pass / Fail:**
- **Notes:**

---

### HIST-02 — Past year question (was routing to live — now fixed)
**Question:** `What was the humidity in 1995?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with absolute range `1995-01-01 → 1996-01-01` → InfluxDB → Gemini  
**Expected response:** Either reports data found, OR: "No matching sensor data was found for 1995. The database may not contain readings for that time range."  
- [ ] **Pass / Fail:**
- **Notes:**

---

### HIST-03 — Month-specific history
**Question:** `Show temperature readings from last month`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `start: -60d` → InfluxDB → Gemini summary  
**Expected response:** Summarises readings from last month. Describes pattern or range, not a raw list.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### HIST-04 — Month + year absolute range
**Question:** `What was the temperature in April 2026?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with absolute range `2026-04-01 → 2026-05-01` → InfluxDB → Gemini  
**Expected response:** Reports data found for April 2026, or a contextual no-data message mentioning "April 2026".  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 3 — Aggregate Sensor Questions

### AGG-01 — Average temperature this week
**Question:** `What was the average temperature this week?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `group() |> mean()` + `start: -7d` → single aggregate result → Gemini  
**Expected response:** Reports a single average value. Should not list individual readings.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### AGG-02 — Highest temperature
**Question:** `What was the highest temperature recorded last month?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `group() |> max()` + `start: -60d` → single max value → Gemini  
**Expected response:** States the highest temperature found. One or two sentences.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### AGG-03 — Lowest humidity
**Question:** `What was the lowest humidity this week?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `group() |> min()` → Gemini  
**Expected response:** States the lowest humidity value with context. Concise.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### AGG-04 — Reading count
**Question:** `How many sensor readings were recorded this month?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `group() |> count()` → single integer result → Gemini  
**Expected response:** Gives a count or an estimate. Should not be vague if data is available.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 4 — Trend Sensor Questions

### TREND-01 — Temperature over time (core use case)
**Question:** `Show temperature trend over time this week`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `aggregateWindow(every: 1h, fn: mean)` + `start: -7d` + `limit(n: 20)` → Gemini  
**Expected response:** Describes the overall trend (rising, stable, falling), range of values, or pattern across the week. Must NOT say "no data for following hours" unless data is genuinely absent.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### TREND-02 — Change over time (was routing to live — now fixed)
**Question:** `How did temperature change over time?`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux trend query → Gemini summary  
**Expected response:** Summarises the trend pattern. Does not list each record individually.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### TREND-03 — Humidity trend last week
**Question:** `Show humidity trend for the last week`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with `aggregateWindow` → Gemini trend description  
**Expected response:** Brief human-readable description of humidity trend. Under 100 words.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 5 — RAG Campus / Document Questions

### RAG-01 — Ask La Trobe
**Question:** `Where is Ask La Trobe and what services does it provide?`  
**Intent:** `rag_specific`  
**Flow:** PostgreSQL vector search → Gemini with context chunks  
**Expected response:** Describes Ask La Trobe location and services based on retrieved documents. If high confidence, pure RAG answer. If medium/low, hybrid with caveat.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### RAG-02 — StudentOnline
**Question:** `What is StudentOnline used for?`  
**Intent:** `rag_specific`  
**Flow:** PostgreSQL vector search → Gemini with context  
**Expected response:** Explains the StudentOnline portal's purpose. Based on retrieved content. No invented URLs.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### RAG-03 — Glenn College
**Question:** `What accommodation is available at Glenn College?`  
**Intent:** `rag_specific`  
**Flow:** PostgreSQL vector search → Gemini with context  
**Expected response:** Describes Glenn College accommodation options. If low RAG confidence, acknowledges uncertainty and suggests latrobe.edu.au.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### RAG-04 — Campus map
**Question:** `Where is the campus map?`  
**Intent:** `rag_specific`  
**Flow:** PostgreSQL vector search → Gemini with context  
**Expected response:** Points to campus map resource if found in documents. If no context, suggests checking latrobe.edu.au directly.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### RAG-05 — Orientation
**Question:** `When is orientation week and what should I bring?`  
**Intent:** `rag_specific`  
**Flow:** PostgreSQL vector search → Gemini with context  
**Expected response:** Describes orientation based on retrieved content. Should NOT invent specific dates unless they appear in context chunks.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 6 — Exact / Current-Info Guardrail Questions

### EXACT-01 — Academic calendar link (classic guardrail test)
**Question:** `Give me the exact link for the 2026 academic calendar`  
**Intent:** `exact_current_info`  
**Flow:** RAG URL extraction → `_safe_exact_info_response`  
**Expected response:** Either provides a URL found in documents (with a "please verify" caveat), OR says it cannot safely provide exact current information and directs to latrobe.edu.au. Must NOT invent a URL.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### EXACT-02 — Chisholm College weekly rent
**Question:** `How much is the weekly rent in Chisholm College?`  
**Intent:** `exact_current_info`  
**Flow:** RAG URL extraction → guardrail  
**Expected response:** Either cites a reference from documents (with caveat), or clearly states it cannot safely provide current fee information and suggests latrobe.edu.au. Must NOT invent a price.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### EXACT-03 — Current tuition fee
**Question:** `How much is the current tuition fee?`  
**Intent:** `exact_current_info`  
**Flow:** RAG URL extraction → guardrail  
**Expected response:** Must not invent a dollar amount. Directs user to latrobe.edu.au or student services.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### EXACT-04 — Official website URL
**Question:** `What is the official La Trobe University website URL?`  
**Intent:** `exact_current_info`  
**Flow:** RAG URL extraction → guardrail  
**Expected response:** May provide a URL found in documents, or directs to latrobe.edu.au. Must not hallucinate a URL.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 7 — General Conceptual Questions

### CONCEPT-01 — Student wellbeing (core test)
**Question:** `How can campuses improve student wellbeing?`  
**Intent:** `general_conceptual`  
**Flow:** RAG (optional) → Gemini hybrid response  
**Expected response:** General, balanced answer about campus wellbeing strategies. Not La Trobe-specific. No invented links or fees.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### CONCEPT-02 — Benefits of green spaces
**Question:** `What are the benefits of campus green spaces for student wellbeing?`  
**Intent:** `general_conceptual`  
**Flow:** RAG optional → Gemini hybrid  
**Expected response:** General educational response about green spaces and wellbeing. Concise and helpful.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### CONCEPT-03 — Library use habits
**Question:** `How do students usually use the library effectively?`  
**Intent:** `general_conceptual`  
**Flow:** RAG optional → Gemini hybrid  
**Expected response:** Practical general tips for library use. Not claiming to be La Trobe-specific unless context confirms it.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 8 — Normal / General LLM Questions

### LLM-01 — General AI question
**Question:** `What are the advantages of AI chatbots for campuses?`  
**Intent:** `general_conceptual`  
**Flow:** RAG optional → Gemini hybrid  
**Expected response:** General informative answer about AI chatbot benefits. Balanced and factual.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### LLM-02 — Open-ended personal help
**Question:** `I'm stressed about my exams, what should I do?`  
**Intent:** `normal_llm`  
**Flow:** Plain Gemini response  
**Expected response:** Empathetic, practical advice. No invented links or La Trobe-specific claims.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### LLM-03 — Broad general query
**Question:** `Tell me about La Trobe University`  
**Intent:** `normal_llm`  
**Flow:** Plain Gemini response  
**Expected response:** General description of La Trobe University. Should not invent specific current facts (fees, dates). Should suggest latrobe.edu.au for exact details.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Section 9 — Ambiguous Queries

### AMB-01 — Ambiguous sensor or general
**Question:** `Is it hot in there?`  
**Intent:** `sensor_live` (contains "hot" which is a SENSOR_KEYWORD)  
**Flow:** Sync live sensor → InfluxDB → Gemini format  
**Expected response:** Reports current temperature and comments on whether it feels hot. Natural phrasing.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### AMB-02 — Time-ambiguous sensor
**Question:** `Show temperature trend over time`  
**Intent:** `sensor_history`  
**Flow:** Text-to-Flux with default `-30d` range → aggregateWindow → Gemini  
**Expected response:** Reports trend over the last 30 days (default). Should describe the pattern, not individual rows.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### AMB-03 — Destructive-sounding query
**Question:** `Delete all sensor data`  
**Intent:** `sensor_history` (routes via "all sensor" keyword, then Flux safety check blocks it)  
**Flow:** Text-to-Flux → `is_safe_flux_query` blocks "delete" → `text_to_flux_blocked` status  
**Expected response:** "Sorry, I could not safely convert that question into an InfluxDB query." Must NOT execute any delete.  
- [ ] **Pass / Fail:**
- **Notes:** ⚠️ This is expected to be blocked by the safety filter, not executed.

---

## Section 10 — Nonsense / Out-of-Scope Queries

### NOISE-01 — Random gibberish
**Question:** `asdfghjkl`  
**Intent:** `normal_llm`  
**Flow:** Plain Gemini response  
**Expected response:** Handles gracefully — either asks for clarification or gives a polite "I don't understand" response. Must not crash.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### NOISE-02 — Deliberately vague
**Question:** `Tell me everything`  
**Intent:** `normal_llm`  
**Flow:** Plain Gemini response  
**Expected response:** Asks for clarification or gives a short campus-context framing. Should not produce an overwhelming wall of text.  
- [ ] **Pass / Fail:**
- **Notes:**

---

### NOISE-03 — Empty / whitespace query
**Question:** *(send empty string or just spaces)*  
**Intent:** `normal_llm` (routing returns empty-query default)  
**Flow:** Plain Gemini response or router default  
**Expected response:** Handles gracefully. Must not crash the backend.  
- [ ] **Pass / Fail:**
- **Notes:**

---

## Summary Checklist

| ID | Question (abbreviated) | Expected Intent | Pass | Fail | Notes |
|----|------------------------|-----------------|------|------|-------|
| LIVE-01 | Current temperature | sensor_live | | | |
| LIVE-02 | Latest humidity | sensor_live | | | |
| LIVE-03 | Pressure reading now | sensor_live | | | |
| HIST-01 | Show all temperature readings | sensor_history | | | |
| HIST-02 | Humidity in 1995 | sensor_history | | | |
| HIST-03 | Readings from last month | sensor_history | | | |
| HIST-04 | Temperature in April 2026 | sensor_history | | | |
| AGG-01 | Average temperature this week | sensor_history | | | |
| AGG-02 | Highest temperature last month | sensor_history | | | |
| AGG-03 | Lowest humidity this week | sensor_history | | | |
| AGG-04 | How many readings this month | sensor_history | | | |
| TREND-01 | Temperature trend this week | sensor_history | | | |
| TREND-02 | How did temperature change over time | sensor_history | | | |
| TREND-03 | Humidity trend last week | sensor_history | | | |
| RAG-01 | Ask La Trobe services | rag_specific | | | |
| RAG-02 | StudentOnline purpose | rag_specific | | | |
| RAG-03 | Glenn College accommodation | rag_specific | | | |
| RAG-04 | Campus map location | rag_specific | | | |
| RAG-05 | Orientation week | rag_specific | | | |
| EXACT-01 | Link for 2026 academic calendar | exact_current_info | | | |
| EXACT-02 | Weekly rent in Chisholm College | exact_current_info | | | |
| EXACT-03 | Current tuition fee | exact_current_info | | | |
| EXACT-04 | Official La Trobe website URL | exact_current_info | | | |
| CONCEPT-01 | Campus improve student wellbeing | general_conceptual | | | |
| CONCEPT-02 | Benefits of green spaces | general_conceptual | | | |
| CONCEPT-03 | How students use the library | general_conceptual | | | |
| LLM-01 | Advantages of AI chatbots | general_conceptual | | | |
| LLM-02 | Stressed about exams | normal_llm | | | |
| LLM-03 | Tell me about La Trobe | normal_llm | | | |
| AMB-01 | Is it hot in there? | sensor_live | | | |
| AMB-02 | Show temperature trend over time | sensor_history | | | |
| AMB-03 | Delete all sensor data | sensor_history (blocked) | | | |
| NOISE-01 | asdfghjkl | normal_llm | | | |
| NOISE-02 | Tell me everything | normal_llm | | | |
| NOISE-03 | (empty query) | normal_llm | | | |

---

*Total: 35 test cases across 10 categories.*
