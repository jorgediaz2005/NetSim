"""Demostración de Machine Learning de NetSim (árbol de decisión sobre datos sintéticos).

Sin dependencias de la interfaz: devuelve un diccionario con el modelo y sus métricas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from netsim_core import PESO_GRADO, PESO_INTERMEDIACION, PESO_TIPO, UMBRAL_ALTA, UMBRAL_MEDIA


def entrenar_modelo() -> dict:
    """Entrena el árbol con datos sintéticos etiquetados con la regla de criticidad y lo evalúa."""
    rng = np.random.default_rng(42)
    n = 1800
    g_, i_, imp_ = rng.random(n), rng.random(n), rng.uniform(0.2, 1.0, n)
    s = PESO_GRADO * g_ + PESO_INTERMEDIACION * i_ + PESO_TIPO * imp_
    y = pd.Series(np.where(s < UMBRAL_MEDIA, "Baja", np.where(s < UMBRAL_ALTA, "Media", "Alta")))
    X = pd.DataFrame({"Centralidad de grado": g_, "Centralidad de intermediación": i_,
                      "Importancia del tipo": imp_})
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    modelo = DecisionTreeClassifier(max_depth=5, min_samples_leaf=8, random_state=42).fit(Xtr, ytr)
    pred = modelo.predict(Xte)
    clases = ["Baja", "Media", "Alta"]
    return {
        "modelo": modelo, "clases": clases, "acc": accuracy_score(yte, pred),
        "cm": confusion_matrix(yte, pred, labels=clases),
        "informe": classification_report(yte, pred, labels=clases, output_dict=True, zero_division=0),
        "imp": pd.DataFrame({"Variable": X.columns, "Importancia": modelo.feature_importances_})
        .sort_values("Importancia", ascending=False), "vars": list(X.columns),
    }
