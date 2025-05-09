
import json
import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(layout="wide")

st.markdown("""<style>
.selected-card {
    background-color: #e8f4f8;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 15px;
    border-left: 5px solid #3498db;
}
.selected-char { font-size: 2.5em; color: #e74c3c; margin: 0; }
.details { font-size: 1.5em; color: #34495e; margin: 0; }
.details strong { color: #2c3e50; }
.results-header { font-size: 1.5em; color: #2c3e50; margin: 20px 0 10px; }
.char-card {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.char-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}
.char-title { font-size: 1.4em; color: #e74c3c; margin: 0; display: inline; }
.compounds-section {
    background-color: #f1f8e9;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
}
.compounds-title { font-size: 1.1em; color: #558b2f; margin: 0 0 5px; }
.compounds-list { font-size: 1em; color: #34495e; margin: 0; }
@media (max-width: 768px) {
    .selected-card { flex-direction: column; align-items: flex-start; padding: 10px; }
    .selected-char { font-size: 2em; }
    .details, .compounds-list { font-size: 0.95em; line-height: 1.5; }
    .results-header { font-size: 1.3em; }
    .char-card { padding: 10px; }
    .char-title { font-size: 1.2em; }
    .compounds-title { font-size: 1em; }
}
</style>""", unsafe_allow_html=True)

# --- Load preprocessed component map ---
@st.cache_data
def load_component_map():
    with open("enhanced_component_map_with_etymology.json", "r", encoding="utf-8") as f:
        return json.load(f)

component_map = load_component_map()

# --- Custom CSS ---
st.markdown("""
<style>
/* (CSS omitted for brevity - same styling preserved) */
</style>
""", unsafe_allow_html=True)

# --- Utility Functions ---
def clean_field(field):
    return field[0] if isinstance(field, list) and field else field or "—"

def get_stroke_count(char):
    return component_map.get(char, {}).get("meta", {}).get("strokes", -1)

# --- Session State Init ---
def init_session():
    if "selected_comp" not in st.session_state:
        config_options = [
            {"selected_comp": "爫", "stroke_range": (4, 14)},
            {"selected_comp": "心", "stroke_range": (4, 14)},
            {"selected_comp": "⺌", "stroke_range": (3, 14)}
        ]
        selected = random.choice(config_options)
        st.session_state.selected_comp = selected["selected_comp"]
        st.session_state.previous_selected_comp = selected["selected_comp"]
        st.session_state.stroke_range = selected["stroke_range"]
        st.session_state.display_mode = "Single Character"
        st.session_state.selected_idc = "No Filter"
        st.session_state.text_input_comp = selected["selected_comp"]
        st.session_state.page = 1
        st.session_state.results_per_page = 50
        st.session_state.output_char_select = "Select a character..."

init_session()

def update_selected_comp(val):
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.selected_comp = val
    st.session_state.text_input_comp = val
    st.session_state.page = 1

def on_output_select():
    val = st.session_state.output_char_select
    if val != "Select a character..." and val in component_map:
        update_selected_comp(val)
    else:
        st.session_state.output_char_select = "Select a character..."

# --- Controls ---
def render_controls():
    min_strokes, max_strokes = st.session_state.stroke_range
    filtered_components = [
        comp for comp in component_map
        if min_strokes <= get_stroke_count(comp) <= max_strokes
    ]
    sorted_components = sorted(filtered_components, key=get_stroke_count)
    if st.session_state.selected_comp not in sorted_components:
        sorted_components.insert(0, st.session_state.selected_comp)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Select a component:", sorted_components,
                    format_func=lambda c: f"{c} ({clean_field(component_map[c]['meta'].get('pinyin'))}, {get_stroke_count(c)} strokes, {clean_field(component_map[c]['meta'].get('definition'))})",
                    index=sorted_components.index(st.session_state.selected_comp),
                    key="selected_comp", on_change=lambda: update_selected_comp(st.session_state.selected_comp))
    with col2:
        st.text_input("Or type a component:", value=st.session_state.text_input_comp,
                    key="text_input_comp", on_change=lambda: update_selected_comp(st.session_state.text_input_comp))
    with col3:
        idcs = {"No Filter"}
        for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", []):
            idc = component_map.get(c, {}).get("meta", {}).get("IDC", "—")
            if idc and idc != "—":
                idcs.add(idc)
        idc_list = sorted(list(idcs))
        if st.session_state.selected_idc not in idc_list:
            st.session_state.selected_idc = "No Filter"
        st.selectbox("IDC Filter:", idc_list, key="selected_idc")

    st.slider("Strokes Range", 0, 30, st.session_state.stroke_range, key="stroke_range")
    st.radio("Display Mode:", ["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"], key="display_mode")

