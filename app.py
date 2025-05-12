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
    .stContainer {
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #2980b9;
    }
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
def init_session_state():
    config_options = [
        {"selected_comp": "爫", "stroke_count": 4, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "心", "stroke_count": 4, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "⿱", "output_radical": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "⺌", "stroke_count": 3, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "3-Character Phrases"},
        {"selected_comp": "㐱", "stroke_count": 5, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "覀", "stroke_count": 6, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "豕", "stroke_count": 7, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "⿰", "output_radical": "No Filter", "display_mode": "3-Character Phrases"}
    ]
    selected_config = random.choice(config_options)
    defaults = {
        "selected_comp": selected_config["selected_comp"],
        "stroke_count": selected_config["stroke_count"],
        "radical": selected_config["radical"],
        "display_mode": selected_config["display_mode"],
        "selected_idc": selected_config["selected_idc"],
        "component_idc": selected_config["component_idc"],
        "output_radical": selected_config["output_radical"],
        "idc_refresh": False,
        "text_input_comp": selected_config["selected_comp"],
        "page": 1,
        "previous_selected_comp": selected_config["selected_comp"]
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

init_session_state()

# Callback functions
def on_text_input_change(component_map):
    text_value = st.session_state.text_input_comp.strip()
    if len(text_value) != 1:
        st.warning("Please enter exactly one character.")
        return
    if text_value in component_map:
        st.session_state.previous_selected_comp = st.session_state.selected_comp
        st.session_state.selected_comp = text_value
        st.session_state.page = 1
        st.session_state.idc_refresh = not st.session_state.idc_refresh
    else:
        st.warning("Invalid character. Please enter a valid component.")
        st.session_state.text_input_comp = st.session_state.selected_comp

def on_selectbox_change():
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.page = 1
    st.session_state.idc_refresh = not st.session_state.idc_refresh
    st.session_state.text_input_comp = st.session_state.selected_comp

def on_output_char_select(component_map):
    selected_char = st.session_state.output_char_select
    if selected_char == "Select a character..." or selected_char not in component_map:
        if selected_char != "Select a character...":
            st.warning("Invalid character selected.")
        st.session_state.output_char_select = "Select a character..."
        return
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.selected_comp = selected_char
    st.session_state.text_input_comp = selected_char
    st.session_state.page = 1
    st.session_state.idc_refresh = not st.session_state.idc_refresh

def on_reset_filters():
    st.session_state.stroke_count = 0
    st.session_state.radical = "No Filter"
    st.session_state.component_idc = "No Filter"
    st.session_state.selected_idc = "No Filter"
    st.session_state.output_radical = "No Filter"
    st.session_state.page = 1
    st.session_state.idc_refresh = not st.session_state.idc_refresh

def is_reset_needed():
    return (
        st.session_state.stroke_count != 0 or
        st.session_state.radical != "No Filter" or
        st.session_state.component_idc != "No Filter" or
        st.session_state.selected_idc != "No Filter" or
        st.session_state.output_radical != "No Filter"
    )

# Render controls
def render_controls(component_map):
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

    # Filter row for component input filters
    with st.container():
        st.markdown("### Component Filters")
        st.caption("Filter components by stroke count, radical, or structure.")
        col1, col2, col3 = st.columns([0.4, 0.4, 0.4])

        with col1:
            stroke_counts = sorted(set(
                sc for sc in (
                    get_stroke_count(comp) for comp in component_map
                    if isinstance(comp, str) and len(comp) == 1
                ) if isinstance(sc, int) and sc > 0
            ))
            if stroke_counts:
                st.selectbox(
                    "Filter by Strokes:",
                    options=[0] + stroke_counts,
                    key="stroke_count",
                    format_func=lambda x: "No Filter" if x == 0 else str(x)
                )
            else:
                st.warning("No valid stroke counts available. Using fallback options.")
                st.selectbox(
                    "Filter by Strokes:",
                    options=[0],
                    key="stroke_count",
                    format_func=lambda x: "No Filter"
                )

        with col2:
            filtered_components = [
                comp for comp in component_map
                if isinstance(comp, str) and len(comp) == 1 and
                (st.session_state.stroke_count == 0 or get_stroke_count(comp) == st.session_state.stroke_count) and
                (st.session_state.radical == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("radical", "") == st.session_state.radical) and
                (st.session_state.component_idc == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("IDC", "") == st.session_state.component_idc)
            ]
            radicals = {"No Filter"} | {
                component_map.get(c, {}).get("meta", {}).get("radical", "")
                for c in filtered_components
                if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("radical", "")
            }
            radical_options = ["No Filter"] + sorted(radicals - {"No Filter"})
            st.selectbox(
                "Filter by Radical:",
                options=radical_options,
                key="radical"
            )

        with col3:
            component_idcs = {"No Filter"} | {
                component_map.get(c, {}).get("meta", {}).get("IDC", "")
                for c in filtered_components
                if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("IDC", "")
            }
            component_idc_options = ["No Filter"] + sorted(component_idcs - {"No Filter"})
            st.selectbox(
                "Filter by Structure IDC:",
                options=component_idc_options,
                format_func=lambda x: f"{x} ({idc_descriptions.get(x, x)})" if x != "No Filter" else x,
                index=component_idc_options.index(st.session_state.component_idc) if st.session_state.component_idc in component_idc_options else 0,
                key="component_idc"
            )

    # Input row for component selection
    with st.container():
        st.markdown("### Select Input Component")
        st.caption("Choose or type a single character to explore its related characters.")
        col4, col5 = st.columns([1.5, 0.2])

        with col4:
            sorted_components = sorted(filtered_components, key=lambda c: get_stroke_count(c) or 0)
            selectbox_index = 0
            if sorted_components:
                if st.session_state.selected_comp not in sorted_components:
                    st.session_state.selected_comp = sorted_components[0]
                    st.session_state.text_input_comp = sorted_components[0]
                selectbox_index = sorted_components.index(st.session_state.selected_comp)
            else:
                st.session_state.selected_comp = ""
                st.session_state.text_input_comp = ""
                st.warning("No valid components available. Please adjust the stroke count, radical, or IDC filter or check the JSON data.")

            if sorted_components:
                st.selectbox(
                    "Select a component:",
                    options=sorted_components,
                    index=selectbox_index,
                    format_func=lambda c: (
                        f"{c} ({clean_field(component_map.get(c, {}).get('meta', {}).get('pinyin', '—'))}, "
                        f"{clean_field(component_map.get(c, {}).get('meta', {}).get('IDC', '—'))}, "
                        f"{get_stroke_count(c) or 'unknown'} strokes, "
                        f"{clean_field(component_map.get(c, {}).get('meta', {}).get('definition', 'No definition available'))})"
                    ),
                    key="selected_comp",
                    on_change=on_selectbox_change
                )

        with col5:
            st.text_input("Or type:", key="text_input_comp", on_change=on_text_input_change, args=(component_map,))

    # Output filters and results
    with st.container():
        st.markdown("### Filter Output Characters")
        st.caption("Customize the output by character structure and display mode.")
        col6, col7, col8 = st.columns([0.33, 0.33, 0.34])
        with col6:
            idcs = {"No Filter"} | {
                component_map.get(c, {}).get("meta", {}).get("IDC", "")
                for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
                if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("IDC", "")
            }
            idc_options = ["No Filter"] + sorted(idcs - {"No Filter"})
            st.selectbox(
                "Result IDC:",
                options=idc_options,
                format_func=lambda x: f"{x} ({idc_descriptions.get(x, x)})" if x != "No Filter" else x,
                index=idc_options.index(st.session_state.selected_idc) if st.session_state.selected_idc in idc_options else 0,
                key="selected_idc"
            )
        with col7:
            output_radicals = {"No Filter"} | {
                component_map.get(c, {}).get("meta", {}).get("radical", "")
                for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
                if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("radical", "")
            }
            output_radical_options = ["No Filter"] + sorted(output_radicals - {"No Filter"})
            st.selectbox(
                "Result Radical:",
                options=output_radical_options,
                key="output_radical"
            )
        with col8:
            st.radio("Output Type:", ["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"], key="display_mode")
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
    details = " ".join(f"<strong>{k}:</strong> {v}" for k, v in fields.items())
    st.markdown(f"""<div class='char-card'><h3 class='char-title'>{char}</h3><p class='details'>{details}</p>""", unsafe_allow_html=True)
    if compounds and st.session_state.display_mode != "Single Character":
        compounds_text = " ".join(sorted(compounds))
        st.markdown(f"""<div class='compounds-section'><p class='compounds-title'>{st.session_state.display_mode} for {char}:</p><p class='compounds-list'>{compounds_text}</p></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main function
def main():
    if not component_map:
        st.error("No data available. Please check the JSON file.")
        return

    st.markdown("<h1>🧩 Character Decomposition Explorer</h1>", unsafe_allow_html=True)
    render_controls(component_map)

    if not st.session_state.selected_comp:
        st.info("Please select or type a component to view results.")
        return

    meta = component_map.get(st.session_state.selected_comp, {}).get("meta", {})
    fields = {
        "Pinyin": clean_field(meta.get("pinyin", "—")),
        "Definition": clean_field(meta.get("definition", "No definition available")),
        "Radical": clean_field(meta.get("radical", "—")),
        "Hint": clean_field(meta.get("etymology", {}).get("hint", "No hint available")),
        "Strokes": f"{get_stroke_count(st.session_state.selected_comp)} strokes" if get_stroke_count(st.session_state.selected_comp) is not None else "unknown strokes"
    }
    details = " ".join(f"<strong>{k}:</strong> {v}" for k, v in fields.items())
    st.markdown(f"""<div class='selected-card'><h2 class='selected-char'>{st.session_state.selected_comp}</h2><p class='details'>{details}</p></div>""", unsafe_allow_html=True)

    related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
    filtered_chars = [
        c for c in related
        if isinstance(c, str) and len(c) == 1 and
        (st.session_state.selected_idc == "No Filter" or component_map.get(c, {}).get("meta", {}).get("IDC", "") == st.session_state.selected_idc) and
        (st.session_state.output_radical == "No Filter" or component_map.get(c, {}).get("meta", {}).get("radical", "") == st.session_state.output_radical)
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
        options = ["Select a character..."] + sorted(filtered_chars, key=lambda c: get_stroke_count(c) or 0)
        if (st.session_state.previous_selected_comp and
                st.session_state.previous_selected_comp != st.session_state.selected_comp and
                st.session_state.previous_selected_comp not in filtered_chars and
                st.session_state.previous_selected_comp in component_map):
            options.insert(1, st.session_state.previous_selected_comp)
        st.selectbox(
            "Select a character from the list below:",
            options=options,
            key="output_char_select",
            on_change=on_output_char_select,
            args=(component_map,),
            format_func=lambda c: (
                c if c == "Select a character..." else
                f"{c} ({clean_field(component_map.get(c, {}).get('meta', {}).get('pinyin', '—'))}, "
                f"{get_stroke_count(c) or 'unknown'} strokes, "
                f"{clean_field(component_map.get(c, {}).get('meta', {}).get('definition', 'No definition available'))})"
            )
        )

    st.markdown(f"<h2 class='results-header'>🧬 Results for {st.session_state.selected_comp} — {len(filtered_chars)} result(s)</h2>", unsafe_allow_html=True)
    for char in sorted(filtered_chars, key=lambda c: get_stroke_count(c) or 0):
        render_char_card(char, char_compounds.get(char, []))

    if filtered_chars and st.session_state.display_mode != "Single Character":
        with st.expander("Export Compounds"):
            st.caption("Copy this text to get pinyin and meanings for the displayed compounds.")
            export_text = "Give me the hanyu pinyin and meaning of each compound phrase in one line a phrase in a downloadable word file\n\n"
            export_text += "\n".join(
                compound
                for char in filtered_chars
                for compound in char_compounds.get(char, [])
            )
            st.text_area("Export Text", export_text, height=200, key="export_text")
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
