import json
import random
import streamlit as st
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(layout="wide")

# Global IDC characters
IDC_CHARS = {'⿰', '⿱', '⿲', '⿳', '⿴', '⿵', '⿶', '⿷', '⿸', '⿹', '⿺', '⿻'}

# Custom CSS
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

# Load component map
@st.cache_data
def load_component_map():
    try:
        with open("enhanced_component_map_with_etymology.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load enhanced_component_map_with_etymology.json: {e}")
        return {}

component_map = load_component_map()

# Utility functions
def clean_field(field):
    return field[0] if isinstance(field, list) and field else field or "—"

def get_stroke_count(char):
    strokes = component_map.get(char, {}).get("meta", {}).get("strokes", None)
    try:
        if isinstance(strokes, (int, float)) and strokes > 0:
            return int(strokes)
        elif isinstance(strokes, str) and strokes.isdigit():
            return int(strokes)
    except (TypeError, ValueError):
        pass
    return None

# Session state initialization
def init_session():
    config_options = [
        {"selected_comp": "爫", "stroke_range": (4, 14), "selected_idc": "No Filter", "component_idc": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "心", "stroke_range": (4, 14), "selected_idc": "No Filter", "component_idc": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "⺌", "stroke_range": (3, 14), "selected_idc": "No Filter", "component_idc": "No Filter", "display_mode": "3-Character Phrases"},
        {"selected_comp": "㐱", "stroke_range": (5, 14), "selected_idc": "No Filter", "component_idc": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "覀", "stroke_range": (6, 14), "selected_idc": "No Filter", "component_idc": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "豕", "stroke_range": (7, 14), "selected_idc": "No Filter", "component_idc": "No Filter", "display_mode": "3-Character Phrases"}
    ]
    selected_config = random.choice(config_options)
    defaults = {
        "selected_comp": selected_config["selected_comp"],
        "stroke_range": selected_config["stroke_range"],
        "display_mode": selected_config["display_mode"],
        "selected_idc": selected_config["selected_idc"],
        "component_idc": selected_config["component_idc"],
        "text_input_comp": selected_config["selected_comp"],
        "page": 1,
        "results_per_page": 50,
        "previous_selected_comp": selected_config["selected_comp"],
        "output_char_select": "Select a character..."
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

init_session()

# Callback functions
def update_selected_comp(val):
    if len(val.strip()) != 1:
        st.warning("Please enter exactly one character.")
        return
    if val in component_map:
        st.session_state.previous_selected_comp = st.session_state.selected_comp
        st.session_state.selected_comp = val
        st.session_state.text_input_comp = val
        st.session_state.page = 1
    else:
        st.warning("Invalid character. Please enter a valid component.")
        st.session_state.text_input_comp = st.session_state.selected_comp

def on_output_select():
    val = st.session_state.output_char_select
    if val == "Select a character..." or val not in component_map:
        if val != "Select a character...":
            st.warning("Invalid character selected.")
        st.session_state.output_char_select = "Select a character..."
        return
    update_selected_comp(val)

def on_reset_filters():
    st.session_state.stroke_range = (0, 30)
    st.session_state.selected_idc = "No Filter"
    st.session_state.component_idc = "No Filter"
    st.session_state.page = 1

def is_reset_needed():
    min_strokes, max_strokes = st.session_state.stroke_range
    return (
        min_strokes != 0 or max_strokes != 30 or
        st.session_state.selected_idc != "No Filter" or
        st.session_state.component_idc != "No Filter"
    )

# Render controls
def render_controls():
    idc_descriptions = {
        "No Filter": "No Filter",
        "⿰": "Left Right",
        "⿱": "Top Bottom",
        "⿲": "Left Middle Right",
        "⿳": "Top Middle Bottom",
        "⿴": "Surround",
        "⿵": "Surround Top",
        "⿶": "Surround Bottom",
        "⿷": "Surround Left",
        "⿸": "Top Left Corner",
        "⿹": "Top Right Corner",
        "⿺": "Bottom Left Corner",
        "⿻": "Overlaid"
    }

    min_strokes, max_strokes = st.session_state.stroke_range
    filtered_components = [
        comp for comp in component_map
        if isinstance(comp, str) and len(comp) == 1 and
        min_strokes <= (get_stroke_count(comp) or 0) <= max_strokes and
        (st.session_state.component_idc == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("IDC", "") == st.session_state.component_idc)
    ]
    sorted_components = sorted(filtered_components, key=lambda c: get_stroke_count(c) or 0)
    if st.session_state.selected_comp not in sorted_components and st.session_state.selected_comp in component_map:
        sorted_components.insert(0, st.session_state.selected_comp)

    col1, col2, col3 = st.columns(3)
    with col1:
        if sorted_components:
            st.selectbox(
                "Select a component:",
                options=sorted_components,
                index=sorted_components.index(st.session_state.selected_comp) if st.session_state.selected_comp in sorted_components else 0,
                format_func=lambda c: (
                    f"{c} ({clean_field(component_map.get(c, {}).get('meta', {}).get('pinyin', '—'))}, "
                    f"{get_stroke_count(c) or 'unknown'} strokes, "
                    f"{clean_field(component_map.get(c, {}).get('meta', {}).get('definition', 'No definition available'))})"
                ),
                key="selected_comp",
                on_change=lambda: update_selected_comp(st.session_state.selected_comp)
            )
        else:
            st.warning("No valid components available. Please adjust the stroke range or IDC filter or check the JSON data.")

    with col2:
        st.text_input("Or type a component:", value=st.session_state.text_input_comp, key="text_input_comp", on_change=lambda: update_selected_comp(st.session_state.text_input_comp))

    with col3:
        component_idcs = {"No Filter"} | {
            component_map.get(c, {}).get("meta", {}).get("IDC", "")
            for c in component_map
            if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("IDC", "")
        }
        component_idc_options = ["No Filter"] + sorted(component_idcs - {"No Filter"})
        st.selectbox(
            "Component IDC:",
            options=component_idc_options,
            format_func=lambda x: f"{x} ({idc_descriptions.get(x, x)})" if x != "No Filter" else x,
            index=component_idc_options.index(st.session_state.component_idc) if st.session_state.component_idc in component_idc_options else 0,
            key="component_idc"
        )

        idcs = {"No Filter"} | {
            component_map.get(c, {}).get("meta", {}).get("IDC", "")
            for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
            if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("IDC", "")
        }
        idc_options = ["No Filter"] + sorted(idcs - {"No Filter"})
        st.selectbox(
            "Output IDC:",
            options=idc_options,
            format_func=lambda x: f"{x} ({idc_descriptions.get(x, x)})" if x != "No Filter" else x,
            index=idc_options.index(st.session_state.selected_idc) if st.session_state.selected_idc in idc_options else 0,
            key="selected_idc"
        )

    st.slider("Strokes Range", 0, 30, st.session_state.stroke_range, key="stroke_range")
    st.radio("Display Mode:", ["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"], key="display_mode")
    st.button("Reset Filters", on_click=on_reset_filters, disabled=not is_reset_needed())

# Render character card
def render_char_card(char, compounds):
    meta = component_map.get(char, {}).get("meta", {})
    fields = {
        "Pinyin": clean_field(meta.get("pinyin", "—")),
        "Definition": clean_field(meta.get("definition", "No definition available")),
        "Radical": clean_field(meta.get("radical", "—")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint", "No hint available")),
        "Strokes": f"{get_stroke_count(char)} strokes" if get_stroke_count(char) is not None else "unknown strokes",
        "IDC": clean_field(meta.get("IDC", "—"))
    }
    details = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in fields.items())
    st.markdown(f"<div class='char-card'><h3 class='char-title'>{char}</h3><p class='details'>{details}</p>", unsafe_allow_html=True)
    if compounds and st.session_state.display_mode != "Single Character":
        compounds_text = " ".join(sorted(compounds))
        st.markdown(f"<div class='compounds-section'><p class='compounds-title'>{st.session_state.display_mode} for {char}:</p><p class='compounds-list'>{compounds_text}</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main function
def main():
    if not component_map:
        st.error("No data available. Please check the JSON file.")
        return

    st.markdown("<h1>🧩 Character Decomposition Explorer</h1>", unsafe_allow_html=True)
    render_controls()

    if not st.session_state.selected_comp or st.session_state.selected_comp not in component_map:
        st.info("Please select or type a valid component to view results.")
        return

    meta = component_map.get(st.session_state.selected_comp, {}).get("meta", {})
    fields = {
        "Pinyin": clean_field(meta.get("pinyin", "—")),
        "Definition": clean_field(meta.get("definition", "No definition available")),
        "Radical": clean_field(meta.get("radical", "—")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint", "No hint available")),
        "Strokes": f"{get_stroke_count(st.session_state.selected_comp)} strokes" if get_stroke_count(st.session_state.selected_comp) is not None else "unknown strokes",
        "IDC": clean_field(meta.get("IDC", "—")),
        "Stroke Range": f"{st.session_state.stroke_range[0]} – {st.session_state.stroke_range[1]}"
    }
    details = " ".join(f"<strong>{k}:</strong> {v}  " for k, v in fields.items())
    st.markdown(f"<div class='selected-card'><h2 class='selected-char'>{st.session_state.selected_comp}</h2><p class='details'>{details}</p></div>", unsafe_allow_html=True)

    related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
    filtered_chars = [
        c for c in related
        if isinstance(c, str) and len(c) == 1 and
        (st.session_state.selected_idc == "No Filter" or component_map.get(c, {}).get("meta", {}).get("IDC", "") == st.session_state.selected_idc)
    ]

    char_compounds = {
        c: [] if st.session_state.display_mode == "Single Character" else [
            comp for comp in component_map.get(c, {}).get("meta", {}).get("compounds", [])
            if len(comp) == int(st.session_state.display_mode[0])
        ]
        for c in filtered_chars
    }
    filtered_chars = [c for c in filtered_chars if st.session_state.display_mode == "Single Character" or char_compounds[c]]

    if filtered_chars:
        dropdown_options = ["Select a character..."] + sorted(filtered_chars, key=lambda c: get_stroke_count(c) or 0)
        if (
            st.session_state.previous_selected_comp and
            st.session_state.previous_selected_comp != st.session_state.selected_comp and
            st.session_state.previous_selected_comp not in filtered_chars and
            st.session_state.previous_selected_comp in component_map
        ):
            dropdown_options.insert(1, st.session_state.previous_selected_comp)

        st.selectbox(
            "Select a character from the list below:",
            options=dropdown_options,
            key="output_char_select",
            on_change=on_output_select,
            format_func=lambda c: (
                c if c == "Select a character..." else
                f"{c} ({clean_field(component_map.get(c, {}).get('meta', {}).get('pinyin', '—'))}, "
                f"{get_stroke_count(c) or 'unknown'} strokes, "
                f"{clean_field(component_map.get(c, {}).get('meta', {}).get('definition', 'No definition available'))})"
            )
        )

    st.markdown(f"<h2 class='results-header'>🧬 Characters with {st.session_state.selected_comp} — {len(filtered_chars)} result(s)</h2>", unsafe_allow_html=True)
    for c in sorted(filtered_chars, key=lambda c: get_stroke_count(c) or 0):
        render_char_card(c, char_compounds.get(c, []))

    if filtered_chars and st.session_state.display_mode != "Single Character":
        export_text = "Give me the hanyu pinyin and meaning of each compound phrase in one line a phrase in a downloadable word file\n\n"
        export_text += "\n".join(
            compound
            for c in filtered_chars
            for compound in char_compounds.get(c, [])
        )
        st.text_area("Right click, Select all, copy; paste to ChatGPT", export_text, height=300)
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
