import streamlit as st
import json
import re

# Insert the SignalEngine class we discussed earlier here
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

        # Viltrumite Validation Logic
        if direction == "BUY" and data['sl'] >= data['entry']:
            data['valid'] = False
            data['error'] = "Critical: SL cannot be above Entry for BUY."
        elif direction == "SELL" and data['sl'] <= data['entry']:
            data['valid'] = False
            data['error'] = "Critical: SL cannot be below Entry for SELL."
        
        return data

# --- Streamlit UI ---
st.set_page_config(page_title="FX Signal Parser MVP", page_icon="📈")
st.title("⚡ Institutional Signal Parser")
st.markdown("Proof of Concept: Telegram to FXBlue Logic Bridge")

st.sidebar.header("Instructions")
st.sidebar.info("Paste a raw signal in English, Dutch, or Spanish to see the parser normalize the data for the FXBlue API.")

raw_input = st.text_area("Paste Raw Telegram Signal:", placeholder="e.g., KOOP EURUSD @ 1,0850 | SL: 1,0800 | TP1: 1,0900", height=150)

if st.button("Parse Signal"):
    engine = SignalEngine()
    result = engine.parse_signal(raw_input)
    
    if result.get("valid") == False:
        st.error(f"Validation Failed: {result.get('error')}")
    elif result.get("status") == "Error":
        st.warning(result.get("message"))
    else:
        st.success("Signal Normalized Successfully")
    
    st.subheader("Normalized Output (JSON for API)")
    st.json(result)

st.divider()
st.caption("Built for Phase 1 MVP - Secure Backend Logic")
