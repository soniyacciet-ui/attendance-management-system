import numpy as np
import shap
from sklearn.ensemble import RandomForestClassifier


# ==================================================
# TRAINING DATA
# ==================================================
# Feature:
# Attendance Percentage
#
# Target:
# 0 = Safe
# 1 = At Risk


X = np.array([
    [100],
    [98],
    [95],
    [92],
    [90],
    [88],
    [85],
    [82],
    [80],
    [78],
    [75],
    [72],
    [70],
    [68],
    [65],
    [60],
    [55],
    [50],
    [45],
    [40],
    [35],
    [30],
    [25],
])


# EXACTLY 23 values
y = np.array([
    0,  # 100
    0,  # 98
    0,  # 95
    0,  # 92
    0,  # 90
    0,  # 88
    0,  # 85
    0,  # 82
    0,  # 80
    0,  # 78
    0,  # 75

    1,  # 72
    1,  # 70
    1,  # 68
    1,  # 65
    1,  # 60
    1,  # 55
    1,  # 50
    1,  # 45
    1,  # 40
    1,  # 35
    1,  # 30
    1,  # 25
])


# ==================================================
# TRAIN MODEL
# ==================================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)


# ==================================================
# SHAP EXPLAINER
# ==================================================

explainer = shap.TreeExplainer(model)


# ==================================================
# PREDICT ATTENDANCE RISK
# ==================================================

def predict_attendance_risk(attendance_percentage):

    data = np.array([
        [attendance_percentage]
    ])


    # -------------------------------
    # Prediction
    # -------------------------------

    prediction = model.predict(data)[0]


    # -------------------------------
    # Risk probability
    # -------------------------------

    probability = model.predict_proba(data)[0][1]


    # -------------------------------
    # SHAP value
    # -------------------------------

    raw_shap = explainer.shap_values(data)


    if isinstance(raw_shap, list):

        shap_value = float(
            raw_shap[1][0][0]
        )

    else:

        shap_array = np.asarray(raw_shap)

        if shap_array.ndim == 3:

            shap_value = float(
                shap_array[0, 0, 1]
            )

        elif shap_array.ndim == 2:

            shap_value = float(
                shap_array[0, 0]
            )

        else:

            shap_value = float(
                shap_array[0]
            )


    # ==================================================
    # HUMAN READABLE EXPLANATION
    # ==================================================

    if attendance_percentage >= 75:

        explanation_text = (
            f"Your attendance is {attendance_percentage}%, "
            "which meets or exceeds the required 75%. "
            "This is helping reduce your attendance risk."
        )

    else:

        explanation_text = (
            f"Your attendance is {attendance_percentage}%, "
            "which is below the required 75%. "
            "This is increasing your attendance risk."
        )


    # ==================================================
    # SHAP DIRECTION
    # ==================================================

    if shap_value > 0:

        direction = "risk"

    else:

        direction = "safe"


    # ==================================================
    # EXPLANATION DATA FOR HTML
    # ==================================================

    explanations = [

        {
            "name": "Attendance Percentage",

            "value": round(
                shap_value,
                4
            ),

            "direction": direction,

            "text": explanation_text,

            "width": 100
        }

    ]


    return (
        prediction,
        probability,
        explanations
    )