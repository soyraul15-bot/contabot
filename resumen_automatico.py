
def generar_resumen(df, ingresos, gastos, balance):
    resumen = []

    if balance > 0:
        resumen.append(f"✅ Tuviste un mes positivo con un balance neto de ${balance:.2f}.")
    elif balance < 0:
        resumen.append(f"⚠️ Tuviste un mes negativo con un balance neto de ${balance:.2f}.")
    else:
        resumen.append("🔄 Tuviste un balance neto de $0. No ganaste ni perdiste.")

    # Ingreso principal
    ingreso_principal = df[df["tipo"] == "Ingreso"]["descripcion"].mode()
    if not ingreso_principal.empty:
        resumen.append(f"💵 El ingreso más frecuente fue por '{ingreso_principal[0]}'.")

    # Gasto más alto
    df_gastos = df[df["tipo"] == "Gasto"]
    if not df_gastos.empty:
        mayor_gasto = df_gastos.loc[df_gastos["monto"].idxmin()]
        resumen.append(f"💸 El gasto más alto fue '{mayor_gasto['descripcion']}' por ${-mayor_gasto['monto']:.2f}.")

    # Categoría de gasto más común
    gasto_frecuente = df_gastos["descripcion"].mode()
    if not gasto_frecuente.empty:
        resumen.append(f"📌 El gasto más frecuente fue en '{gasto_frecuente[0]}'.")

    return " ".join(resumen)
