import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="Платформа аналитики трейд-маркетинга",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

if "mapped_stores" not in st.session_state:
    st.session_state.mapped_stores = {}

if "mapped_models" not in st.session_state:
    st.session_state.mapped_models = {}

if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

if "card_generated" not in st.session_state:
    st.session_state.card_generated = False

with st.sidebar:
    st.title("🏢 Аналитика ТМ")
    st.caption("Контур РФ • Сервер: Selectel RU-1 (152-ФЗ)")
    st.divider()

    st.subheader("👤 Профиль и права доступа")
    role = st.selectbox(
        "Активная роль (Я-6):",
        [
            "Администратор Заказчика (Полный доступ)",
            "Трейд-маркетинг (Загрузка и отчёты)",
            "Просмотр: Только Сеть 1 и 2",
            "Просмотр: Только Сеть 3 (Регион Центр)",
            "Отдел обучения (Модуль ИИ)"
        ]
    )

    st.divider()
    st.subheader("🔍 Сквозные фильтры (Я-18)")
    period = st.selectbox("Отчётный период:", ["Ноябрь 2026", "Октябрь 2026", "Январь 2026 (Архив)"])
    brand = st.radio("Бренд:", ["Все бренды", "Бренд А", "Бренд Б"], horizontal=True)
    merge_networks = st.toggle("Сети 1 и 2: Суммарно (Я-19)", value=True)
    
    st.info(f"📅 **Версия справочников (Я-15):**\nРасчёт ведётся строго по АП и кластерам, действовавшим на **{period}**.")

st.title("Платформа аналитики трейд-маркетинга и обучения")
st.caption(f"Текущая сессия: **{role}** | Период: **{period}**")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 1. Загрузка и разворот Excel",
    "🏪 2. Маппинг точек Сети 3 (П-6)",
    "🔧 3. Нормализация моделей (Б-3)",
    "📈 4. Светофор и Продажи с ПК",
    "🤖 5. ИИ-генератор карточек (О-1..О-6)"
])

with tab1:
    st.subheader("Загрузка исходных файлов сетей и агентства (без ручной подготовки)")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        uploaded_file = st.file_uploader(
            "Выберите файл выгрузки (поддерживаются все 9 форматов из Раздела 8 ТЗ):",
            type=["xlsx", "xls"]
        )
    with col_u2:
        st.markdown("**Тестовый прогон из архива:**")
        if st.button("⚡ Загрузить выгрузку Сети 3 (10 804 колонки)", use_container_width=True):
            with st.spinner("Потоковое чтение и разворот сводной таблицы..."):
                time.sleep(0.9)
                st.session_state.file_processed = True

    if uploaded_file is not None or st.session_state.file_processed:
        fname = uploaded_file.name if uploaded_file else "Выгрузка_Сеть3_Ноябрь_2026.xlsx"
        st.success(f"✅ Файл принят в обработку: **{fname}**")
        
        st.markdown("#### 🔍 Автоопределение метаданных (Требование Я-10):")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Тип документа", "Продажи и остатки (Сеть 3)")
        c2.metric("Структура", "Сводная (10 804 колонки)")
        c3.metric("Отчётный период", period)
        c4.metric("Валидных точек", "2 701 магазин")

        st.markdown("""
        * **Служебные колонки и пароли (Я-17):** Исключены из импорта.
        * **Склады и админобъекты (П-6):** Отфильтровано 42 технических объекта.
        * **Разворот в плоскую витрину (П-2):** Сформировано **92 410** записей `Точка × Товар`.
        """)
        
        if st.button("💾 Записать в БД (сформировать версию #2 отчёта)", type="primary"):
            st.toast("Данные сохранены в PostgreSQL! Версия #2 активна.", icon="✅")

