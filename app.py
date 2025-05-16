import json
import random
import streamlit as st
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(layout="wide")

# Global IDC characters
IDC_CHARS = {'⿰', '⿱', '⿲', '⿳', '⿴', '⿵', '⿶', '⿷', '⿸', '⿹', '⿺', '⿻'}

# Dynamic CSS with font scaling
def apply_dynamic_css():
    """
    Applies dynamic CSS to the Streamlit app, allowing font scaling.
    Uses st.session_state to persist the font scale.
    """
    font_scale = st.session_state.get('font_scale', 1.0)  # Default font scale is 1.0
    css = f"""
    <style>
        .selected-card {{
            background-color: #e8f4f8;
            padding: 2px;
            border-radius: 8px;
            margin: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 5px;
            border-left: 4px solid #3498db;
        }}
        .selected-char {{ font-size: calc(2.2em * {font_scale}); color: #e74c3c; margin: 0; }}
        .details {{ font-size: calc(1.3em * {font_scale}); color: #34495e; margin: 0; }}
        .details strong {{ color: #2c3e50; }}
        .results-header {{ font-size: calc(1.4em * {font_scale}); color: #2c3e50; margin: 0; }}
        .char-card {{
            background-color: #ffffff;
            padding: 5px;
            border-radius: 6px;
            margin: 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .char-card:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .char-title {{ font-size: calc(1.3em * {font_scale}); color: #e74c3c; margin: 0; display: inline; }}
        .compounds-section {{
            background-color: #f1f8e9;
            padding: 2px;
            border-radius: 4px;
            margin: 0;
        }}
        .compounds-title {{ font-size: calc(1.0em * {font_scale}); color: #558b2f; margin: 0; }}
        .compounds-list {{ font-size: calc(0.9em * {font_scale}); color: #34495e; margin: 0; }}
        .input-section {{
            background-color: #e6f3ff;
            padding: 2px;
            border-radius: 8px;
            margin: 0;
            border: 1px solid #b3d4ff;
        }}
        .output-section {{
            background-color: #e6ffe6;
            padding: 2px;
            border-radius: 8px;
            margin: 0;
            border: 1px solid #b3ffb3;
        }}
        .filter-section {{
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 6px;
            margin: 0;
        }}
        .stButton button {{
            background-color: #3498db;
            color: white;
            border-radius: 4px;
            font-size: calc(0.8em * {font_scale});
        }}
        .stButton button:hover {{
            background-color: #2980b9;
        }}
        .debug-section {{
            background-color: #f5f5f5;
            padding: 2px;
            border-radius: 4px;
            margin: 0;
        }}
        .diagnostic-message.error {{ color: #c0392b; }}
        .diagnostic-message.warning {{ color: #e67e22; }}
        .diagnostic-message.info {{ color: #3498db; }}
        .stSelectbox, .stTextInput, .stRadio, .stSlider {{
            font-size: calc(0.8em * {font_scale});
        }}
        @media (max-width: 768px) {{
            .selected-card {{ flex-direction: column; align-items: flex-start; padding: 2px; }}
            .selected-char {{ font-size: calc(1.8em * {font_scale}); }}
            .details, .compounds-list {{ font-size: calc(0.9em * {font_scale}); line-height: 1.4; }}
            .results-header {{ font-size: calc(1.2em * {font_scale}); }}
            .char-card {{ padding: 2px; }}
            .char-title {{ font-size: calc(1.1em * {font_scale}); }}
            .compounds-title {{ font-size: calc(0.9em * {font_scale}); }}
            .input-section, .output-section, .filter-section {{ padding: 2px; }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load component map
@st.cache_data
def load_component_map():
    """
    Loads the component map from a JSON file.  Uses st.session_state for
    diagnostic messages, and handles potential file loading errors.  Also
    performs data validation.
    """
    diagnostic_messages = getattr(st.session_state, 'diagnostic_messages', [])
    try:
        with open("enhanced_component_map_with_etymology.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            diagnostic_messages.append({
                "type": "info",
                "message": f"Loaded component_map with {len(data)} entries"
            })
            # Validate the loaded data
            for char, entry in data.items():
                decomposition = entry.get("meta", {}).get("decomposition", "")
                if '?' in decomposition:
                    diagnostic_messages.append({
                        "type": "warning",
                        "message": f"Invalid component '?' in decomposition for {char}: {decomposition}"
                    })
                    entry["meta"]["decomposition"] = ""  # Correct the data
                related = entry.get("related_characters", [])
                if '?' in related:
                    diagnostic_messages.append({
                        "type": "warning",
                        "message": f"Invalid component '?' in related_characters for {char}"
                    })
                    entry["related_characters"] = [c for c in related if c != '?']  # Correct the data

            if hasattr(st.session_state, 'diagnostic_messages'):
                st.session_state.diagnostic_messages = diagnostic_messages
            return data
    except FileNotFoundError:
        error_msg = "Error: enhanced_component_map_with_etymology.json not found.  Please ensure the file is in the same directory."
        st.error(error_msg)
        diagnostic_messages.append({"type": "error", "message": error_msg})
        if hasattr(st.session_state, 'diagnostic_messages'):
            st.session_state.diagnostic_messages = diagnostic_messages
        return {}
    except json.JSONDecodeError as e:
        error_msg = f"Error: Invalid JSON format in enhanced_component_map_with_etymology.json: {e}"
        st.error(error_msg)
        diagnostic_messages.append({"type": "error", "message": error_msg})
        if hasattr(st.session_state, 'diagnostic_messages'):
            st.session_state.diagnostic_messages = diagnostic_messages
        return {}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        st.error(error_msg)
        diagnostic_messages.append({"type": "error", "message": error_msg})
        if hasattr(st.session_state, 'diagnostic_messages'):
            st.session_state.diagnostic_messages = diagnostic_messages
        return {}

# Utility functions
def clean_field(field):
    """
    Cleans a field from the component map data. Handles lists and None values.
    """
    return field[0] if isinstance(field, list) and field else field or "—"

def get_stroke_count(char):
    """
    Gets the stroke count of a character from the component map.
    Handles potential errors in the stroke count data.
    """
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
    """
    Formats the etymology text from the component map data.
    Handles cases where etymology data is missing or incomplete.
    """
    etymology = meta.get("etymology", {})
    hint = clean_field(etymology.get("hint", "No hint available"))
    details = clean_field(etymology.get("details", ""))
    return f"{hint}{'; Details: ' + details if details and details != '—' else ''}"

def format_decomposition(char):
    """
    Formats the decomposition string, handling missing or invalid decompositions.
    """
    decomposition = component_map.get(char, {}).get("meta", {}).get("decomposition", "")
    if not decomposition or '?' in decomposition:
        return "—"
    if decomposition[0] not in IDC_CHARS:
        return decomposition
    return decomposition

def get_components_for_display(char):
    """
    Gets the components for display, with a special case for '票'.
    """
    if char == '票':
        return {'覀', '示'}
    return set()

# Session state initialization
def init_session_state():
    """
    Initializes the session state with default values and handles configuration.
    Uses a more robust method to select a configuration and provides detailed
    diagnostic messages.
    """
    default_config = {
        "selected_comp": "心",
        "stroke_count": 0,
        "radical": "No Filter",
        "selected_idc": "No Filter",
        "component_idc": "No Filter",
        "output_radical": "No Filter",
        "display_mode": "Single Character"
    }

    config_options = [
        {"selected_comp": "爫", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "心", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "⿱", "output_radical": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "⺌", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "3-Character Phrases"},
        {"selected_comp": "㐱", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "Single Character"},
        {"selected_comp": "覀", "stroke_count": 0, "radical": "No Filter", "selected_idc": "No Filter", "component_idc": "No Filter", "output_radical": "No Filter", "display_mode": "2-Character Phrases"},
        {"selected_comp": "豕", "stroke_count": 0, "radical": "No Filter", "component_idc": "⿰", "output_radical": "No Filter", "display_mode": "3-Character Phrases"}
    ]

    if "diagnostic_messages" not in st.session_state:
        st.session_state.diagnostic_messages = []

    st.session_state.diagnostic_messages.append({
        "type": "info",
        "message": f"Available config_options: {config_options}"
    })

    required_keys = set(default_config.keys())
    valid_configs = [
        config for config in config_options
        if isinstance(config, dict) and required_keys.issubset(set(config.keys()))
    ]

    if not valid_configs:
        st.session_state.diagnostic_messages.append({
            "type": "error",
            "message": "No valid configurations found in config_options. Using default configuration."
        })
        selected_config = default_config
    else:
        selected_config = random.choice(valid_configs)

    st.session_state.diagnostic_messages.append({
        "type": "info",
        "message": f"Selected configuration: {selected_config}"
    })

    defaults = {
        "selected_comp": selected_config.get("selected_comp", default_config["selected_comp"]),
        "stroke_count": selected_config.get("stroke_count", default_config["stroke_count"]),
        "radical": selected_config.get("radical", default_config["radical"]),
        "display_mode": selected_config.get("display_mode", default_config["display_mode"]),
        "selected_idc": selected_config.get("selected_idc", default_config["selected_idc"]),
        "component_idc": selected_config.get("component_idc", default_config["component_idc"]),
        "output_radical": selected_config.get("output_radical", default_config["output_radical"]),
        "text_input_comp": "",
        "page": 1,
        "previous_selected_comp": selected_config.get("selected_comp", default_config["selected_comp"]),
        "text_input_warning": None,
        "debug_info": f"Initialized session state with config: {selected_config}",
        "last_processed_input": "",
        "diagnostic_messages": st.session_state.diagnostic_messages,
        "font_scale": 1.0,
        "output_selected_char": None
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

# Initialize session state before loading component map
init_session_state()

# Now load component map
component_map = load_component_map()

# Callback functions
def process_text_input(component_map):
    """
    Processes text input for component selection.  Handles input validation,
    updates session state, and displays appropriate messages.
    """
    try:
        text_value = st.session_state.text_input_comp.strip()
        st.session_state.debug_info = f"Input received: '{text_value}'"

        if text_value == st.session_state.last_processed_input:
            st.session_state.debug_info += "; Input already processed, skipping"
            return

        radicals = {c for c in component_map if component_map.get(c, {}).get("meta", {}).get("radical", "") == c}
        st.session_state.debug_info += f"; {len(radicals)} radicals in component_map"

        if len(text_value) != 1:
            warning_msg = "Please enter exactly one character."
            st.session_state.text_input_warning = warning_msg
            st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
            st.session_state.debug_info += "; Invalid length"
            st.session_state.text_input_comp = ""
            st.session_state.last_processed_input = text_value
            return
        if text_value in component_map:
            st.session_state.debug_info += f"; Component '{text_value}' is valid (Text input takes precedence)"
            st.session_state.previous_selected_comp = st.session_state.selected_comp
            st.session_state.selected_comp = text_value
            st.session_state.text_input_comp = text_value
            st.session_state.page = 1
            st.session_state.text_input_warning = None
            st.session_state.output_char_select = "Select a character..."
            st.session_state.output_selected_char = None
            st.session_state.stroke_count = 0
            st.session_state.radical = "No Filter"
            st.session_state.component_idc = "No Filter"
            st.session_state.selected_idc = "No Filter"
            st.session_state.output_radical = "No Filter"
            st.session_state.last_processed_input = text_value
        else:
            warning_msg = "Invalid character. Please enter a valid component."
            st.session_state.text_input_warning = warning_msg
            st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
            st.session_state.debug_info += f"; Invalid component '{text_value}'"
            st.session_state.text_input_comp = ""
            st.session_state.last_processed_input = text_value
    except Exception as e:
        error_msg = f"Error processing input: {str(e)}"
        st.session_state.text_input_warning = error_msg
        st.session_state.diagnostic_messages.append({"type": "error", "message": error_msg})
        st.session_state.debug_info += f"; Error: {str(e)}"
        st.session_state.text_input_comp = ""
        st.session_state.last_processed_input = text_value

def on_selectbox_change():
    """
    Handles changes in the component selection dropdown.  Updates session state
    and resets relevant output parameters.
    """
    st.session_state.previous_selected_comp = st.session_state.selected_comp
    st.session_state.page = 1
    st.session_state.text_input_warning = None
    st.session_state.text_input_comp = st.session_state.selected_comp
    st.session_state.output_char_select = "Select a character..."
    st.session_state.output_selected_char = None
    st.session_state.stroke_count = 0
    st.session_state.radical = "No Filter"
    st.session_state.component_idc = "No Filter"
    st.session_state.selected_idc = "No Filter"
    st.session_state.output_radical = "No Filter"
    st.session_state.debug_info = f"Selectbox changed to '{st.session_state.selected_comp}' (Component dropdown takes precedence)"

def on_output_char_select(component_map):
    """
    Handles selection of a character from the output dropdown.
    Updates session state and handles invalid selections.
    """
    selected_char = st.session_state.output_char_select
    if selected_char == "Select a character..." or selected_char not in component_map or selected_char == '?':
        if selected_char != "Select a character..." and selected_char != '?':
            warning_msg = "Invalid character selected."
            st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
        st.session_state.output_char_select = "Select a character..."
        st.session_state.output_selected_char = None
        st.session_state.debug_info = "Output char selection cleared"
        return
    st.session_state.output_selected_char = selected_char
    st.session_state.text_input_warning = None
    st.session_state.debug_info = f"Output char selected: '{selected_char}' (Displays only this char and components)"

def on_reset_input_filters():
    """
    Resets input filters to their default values.
    """
    st.session_state.stroke_count = 0
    st.session_state.radical = "No Filter"
    st.session_state.component_idc = "No Filter"
    st.session_state.text_input_comp = ""
    st.session_state.text_input_warning = None
    st.session_state.debug_info = "Input filters reset"

def on_reset_output_filters():
    """
    Resets output filters to their default values.
    """
    st.session_state.selected_idc = "No Filter"
    st.session_state.output_radical = "No Filter"
    st.session_state.display_mode = "Single Character"
    st.session_state.output_char_select = "Select a character..."
    st.session_state.output_selected_char = None
    st.session_state.debug_info = "Output filters reset"

def is_input_reset_needed():
    """
    Checks if the input filters need to be reset.
    """
    return (
        st.session_state.stroke_count != 0 or
        st.session_state.radical != "No Filter" or
        st.session_state.component_idc != "No Filter"
    )

def is_output_reset_needed():
    """
    Checks if the output filters need to be reset.
    """
    return (
        st.session_state.selected_idc != "No Filter" or
        st.session_state.output_radical != "No Filter" or
        st.session_state.display_mode != "Single Character"
    )

# Render input controls
def render_input_controls(component_map):
    """
    Renders the input controls section of the app, including dropdowns for
    filtering components by stroke count, radical, and IDC.
    """
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

    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("### Choose Input Component")
    st.caption("Select or type a single Chinese character to explore its related characters and compounds.")

    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    st.markdown("#### Component Filters")
    st.caption("Filter available components by stroke count, radical, or structure.")
    col1, col2, col3 = st.columns([0.4, 0.4, 0.4])

    with col1:
        stroke_counts = sorted(set(
            sc for sc in (
                get_stroke_count(comp) for comp in component_map
                if isinstance(comp, str) and len(comp) == 1 and comp != '?'
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
        pre_filtered_components = [
            comp for comp in component_map
            if isinstance(comp, str) and len(comp) == 1 and comp != '?' and
            (st.session_state.stroke_count == 0 or get_stroke_count(comp) == st.session_state.stroke_count)
        ]
        radicals = {"No Filter"} | {
            component_map.get(comp, {}).get("meta", {}).get("radical", "")
            for comp in pre_filtered_components
            if component_map.get(comp, {}).get("meta", {}).get("radical", "")
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
        pre_filtered_components = [
            comp for comp in component_map
            if isinstance(comp, str) and len(comp) == 1 and comp != '?' and
            (st.session_state.stroke_count == 0 or get_stroke_count(comp) == st.session_state.stroke_count) and
            (st.session_state.radical == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("radical", "") == st.session_state.radical)
        ]
        component_idcs = {"No Filter"} | {
            component_map.get(comp, {}).get("meta", {}).get("decomposition", "")[0]
            for comp in pre_filtered_components
            if component_map.get(comp, {}).get("meta", {}).get("decomposition", "") and component_map.get(comp, {}).get("meta", {}).get("decomposition", "")[0] in IDC_CHARS
        }
        component_idc_options = ["No Filter"] + sorted(component_idcs - {"No Filter"})
        if st.session_state.component_idc not in component_idc_options:
            st.session_state.component_idc = "No Filter"
        st.selectbox(
            "Filter by Structure IDC:",
            options=component_idc_options,
            format_func=lambda x: f"{x} ({idc_descriptions.get(x, x)})" if x != "No Filter" else x,
            index=component_idc_options.index(st.session_state.component_idc),
            key="component_idc"
        )

    st.button("Reset Input Filters", on_click=on_reset_input_filters, disabled=not is_input_reset_needed())
    st.markdown("</div>", unsafe_allow_html=True)

    col4, col5 = st.columns([1.5, 0.2])
    with col4:
        filtered_components = [
            comp for comp in component_map
            if isinstance(comp, str) and len(comp) == 1 and comp != '?' and
            (st.session_state.stroke_count == 0 or get_stroke_count(comp) == st.session_state.stroke_count) and
            (st.session_state.radical == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("radical", "") == st.session_state.radical) and
            (st.session_state.component_idc == "No Filter" or component_map.get(comp, {}).get("meta", {}).get("decomposition", "").startswith(st.session_state.component_idc))
        ]
        st.session_state.diagnostic_messages.append({
            "type": "info",
            "message": f"Filtered components: {len(filtered_components)} components"
        })

        sorted_components = sorted(filtered_components, key=lambda c: get_stroke_count(c) or 0)

        if not sorted_components:
            st.session_state.selected_comp = ""
            st.session_state.text_input_comp = ""
            warning_msg = "No components match the current filters. Please adjust the stroke count, radical, or IDC filters."
            st.session_state.diagnostic_messages.append({"type": "warning", "message": warning_msg})
            st.warning(warning_msg)
        else:
            if st.session_state.selected_comp not in sorted_components:
                st.session_state.selected_comp = sorted_components[0]
                st.session_state.text_input_comp = sorted_components[0]
                st.session_state.debug_info += f"; Reset selected_comp to '{sorted_components[0]}' due to filters"

            index = sorted_components.index(st.session_state.selected_comp) if st.session_state.selected_comp in sorted_components else 0
            st.selectbox(
                "Select a component:",
                options=sorted_components,
                index=index,
                format_func=lambda c: (
                    c if c == "Select a component..." else
                    f"{c} (Pinyin: {clean_field(component_map.get(c, {}).get('meta', {}).get('pinyin', '—'))}, "
                    f"Strokes: {get_stroke_count(c) or 'unknown'}, "
                    f"Radical: {clean_field(component_map.get(c, {}).get('meta', {}).get('radical', '—'))}, "
                    f"Decomposition: {format_decomposition(c)}, "
                    f"Definition: {clean_field(component_map.get(c, {}).get('meta', {}).get('definition', 'No definition available'))}, "
                    f"Etymology: {get_etymology_text(component_map.get(c, {}).get('meta', {}))})"
                ),
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
    st.markdown("</div>", unsafe_allow_html=True)

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

# Render output controls
def render_output_controls(component_map):
    """
    Renders the output controls section, including dropdowns for filtering
    output characters by IDC and radical, and a radio button for display mode.
    """
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

    st.markdown("<div class='output-section'>", unsafe_allow_html=True)
    st.markdown("### Select Output Character")
    st.caption("Choose a character from the results to view only that character and its components.")

    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    st.markdown("#### Output Filters")
    st.caption("Customize the output by character structure, radical, or display mode.")
    col6, col7, col8 = st.columns([0.33, 0.33, 0.34])

    with col6:
        if st.session_state.selected_comp and st.session_state.selected_comp in component_map:
            related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
            st.session_state.debug_info += f"; Related characters for {st.session_state.selected_comp}: {related}"
            idcs = {"No Filter"} | {
                component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0]
                for c in related
                if isinstance(c, str) and len(c) == 1 and c != '?' and component_map.get(c, {}).get("meta", {}).get("decomposition", "") and component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0] in IDC_CHARS
            }
            idc_options = ["No Filter"] + sorted(idcs - {"No Filter"})
            if st.session_state.selected_idc not in idc_options:
                st.session_state.selected_idc = "No Filter"
            st.selectbox(
                "Result IDC:",
                options=idc_options,
                format_func=lambda x: f"{x} ({idc_descriptions.get(x, x)})" if x != "No Filter" else x,
                index=idc_options.index(st.session_state.selected_idc),
                key="selected_idc"
            )
        else:
            st.selectbox("Result IDC:", ["No Filter"], key="selected_idc", disabled=True)

    with col7:
        if st.session_state.selected_comp and st.session_state.selected_comp in component_map:
            related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
            output_radicals = {"No Filter"} | {
                component_map.get(c, {}).get("meta", {}).get("radical", "")
                for c in related
                if isinstance(c, str) and len(c) == 1 and c != '?' and component_map.get(c, {}).get("meta", {}).get("radical", "")
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
        else:
            st.selectbox("Result Radical:", ["No Filter"], key="output_radical", disabled=True)

    with col8:
        st.radio("Output Type:", ["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"], key="display_mode")

    st.button("Reset Output Filters", on_click=on_reset_output_filters, disabled=not is_output_reset_needed())
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.selected_comp and st.session_state.selected_comp in component_map:
        related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
        if not related:
            st.warning("No related characters found for the selected input component. Please check the JSON data or select a different component.")
        filtered_chars = [
            c for c in related
            if isinstance(c, str) and len(c) == 1 and c != '?' and
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

        st.selectbox(
            "Select a character from the list below:",
            options=["Select a character..."] + (sorted([c for c in filtered_chars if c != '?'], key=lambda c: get_stroke_count(c) or 0) if filtered_chars else []),
            index=0,
            key="output_char_select",
            on_change=on_output_char_select,
            args=(component_map,),
            format_func=lambda c: (
                c if c == "Select a character..." else
                f"{c} (Pinyin: {clean_field(component_map.get(c, {}).get('meta', {}).get('pinyin', '—'))}, "
                f"Strokes: {get_stroke_count(c) or 'unknown'}, "
                f"Radical: {clean_field(component_map.get(c, {}).get('meta', {}).get('radical', '—'))}, "
                f"Decomposition: {format_decomposition(c)}, "
                f"Definition: {clean_field(component_map.get(c, {}).get('meta', {}).get('definition', 'No definition available'))}, "
                f"Etymology: {get_etymology_text(component_map.get(c, {}).get('meta', {}))})"
            )
        )
    else:
        st.warning("Please select a valid input component to enable output selection.")
    st.markdown("</div>", unsafe_allow_html=True)

# Render character card
def render_char_card(char, compounds):
    """
    Renders a character card with its details and compounds.
    """
    if char == '?' or char not in ['票', '覀', '示']:
        return
    meta = component_map.get(char, {}).get("meta", {})
    if not meta:
        return
    fields = {
        "Pinyin": clean_field(meta.get("pinyin", "—")),
        "Strokes": f"{get_stroke_count(char)} strokes" if get_stroke_count(char) is not None else "unknown strokes",
        "Radical": clean_field(meta.get("radical", "—")),
        "Decomposition": format_decomposition(char),
        "Definition": clean_field(meta.get("definition", "No definition available")),
        "Etymology": get_etymology_text(meta)
    }
    details = " ".join(f"<strong>{k}:</strong> {v}" for k, v in fields.items())
    st.markdown(f"""<div class='char-card'><h3 class='char-title'>{char}</h3><p class='details'>{details}</p>""", unsafe_allow_html=True)
    if compounds and st.session_state.display_mode != "Single Character":
        compounds_text = " ".join(sorted(compounds))
        st.markdown(f"""<div class='compounds-section'><p class='compounds-title'>{st.session_state.display_mode} for {char}:</p><p class='compounds-list'>{compounds_text}</p></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main function
