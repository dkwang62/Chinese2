
import json
from collections import defaultdict
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# --- Load Enhanced Component Map ---
@st.cache_data
def load_component_map():
    with open("enhanced_component_map_with_etymology.json", "r", encoding="utf-8") as f:
        return json.load(f)

component_map = load_component_map()

# --- Utility Functions ---
def clean_field(field):
    return field[0] if isinstance(field, list) and field else field or "—"

def get_stroke_count(char):
    return component_map.get(char, {}).get("meta", {}).get("strokes", -1)

def update_selected_comp(new_comp):
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.selected_comp = new_comp
    st.session_state.text_input_comp = new_comp
    st.session_state.idc_refresh = not st.session_state.idc_refresh
    st.session_state.page = 1

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
        compounds_text = " ".join(sorted(compounds, key=lambda x: x[0]))
        st.markdown(f"<div class='compounds-section'><p class='compounds-title'>{st.session_state.display_mode} for {char}:</p><p class='compounds-list'>{compounds_text}</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Session State Initialization ---
def init_session_state():
    if "selected_comp" not in st.session_state:
        st.session_state.selected_comp = "心"
        st.session_state.previous_selected_comp = "心"
        st.session_state.max_depth = 3
        st.session_state.stroke_range = (4, 14)
        st.session_state.display_mode = "Single Character"
        st.session_state.selected_idc = "No Filter"
        st.session_state.text_input_comp = "心"
        st.session_state.page = 1
        st.session_state.results_per_page = 50
        st.session_state.idc_refresh = False

init_session_state()

# --- Controls UI ---
def render_controls():
    min_strokes, max_strokes = st.session_state.stroke_range
    all_components = sorted(component_map.keys(), key=get_stroke_count)
    if st.session_state.selected_comp not in all_components:
        all_components.insert(0, st.session_state.selected_comp)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Select a component:", options=all_components,
                     format_func=lambda c: f"{c} ({get_stroke_count(c)} strokes)",
                     index=all_components.index(st.session_state.selected_comp),
                     key="selected_comp", on_change=lambda: update_selected_comp(st.session_state.selected_comp))
    with col2:
        st.text_input("Or type a component:", value=st.session_state.selected_comp,
                      key="text_input_comp", on_change=lambda: update_selected_comp(st.session_state.text_input_comp))
    with col3:
        idc_options = {"No Filter"}
        for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", []):
            meta = component_map.get(c, {}).get("meta", {})
            idc = meta.get("IDC", "—")
            if idc != "—":
                idc_options.add(idc)
        idc_list = sorted(list(idc_options))
        st.selectbox("IDC Filter:", options=idc_list,
                     index=idc_list.index(st.session_state.selected_idc),
                     key="selected_idc")

    st.slider("Strokes Range", 0, 30, key="stroke_range")
    st.radio("Display Mode:", options=["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"],
             key="display_mode")

# --- Main ---
def main():
    st.markdown("<h1>🧩 Character Decomposition Explorer</h1>", unsafe_allow_html=True)
    render_controls()

    selected = st.session_state.selected_comp
    meta = component_map.get(selected, {}).get("meta", {})
    fields = {
        "Pinyin": clean_field(meta.get("pinyin")),
        "Definition": clean_field(meta.get("definition")),
        "Radical": clean_field(meta.get("radical")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint")),
        "Strokes": f"{meta.get("strokes", '—')} strokes",
        "IDC": clean_field(meta.get("IDC")),
        "Stroke Range": f"{st.session_state.stroke_range[0]} – {st.session_state.stroke_range[1]}"
    }
    detail_str = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in fields.items())
    st.markdown(f"<div class='selected-card'><h2 class='selected-char'>{selected}</h2><p class='details'>{detail_str}</p></div>", unsafe_allow_html=True)

    # Filter characters
    min_s, max_s = st.session_state.stroke_range
    related_chars = component_map.get(selected, {}).get("related_characters", [])
    filtered = []
    for c in related_chars:
        m = component_map.get(c, {}).get("meta", {})
        strokes = m.get("strokes", -1)
        if strokes < min_s or strokes > max_s:
            continue
        if st.session_state.selected_idc != "No Filter" and m.get("IDC", "") != st.session_state.selected_idc:
            continue
        filtered.append(c)

    char_compounds = {}
    for c in filtered:
        compounds = component_map.get(c, {}).get("meta", {}).get("compounds", [])
        if st.session_state.display_mode == "Single Character":
            char_compounds[c] = []
        else:
            length = int(st.session_state.display_mode[0])
            char_compounds[c] = [comp for comp in compounds if len(comp) == length]

    filtered_chars = [c for c in filtered if char_compounds[c] or st.session_state.display_mode == "Single Character"]

    st.markdown(f"<h2 class='results-header'>🧬 Characters with {selected} — {len(filtered_chars)} result(s)</h2>", unsafe_allow_html=True)
    for char in sorted(filtered_chars, key=get_stroke_count):
        render_char_card(char, char_compounds.get(char, []))

    if filtered_chars:
        export_text = "Give me the hanyu pinyin and meaning of each compound phrase in one line a phrase in a downloadable word file\n\n"
        export_text += "\n".join(
            f"{compound}"
            for char in filtered_chars
            for compound in char_compounds.get(char, [])
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

if __name__ == "__main__":
    main()
