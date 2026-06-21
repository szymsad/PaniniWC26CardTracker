import streamlit as st
import pandas as pd
from database import (
    initialize_database,
    add_card,
    remove_card,
    get_card,
    get_duplicates,
    get_stats,
    get_missing,
    get_cards_by_country,
    get_country_stats,
    get_owned_cards,
    COUNTRIES,
    special,
)

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WC 2026 · Card Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styling — white base ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset to white ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
.block-container {
    background: #ffffff !important;
    color: #111827 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f8fafc !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * { color: #111827 !important; }

/* ── Stat cards ── */
.stat-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.stat-value { font-size: 2rem; font-weight: 800; line-height: 1; }
.stat-label { font-size: 0.72rem; color: #64748b; margin-top: 5px;
              text-transform: uppercase; letter-spacing: .08em; }

/* ── Progress bar ── */
.progress-wrap { background:#e2e8f0; border-radius:99px; height:8px;
                 overflow:hidden; margin:5px 0 6px; }
.progress-fill  { height:100%; border-radius:99px;
                  background:linear-gradient(90deg,#16a34a,#22c55e); }

/* ── Album grid ── */
.album-page-title {
    font-size: .78rem; font-weight: 700; color: #64748b;
    text-transform: uppercase; letter-spacing: .1em;
    margin: 24px 0 10px;
    padding-bottom: 4px;
    border-bottom: 1px solid #e2e8f0;
}
.album-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 6px;
}
.album-card {
    border-radius: 8px;
    padding: 10px 12px;
    border: 1.5px solid;
    font-size: .78rem;
    line-height: 1.35;
    position: relative;
    min-height: 72px;
}
/* owned */
.album-card.owned {
    background: #f0fdf4;
    border-color: #86efac;
}
/* missing */
.album-card.missing {
    background: #fff;
    border-color: #e2e8f0;
    color: #94a3b8;
}
.card-number {
    font-size: .65rem; font-weight: 700;
    color: #94a3b8; display: block; margin-bottom:2px;
}
.card-name { font-weight: 600; color: #1e293b; display:block; }
.album-card.missing .card-name { color: #cbd5e1; }
.card-type-badge {
    display: inline-block;
    margin-top: 4px;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: .6rem;
    font-weight: 800;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.badge-ff   { background:#dbeafe; color:#1d4ed8; }
.badge-logo { background:#dcfce7; color:#15803d; }
.badge-icon { background:#fef9c3; color:#854d0e; }
.badge-hero { background:#f3e8ff; color:#7e22ce; }
.badge-rookie { background:#ffe4e6; color:#be123c; }
.badge-fav    { background:#ffedd5; color:#c2410c; }
.badge-eternal { background:#e0f2fe; color:#0369a1; }

/* qty bubble */
.qty-bubble {
    position: absolute; top:8px; right:8px;
    background:#22c55e; color:#fff;
    font-size:.6rem; font-weight:800;
    border-radius:99px; padding:1px 6px;
    line-height:1.4;
}
.qty-bubble.dup { background:#f97316; }

/* ── Country header ── */
.country-header {
    display:flex; align-items:center; gap:14px;
    background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:10px;
    padding:14px 20px; margin-bottom:14px;
}
.country-name { font-size:1.2rem; font-weight:800; color:#111827; }
.country-code { font-size:.8rem; color:#64748b; }

/* ── Country cards list ── */
.country-card-row {
    display:flex; align-items:center; gap:10px;
    padding: 7px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    border: 1px solid #e2e8f0;
    background: #fff;
    font-size: .85rem;
}
.country-card-row.owned-row { background:#f0fdf4; border-color:#86efac; }
.country-card-row.missing-row { background:#fff; color:#94a3b8; }
.cc-num { font-size:.7rem; color:#94a3b8; width:28px; flex-shrink:0; font-weight:700; }
.cc-name { flex:1; font-weight:600; color:#1e293b; }
.country-card-row.missing-row .cc-name { color:#cbd5e1; }
.cc-status { font-size:1rem; }

/* ── Dup table ── */
.dup-row {
    display:flex; align-items:center; gap:10px;
    padding:7px 12px; border-radius:6px; margin-bottom:4px;
    background:#fff7ed; border:1px solid #fed7aa;
    font-size:.85rem;
}
.dup-badge {
    background:#f97316; color:#fff;
    border-radius:4px; padding:2px 8px;
    font-size:.72rem; font-weight:800;
}

/* ── General ── */
div[data-testid="stButton"] button { border-radius:7px; font-weight:600; }
[data-testid="stDataFrame"] { border-radius:8px; overflow:hidden; }

/* override Streamlit dark scrollbar / metric bg */
[data-testid="metric-container"] { background:#f8fafc !important;
    border:1.5px solid #e2e8f0; border-radius:10px; padding:12px 16px; }
</style>
""", unsafe_allow_html=True)

# ─── Init DB ──────────────────────────────────────────────────────────────────
initialize_database()

# ─── Helpers ─────────────────────────────────────────────────────────────────

def pct_bar(pct: float) -> str:
    return (
        f'<div class="progress-wrap">'
        f'<div class="progress-fill" style="width:{pct}%"></div></div>'
    )


TYPE_BADGE = {
    "Fan Favourite": '<span class="card-type-badge badge-fav">Fan Fav</span>',
    "Icon":          '<span class="card-type-badge badge-icon">Icon</span>',
    "Hero":          '<span class="card-type-badge badge-hero">Hero</span>',
    "Master Rookie": '<span class="card-type-badge badge-rookie">Rookie</span>',
    "Eternos":       '<span class="card-type-badge badge-eternal">Eternos</span>',
}

COUNTRY_SPECIAL = {
    0: '<span class="card-type-badge badge-fav">Fan Fav</span>',
    1: '<span class="card-type-badge badge-logo">Logo</span>',
    2: '<span class="card-type-badge badge-icon">Icon</span>',
}


def card_type_badge(category: str) -> str:
    for key, html in TYPE_BADGE.items():
        if key.lower() in (category or "").lower():
            return html
    return ""


@st.cache_data(ttl=5)
def get_all_cards_for_album():
    """Return all catalog cards (owned + missing) ordered by card_number."""
    from database import get_db, _CARD_COLUMNS, _CARD_JOIN
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT {_CARD_COLUMNS} {_CARD_JOIN} ORDER BY c.card_number")
        return cur.fetchall()


def render_album_page(cards_on_page: list, page_num: int):
    """Render one album page as a 3×3 HTML grid.
    cards_on_page: list of DB tuples (num, name, cat, qty) OR None for empty slot.
    """
    items_html = ""
    for card in cards_on_page:
        if card is None:
            # true empty slot — shouldn't happen but guard anyway
            items_html += '<div class="album-card missing"><span class="card-number">—</span></div>'
            continue
        num, name, cat, qty = card[0], card[1], card[2] or "", card[3] or 0
        owned_cls = "owned" if qty > 0 else "missing"
        badge = card_type_badge(cat)
        qty_html = ""
        if qty == 1:
            qty_html = '<span class="qty-bubble">✓</span>'
        elif qty > 1:
            qty_html = f'<span class="qty-bubble dup">×{qty}</span>'

        items_html += (
            f'<div class="album-card {owned_cls}">'
            f'  {qty_html}'
            f'  <span class="card-number">#{num}</span>'
            f'  <span class="card-name">{name}</span>'
            f'  {badge}'
            f'</div>'
        )

    # pad last row to fill 3 cols
    remainder = len(cards_on_page) % 3
    if remainder:
        for _ in range(3 - remainder):
            items_html += '<div></div>'

    st.markdown(
        f'<div class="album-page-title">Strona {page_num}</div>'
        f'<div class="album-grid">{items_html}</div>',
        unsafe_allow_html=True,
    )


def render_country_cards(cards: list):
    """Render country card list with special-type labels for first 3."""
    html = ""
    for idx, r in enumerate(cards):
        num, name, cat, qty = r[0], r[1], r[2] or "", r[3] or 0
        owned_cls = "owned-row" if qty > 0 else "missing-row"
        status = "✅" if qty > 0 else "❌"
        badge = COUNTRY_SPECIAL.get(idx, "")
        qty_info = f'<span style="font-size:.7rem;color:#64748b">×{qty}</span>' if qty > 1 else ""
        html += (
            f'<div class="country-card-row {owned_cls}">'
            f'  <span class="cc-num">#{num}</span>'
            f'  <span class="cc-name">{name}</span>'
            f'  {badge}{qty_info}'
            f'  <span class="cc-status">{status}</span>'
            f'</div>'
        )
    st.markdown(html, unsafe_allow_html=True)


def show_country_detail(code: str):
    """Render full country breakdown — reused in Kraje page and Stats click."""
    cards = get_cards_by_country(code)
    cs    = get_country_stats(code)
    if cards == 0 or not cs:
        st.error("Nie znaleziono kraju.")
        return
    pct_c = cs["percentage"]
    st.markdown(
        f'<div class="country-header">'
        f'  <div>'
        f'    <div class="country-name">{cs["country"]}</div>'
        f'    <div class="country-code">{code.upper()}</div>'
        f'  </div>'
        f'  <div style="flex:1;margin-left:20px">'
        f'    {pct_bar(pct_c)}'
        f'    <small style="color:#64748b">{cs["owned"]}/{cs["total"]} kart · {pct_c}%</small>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Posiadane", cs["owned"])
    c2.metric("❌ Brakujące", cs["missing"])
    c3.metric("📦 Łącznie",  cs["total"])
    render_country_cards(cards)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ FIFA World Cup 2026")
    st.markdown("**Kolekcja kart**")
    st.markdown("**PANINI**")
    st.divider()

    page = st.radio(
        "Nawigacja",
        ["📊 Statystyki", "➕ Dodaj / Usuń", "🌍 Kraje", "📋 Posiadane", "❌ Brakujące", "🔁 Duplikaty"],
        label_visibility="collapsed",
    )

    st.divider()
    stats = get_stats()
    pct   = stats["percentage"]
    st.markdown("**Ukończenie albumu**")
    st.markdown(pct_bar(pct), unsafe_allow_html=True)
    st.markdown(f"<small style='color:#64748b'>{stats['owned']} / 630 · {pct}%</small>",
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STATYSTYKI
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Statystyki":
    st.title("📊 Statystyki kolekcji")

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, color in [
        (c1, "Posiadane",  stats["owned"],     "#2563eb"),
        (c2, "Brakujące",  stats["missing"],   "#dc2626"),
        (c3, "Ukończenie", f"{pct}%",          "#16a34a"),
        (c4, "Wszystkich", stats["all cards"], "#d97706"),
    ]:
        col.markdown(
            f'<div class="stat-card">'
            f'  <div class="stat-value" style="color:{color}">{val}</div>'
            f'  <div class="stat-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Postęp — kraje")
    st.caption("Kliknij wiersz, aby zobaczyć karty kraju.")

    country_rows = []
    for code, name in COUNTRIES.items():
        cs = get_country_stats(code)
        if cs:
            country_rows.append({
                "Kod": code, "Kraj": name,
                "Posiadane": cs["owned"], "Brakujące": cs["missing"],
                "Łącznie": cs["total"], "%": cs["percentage"],
            })

    if country_rows:
        df_c = pd.DataFrame(country_rows).sort_values("%", ascending=False)
        sel  = st.dataframe(
            df_c, use_container_width=True, hide_index=True,
            on_select="rerun", selection_mode="single-row",
            column_config={
                "%": st.column_config.ProgressColumn(
                    "Ukończenie", min_value=0, max_value=100, format="%.1f%%"),
                "Posiadane": st.column_config.NumberColumn("✅ Posiadane"),
                "Brakujące": st.column_config.NumberColumn("❌ Brakujące"),
            },
        )
        rows_sel = sel.selection.get("rows", [])
        if rows_sel:
            chosen_code = df_c.iloc[rows_sel[0]]["Kod"]
            st.divider()
            show_country_detail(chosen_code)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DODAJ / USUŃ
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Dodaj / Usuń":
    st.title("➕ Dodaj / Usuń karty")

    col_add, col_rem = st.columns(2)

    with col_add:
        st.subheader("Dodaj karty")
        add_input = st.text_input("Numery kart (spacja lub przecinek)", placeholder="np. 1 42 87 204")
        if st.button("✅ Dodaj", use_container_width=True):
            if add_input.strip():
                raw = add_input.replace(",", " ").split()
                new_cards, dup_cards, errors = [], [], []
                for tok in raw:
                    if tok.isdigit():
                        num = int(tok)
                        if 1 <= num <= 630:
                            is_new = add_card(num)
                            card   = get_card(num)
                            (new_cards if is_new else dup_cards).append(card)
                        else:
                            errors.append(tok)
                    else:
                        errors.append(tok)
                if new_cards:
                    st.success(f"Dodano {len(new_cards)} nowych kart")
                    rows = [{"#": c[0], "Nazwa": c[1], "Kategoria": c[2]} for c in new_cards]
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                if dup_cards:
                    st.info(f"{len(dup_cards)} duplikatów (zwiększono licznik)")
                    rows = [{"#": c[0], "Nazwa": c[1], "Sztuk": c[3]} for c in dup_cards]
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                if errors:
                    st.warning(f"Nierozpoznane: {', '.join(errors)}")
            else:
                st.warning("Wpisz co najmniej jeden numer.")

    with col_rem:
        st.subheader("Usuń karty")
        rem_input = st.text_input("Numery kart (spacja lub przecinek)", placeholder="np. 1 42 87", key="rem")
        if st.button("🗑️ Usuń", use_container_width=True):
            if rem_input.strip():
                raw = rem_input.replace(",", " ").split()
                removed = []
                for tok in raw:
                    if tok.isdigit():
                        num  = int(tok)
                        card = get_card(num)
                        remove_card(num)
                        if card:
                            removed.append(card)
                if removed:
                    st.success(f"Usunięto / zmniejszono licznik: {len(removed)} kart")
                    rows = [{"#": c[0], "Nazwa": c[1]} for c in removed]
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
            else:
                st.warning("Wpisz co najmniej jeden numer.")

    st.divider()
    st.subheader("🔍 Podgląd karty")
    lookup = st.number_input("Numer karty", min_value=1, max_value=630, step=1)
    if st.button("Sprawdź"):
        card = get_card(int(lookup))
        if card:
            qty    = card[3] or 0
            status = "✅ Posiadana" if qty > 0 else "❌ Brakująca"
            st.markdown(f"**#{card[0]}** · {card[1]}  \n"
                        f"Kategoria: `{card[2]}`  \n"
                        f"Status: {status} · Sztuk: **{qty}**")
        else:
            st.error("Nie znaleziono karty w katalogu.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: KRAJE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Kraje":
    st.title("🌍 Karty krajowe")

    # If a country was selected from the table, keep it in session state
    if "selected_country" not in st.session_state:
        st.session_state.selected_country = ""

    search = st.text_input(
        "Wyszukaj kraj (kod 3-literowy lub pełna nazwa)",
        value=st.session_state.selected_country,
        placeholder="np. POL lub Poland",
    )
    if search != st.session_state.selected_country:
        st.session_state.selected_country = search

    if search:
        if st.button("← Powrót do listy"):
            st.session_state.selected_country = ""
            st.rerun()
        show_country_detail(search)
    else:
        # Show country table; clicking a row fills the search
        st.caption("Kliknij wiersz, aby zobaczyć karty danego kraju.")
        country_grid = []
        for code, name in COUNTRIES.items():
            cs = get_country_stats(code)
            if cs:
                country_grid.append({
                    "Kod": code, "Kraj": name,
                    "Posiadane": cs["owned"], "Brakujące": cs["missing"],
                    "Ukończenie": cs["percentage"],
                })
        if country_grid:
            df_all = pd.DataFrame(country_grid)
            sel = st.dataframe(
                df_all, hide_index=True, use_container_width=True,
                on_select="rerun", selection_mode="single-row",
                column_config={
                    "Ukończenie": st.column_config.ProgressColumn(
                        "Ukończenie %", min_value=0, max_value=100, format="%.1f%%"),
                },
            )
            rows_sel = sel.selection.get("rows", [])
            if rows_sel:
                chosen_code = df_all.iloc[rows_sel[0]]["Kod"]
                st.session_state.selected_country = chosen_code
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: POSIADANE — pełny album grid z pustymi miejscami, 9 kart / strona
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Posiadane":
    st.title("📋 Album — podgląd kolekcji")

    all_cards = get_all_cards_for_album()

    if not all_cards:
        st.info("Baza kart jest pusta. Upewnij się że katalog jest załadowany.")
    else:
        owned_count = sum(1 for c in all_cards if (c[3] or 0) > 0)
        st.markdown(f"Posiadane: **{owned_count}** / {len(all_cards)} kart")

        PAGE_SIZE = 9
        # Obliczamy całkowitą liczbę pojedynczych stron
        total_single_pages = (len(all_cards) + PAGE_SIZE - 1) // PAGE_SIZE

        # Obliczamy liczbę "widoków" (rozkładówek).
        # Strona 1 to widok 1. Każdy kolejny widok mieści 2 strony.
        if total_single_pages <= 1:
            total_views = 1
        else:
            total_views = 1 + (total_single_pages - 1 + 1) // 2

        if "album_view" not in st.session_state:
            st.session_state.album_view = 1

        # ── Kontrola nawigacji (Widoki/Rozkładówki) ───────────────────────────
        col_prev, col_input, col_of, col_next = st.columns([1, 2, 2, 1])

        with col_prev:
            if st.button("◀", use_container_width=True,
                         disabled=st.session_state.album_view <= 1):
                st.session_state.album_view = max(1, st.session_state.album_view - 1)
                st.rerun()

        with col_input:
            entered = st.number_input(
                "Rozkładówka", min_value=1, max_value=total_views,
                value=st.session_state.album_view,
                step=1, label_visibility="collapsed",
            )
            if entered != st.session_state.album_view:
                st.session_state.album_view = int(entered)
                st.rerun()

        with col_of:
            st.markdown(
                f'<div style="padding:6px 4px;font-size:.85rem;color:#64748b">z {total_views}</div>',
                unsafe_allow_html=True,
            )

        with col_next:
            if st.button("▶", use_container_width=True,
                         disabled=st.session_state.album_view >= total_views):
                st.session_state.album_view = min(total_views, st.session_state.album_view + 1)
                st.rerun()

        # ── Logika wyznaczania stron dla danego widoku ───────────────────────
        cur_view = int(st.session_state.album_view)

        if cur_view == 1:
            # Pierwszy widok: tylko jedna strona po prawej
            pages_to_show = [1]
        else:
            # Kolejne widoki: np. widok 2 -> strony 2 i 3, widok 3 -> strony 4 i 5
            left_page = (cur_view - 1) * 2
            right_page = left_page + 1
            pages_to_show = [left_page, right_page]

        # Tworzymy dwie kolumny w Streamlicie dla lewej i prawej strony
        col_left_page, col_right_page = st.columns(2)

        first_card_idx = None
        last_card_idx = None

        # Renderowanie stron w układzie książkowym
        if cur_view == 1:
            # Pierwsza strona ląduje po prawej stronie, lewa zostaje pusta (okładka)
            with col_right_page:
                start = 0
                chunk = list(all_cards[start: start + PAGE_SIZE])
                if chunk:
                    render_album_page(chunk, 1)
                    first_card_idx = chunk[0][0]
                    last_card_idx = chunk[-1][0]
        else:
            # Lewa strona rozkładówki
            p_left = pages_to_show[0]
            with col_left_page:
                start_l = (p_left - 1) * PAGE_SIZE
                chunk_l = list(all_cards[start_l: start_l + PAGE_SIZE])
                if chunk_l:
                    render_album_page(chunk_l, p_left)
                    if first_card_idx is None:
                        first_card_idx = chunk_l[0][0]
                    last_card_idx = chunk_l[-1][0]
                else:
                    st.write("")  # Pusta strona jeśli brak kart

            # Prawa strona rozkładówki
            p_right = pages_to_show[1]
            if p_right <= total_single_pages:
                with col_right_page:
                    start_r = (p_right - 1) * PAGE_SIZE
                    chunk_r = list(all_cards[start_r: start_r + PAGE_SIZE])
                    if chunk_r:
                        render_album_page(chunk_r, p_right)
                        if first_card_idx is None:
                            first_card_idx = chunk_r[0][0]
                        last_card_idx = chunk_r[-1][0]

        # Stopka informacyjna o zakresie kart na ekranie
        if first_card_idx is not None and last_card_idx is not None:
            st.caption(f"Karty #{first_card_idx}–#{last_card_idx}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BRAKUJĄCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "❌ Brakujące":
    st.title("❌ Brakujące karty")

    missing = get_missing()
    if not missing:
        st.success("🎉 Album ukończony! Nie brakuje żadnej karty.")
    else:
        st.markdown(f"Brakujących kart: **{len(missing)}**")
        df = pd.DataFrame([{"#": r[0], "Nazwa": r[1], "Kategoria": r[2]} for r in missing])

        cats = ["Wszystkie"] + sorted(df["Kategoria"].dropna().unique().tolist())
        cat_filter  = st.selectbox("Filtruj po kategorii", cats)
        search_name = st.text_input("Szukaj po nazwie", "")

        if cat_filter != "Wszystkie":
            df = df[df["Kategoria"] == cat_filter]
        if search_name:
            df = df[df["Nazwa"].str.contains(search_name, case=False, na=False)]

        st.dataframe(df, hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DUPLIKATY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔁 Duplikaty":
    st.title("🔁 Duplikaty")

    duplicates = get_duplicates()
    if not duplicates:
        st.info("Brak duplikatów.")
    else:
        total_extra = sum(r[3] - 1 for r in duplicates)
        c1, c2 = st.columns(2)
        c1.metric("Rodzajów kart z duplikatem", len(duplicates))
        c2.metric("Kart do wymiany łącznie",    total_extra)

        st.markdown("<br>", unsafe_allow_html=True)

        html = ""
        for r in duplicates:
            num, name, cat, qty = r[0], r[1], r[2] or "", r[3]
            extra = qty - 1
            badge = card_type_badge(cat)
            html += (
                f'<div class="dup-row">'
                f'  <span style="font-size:.7rem;color:#94a3b8;width:28px;flex-shrink:0;font-weight:700">#{num}</span>'
                f'  <span style="flex:1;font-weight:600;color:#1e293b">{name}</span>'
                f'  {badge}'
                f'  <span class="dup-badge">+{extra} do wymiany</span>'
                f'</div>'
            )
        st.markdown(html, unsafe_allow_html=True)