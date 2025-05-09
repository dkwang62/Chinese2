
# Chinese Character Decomposition Explorer

This is a Streamlit web app for exploring the decomposition of Chinese characters, including their strokes, meanings, components, etymology hints, and related compounds.

## Features
- Select components and view related characters
- Filter by stroke range and IDC structure
- View Hanyu Pinyin, definitions, radicals, and etymology
- Auto-copy compound phrases for easy use

## How to Run

1. Upload this repo to [Streamlit Cloud](https://streamlit.io/cloud).
2. Ensure the following files are present in your repository:
   - `app.py` (your main script)
   - `enhanced_component_map_with_etymology.json` (data file)
   - `requirements.txt`

3. Streamlit will automatically detect `app.py` and start the app.

## Local Development

To run locally:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## File Summary

| File                                  | Purpose                            |
|---------------------------------------|------------------------------------|
| `app.py`                              | Main Streamlit app script          |
| `enhanced_component_map_with_etymology.json` | Preprocessed character data         |
| `requirements.txt`                    | Python package dependencies        |
| `README.md`                           | App description and instructions   |

## License
MIT
