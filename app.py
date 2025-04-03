import streamlit as st

# Устанавливаем некоторые настройки страницы (необязательно)
st.set_page_config(
    page_title="Прогнозирование ВРГН",
    layout="centered"
)

# 1. CSS для фона приложения
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

# --------------------------------------------------------------------------------
# 2. Функции для интерполяции и расчёта риска
# --------------------------------------------------------------------------------

def interpolate_clamped(value, min_val, max_val, risk_min, risk_max):
    """
    Линейно интерполирует риск между risk_min и risk_max
    в диапазоне [min_val, max_val].
    Если value < min_val -> возвращаем risk_min
    Если value > max_val -> возвращаем risk_max
    """
    if value <= min_val:
        return risk_min
    elif value >= max_val:
        return risk_max
    else:
        ratio = (value - min_val) / (max_val - min_val)
        return risk_min + ratio * (risk_max - risk_min)

def calculate_risk(region_toxins, tail_length, tail_dna, tail_moment, has_g_allele):
    """
    Расчёт риска (в долях, где 0.0015 = 0.15%) по заданным правилам:
      - Если region_toxins=False => риск=0.0015
      - Если region_toxins=True => для каждого параметра делаем 
          интерполяцию [ (min_val=..., max_val=...) -> (0.0015, 0.00365) ]
        и берём среднее.
      - Если has_g_allele=True => умножаем финальный риск на 3.2
    """
    if not region_toxins:
        # Регион без экотоксикантов
        final_risk = 0.0015
    else:
        # Регион с экотоксикантами => интерполяция
        r1 = interpolate_clamped(
            tail_length,
            min_val=106.974489,
            max_val=114.028956,
            risk_min=0.0015,
            risk_max=0.00365
        )
        r2 = interpolate_clamped(
            tail_dna,
            min_val=5.143913,
            max_val=6.662332,
            risk_min=0.0015,
            risk_max=0.00365
        )
        r3 = interpolate_clamped(
            tail_moment,
            min_val=550.333221,
            max_val=759.152807,
            risk_min=0.0015,
            risk_max=0.00365
        )
        # Среднее трёх
        final_risk = (r1 + r2 + r3) / 3.0
    
    # Генотип G-аллеля => умножаем на 3.2
    if has_g_allele:
        final_risk *= 3.2
    
    return final_risk

# --------------------------------------------------------------------------------
# 3. Интерфейс
# --------------------------------------------------------------------------------

# 3.1. Две колонки: слева — инструкция, справа — картинка
col_left, col_right = st.columns([0.7, 0.3])
st.title("Прогнозирование риска врождённой расщелины губы и нёба (ВРГН)")
with col_left:
    st.markdown(
        """
        ### Как заполнить форму:
        1. Отметьте галочкой, если регион находится под воздействием экотоксикантов.
        2. С помощью ползунков укажите значения, полученные в результате комет-анализа.
        3. Если у пациента выявлен G-аллель (rs1695) по доминантной модели, поставьте соответствующую галочку.
        4. Нажмите "Рассчитать риск" для получения результата.
        """
    )

with col_right:
    st.image("img.png", use_container_width=True)

# Ввод данных
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

has_g_allele = st.checkbox("Наличие G-аллеля (rs1695, доминантная модель)", value=False)

# Кнопка расчёта
if st.button("Рассчитать риск"):
    # Вычисляем риск в долях
    final_risk = calculate_risk(
        region_toxins=region_toxins,
        tail_length=tail_length_mean,
        tail_dna=tail_dna_percent_mean,
        tail_moment=tail_moment_mean,
        has_g_allele=has_g_allele
    )
    # Переводим в проценты
    risk_percent = final_risk * 100.0

    st.subheader(f"Результат: риск = {risk_percent:.4f}%")

    # Задаём теоретический минимум и максимум для шкалы
    # Мин: 0.15% (0.0015)
    # Макс: ~1.168% (0.00365*3.2) 
    min_risk_percent = 0.15
    max_risk_percent = 1.168

    # "Зажимаем" результат в диапазон [min_risk_percent, max_risk_percent]
    clamped_risk = max(min(risk_percent, max_risk_percent), min_risk_percent)
    fraction = (clamped_risk - min_risk_percent) / (max_risk_percent - min_risk_percent)

    bar_width = 300
    indicator_left = fraction * bar_width

    # Отрисовка цветной линейки
    st.markdown(
        f"""
        <div style="width:{bar_width}px; height:25px; background: linear-gradient(to right, green, red); 
                    position: relative; border-radius: 5px;">
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
