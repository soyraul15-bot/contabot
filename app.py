
import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import telegram
import openai
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
from jinja2 import Template
import os
from resumen_automatico import generar_resumen
from estado_resultados import generar_estado_resultados

PDF_CONFIG = None  # wkhtmltopdf desactivado en Render

st.title("ContaBot AI – Reporte Contable Inteligente")

modo = st.radio("¿Cómo deseas ingresar tus transacciones?", ["Subir archivo CSV", "Llenar formulario manual"])

df = None

if modo == "Subir archivo CSV":
    archivo = st.file_uploader("📤 Sube tu archivo CSV", type=["csv"])
    if archivo:
        df = pd.read_csv(archivo)
elif modo == "Llenar formulario manual":
    filas = st.number_input("¿Cuántas transacciones deseas ingresar?", min_value=1, max_value=50, step=1, value=5)
    data = []
    for i in range(filas):
        st.markdown(f"### Transacción {i+1}")
        fecha = st.date_input(f"📅 Fecha {i+1}", key=f"fecha_{i}")
        descripcion = st.text_input(f"📝 Descripción {i+1}", key=f"desc_{i}")
        monto = st.number_input(f"💰 Monto {i+1}", key=f"monto_{i}", format="%.2f")
        data.append({"fecha": fecha, "descripcion": descripcion, "monto": monto})
    df = pd.DataFrame(data)

def generar_recomendacion_ai(df, ingresos, gastos, balance, resumen_texto):
    prompt = f"""
    Eres un asesor financiero. Resume y da consejos sobre este reporte:

    Ingresos: {ingresos}
    Gastos: {gastos}
    Balance: {balance}
    Detalle: {resumen_texto}

    Da consejos útiles y simples para mejorar las finanzas del usuario.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


if df is not None and not df.empty:
    def clasificar(desc):
        desc = str(desc).lower()
        if "salario" in desc or "venta" in desc:
            return "Ingreso"
        elif "supermercado" in desc or "uber" in desc or "netflix" in desc:
            return "Gasto"
        else:
            return "Otro"

    df["tipo"] = df["descripcion"].apply(clasificar)
    ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()
    gastos = df[df["tipo"] == "Gasto"]["monto"].sum()
    balance = ingresos + gastos

    st.subheader("📊 Resumen")
    st.write(f"**Ingresos:** ${ingresos:.2f}")
    st.write(f"**Gastos:** ${-gastos:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")
    st.dataframe(df)

    resumen_automatico = generar_resumen(df, ingresos, gastos, balance)
    estado = generar_estado_resultados(df)

    st.subheader("📈 Gráfico")
    totales = df.groupby("tipo")["monto"].sum()
    fig, ax = plt.subplots()
    totales.plot(kind="bar", ax=ax)
    st.pyplot(fig)

    st.subheader("🧠 Resumen Inteligente")
    st.info(resumen_automatico)

    st.subheader("📄 Estado de Resultados")
    st.code(f"""
Ingresos:               ${estado["ingresos"]:.2f}
Costos Operativos:      ${estado["costos_operativos"]:.2f}
Gastos Administrativos: ${estado["gastos_admin"]:.2f}
------------------------------------------
Utilidad Neta:          ${estado["utilidad"]:.2f}
""")

    try:
        with open("reporte_template.html", "r", encoding="utf-8") as f:
            template = Template(f.read())

        recomendaciones_ai = generar_recomendacion_ai(df, ingresos, gastos, balance, resumen_automatico)

        html_render = template.render(
            ingresos=f"{ingresos:.2f}",
            gastos=f"{-gastos:.2f}",
            balance=f"{balance:.2f}",
            tabla=df.to_html(index=False),
            resumen_automatico=resumen_automatico,
            recomendaciones_ai=recomendaciones_ai,
            estado_resultados=estado
        )

        with open("reporte_generado.html", "w", encoding="utf-8") as f:
            f.write(html_render)
    except Exception as e:
        st.error(f"⚠️ Error generando el HTML del reporte: {e}")
        html_render = None

    telegram_id = st.text_input("📨 Tu ID de Telegram (opcional)")
    enviar = st.checkbox("📤 Enviar PDF por Telegram")
    if enviar and telegram_id and st.button("Enviar ahora"):
        if html_render:
            bot = telegram.Bot(token=os.environ.get("BOT_TOKEN"))
            with open("reporte_generado.html", "rb") as f:
                f.seek(0)
                bot.send_document(chat_id=telegram_id.strip(), document=f)
                st.success("📤 PDF enviado por Telegram.")
        else:
            st.warning("⚠️ No se generó el archivo PDF porque hubo un error en el HTML.")
