import streamlit as st

st.set_page_config(
    page_title="Прогнозирование ВРГН",
    layout="centered",
    initial_sidebar_state="auto"
)

# -----------------------------------------------
# 1. Функция линейной интерполяции (с "зажатием" за пределами)
# -----------------------------------------------
def interpolate_clamped(value, min_val, max_val, risk_min, risk_max):
    """
    Линейно интерполирует риск между risk_min и risk_max
    в диапазоне [min_val, max_val].
    Если value < min_val -> возвращаем risk_min,
    если value > max_val -> возвращаем risk_max.
    """
    if value <= min_val:
        return risk_min
    elif value >= max_val:
        return risk_max
    else:
        ratio = (value - min_val) / (max_val - min_val)
        return risk_min + ratio * (risk_max - risk_min)

# -----------------------------------------------
# 2. Основная функция для расчёта риска
# -----------------------------------------------
def calculate_risk(region_toxins, tail_length, tail_dna, tail_moment, has_g_allele):
    """
    Расчёт риска по описанной логике:
      - Если region_toxins = False => итоговый риск = 0.0015
      - Иначе берём среднее интерполированных рисков для каждого параметра.
      - Если has_g_allele = True => умножаем на 3.2
    Возвращаем риск в долях (например, 0.0015 = 0.15%).
    """
    if not region_toxins:
        # Регион без экотоксикантов => базовый риск (0.0015)
        final_risk = 0.0015
    else:
        # Регион с экотоксикантами => интерполяция для каждого параметра
        r1 = interpolate_clamped(tail_length,
                                 min_val=106.974489,
                                 max_val=114.028956,
                                 risk_min=0.0015,
                                 risk_max=0.00365)
        
        r2 = interpolate_clamped(tail_dna,
                                 min_val=5.143913,
                                 max_val=6.662332,
                                 risk_min=0.0015,
                                 risk_max=0.00365)
        
        r3 = interpolate_clamped(tail_moment,
                                 min_val=550.333221,
                                 max_val=759.152807,
                                 risk_min=0.0015,
                                 risk_max=0.00365)
        
        # Берём среднее как итог
        final_risk = (r1 + r2 + r3) / 3.0

    # Умножаем на 3.2 при наличии G-аллеля (доминантная модель)
    if has_g_allele:
        final_risk *= 3.2

    return final_risk

# -----------------------------------------------
# 3. Интерфейс Streamlit
# -----------------------------------------------
st.title("Прогнозирование риска врождённой расщелины губы и нёба (ВРГН)")

st.markdown(
    """
    **Как заполнить форму:**
    1. Отметьте галочкой, если регион находится под воздействием экотоксикантов.
    2. С помощью ползунков укажите значения, полученные в результате комет-анализа (длина хвоста, процент ДНК, момент хвоста).
    3. Если у пациента выявлен G-аллель (rs1695) по доминантной модели, поставьте соответствующую галочку.
    4. Нажмите "Рассчитать риск" для получения результата.
    """
)



# 3.1. Ввод данных пользователем
region_toxins = st.checkbox("Регион с экотоксикантами", value=False)

# Слайдеры
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

# 3.2. Кнопка расчёта
if st.button("Рассчитать риск"):
    # Вычисляем риск
    risk = calculate_risk(
        region_toxins=region_toxins,
        tail_length=tail_length_mean,
        tail_dna=tail_dna_percent_mean,
        tail_moment=tail_moment_mean,
        has_g_allele=has_g_allele
    )
    # Перевод в проценты
    risk_percent = risk * 100.0
    
    st.subheader(f"Результат: риск = {risk_percent:.4f}%")
    
    # -----------------------------------------------
    # 3.3. Отображение шкалы (от min до max)
    # -----------------------------------------------
    # Теоретический минимум (region=False, no G):  0.0015 -> 0.15%
    # Теоретический максимум (region=True, все параметры ~ max, G-аллель):  ~0.00365 * 3.2 = 0.01168 -> 1.168%
    
    min_risk_percent = 0.15
    max_risk_percent = 1.168
    
    # "Нормируем" текущий риск в диапазоне 0.15% - 1.168%
    # (Если вдруг риск_percent < 0.15, сделаем 0.15, если >1.168, то 1.168)
    clamped_risk = max(min(risk_percent, max_risk_percent), min_risk_percent)
    fraction = (clamped_risk - min_risk_percent) / (max_risk_percent - min_risk_percent)
    
    # Выводим красивую "прогресс-бар"-шкалу вручную с помощью HTML + CSS (градиент от зеленого к красному)
    # Можно, конечно, использовать и st.progress, но он голубой по умолчанию.
    # Для наглядности ниже – пример кастомной полосы.
    
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
