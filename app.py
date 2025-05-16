import json
import random
import streamlit as st
import streamlit.components.v1 as components

# CSS Styles
CSS_STYLES = """
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
.debug-section {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
    margin-top: 20px;
}
.diagnostic-message.error { color: #c0392b; }
.diagnostic-message.warning { color: #e67e22; }
@media (max-width: 768px) {
    .selected-card { flex-direction: column; align-items: flex-start; padding: 10px; }
    .selected-char { font-size: 2em; }
    .details, .compounds-list { font-size: 0.95em; line-height: 1.5; }
    .results-header { font-size: 1.3em; }
    .char-card { padding: 10px; }
    .char-title { font-size: 1.2em; }
    .compounds-title { font-size: 1em; }
}
"""

# Constants
IDC_CHARS = {'⿰', '⿱', '⿲', '⿳', '⿴', '⿵', '⿶', '⿷', '⿸', '⿹', '⿺', '⿻'}

IDC_DESCRIPTIONS = {
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

# Utility Functions
@st.cache_data
def load_component_map():
    try:
        with open("enhanced_component_map_with_etymology.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for char, entry in data.items():
                decomposition = entry.get("meta", {}).get("decomposition", "")
                if '?' in decomposition:
                    st.session_state.diagnostic_messages.append({
                        "type": "warning",
                        "message": f"Invalid component '?' in decomposition for {char}: {decomposition}"
                    })
                    entry["meta"]["decomposition"] = ""
            return data
    except Exception as e:
        error_msg = f"Failed to load enhanced_component_map_with_etymology.json: {e}"
        st.session_state.diagnostic_messages.append({"type": "error", "message": error_msg})
        return {}

def clean_field(field):
    return field[0] if isinstance(field, list) and field else field or "—"

def get_stroke_count(char, component_map):
    strokes = component_map.get(char, {}).get("meta", {}).get("strokes", None)
    try:
        if isinstance(strokes, (int, float)) and strokes > 0:
            return int(strokes)
        elif isinstance(strokes, str) and strokes.isdigit():
            return int(strokes)
    except (TypeError, ValueError):
        pass
    return None

def get_etymology_text(meta):
    etymology = meta.get("etymology", {})
    hint = clean_field(etymology.get("hint", "No hint available"))
    details = clean_field(etymology.get("details", ""))
    return f"{hint}{'; Details: ' + details if details and details != '—' else ''}"

def format_decomposition(char, component_map):
    decomposition = component_map.get(char, {}).get("meta", {}).get("decomposition", "")
    if not decomposition or '?' in decomposition:
        return "—"
    if decomposition[0] not in IDC_CHARS:
        return decomposition
    return decomposition

def get_all_components(char, component_map, max_depth, depth=0, seen=None):
    if seen is None:
        seen = set()
    if char in seen or depth > max_depth or not isinstance(char, str) or len(char) != 1:
        return set()
    seen.add(char)
    components = set()
    decomposition = component_map.get(char, {}).get("meta", {}).get("decomposition", "")
    if decomposition:
        for comp in decomposition:
            if comp in IDC_CHARS or comp == '?' or not isinstance(comp, str) or len(comp) != 1:
                continue
            components.add(comp)
            components.update(get_all_components(comp, component_map, max_depth, depth + 1, seen.copy()))
    return components

def format_char_details(char, component_map):
    meta = component_map.get(char, {}).get("meta", {})
    return (
        f"{char} (Pinyin: {clean_field(meta.get('pinyin', '—'))}, "
        f"Strokes: {get_stroke_count(char, component_map) or 'unknown'}, "
        f"Radical: {clean_field(meta.get('radical', '—'))}, "
        f"Decomposition: {format_decomposition(char, component_map)}, "
        f"Definition: {clean_field(meta.get('definition', 'No definition available'))}, "
        f"Etymology: {get_etymology_text(meta)})"
    )

@st.cache_data
def get_filtered_components(component_map, stroke_count, radical, component_idc, _cache_key):
    return [
        comp for comp in component_map
        if isinstance(comp, str) and len(comp) == 1 and
        (stroke_count == 0 or get_stroke_count(comp, component_map) == stroke_count) and
        (radical == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("radical", "") == radical) and
        (component_idc == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("decomposition", "").startswith(component_idc))
    ]

# State Management
DEFAULT_SESSION_VALUES = {
    "stroke_count": 0,
    "radical": "No Filter",
    "selected_idc": "No Filter",
    "component_idc": "No Filter",
    "output_radical": "No Filter",
    "display_mode": "Single Character",
    "text_input_comp": "",
    "page": 1,
    "previous_selected_comp": "",
    "text_input_warning": None,
    "debug_info": "",
    "last_processed_input": "",
    "diagnostic_messages": []
}

def init_session_state():
    config_options = [
        {"selected_comp": "爫", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "心", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "⿱", "output_radical": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "⺌", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "3-Character Phrases"},
        {"selected_comp": "㐱", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "覀", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "豕", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "⿰", "output_radical": "No Filter", "display_mode": "3-Character Phrases"}
    ]
    selected_config = random.choice(config_options)
    defaults = DEFAULT_SESSION_VALUES.copy()
    defaults.update(selected_config)
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

def process_text_input(component_map):
    try:
        text_value = st.session_state.text_input_comp.strip()
        st.session_state.debug_info = f"Input received: '{text_value}'"
        
        if not text_value:
            st.session_state.text_input_warning = "Input cannot be empty."
            st.session_state.diagnostic_messages.append({"type": "warning", "message": "Input cannot be empty."})
            return
        
        if text_value == st.session_state.last_processed_input:
            st.session_state.debug_info += "; Input already processed, skipping"
            return
        
        if len(text_value) != 1:
            st.session_state.text_input_warning = "Please enter exactly one character."
            st.session_state.diagnostic_messages.append({"type": "warning", "message": "Please enter exactly one character."})
            st.session_state.last_processed_input = text_value
            return
        
        radicals = {c for c in component_map if component_map.get(c, {}).get("meta", {}).get("radical", "") == c}
        st.session_state.debug_info += f"; {len(radicals)} radicals in component_map"

        if text_value in component_map:
            st.session_state.debug_info += f"; Component '{text_value}' is valid"
            st.session_state.previous_selected_comp = st.session_state.selected_comp
            st.session_state.page = 1
            st.session_state.text_input_warning = None
            cache_key = f"{st.session_state.stroke_count}_{st.session_state.radical}_{st.session_state.component_idc}"
            filtered_components = get_filtered_components(
                component_map, 
                st.session_state.stroke_count, 
                st.session_state.radical, 
                st.session_state.component_idc, 
                cache_key
            )
            if text_value not in filtered_components:
                st.session_state.debug_info += f"; '{text_value}' not in filtered components, resetting filters"
                st.session_state.stroke_count = 0
                st.session_state.radical = "No Filter"
                st.session_state.component_idc = "No Filter"
            st.session_state.last_processed_input = text_value
        else:
            warning_msg = "Invalid character. Please enter a valid component."
            st.session_state.text_input_warning = warning_msg
            st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
            st.session_state.debug_info += f"; Invalid component '{text_value}'"
            st.session_state.last_processed_input = text_value
    except Exception as e:
        error_msg = f"Error processing input: {str(e)}"
        st.session_state.text_input_warning = error_msg
        st.session_state.diagnostic_messages.append({"type": "error", "message": error_msg})
        st.session_state.debug_info += f"; Error: {str(e)}"
        st.session_state.last_processed_input = text_value

def on_selectbox_change():
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.page = 1
    st.session_state.text_input_warning = None
    st.session_state.text_input_comp = st.session_state.selected_comp
    st.session_state.debug_info = f"Selectbox changed to '{st.session_state.selected_comp}'"

def on_output_char_select(component_map):
    selected_char = st.session_state.output_char_select
    if selected_char == "Select a character..." or selected_char not in component_map:
        if selected_char != "Select a character...":
            warning_msg = "Invalid character selected."
            st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
        st.session_state.output_char_select = "Select a character..."
        return
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.selected_comp = selected_char
    st.session_state.page = 1
    st.session_state.text_input_warning = None
    st.session_state.text_input_comp = selected_char
    st.session_state.debug_info = f"Output char selected: '{selected_char}'"

def on_reset_filters():
    st.session_state.stroke_count = 0
    st.session_state.radical = "No Filter"
    st.session_state.component_idc = "No Filter"
    st.session_state.selected_idc = "No Filter"
    st.session_state.output_radical = "No Filter"
    st.session_state.page = 1
    st.session_state.text_input_warning = None
    st.session_state.text_input_comp = ""
    st.session_state.debug_info = "Filters reset"

def is_reset_needed():
    return (
        st.session_state.stroke_count != 0 or
        st.session_state.radical != "No Filter" or
        st.session_state.component_idc != "No Filter" or
        st.session_state.selected_idc != "No Filter" or
        st.session_state.output_radical != "No Filter"
    )

# UI Rendering
def render_controls(component_map):
    try:
        with st.container():
            st.markdown("### Component Filters")
            st.caption("Filter components by stroke count, radical, or structure.")
            col1, col2, col3 = st.columns([0.4, 0.4, 0.4])

            with col1:
                stroke_counts = sorted(set(
                    sc for sc in (
                        get_stroke_count(comp, component_map) for comp in component_map
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
                cache_key = f"{st.session_state.stroke_count}_radical"
                pre_filtered_components = get_filtered_components(
                    component_map, 
                    st.session_state.stroke_count, 
                    "No Filter", 
                    "No Filter", 
                    cache_key
                )
                radicals = {"No Filter"} | {
                    component_map.get(c, {}).get("meta", {}).get("radical", "")
                    for c in pre_filtered_components
                    if component_map.get(c, {}).get("meta", {}).get("radical", "")
                }
                radical_options = ["No Filter"] + sorted(radicals - {"No Filter"})
                if st.session_state.radical not in radical_options:
                    st.session_state.radical = "No Filter"
                st.selectbox(
                    "Filter by Radical:",
                    options=radical_options,
                    index=radical_options.index(st.session_state.radical),
                    key="radical"
                )

            with col3:
                cache_key = f"{st.session_state.stroke_count}_{st.session_state.radical}_idc"
                pre_filtered_components = get_filtered_components(
                    component_map, 
                    st.session_state.stroke_count, 
                    st.session_state.radical, 
                    "No Filter", 
                    cache_key
                )
                component_idcs = {"No Filter"} | {
                    component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0]
                    for c in pre_filtered_components
                    if component_map.get(c, {}).get("meta", {}).get("decomposition", "") and component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0] in IDC_CHARS
                }
                component_idc_options = ["No Filter"] + sorted(component_idcs - {"No Filter"})
                if st.session_state.component_idc not in component_idc_options:
                    st.session_state.component_idc = "No Filter"
                st.selectbox(
                    "Filter by Structure IDC:",
                    options=component_idc_options,
                    format_func=lambda x: f"{x} ({IDC_DESCRIPTIONS.get(x, x)})" if x != "No Filter" else x,
                    index=component_idc_options.index(st.session_state.component_idc),
                    key="component_idc"
                )

        with st.container():
            st.markdown("### Select Input Component")
            st.caption("Choose or type a single character to explore its related characters.")
            col4, col5 = st.columns([1.5, 0.2])

            with col4:
                cache_key = f"{st.session_state.stroke_count}_{st.session_state.radical}_{st.session_state.component_idc}"
                filtered_components = get_filtered_components(
                    component_map, 
                    st.session_state.stroke_count, 
                    st.session_state.radical, 
                    st.session_state.component_idc, 
                    cache_key
                )
                selected_char_components = get_all_components(st.session_state.selected_comp, component_map, max_depth=5) if st.session_state.selected_comp else set()
                filtered_components.extend([comp for comp in selected_char_components if comp not in filtered_components and comp in component_map])
                if st.session_state.text_input_comp and st.session_state.text_input_comp in component_map and st.session_state.text_input_comp not in filtered_components:
                    filtered_components.append(st.session_state.text_input_comp)
                sorted_components = sorted(filtered_components, key=lambda c: get_stroke_count(c, component_map) or 0)
                
                if not sorted_components:
                    st.session_state.selected_comp = ""
                    st.session_state.text_input_comp = ""
                    warning_msg = "No components match the current filters. Please adjust the stroke count, radical, or IDC filters."
                    st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
                    st.warning(warning_msg)
                    return
                
                if st.session_state.selected_comp not in sorted_components:
                    st.session_state.selected_comp = sorted_components[0]
                    if not st.session_state.text_input_comp:
                        st.session_state.text_input_comp = sorted_components[0]
                    st.session_state.debug_info += f"; Reset selected_comp to '{sorted_components[0]}' due to filters"

                index = sorted_components.index(st.session_state.selected_comp) if st.session_state.selected_comp in sorted_components else 0
                st.selectbox(
                    "Select a component:",
                    options=sorted_components,
                    index=index,
                    format_func=lambda c: c if c == "Select a component..." else format_char_details(c, component_map),
                    key="selected_comp",
                    on_change=on_selectbox_change
                )

            with col5:
                if st.session_state.text_input_warning:
                    st.warning(st.session_state.text_input_warning)
                st.text_input(
                    "Or type:",
                    value=st.session_state.text_input_comp,
                    key="text_input_comp",
                    on_change=process_text_input,
                    args=(component_map,),
                    placeholder="Enter one Chinese character"
                )

        components.html("""
            <script>
                let debounceTimeout = null;
                document.addEventListener('paste', function(e) {
                    clearTimeout(debounceTimeout);
                    const text = (e.clipboardData || window.clipboardData).getData('text').trim();
                    const input = document.querySelector('input[data-testid="stTextInput"]');
                    if (input) {
                        input.value = text;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
            </script>
        """, height=0)

        with st.container():
            st.markdown("### Filter Output Characters")
            st.caption("Customize the output by character structure and display mode.")
            col6, col7, col8 = st.columns([0.33, 0.33, 0.34])
            with col6:
                idcs = {"No Filter"} | {
                    component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0]
                    for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
                    if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("decomposition", "") and component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0] in IDC_CHARS
                }
                idc_options = ["No Filter"] + sorted(idcs - {"No Filter"})
                if st.session_state.selected_idc not in idc_options:
                    st.session_state.selected_idc = "No Filter"
                st.selectbox(
                    "Result IDC:",
                    options=idc_options,
                    format_func=lambda x: f"{x} ({IDC_DESCRIPTIONS.get(x, x)})" if x != "No Filter" else x,
                    index=idc_options.index(st.session_state.selected_idc),
                    key="selected_idc"
                )
            with col7:
                output_radicals = {"No Filter"} | {
                    component_map.get(c, {}).get("meta", {}).get("radical", "")
                    for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
                    if isinstance(c, str) and len(c) == 1 and component_map.get(c, {}).get("meta", {}).get("radical", "")
                }
                output_radical_options = ["No Filter"] + sorted(output_radicals - {"No Filter"})
                if st.session_state.output_radical not in output_radical_options:
                    st.session_state.output_radical = "No Filter"
                st.selectbox(
                    "Result Radical:",
                    options=output_radical_options,
                    index=output_radical_options.index(st.session_state.output_radical),
                    key="output_radical"
                )
            with col8:
                st.radio("Output Type:", ["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"], key="display_mode")
            st.button("Reset Filters", on_click=on_reset_filters, disabled=not is_reset_needed())
    except Exception as e:
        st.error(f"Error rendering controls: {e}")
        st.session_state.diagnostic_messages.append({"type": "error", "message": f"Error rendering controls: {e}"})

def render_char_card(char, compounds, component_map):
    try:
        details = format_char_details(char, component_map).replace(f"{char} (", "").rstrip(")")
        st.markdown(f"""<div class='char-card'><h3 class='char-title'>{char}</h3><p class='details'>{details}</p>""", unsafe_allow_html=True)
        if compounds and st.session_state.display_mode != "Single Character":
            compounds_text = " ".join(sorted(compounds))
            st.markdown(f"""<div class='compounds-section'><p class='compounds-title'>{st.session_state.display_mode} for {char}:</p><p class='compounds-list'>{compounds_text}</p></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering character card for {char}: {e}")
        st.session_state.diagnostic_messages.append({"type": "error", "message": f"Error rendering character card for {char}: {e}"})

# Main Application
st.set_page_config(layout="wide")
st.markdown(f"<style>{CSS_STYLES}</style>", unsafe_allow_html=True)

component_map = load_component_map()
init_session_state()

def main():
    if not component_map:
        error_msg = "No data available. Please check the JSON file."
        st.error(error_msg)
        st.session_state.diagnostic_messages.append({"type": "error", "message": error_msg})
        return

    st.markdown("<h1>🧩 汉字 Radix</h1>", unsafe_allow_html=True)
    render_controls(component_map)

    active_comp = st.session_state.text_input_comp if st.session_state.text_input_comp in component_map else st.session_state.selected_comp
    if not active_comp:
        st.info("Please select or type a component to view results.")
        return

    try:
        details = format_char_details(active_comp, component_map).replace(f"{active_comp} (", "").rstrip(")")
        st.markdown(f"""<div class='selected-card'><h2 class='selected-char'>{active_comp}</h2><p class='details'>{details}</p></div>""", unsafe_allow_html=True)

        related = component_map.get(active_comp, {}).get("related_characters", [])
        filtered_chars = [
            c for c in related
            if isinstance(c, str) and len(c) == 1 and
            (st.session_state.selected_idc == "No Filter" or component_map.get(c, {}).get("meta", {}).get("decomposition", "").startswith(st.session_state.selected_idc)) and
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
            selected_char_components = get_all_components(active_comp, component_map, max_depth=5) if active_comp else set()
            output_options = sorted(filtered_chars, key=lambda c: get_stroke_count(c, component_map) or 0)
            output_options.extend([comp for comp in selected_char_components if comp not in output_options and comp in component_map])
            options = ["Select a character..."] + sorted(output_options, key=lambda c: get_stroke_count(c, component_map) or 0)
            if (st.session_state.previous_selected_comp and
                    st.session_state.previous_selected_comp != active_comp and
                    st.session_state.previous_selected_comp not in output_options and
                    st.session_state.previous_selected_comp in component_map):
                options.insert(1, st.session_state.previous_selected_comp)
            st.selectbox(
                "Select a character from the list below:",
                options=options,
                key="output_char_select",
                on_change=on_output_char_select,
                args=(component_map,),
                format_func=lambda c: c if c == "Select a character..." else format_char_details(c, component_map)
            )

        st.markdown(f"<h2 class='results-header'>🧬 Results for {active_comp} — {len(filtered_chars)} result(s)</h2>", unsafe_allow_html=True)
        for char in sorted(filtered_chars, key=lambda c: get_stroke_count(c, component_map) or 0):
            render_char_card(char, char_compounds.get(char, []), component_map)

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

        radicals = {c for c in component_map if component_map.get(c, {}).get("meta", {}).get("radical", "") == c}
        with st.expander("Debug Information (For Developers)", expanded=False):
            st.markdown("<div class='debug-section'>", unsafe_allow_html=True)
            st.write(f"Total components: {len(component_map)}, Radicals: {len(radicals)}")
            st.write(f"Current text_input_comp: '{st.session_state.text_input_comp}'")
            st.write(f"Current selected_comp: '{st.session_state.selected_comp}'")
            st.write(f"Current stroke_count: {st.session_state.stroke_count}")
            st.write(f"Current radical: {st.session_state.radical}")
            st.write(f"Current component_idc: {st.session_state.component_idc}")
            st.write(f"Debug log: {st.session_state.debug_info}")
            st.markdown("### Errors and Warnings")
            for msg in st.session_state.diagnostic_messages:
                class_name = 'error' if msg['type'] == 'error' else 'warning'
                st.markdown(f"<p class='diagnostic-message {class_name}'>{msg['type'].capitalize()}: {msg['message']}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error in main app: {e}")
        st.session_state.diagnostic_messages.append({"type": "error", "message": f"Error in main app: {e}"})

if __name__ == "__main__":
    main()
