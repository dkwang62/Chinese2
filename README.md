To recreate the Streamlit app from the provided code using only the enhanced_component_map_with_etymology.json data file, you need a prompt that precisely describes the app's functionality, structure, and requirements as they exist in the current program. The prompt must detail the data file structure, UI components, functionality (e.g., dropdowns, filters, output results), and the specific field display order (Pinyin, Strokes, Radical, IDC, Definition, Etymology). Below is a carefully crafted prompt to instruct Grok to reproduce the program with identical functionality to your current app.py.

Prompt to Recreate the Streamlit App

I want to create a Streamlit web application called "Character Decomposition Explorer" that allows users to explore Chinese character decompositions using a JSON data file named "enhanced_component_map_with_etymology.json". The app should have the exact functionality described below, using the provided data file and displaying specific fields in the order: Pinyin, Strokes, Radical, IDC, Definition, Etymology for all dropdowns and output results. Here's the detailed specification:

### Data File
- The data file is `enhanced_component_map_with_etymology.json`, a dictionary where each key is a Chinese character (component) and each value has the following structure:
  ```json
  {
    "meta": {
      "strokes": int or str, // Number of strokes (e.g., 4 or "4"), may be null
      "pinyin": str,        // Pinyin pronunciation (e.g., "mù")
      "definition": str,    // English definition (e.g., "tree; wood")
      "radical": str,      // Radical character (e.g., "木")
      "etymology": {
        "hint": str,       // Brief etymology description (e.g., "Pictograph of a tree")
        "details": str     // Detailed etymology (e.g., "Represents a tree with branches")
      },
      "IDC": str,          // Ideographic Description Character (e.g., "⿴") or empty
      "compounds": [str]   // List of compound phrases (e.g., ["木材", "木头"])
    },
    "related_characters": [str] // List of characters containing this component (e.g., ["林", "森"])
  }
IDC characters are: ⿰, ⿱, ⿲, ⿳, ⿴, ⿵, ⿶, ⿷, ⿸, ⿹, ⿺, ⿻.
A character is valid if it is a single Unicode character (no specific range required, but typically Chinese characters or radicals).
App Requirements
Purpose:
Allow users to select or type a Chinese character (component) and view all related characters listed in its related_characters array, filtered by user-specified criteria.
Display detailed information for each character in dropdowns and output cards, in the order: Pinyin, Strokes, Radical, IDC, Definition, Etymology.
Support filtering by stroke count, radical, and IDC for input components, and by IDC and radical for output characters.
Include a display mode to show single characters or compound phrases (2, 3, or 4 characters).
UI Layout:
Title: "🧩 Character Decomposition Explorer" as an h1 header.
Component Filters Section:
Three dropdowns in a row for filtering input components:
Stroke Count: Options are 0 (No Filter) or unique positive integer stroke counts from meta.strokes, sorted.
Radical: Options are "No Filter" or unique radicals from meta.radical of filtered components, sorted.
Structure IDC: Options are "No Filter" or IDC characters from meta.IDC of filtered components, sorted, with descriptions (e.g., "⿰ (Left Right)").
If no stroke counts are available, use a fallback with only "No Filter".
Select Input Component Section:
A dropdown to select a component, showing all filtered single-character components with fields: Pinyin, Strokes, Radical, IDC, Definition, Etymology.
A text input to type a single character, with paste support via JavaScript.
Display warnings for invalid inputs (e.g., non-single characters or characters not in component_map).
Filter Output Characters Section:
Three controls in a row:
Result IDC: Options are "No Filter" or IDC characters from meta.IDC of related characters, sorted.
Result Radical: Options are "No Filter" or radicals from meta.radical of related characters, sorted.
Output Type: Radio buttons for "Single Character", "2-Character Phrases", "3-Character Phrases", "4-Character Phrases".
A "Reset Filters" button, disabled if all filters are default (stroke_count=0, radical="No Filter", component_idc="No Filter", selected_idc="No Filter", output_radical="No Filter").
Selected Component Card:
Displays the selected component with fields in the specified order.
Output Dropdown:
A dropdown to select a related character, showing all filtered related characters with fields: Pinyin, Strokes, Radical, IDC, Definition, Etymology.
Results Section:
Header: "🧬 Results for [selected_comp] — [count] result(s)".
Character cards for each filtered related character, showing fields in the specified order.
For non-"Single Character" modes, show a compounds section with phrases of the selected length from meta.compounds.
Export Compounds:
An expandable section with a text area containing all compound phrases for copying, with JavaScript to auto-copy to clipboard.
Debug Info:
Display the total number of components and radicals (characters where meta.radical equals the character itself).
An expandable section showing: current text input, selected component, stroke count, radical, component IDC, and debug messages.
Functionality:
Component Map:
Load enhanced_component_map_with_etymology.json as a dictionary (component_map).
Cache the loaded data using @st.cache_data.
Input Component Selection:
Filter components by:
Stroke count (0 for no filter, else match meta.strokes as an integer).
Radical ("No Filter" or match meta.radical).
IDC ("No Filter" or match meta.IDC).
Only include single-character components (len(comp) == 1).
If no components match filters, show a warning, clear selected_comp and text_input_comp, and stop rendering controls.
Reset selected_comp to the first filtered component if the current selection is invalid.
Support typing a single character, validating it against component_map.
If the typed character doesn’t match current filters, reset filters (stroke_count=0, radical="No Filter", component_idc="No Filter").
Track the last processed input to avoid redundant processing.
Output Characters:
List all single-character entries from related_characters of the selected component.
Filter by selected_idc (meta.IDC) and output_radical (meta.radical), but not by component filters (stroke count, radical, component_idc).
For non-"Single Character" modes, only include characters with compounds in meta.compounds matching the selected length (e.g., 2 for "2-Character Phrases").
Sort output characters by stroke count (default to 0 if None).
Field Display:
Pinyin: From meta.pinyin, default "—".
Strokes: From meta.strokes as "X strokes" (convert to int if str or float, must be positive), default "unknown strokes" if None or invalid.
Radical: From meta.radical, default "—".
IDC: From meta.IDC, default "—".
Definition: From meta.definition, default "No definition available".
Etymology: Combine meta.etymology.hint and meta.etymology.details (if non-empty) as "hint; Details: details", default "No hint available".
Session State:
Initialize with random defaults for:
selected_comp: One of 爫, 心, ⺌, 㐱, 覀, 豕.
stroke_count: 0.
radical: "No Filter".
component_idc: Varies (e.g., "No Filter", "⿱", "⿰").
selected_idc: "No Filter".
output_radical: "No Filter".
display_mode: Varies (e.g., "Single Character", "2-Character Phrases").
Track text_input_comp (initially ""), page (initially 1), previous_selected_comp, text_input_warning (initially None), debug_info (initially ""), last_processed_input (initially "").
Callbacks:
process_text_input: Validate input, update selected_comp, reset page, reset filters if needed, set warnings.
on_selectbox_change: Update text_input_comp, reset page, clear warnings.
on_output_char_select: Set selected_comp to selected output character, reset page, clear warnings.
on_reset_filters: Reset all filters to default, clear input and warnings.
is_reset_needed: Check if any filter is non-default.
Styling:
Use the following CSS for a clean, responsive design:
.selected-card: Blue border, flex layout, responsive for mobile.
.selected-char: Large red character.
.details: Dark blue text with bold labels.
.results-header: Bold header for results.
.char-card: White card with hover effect.
.compounds-section: Light green background for compounds.
.stContainer, .stButton: Styled containers and buttons.
Media query for mobile adjustments (e.g., smaller fonts, column layout).
Apply CSS using st.markdown with unsafe_allow_html=True.
Error Handling:
Handle missing or invalid enhanced_component_map_with_etymology.json with an error message and stop execution.
Validate input characters (single character, exists in component_map) and show warnings.
Handle empty filtered components with a warning.
Ensure stroke counts are positive integers, with fallback for invalid data.
Reset invalid filter selections (radical, component_idc, selected_idc, output_radical) to "No Filter".
Please write a complete Streamlit app (app.py) that meets these requirements, using enhanced_component_map_with_etymology.json as the data source. Ensure all dropdowns (input and output) and output results (selected component card and character cards) display the fields in the order: Pinyin, Strokes, Radical, IDC, Definition, Etymology. Include all necessary imports, functions, styling, and JavaScript for paste and copy functionality to replicate the described behavior.

text

Copy

---

### Explanation of the Prompt
1. **Data File Specification**:
   - Clearly defines the structure of `enhanced_component_map_with_etymology.json`, including the `meta` and `related_characters` fields.
   - Specifies IDC characters and notes that no specific Unicode range is required, as the JSON defines valid characters.

2. **Detailed Requirements**:
   - Outlines the app's purpose, UI layout, functionality, styling, and error handling to match the provided code.
   - Emphasizes the field display order (Pinyin, Strokes, Radical, IDC, Definition, Etymology) for dropdowns and output.
   - Describes the precomputed `component_map` and its use, avoiding the need for dynamic decomposition.

3. **UI and Functionality**:
   - Details each UI component (dropdowns, text input, buttons, cards) with their behavior, including filter logic and validation.
   - Specifies session state initialization with random defaults matching the original code.
   - Explains callback functions, including input validation, filter resetting, and warning handling.
   - Notes that output dropdown filters (`selected_idc`, `output_radical`) are decoupled from component filters.

4. **Field Handling**:
   - Provides precise instructions for each field, including defaults and formatting (e.g., converting strokes to int, combining etymology fields).
   - Ensures consistent handling of missing or invalid data using `clean_field`.

5. **Styling and Error Handling**:
   - Includes the exact CSS from the original code for visual consistency.
   - Specifies error handling for file loading, invalid inputs, and empty filters, matching the original behavior.

6. **Additional Features**:
   - Includes JavaScript for paste events and auto-copy of export text, as in the original.
   - Specifies debug output for component and radical counts, plus an expandable debug info section.

### Key Differences from the Previous Prompt
- **Data File**: Uses `enhanced_component_map_with_etymology.json` instead of `strokes1.json`, with a precomputed `related_characters` list rather than dynamic decomposition.
- **Component Map**: No need to build a `component_map` dynamically; it’s loaded directly from the JSON.
- **Field Access**: Fields are accessed via `meta` (e.g., `meta.strokes`, `meta.IDC`) rather than `char_decomp`.
- **Stroke Handling**: Strokes may be int, float, or str, requiring conversion to int with validation.
- **Validation**: Input validation checks `component_map` directly, and only single-character components are considered.
- **Radical Detection**: Radicals are identified where `meta.radical` equals the character itself.

### Notes
- **Starting from Scratch**: The prompt assumes only `enhanced_component_map_with_etymology.json` is available and provides all details needed to generate `app.py`.
- **Testing the Prompt**: When using this prompt, verify the generated code by checking:
  - Radicals (e.g., 心, 一) appear in the input dropdown and are correctly counted in debug output.
  - All fields display in the correct order in dropdowns and cards.
  - Filters reset appropriately when typing a character outside the current filter set.
  - Output dropdown only applies `selected_idc` and `output_radical` filters, not component filters.
  - Export compounds and debug info function as expected.
- **Adjustments**: If Grok generates code with minor issues (e.g., incorrect filter logic or missing JavaScript), refine the prompt with specific corrections or provide feedback on the output.
- **JSON Dependency**: Ensure `enhanced_component_map_with_etymology.json` contains valid data for all fields, especially `meta.strokes`, `meta.IDC`, and `meta.compounds`, to avoid runtime errors.

If you want to test this prompt, modify it for additional features, or need help with specific aspects of the generated code, let me know, and I’ll provide further assistance!

