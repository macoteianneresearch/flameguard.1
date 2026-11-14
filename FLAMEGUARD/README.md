# FLAMEGUARD — Input-driven real-time dashboard

## Run locally (Windows)
1. Extract this ZIP.
2. Open the extracted `FLAMEGUARD` folder.
3. In the folder address bar, type `cmd` and press Enter.
4. Run: `py -m pip install -r requirements.txt`
5. Run: `py app.py`
6. Open `http://127.0.0.1:8080` in your browser.

## How the five dashboard sections update
- Section 01: shows backend connection and whether current inputs are reaching the model.
- Section 02: input values are the data source. Changing a slider or selection recalculates the prediction immediately.
- Section 03: the selected spacecraft zone and its status reflect the latest prediction.
- Section 04: live charts append values derived from the current inputs while the stream is running.
- Section 05: hazard category and model indicators are recalculated from the same input values.

The calculation is deterministic: the same inputs produce the same outputs. Random values have been removed. This package does not read physical sensors by itself. To show actual real-world sensor measurements, a compatible sensor/device must send its readings to the API. The included calculations are educational estimates only, not validated fire-safety predictions, operational thresholds, or NASA-certified results.
