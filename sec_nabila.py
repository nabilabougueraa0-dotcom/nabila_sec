import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SEC Capture CO₂", page_icon="🌬️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0f1117; color: #c9d6df; }
h1,h2,h3 { font-family: 'IBM Plex Mono', monospace; color: #e8f4f8; }
.card {
    background: linear-gradient(135deg, #1a2332, #16202e);
    border: 1px solid #2a3f55; border-left: 4px solid #00b4d8;
    border-radius: 8px; padding: 18px 22px; margin: 10px 0;
    font-family: 'IBM Plex Mono', monospace;
}
.card.total { border-left-color: #f77f00; background: linear-gradient(135deg,#1f1a0f,#1a1608); }
.card-label { font-size:0.75rem; letter-spacing:0.12em; text-transform:uppercase; color:#6b8fa3; margin-bottom:4px; }
.card-value { font-size:1.9rem; font-weight:600; color:#e8f4f8; }
.card-unit  { font-size:0.8rem; color:#6b8fa3; margin-top:2px; }
.sec-header {
    font-family:'IBM Plex Mono',monospace; font-size:0.7rem; letter-spacing:0.18em;
    text-transform:uppercase; color:#00b4d8; border-bottom:1px solid #1e3448;
    padding-bottom:6px; margin:26px 0 14px 0;
}
.row { display:flex; justify-content:space-between; padding:8px 0;
       border-bottom:1px solid #1a2a3a; font-size:0.87rem; color:#8aa5bc; }
.val { font-family:'IBM Plex Mono',monospace; color:#c9d6df; font-weight:600; }
.info { background:#111827; border:1px solid #1e3448; border-radius:6px;
        padding:13px 17px; font-size:0.81rem; color:#6b8fa3; margin:8px 0; line-height:1.65; }
.err  { background:#1f0a0a; border:1px solid #8b1a1a; border-radius:6px;
        padding:12px 16px; color:#ff6b6b; font-size:0.85rem; }
.formula { background:#0a1628; border:1px solid #1e3448; border-radius:6px;
           padding:12px 16px; font-family:'IBM Plex Mono',monospace;
           font-size:0.82rem; color:#48cae4; margin:8px 0; }
.stButton>button {
    background:#00b4d8; color:#0f1117; font-family:'IBM Plex Mono',monospace;
    font-weight:600; border:none; border-radius:4px; padding:10px 28px; width:100%;
}
.stButton>button:hover { background:#48cae4; }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("# 🌬️ SEC Capture CO₂ — 8 760 valeurs horaires")

st.markdown("""<div class="formula">
  CI(h) = C*_CO₂(h) [kg/m³] = [SP(h) − RH(h)/100 · 610.94 · exp(17.625·T/(T+243.04))] · x_CO₂ · M_CO₂ / (R · T_K)<br>
  SEC_elec(h) [kWh/t] = ΔP · (1+ε) / (η_elec · CI(h) · α · 3600)<br>
  SEC_th(h)   [kWh/t] = SEC_th[GJ/t] · 277.778 · (T_cible − T_a(h)) / (η_th · T_cible)<br>
  SEC_total(h) = SEC_elec(h) + SEC_th(h)
</div>""", unsafe_allow_html=True)

# ── Paramètres ────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">⚙️ Paramètres</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Électrique**")
    delta_P  = st.number_input("ΔP ventilateur (Pa)",  10.0,  5000.0, 236.8,  1.0)
    eps_pct  = st.number_input("ε — pertes auxiliaires (%)", 0.0, 50.0, 15.0, 0.5)
    eta_elec = st.number_input("η_elec", 0.1, 1.0, 0.75, 0.01)
    alpha    = st.number_input("α — taux capture CO₂", 0.01, 1.0, 0.70, 0.01)

with c2:
    st.markdown("**CO₂**")
    x_CO2    = st.number_input("x_CO₂ — fraction molaire", 0.0001, 0.20, 0.0004, 0.0001, format="%.4f",
                                help="400 ppm = 0.0004")
    SEC_th_GJ = st.selectbox("SEC_th [GJ/t CO₂]", [2, 3, 4], index=1)
    T_cible   = st.number_input("T_cible (°C)", 50.0, 1200.0, 100.0, 10.0)

with c3:
    st.markdown("**Thermique**")
    eta_th   = st.number_input("η_th", 0.1, 1.0, 0.45, 0.01,
                                help="0.4–0.5 si T~100°C | 0.85–0.95 si T~1000°C")

# ── Vérification heure 1 ──────────────────────────────────────────────────────
st.markdown('<div class="sec-header">🔢 Vérification — Heure 1 (T=7.69°C, RH=59.13%, SP=95490 Pa)</div>',
            unsafe_allow_html=True)

M_CO2_gmol = 44.011
R          = 8.314

Tc_v = 7.69; RH_v = 59.13; SP_v = 95490.0
Tk_v = Tc_v + 273.15
Pv_v = (RH_v/100.0)*(610.94*np.exp(17.625*Tc_v/(Tc_v+243.04)))
CI_v = ((SP_v - Pv_v)*x_CO2*M_CO2_gmol)/(R*Tk_v) / 1000.0   # kg/m³
SEC_elec_v = (delta_P*(1+eps_pct/100)) / (eta_elec*CI_v*alpha*3600)
SEC_th_v   = float(SEC_th_GJ)*277.778*(T_cible-(Tc_v))/(eta_th*T_cible)
SEC_tot_v  = SEC_elec_v + SEC_th_v

cv1, cv2, cv3, cv4 = st.columns(4)
with cv1:
    st.markdown(f'<div class="card"><div class="card-label">CI = C*_CO₂</div>'
                f'<div class="card-value">{CI_v:.7f}</div>'
                f'<div class="card-unit">kg/m³</div></div>', unsafe_allow_html=True)
with cv2:
    st.markdown(f'<div class="card"><div class="card-label">SEC_elec</div>'
                f'<div class="card-value">{SEC_elec_v:.4f}</div>'
                f'<div class="card-unit">kWh/t CO₂</div></div>', unsafe_allow_html=True)
with cv3:
    st.markdown(f'<div class="card"><div class="card-label">SEC_th</div>'
                f'<div class="card-value">{SEC_th_v:.4f}</div>'
                f'<div class="card-unit">kWh/t CO₂</div></div>', unsafe_allow_html=True)
with cv4:
    st.markdown(f'<div class="card total"><div class="card-label">SEC_total</div>'
                f'<div class="card-value">{SEC_tot_v:.4f}</div>'
                f'<div class="card-unit">kWh/t CO₂</div></div>', unsafe_allow_html=True)

# ── Import fichier ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">📂 Import fichier 8 760 lignes</div>', unsafe_allow_html=True)
st.markdown('<div class="info">'
            'Colonnes : <b>T2m</b> (°C) · <b>SP</b> (Pa = P_atm) · <b>RH</b> (%)'
            '</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Fichier Excel (.xlsx) ou CSV (.csv)", type=["xlsx","xls","csv"])

if uploaded:
    try:
        df = pd.read_csv(uploaded, sep=None, engine="python") if uploaded.name.endswith(".csv") \
             else pd.read_excel(uploaded)
    except Exception as e:
        st.markdown(f'<div class="err">❌ Erreur lecture : {e}</div>', unsafe_allow_html=True)
        st.stop()

    df.columns = [c.strip().upper() for c in df.columns]

    aliases = {
        "T":  ["T", "T2M", "TEMP", "TEMPERATURE", "TAIR"],
        "SP": ["SP", "PRESSURE", "PRESSION", "PATM", "P_ATM"],
        "RH": ["RH", "HR", "HUMIDITY", "HUMIDITE"],
    }
    col_map = {}
    for var, names in aliases.items():
        for name in names:
            if name in df.columns:
                col_map[var] = name
                break

    missing = [v for v in ["T","SP","RH"] if v not in col_map]
    if missing:
        st.markdown(f'<div class="info">⚠️ Colonnes non détectées : <b>{", ".join(missing)}</b></div>',
                    unsafe_allow_html=True)
        for var in missing:
            col_map[var] = st.selectbox(f"Colonne pour {var}", list(df.columns), key=f"sel_{var}")

    st.markdown('<div class="sec-header">👁️ Aperçu</div>', unsafe_allow_html=True)
    st.dataframe(df[[col_map[v] for v in ["T","SP","RH"]]].head(10), use_container_width=True)

    n = len(df)
    st.markdown(f'<div class="row"><span>Lignes lues</span><span class="val">{n:,} heures</span></div>',
                unsafe_allow_html=True)
    if n != 8760:
        st.markdown(f'<div class="info">⚠️ {n} lignes (attendu 8 760).</div>', unsafe_allow_html=True)

    if st.button("▶ Calculer les 8 760 SEC"):
        try:
            Tc = df[col_map["T"]].astype(float).values
            SP = df[col_map["SP"]].astype(float).values
            RH = df[col_map["RH"]].astype(float).values
            Tk = Tc + 273.15
            eps = eps_pct / 100.0

            # ── CI = C*_CO₂ (kg/m³) ──────────────────────────────────────────
            Pv   = (RH/100.0)*(610.94*np.exp(17.625*Tc/(Tc+243.04)))
            CI_h = ((SP - Pv)*x_CO2*M_CO2_gmol)/(R*Tk) / 1000.0   # kg/m³
            CI_h = np.where(CI_h <= 0, np.nan, CI_h)

            # ── SEC_elec(h) ───────────────────────────────────────────────────
            # ΔP·(1+ε) / (η_elec · CI[kg/m³] · α · 3600)
            SEC_elec_h = (delta_P*(1+eps)) / (eta_elec*CI_h*alpha*3600.0)

            # ── SEC_th(h) ─────────────────────────────────────────────────────
            # SEC_th[GJ/t] · 277.778 · (T_cible - T_a(h)) / (η_th · T_cible)
            SEC_th_h = float(SEC_th_GJ)*277.778*(T_cible - Tc)/(eta_th*T_cible)

            # ── SEC_total(h) ──────────────────────────────────────────────────
            SEC_tot_h = SEC_elec_h + SEC_th_h

            # ── Table résultats ───────────────────────────────────────────────
            results_df = pd.DataFrame({
                "Heure":             np.arange(1, n+1),
                "T2m (°C)":          np.round(Tc, 2),
                "SP / P_atm (Pa)":   np.round(SP, 1),
                "RH (%)":            np.round(RH, 2),
                "CI = C*_CO₂ (kg/m³)": np.round(CI_h, 7),
                "SEC_elec (kWh/t)":  np.round(SEC_elec_h, 4),
                "SEC_th (kWh/t)":    np.round(SEC_th_h, 4),
                "SEC_total (kWh/t)": np.round(SEC_tot_h, 4),
            })

            # ── Statistiques ──────────────────────────────────────────────────
            st.markdown('<div class="sec-header">📊 Statistiques annuelles</div>', unsafe_allow_html=True)
            ca, cb, cc = st.columns(3)
            for col_ui, label, arr in [
                (ca, "CI (kg/m³)",       CI_h),
                (cb, "SEC_elec (kWh/t)", SEC_elec_h),
                (cc, "SEC_th (kWh/t)",   SEC_th_h),
            ]:
                with col_ui:
                    st.markdown(f"**{label}**")
                    for stat, fn in [("Moyenne", np.nanmean), ("Min", np.nanmin), ("Max", np.nanmax)]:
                        st.markdown(f'<div class="row"><span>{stat}</span>'
                                    f'<span class="val">{fn(arr):.4f}</span></div>',
                                    unsafe_allow_html=True)

            # ── Cards SEC total ───────────────────────────────────────────────
            st.markdown('<div class="sec-header">🎯 SEC Total — 8 760 h</div>', unsafe_allow_html=True)
            r1, r2, r3 = st.columns(3)
            with r1:
                st.markdown(f'<div class="card"><div class="card-label">Moyenne annuelle</div>'
                            f'<div class="card-value">{np.nanmean(SEC_tot_h):.4f}</div>'
                            f'<div class="card-unit">kWh / t CO₂</div></div>', unsafe_allow_html=True)
            with r2:
                st.markdown(f'<div class="card"><div class="card-label">Minimum</div>'
                            f'<div class="card-value">{np.nanmin(SEC_tot_h):.4f}</div>'
                            f'<div class="card-unit">kWh / t CO₂</div></div>', unsafe_allow_html=True)
            with r3:
                st.markdown(f'<div class="card total"><div class="card-label">Maximum</div>'
                            f'<div class="card-value">{np.nanmax(SEC_tot_h):.4f}</div>'
                            f'<div class="card-unit">kWh / t CO₂</div></div>', unsafe_allow_html=True)

            # ── Tableau 8760 ──────────────────────────────────────────────────
            st.markdown('<div class="sec-header">📄 Les 8 760 valeurs horaires</div>', unsafe_allow_html=True)
            st.dataframe(results_df, use_container_width=True, height=420)

            # ── Export CSV ────────────────────────────────────────────────────
            csv_out = results_df.to_csv(index=False, float_format="%.4f").encode("utf-8")
            st.download_button("⬇️ Télécharger CSV — 8 760 résultats",
                               csv_out, "SEC_8760_resultats.csv", "text/csv")

        except Exception as e:
            st.markdown(f'<div class="err">❌ Erreur : {e}</div>', unsafe_allow_html=True)
            import traceback
            st.code(traceback.format_exc())

else:
    st.markdown('<div class="info" style="text-align:center;padding:32px;">'
                '⬆️ Importez votre fichier Excel ou CSV avec T2m, SP, RH — 8 760 lignes.'
                '</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="font-size:0.73rem;color:#3a5068;font-family:\'IBM Plex Mono\',monospace;text-align:center;">'
            'SEC Capture CO₂ · CI=C*_CO₂ · ΔP·(1+ε)/(η·CI·α·3600) · 8 760 h</p>',
            unsafe_allow_html=True)