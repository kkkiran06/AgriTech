from flask import Blueprint, render_template, request
from app.database.db import get_db

soil_bp = Blueprint('soil', __name__)

# Standard NPK recommendations per acre for common crops (in kg/acre)
CROP_NPK_ACRE = {
    "Rice (Paddy)": {"N": 40.0, "P": 20.0, "K": 20.0},
    "Wheat": {"N": 48.0, "P": 24.0, "K": 16.0},
    "Cotton": {"N": 40.0, "P": 20.0, "K": 20.0},
    "Maize (Corn)": {"N": 48.0, "P": 24.0, "K": 16.0},
    "Sugarcane": {"N": 100.0, "P": 40.0, "K": 50.0},
    "Tomato": {"N": 40.0, "P": 24.0, "K": 24.0},
    "Potato": {"N": 60.0, "P": 40.0, "K": 40.0},
    "Groundnut": {"N": 10.0, "P": 20.0, "K": 20.0}
}

@soil_bp.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    soils = db.execute("SELECT * FROM fertilizer_soil ORDER BY id ASC").fetchall()
    
    # Fertilizer calculator handling
    calc_result = None
    selected_crop = "Wheat"
    acres = 1.0

    if request.method == 'POST':
        selected_crop = request.form.get('crop', 'Wheat')
        try:
            acres = max(0.1, float(request.form.get('acres', '1.0')))
        except ValueError:
            acres = 1.0

        base_npk = CROP_NPK_ACRE.get(selected_crop, {"N": 40.0, "P": 20.0, "K": 20.0})
        total_n = round(base_npk['N'] * acres, 1)
        total_p = round(base_npk['P'] * acres, 1)
        total_k = round(base_npk['K'] * acres, 1)

        # Commercial Fertilizer Bag Estimations (approx standard 45/50kg bags)
        # Urea (46% N) -> N / 0.46
        # DAP (18% N, 46% P) -> P / 0.46 gives DAP kg; remainder N is met by Urea
        dap_kg = round(total_p / 0.46, 1) if total_p > 0 else 0
        n_from_dap = dap_kg * 0.18
        remaining_n = max(0.0, total_n - n_from_dap)
        urea_kg = round(remaining_n / 0.46, 1)
        # MOP (Muriate of Potash 60% K) -> K / 0.60
        mop_kg = round(total_k / 0.60, 1) if total_k > 0 else 0

        calc_result = {
            "crop": selected_crop,
            "acres": acres,
            "total_n": total_n,
            "total_p": total_p,
            "total_k": total_k,
            "urea_bags": round(urea_kg / 45.0, 1), # 45kg standard bag
            "urea_kg": urea_kg,
            "dap_bags": round(dap_kg / 50.0, 1),  # 50kg standard bag
            "dap_kg": dap_kg,
            "mop_bags": round(mop_kg / 50.0, 1),  # 50kg standard bag
            "mop_kg": mop_kg,
            "organic_compost_tons": round(2.5 * acres, 1)
        }

    return render_template(
        'soil/index.html',
        soils=soils,
        crop_options=list(CROP_NPK_ACRE.keys()),
        calc_result=calc_result,
        selected_crop=selected_crop,
        acres=acres
    )
