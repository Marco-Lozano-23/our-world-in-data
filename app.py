import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reporte Ejecutivo - Our World in Data", layout="wide")

st.title("Reporte Ejecutivo con Datos Públicos")
st.caption("Fuente: Our World in Data | Procesamiento: Python + Streamlit")

DATA_URL = "https://ourworldindata.org/grapher/life-expectancy.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df


try:
    df = load_data()
    st.success("Conexión realizada correctamente con el repositorio público.")

    # Identificación automática de la columna de valores
    fixed_cols = ["Entity", "Code", "Year"]
    value_col = [c for c in df.columns if c not in fixed_cols][0]

    # --- Barra lateral: selector de países ---
    countries = sorted(df["Entity"].unique())
    default_countries = [c for c in ["Mexico", "United States", "Spain"] if c in countries]

    selected_countries = st.sidebar.multiselect(
        "Selecciona países",
        options=countries,
        default=default_countries,
    )

    # --- Barra lateral: selector de periodo ---
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    default_start = max(min_year, max_year - 30)

    year_range = st.sidebar.slider(
        "Rango de años",
        min_value=min_year,
        max_value=max_year,
        value=(default_start, max_year),
    )

    # --- Filtrado ---
    filtered = df[
        (df["Entity"].isin(selected_countries))
        & (df["Year"] >= year_range[0])
        & (df["Year"] <= year_range[1])
    ].copy()

    # --- Indicadores principales ---
    st.header("Indicadores principales")

    if not filtered.empty:
        latest = (
            filtered.sort_values("Year")
            .groupby("Entity")
            .tail(1)
            .sort_values("Entity")
        )

        cols = st.columns(max(len(latest), 1))
        for col, (_, row) in zip(cols, latest.iterrows()):
            col.metric(label=row["Entity"], value=f"{row[value_col]:.1f} años")
    else:
        latest = pd.DataFrame()
        st.info("No existen datos para los filtros seleccionados.")

    # --- Evolución histórica ---
    st.header("Evolución histórica")

    if not filtered.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        for country in selected_countries:
            country_data = filtered[filtered["Entity"] == country]
            ax.plot(country_data["Year"], country_data[value_col], label=country)

        ax.set_xlabel("Año")
        ax.set_ylabel("Esperanza de vida")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    else:
        st.info("No existen datos para los filtros seleccionados.")

    # --- Tabla de datos ---
    st.header("Tabla de datos")
    st.dataframe(filtered, use_container_width=True)

    # --- Descarga ---
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar datos filtrados en CSV",
        data=csv_data,
        file_name="reporte_esperanza_vida.csv",
        mime="text/csv",
    )

    # --- Conclusión automática ---
    st.header("Conclusión automática")

    if not latest.empty:
        max_row = latest.loc[latest[value_col].idxmax()]
        min_row = latest.loc[latest[value_col].idxmin()]

        st.write(
            f"En el último año disponible dentro del rango seleccionado, "
            f"{max_row['Entity']} presenta el valor más alto "
            f"({max_row[value_col]:.1f} años), mientras que {min_row['Entity']} "
            f"registra {min_row[value_col]:.1f} años."
        )
    else:
        st.info("No existen datos para los filtros seleccionados.")

except Exception as e:
    st.error("No fue posible cargar o procesar la información.")
    st.exception(e)
