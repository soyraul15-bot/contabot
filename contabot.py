import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Template
import pdfkit
import telegram


# Cargar archivo
df = pd.read_csv("transacciones.csv")

# Clasificación
def clasificar(descripcion):
    descripcion = descripcion.lower()
    if "salario" in descripcion or "venta" in descripcion:
        return "Ingreso"
    elif "supermercado" in descripcion or "uber" in descripcion or "netflix" in descripcion:
        return "Gasto"
    else:
        return "Otro"

df["tipo"] = df["descripcion"].apply(clasificar)

# Resumen
ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()
gastos = df[df["tipo"] == "Gasto"]["monto"].sum()
balance = ingresos + gastos

# Gráfico de barras
totales = df.groupby("tipo")["monto"].sum()
totales.plot(kind="bar", title="Resumen Financiero")
plt.ylabel("Monto ($)")
plt.tight_layout()
plt.savefig("grafico.png")
plt.close()

# Crear tabla en HTML
tabla_html = df.to_html(index=False)

# Cargar plantilla
with open("reporte_template.html", "r", encoding="utf-8") as file:
    template = Template(file.read())

html_render = template.render(
    ingresos=f"{ingresos:.2f}",
    gastos=f"{-gastos:.2f}",
    balance=f"{balance:.2f}",
    tabla=tabla_html
)

# Guardar reporte
with open("reporte_generado.html", "w", encoding="utf-8") as f:
    f.write(html_render)

print("✅ Reporte generado: reporte_generado.html")

# Configura la ruta de wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=r"C:\Users\Admin\Desktop\mitox\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Genera el PDF desde el HTML
pdfkit.from_file(
    "reporte_generado.html",
    "reporte_final.pdf",
    configuration=config,
    options={"enable-local-file-access": ""}
)
print("📄 PDF generado: reporte_final.pdf")

# Datos de tu bot
bot_token = "7080814201:AAFp_Nw4Jp2Wtc3zHgEiJH_ZYU6bX4oaDfQ"
chat_id = "1573195190"  # entre comillas si lo copias como string

# Enviar el PDF por Telegram
bot = telegram.Bot(token=bot_token)
with open("reporte_final.pdf", "rb") as f:
    bot.send_document(chat_id=chat_id, document=f)

print("📤 Reporte enviado por Telegram")
