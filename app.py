import streamlit as st

# Устанавливаем фон приложения (цвет #b1d1de)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #b1d1de;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Прогнозирование риска врождённой расщелины губы и нёба (ВРГН)")

# Мини-инструкция:
st.markdown(
    """
    **Как заполнить форму:**
    1. Отметьте галочкой, если регион находится под воздействием экотоксикантов.
    2. С помощью ползунков укажите значения, полученные в результате комет-анализа.
    3. Если у пациента выявлен G-аллель (rs1695) по доминантной модели, поставьте соответствующую галочку.
    4. Нажмите "Рассчитать риск" для получения результата.
    ---
    """
)

# ------------------
# Входные данные
# ------------------
region_toxins = st.checkbox("Регион с экотоксикантами", value=False)

tail_length_mean = st.slider(
    "Длина хвоста кометы (Tail_Length_Mean)",
    min_value=100.0,
    max_value=200.0,
    value=110.0,
    step=0.1
)

tail_dna_percent_mean = st.slider(
    "Процент ДНК в хвосте (Tail_DNA_Percent_Mean)",
    min_value=5.0,
    max_value=8.0,
    value=6.0,
    step=0.01
)

tail_moment_mean = st.slider(
    "Момент хвоста (Tail_Moment_Mean)",
    min_value=500.0,
    max_value=1000.0,
    value=600.0,
    step=1.0
)

has_g_allele = st.checkbox("Наличие G-аллеля (доминантная модель) по rs1695 (GSTP1)", value=False)

# ------------------
# Кнопка расчёта
# ------------------
if st.button("Рассчитать риск"):
    # (Здесь впишите вашу функцию расчёта риска, например: calculate_risk(...))
    # Предположим, что у нас есть уже подсчитанный риск в процентах:
    risk_percent = 0.55  # <-- Этот риск вы получаете из своей функции

    st.subheader(f"Результат: риск = {risk_percent:.4f}%")

    # Определим теоретический минимум/максимум
    min_risk_percent = 0.15
    max_risk_percent = 1.168

    # "Зажмём" риск внутри [min_risk_percent, max_risk_percent]
    clamped_risk = max(min(risk_percent, max_risk_percent), min_risk_percent)
    fraction = (clamped_risk - min_risk_percent) / (max_risk_percent - min_risk_percent)

    # -------------------------
    # Две колонки: слева шкала, справа картинка
    # -------------------------
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        # Рисуем градиентную шкалу
        bar_width = 300  # px, ширина шкалы
        indicator_left = fraction * bar_width

        st.markdown(
            f"""
            <div style="width:{bar_width}px; height:25px; background: linear-gradient(to right, green, red); position: relative; border-radius: 5px;">
                <div style="
                    position: absolute; 
                    left: {indicator_left}px; 
                    top: 0; 
                    width: 2px; 
                    height: 25px; 
                    background-color: black;">
                </div>
            </div>
            <p style="margin-top: 5px;">
                <b>{risk_percent:.4f}%</b>
                (минимум: {min_risk_percent}% / максимум: {max_risk_percent}%)
            </p>
            """,
            unsafe_allow_html=True
        )

    with col2:
        # Отображаем картинку (img.png), которая должна лежать в той же папке
        st.image("img.png", use_column_width=True)