with tab2:
    st.subheader("Связка магазинов Сети 3 со справочником (Требование П-6)")
    st.caption("Каскад точных правил автоматически связал 98.4% точек (354 из 360 точек АП). Неоднозначные названия требуют однократного подтверждения.")

    unmatched_stores = [
        {"raw": "ТЦ Мегаполис (г. Воронеж, Московский пр-т 129/1) НОВЫЙ", "candidates": ["VRN_014 | Воронеж, ТРЦ Московский Проспект", "VRN_002 | Воронеж, ТЦ Галерея Чижова"]},
        {"raw": "Екб Алатырь 2 этаж (техника)", "candidates": ["EKB_009 | Екатеринбург, ТРЦ Алатырь, ул. Малышева 5", "EKB_012 | Екатеринбург, ТЦ Гринвич"]},
        {"raw": "СПб ТРК Лето Пулковское ш. (склад+зал)", "candidates": ["SPB_031 | Санкт-Петербург, ТРК Лето, Пулковское ш. 25", "SPB_004 | Санкт-Петербург, ТК Невский Центр"]}
    ]

    for idx, item in enumerate(unmatched_stores):
        raw_name = item["raw"]
        if raw_name in st.session_state.mapped_stores:
            st.success(f"🔗 **{raw_name}** ➔ привязано к `{st.session_state.mapped_stores[raw_name]}` (Правило сохранено в справочнике)")
        else:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                col1.markdown(f"**Из выгрузки сети:**\n`{raw_name}`")
                selected = col2.selectbox("Эталон из справочника:", item["candidates"], key=f"store_sel_{idx}", label_visibility="collapsed")
                if col3.button("Подтвердить и запомнить", key=f"store_btn_{idx}", use_container_width=True):
                    st.session_state.mapped_stores[raw_name] = selected
                    st.rerun()
                  with tab3:
    st.subheader("Нормализация наименований моделей из отчёта агентства (Требование Б-3)")
    st.caption("Очистка регистра, пробелов, префикса бренда и типовых опечаток (5l / 5I / 51). Подтверждённые связки запоминаются автоматически.")

    dirty_models = [
        {"raw": "БРЕНД-А WMD-65l0 (опечатка l вместо 1)", "auto": "WMD-6510 (Стиральная машина)", "conf": "96%"},
        {"raw": "дух.шкаф EOB 945X нерж", "auto": "EOB-945X (Духовой шкаф)", "conf": "92%"},
        {"raw": "Холод. RNF-320W белый", "auto": "RNF-320W (Холодильник)", "conf": "89%"}
    ]

    for idx, m in enumerate(dirty_models):
        raw_m = m["raw"]
        if raw_m in st.session_state.mapped_models:
            st.info(f"✅ Словарь синонимов обновлён: `{raw_m}` ➔ **{st.session_state.mapped_models[raw_m]}**")
        else:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
                c1.markdown(f"**Вписано в отчёте агентства:**\n`{raw_m}`")
                c2.markdown(f"**Сопоставлено со справочником:**\n**{m['auto']}**")
                c3.metric("Совпадение", m["conf"])
                if c4.button("Запомнить", key=f"mod_btn_{idx}", use_container_width=True):
                    st.session_state.mapped_models[raw_m] = m["auto"]
                    st.rerun()

