
def generar_estado_resultados(df):
    ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()

    # Clasificación automática de gastos
    costos_operativos = df[df["descripcion"].str.lower().str.contains("supermercado|uber", na=False)]["monto"].sum()
    gastos_admin = df[df["descripcion"].str.lower().str.contains("netflix|oficina|admin", na=False)]["monto"].sum()

    utilidad = ingresos + costos_operativos + gastos_admin  # gastos y costos son negativos

    return {
        "ingresos": ingresos,
        "costos_operativos": costos_operativos,
        "gastos_admin": gastos_admin,
        "utilidad": utilidad
    }
