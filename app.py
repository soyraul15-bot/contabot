import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfkit
import telegram
from jinja2 import Template
from io import BytesIO

# Configuración de PDF (ajusta ruta si la cambiaste)
PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Users\Admin\Desktop\mitox\wkhtmltopdf\bin\wkhtmltopdf.exe")

st.title("ContaBot AI – Generador de Reporte Contable")

st.markdown("🧾 Agrega tus transacciones una por una. Al terminar, genera el reporte.")

# Crear entradas dinámicas
num_filas = st.number_input("¿Cuántas transacciones deseas ingresar?", min_value=1, max_value=50, step=1, value=5)

data = []
for i in range(num_filas):
    st.markdown(f"### Transacción {i+1}")
    fecha = st.date_input(f"📅 Fecha {i+1}", key=f"fecha_{i}")
    descripcion = st.text_input(f"📝 Descripción {i+1}", key=f"desc_{i}")
    monto = st.number_input(f"💰 Monto {i+1}", key=f"monto_{i}", format="%.2f")
    data.append({"fecha": fecha, "descripcion": descripcion, "monto": monto})

telegram_id = st.text_input("💬 Ingresa tu ID de Telegram (opcional para recibir el PDF):")
enviar_telegram = st.checkbox("¿Enviar el PDF por Telegram?")

if st.button("📊 Generar Reporte"):
    df = pd.DataFrame(data)

    # Clasificación automática
    def clasificar(descripcion):
        descripcion = str(descripcion).lower()
        if "salario" in descripcion or "venta" in descripcion:
            return "Ingreso"
        elif "supermercado" in descripcion or "uber" in descripcion or "netflix" in descripcion:
            return "Gasto"
        else:
            return "Otro"

    df["tipo"] = df["descripcion"].apply(clasificar)
    ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()
    gastos = df[df["tipo"] == "Gasto"]["monto"].sum()
    balance = ingresos + gastos

    # Mostrar tabla y resumen
    st.subheader("📊 Resumen")
    st.write(f"**Ingresos:** ${ingresos:.2f}")
    st.write(f"**Gastos:** ${-gastos:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")
    st.dataframe(df)

    # Gráfico
    st.subheader("📈 Gráfico")
    totales = df.groupby("tipo")["monto"].sum()
    fig, ax = plt.subplots()
    totales.plot(kind="bar", ax=ax)
    st.pyplot(fig)

    # HTML render
    with open("reporte_template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())
    html_render = template.render(
        ingresos=f"{ingresos:.2f}",
        gastos=f"{-gastos:.2f}",
        balance=f"{balance:.2f}",
        tabla=df.to_html(index=False)
    )

    with open("reporte_generado.html", "w", encoding="utf-8") as f:
        f.write(html_render)

    # Generar PDF
    pdfkit.from_file("reporte_generado.html", "reporte_final.pdf", configuration=PDF_CONFIG, options={"enable-local-file-access": ""})
    with open("reporte_final.pdf", "rb") as f:
        st.download_button("📥 Descargar PDF", f, file_name="reporte_final.pdf")

        # Enviar por Telegram
        if enviar_telegram and telegram_id.strip():
            bot = telegram.Bot(token="7080814201:AAFp_Nw4Jp2Wtc3zHgEiJH_ZYU6bX4oaDfQ")
            f.seek(0)
            bot.send_document(chat_id=telegram_id.strip(), document=f)
            st.success("📤 Reporte enviado por Telegram.")