with tab4:
    st.subheader(f"Сводная аналитика за {period} • {brand}")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Покрытие АП (Бренд-зоны)", "94.2%", "+1.8% к пред. мес.")
    k2.metric("Пустые места (Дыры, Б-11)", "28 мест", "-5 мест")
    k3.metric("Модели EOL на полках (Б-12)", "7 шт.", "Требуется замена", delta_color="inverse")
    k4.metric("Прирост в точках с ПК (П-11)", "+34.5%", "Внутри кластера А")

    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 🚦 Сверка мест Бренд-зоны (Светофор, п. 5.3)")
        df_bz = pd.DataFrame([
            {"Точка": "MSK_102 (Авиапарк)", "Место": "Место 1 (Дух. шкаф)", "Модель факт": "EOB-945X", "Статус": "🟢 Верно"},
            {"Точка": "MSK_102 (Авиапарк)", "Место": "Место 2 (Вар. панель)", "Модель факт": "EHI-640B (Резерв)", "Статус": "🟢 Резерв"},
            {"Точка": "SPB_031 (ТРК Лето)", "Место": "Место 3 (Стир. маш.)", "Модель факт": "WMD-5000", "Статус": "🟡 Свой вариант"},
            {"Точка": "EKB_009 (Алатырь)", "Место": "Место 4 (Холодильник)", "Модель факт": "RNF-210S", "Статус": "🔴 EOL (Снята)"},
            {"Точка": "VRN_014 (Моск. пр-т)", "Место": "Место 5 (ПММ)", "Модель факт": "—", "Статус": "⚪ Дыра"}
        ])
        st.dataframe(df_bz, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("#### 📊 Кластерное сравнение: точки с ПК и без (П-11)")
        if "Только Сеть 3" in role:
            st.warning("🔒 Согласно правам вашей роли (Я-6), данные по Сети 1 и Сети 2 скрыты.")
            df_sales = pd.DataFrame([
                {"Сеть": "Сеть 3", "Кластер": "Кластер А (с ПК)", "Продажи, шт.": 4120, "Доля категории": "18.4%"},
                {"Сеть": "Сеть 3", "Кластер": "Кластер А (без ПК)", "Продажи, шт.": 2890, "Доля категории": "12.9%"},
            ])
        else:
            if merge_networks:
                df_sales = pd.DataFrame([
                    {"Сеть": "Сети 1 + 2 (Суммарно)", "Кластер": "Кластер А (с ПК)", "Продажи, шт.": 6450, "Доля категории": "21.2%"},
                    {"Сеть": "Сети 1 + 2 (Суммарно)", "Кластер": "Кластер А (без ПК)", "Продажи, шт.": 4310, "Доля категории": "14.5%"},
                    {"Сеть": "Сеть 3", "Кластер": "Кластер А (с ПК)", "Продажи, шт.": 4120, "Доля категории": "18.4%"},
                    {"Сеть": "Сеть 3", "Кластер": "Кластер А (без ПК)", "Продажи, шт.": 2890, "Доля категории": "12.9%"},
                ])
            else:
                df_sales = pd.DataFrame([
                    {"Сеть": "Сеть 1 (1P + 3P)", "Кластер": "Кластер А (с ПК)", "Продажи, шт.": 3900, "Доля категории": "22.0%"},
                    {"Сеть": "Сеть 2 (1P + 3P)", "Кластер": "Кластер А (с ПК)", "Продажи, шт.": 2550, "Доля категории": "20.1%"},
                    {"Сеть": "Сеть 3", "Кластер": "Кластер А (с ПК)", "Продажи, шт.": 4120, "Доля категории": "18.4%"},
                ])
        st.dataframe(df_sales, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("ИИ-агент подготовки обучающих карточек (Модуль обучения)")
    st.caption("Языковая модель: YandexGPT Pro (Контур РФ) • Строгий режим RAG: генерация только по фактуре из исходников Заказчика.")

    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        st.selectbox("Фирменный шаблон (О-1):", ["Карточка модели КБТ (156 фигур, без плейсхолдеров)"])
        st.text_input("Код модели из банка изображений (О-4):", value="EOB-945X")
        task_text = st.text_area(
            "Постановка задачи агенту (О-6):",
            value="Собери одностраничную карточку по духовому шкафу EOB-945X: выдели 3 главных преимущества (пиролиз, термощуп, доводчик двери) и сухие технические характеристики строго из приложенного PDF.",
            height=110
        )
        if st.button("✨ Сгенерировать карточку по шаблону", type="primary", use_container_width=True):
            with st.spinner("Извлечение фактуры из PDF и маппинг в фигуры PPTX..."):
                time.sleep(1.0)
                st.session_state.card_generated = True

    with col_ai2:
        if st.session_state.card_generated:
            with st.container(border=True):
                st.markdown("### 📄 Предпросмотр свёрстанной карточки: `EOB-945X`")
                st.success("✅ Проверка фактуры (О-3): 100% цифр подтверждено по исходному PDF.")
                st.markdown("""
                * **Заголовок (Фигура #12):** Духовой шкаф EOB-945X — идеальный контроль прожарки
                * **Блок УТП 1 (Фигура #45):** Пиролитическая очистка при 480 °C (сжигание загрязнений в пепел)
                * **Блок УТП 2 (Фигура #68):** Встроенный термощуп с автоотключением при достижении целевой температуры
                * **Характеристики (Фигура #114):** Объём 72 л • Класс энергопотребления A+ • 12 режимов нагрева
                """)
                b1, b2, b3 = st.columns(3)
                b1.button("📥 Скачать PPTX", use_container_width=True)
                b2.button("🖼️ Скачать JPG", use_container_width=True)
                b3.button("🌐 Скачать HTML (СДО)", use_container_width=True)
        else:
            st.info("👈 Задайте параметры слева и нажмите **«Сгенерировать карточку по шаблону»**, чтобы увидеть раскладку по фигурам PPTX и кнопки экспорта.")
          
