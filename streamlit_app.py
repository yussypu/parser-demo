import streamlit as st
import json
import re

class SignalEngine:
    def __init__(self):
        self.keywords = {
            "buy": ["buy", "koop", "compra", "long", "bullish"],
            "sell": ["sell", "verkoop", "venta", "short", "bearish"]
        }

    def normalize_numbers(self, text):
        return text.replace(',', '.')

    def parse_signal(self, raw_text):
        text = self.normalize_numbers(raw_text.lower())
        direction = next((k.upper() for k, v in self.keywords.items() if any(a in text for a in v)), None)
        pair = re.search(r'([a-z]{3}/?[a-z]{3}|gold|xauusd|us30|nas100)', text)
        prices = re.findall(r'(\d{1,5}\.\d{1,5}|\d{4,5})', text)

        if not direction or not pair or len(prices) < 2:
            return {"status": "Error", "message": "Incomplete data. Need Pair, Direction, Entry, and SL."}

        data = {
            "pair": pair.group(0).upper().replace('/', ''),
            "type": direction,
            "entry": float(prices[0]),
            "sl": float(prices[1]),
            "tp_levels": [float(p) for p in prices[2:]],
            "valid": True
        }

        if direction == "BUY" and data['sl'] >= data['entry']:
            data['valid'] = False
            data['error'] = "Critical: SL cannot be above Entry for BUY."
        elif direction == "SELL" and data['sl'] <= data['entry']:
            data['valid'] = False
            data['error'] = "Critical: SL cannot be below Entry for SELL."
        
        return data

st.set_page_config(page_title="FX Signal Parser MVP")
st.title("Institutional Signal Parser")
st.markdown("### Phase 1 MVP: Telegram-to-FXBlue Bridge")

st.subheader("Try a Live Example")
col1, col2, col3 = st.columns(3)

examples = {
    "English": "BUY GBPUSD @ 1.2650 | SL: 1.2600 | TP1: 1.2700 | TP2: 1.2750",
    "Dutch": "KOOP EUR/USD entry 1,0850 stop 1,0800 tp 1,0900 tp 1,0950",
    "Spanish": "Venta XAUUSD entrada 2035.50 sl 2045.00 tp 2020.00"
}

# Button Logic to pre-fill the text area
if col1.button("English"):
    st.session_state.raw_input = examples["English"]
if col2.button("Dutch"):
    st.session_state.raw_input = examples["Dutch"]
if col3.button("Spanish"):
    st.session_state.raw_input = examples["Spanish"]

# The Input Area (initialized with session state)
if 'raw_input' not in st.session_state:
    st.session_state.raw_input = ""

raw_input = st.text_area(
    "Paste Raw Telegram Signal:", 
    value=st.session_state.raw_input,
    placeholder="Paste or click an example above...", 
    height=120
)

if st.button("Parse & Validate Signal", type="primary"):
    if raw_input:
        engine = SignalEngine()
        result = engine.parse_signal(raw_input)
        
        if result.get("valid") == False:
            st.error(f"Validation Failed: {result.get('error')}")
            st.json(result)
        elif result.get("status") == "Error":
            st.warning(f"Partial Data Detected: {result.get('message')}")
        else:
            st.success("Institutional Signal Normalized")
            
            # Human Readable summary before the JSON
            st.info(f"**Executing {result['type']} on {result['pair']}** at {result['entry']}. Protection set at {result['sl']}.")
            
            st.subheader("Developer Output (JSON)")
            st.json(result)
    else:
        st.write("Please enter a signal or click an example above.")

st.divider()
st.caption("Architecture: Python Backend | Regex Normalization | FXBlue API Compatible")