def main():
    """
    Main function to run the Streamlit app.  Calls the other functions to
    render the UI and handle user interactions.
    """
    if not component_map:
        st.error("Failed to load component map. Please check the error messages above.")
        return

    apply_dynamic_css()

    render_input_controls(component_map)
    render_output_controls(component_map)

    # Display selected character
    if st.session_state.output_selected_char:
        selected_char = st.session_state.output_selected_char
        st.markdown(f"<h2 class='results-header'>Selected Character:</h2>", unsafe_allow_html=True)
        render_char_card(selected_char, [])  # Pass an empty list for compounds since we only want the single char

        st.markdown("<h2 class='results-header'>Decomposition</h2>", unsafe_allow_html=True)
        decomposition = format_decomposition(selected_char)
        if decomposition != "—":
            components_for_display = decomposition.replace('⿰', '').replace('⿱', '').replace('⿲', '').replace('⿳', '').replace('⿴', '').replace('⿵', '').replace('⿶', '').replace('⿷', '').replace('⿸', '').replace('⿹', '').replace('⿺', '').replace('⿻', '')
            cols = st.columns(len(components_for_display))
            for i, comp in enumerate(components_for_display):
                with cols[i]:
                    st.markdown(f"<div class='selected-card'><h3 class='selected-char'>{comp}</h3></div>", unsafe_allow_html=True)
        else:
            st.markdown("Decomposition: —", unsafe_allow_html=True)
    elif st.session_state.selected_comp:  # Only show results if a component is selected
        st.markdown(f"<h2 class='results-header'>Characters Containing Component '{st.session_state.selected_comp}':</h2>", unsafe_allow_html=True)
        related_chars = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
        filtered_chars = [
            c for c in related_chars
            if isinstance(c, str) and len(c) == 1 and c != '?' and
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
        if not filtered_chars:
            st.warning("No characters found matching the criteria.")
        else:
            cols = st.columns(min(len(filtered_chars), 5))  # Adjust the number 5 to fit your layout
            for i, char in enumerate(filtered_chars):
                with cols[i % len(cols)]:
                    render_char_card(char, char_compounds[char])

    # Display debug info
    if st.session_state.debug_info:
        st.markdown("<div class='debug-section'><h4>Debug Info:</h4>", unsafe_allow_html=True)
        st.write(st.session_state.debug_info)
        st.markdown("</div>", unsafe_allow_html=True)

    # Display diagnostic messages
    if st.session_state.diagnostic_messages:
        st.markdown("<h4>Diagnostic Messages:</h4>", unsafe_allow_html=True)
        for message in st.session_state.diagnostic_messages:
            message_type_class = f"diagnostic-message {message['type']}"
            st.markdown(f"<p class='{message_type_class}'>{message['message']}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
