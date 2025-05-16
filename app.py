# ... (previous imports and functions remain unchanged until render_input_controls)

# Render input controls (updated)
def render_input_controls(component_map):
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

    with st.container():
        st.markdown("<div class='input-section'>", unsafe_allow_html=True)
        st.markdown("### Choose Input Component")
        st.caption("Select or type a single Chinese character to explore its related characters and compounds.")

        # Input filters
        with st.container():
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

        # Component selection
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

# Render output controls (updated)
def render_output_controls(component_map):
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

    with st.container():
        st.markdown("<div class='output-section'>", unsafe_allow_html=True)
        st.markdown("### Select Output Character")
        st.caption("Choose a character from the results to view only that character and its components.")

        # Output filters
        with st.container():
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("#### Output Filters")
            st.caption("Customize the output by character structure, radical, or display mode.")
            col6, col7, col8 = st.columns([0.33, 0.33, 0.34])

            with col6:
                if st.session_state.selected_comp and st.session_state.selected_comp in component_map:
                    idcs = {"No Filter"} | {
                        component_map.get(c, {}).get("meta", {}).get("decomposition", "")[0]
                        for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
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
                    st.write("Select an input component first.")

            with col7:
                if st.session_state.selected_comp and st.session_state.selected_comp in component_map:
                    output_radicals = {"No Filter"} | {
                        component_map.get(c, {}).get("meta", {}).get("radical", "")
                        for c in component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
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
                    st.write("Select an input component first.")

            with col8:
                st.radio("Output Type:", ["Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases"], key="display_mode")

            st.button("Reset Output Filters", on_click=on_reset_output_filters, disabled=not is_output_reset_needed())
            st.markdown("</div>", unsafe_allow_html=True)

        # Output character selection
        if st.session_state.selected_comp and st.session_state.selected_comp in component_map:
            related = component_map.get(st.session_state.selected_comp, {}).get("related_characters", [])
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

            if filtered_chars:
                selected_char_components = get_all_components(st.session_state.selected_comp, max_depth=5) if st.session_state.selected_comp else set()
                output_options = sorted([c for c in filtered_chars if c != '?'], key=lambda c: get_stroke_count(c) or 0)
                output_options.extend([comp for comp in selected_char_components if comp not in output_options and comp in component_map and comp != '?'])
                if (st.session_state.selected_comp and
                        st.session_state.selected_comp in component_map and
                        st.session_state.selected_comp not in output_options and
                        st.session_state.selected_comp != '?'):
                    output_options.append(st.session_state.selected_comp)
                if (st.session_state.previous_selected_comp and
                        st.session_state.previous_selected_comp != st.session_state.selected_comp and
                        st.session_state.previous_selected_comp not in output_options and
                        st.session_state.previous_selected_comp in component_map and
                        st.session_state.previous_selected_comp != '?'):
                    output_options.insert(0, st.session_state.previous_selected_comp)
                options = ["Select a character..."] + sorted(output_options, key=lambda c: get_stroke_count(c) or 0)
                index = options.index(st.session_state.output_char_select) if st.session_state.get('output_char_select') in options else 0
                st.selectbox(
                    "Select a character from the list below:",
                    options=options,
                    index=index,
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
                st.warning("No related characters match the current output filters.")
        else:
            st.warning("Please select a valid input component to enable output selection.")
        st.markdown("</div>", unsafe_allow_html=True)

# ... (rest of the code, including render_char_card, main, etc., remains unchanged)