# --- Character Card ---
def render_char_card(char, compounds):
    meta = component_map.get(char, {}).get("meta", {})
    fields = {
        "Pinyin": clean_field(meta.get("pinyin")),
        "Definition": clean_field(meta.get("definition")),
        "Radical": clean_field(meta.get("radical")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint")),
        "Strokes": f"{meta.get("strokes", "—")} strokes",
        "IDC": clean_field(meta.get("IDC"))
    }
    details = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in fields.items())
    st.markdown(f"<div class='char-card'><h3 class='char-title'>{char}</h3><p class='details'>{details}</p>", unsafe_allow_html=True)
    if compounds and st.session_state.display_mode != "Single Character":
        compound_str = " ".join(sorted(compounds))
        st.markdown(f"<div class='compounds-section'><p class='compounds-title'>{st.session_state.display_mode} for {char}:</p><p class='compounds-list'>{compound_str}</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main ---
st.markdown("<h1>🧩 Character Decomposition Explorer</h1>", unsafe_allow_html=True)
render_controls()

# --- Selected Summary ---
meta = component_map.get(st.session_state.selected_comp, {}).get("meta", {})
fields = {
    "Pinyin": clean_field(meta.get("pinyin")),
    "Definition": clean_field(meta.get("definition")),
    "Radical": clean_field(meta.get("radical")),
    "Hint": clean_field(meta.get("etymology", {}).get("hint")),
    "Strokes": f"{meta.get("strokes", "—")} strokes",
    "IDC": clean_field(meta.get("IDC")),
    "Stroke Range": f"{st.session_state.stroke_range[0]} – {st.session_state.stroke_range[1]}"
}
details = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in fields.items())
st.markdown(f"<div class='selected-card'><h2 class='selected-char'>{st.session_state.selected_comp}</h2><p class='details'>{details}</p></div>", unsafe_allow_html=True)

# --- Filter Characters ---
min_s, max_s = st.session_state.stroke_range
related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
filtered_chars = []
for c in related:
    meta = component_map.get(c, {}).get("meta", {})
    if not (min_s <= meta.get("strokes", 0) <= max_s):
        continue
    if st.session_state.selected_idc != "No Filter" and meta.get("IDC") != st.session_state.selected_idc:
        continue
    filtered_chars.append(c)

char_compounds = {}
for c in filtered_chars:
    meta = component_map.get(c, {}).get("meta", {})
    compounds = meta.get("compounds", [])
    if st.session_state.display_mode == "Single Character":
        char_compounds[c] = []
    else:
        n = int(st.session_state.display_mode[0])
        char_compounds[c] = [p for p in compounds if len(p) == n]

filtered_chars = [c for c in filtered_chars if st.session_state.display_mode == "Single Character" or char_compounds[c]]

# --- Dropdown output selection ---
if filtered_chars:
    dropdown_options = ["Select a character..."] + sorted(filtered_chars, key=get_stroke_count)
if (st.session_state.previous_selected_comp and 
        st.session_state.previous_selected_comp != st.session_state.selected_comp and 
        st.session_state.previous_selected_comp not in filtered_chars and 
        st.session_state.previous_selected_comp in component_map):
        dropdown_options.insert(1, st.session_state.previous_selected_comp)
    st.selectbox("Select a character from the list below:", dropdown_options, key="output_char_select", on_change=on_output_select,
                format_func=lambda c: c if c == "Select a character..." else f"{c} ({clean_field(component_map[c]['meta'].get('pinyin'))}, {get_stroke_count(c)} strokes, {clean_field(component_map[c]['meta'].get('definition'))})")

# --- Render Results ---
st.markdown(f"<h2 class='results-header'>🧬 Characters with {st.session_state.selected_comp} — {len(filtered_chars)} result(s)</h2>", unsafe_allow_html=True)
for c in sorted(filtered_chars, key=get_stroke_count):
    render_char_card(c, char_compounds.get(c, []))

# --- Export Copy Text ---
if filtered_chars:
    export_text = "Give me the hanyu pinyin and meaning of each compound phrase in one line a phrase in a downloadable word file\n\n"
    export_text += "\n".join(comp for c in filtered_chars for comp in char_compounds.get(c, []))
    st.text_area("Right click, Select all, copy; paste to ChatGPT", export_text, height=300)
    components.html(f"""
        <textarea id="copyTarget" style="opacity:0;position:absolute;left:-9999px;">{export_text}</textarea>
        <script>
        const copyText = document.getElementById("copyTarget");
        copyText.select();
        document.execCommand("copy");
        </script>
    """, height=0)