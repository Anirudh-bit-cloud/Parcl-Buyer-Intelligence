from pathlib import Path

# 1. Update model_service.py
ms_path = Path("e:/parcl-buyer-intelligence/apps/api/services/model_service.py")
ms_text = ms_path.read_text(encoding="utf-8")

target1 = """        input_df = pd.DataFrame([payload])
        if "satisfaction_score" not in input_df:
            input_df["satisfaction_score"] = 3
        if "is_multi_unit" not in input_df:
            input_df["is_multi_unit"] = bool(payload.get("n_units", 1) > 1)
        if "n_towers" not in input_df:
            input_df["n_towers"] = min(int(payload.get("n_units", 1)), 20)
        if "price_per_sqft" not in input_df:
            input_df["price_per_sqft"] = 300.0"""

repl1 = """        input_df = pd.DataFrame([payload])
        if "satisfaction_score" not in input_df:
            input_df["satisfaction_score"] = 3
        if "is_multi_unit" not in input_df:
            input_df["is_multi_unit"] = bool(payload.get("n_units", 1) > 1)
        if "n_towers" not in input_df:
            input_df["n_towers"] = min(int(payload.get("n_units", 1)), 4)
        if "price_per_sqft" not in input_df:
            input_df["price_per_sqft"] = 302.264583
        if "avg_floor_area" not in input_df:
            input_df["avg_floor_area"] = 1129.176667
        if "portfolio_towers_hhi" not in input_df:
            input_df["portfolio_towers_hhi"] = 0.25
        if "purchase_span_months" not in input_df:
            input_df["purchase_span_months"] = 13.0"""

assert target1 in ms_text, "target1 not found in model_service.py"
ms_text = ms_text.replace(target1, repl1, 1)
ms_path.write_text(ms_text, encoding="utf-8")
print("Updated model_service.py with cohort medians")

# 2. Update generate_samples.py
gs_path = Path("e:/parcl-buyer-intelligence/scripts/generate_samples.py")
gs_text = gs_path.read_text(encoding="utf-8")
gs_target = '"avg_floor_area": 1150.0,'
gs_repl = '"avg_floor_area": 1129.18,'
if gs_target in gs_text:
    gs_text = gs_text.replace(gs_target, gs_repl, 1)
    gs_path.write_text(gs_text, encoding="utf-8")
    print("Updated generate_samples.py with avg_floor_area: 1129.18")

# 3. Update test_golden_responses.py
gr_path = Path("e:/parcl-buyer-intelligence/apps/api/tests/test_golden_responses.py")
gr_text = gr_path.read_text(encoding="utf-8")
if gs_target in gr_text:
    gr_text = gr_text.replace(gs_target, gs_repl, 1)
    gr_path.write_text(gr_text, encoding="utf-8")
    print("Updated test_golden_responses.py with avg_floor_area: 1129.18")

# 4. Update test_predictions.py
tp_path = Path("e:/parcl-buyer-intelligence/apps/api/tests/test_predictions.py")
tp_text = tp_path.read_text(encoding="utf-8")
if gs_target in tp_text:
    tp_text = tp_text.replace(gs_target, gs_repl, 1)
    tp_path.write_text(tp_text, encoding="utf-8")
    print("Updated test_predictions.py with avg_floor_area: 1129.18")
