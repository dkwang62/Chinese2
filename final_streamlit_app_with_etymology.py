
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# --- Load Data ---
@st.cache_data
def load_enhanced_component_map():
    with open("enhanced_component_map_with_etymology.json", "r", encoding="utf-8") as f:
        return json.load(f)

component_map = load_enhanced_component_map()

# --- Utilities ---
def clean_field(field):
    return field[0] if isinstance(field, list) and field else field or "—"

def get_stroke_count(char):
    return component_map.get(char, {}).get("meta", {}).get("strokes", -1)

def get_all_related_characters(comp, stroke_range, idc_filter):
    chars = component_map.get(comp, {}).get("related_characters", [])
    result = []
    for c in chars:
        meta = component_map.get(c, {}).get("meta", {})
        if not meta:
            continue
        strokes = meta.get("strokes", -1)
        if not (stroke_range[0] <= strokes <= stroke_range[1]):
            continue
        idc = meta.get("IDC", "—")
        if idc_filter == "No Filter" or idc == idc_filter:
            result.append(c)
    return result

# --- UI Elements ---
def render_char_card(char):
    entry = component_map.get(char, {})
    meta = entry.get("meta", {})
    fields = {
        "Pinyin": clean_field(meta.get("pinyin")),
        "Definition": clean_field(meta.get("definition")),
        "Radical": clean_field(meta.get("radical")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint")),
        "Strokes": f"{meta.get('strokes', '—')} strokes",
        "IDC": clean_field(meta.get("IDC"))
    }
    details = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in fields.items())
    st.markdown(f"<div class='char-card'><h3 class='char-title'>{char}</h3><p class='details'>{details}</p></div>", unsafe_allow_html=True)

# --- Main App ---
st.title("🧩 Character Decomposition Explorer")

default_comp = "心"
if "selected_comp" not in st.session_state:
    st.session_state.selected_comp = default_comp
    st.session_state.stroke_range = (4, 14)
    st.session_state.selected_idc = "No Filter"

col1, col2 = st.columns([2, 3])
with col1:
    st.session_state.selected_comp = st.selectbox("Select Component", sorted(component_map.keys()),
        index=sorted(component_map.keys()).index(st.session_state.selected_comp))
    st.session_state.stroke_range = st.slider("Stroke Range", 0, 30, st.session_state.stroke_range)
    idcs = {"No Filter"} | {component_map[c]["meta"].get("IDC", "—") for c in component_map[st.session_state.selected_comp]["related_characters"]}
    st.session_state.selected_idc = st.selectbox("IDC Filter", sorted(idcs))

with col2:
    meta = component_map[st.session_state.selected_comp]["meta"]
    details = {
        "Pinyin": clean_field(meta.get("pinyin")),
        "Definition": clean_field(meta.get("definition")),
        "Radical": clean_field(meta.get("radical")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint")),
        "Strokes": f"{meta.get('strokes', '—')} strokes",
        "IDC": clean_field(meta.get("IDC"))
    }
    detail_str = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in details.items())
    st.markdown(f"<div class='selected-card'><h2 class='selected-char'>{st.session_state.selected_comp}</h2><p class='details'>{detail_str}</p></div>", unsafe_allow_html=True)

filtered_chars = get_all_related_characters(st.session_state.selected_comp, st.session_state.stroke_range, st.session_state.selected_idc)
st.markdown(f"<h2 class='results-header'>🧬 Characters with {st.session_state.selected_comp} — {len(filtered_chars)} result(s)</h2>", unsafe_allow_html=True)

for char in sorted(filtered_chars, key=get_stroke_count):
    render_char_card(char)

# --- Export Block ---
if filtered_chars:
    export_text = "Give me the hanyu pinyin and meaning of each compound phrase in one line a phrase in a downloadable word file

"
    export_text += "\n".join(
        f"{compound}"
        for char in filtered_chars
        for compound in component_map.get(char, {}).get("meta", {}).get("compounds", [])
    )
    st.text_area("Right click, Select all, copy; paste to ChatGPT", export_text, height=300, key="export_text")

    components.html(f"""
        <textarea id="copyTarget" style="opacity:0;position:absolute;left:-9999px;">{export_text}</textarea>
        <script>
        const copyText = document.getElementById("copyTarget");
        copyText.select();
        document.execCommand("copy");
        </script>
    """, height=0)
