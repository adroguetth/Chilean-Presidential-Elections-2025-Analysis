"""
Translations
============================================================================
Single source of truth for bilingual UI text (ES/EN). This module contains
only the `LANG` dictionary, which maps language codes to flat dictionaries
of key-value strings.

Keys are grouped by view/component with comments. Proper names (candidates,
regions, parties, communes) are not translated: they are proper nouns and
are kept as-is. Only UI labels and analysis text are translated.

Texts with embedded HTML are kept complete (not split), and dynamic comments
from `_comment_for_r()` are hardcoded in Spanish inside the views (they are
not in this dictionary, see TECHNICAL DEBT in `views/second_round/panorama.py`
and `views/first_round/panorama.py`).

Features
--------
- Bilingual dictionary (`LANG`) with `ES` and `EN` keys.
- Grouped by view/component (app, pages, views, components).
- Placeholders use `.format()` (e.g. "{pct}% of total").
- Dynamic comments excluded (see TECHNICAL DEBT).

Dependencies
------------
- Internal: none.
- External: none.
- Downstream: app.py, components/layout.py, components/charts.py,
  pages/*.py, views/first_round/*.py, views/second_round/*.py.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

LANG = {
    "ES": {
        # ====================================================================
        # APP / HEADER
        # ====================================================================
        "country": "República de Chile",
        "app_title": "Elecciones Presidenciales 2025",
        "page_title": "Elecciones Presidenciales 2025",
        "app_subtitle": "Resultados nacionales",
        "language": "Idioma",
        "error_importing_page": "Error al importar la página",
        "error": "Error al cargar los datos",
        "no_data": "No hay datos disponibles",
        "loading": "Cargando datos...",

        # ====================================================================
        # NAVEGACIÓN PRINCIPAL
        # ====================================================================
        "summary": "Resumen",
        "first_round": "Primera Vuelta",
        "second_round": "Segunda Vuelta",
        "territorial_explorer": "Explorador Territorial",
        "panorama": "Panorama",
        "historical": "Histórico",
        "historical_first_round": "Histórico Primera Vuelta",

        # ====================================================================
        # PAGES/SUMMARY.PY — Resumen Ejecutivo
        # ====================================================================
        "summary_title": "Resumen Ejecutivo",

        # Títulos de vista
        "summary_sr_view_title": "Segunda Vuelta 2025",
        "summary_sr_view_subtitle": "Balotaje Kast vs Jara. Resultados finales.",
        "summary_fr_view_title": "Primera Vuelta 2025",
        "summary_fr_view_subtitle": "8 candidatos. Resultados de la primera vuelta.",

        # KPIs
        "summary_kpi_casted": "Votos emitidos",
        "summary_kpi_valid": "Votos válidos",
        "summary_kpi_null": "Votos nulos",
        "summary_kpi_blank": "Votos en blanco",
        "summary_kpi_pct_padron": "{pct}% del padrón electoral",
        "summary_kpi_pct_total": "{pct}% del total",
        "summary_kpi_diff_vs_fr": "{pp} pp vs 1ª vuelta",

        # Bloque ganador
        "summary_winner_label": "GANADOR · SEGUNDA VUELTA 2025",
        "summary_margin_label": "Margen",
        "summary_margin_votes": "+{n} votos",
        "summary_bar_midlabel": "50%",
        "summary_votes_unit": "{n} votos",

        # Tabla de candidatos
        "summary_table_no_data": "No hay datos disponibles",

        # Footer
        "summary_footer_data_source": "Datos extraídos de Servicio Electoral de Chile (Servel)",
        "summary_footer_data_source_note": "Escrutinio definitivo · Actualizado: 18 de diciembre 2025",

        # ====================================================================
        # PAGES/FIRST_ROUND.PY — Orquestador
        # ====================================================================
        "fr_orch_fallback_summary": "Resumen de Primera Vuelta no disponible.",
        "fr_orch_fallback_territorial": "Explorador Territorial no disponible.",
        "fr_orch_fallback_panorama": "Panorama en construcción. Disponible en el próximo bloque.",
        "fr_orch_fallback_historical": "Histórico Primera Vuelta en construcción. Disponible en el próximo bloque.",
        "fr_orch_fallback_modulo": "Módulo no disponible: {err}",

        # ====================================================================
        # PAGES/SECOND_ROUND.PY — Orquestador
        # ====================================================================
        "sr_orch_tab_panorama": "Panorama general",
        "sr_orch_tab_jara": "Candidata Jara",
        "sr_orch_tab_kast": "Candidato Kast",
        "sr_orch_fallback_summary": "Resumen de Segunda Vuelta no disponible.",
        "sr_orch_fallback_territorial": "Explorador Territorial no disponible.",
        "sr_orch_fallback_panorama": "Panorama general en construcción.",
        "sr_orch_fallback_jara": "Análisis de Jara en construcción.",
        "sr_orch_fallback_kast": "Análisis de Kast en construcción.",
        "sr_orch_fallback_historical": "Histórico de Segunda Vuelta en construcción.",

        # ====================================================================
        # VIEWS/FIRST_ROUND/SUMMARY.PY
        # ====================================================================
        # Secciones
        "fr_summary_section_communes_won": "Comunas ganadas por candidato",
        "fr_summary_section_bastions": "Top 5 comunas por candidato (Bastiones electorales)",
        "fr_summary_section_macrozone": "Resultados por macrozona",

        # KPIs
        "fr_summary_kpi_inscritos": "Inscritos",
        "fr_summary_kpi_obligatorio": "Voto obligatorio",
        "fr_summary_kpi_casted": "Votos emitidos",
        "fr_summary_kpi_valid": "Votos válidos",
        "fr_summary_kpi_null": "Votos nulos",
        "fr_summary_kpi_blank": "Votos en blanco",
        "fr_summary_kpi_candidates": "Candidatos",
        "fr_summary_kpi_pct_padron": "{pct}% del padrón",
        "fr_summary_kpi_pct_total": "{pct}% del total",
        "fr_summary_kpi_over_10": "{n} con >10%",

        # Tablas
        "fr_summary_table_hash": "#",
        "fr_summary_table_commune": "Comuna",
        "fr_summary_table_region": "Región",
        "fr_summary_table_macrozone": "Macrozona",
        "fr_summary_table_jara_pct": "Jara %",
        "fr_summary_table_kast_pct": "Kast %",
        "fr_summary_table_parisi_pct": "Parisi %",
        "fr_summary_table_null_pct": "% Nulo",
        "fr_summary_table_winner": "Ganador",
        "fr_summary_table_distribution": "Distribución",
        "fr_summary_no_data_bastions": "No hay datos",
        "fr_summary_no_data_macrozone": "No hay datos para macrozona",

        # ====================================================================
        # VIEWS/FIRST_ROUND/PANORAMA.PY
        # ====================================================================
        # Vista
        "fr_pano_view_title": "Panorama",
        "fr_pano_view_subtitle": "Cada sección es desplegable.",

        # Expanders
        "fr_pano_exp_nulos": "Análisis de nulos",
        "fr_pano_exp_blancos": "Análisis de blancos",
        "fr_pano_exp_resultados": "Resultados nacionales",
        "fr_pano_exp_top_comunas": "Top comunas por candidato",
        "fr_pano_exp_comunas_ganadas": "Comunas ganadas",
        "fr_pano_exp_ganadores_regionales": "Ganadores regionales",
        "fr_pano_exp_capitales": "Voto en capitales regionales",
        "fr_pano_exp_tamano_comuna": "Voto según tamaño de comuna",
        "fr_pano_exp_recuperables": "Segunda vuelta: comunas recuperables",
        "fr_pano_exp_antisistema": "Análisis voto antisistema: Franco Parisi",
        "fr_pano_exp_kaiser": "Kaiser: la nueva derecha libertaria",

        # Títulos de sección
        "fr_pano_section_participacion": "Participación nacional",
        "fr_pano_section_reg_nulos_abs": "Regiones con más votos nulos (absoluto)",
        "fr_pano_section_com_nulos_abs": "Comunas con más votos nulos (absoluto)",
        "fr_pano_section_com_nulos_rel": "Comunas con mayor % de votos nulos",
        "fr_pano_section_reg_blancos_abs": "Regiones con más votos blancos (absoluto)",
        "fr_pano_section_com_blancos_abs": "Comunas con más votos blancos (absoluto)",
        "fr_pano_section_com_blancos_rel": "Comunas con mayor % de votos blancos",
        "fr_pano_section_bloques": "Análisis Estratégico por Bloques Ideológicos",
        "fr_pano_section_comunas_macro": "Comunas ganadas por macrozona",
        "fr_pano_section_dist_macro": "Distribución por macrozona",
        "fr_pano_section_parisi_top": "Comunas con mayor % de voto a Parisi",
        "fr_pano_section_parisi_bottom": "Comunas con menor % de voto a Parisi",
        "fr_pano_section_kaiser_macro": "Distribución territorial por macrozona",
        "fr_pano_section_kaiser_top": "Top 10 comunas donde Kaiser fue más fuerte",

        # Subtítulos
        "fr_pano_sub_top_comunas": "Comunas con mayor porcentaje de voto para cada candidato (filtro: al menos 300 votos emitidos). La columna RESULTADO indica si el candidato ganó en esa comuna.",
        "fr_pano_sub_comunas_ganadas": "Distribución del total de comunas del país según el candidato ganador en cada una (346 comunas).",
        "fr_pano_sub_ganadores_regionales": "Ganador de cada región, segundo lugar y brecha entre ambos en puntos porcentuales.",
        "fr_pano_sub_capitales": "Ganador de cada capital regional, segundo lugar y brecha entre ambos en puntos porcentuales.",
        "fr_pano_sub_tamano_comuna": "Distribución del voto entre los 5 candidatos principales según el tamaño poblacional de la comuna. Cada barra representa un tramo de población; los segmentos son el % de cada candidato sobre votos válidos del tramo.",
        "fr_pano_sub_recuperables": "Comunas donde Jara o Kast perdieron por menos de 1.000 votos en primera vuelta y que, de cara a la segunda vuelta, son los territorios más disputables. Eje X: margen a revertir. Eje Y: tamaño de la comuna (votos emitidos). Las comunas en la esquina superior izquierda son las más atractivas para invertir esfuerzo de campaña.",
        "fr_pano_sub_antisistema": "Distribución del voto a Franco Parisi por rango de intensidad (% sobre votos válidos de cada comuna). El análisis muestra el gradiente territorial del voto antisistema: concentrado en el Norte Grande, con presencia decreciente hacia el sur.",
        "fr_pano_sub_kaiser": "Johannes Kaiser es la irrupción de 2025. Sin equivalente en la elección anterior, su candidatura ocupó el espacio de la nueva derecha libertaria y se posicionó como la cuarta fuerza nacional.",
        "fr_pano_sub_kaiser_comp": "Comparación con los otros dos candidatos de la derecha (Kast y Matthei) por macrozona. Permite ver si Kaiser compite por el mismo electorado o si ocupa un espacio territorial propio.",

        # KPIs
        "fr_pano_kpi_total_emitidos": "Total emitidos",
        "fr_pano_kpi_nulos_blancos": "Nulos+Blancos: {pct}%",
        "fr_pano_kpi_validos": "Votos válidos",
        "fr_pano_kpi_nulos": "Votos nulos",
        "fr_pano_kpi_blancos": "Votos blancos",
        "fr_pano_kpi_pct_total": "{pct}% del total",

        # Bloques ideológicos
        "fr_pano_bloques_izq": "Izquierda",
        "fr_pano_bloques_antisistema": "Antisistema",
        "fr_pano_bloques_der": "Derecha",
        "fr_pano_bloques_izq_legend": "Izquierda (Artés, Jara, ME-O)",
        "fr_pano_bloques_antisistema_legend": "Antisistema (Parisi, Mayne-Nicholls)",
        "fr_pano_bloques_der_legend": "Derecha (Kast, Kaiser, Matthei)",
        "fr_pano_bloques_votos": "{n} votos",
        "fr_pano_bloque_izq_caract": "Liderazgo claro, base estrecha",
        "fr_pano_bloque_der_caract": "Mayoría teórica, alta fragmentación",
        "fr_pano_bloque_cen_caract": "Pivote decisivo del balotaje",

        # Headers de tablas (comunes)
        "fr_pano_th_comuna": "COMUNA",
        "fr_pano_th_comunas": "Comunas",
        "fr_pano_th_region": "REGIÓN",
        "fr_pano_th_ganador": "GANADOR",
        "fr_pano_th_candidato": "CANDIDATO",
        "fr_pano_th_partido": "PARTIDO / COALICIÓN",
        "fr_pano_th_votos": "VOTOS",
        "fr_pano_th_estado": "ESTADO",
        "fr_pano_th_segundo": "2º LUGAR",
        "fr_pano_th_brecha": "BRECHA",
        "fr_pano_th_intensidad": "INTENSIDAD",
        "fr_pano_th_capital": "CAPITAL",
        "fr_pano_th_pct_parisi": "% PARISI",
        "fr_pano_th_pct_jara": "% JARA",
        "fr_pano_th_pct_kast": "% KAST",
        "fr_pano_th_macrozone": "MACROZONA",
        "fr_pano_th_total": "Total",
        "fr_pano_th_pct_del_total": "% del total",

        # Plotly — ejes y labels
        "fr_pano_plot_x_nulos": "Votos nulos",
        "fr_pano_plot_x_blancos": "Votos blancos",
        "fr_pano_plot_no_data": "Sin datos para mostrar.",

        # Scatter recuperables
        "fr_pano_scatter_xaxis": "Votos necesarios para revertir la comuna",
        "fr_pano_scatter_yaxis": "Votos emitidos en la comuna",
        "fr_pano_scatter_lost": "Perdió: {cand}",
        "fr_pano_scatter_margin": "Margen: {n} votos",
        "fr_pano_scatter_casted": "Emitidos: {n}",
        "fr_pano_radio_label": "Mostrar",
        "fr_pano_radio_ambos": "Ambos",
        "fr_pano_radio_jara": "Solo Jara",
        "fr_pano_radio_kast": "Solo Kast",
        "fr_pano_card_recuperables": "Comunas recuperables",
        "fr_pano_card_total_revertir": "Votos totales a revertir",
        "fr_pano_card_prom_comuna": "Promedio por comuna",
        "fr_pano_diff_menor": "Desafío menor",
        "fr_pano_diff_moderado": "Desafío moderado",
        "fr_pano_diff_significativo": "Desafío significativo",

        # Kaiser cards
        "fr_pano_kaiser_card_votos": "Votos",
        "fr_pano_kaiser_card_comunas": "Comunas ganadas",
        "fr_pano_kaiser_card_posicion": "Posición nacional",
        "fr_pano_kaiser_card_bloque": "Bloque",
        "fr_pano_kaiser_val_pct_validos": "{pct}% de válidos",
        "fr_pano_kaiser_val_de_comunas": "de 346 comunas",
        "fr_pano_kaiser_val_posicion": "4°",
        "fr_pano_kaiser_val_de_candidatos": "de 8 candidatos",
        "fr_pano_kaiser_val_bloque": "Nueva derecha libertaria",
        "fr_pano_kaiser_val_bloque_sub": "sin equivalente en 2021",
        "fr_pano_kaiser_th_votos": "Votos Kaiser",
        "fr_pano_kaiser_th_pct": "% Kaiser",
        "fr_pano_kaiser_th_kast": "% Kast",
        "fr_pano_kaiser_th_matthei": "% Matthei",

        # Parisi card singular/plural
        "fr_pano_parisi_cat_singular": "comuna",
        "fr_pano_parisi_cat_plural": "comunas",

        # Tramos población
        "fr_pano_tramo_meta": "{n} comunas · {pct}% población nacional",
        "fr_pano_waffle_title": "Cada celda representa una comuna. {n} comunas en total, agrupadas por candidato ganador.",

        # Mensajes de estado
        "fr_pano_no_data_simple": "Sin datos",
        "fr_pano_no_data_macrozone": "Sin datos de macrozona.",
        "fr_pano_no_cand_cols": "Sin columnas de porcentaje por candidato.",
        "fr_pano_no_data_capitales": "Sin datos suficientes para capitales regionales.",
        "fr_pano_no_data_regionales": "Sin datos suficientes para ganadores regionales.",
        "fr_pano_no_capitales_found": "No se encontraron las capitales regionales en los datos.",
        "fr_pano_no_votes_cols": "Sin columnas de votos por candidato.",
        "fr_pano_no_population": "Se necesita la columna 'population' en los datos.",
        "fr_pano_missing_cols": "Faltan columnas: {cols}",
        "fr_pano_no_margin_1000": "No hay comunas con margen menor a 1000 votos.",
        "fr_pano_no_parisi_pct": "Sin columna 'parisi_pct' en los datos.",
        "fr_pano_no_kaiser_cols": "Sin columnas de Kaiser en los datos.",
        "fr_pano_no_cols_cand": "Columnas no disponibles para {nombre}.",

        # Footer
        "fr_pano_footer": "Datos extraídos de Servicio Electoral de Chile (Servel) · Escrutinio definitivo · Actualizado: 18 de diciembre de 2025",

        # ====================================================================
        # VIEWS/FIRST_ROUND/TERRITORIAL_EXPLORER.PY
        # ====================================================================
        # Niveles (labels visibles de los selectboxes)
        "fr_te_level_macrozona": "Macrozona",
        "fr_te_level_region": "Región",
        "fr_te_level_circunscripcion": "Circunscripción",
        "fr_te_level_distrito": "Distrito",
        "fr_te_level_provincia": "Provincia",
        "fr_te_level_comuna": "Comuna",
        "fr_te_level_all": "Todas",

        # Vista principal
        "fr_te_view_title": "Explorador Territorial",
        "fr_te_view_mapa": "Mapa - {label} ({n} zonas)",
        "fr_te_view_resultados": "Resultados : {zona}",
        "fr_te_view_desglose": "Desglose : {zona}",

        # Navegación
        "fr_te_breadcrumb": "Ruta: {trail} | Ancla movil: {anchor}",
        "fr_te_breadcrumb_nacional": "Nacional (346 comunas)",
        "fr_te_breadcrumb_circunscripcion": "Circunscripción {n}",
        "fr_te_breadcrumb_distrito": "Distrito {n}",
        "fr_te_reset_btn": "Restablecer navegación",

        # Labels dinámicos del mapa
        "fr_te_mapa_macrozone": "Macrozona",
        "fr_te_mapa_region_de": "Regiones de {zona}",
        "fr_te_mapa_provincia_de": "Provincias de {zona}",
        "fr_te_mapa_comuna_de": "Comunas de {zona}",
        "fr_te_mapa_comuna_circ": "Comunas Circunscripción {zona}",
        "fr_te_mapa_comuna_dist": "Comunas Distrito {zona}",
        "fr_te_mapa_comuna_single": "Comuna {zona}",
        "fr_te_mapa_comunas": "Comunas",

        # Sección "Votos nulos y blancos"
        "fr_te_section_validos": "Votos validos",
        "fr_te_section_nulos_blancos": "Votos nulos y blancos",

        # Cards
        "fr_te_card_emitidos": "Total emitidos",
        "fr_te_card_nb_pct": "Nulos+Blancos: {pct}%",
        "fr_te_card_pct_total": "{pct}% del total",

        # Rankings de nulos+blancos
        "fr_te_rank_nacional": "Top zonas con mayor % Nulos+Blancos En: Regiones de Chile",
        "fr_te_rank_macrozona": "Top zonas con mayor % Nulos+Blancos por región",
        "fr_te_rank_region": "Top zonas con mayor % Nulos+Blancos por provincia",
        "fr_te_rank_provincia": "Top zonas con mayor % Nulos+Blancos por comuna",
        "fr_te_rank_otro": "Top zonas con mayor % Nulos+Blancos En: {zona}",

        # Tablas en cascada
        "fr_te_tabla_macrozonas": "Tabla 1: Macrozonas",
        "fr_te_tabla_regiones_1": "Tabla 1: Regiones",
        "fr_te_tabla_regiones_2": "Tabla 2: Regiones",
        "fr_te_tabla_provincias": "Tabla 1: Provincias",
        "fr_te_tabla_comunas_1": "Tabla 1: Comunas",
        "fr_te_tabla_comunas_2": "Tabla 2: Comunas",

        # Headers de tablas
        "fr_te_th_zona": "Zona",
        "fr_te_th_ganador": "Ganador",
        "fr_te_th_pct_ganador": "% Ganador",
        "fr_te_th_comunas": "Comunas",
        "fr_te_th_nulos": "Nulos",
        "fr_te_th_blancos": "Blancos",
        "fr_te_th_nb": "N+B",
        "fr_te_th_pct_nb": "% N+B",
        "fr_te_th_comuna": "Comuna",

        # Tooltips del mapa
        "fr_te_tooltip_ganador": "Ganador: ",
        "fr_te_tooltip_validos": "Votos válidos: ",
        "fr_te_tooltip_nulos": "Votos nulos: ",
        "fr_te_tooltip_blancos": "Votos blancos: ",
        "fr_te_tooltip_region": "Región: ",

        # Waffle (hover)
        "fr_te_waffle_validos": "Válidos: {n} votos ({pct}%)",
        "fr_te_waffle_nulos": "Nulos: {n} votos ({pct}%)",
        "fr_te_waffle_blancos": "Blancos: {n} votos ({pct}%)",

        # Estado / fallback
        "fr_te_no_results": "Sin resultados",
        "fr_te_no_data": "Sin datos",
        "fr_te_no_votes": "Sin votos",
        "fr_te_no_zones": "Sin zonas para {alvl}={aval}",
        "fr_te_no_waffle": "Sin datos para waffle",
        "fr_te_donut_unavailable": "Donut no disponible: {err}",
        "fr_te_map_unavailable": "Mapa OSM no disponible: {err}",
        "fr_te_rank_unavailable": "Ranking no disponible: {err}",
        "fr_te_waffle_unavailable": "Waffle no disponible: {err}",
        "fr_te_na": "—",
        "fr_te_donut_otros": "Otros",
        "fr_te_error_prefix": "Error {err}",

        # ====================================================================
        # VIEWS/FIRST_ROUND/HISTORICAL.PY
        # ====================================================================
        "fr_hist_view_title": "Histórico",
        "fr_hist_view_subtitle": "Comparativa primera vuelta 2021 vs 2025. Cada sección es desplegable.",

        # Expanders
        "fr_hist_exp_participacion": "Participación nacional 2021 vs 2025",
        "fr_hist_exp_bloques": "Evolución de bloques políticos",
        "fr_hist_exp_realineamiento": "Realineamiento electoral: transiciones de ganador 2021 → 2025",
        "fr_hist_exp_cambios_agrupados": "Cambios de ganador agrupados por transición",
        "fr_hist_exp_contundentes": "Comunas que cambiaron de ganador: contundentes vs reñidas",
        "fr_hist_exp_fragmentacion": "Fragmentación del sistema político 2021 vs 2025",
        "fr_hist_exp_parisi_evolucion": "Franco Parisi: evolución y territorio 2021 → 2025",
        "fr_hist_exp_parisi_absorcion": "Franco Parisi: comunas y absorción 2021 → 2025",

        # Secciones
        "fr_hist_section_top_contundentes": "Top 10 cambios más contundentes",
        "fr_hist_section_top_reñidas": "Top 10 cambios más reñidos",
        "fr_hist_section_desglose_2021": "Desglose 2021",
        "fr_hist_section_desglose_2025": "Desglose 2025",
        "fr_hist_section_parisi_macrozone": "Análisis por macrozona · La doble ofensiva",
        "fr_hist_section_parisi_region": "Análisis por región · Un avance casi nacional",
        "fr_hist_section_parisi_top_inc": "Top 10 comunas donde más creció Parisi",
        "fr_hist_section_parisi_top_dec": "Top 10 comunas donde más cayó Parisi",
        "fr_hist_section_parisi_absorbente": "Parisi como gran absorbente · Origen de sus comunas 2025",

        # KPIs / cards
        "fr_hist_kpi_cast_growth": "Crecimiento en votos emitidos",
        "fr_hist_kpi_voto_obligatorio": "Voto voluntario → obligatorio",
        "fr_hist_kpi_efectivo_2025": "Número efectivo de candidatos 2025",
        "fr_hist_kpi_fragmentacion_sub": "Fragmentación sobre votos válidos",
        "fr_hist_kpi_comunas_cambiaron": "Comunas que cambiaron de ganador",
        "fr_hist_kpi_parisi_growth": "Parisi: crecimiento en votos",
        "fr_hist_kpi_pct_comparado": "{pct}% del total comparado",
        "fr_hist_kpi_parisi_sub": "vs 2021 · el candidato que más creció",

        "fr_hist_card_comunas_comp": "Comunas comparadas",
        "fr_hist_card_comunas_comp_sub": "Total 2021 ∩ 2025",
        "fr_hist_card_se_mantiene": "Se mantiene",
        "fr_hist_card_cambia": "Cambia",
        "fr_hist_card_pct_total": "{pct}% del total",
        "fr_hist_card_contundentes": "Cambios contundentes",
        "fr_hist_card_reñidas": "Cambios reñidos",
        "fr_hist_card_contundentes_sub": "ganador 2025 ≥ 40%",
        "fr_hist_card_reñidas_sub": "ganador 2025 < 30%",
        "fr_hist_card_efectivo_2021": "Número efectivo de candidatos 2021",
        "fr_hist_card_cambio": "Cambio",
        "fr_hist_card_mas_fragmentado": "más fragmentado",
        "fr_hist_card_menos_fragmentado": "menos fragmentado",
        "fr_hist_card_votos_2021": "Votos 2021",
        "fr_hist_card_votos_2025": "Votos 2025",
        "fr_hist_card_crecimiento_abs": "Crecimiento absoluto",
        "fr_hist_card_tasa_crecimiento": "Tasa de crecimiento",
        "fr_hist_card_cambio_pp": "Cambio en pp",
        "fr_hist_card_sobre_validos": "sobre votos válidos",
        "fr_hist_card_vs_2021": "vs 2021",
        "fr_hist_card_votos_mas": "votos más que en 2021",

        # Headers de tablas
        "fr_hist_th_metric": "Métrica",
        "fr_hist_th_delta": "Delta",
        "fr_hist_th_delta_pct": "Delta %",
        "fr_hist_th_bloque": "Bloque",
        "fr_hist_th_cand_2021": "Candidato 2021",
        "fr_hist_th_cand_2025": "Candidato 2025",
        "fr_hist_th_delta_pp": "Delta pp",
        "fr_hist_th_ganador_2021": "Ganador 2021",
        "fr_hist_th_ganador_2025": "Ganador 2025",
        "fr_hist_th_comunas": "Comunas",
        "fr_hist_th_pct_min_2025": "% mín 2025",
        "fr_hist_th_pct_prom_2025": "% prom 2025",
        "fr_hist_th_pct_max_2025": "% máx 2025",
        "fr_hist_th_pct_gan_2021": "% Gan. 2021",
        "fr_hist_th_pct_gan_2025": "% Gan. 2025",
        "fr_hist_th_candidato": "Candidato",
        "fr_hist_th_votos": "Votos",
        "fr_hist_th_pct": "%",
        "fr_hist_th_p2": "p²",
        "fr_hist_th_aporte": "Aporte al índice",
        "fr_hist_th_macrozone": "Macrozona",
        "fr_hist_th_pct_2021": "% 2021",
        "fr_hist_th_pct_2025": "% 2025",
        "fr_hist_th_validos_2021": "Válidos 2021",
        "fr_hist_th_validos_2025": "Válidos 2025",
        "fr_hist_th_region": "Región",
        "fr_hist_th_delta_pct": "Δ %",
        "fr_hist_th_comunas_capturadas": "Comunas capturadas",
        "fr_hist_th_pct_del_total": "% del total",

        # Headers adicionales (reutilizables)
        "fr_hist_th_comuna": "Comuna",
        "fr_hist_th_region_short": "Región",

        # Notas al pie
        "fr_hist_note_participacion": "2021: voto voluntario · 2025: voto obligatorio · Crecimiento en votos emitidos: +{pct}%",
        "fr_hist_note_bloques": "Porcentajes calculados sobre votos válidos de cada año. Provoste (centroizquierda) se agrupa con Boric para continuidad con Jara. Kaiser era Republicano en 2021, ahora corre como Libertario.",
        "fr_hist_note_bloques_delta": "Cambio en puntos porcentuales: Izquierda/Centro-Izquierda {izq} · Antisistema {cen} · Derecha/Centro-Derecha {der}.",
        "fr_hist_note_realineamiento": "Filas: ganador 2021 · Columnas: ganador 2025. Las celdas con fondo del color del ganador 2025 indican cuántas comunas pasaron de un ganador a otro.",
        "fr_hist_note_transiciones": "Total de comunas que cambiaron de ganador: {total}. Las columnas % mín/prom/máx 2025 muestran el porcentaje del ganador 2025 en las comunas de cada transición (mínimo, promedio y máximo). Una transición con % alto indica un cambio contundente; % bajo indica un cambio reñido.",
        "fr_hist_note_contundentes": "Comunas donde el ganador 2025 obtuvo los mayores porcentajes sobre votos válidos. Son los cambios donde el nuevo ganador se impuso con más holgura.",
        "fr_hist_note_reñidas": "Comunas donde el ganador 2025 obtuvo los menores porcentajes sobre votos válidos. Son los cambios donde el nuevo ganador se impuso por márgenes más ajustados: territorios donde la disputa política está más abierta.",
        "fr_hist_note_fragmentacion": "El número efectivo de candidatos (índice Laakso-Taagepera) se calcula como 1 / Σ(pᵢ²) sobre votos válidos. Un valor más alto indica mayor fragmentación del sistema (el voto se reparte entre más candidatos con peso relevante). La columna Aporte al índice muestra el peso relativo de cada candidato en el total.",
        "fr_hist_note_parisi_region": "Porcentajes calculados sobre votos válidos de cada año. Regiones ordenadas de norte a sur.",
        "fr_hist_note_parisi_absorcion": "Estas caídas son relativas: Parisi creció en total nacional, pero en algunas comunas donde era muy fuerte en 2021 perdió terreno relativo en 2025. No es una debacle, es una dilución por crecimiento en otras partes del territorio.",
        "fr_hist_note_parisi_absorbente": "Total de comunas que Parisi ganó en 2025: {total}. De ellas, {capturadas} fueron capturadas de otros bloques (las restantes ya eran de Parisi en 2021).",

        # Mensajes de estado
        "fr_hist_info_sin_cambios": "No hubo comunas que cambiaran de ganador entre 2021 y 2025.",
        "fr_hist_info_parisi_sin_absorcion": "Parisi no capturó comunas de otros bloques en 2025.",

        # Bloques políticos
        "fr_hist_bloque_izq": "Izquierda / Centro-Izquierda",
        "fr_hist_bloque_der_cons": "Derecha Conservadora",
        "fr_hist_bloque_der_trad": "Derecha Tradicional",
        "fr_hist_bloque_antisistema": "Tercera Vía / Antisistema",
        "fr_hist_bloque_libertario": "Nueva Derecha / Libertario",
        "fr_hist_bloque_izq_alt": "Izquierda Alternativa",
        "fr_hist_bloque_izq_rad": "Izquierda Radical",
        "fr_hist_bloque_indep": "Independiente",
        "fr_hist_bloque_no_existia": "No existía",

        # Labels de candidatos por año (apellido + ideología)
        "fr_hist_label_2021_boric": "Boric (Izquierda)",
        "fr_hist_label_2021_kast": "Kast (Derecha)",
        "fr_hist_label_2021_parisi": "Parisi (Antisistema)",
        "fr_hist_label_2021_sichel": "Sichel (Derecha Trad.)",
        "fr_hist_label_2021_provoste": "Provoste (Centro-Izq.)",
        "fr_hist_label_2025_jara": "Jara (Izquierda)",
        "fr_hist_label_2025_kast": "Kast (Derecha)",
        "fr_hist_label_2025_parisi": "Parisi (Antisistema)",
        "fr_hist_label_2025_kaiser": "Kaiser (Libertario)",
        "fr_hist_label_2025_matthei": "Matthei (Derecha Trad.)",

        # ====================================================================
        # VIEWS/SECOND_ROUND/SUMMARY.PY
        # ====================================================================
        "sr_summary_section_comparativa": "Comparativa con Primera Vuelta",
        "sr_summary_section_top_comunas": "Top 10 Comunas por Margen",
        "sr_summary_section_macrozone": "Resultados por macrozona",

        # Bloque ganador
        "sr_summary_winner_label": "GANADOR · SEGUNDA VUELTA 2025",
        "sr_summary_bar_midlabel": "50%",
        "sr_summary_votes_unit": "{n} votos",
        "sr_summary_margin_label": "Margen",
        "sr_summary_margin_votes": "+{n} votos",

        # KPIs
        "sr_summary_kpi_inscritos": "Inscritos",
        "sr_summary_kpi_voto_obligatorio": "Voto obligatorio",
        "sr_summary_kpi_cast": "Votos emitidos",
        "sr_summary_kpi_pct_padron": "{pct}% del padrón",
        "sr_summary_kpi_delta_vs_fr": "{pp} pp vs 1ª vuelta",
        "sr_summary_kpi_valid": "Votos válidos",
        "sr_summary_kpi_pct_total": "{pct}% del total",
        "sr_summary_kpi_null": "Votos nulos",
        "sr_summary_kpi_blank": "Votos en blanco",
        "sr_summary_kpi_margin": "Margen",
        "sr_summary_kpi_margin_value": "+{n}",
        "sr_summary_kpi_margin_sub": "votos de diferencia",
        "sr_summary_kpi_margin_delta": "{pp} pp",

        # Tabla comparativa
        "sr_summary_th_candidato": "Candidato",
        "sr_summary_th_1v": "1ª Vuelta",
        "sr_summary_th_2v": "2ª Vuelta",
        "sr_summary_th_delta_pp": "Δ pp",

        # Top comunas
        "sr_summary_top10_label": "Top 10 · {winner}",
        "sr_summary_th_hash": "#",
        "sr_summary_th_comuna": "Comuna",
        "sr_summary_th_region": "Región",
        "sr_summary_th_pct_gan": "% Gan.",
        "sr_summary_th_margen": "Margen",
        "sr_summary_no_data": "Sin datos",

        # Macrozonas
        "sr_summary_th_macrozone": "Macrozona",
        "sr_summary_th_jara_pct": "Jara %",
        "sr_summary_th_kast_pct": "Kast %",
        "sr_summary_th_null_pct": "% Nulo",
        "sr_summary_th_ganador": "Ganador",
        "sr_summary_th_distribucion": "Distribución",
        "sr_summary_no_data_macrozone": "Sin datos por macrozona.",

        # ====================================================================
        # VIEWS/SECOND_ROUND/JARA.PY
        # ====================================================================
        # Expanders
        "sr_jara_exp_bastiones": "Victorias: Bastiones territoriales",
        "sr_jara_exp_flips": "Victorias: Flips de Jara",
        "sr_jara_exp_expansion": "Victorias: Expansión de bastiones",
        "sr_jara_exp_perfil_macro": "Geografía del voto: Perfil por macrozona",
        "sr_jara_exp_gradiente_size": "Gradiente urbano-rural: Jara por tamaño de comuna",
        "sr_jara_exp_gradiente_intensidad": "Gradiente urbano-rural: Intensidad de Jara por zona geográfica",
        "sr_jara_exp_derrotas_comp": "Derrotas ajustadas: Comunas competitivas",
        "sr_jara_exp_derrotas_dist": "Derrotas ajustadas: Distribución por zona",
        "sr_jara_exp_derrotas_zona_margen": "Derrotas ajustadas: Por zona y margen (derrotas por menos de 5 pp)",
        "sr_jara_exp_elite": "Comportamiento: Élite santiaguina",
        "sr_jara_exp_protesta": "Relación: Voto protesta y candidatura de Jara",

        # Subtítulos
        "sr_jara_sub_bastiones": "Jara obtuvo mayoría absoluta (&gt;50% de votos válidos) en <b>{n}</b> comunas.",
        "sr_jara_sub_flips": "Jara <b>dio vuelta {n} comunas</b> entre 1ª y 2ª vuelta: perdió en 1ª y ganó en 2ª.",
        "sr_jara_sub_expansion": "Top 20 comunas donde Jara <b>ganó más votos absolutos</b> entre la 1ª y la 2ª vuelta.",
        "sr_jara_sub_size": "Votación de Jara en 2ª vuelta por tamaño poblacional de la comuna. El % es Jara sobre votos válidos del tramo (Jara + Kast), ponderado por volumen de votos.",
        "sr_jara_sub_size_macro": "Intensidad de Jara (% sobre votos emitidos) cruzando tamaño poblacional de la comuna con macrozona geográfica. El % está ponderado por volumen de votos del tramo. Rojo más oscuro = mayor apoyo a Jara.",
        "sr_jara_sub_size_macro_footer": "Cada celda muestra el % de Jara sobre votos emitidos del cruce tamaño × macrozona. Las celdas en blanco indican que no hay comunas en esa combinación.",
        "sr_jara_sub_derrotas_comp": "Jara estuvo a menos de 2 pp de ganar en <b>{n}</b> comunas.",
        "sr_jara_sub_dist_zona": "Distribución porcentual de las derrotas ajustadas dentro de cada macrozona. Cada barra suma 100%.",
        "sr_jara_sub_derrotas_zona_margen": "Comunas donde Jara perdió por menos de 5 pp, cruzadas por macrozona y rango de margen.",
        "sr_jara_sub_elite": "Evolución de Jara en las 3 comunas de mayor ingreso de Santiago.",
        "sr_jara_sub_protesta": "Relación entre el aumento del voto protesta (nulos + blancos) y la variación de Jara en puntos porcentuales, agrupado por tramos.",

        # Secciones
        "sr_jara_section_top_protesta": "Top 10 comunas con mayor aumento de voto protesta",

        # KPIs
        "sr_jara_kpi_votos_2v": "Votos 2ª vuelta",
        "sr_jara_kpi_votos_2v_sub": "votos totales",
        "sr_jara_kpi_pct_validos": "% sobre válidos",
        "sr_jara_kpi_pct_validos_sub": "de la 2ª vuelta",
        "sr_jara_kpi_comunas_ganadas": "Comunas ganadas",
        "sr_jara_kpi_comunas_ganadas_sub": "de 346 comunas",
        "sr_jara_kpi_flips": "Flips desde 1ª",
        "sr_jara_kpi_flips_sub": "comunas que dio vuelta",

        # Barra bastiones
        "sr_jara_bar_bastiones_izq": "<b>{n} comunas</b> con mayoría absoluta",
        "sr_jara_bar_bastiones_der": "Resto de las comunas",

        # Headers de tablas
        "sr_jara_th_comuna": "Comuna",
        "sr_jara_th_region": "Región",
        "sr_jara_th_pct_jara": "% Jara",
        "sr_jara_th_votos_jara": "Votos Jara",
        "sr_jara_th_ganador_1v": "Ganador 1ª",
        "sr_jara_th_pct_jara_1v": "% Jara 1ª",
        "sr_jara_th_pct_jara_2v": "% Jara 2ª",
        "sr_jara_th_swing": "Swing",
        "sr_jara_th_votos_1v": "Votos 1ª",
        "sr_jara_th_votos_2v": "Votos 2ª",
        "sr_jara_th_delta_votos": "Δ votos",
        "sr_jara_th_delta_pct": "Δ %",
        "sr_jara_th_pct_kast": "% Kast",
        "sr_jara_th_margen_kast": "Margen Kast",
        "sr_jara_th_competitividad": "Competitividad",
        "sr_jara_th_delta_voto_protesta": "Δ voto protesta",
        "sr_jara_th_comunas": "Comunas",
        "sr_jara_th_delta_jara_prom": "Δ Jara (promedio)",
        "sr_jara_th_delta_protesta": "Δ Protesta",
        "sr_jara_th_delta_jara_pp": "Δ Jara (pp)",

        # Labels de gráficos
        "sr_jara_label_1v": "1ª vuelta",
        "sr_jara_label_2v": "2ª vuelta",
        "sr_jara_meta_comunas": "{n} comunas",
        "sr_jara_axis_macrozone": "Macrozona",
        "sr_jara_axis_size": "Tamaño de comuna",
        "sr_jara_colorbar_pct_jara": "% Jara",
        "sr_jara_axis_margen_derrota": "Margen de derrota",
        "sr_jara_colorbar_comunas": "Comunas",

        # Competitividad
        "sr_jara_comp_ultra": "Ultra-tight (<1pp)",
        "sr_jara_comp_competitive": "Competitive (1-2pp)",

        # Mensaje zonas sin derrotas
        "sr_jara_msg_sin_derrotas": "En <b>{zonas}</b> no hay derrotas ajustadas para Jeannette Jara: en todas las comunas, el margen entre la candidata y José Antonio Kast (candidato ganador) supera los <b>5 puntos porcentuales</b>.",

        # Estados
        "sr_jara_no_data": "Sin datos",
        "sr_jara_no_data_macrozone": "Sin datos por macrozona.",
        "sr_jara_no_data_population": "Sin datos de población para clasificar comunas.",
        "sr_jara_no_data_size_macro": "Sin datos suficientes para cruzar tamaño de comuna con macrozona.",

        # Buckets de voto protesta (agrupación por cambio absoluto)
        "sr_jara_bucket_disminuye": "Disminuye",
        "sr_jara_bucket_0_500": "0 – 500",
        "sr_jara_bucket_500_1000": "500 – 1.000",
        "sr_jara_bucket_1000_2000": "1.000 – 2.000",
        "sr_jara_bucket_2000_mas": "> 2.000",

        # ====================================================================
        # VIEWS/SECOND_ROUND/KAST.PY
        # ====================================================================
        # Expanders
        "sr_kast_exp_bastiones": "Victorias: Bastiones territoriales",
        "sr_kast_exp_regionales": "Geografía del voto: bastiones regionales",
        "sr_kast_exp_perfil_macro": "Geografía del voto: Perfil por macrozona",
        "sr_kast_exp_duelos": "Victorias: Duelos revertidos (Jara 1ª → Kast 2ª)",
        "sr_kast_exp_margenes": "Victorias: Márgenes estrechos (Kast por <5 pp)",
        "sr_kast_exp_protesta": "Relación: Voto protesta y candidatura de Kast",
        "sr_kast_exp_crecimiento_dual": "Crecimiento Dual y Lealtad de Base",
        "sr_kast_exp_gradiente_size": "Gradiente urbano-rural: Kast por tamaño de comuna",
        "sr_kast_exp_gradiente_intensidad": "Gradiente urbano-rural: Intensidad de Kast por zona geográfica",

        # Secciones
        "sr_kast_section_intensidad": "Intensidad de victoria",
        "sr_kast_section_swing": "Top 20 comunas por swing Kast",
        "sr_kast_section_growth_top_abs": "Top {n} · Mayor crecimiento absoluto",
        "sr_kast_section_growth_top_rel": "Top {n} · Mayor crecimiento relativo",
        "sr_kast_section_growth_scatter": "Crecimiento absoluto vs relativo",
        "sr_kast_section_growth_bot_abs": "Bottom {n} · Menor crecimiento absoluto",
        "sr_kast_section_growth_bot_rel": "Bottom {n} · Menor crecimiento relativo",

        # Subtítulos
        "sr_kast_sub_bastiones": "Kast superó el <b>{u}%</b> de los votos válidos en <b>{n}</b> comunas. Esas comunas concentran el <b>{p}%</b> de su voto total.",
        "sr_kast_sub_intensidad": "Análisis de comunas competitivas a baluartes históricos",
        "sr_kast_sub_regionales": "Kast superó el <b>{u}%</b> en <b>{n}</b> comunas, distribuidas en <b>{r}</b> regiones. Regiones ordenadas de norte a sur.",
        "sr_kast_sub_duelos": "Kast dio vuelta <b>{n}</b> comunas que Jara había ganado en 1ª vuelta. En todas ellas Kast pasó de perder a ganar entre las dos vueltas.",
        "sr_kast_sub_margenes": "Kast ganó, pero por menos de 5 puntos porcentuales, en <b>{n}</b> comunas. Son sus victorias más frágiles: con un swing menor, habrían quedado del lado de Jara.",
        "sr_kast_sub_protesta": "Relación entre el aumento del voto protesta (nulos + blancos) y el crecimiento de Kast en puntos porcentuales, agrupado por tramos.",
        "sr_kast_sub_size": "Votación de Kast en 2ª vuelta por tamaño poblacional de la comuna. El % es Kast sobre votos válidos del tramo (Kast + Jara), ponderado por volumen de votos.",
        "sr_kast_sub_size_macro": "Intensidad de Kast (% sobre votos emitidos) cruzando tamaño poblacional de la comuna con macrozona geográfica. El % está ponderado por volumen de votos del tramo. Azul más oscuro = mayor apoyo a Kast.",
        "sr_kast_sub_size_macro_footer": "Cada celda muestra el % de Kast sobre votos emitidos del cruce tamaño × macrozona. Las celdas en blanco indican que no hay comunas en esa combinación.",

        # KPIs
        "sr_kast_kpi_votos_2v": "Votos 2ª vuelta",
        "sr_kast_kpi_votos_2v_sub": "votos totales",
        "sr_kast_kpi_pct_validos": "% sobre válidos",
        "sr_kast_kpi_pct_validos_sub": "de la 2ª vuelta",
        "sr_kast_kpi_comunas_ganadas": "Comunas ganadas",
        "sr_kast_kpi_comunas_ganadas_sub": "de 346 comunas",
        "sr_kast_kpi_bastiones": "Bastiones (>{u}%)",
        "sr_kast_kpi_bastiones_sub": "comunas",

        # Barras
        "sr_kast_bar_bastiones_izq": "<b>{n} votos</b> en {m} comunas &gt; {u}%",
        "sr_kast_bar_bastiones_der": "Resto del voto de Kast",
        "sr_kast_bar_flips_izq": "<b>{n} votos</b> en {m} comunas revertidas",

        # Headers
        "sr_kast_th_comuna": "Comuna",
        "sr_kast_th_region": "Región",
        "sr_kast_th_pct_kast": "% Kast",
        "sr_kast_th_margen": "Margen",
        "sr_kast_th_tipo_victoria": "Tipo de victoria",
        "sr_kast_th_categoria": "Categoría",
        "sr_kast_th_comunas": "Comunas",
        "sr_kast_th_pct_victorias": "% de victorias",
        "sr_kast_th_pct_kast_prom": "% Kast prom.",
        "sr_kast_th_pct_kast_min": "% Kast mín.",
        "sr_kast_th_pct_kast_max": "% Kast máx.",
        "sr_kast_th_comunas_gt": "Comunas &gt;{u}%",
        "sr_kast_th_pct_del_total": "% del total",
        "sr_kast_th_margen_prom": "Margen prom.",
        "sr_kast_th_pct_jara_1v": "% Jara 1ª",
        "sr_kast_th_pct_kast_1v": "% Kast 1ª",
        "sr_kast_th_pct_kast_2v": "% Kast 2ª",
        "sr_kast_th_swing_kast": "Swing Kast",
        "sr_kast_th_pct_jara": "% Jara",
        "sr_kast_th_margen_kast": "Margen Kast",
        "sr_kast_th_delta_voto_protesta": "Δ Voto protesta",
        "sr_kast_th_delta_kast_pp": "Δ Kast (pp)",
        "sr_kast_th_delta_nulos": "Δ Nulos (%)",
        "sr_kast_th_delta_blancos": "Δ Blancos (%)",
        "sr_kast_th_votos_kast_1v": "Votos Kast 1ª",
        "sr_kast_th_votos_kast_2v": "Votos Kast 2ª",
        "sr_kast_th_delta_abs": "Δ Absoluto",
        "sr_kast_th_delta_rel": "Δ Relativo",

        # Clasificaciones
        "sr_kast_victoria_arrasa": "Arrasa",
        "sr_kast_victoria_bastion": "Bastión",
        "sr_kast_victoria_solido": "Sólido",
        "sr_kast_victoria_otro": "Otro",
        "sr_kast_victoria_ext_arrasa": "Arrasa (>80%)",
        "sr_kast_victoria_ext_bastion": "Bastión (70-80%)",
        "sr_kast_victoria_ext_solido": "Sólido (60-70%)",
        "sr_kast_victoria_ext_mayoria": "Mayoría simple (50-60%)",

        "sr_kast_protest_disminuye": "Disminuye el voto protesta",
        "sr_kast_protest_bajo": "Aumento bajo (0-500)",
        "sr_kast_protest_medio": "Aumento medio (500-1.000)",
        "sr_kast_protest_alto": "Aumento alto (1.000-2.000)",
        "sr_kast_protest_muy_alto": "Aumento muy alto (>2.000)",

        # Scatter / radio
        "sr_kast_radio_label": "Vista",
        "sr_kast_radio_dual": "Crecimiento Dual",
        "sr_kast_radio_lealtad": "Lealtad de Base",
        "sr_kast_scatter_all": "Todas las comunas ({n})",
        "sr_kast_scatter_hover_rel": "Crec. relativo: %{x:.1f}%",
        "sr_kast_scatter_hover_abs": "Crec. absoluto: %{y:,}",
        "sr_kast_scatter_xaxis": "Crecimiento relativo (%)",
        "sr_kast_scatter_yaxis": "Crecimiento absoluto (votos)",
        "sr_kast_axis_macrozone": "Macrozona",
        "sr_kast_axis_size": "Tamaño de comuna",
        "sr_kast_colorbar_pct_kast": "% Kast",
        "sr_kast_colorbar_comunas": "Comunas",
        "sr_kast_scatter_label_top_abs": "Top {n} absoluto",
        "sr_kast_scatter_label_top_rel": "Top {n} relativo",
        "sr_kast_scatter_label_bot_abs": "Bottom {n} absoluto",
        "sr_kast_scatter_label_bot_rel": "Bottom {n} relativo",

        # Estados
        "sr_kast_no_data": "Sin datos",
        "sr_kast_no_data_macrozone": "Sin datos por macrozona.",
        "sr_kast_no_data_population": "Sin datos de población para clasificar comunas.",
        "sr_kast_no_data_size_macro": "Sin datos suficientes para cruzar tamaño de comuna con macrozona.",

        # ====================================================================
        # VIEWS/SECOND_ROUND/HISTORICAL.PY
        # ====================================================================
        "sr_hist_view_title": "Histórico",
        "sr_hist_view_subtitle": "Comparativa Segunda Vuelta 2021 (Boric vs Kast) vs Segunda Vuelta 2025 (Kast vs Jara). Cada sección es desplegable.",

        # Expanders
        "sr_hist_exp_participacion": "Participación nacional 2021 vs 2025",
        "sr_hist_exp_resultado_nacional": "Resultado nacional: Boric vs Kast (2021) y Kast vs Jara (2025)",
        "sr_hist_exp_bloques": "Evolución de bloques políticos 2021 → 2025",
        "sr_hist_exp_realineamiento": "Realineamiento electoral: matriz de transición 2021 → 2025",
        "sr_hist_exp_kast_evolucion": "Kast: evolución por comuna 2021 → 2025",
        "sr_hist_exp_izquierda": "La izquierda: Boric 2021 → Jara 2025",
        "sr_hist_exp_contundentes": "Comunas que cambiaron de ganador: contundentes vs reñidas",

        # Secciones
        "sr_hist_section_kast_top_up": "Top 10 comunas donde Kast más creció (pp)",
        "sr_hist_section_kast_top_down": "Top 10 comunas donde Kast más cayó (pp)",
        "sr_hist_section_por_region": "Por región",
        "sr_hist_section_top_contundentes": "Top 10 cambios más contundentes",
        "sr_hist_section_top_reñidas": "Top 10 cambios más reñidos",

        # Subtítulos
        "sr_hist_sub_transicion_matrix": "Filas: ganador SR 2021. Columnas: ganador SR 2025. Celdas: número de comunas.",

        # KPIs
        "sr_hist_kpi_cast_growth": "Crecimiento en votos emitidos",
        "sr_hist_kpi_sr_growth_sub": "SR 2021 → SR 2025",
        "sr_hist_kpi_margin_2025": "Margen Kast-Jara 2025",
        "sr_hist_kpi_on_valid": "sobre votos válidos",
        "sr_hist_kpi_comunas_cambiaron": "Comunas que cambiaron de ganador",
        "sr_hist_kpi_pct_total": "{pct}% del total",
        "sr_hist_kpi_kast_growth": "Kast: crecimiento en votos",
        "sr_hist_kpi_kast_unique": "único candidato en ambos balotajes",

        # Cards
        "sr_hist_card_total_comunas": "Total comunas",
        "sr_hist_card_universo": "universo completo",
        "sr_hist_card_mantuvo": "Mantuvo ganador",
        "sr_hist_card_cambio": "Cambió ganador",
        "sr_hist_card_contundentes": "Cambios contundentes",
        "sr_hist_card_reñidas": "Cambios reñidos",
        "sr_hist_card_contundentes_sub": "ganador 2025 ≥ 40%",
        "sr_hist_card_reñidas_sub": "ganador 2025 < 30%",
        "sr_hist_card_boric_2021": "Boric 2021",
        "sr_hist_card_jara_2025": "Jara 2025",
        "sr_hist_card_delta_pp": "Δ pp",
        "sr_hist_card_delta_votos": "Δ votos",
        "sr_hist_card_izq_sub": "izquierda SR 2021 → SR 2025",
        "sr_hist_card_votos": "votos",

        # Headers
        "sr_hist_th_metric": "Métrica",
        "sr_hist_th_sr_2021": "SR 2021",
        "sr_hist_th_sr_2025": "SR 2025",
        "sr_hist_th_delta_abs": "Δ absoluto",
        "sr_hist_th_delta_pct": "Δ %",
        "sr_hist_th_eleccion": "Elección",
        "sr_hist_th_cand_izq": "Candidato izquierda",
        "sr_hist_th_cand_der": "Candidato derecha",
        "sr_hist_th_margin": "Margen",
        "sr_hist_th_ganador": "Ganador",
        "sr_hist_th_bloque": "Bloque",
        "sr_hist_th_cand_2021": "Candidato 2021",
        "sr_hist_th_cand_2025": "Candidato 2025",
        "sr_hist_th_votos": "Votos",
        "sr_hist_th_pct": "%",
        "sr_hist_th_delta_pp": "Δ %",
        "sr_hist_th_comuna": "Comuna",
        "sr_hist_th_region": "Región",
        "sr_hist_th_pct_kast_2021": "% Kast 2021",
        "sr_hist_th_pct_kast_2025": "% Kast 2025",
        "sr_hist_th_pct_boric_2021": "% Boric 2021",
        "sr_hist_th_pct_jara_2025": "% Jara 2025",
        "sr_hist_th_ganador_sr_2021": "Ganador SR 2021",
        "sr_hist_th_ganador_sr_2025": "Ganador SR 2025",
        "sr_hist_th_pct_gan_2021": "% Gan. 2021",
        "sr_hist_th_pct_gan_2025": "% Gan. 2025",

        # Notas
        "sr_hist_note_participacion": "2021: voto voluntario · 2025: voto obligatorio. El crecimiento en votos emitidos refleja el cambio de régimen electoral.",
        "sr_hist_note_resultado": "En 2021 Boric venció con {m21} pp de margen ({v21} votos). En 2025 Kast venció con {m25} pp de margen ({v25} votos).",
        "sr_hist_note_bloques": "Porcentajes calculados sobre votos válidos de cada balotaje. En SR solo participan los dos candidatos más votados en la primera vuelta, así que los bloques están representados por un candidato único cada uno.",
        "sr_hist_note_kast": "Kast es el único candidato presente en ambos balotajes (2021 y 2025). El análisis muestra en qué comunas consolidó su base y dónde perdió terreno relativo. Una caída de pp no necesariamente implica menos votos absolutos: puede reflejar que otros territorios crecieron más.",
        "sr_hist_note_cambios": "Los cambios contundentes son donde el nuevo ganador se impuso con más holgura. Los reñidos son territorios donde la disputa política está más abierta y podría revertirse.",

        # Plotly
        "sr_hist_plot_matrix_title": "Matriz de transición · SR 2021 → SR 2025",

        # Pill ganador
        "sr_hist_pill_elected": "{winner} electo",

        # Estados
        "sr_hist_no_data_transiciones": "Sin datos para analizar transiciones.",
        "sr_hist_no_data_cambios": "No hubo comunas que cambiaran de ganador entre SR 2021 y SR 2025.",

        # Winner labels + change states + participation rows
        "sr_hist_winner_boric": "Boric (izquierda)",
        "sr_hist_winner_jara": "Jara (izquierda)",
        "sr_hist_winner_kast": "Kast (derecha)",
        "sr_hist_change_same": "Igual",
        "sr_hist_change_changed": "Cambió",
        "sr_hist_row_pct_valid": "% válidos sobre emitidos",
        "sr_hist_row_pct_null": "% nulos sobre emitidos",
        "sr_hist_row_pct_blank": "% blancos sobre emitidos",

        # ====================================================================
        # VIEWS/SECOND_ROUND/PANORAMA.PY
        # ====================================================================
        "sr_pano_view_title": "Panorama",
        "sr_pano_view_subtitle": "Cada sección es desplegable.",
        "sr_pano_p_not_significant": "no significativo",

        # Expanders
        "sr_pano_exp_part_comp": "Participación y Voto Válido: 1ª vs 2ª vuelta",
        "sr_pano_exp_nulos": "Análisis de nulos",
        "sr_pano_exp_blancos": "Análisis de blancos",
        "sr_pano_exp_resultados": "Resultados nacionales",
        "sr_pano_exp_comunas_ganadas": "Comunas ganadas",
        "sr_pano_exp_regionales": "Ganadores regionales",
        "sr_pano_exp_capitales": "Voto en capitales regionales",
        "sr_pano_exp_tamano_comuna": "Voto según tamaño de comuna",
        "sr_pano_exp_realineamiento": "Realineamiento electoral: transición de ganadores 1ª → 2ª vuelta",
        "sr_pano_exp_parisi_destino": "Parisi: el destino del voto antisistema",
        "sr_pano_exp_parisi_segmentacion": "Parisi: segmentación de sus comunas",

        # Secciones
        "sr_pano_section_participacion": "Participación nacional",
        "sr_pano_section_reg_nulos_abs": "Regiones con más votos nulos (absoluto)",
        "sr_pano_section_com_nulos_abs": "Comunas con más votos nulos (absoluto)",
        "sr_pano_section_com_nulos_rel": "Comunas con mayor % de votos nulos",
        "sr_pano_section_nulos_comp": "Nulos por región · 1ª vs 2ª vuelta",
        "sr_pano_section_nulos_top": "Top 10 comunas por aumento de nulos",
        "sr_pano_section_reg_blancos_abs": "Regiones con más votos blancos (absoluto)",
        "sr_pano_section_com_blancos_abs": "Comunas con más votos blancos (absoluto)",
        "sr_pano_section_com_blancos_rel": "Comunas con mayor % de votos blancos",
        "sr_pano_section_blancos_comp": "Blancos por región · 1ª vs 2ª vuelta",
        "sr_pano_section_blancos_top": "Top 10 comunas por aumento de blancos",
        "sr_pano_section_matriz": "Matriz de transición · 1ª vuelta → 2ª vuelta",
        "sr_pano_section_retencion": "Tasa de retención por ganador de 1ª vuelta",
        "sr_pano_section_top_caida": "Top 10 comunas con mayor caída de participación",
        "sr_pano_section_high_both": "Comunas con >20% Parisi y margen Kast >10 pp",
        "sr_pano_section_clusters": "Clusters de comunas Parisi",
        "sr_pano_section_pca": "Proyección PCA 2D",
        "sr_pano_section_perfil_clusters": "Perfil de los clusters (métricas normalizadas)",

        # Subtítulos
        "sr_pano_sub_part_comp": "Comparación de votos emitidos, válidos, blancos y nulos entre la primera y la segunda vuelta. Los porcentajes entre paréntesis son sobre votos emitidos de cada vuelta.",
        "sr_pano_sub_resultados": "Resultado final de la segunda vuelta: porcentaje sobre votos válidos, total de votos y margen de victoria.",
        "sr_pano_sub_comunas_ganadas": "Distribución del total de comunas según el candidato ganador (346 comunas).",
        "sr_pano_sub_regionales": "Ganador de cada región, porcentaje obtenido y brecha con el perdedor.",
        "sr_pano_sub_capitales": "Ganador en cada capital regional, porcentaje y brecha.",
        "sr_pano_sub_tamano_comuna": "Balance Jara vs Kast según el tamaño poblacional de la comuna. Cada barra representa un tramo; los segmentos son el % de cada candidato sobre votos válidos del tramo.",
        "sr_pano_sub_realineamiento": "Analiza cuántas comunas cambiaron de ganador entre la primera y la segunda vuelta, con matriz de transición y tasa de retención por candidato.",
        "sr_pano_sub_parisi": "Tres análisis sobre el voto a Franco Parisi en 1ª vuelta y su relación con la participación, el voto nulo/blanco y el margen Kast-Jara en 2ª vuelta.",
        "sr_pano_sub_segmentacion": "Segmentación (K-means) de las comunas donde Parisi ganó en 1ª vuelta, según su comportamiento electoral en la segunda vuelta.",
        "sr_pano_sub_matriz": "Filas: ganador en 1ª vuelta. Columnas: ganador en 2ª vuelta. Celdas: número de comunas.",
        "sr_pano_sub_retencion": "Comunas que mantuvieron el mismo ganador entre 1ª y 2ª vuelta.",

        # KPIs
        "sr_pano_kpi_total_emitidos": "Total emitidos",
        "sr_pano_kpi_nulos_blancos": "Nulos+Blancos: {pct}%",
        "sr_pano_kpi_validos": "Votos válidos",
        "sr_pano_kpi_nulos": "Votos nulos",
        "sr_pano_kpi_blancos": "Votos blancos",
        "sr_pano_kpi_pct_total": "{pct}% del total",

        # Cards
        "sr_pano_card_total_comunas": "Total comunas",
        "sr_pano_card_universo": "universo completo",
        "sr_pano_card_mantuvo": "Mantuvo ganador",
        "sr_pano_card_cambio": "Cambió ganador",
        "sr_pano_card_segment_label": "Segmentación de comunas Parisi",
        "sr_pano_card_segment_value": "{n} comunas",
        "sr_pano_card_segment_sub": "K-means con k={k} sobre comportamiento en 2ª vuelta (Kast %, Jara %, nulo %, blanco %, margen).",
        "sr_pano_card_corr_part": "Correlación entre % Parisi (1ª vuelta) y cambio de participación (2ª vuelta)",
        "sr_pano_card_corr_null": "Correlación Parisi % vs Nulo 2ª vuelta",
        "sr_pano_card_corr_blank": "Correlación Parisi % vs Blanco 2ª vuelta",
        "sr_pano_card_corr_margen": "Correlación entre % Parisi (1ª vuelta) y margen Kast-Jara (2ª vuelta)",

        # Headers
        "sr_pano_th_nulos": "Nulos",
        "sr_pano_th_blancos": "Blancos",
        "sr_pano_th_indicador": "Indicador",
        "sr_pano_th_v1": "1ª Vuelta",
        "sr_pano_th_v2": "2ª Vuelta",
        "sr_pano_th_delta_abs": "Δ Absoluto",
        "sr_pano_th_delta_pct": "Δ %",
        "sr_pano_th_tendencia": "Tendencia",
        "sr_pano_th_region": "Región",
        "sr_pano_th_votos_1v": "{label} 1ª",
        "sr_pano_th_votos_2v": "{label} 2ª",
        "sr_pano_th_delta_votos": "Δ votos",
        "sr_pano_th_pct_1v": "% 1ª",
        "sr_pano_th_pct_2v": "% 2ª",
        "sr_pano_th_delta_pp": "Δ pp",
        "sr_pano_th_comuna": "Comuna",
        "sr_pano_th_ganador_1v": "Ganador 1ª",
        "sr_pano_th_candidato": "Candidato",
        "sr_pano_th_pct_validos": "% sobre válidos",
        "sr_pano_th_votos": "Votos",
        "sr_pano_th_estado": "Estado",
        "sr_pano_th_cand_upper": "CANDIDATO",
        "sr_pano_th_comunas_upper": "COMUNAS GANADAS",
        "sr_pano_th_pct_total_upper": "% DEL TOTAL",
        "sr_pano_th_region_upper": "REGIÓN",
        "sr_pano_th_ganador_upper": "GANADOR",
        "sr_pano_th_pct_ganador_upper": "% GANADOR",
        "sr_pano_th_pct_perdedor_upper": "% PERDEDOR",
        "sr_pano_th_brecha_upper": "BRECHA",
        "sr_pano_th_intensidad_upper": "INTENSIDAD",
        "sr_pano_th_capital_upper": "CAPITAL",
        "sr_pano_th_matriz_label": "1ª vuelta \\ 2ª vuelta",
        "sr_pano_th_total": "Total",
        "sr_pano_th_ganador_1v_lower": "Ganador 1ª vuelta",
        "sr_pano_th_comunas_1v": "Comunas 1ª",
        "sr_pano_th_retenidas": "Retenidas",
        "sr_pano_th_retencion": "Retención %",
        "sr_pano_th_tramo_parisi": "Tramo Parisi",
        "sr_pano_th_comunas": "Comunas",
        "sr_pano_th_pct_parisi_prom": "% Parisi prom.",
        "sr_pano_th_delta_part_prom": "Δ participación prom.",
        "sr_pano_th_delta_pct_prom": "Δ % prom.",
        "sr_pano_th_pct_con_caida": "% con caída",
        "sr_pano_th_pct_kast_prom": "% Kast prom.",
        "sr_pano_th_pct_jara_prom": "% Jara prom.",
        "sr_pano_th_pct_nulo_2v_prom": "% Nulo 2V prom.",
        "sr_pano_th_pct_blanco_2v_prom": "% Blanco 2V prom.",
        "sr_pano_th_pct_parisi_1v": "% Parisi 1V",
        "sr_pano_th_pct_kast_2v": "% Kast 2V",
        "sr_pano_th_pct_jara_2v": "% Jara 2V",
        "sr_pano_th_margen": "Margen",
        "sr_pano_th_margen_prom": "Margen prom.",
        "sr_pano_th_pct_comunas_kast": "% comunas Kast",
        "sr_pano_th_cluster": "Cluster",
        "sr_pano_th_pct_nulo_prom": "% Nulo prom.",

        # Radio / vistas
        "sr_pano_radio_label": "Vista",
        "sr_pano_radio_nulos_v2": "Nulos en 2ª vuelta",
        "sr_pano_radio_nulos_comp": "Comparativa 1ª vs 2ª",
        "sr_pano_radio_blancos_v2": "Blancos en 2ª vuelta",
        "sr_pano_radio_blancos_comp": "Comparativa 1ª vs 2ª",
        "sr_pano_radio_parisi_part": "Participación",
        "sr_pano_radio_parisi_nb": "Voto nulo y blanco",
        "sr_pano_radio_parisi_margen": "Margen Kast-Jara",

        # Trends (pills)
        "sr_pano_trend_up": "sube",
        "sr_pano_trend_down": "baja",
        "sr_pano_trend_flat": "igual",

        # Tramos Parisi
        "sr_pano_parisi_tramo4_bajo": "Bajo (<10%)",
        "sr_pano_parisi_tramo4_medio": "Medio (10-20%)",
        "sr_pano_parisi_tramo4_alto": "Alto (20-30%)",
        "sr_pano_parisi_tramo4_muy_alto": "Muy alto (>30%)",
        "sr_pano_parisi_tramo5_1": "<5%",
        "sr_pano_parisi_tramo5_2": "5-10%",
        "sr_pano_parisi_tramo5_3": "10-15%",
        "sr_pano_parisi_tramo5_4": "15-20%",
        "sr_pano_parisi_tramo5_5": ">20%",

        # Clusters (etiquetas dinámicas)
        "sr_pano_cluster_feudos_kast": "Cluster {cid}: Feudos de Kast (Kast alto, nulo bajo)",
        "sr_pano_cluster_proclives_kast": "Cluster {cid}: Proclives a Kast (Kast medio)",
        "sr_pano_cluster_proclives_jara": "Cluster {cid}: Proclives a Jara",
        "sr_pano_cluster_mixto": "Cluster {cid}: Mixto / Competitivo",

        # Plotly
        "sr_pano_plot_part_title": "Parisi 1ª vuelta vs Cambio de participación",
        "sr_pano_plot_part_x": "Parisi 1ª vuelta (%)",
        "sr_pano_plot_part_y": "Δ participación (2ª vs 1ª)",
        "sr_pano_plot_null_title": "Parisi 1ª vuelta vs Voto nulo 2ª vuelta",
        "sr_pano_plot_null_y": "Voto nulo 2ª vuelta (%)",
        "sr_pano_plot_blank_title": "Parisi 1ª vuelta vs Voto blanco 2ª vuelta",
        "sr_pano_plot_blank_y": "Voto blanco 2ª vuelta (%)",
        "sr_pano_plot_margen_title": "Parisi 1ª vuelta vs margen Kast-Jara 2ª vuelta",
        "sr_pano_plot_margen_y": "Margen Kast - Jara (pp)",
        "sr_pano_plot_margen_bar_title": "Margen Kast-Jara promedio por tramo de Parisi",
        "sr_pano_plot_pca_x": "PC1 ({pct}% var.)",
        "sr_pano_plot_pca_y": "PC2 ({pct}% var.)",
        "sr_pano_plot_tendencia": "Tendencia",

        # Cards de resultado nacional
        "sr_pano_result_electo": "Presidente electo",
        "sr_pano_result_segundo": "Segundo lugar",
        "sr_pano_result_margen": "Margen de victoria",

        # Estados
        "sr_pano_no_data": "Sin datos",
        "sr_pano_no_data_region": "Sin datos de región.",
        "sr_pano_no_data_regionales": "Sin datos suficientes para ganadores regionales.",
        "sr_pano_no_data_capitales": "Sin datos suficientes para capitales regionales.",
        "sr_pano_no_capitales_found": "No se encontraron las capitales regionales en los datos.",
        "sr_pano_no_transiciones": "Sin datos para analizar transiciones.",
        "sr_pano_no_high_both": "No hay comunas con esa combinación.",
        "sr_pano_no_parisi": "Sin datos para el análisis de Parisi.",
        "sr_pano_no_parisi_wins": "No hay comunas donde Parisi haya ganado en 1ª vuelta.",
        "sr_pano_no_clustering": "Muy pocas comunas para clustering.",
        "sr_pano_no_population": "Se necesita la columna 'population' en los datos.",

        # Comments dinámicos _comment_for_r — participación
        "sr_pano_comment_part_neg": "Tendencia negativa clara (r = {r}, {p_txt}). A mayor % de Parisi en 1ª vuelta, menor participación en 2ª vuelta.",
        "sr_pano_comment_part_lev_neg": "Leve tendencia negativa (r = {r}, {p_txt}). A mayor % de Parisi en 1ª vuelta, menor participación en 2ª vuelta.",
        "sr_pano_comment_part_flat": "Ausencia de relación (r = {r}, {p_txt}). A mayor % de Parisi en 1ª vuelta, similar participación en 2ª vuelta.",
        "sr_pano_comment_part_pos": "Tendencia positiva (r = {r}, {p_txt}). A mayor % de Parisi en 1ª vuelta, mayor participación en 2ª vuelta.",

        # Comments dinámicos _comment_for_r — voto nulo
        "sr_pano_comment_null_pos": "Tendencia positiva clara (r = {r}, {p_txt}). El electorado de Parisi canalizó parte de su protesta hacia el voto nulo cuando su candidato ya no estaba en la papeleta.",
        "sr_pano_comment_null_lev_pos": "Leve tendencia positiva (r = {r}, {p_txt}). El electorado de Parisi no muestra una relación fuerte con el voto nulo en 2ª vuelta.",
        "sr_pano_comment_null_flat": "Ausencia de relación (r = {r}, {p_txt}). El electorado de Parisi no muestra una relación fuerte con el voto nulo en 2ª vuelta.",
        "sr_pano_comment_null_neg": "Tendencia negativa (r = {r}, {p_txt}). El electorado de Parisi no muestra una relación fuerte con el voto nulo en 2ª vuelta.",

        # Comments dinámicos _comment_for_r — voto blanco
        "sr_pano_comment_blank_flat": "Sin relación aparente (r = {r}, {p_txt}). La dispersión es prácticamente plana: el voto en blanco en 2ª vuelta no está asociado al electorado de Parisi.",
        "sr_pano_comment_blank_pos": "Tendencia positiva (r = {r}, {p_txt}). El voto en blanco en 2ª vuelta crece levemente con el % de Parisi en 1ª vuelta.",
        "sr_pano_comment_blank_neg": "Tendencia negativa (r = {r}, {p_txt}). El voto en blanco en 2ª vuelta decrece levemente con el % de Parisi en 1ª vuelta.",

        # Comments dinámicos _comment_for_r — margen
        "sr_pano_comment_margen_pos": "Tendencia positiva clara (r = {r}, {p_txt}). El voto de Parisi se volcó mayoritariamente hacia Kast en el balotaje.",
        "sr_pano_comment_margen_lev_pos": "Leve tendencia positiva (r = {r}, {p_txt}). Hay cierta relación entre Parisi y el margen Kast-Jara.",
        "sr_pano_comment_margen_flat": "Ausencia de relación (r = {r}, {p_txt}). No hay una dirección clara del voto Parisi en el balotaje.",
        "sr_pano_comment_margen_neg": "Tendencia negativa (r = {r}, {p_txt}). Hay cierta relación entre Parisi y el margen Kast-Jara.",

        # Bloque margen — comentarios inline
        "sr_pano_parisi_margen_comment_alto": "El margen Kast-Jara promedio crece a medida que aumenta el % de Parisi en la comuna. En el tramo >20% Parisi, el margen alcanza {margen} pp a favor de {ganador}.",
        "sr_pano_parisi_margen_comment": "El margen Kast-Jara promedio crece a medida que aumenta el % de Parisi en la comuna.",

        # Radar — metric labels
        "sr_pano_radar_pct_kast": "% Kast",
        "sr_pano_radar_pct_jara": "% Jara",
        "sr_pano_radar_pct_null": "% Nulo",
        "sr_pano_radar_pct_blank": "% Blanco",
        "sr_pano_radar_margin": "Margen",

        "sr_pano_winner_sin_dato": "Sin dato",

        # ====================================================================
        # COMPONENTS/CHARTS.PY
        # ====================================================================
        "charts_donut_no_data": "No hay datos de comunas ganadas para mostrar.",
        "charts_heatmap_no_data": "Sin datos para el mapa de calor.",
        "charts_heatmap_no_cols": "Sin columnas de votos por candidato.",

        # ====================================================================
        # FOOTER (compartido)
        # ====================================================================
        "data_source": "Datos extraídos de Servicio Electoral de Chile (Servel)",
        "data_source_note": "Escrutinio definitivo · Actualizado: 18 de diciembre 2025",

        # ====================================================================
        # GENÉRICOS (reutilizables, existentes en el diccionario original)
        # ====================================================================
        "casted_votes": "Votos emitidos",
        "valid_votes": "Votos válidos",
        "null_votes": "Votos nulos",
        "blank_votes": "Votos en blanco",
        "winner": "Presidente electo",
        "difference": "Diferencia",
        "votes": "votos",
        "passes_to_runoff": "Pasa a 2ª vuelta",
        "does_not_pass": "No pasa",
        "candidate": "Candidato",
        "party": "Partido / Coalición",
        "pct": "%",
        "status": "Estado",
        "candidate_results_title": "Resultados por candidato",
        "runoff_note": "De acuerdo con la ley N° 18.700, en el caso que ningún candidato obtenga la mayoría absoluta de los votos válidamente emitidos (50% + 1), se realizará una segunda vuelta entre las dos candidaturas más votadas.",

    },

    "EN": {

        # ====================================================================
        # APP / HEADER
        # ====================================================================
        "country": "Republic of Chile",
        "app_title": "Presidential Elections 2025",
        "page_title": "Presidential Elections 2025",
        "app_subtitle": "National results",
        "language": "Language",
        "error_importing_page": "Error importing page",
        "error": "Error loading data",
        "no_data": "No data available",
        "loading": "Loading data...",

        # ====================================================================
        # MAIN NAVIGATION
        # ====================================================================
        "summary": "Summary",
        "first_round": "First Round",
        "second_round": "Second Round",
        "territorial_explorer": "Territorial Explorer",
        "panorama": "Panorama",
        "historical": "Historical",
        "historical_first_round": "First Round History",

        # ====================================================================
        # PAGES/SUMMARY.PY
        # ====================================================================
        "summary_title": "Executive Summary",

        "summary_sr_view_title": "Second Round 2025",
        "summary_sr_view_subtitle": "Kast vs Jara runoff. Final results.",
        "summary_fr_view_title": "First Round 2025",
        "summary_fr_view_subtitle": "8 candidates. First round results.",

        "summary_kpi_casted": "Casted votes",
        "summary_kpi_valid": "Valid votes",
        "summary_kpi_null": "Null votes",
        "summary_kpi_blank": "Blank votes",
        "summary_kpi_pct_padron": "{pct}% of the electoral roll",
        "summary_kpi_pct_total": "{pct}% of total",
        "summary_kpi_diff_vs_fr": "{pp} pp vs first round",

        "summary_winner_label": "WINNER · SECOND ROUND 2025",
        "summary_margin_label": "Margin",
        "summary_margin_votes": "+{n} votes",
        "summary_bar_midlabel": "50%",
        "summary_votes_unit": "{n} votes",

        "summary_table_no_data": "No data available",

        "summary_footer_data_source": "Data from Servicio Electoral de Chile (Servel)",
        "summary_footer_data_source_note": "Final scrutiny · Updated: December 18, 2025",

        # ====================================================================
        # PAGES/FIRST_ROUND.PY
        # ====================================================================
        "fr_orch_fallback_summary": "First Round Summary not available.",
        "fr_orch_fallback_territorial": "Territorial Explorer not available.",
        "fr_orch_fallback_panorama": "Panorama under construction. Available in the next block.",
        "fr_orch_fallback_historical": "First Round History under construction. Available in the next block.",
        "fr_orch_fallback_modulo": "Module not available: {err}",

        # ====================================================================
        # PAGES/SECOND_ROUND.PY
        # ====================================================================
        "sr_orch_tab_panorama": "General panorama",
        "sr_orch_tab_jara": "Candidate Jara",
        "sr_orch_tab_kast": "Candidate Kast",
        "sr_orch_fallback_summary": "Second Round Summary not available.",
        "sr_orch_fallback_territorial": "Territorial Explorer not available.",
        "sr_orch_fallback_panorama": "General panorama under construction.",
        "sr_orch_fallback_jara": "Jara analysis under construction.",
        "sr_orch_fallback_kast": "Kast analysis under construction.",
        "sr_orch_fallback_historical": "Second Round History under construction.",

        # ====================================================================
        # VIEWS/FIRST_ROUND/SUMMARY.PY
        # ====================================================================
        "fr_summary_section_communes_won": "Communes won by candidate",
        "fr_summary_section_bastions": "Top 5 communes per candidate (Electoral strongholds)",
        "fr_summary_section_macrozone": "Results by macrozone",

        "fr_summary_kpi_inscritos": "Registered voters",
        "fr_summary_kpi_obligatorio": "Compulsory voting",
        "fr_summary_kpi_casted": "Casted votes",
        "fr_summary_kpi_valid": "Valid votes",
        "fr_summary_kpi_null": "Null votes",
        "fr_summary_kpi_blank": "Blank votes",
        "fr_summary_kpi_candidates": "Candidates",
        "fr_summary_kpi_pct_padron": "{pct}% of the roll",
        "fr_summary_kpi_pct_total": "{pct}% of total",
        "fr_summary_kpi_over_10": "{n} with >10%",

        "fr_summary_table_hash": "#",
        "fr_summary_table_commune": "Commune",
        "fr_summary_table_region": "Region",
        "fr_summary_table_macrozone": "Macrozone",
        "fr_summary_table_jara_pct": "Jara %",
        "fr_summary_table_kast_pct": "Kast %",
        "fr_summary_table_parisi_pct": "Parisi %",
        "fr_summary_table_null_pct": "% Null",
        "fr_summary_table_winner": "Winner",
        "fr_summary_table_distribution": "Distribution",
        "fr_summary_no_data_bastions": "No data",
        "fr_summary_no_data_macrozone": "No data for macrozone",

        # ====================================================================
        # VIEWS/FIRST_ROUND/PANORAMA.PY
        # ====================================================================
        "fr_pano_view_title": "Panorama",
        "fr_pano_view_subtitle": "Each section is expandable.",

        "fr_pano_exp_nulos": "Null vote analysis",
        "fr_pano_exp_blancos": "Blank vote analysis",
        "fr_pano_exp_resultados": "National results",
        "fr_pano_exp_top_comunas": "Top communes per candidate",
        "fr_pano_exp_comunas_ganadas": "Communes won",
        "fr_pano_exp_ganadores_regionales": "Regional winners",
        "fr_pano_exp_capitales": "Vote in regional capitals",
        "fr_pano_exp_tamano_comuna": "Vote by commune size",
        "fr_pano_exp_recuperables": "Second round: recoverable communes",
        "fr_pano_exp_antisistema": "Anti-system vote analysis: Franco Parisi",
        "fr_pano_exp_kaiser": "Kaiser: the new libertarian right",

        "fr_pano_section_participacion": "National participation",
        "fr_pano_section_reg_nulos_abs": "Regions with most null votes (absolute)",
        "fr_pano_section_com_nulos_abs": "Communes with most null votes (absolute)",
        "fr_pano_section_com_nulos_rel": "Communes with highest % of null votes",
        "fr_pano_section_reg_blancos_abs": "Regions with most blank votes (absolute)",
        "fr_pano_section_com_blancos_abs": "Communes with most blank votes (absolute)",
        "fr_pano_section_com_blancos_rel": "Communes with highest % of blank votes",
        "fr_pano_section_bloques": "Strategic Analysis by Ideological Blocks",
        "fr_pano_section_comunas_macro": "Communes won by macrozone",
        "fr_pano_section_dist_macro": "Distribution by macrozone",
        "fr_pano_section_parisi_top": "Communes with highest % of vote for Parisi",
        "fr_pano_section_parisi_bottom": "Communes with lowest % of vote for Parisi",
        "fr_pano_section_kaiser_macro": "Territorial distribution by macrozone",
        "fr_pano_section_kaiser_top": "Top 10 communes where Kaiser was strongest",

        "fr_pano_sub_top_comunas": "Communes with the highest vote percentage for each candidate (filter: at least 300 casted votes). The RESULT column indicates whether the candidate won in that commune.",
        "fr_pano_sub_comunas_ganadas": "Distribution of the total number of communes in the country according to the winning candidate in each one (346 communes).",
        "fr_pano_sub_ganadores_regionales": "Winner of each region, runner-up and gap between them in percentage points.",
        "fr_pano_sub_capitales": "Winner of each regional capital, runner-up and gap between them in percentage points.",
        "fr_pano_sub_tamano_comuna": "Vote distribution among the 5 main candidates by population size of the commune. Each bar represents a population bracket; segments are the % of each candidate over valid votes in the bracket.",
        "fr_pano_sub_recuperables": "Communes where Jara or Kast lost by less than 1,000 votes in the first round and which, ahead of the second round, are the most contestable territories. X axis: margin to reverse. Y axis: size of the commune (casted votes). Communes in the top-left corner are the most attractive for campaign effort.",
        "fr_pano_sub_antisistema": "Distribution of the vote for Franco Parisi by intensity range (% over valid votes in each commune). The analysis shows the territorial gradient of the anti-system vote: concentrated in the Norte Grande, with decreasing presence toward the south.",
        "fr_pano_sub_kaiser": "Johannes Kaiser is the 2025 breakthrough. With no equivalent in the previous election, his candidacy occupied the space of the new libertarian right and positioned itself as the fourth national force.",
        "fr_pano_sub_kaiser_comp": "Comparison with the other two right-wing candidates (Kast and Matthei) by macrozone. It shows whether Kaiser competes for the same electorate or occupies his own territorial space.",

        "fr_pano_kpi_total_emitidos": "Total casted",
        "fr_pano_kpi_nulos_blancos": "Null+Blank: {pct}%",
        "fr_pano_kpi_validos": "Valid votes",
        "fr_pano_kpi_nulos": "Null votes",
        "fr_pano_kpi_blancos": "Blank votes",
        "fr_pano_kpi_pct_total": "{pct}% of total",

        "fr_pano_bloques_izq": "Left",
        "fr_pano_bloques_antisistema": "Anti-system",
        "fr_pano_bloques_der": "Right",
        "fr_pano_bloques_izq_legend": "Left (Artés, Jara, ME-O)",
        "fr_pano_bloques_antisistema_legend": "Anti-system (Parisi, Mayne-Nicholls)",
        "fr_pano_bloques_der_legend": "Right (Kast, Kaiser, Matthei)",
        "fr_pano_bloques_votos": "{n} votes",
        "fr_pano_bloque_izq_caract": "Clear leadership, narrow base",
        "fr_pano_bloque_der_caract": "Theoretical majority, high fragmentation",
        "fr_pano_bloque_cen_caract": "Decisive pivot of the runoff",

        "fr_pano_th_comuna": "COMMUNE",
        "fr_pano_th_comunas": "Communes",
        "fr_pano_th_region": "REGION",
        "fr_pano_th_ganador": "WINNER",
        "fr_pano_th_candidato": "CANDIDATE",
        "fr_pano_th_partido": "PARTY / COALITION",
        "fr_pano_th_votos": "VOTES",
        "fr_pano_th_estado": "STATUS",
        "fr_pano_th_segundo": "RUNNER-UP",
        "fr_pano_th_brecha": "GAP",
        "fr_pano_th_intensidad": "INTENSITY",
        "fr_pano_th_capital": "CAPITAL",
        "fr_pano_th_pct_parisi": "% PARISI",
        "fr_pano_th_pct_jara": "% JARA",
        "fr_pano_th_pct_kast": "% KAST",
        "fr_pano_th_macrozone": "MACROZONE",
        "fr_pano_th_total": "Total",
        "fr_pano_th_pct_del_total": "% of total",

        "fr_pano_plot_x_nulos": "Null votes",
        "fr_pano_plot_x_blancos": "Blank votes",
        "fr_pano_plot_no_data": "No data to display.",

        "fr_pano_scatter_xaxis": "Votes needed to reverse the commune",
        "fr_pano_scatter_yaxis": "Casted votes in the commune",
        "fr_pano_scatter_lost": "Lost by: {cand}",
        "fr_pano_scatter_margin": "Margin: {n} votes",
        "fr_pano_scatter_casted": "Casted: {n}",
        "fr_pano_radio_label": "Show",
        "fr_pano_radio_ambos": "Both",
        "fr_pano_radio_jara": "Jara only",
        "fr_pano_radio_kast": "Kast only",
        "fr_pano_card_recuperables": "Recoverable communes",
        "fr_pano_card_total_revertir": "Total votes to reverse",
        "fr_pano_card_prom_comuna": "Average per commune",
        "fr_pano_diff_menor": "Minor challenge",
        "fr_pano_diff_moderado": "Moderate challenge",
        "fr_pano_diff_significativo": "Significant challenge",

        "fr_pano_kaiser_card_votos": "Votes",
        "fr_pano_kaiser_card_comunas": "Communes won",
        "fr_pano_kaiser_card_posicion": "National position",
        "fr_pano_kaiser_card_bloque": "Bloc",
        "fr_pano_kaiser_val_pct_validos": "{pct}% of valid",
        "fr_pano_kaiser_val_de_comunas": "of 346 communes",
        "fr_pano_kaiser_val_posicion": "4th",
        "fr_pano_kaiser_val_de_candidatos": "of 8 candidates",
        "fr_pano_kaiser_val_bloque": "New libertarian right",
        "fr_pano_kaiser_val_bloque_sub": "no equivalent in 2021",
        "fr_pano_kaiser_th_votos": "Kaiser votes",
        "fr_pano_kaiser_th_pct": "% Kaiser",
        "fr_pano_kaiser_th_kast": "% Kast",
        "fr_pano_kaiser_th_matthei": "% Matthei",

        "fr_pano_parisi_cat_singular": "commune",
        "fr_pano_parisi_cat_plural": "communes",

        "fr_pano_tramo_meta": "{n} communes · {pct}% national population",
        "fr_pano_waffle_title": "Each cell represents a commune. {n} communes in total, grouped by winning candidate.",

        "fr_pano_no_data_simple": "No data",
        "fr_pano_no_data_macrozone": "No macrozone data.",
        "fr_pano_no_cand_cols": "No candidate percentage columns.",
        "fr_pano_no_data_capitales": "Not enough data for regional capitals.",
        "fr_pano_no_data_regionales": "Not enough data for regional winners.",
        "fr_pano_no_capitales_found": "Regional capitals not found in the data.",
        "fr_pano_no_votes_cols": "No vote columns per candidate.",
        "fr_pano_no_population": "The 'population' column is required in the data.",
        "fr_pano_missing_cols": "Missing columns: {cols}",
        "fr_pano_no_margin_1000": "No communes with margin below 1000 votes.",
        "fr_pano_no_parisi_pct": "No 'parisi_pct' column in the data.",
        "fr_pano_no_kaiser_cols": "No Kaiser columns in the data.",
        "fr_pano_no_cols_cand": "Columns not available for {nombre}.",

        "fr_pano_footer": "Data from Servicio Electoral de Chile (Servel) · Final scrutiny · Updated: December 18, 2025",

        # ====================================================================
        # VIEWS/FIRST_ROUND/TERRITORIAL_EXPLORER.PY
        # ====================================================================
        # Levels (visible selectbox labels)
        "fr_te_level_macrozona": "Macrozone",
        "fr_te_level_region": "Region",
        "fr_te_level_circunscripcion": "Circumscription",
        "fr_te_level_distrito": "District",
        "fr_te_level_provincia": "Province",
        "fr_te_level_comuna": "Commune",
        "fr_te_level_all": "All",

        # Main view
        "fr_te_view_title": "Territorial Explorer",
        "fr_te_view_mapa": "Map - {label} ({n} zones)",
        "fr_te_view_resultados": "Results : {zona}",
        "fr_te_view_desglose": "Breakdown : {zona}",

        # Navigation
        "fr_te_breadcrumb": "Path: {trail} | Moving anchor: {anchor}",
        "fr_te_breadcrumb_nacional": "National (346 communes)",
        "fr_te_breadcrumb_circunscripcion": "Circumscription {n}",
        "fr_te_breadcrumb_distrito": "District {n}",
        "fr_te_reset_btn": "Reset navigation",

        # Dynamic map labels
        "fr_te_mapa_macrozone": "Macrozone",
        "fr_te_mapa_region_de": "Regions of {zona}",
        "fr_te_mapa_provincia_de": "Provinces of {zona}",
        "fr_te_mapa_comuna_de": "Communes of {zona}",
        "fr_te_mapa_comuna_circ": "Communes Circumscription {zona}",
        "fr_te_mapa_comuna_dist": "Communes District {zona}",
        "fr_te_mapa_comuna_single": "Commune {zona}",
        "fr_te_mapa_comunas": "Communes",

        # "Null and blank votes" section
        "fr_te_section_validos": "Valid votes",
        "fr_te_section_nulos_blancos": "Null and blank votes",

        # Cards
        "fr_te_card_emitidos": "Total casted",
        "fr_te_card_nb_pct": "Null+Blank: {pct}%",
        "fr_te_card_pct_total": "{pct}% of total",

        # Null+Blank rankings
        "fr_te_rank_nacional": "Top zones by highest % Null+Blank In: Regions of Chile",
        "fr_te_rank_macrozona": "Top zones by highest % Null+Blank per region",
        "fr_te_rank_region": "Top zones by highest % Null+Blank per province",
        "fr_te_rank_provincia": "Top zones by highest % Null+Blank per commune",
        "fr_te_rank_otro": "Top zones by highest % Null+Blank In: {zona}",

        # Cascading tables
        "fr_te_tabla_macrozonas": "Table 1: Macrozone",
        "fr_te_tabla_regiones_1": "Table 1: Regions",
        "fr_te_tabla_regiones_2": "Table 2: Regions",
        "fr_te_tabla_provincias": "Table 1: Provinces",
        "fr_te_tabla_comunas_1": "Table 1: Communes",
        "fr_te_tabla_comunas_2": "Table 2: Communes",

        # Table headers
        "fr_te_th_zona": "Zone",
        "fr_te_th_ganador": "Winner",
        "fr_te_th_pct_ganador": "% Winner",
        "fr_te_th_comunas": "Communes",
        "fr_te_th_nulos": "Nulls",
        "fr_te_th_blancos": "Blanks",
        "fr_te_th_nb": "N+B",
        "fr_te_th_pct_nb": "% N+B",
        "fr_te_th_comuna": "Commune",

        # Map tooltips
        "fr_te_tooltip_ganador": "Winner: ",
        "fr_te_tooltip_validos": "Valid votes: ",
        "fr_te_tooltip_nulos": "Null votes: ",
        "fr_te_tooltip_blancos": "Blank votes: ",
        "fr_te_tooltip_region": "Region: ",

        # Waffle (hover)
        "fr_te_waffle_validos": "Valid: {n} votes ({pct}%)",
        "fr_te_waffle_nulos": "Nulls: {n} votes ({pct}%)",
        "fr_te_waffle_blancos": "Blanks: {n} votes ({pct}%)",

        # State / fallback
        "fr_te_no_results": "No results",
        "fr_te_no_data": "No data",
        "fr_te_no_votes": "No votes",
        "fr_te_no_zones": "No zones for {alvl}={aval}",
        "fr_te_no_waffle": "No data for waffle",
        "fr_te_donut_unavailable": "Donut not available: {err}",
        "fr_te_map_unavailable": "OSM map not available: {err}",
        "fr_te_rank_unavailable": "Ranking not available: {err}",
        "fr_te_waffle_unavailable": "Waffle not available: {err}",
        "fr_te_na": "—",
        "fr_te_donut_otros": "Others",
        "fr_te_error_prefix": "Error {err}",

        # ====================================================================
        # VIEWS/FIRST_ROUND/HISTORICAL.PY
        # ====================================================================
        "fr_hist_view_title": "Historical",
        "fr_hist_view_subtitle": "First round 2021 vs 2025 comparison. Each section is expandable.",

        "fr_hist_exp_participacion": "National participation 2021 vs 2025",
        "fr_hist_exp_bloques": "Political bloc evolution",
        "fr_hist_exp_realineamiento": "Electoral realignment: winner transitions 2021 → 2025",
        "fr_hist_exp_cambios_agrupados": "Winner changes grouped by transition",
        "fr_hist_exp_contundentes": "Communes that changed winner: decisive vs close",
        "fr_hist_exp_fragmentacion": "Political system fragmentation 2021 vs 2025",
        "fr_hist_exp_parisi_evolucion": "Franco Parisi: evolution and territory 2021 → 2025",
        "fr_hist_exp_parisi_absorcion": "Franco Parisi: communes and absorption 2021 → 2025",

        "fr_hist_section_top_contundentes": "Top 10 most decisive changes",
        "fr_hist_section_top_reñidas": "Top 10 closest changes",
        "fr_hist_section_desglose_2021": "2021 breakdown",
        "fr_hist_section_desglose_2025": "2025 breakdown",
        "fr_hist_section_parisi_macrozone": "Macrozone analysis · The double offensive",
        "fr_hist_section_parisi_region": "Region analysis · An almost national advance",
        "fr_hist_section_parisi_top_inc": "Top 10 communes where Parisi grew the most",
        "fr_hist_section_parisi_top_dec": "Top 10 communes where Parisi fell the most",
        "fr_hist_section_parisi_absorbente": "Parisi as great absorber · Origin of his 2025 communes",

        "fr_hist_kpi_cast_growth": "Growth in casted votes",
        "fr_hist_kpi_voto_obligatorio": "Voluntary → compulsory voting",
        "fr_hist_kpi_efectivo_2025": "Effective number of candidates 2025",
        "fr_hist_kpi_fragmentacion_sub": "Fragmentation over valid votes",
        "fr_hist_kpi_comunas_cambiaron": "Communes that changed winner",
        "fr_hist_kpi_parisi_growth": "Parisi: growth in votes",
        "fr_hist_kpi_pct_comparado": "{pct}% of the compared total",
        "fr_hist_kpi_parisi_sub": "vs 2021 · the candidate who grew the most",

        "fr_hist_card_comunas_comp": "Communes compared",
        "fr_hist_card_comunas_comp_sub": "Total 2021 ∩ 2025",
        "fr_hist_card_se_mantiene": "Holds",
        "fr_hist_card_cambia": "Changes",
        "fr_hist_card_pct_total": "{pct}% of total",
        "fr_hist_card_contundentes": "Decisive changes",
        "fr_hist_card_reñidas": "Close changes",
        "fr_hist_card_contundentes_sub": "2025 winner ≥ 40%",
        "fr_hist_card_reñidas_sub": "2025 winner < 30%",
        "fr_hist_card_efectivo_2021": "Effective number of candidates 2021",
        "fr_hist_card_cambio": "Change",
        "fr_hist_card_mas_fragmentado": "more fragmented",
        "fr_hist_card_menos_fragmentado": "less fragmented",
        "fr_hist_card_votos_2021": "Votes 2021",
        "fr_hist_card_votos_2025": "Votes 2025",
        "fr_hist_card_crecimiento_abs": "Absolute growth",
        "fr_hist_card_tasa_crecimiento": "Growth rate",
        "fr_hist_card_cambio_pp": "Change in pp",
        "fr_hist_card_sobre_validos": "over valid votes",
        "fr_hist_card_vs_2021": "vs 2021",
        "fr_hist_card_votos_mas": "votes more than in 2021",

        "fr_hist_th_metric": "Metric",
        "fr_hist_th_delta": "Delta",
        "fr_hist_th_delta_pct": "Delta %",
        "fr_hist_th_bloque": "Bloc",
        "fr_hist_th_cand_2021": "Candidate 2021",
        "fr_hist_th_cand_2025": "Candidate 2025",
        "fr_hist_th_delta_pp": "Delta pp",
        "fr_hist_th_ganador_2021": "Winner 2021",
        "fr_hist_th_ganador_2025": "Winner 2025",
        "fr_hist_th_comunas": "Communes",
        "fr_hist_th_pct_min_2025": "% min 2025",
        "fr_hist_th_pct_prom_2025": "% avg 2025",
        "fr_hist_th_pct_max_2025": "% max 2025",
        "fr_hist_th_pct_gan_2021": "% Win. 2021",
        "fr_hist_th_pct_gan_2025": "% Win. 2025",
        "fr_hist_th_candidato": "Candidate",
        "fr_hist_th_votos": "Votes",
        "fr_hist_th_pct": "%",
        "fr_hist_th_p2": "p²",
        "fr_hist_th_aporte": "Contribution to index",
        "fr_hist_th_macrozone": "Macrozone",
        "fr_hist_th_pct_2021": "% 2021",
        "fr_hist_th_pct_2025": "% 2025",
        "fr_hist_th_validos_2021": "Valid 2021",
        "fr_hist_th_validos_2025": "Valid 2025",
        "fr_hist_th_region": "Region",
        "fr_hist_th_delta_pct": "Δ %",
        "fr_hist_th_comunas_capturadas": "Communes captured",
        "fr_hist_th_pct_del_total": "% of total",

        # Additional table headers (reusable)
        "fr_hist_th_comuna": "Commune",
        "fr_hist_th_region_short": "Region",

        "fr_hist_note_participacion": "2021: voluntary voting · 2025: compulsory voting · Growth in casted votes: +{pct}%",
        "fr_hist_note_bloques": "Percentages calculated over valid votes of each year. Provoste (center-left) is grouped with Boric for continuity with Jara. Kaiser was Republican in 2021, now runs as Libertarian.",
        "fr_hist_note_bloques_delta": "Change in percentage points: Left/Center-Left {izq} · Anti-system {cen} · Right/Center-Right {der}.",
        "fr_hist_note_realineamiento": "Rows: 2021 winner · Columns: 2025 winner. Cells with the 2025 winner's color background indicate how many communes moved from one winner to another.",
        "fr_hist_note_transiciones": "Total communes that changed winner: {total}. The % min/avg/max 2025 columns show the 2025 winner's percentage in the communes of each transition (minimum, average and maximum). A transition with a high % indicates a decisive change; a low % indicates a close change.",
        "fr_hist_note_contundentes": "Communes where the 2025 winner obtained the highest percentages over valid votes. These are the changes where the new winner prevailed most comfortably.",
        "fr_hist_note_reñidas": "Communes where the 2025 winner obtained the lowest percentages over valid votes. These are the changes where the new winner prevailed by the narrowest margins: territories where political contest is most open.",
        "fr_hist_note_fragmentacion": "The effective number of candidates (Laakso-Taagepera index) is calculated as 1 / Σ(pᵢ²) over valid votes. A higher value indicates greater fragmentation of the system (the vote is spread among more candidates with relevant weight). The Contribution to index column shows the relative weight of each candidate in the total.",
        "fr_hist_note_parisi_region": "Percentages calculated over valid votes of each year. Regions ordered from north to south.",
        "fr_hist_note_parisi_absorcion": "These falls are relative: Parisi grew nationally, but in some communes where he was very strong in 2021 he lost relative ground in 2025. It is not a debacle, it is a dilution through growth elsewhere in the territory.",
        "fr_hist_note_parisi_absorbente": "Total communes Parisi won in 2025: {total}. Of these, {capturadas} were captured from other blocs (the rest were already Parisi's in 2021).",

        "fr_hist_info_sin_cambios": "There were no communes that changed winner between 2021 and 2025.",
        "fr_hist_info_parisi_sin_absorcion": "Parisi did not capture communes from other blocs in 2025.",

        "fr_hist_bloque_izq": "Left / Center-Left",
        "fr_hist_bloque_der_cons": "Conservative Right",
        "fr_hist_bloque_der_trad": "Traditional Right",
        "fr_hist_bloque_antisistema": "Third Way / Anti-system",
        "fr_hist_bloque_libertario": "New Right / Libertarian",
        "fr_hist_bloque_izq_alt": "Alternative Left",
        "fr_hist_bloque_izq_rad": "Radical Left",
        "fr_hist_bloque_indep": "Independent",
        "fr_hist_bloque_no_existia": "Did not exist",

        # Candidate labels by year (surname + ideology)
        "fr_hist_label_2021_boric": "Boric (Left)",
        "fr_hist_label_2021_kast": "Kast (Right)",
        "fr_hist_label_2021_parisi": "Parisi (Anti-system)",
        "fr_hist_label_2021_sichel": "Sichel (Traditional Right)",
        "fr_hist_label_2021_provoste": "Provoste (Center-Left)",
        "fr_hist_label_2025_jara": "Jara (Left)",
        "fr_hist_label_2025_kast": "Kast (Right)",
        "fr_hist_label_2025_parisi": "Parisi (Anti-system)",
        "fr_hist_label_2025_kaiser": "Kaiser (Libertarian)",
        "fr_hist_label_2025_matthei": "Matthei (Traditional Right)",

        # ====================================================================
        # VIEWS/SECOND_ROUND/SUMMARY.PY
        # ====================================================================
        "sr_summary_section_comparativa": "Comparison with First Round",
        "sr_summary_section_top_comunas": "Top 10 Communes by Margin",
        "sr_summary_section_macrozone": "Results by macrozone",

        "sr_summary_winner_label": "WINNER · SECOND ROUND 2025",
        "sr_summary_bar_midlabel": "50%",
        "sr_summary_votes_unit": "{n} votes",
        "sr_summary_margin_label": "Margin",
        "sr_summary_margin_votes": "+{n} votes",

        "sr_summary_kpi_inscritos": "Registered voters",
        "sr_summary_kpi_voto_obligatorio": "Compulsory voting",
        "sr_summary_kpi_cast": "Casted votes",
        "sr_summary_kpi_pct_padron": "{pct}% of the roll",
        "sr_summary_kpi_delta_vs_fr": "{pp} pp vs first round",
        "sr_summary_kpi_valid": "Valid votes",
        "sr_summary_kpi_pct_total": "{pct}% of total",
        "sr_summary_kpi_null": "Null votes",
        "sr_summary_kpi_blank": "Blank votes",
        "sr_summary_kpi_margin": "Margin",
        "sr_summary_kpi_margin_value": "+{n}",
        "sr_summary_kpi_margin_sub": "votes difference",
        "sr_summary_kpi_margin_delta": "{pp} pp",

        "sr_summary_th_candidato": "Candidate",
        "sr_summary_th_1v": "1st Round",
        "sr_summary_th_2v": "2nd Round",
        "sr_summary_th_delta_pp": "Δ pp",

        "sr_summary_top10_label": "Top 10 · {winner}",
        "sr_summary_th_hash": "#",
        "sr_summary_th_comuna": "Commune",
        "sr_summary_th_region": "Region",
        "sr_summary_th_pct_gan": "% Win.",
        "sr_summary_th_margen": "Margin",
        "sr_summary_no_data": "No data",

        "sr_summary_th_macrozone": "Macrozone",
        "sr_summary_th_jara_pct": "Jara %",
        "sr_summary_th_kast_pct": "Kast %",
        "sr_summary_th_null_pct": "% Null",
        "sr_summary_th_ganador": "Winner",
        "sr_summary_th_distribucion": "Distribution",
        "sr_summary_no_data_macrozone": "No data by macrozone.",

        # ====================================================================
        # VIEWS/SECOND_ROUND/JARA.PY
        # ====================================================================
        "sr_jara_exp_bastiones": "Wins: Territorial strongholds",
        "sr_jara_exp_flips": "Wins: Jara's flips",
        "sr_jara_exp_expansion": "Wins: Stronghold expansion",
        "sr_jara_exp_perfil_macro": "Vote geography: Profile by macrozone",
        "sr_jara_exp_gradiente_size": "Urban-rural gradient: Jara by commune size",
        "sr_jara_exp_gradiente_intensidad": "Urban-rural gradient: Jara intensity by geographic zone",
        "sr_jara_exp_derrotas_comp": "Close defeats: Competitive communes",
        "sr_jara_exp_derrotas_dist": "Close defeats: Distribution by zone",
        "sr_jara_exp_derrotas_zona_margen": "Close defeats: By zone and margin (defeats by less than 5 pp)",
        "sr_jara_exp_elite": "Behavior: Santiago elite",
        "sr_jara_exp_protesta": "Relationship: Protest vote and Jara's candidacy",

        "sr_jara_sub_bastiones": "Jara obtained an absolute majority (&gt;50% of valid votes) in <b>{n}</b> communes.",
        "sr_jara_sub_flips": "Jara <b>flipped {n} communes</b> between 1st and 2nd round: lost in the 1st and won in the 2nd.",
        "sr_jara_sub_expansion": "Top 20 communes where Jara <b>gained the most absolute votes</b> between the 1st and 2nd round.",
        "sr_jara_sub_size": "Jara's vote in the 2nd round by population size of the commune. The % is Jara over valid votes of the bracket (Jara + Kast), weighted by vote volume.",
        "sr_jara_sub_size_macro": "Jara intensity (% over casted votes) crossing population size of the commune with geographic macrozone. The % is weighted by vote volume of the bracket. Darker red = stronger support for Jara.",
        "sr_jara_sub_size_macro_footer": "Each cell shows the % for Jara over casted votes of the size × macrozone cross. Blank cells indicate no communes in that combination.",
        "sr_jara_sub_derrotas_comp": "Jara was less than 2 pp away from winning in <b>{n}</b> communes.",
        "sr_jara_sub_dist_zona": "Percentage distribution of close defeats within each macrozone. Each bar sums to 100%.",
        "sr_jara_sub_derrotas_zona_margen": "Communes where Jara lost by less than 5 pp, crossed by macrozone and margin range.",
        "sr_jara_sub_elite": "Jara's evolution in the 3 highest-income communes of Santiago.",
        "sr_jara_sub_protesta": "Relationship between the increase in protest vote (null + blank) and Jara's variation in percentage points, grouped by brackets.",

        "sr_jara_section_top_protesta": "Top 10 communes with the largest increase in protest vote",

        "sr_jara_kpi_votos_2v": "2nd round votes",
        "sr_jara_kpi_votos_2v_sub": "total votes",
        "sr_jara_kpi_pct_validos": "% over valid",
        "sr_jara_kpi_pct_validos_sub": "of the 2nd round",
        "sr_jara_kpi_comunas_ganadas": "Communes won",
        "sr_jara_kpi_comunas_ganadas_sub": "of 346 communes",
        "sr_jara_kpi_flips": "Flips from 1st",
        "sr_jara_kpi_flips_sub": "communes flipped",

        "sr_jara_bar_bastiones_izq": "<b>{n} communes</b> with absolute majority",
        "sr_jara_bar_bastiones_der": "Rest of the communes",

        "sr_jara_th_comuna": "Commune",
        "sr_jara_th_region": "Region",
        "sr_jara_th_pct_jara": "% Jara",
        "sr_jara_th_votos_jara": "Jara votes",
        "sr_jara_th_ganador_1v": "1st round winner",
        "sr_jara_th_pct_jara_1v": "% Jara 1st",
        "sr_jara_th_pct_jara_2v": "% Jara 2nd",
        "sr_jara_th_swing": "Swing",
        "sr_jara_th_votos_1v": "Votes 1st",
        "sr_jara_th_votos_2v": "Votes 2nd",
        "sr_jara_th_delta_votos": "Δ votes",
        "sr_jara_th_delta_pct": "Δ %",
        "sr_jara_th_pct_kast": "% Kast",
        "sr_jara_th_margen_kast": "Kast margin",
        "sr_jara_th_competitividad": "Competitiveness",
        "sr_jara_th_delta_voto_protesta": "Δ Protest vote",
        "sr_jara_th_comunas": "Communes",
        "sr_jara_th_delta_jara_prom": "Δ Jara (average)",
        "sr_jara_th_delta_protesta": "Δ Protest",
        "sr_jara_th_delta_jara_pp": "Δ Jara (pp)",

        "sr_jara_label_1v": "1st round",
        "sr_jara_label_2v": "2nd round",
        "sr_jara_meta_comunas": "{n} communes",
        "sr_jara_axis_macrozone": "Macrozone",
        "sr_jara_axis_size": "Commune size",
        "sr_jara_colorbar_pct_jara": "% Jara",
        "sr_jara_axis_margen_derrota": "Defeat margin",
        "sr_jara_colorbar_comunas": "Communes",

        "sr_jara_comp_ultra": "Ultra-tight (<1pp)",
        "sr_jara_comp_competitive": "Competitive (1-2pp)",

        "sr_jara_msg_sin_derrotas": "In <b>{zonas}</b> there are no close defeats for Jeannette Jara: in all communes, the margin between the candidate and José Antonio Kast (winning candidate) exceeds <b>5 percentage points</b>.",

        "sr_jara_no_data": "No data",
        "sr_jara_no_data_macrozone": "No data by macrozone.",
        "sr_jara_no_data_population": "No population data to classify communes.",
        "sr_jara_no_data_size_macro": "Not enough data to cross commune size with macrozone.",

        # Protest vote buckets (grouping by absolute change)
        "sr_jara_bucket_disminuye": "Decreases",
        "sr_jara_bucket_0_500": "0 – 500",
        "sr_jara_bucket_500_1000": "500 – 1,000",
        "sr_jara_bucket_1000_2000": "1,000 – 2,000",
        "sr_jara_bucket_2000_mas": "> 2,000",

        # ====================================================================
        # VIEWS/SECOND_ROUND/KAST.PY
        # ====================================================================
        "sr_kast_exp_bastiones": "Wins: Territorial strongholds",
        "sr_kast_exp_regionales": "Vote geography: regional strongholds",
        "sr_kast_exp_perfil_macro": "Vote geography: Profile by macrozone",
        "sr_kast_exp_duelos": "Wins: Reversed duels (Jara 1st → Kast 2nd)",
        "sr_kast_exp_margenes": "Wins: Narrow margins (Kast by <5 pp)",
        "sr_kast_exp_protesta": "Relationship: Protest vote and Kast's candidacy",
        "sr_kast_exp_crecimiento_dual": "Dual Growth and Base Loyalty",
        "sr_kast_exp_gradiente_size": "Urban-rural gradient: Kast by commune size",
        "sr_kast_exp_gradiente_intensidad": "Urban-rural gradient: Kast intensity by geographic zone",

        "sr_kast_section_intensidad": "Victory intensity",
        "sr_kast_section_swing": "Top 20 communes by Kast swing",
        "sr_kast_section_growth_top_abs": "Top {n} · Highest absolute growth",
        "sr_kast_section_growth_top_rel": "Top {n} · Highest relative growth",
        "sr_kast_section_growth_scatter": "Absolute vs relative growth",
        "sr_kast_section_growth_bot_abs": "Bottom {n} · Lowest absolute growth",
        "sr_kast_section_growth_bot_rel": "Bottom {n} · Lowest relative growth",

        "sr_kast_sub_bastiones": "Kast exceeded <b>{u}%</b> of valid votes in <b>{n}</b> communes. Those communes concentrate <b>{p}%</b> of his total vote.",
        "sr_kast_sub_intensidad": "Analysis of communes from competitive to historic strongholds",
        "sr_kast_sub_regionales": "Kast exceeded <b>{u}%</b> in <b>{n}</b> communes, distributed across <b>{r}</b> regions. Regions ordered from north to south.",
        "sr_kast_sub_duelos": "Kast flipped <b>{n}</b> communes that Jara had won in the 1st round. In all of them Kast went from losing to winning between the two rounds.",
        "sr_kast_sub_margenes": "Kast won, but by less than 5 percentage points, in <b>{n}</b> communes. These are his most fragile victories: with a smaller swing, they would have gone to Jara.",
        "sr_kast_sub_protesta": "Relationship between the increase in protest vote (null + blank) and Kast's growth in percentage points, grouped by brackets.",
        "sr_kast_sub_size": "Kast's vote in the 2nd round by population size of the commune. The % is Kast over valid votes of the bracket (Kast + Jara), weighted by vote volume.",
        "sr_kast_sub_size_macro": "Kast intensity (% over casted votes) crossing population size of the commune with geographic macrozone. The % is weighted by vote volume of the bracket. Darker blue = stronger support for Kast.",
        "sr_kast_sub_size_macro_footer": "Each cell shows the % for Kast over casted votes of the size × macrozone cross. Blank cells indicate no communes in that combination.",

        "sr_kast_kpi_votos_2v": "2nd round votes",
        "sr_kast_kpi_votos_2v_sub": "total votes",
        "sr_kast_kpi_pct_validos": "% over valid",
        "sr_kast_kpi_pct_validos_sub": "of the 2nd round",
        "sr_kast_kpi_comunas_ganadas": "Communes won",
        "sr_kast_kpi_comunas_ganadas_sub": "of 346 communes",
        "sr_kast_kpi_bastiones": "Strongholds (>{u}%)",
        "sr_kast_kpi_bastiones_sub": "communes",

        "sr_kast_bar_bastiones_izq": "<b>{n} votes</b> in {m} communes &gt; {u}%",
        "sr_kast_bar_bastiones_der": "Rest of Kast's vote",
        "sr_kast_bar_flips_izq": "<b>{n} votes</b> in {m} communes flipped",

        "sr_kast_th_comuna": "Commune",
        "sr_kast_th_region": "Region",
        "sr_kast_th_pct_kast": "% Kast",
        "sr_kast_th_margen": "Margin",
        "sr_kast_th_tipo_victoria": "Victory type",
        "sr_kast_th_categoria": "Category",
        "sr_kast_th_comunas": "Communes",
        "sr_kast_th_pct_victorias": "% of victories",
        "sr_kast_th_pct_kast_prom": "% Kast avg.",
        "sr_kast_th_pct_kast_min": "% Kast min.",
        "sr_kast_th_pct_kast_max": "% Kast max.",
        "sr_kast_th_comunas_gt": "Communes &gt;{u}%",
        "sr_kast_th_pct_del_total": "% of total",
        "sr_kast_th_margen_prom": "Avg. margin",
        "sr_kast_th_pct_jara_1v": "% Jara 1st",
        "sr_kast_th_pct_kast_1v": "% Kast 1st",
        "sr_kast_th_pct_kast_2v": "% Kast 2nd",
        "sr_kast_th_swing_kast": "Kast swing",
        "sr_kast_th_pct_jara": "% Jara",
        "sr_kast_th_margen_kast": "Kast margin",
        "sr_kast_th_delta_voto_protesta": "Δ Protest vote",
        "sr_kast_th_delta_kast_pp": "Δ Kast (pp)",
        "sr_kast_th_delta_nulos": "Δ Null (%)",
        "sr_kast_th_delta_blancos": "Δ Blank (%)",
        "sr_kast_th_votos_kast_1v": "Kast votes 1st",
        "sr_kast_th_votos_kast_2v": "Kast votes 2nd",
        "sr_kast_th_delta_abs": "Δ Absolute",
        "sr_kast_th_delta_rel": "Δ Relative",

        "sr_kast_victoria_arrasa": "Sweeps",
        "sr_kast_victoria_bastion": "Stronghold",
        "sr_kast_victoria_solido": "Solid",
        "sr_kast_victoria_otro": "Other",
        "sr_kast_victoria_ext_arrasa": "Sweeps (>80%)",
        "sr_kast_victoria_ext_bastion": "Stronghold (70-80%)",
        "sr_kast_victoria_ext_solido": "Solid (60-70%)",
        "sr_kast_victoria_ext_mayoria": "Simple majority (50-60%)",

        "sr_kast_protest_disminuye": "Protest vote decreases",
        "sr_kast_protest_bajo": "Low increase (0-500)",
        "sr_kast_protest_medio": "Medium increase (500-1,000)",
        "sr_kast_protest_alto": "High increase (1,000-2,000)",
        "sr_kast_protest_muy_alto": "Very high increase (>2,000)",

        "sr_kast_radio_label": "View",
        "sr_kast_radio_dual": "Dual Growth",
        "sr_kast_radio_lealtad": "Base Loyalty",
        "sr_kast_scatter_all": "All communes ({n})",
        "sr_kast_scatter_hover_rel": "Relative growth: %{x:.1f}%",
        "sr_kast_scatter_hover_abs": "Absolute growth: %{y:,}",
        "sr_kast_scatter_xaxis": "Relative growth (%)",
        "sr_kast_scatter_yaxis": "Absolute growth (votes)",
        "sr_kast_axis_macrozone": "Macrozone",
        "sr_kast_axis_size": "Commune size",
        "sr_kast_colorbar_pct_kast": "% Kast",
        "sr_kast_colorbar_comunas": "Communes",
        "sr_kast_scatter_label_top_abs": "Top {n} absolute",
        "sr_kast_scatter_label_top_rel": "Top {n} relative",
        "sr_kast_scatter_label_bot_abs": "Bottom {n} absolute",
        "sr_kast_scatter_label_bot_rel": "Bottom {n} relative",

        "sr_kast_no_data": "No data",
        "sr_kast_no_data_macrozone": "No data by macrozone.",
        "sr_kast_no_data_population": "No population data to classify communes.",
        "sr_kast_no_data_size_macro": "Not enough data to cross commune size with macrozone.",

        # ====================================================================
        # VIEWS/SECOND_ROUND/HISTORICAL.PY
        # ====================================================================
        "sr_hist_view_title": "Historical",
        "sr_hist_view_subtitle": "Second Round 2021 (Boric vs Kast) vs Second Round 2025 (Kast vs Jara) comparison. Each section is expandable.",

        "sr_hist_exp_participacion": "National participation 2021 vs 2025",
        "sr_hist_exp_resultado_nacional": "National result: Boric vs Kast (2021) and Kast vs Jara (2025)",
        "sr_hist_exp_bloques": "Political bloc evolution 2021 → 2025",
        "sr_hist_exp_realineamiento": "Electoral realignment: transition matrix 2021 → 2025",
        "sr_hist_exp_kast_evolucion": "Kast: evolution by commune 2021 → 2025",
        "sr_hist_exp_izquierda": "The left: Boric 2021 → Jara 2025",
        "sr_hist_exp_contundentes": "Communes that changed winner: decisive vs close",

        "sr_hist_section_kast_top_up": "Top 10 communes where Kast grew the most (pp)",
        "sr_hist_section_kast_top_down": "Top 10 communes where Kast fell the most (pp)",
        "sr_hist_section_por_region": "By region",
        "sr_hist_section_top_contundentes": "Top 10 most decisive changes",
        "sr_hist_section_top_reñidas": "Top 10 closest changes",

        "sr_hist_sub_transicion_matrix": "Rows: SR 2021 winner. Columns: SR 2025 winner. Cells: number of communes.",

        "sr_hist_kpi_cast_growth": "Growth in casted votes",
        "sr_hist_kpi_sr_growth_sub": "SR 2021 → SR 2025",
        "sr_hist_kpi_margin_2025": "Kast-Jara margin 2025",
        "sr_hist_kpi_on_valid": "over valid votes",
        "sr_hist_kpi_comunas_cambiaron": "Communes that changed winner",
        "sr_hist_kpi_pct_total": "{pct}% of total",
        "sr_hist_kpi_kast_growth": "Kast: growth in votes",
        "sr_hist_kpi_kast_unique": "only candidate in both runoffs",

        "sr_hist_card_total_comunas": "Total communes",
        "sr_hist_card_universo": "full universe",
        "sr_hist_card_mantuvo": "Held winner",
        "sr_hist_card_cambio": "Changed winner",
        "sr_hist_card_contundentes": "Decisive changes",
        "sr_hist_card_reñidas": "Close changes",
        "sr_hist_card_contundentes_sub": "2025 winner ≥ 40%",
        "sr_hist_card_reñidas_sub": "2025 winner < 30%",
        "sr_hist_card_boric_2021": "Boric 2021",
        "sr_hist_card_jara_2025": "Jara 2025",
        "sr_hist_card_delta_pp": "Δ pp",
        "sr_hist_card_delta_votos": "Δ votes",
        "sr_hist_card_izq_sub": "left SR 2021 → SR 2025",
        "sr_hist_card_votos": "votes",

        "sr_hist_th_metric": "Metric",
        "sr_hist_th_sr_2021": "SR 2021",
        "sr_hist_th_sr_2025": "SR 2025",
        "sr_hist_th_delta_abs": "Δ absolute",
        "sr_hist_th_delta_pct": "Δ %",
        "sr_hist_th_eleccion": "Election",
        "sr_hist_th_cand_izq": "Left candidate",
        "sr_hist_th_cand_der": "Right candidate",
        "sr_hist_th_margin": "Margin",
        "sr_hist_th_ganador": "Winner",
        "sr_hist_th_bloque": "Bloc",
        "sr_hist_th_cand_2021": "Candidate 2021",
        "sr_hist_th_cand_2025": "Candidate 2025",
        "sr_hist_th_votos": "Votes",
        "sr_hist_th_pct": "%",
        "sr_hist_th_delta_pp": "Δ %",
        "sr_hist_th_comuna": "Commune",
        "sr_hist_th_region": "Region",
        "sr_hist_th_pct_kast_2021": "% Kast 2021",
        "sr_hist_th_pct_kast_2025": "% Kast 2025",
        "sr_hist_th_pct_boric_2021": "% Boric 2021",
        "sr_hist_th_pct_jara_2025": "% Jara 2025",
        "sr_hist_th_ganador_sr_2021": "SR 2021 winner",
        "sr_hist_th_ganador_sr_2025": "SR 2025 winner",
        "sr_hist_th_pct_gan_2021": "% Win. 2021",
        "sr_hist_th_pct_gan_2025": "% Win. 2025",

        "sr_hist_note_participacion": "2021: voluntary voting · 2025: compulsory voting. The growth in casted votes reflects the change in electoral regime.",
        "sr_hist_note_resultado": "In 2021 Boric won with a {m21} pp margin ({v21} votes). In 2025 Kast won with a {m25} pp margin ({v25} votes).",
        "sr_hist_note_bloques": "Percentages calculated over valid votes of each runoff. In the SR only the two most-voted candidates from the first round participate, so the blocs are represented by a single candidate each.",
        "sr_hist_note_kast": "Kast is the only candidate present in both runoffs (2021 and 2025). The analysis shows in which communes he consolidated his base and where he lost relative ground. A drop in pp does not necessarily imply fewer absolute votes: it may reflect that other territories grew more.",
        "sr_hist_note_cambios": "Decisive changes are where the new winner prevailed most comfortably. Close ones are territories where political contest is most open and could be reversed.",

        "sr_hist_plot_matrix_title": "Transition matrix · SR 2021 → SR 2025",

        "sr_hist_pill_elected": "{winner} elected",

        "sr_hist_no_data_transiciones": "No data to analyze transitions.",
        "sr_hist_no_data_cambios": "There were no communes that changed winner between SR 2021 and SR 2025.",

        # Winner labels + change states + participation rows
        "sr_hist_winner_boric": "Boric (left)",
        "sr_hist_winner_jara": "Jara (left)",
        "sr_hist_winner_kast": "Kast (right)",
        "sr_hist_change_same": "Same",
        "sr_hist_change_changed": "Changed",
        "sr_hist_row_pct_valid": "% valid over casted",
        "sr_hist_row_pct_null": "% null over casted",
        "sr_hist_row_pct_blank": "% blank over casted",

        # ====================================================================
        # VIEWS/SECOND_ROUND/PANORAMA.PY
        # ====================================================================
        "sr_pano_view_title": "Panorama",
        "sr_pano_view_subtitle": "Each section is expandable.",
        "sr_pano_p_not_significant": "not significant",

        "sr_pano_exp_part_comp": "Participation and Valid Vote: 1st vs 2nd round",
        "sr_pano_exp_nulos": "Null vote analysis",
        "sr_pano_exp_blancos": "Blank vote analysis",
        "sr_pano_exp_resultados": "National results",
        "sr_pano_exp_comunas_ganadas": "Communes won",
        "sr_pano_exp_regionales": "Regional winners",
        "sr_pano_exp_capitales": "Vote in regional capitals",
        "sr_pano_exp_tamano_comuna": "Vote by commune size",
        "sr_pano_exp_realineamiento": "Electoral realignment: winner transition 1st → 2nd round",
        "sr_pano_exp_parisi_destino": "Parisi: the fate of the anti-system vote",
        "sr_pano_exp_parisi_segmentacion": "Parisi: segmentation of his communes",

        "sr_pano_section_participacion": "National participation",
        "sr_pano_section_reg_nulos_abs": "Regions with most null votes (absolute)",
        "sr_pano_section_com_nulos_abs": "Communes with most null votes (absolute)",
        "sr_pano_section_com_nulos_rel": "Communes with highest % of null votes",
        "sr_pano_section_nulos_comp": "Null votes by region · 1st vs 2nd round",
        "sr_pano_section_nulos_top": "Top 10 communes by increase in null votes",
        "sr_pano_section_reg_blancos_abs": "Regions with most blank votes (absolute)",
        "sr_pano_section_com_blancos_abs": "Communes with most blank votes (absolute)",
        "sr_pano_section_com_blancos_rel": "Communes with highest % of blank votes",
        "sr_pano_section_blancos_comp": "Blank votes by region · 1st vs 2nd round",
        "sr_pano_section_blancos_top": "Top 10 communes by increase in blank votes",
        "sr_pano_section_matriz": "Transition matrix · 1st round → 2nd round",
        "sr_pano_section_retencion": "Retention rate by 1st round winner",
        "sr_pano_section_top_caida": "Top 10 communes with largest participation drop",
        "sr_pano_section_high_both": "Communes with >20% Parisi and Kast margin >10 pp",
        "sr_pano_section_clusters": "Clusters of Parisi communes",
        "sr_pano_section_pca": "PCA 2D projection",
        "sr_pano_section_perfil_clusters": "Cluster profile (normalized metrics)",

        "sr_pano_sub_part_comp": "Comparison of casted, valid, blank and null votes between the first and second round. Percentages in parentheses are over casted votes of each round.",
        "sr_pano_sub_resultados": "Final result of the second round: percentage over valid votes, total votes and margin of victory.",
        "sr_pano_sub_comunas_ganadas": "Distribution of the total number of communes according to the winning candidate (346 communes).",
        "sr_pano_sub_regionales": "Winner of each region, percentage obtained and gap with the loser.",
        "sr_pano_sub_capitales": "Winner in each regional capital, percentage and gap.",
        "sr_pano_sub_tamano_comuna": "Jara vs Kast balance by population size of the commune. Each bar represents a bracket; segments are the % of each candidate over valid votes of the bracket.",
        "sr_pano_sub_realineamiento": "Analyzes how many communes changed winner between the first and second round, with transition matrix and retention rate by candidate.",
        "sr_pano_sub_parisi": "Three analyses on the vote for Franco Parisi in the 1st round and its relationship with participation, null/blank vote and the Kast-Jara margin in the 2nd round.",
        "sr_pano_sub_segmentacion": "Segmentation (K-means) of the communes where Parisi won in the 1st round, according to their electoral behavior in the second round.",
        "sr_pano_sub_matriz": "Rows: 1st round winner. Columns: 2nd round winner. Cells: number of communes.",
        "sr_pano_sub_retencion": "Communes that kept the same winner between the 1st and 2nd round.",

        "sr_pano_kpi_total_emitidos": "Total casted",
        "sr_pano_kpi_nulos_blancos": "Null+Blank: {pct}%",
        "sr_pano_kpi_validos": "Valid votes",
        "sr_pano_kpi_nulos": "Null votes",
        "sr_pano_kpi_blancos": "Blank votes",
        "sr_pano_kpi_pct_total": "{pct}% of total",

        "sr_pano_card_total_comunas": "Total communes",
        "sr_pano_card_universo": "full universe",
        "sr_pano_card_mantuvo": "Held winner",
        "sr_pano_card_cambio": "Changed winner",
        "sr_pano_card_segment_label": "Segmentation of Parisi communes",
        "sr_pano_card_segment_value": "{n} communes",
        "sr_pano_card_segment_sub": "K-means with k={k} on 2nd round behavior (Kast %, Jara %, null %, blank %, margin).",
        "sr_pano_card_corr_part": "Correlation between % Parisi (1st round) and participation change (2nd round)",
        "sr_pano_card_corr_null": "Correlation Parisi % vs Null 2nd round",
        "sr_pano_card_corr_blank": "Correlation Parisi % vs Blank 2nd round",
        "sr_pano_card_corr_margen": "Correlation between % Parisi (1st round) and Kast-Jara margin (2nd round)",

        "sr_pano_th_nulos": "Nulls",
        "sr_pano_th_blancos": "Blanks",
        "sr_pano_th_indicador": "Indicator",
        "sr_pano_th_v1": "1st Round",
        "sr_pano_th_v2": "2nd Round",
        "sr_pano_th_delta_abs": "Δ Absolute",
        "sr_pano_th_delta_pct": "Δ %",
        "sr_pano_th_tendencia": "Trend",
        "sr_pano_th_region": "Region",
        "sr_pano_th_votos_1v": "{label} 1st",
        "sr_pano_th_votos_2v": "{label} 2nd",
        "sr_pano_th_delta_votos": "Δ votes",
        "sr_pano_th_pct_1v": "% 1st",
        "sr_pano_th_pct_2v": "% 2nd",
        "sr_pano_th_delta_pp": "Δ pp",
        "sr_pano_th_comuna": "Commune",
        "sr_pano_th_ganador_1v": "1st round winner",
        "sr_pano_th_candidato": "Candidate",
        "sr_pano_th_pct_validos": "% over valid",
        "sr_pano_th_votos": "Votes",
        "sr_pano_th_estado": "Status",
        "sr_pano_th_cand_upper": "CANDIDATE",
        "sr_pano_th_comunas_upper": "COMMUNES WON",
        "sr_pano_th_pct_total_upper": "% OF TOTAL",
        "sr_pano_th_region_upper": "REGION",
        "sr_pano_th_ganador_upper": "WINNER",
        "sr_pano_th_pct_ganador_upper": "% WINNER",
        "sr_pano_th_pct_perdedor_upper": "% LOSER",
        "sr_pano_th_brecha_upper": "GAP",
        "sr_pano_th_intensidad_upper": "INTENSITY",
        "sr_pano_th_capital_upper": "CAPITAL",
        "sr_pano_th_matriz_label": "1st round \\ 2nd round",
        "sr_pano_th_total": "Total",
        "sr_pano_th_ganador_1v_lower": "1st round winner",
        "sr_pano_th_comunas_1v": "Communes 1st",
        "sr_pano_th_retenidas": "Retained",
        "sr_pano_th_retencion": "Retention %",
        "sr_pano_th_tramo_parisi": "Parisi bracket",
        "sr_pano_th_comunas": "Communes",
        "sr_pano_th_pct_parisi_prom": "% Parisi avg.",
        "sr_pano_th_delta_part_prom": "Δ participation avg.",
        "sr_pano_th_delta_pct_prom": "Δ % avg.",
        "sr_pano_th_pct_con_caida": "% with drop",
        "sr_pano_th_pct_kast_prom": "% Kast avg.",
        "sr_pano_th_pct_jara_prom": "% Jara avg.",
        "sr_pano_th_pct_nulo_2v_prom": "% Null 2nd avg.",
        "sr_pano_th_pct_blanco_2v_prom": "% Blank 2nd avg.",
        "sr_pano_th_pct_parisi_1v": "% Parisi 1st",
        "sr_pano_th_pct_kast_2v": "% Kast 2nd",
        "sr_pano_th_pct_jara_2v": "% Jara 2nd",
        "sr_pano_th_margen": "Margin",
        "sr_pano_th_margen_prom": "Avg. margin",
        "sr_pano_th_pct_comunas_kast": "% communes Kast",
        "sr_pano_th_cluster": "Cluster",
        "sr_pano_th_pct_nulo_prom": "% Null avg.",

        "sr_pano_radio_label": "View",
        "sr_pano_radio_nulos_v2": "Nulls in 2nd round",
        "sr_pano_radio_nulos_comp": "1st vs 2nd comparison",
        "sr_pano_radio_blancos_v2": "Blanks in 2nd round",
        "sr_pano_radio_blancos_comp": "1st vs 2nd comparison",
        "sr_pano_radio_parisi_part": "Participation",
        "sr_pano_radio_parisi_nb": "Null and blank vote",
        "sr_pano_radio_parisi_margen": "Kast-Jara margin",

        "sr_pano_trend_up": "up",
        "sr_pano_trend_down": "down",
        "sr_pano_trend_flat": "flat",

        "sr_pano_parisi_tramo4_bajo": "Low (<10%)",
        "sr_pano_parisi_tramo4_medio": "Medium (10-20%)",
        "sr_pano_parisi_tramo4_alto": "High (20-30%)",
        "sr_pano_parisi_tramo4_muy_alto": "Very high (>30%)",
        "sr_pano_parisi_tramo5_1": "<5%",
        "sr_pano_parisi_tramo5_2": "5-10%",
        "sr_pano_parisi_tramo5_3": "10-15%",
        "sr_pano_parisi_tramo5_4": "15-20%",
        "sr_pano_parisi_tramo5_5": ">20%",

        "sr_pano_cluster_feudos_kast": "Cluster {cid}: Kast strongholds (high Kast, low null)",
        "sr_pano_cluster_proclives_kast": "Cluster {cid}: Leaning Kast (medium Kast)",
        "sr_pano_cluster_proclives_jara": "Cluster {cid}: Leaning Jara",
        "sr_pano_cluster_mixto": "Cluster {cid}: Mixed / Competitive",

        "sr_pano_plot_part_title": "Parisi 1st round vs Participation change",
        "sr_pano_plot_part_x": "Parisi 1st round (%)",
        "sr_pano_plot_part_y": "Δ participation (2nd vs 1st)",
        "sr_pano_plot_null_title": "Parisi 1st round vs Null vote 2nd round",
        "sr_pano_plot_null_y": "Null vote 2nd round (%)",
        "sr_pano_plot_blank_title": "Parisi 1st round vs Blank vote 2nd round",
        "sr_pano_plot_blank_y": "Blank vote 2nd round (%)",
        "sr_pano_plot_margen_title": "Parisi 1st round vs Kast-Jara margin 2nd round",
        "sr_pano_plot_margen_y": "Kast - Jara margin (pp)",
        "sr_pano_plot_margen_bar_title": "Average Kast-Jara margin by Parisi bracket",
        "sr_pano_plot_pca_x": "PC1 ({pct}% var.)",
        "sr_pano_plot_pca_y": "PC2 ({pct}% var.)",
        "sr_pano_plot_tendencia": "Trend",

        "sr_pano_result_electo": "President-elect",
        "sr_pano_result_segundo": "Runner-up",
        "sr_pano_result_margen": "Victory margin",

        "sr_pano_no_data": "No data",
        "sr_pano_no_data_region": "No region data.",
        "sr_pano_no_data_regionales": "Not enough data for regional winners.",
        "sr_pano_no_data_capitales": "Not enough data for regional capitals.",
        "sr_pano_no_capitales_found": "Regional capitals not found in the data.",
        "sr_pano_no_transiciones": "No data to analyze transitions.",
        "sr_pano_no_high_both": "No communes with that combination.",
        "sr_pano_no_parisi": "No data for the Parisi analysis.",
        "sr_pano_no_parisi_wins": "No communes where Parisi won in the 1st round.",
        "sr_pano_no_clustering": "Too few communes for clustering.",
        "sr_pano_no_population": "The 'population' column is required in the data.",

        "sr_pano_comment_part_neg": "Clear negative trend (r = {r}, {p_txt}). The higher the % for Parisi in the 1st round, the lower the participation in the 2nd round.",
        "sr_pano_comment_part_lev_neg": "Slight negative trend (r = {r}, {p_txt}). The higher the % for Parisi in the 1st round, the lower the participation in the 2nd round.",
        "sr_pano_comment_part_flat": "No apparent relationship (r = {r}, {p_txt}). The higher the % for Parisi in the 1st round, similar participation in the 2nd round.",
        "sr_pano_comment_part_pos": "Positive trend (r = {r}, {p_txt}). The higher the % for Parisi in the 1st round, the higher the participation in the 2nd round.",

        "sr_pano_comment_null_pos": "Clear positive trend (r = {r}, {p_txt}). Parisi's electorate channeled part of its protest into the null vote once its candidate was no longer on the ballot.",
        "sr_pano_comment_null_lev_pos": "Slight positive trend (r = {r}, {p_txt}). Parisi's electorate does not show a strong relationship with the null vote in the 2nd round.",
        "sr_pano_comment_null_flat": "No apparent relationship (r = {r}, {p_txt}). Parisi's electorate does not show a strong relationship with the null vote in the 2nd round.",
        "sr_pano_comment_null_neg": "Negative trend (r = {r}, {p_txt}). Parisi's electorate does not show a strong relationship with the null vote in the 2nd round.",

        "sr_pano_comment_blank_flat": "No apparent relationship (r = {r}, {p_txt}). The dispersion is practically flat: the blank vote in the 2nd round is not associated with Parisi's electorate.",
        "sr_pano_comment_blank_pos": "Positive trend (r = {r}, {p_txt}). The blank vote in the 2nd round rises slightly with the % for Parisi in the 1st round.",
        "sr_pano_comment_blank_neg": "Negative trend (r = {r}, {p_txt}). The blank vote in the 2nd round falls slightly with the % for Parisi in the 1st round.",

        "sr_pano_comment_margen_pos": "Clear positive trend (r = {r}, {p_txt}). Parisi's vote went mostly to Kast in the runoff.",
        "sr_pano_comment_margen_lev_pos": "Slight positive trend (r = {r}, {p_txt}). There is some relationship between Parisi and the Kast-Jara margin.",
        "sr_pano_comment_margen_flat": "No apparent relationship (r = {r}, {p_txt}). There is no clear direction of Parisi's vote in the runoff.",
        "sr_pano_comment_margen_neg": "Negative trend (r = {r}, {p_txt}). There is some relationship between Parisi and the Kast-Jara margin.",

        "sr_pano_parisi_margen_comment_alto": "The average Kast-Jara margin grows as the % for Parisi in the commune increases. In the >20% Parisi bracket, the margin reaches {margen} pp in favor of {ganador}.",
        "sr_pano_parisi_margen_comment": "The average Kast-Jara margin grows as the % for Parisi in the commune increases.",

        "sr_pano_radar_pct_kast": "% Kast",
        "sr_pano_radar_pct_jara": "% Jara",
        "sr_pano_radar_pct_null": "% Null",
        "sr_pano_radar_pct_blank": "% Blank",
        "sr_pano_radar_margin": "Margin",

        "sr_pano_winner_sin_dato": "No data",

        # ====================================================================
        # COMPONENTS/CHARTS.PY
        # ====================================================================
        "charts_donut_no_data": "No data on communes won to display.",
        "charts_heatmap_no_data": "No data for the heatmap.",
        "charts_heatmap_no_cols": "No vote columns per candidate.",

        # ====================================================================
        # FOOTER (shared)
        # ====================================================================
        "data_source": "Data from Servicio Electoral de Chile (Servel)",
        "data_source_note": "Final scrutiny · Updated: December 18, 2025",

        # ====================================================================
        # GENERIC (existing in the original dictionary)
        # ====================================================================
        "casted_votes": "Casted votes",
        "valid_votes": "Valid votes",
        "null_votes": "Null votes",
        "blank_votes": "Blank votes",
        "winner": "President-elect",
        "difference": "Difference",
        "votes": "votes",
        "passes_to_runoff": "Passes to runoff",
        "does_not_pass": "Does not pass",
        "candidate": "Candidate",
        "party": "Party / Coalition",
        "pct": "%",
        "status": "Status",
        "candidate_results_title": "Results by candidate",
        "runoff_note": "Under Law N° 18.700, if no candidate obtains an absolute majority of validly cast votes (50% + 1), a second round will be held between the two most-voted candidacies.",

    },
}
