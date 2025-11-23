import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="GetAround - Analyse des Retards",
    layout="wide"
)

# Titre principal
st.title("GetAround - Analyse des Retards")
st.markdown("""
Ce dashboard aide le Product Manager à décider :
- **Seuil** : Quelle durée minimale entre deux locations ?
- **Portée** : Toutes les voitures ou Connect uniquement ?
""")

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_excel('get_around_delay_analysis.xlsx')
    return df

df = load_data()

# Sidebar - Filtres
st.sidebar.header("⚙️ Paramètres")
scope = st.sidebar.radio("Portée (Scope)", ["All", "Connect only"])
threshold = st.sidebar.slider("Seuil (minutes)", 0, 360, 120, step=30)

# Filtrage selon le scope
if scope == "Connect only":
    df_filtered = df[df['checkin_type'] == 'connect']
else:
    df_filtered = df

# Section 1 : Vue d'ensemble
st.header("Vue d'ensemble")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total locations", len(df_filtered))
with col2:
    ended = len(df_filtered[df_filtered['state'] == 'ended'])
    st.metric("Locations terminées", ended)
with col3:
    canceled = len(df_filtered[df_filtered['state'] == 'canceled'])
    st.metric("Locations annulées", canceled)
with col4:
    pct_canceled = 100 * canceled / len(df_filtered)
    st.metric("% Annulées", f"{pct_canceled:.1f}%")

# Section 2 : Fréquence des retards
st.header("Fréquence des retards")

ended_df = df_filtered[df_filtered['state'] == 'ended']
with_delay = ended_df[ended_df['delay_at_checkout_in_minutes'].notna()].copy()
with_delay['is_late'] = with_delay['delay_at_checkout_in_minutes'] > 0

col1, col2 = st.columns(2)

with col1:
    late_count = with_delay['is_late'].sum()
    late_pct = 100 * late_count / len(with_delay)
    st.metric("% En retard", f"{late_pct:.1f}%")
    
    # Distribution des retards
    delay_filtered = with_delay[
        (with_delay['delay_at_checkout_in_minutes'] >= -200) & 
        (with_delay['delay_at_checkout_in_minutes'] <= 500)
    ]
    fig = px.histogram(
        delay_filtered, 
        x='delay_at_checkout_in_minutes',
        nbins=50,
        title="Distribution des retards au checkout",
        labels={'delay_at_checkout_in_minutes': 'Retard (minutes)'}
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="À l'heure")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Retards par type de checkin
    if scope == "All":
        late_by_type = with_delay.groupby('checkin_type')['is_late'].mean() * 100
        fig2 = px.bar(
            x=late_by_type.index, 
            y=late_by_type.values,
            title="% de retards par type de checkin",
            labels={'x': 'Type de checkin', 'y': '% en retard'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Filtré sur Connect uniquement")
    
    # Tableau des seuils
    st.subheader("Retards par seuil")
    thresholds_list = [0, 15, 30, 60, 90, 120, 180, 240, 300, 360]
    results = []
    for t in thresholds_list:
        count = (with_delay['delay_at_checkout_in_minutes'] > t).sum()
        pct = 100 * count / len(with_delay)
        results.append({'Seuil (min)': t, 'Nb retards': count, '% retards': f"{pct:.1f}%"})
    st.dataframe(pd.DataFrame(results), hide_index=True)

# Section 3 : Impact sur le conducteur suivant
st.header("Impact sur le conducteur suivant")

# Préparation des données consécutives
consecutive = df_filtered[df_filtered['previous_ended_rental_id'].notna()].copy()
prev_delays = df[['rental_id', 'delay_at_checkout_in_minutes']].copy()
prev_delays.columns = ['previous_ended_rental_id', 'previous_delay']
consecutive = consecutive.merge(prev_delays, on='previous_ended_rental_id', how='left')

with_data = consecutive[
    consecutive['previous_delay'].notna() & 
    consecutive['time_delta_with_previous_rental_in_minutes'].notna()
].copy()

with_data['is_impacted'] = with_data['previous_delay'] > with_data['time_delta_with_previous_rental_in_minutes']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Locations consécutives", len(with_data))
with col2:
    impacted = with_data['is_impacted'].sum()
    st.metric("Cas problématiques", impacted)
with col3:
    pct_impacted = 100 * impacted / len(with_data) if len(with_data) > 0 else 0
    st.metric("% Impactés", f"{pct_impacted:.1f}%")

# Section 4 : Simulation du seuil
st.header(f"Simulation avec seuil = {threshold} min")

def simulate_threshold(data, thresh):
    problematic = data[data['previous_delay'] > data['time_delta_with_previous_rental_in_minutes']]
    resolved = data[
        (data['time_delta_with_previous_rental_in_minutes'] < thresh) & 
        (data['previous_delay'] > data['time_delta_with_previous_rental_in_minutes'])
    ]
    blocked = data[data['time_delta_with_previous_rental_in_minutes'] < thresh]
    
    return {
        'problematic': len(problematic),
        'resolved': len(resolved),
        'pct_resolved': 100 * len(resolved) / len(problematic) if len(problematic) > 0 else 0,
        'blocked': len(blocked),
        'pct_blocked': 100 * len(blocked) / len(data) if len(data) > 0 else 0
    }

result = simulate_threshold(with_data, threshold)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Cas problématiques", result['problematic'])
with col2:
    st.metric("Cas résolus", result['resolved'])
with col3:
    st.metric("% Résolus", f"{result['pct_resolved']:.1f}%")
with col4:
    st.metric("Locations bloquées", result['blocked'], delta=f"{result['pct_blocked']:.1f}%", delta_color="inverse")

# Graphique comparatif des seuils
st.subheader("Comparaison des seuils")

thresholds_sim = [0, 30, 60, 90, 120, 150, 180, 210, 240, 300, 360]
sim_results = [simulate_threshold(with_data, t) for t in thresholds_sim]
df_sim = pd.DataFrame(sim_results)
df_sim['threshold'] = thresholds_sim

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df_sim['threshold'], y=df_sim['pct_resolved'], mode='lines+markers', name='% Cas résolus'))
fig3.add_trace(go.Scatter(x=df_sim['threshold'], y=df_sim['pct_blocked'], mode='lines+markers', name='% Locations bloquées'))
fig3.add_vline(x=threshold, line_dash="dash", line_color="green", annotation_text=f"Seuil choisi: {threshold} min")
fig3.update_layout(
    title="Trade-off : Efficacité vs Impact",
    xaxis_title="Seuil (minutes)",
    yaxis_title="Pourcentage",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
st.plotly_chart(fig3, use_container_width=True)

# Section 5 : Impact sur le revenu
st.header("Impact sur le revenu")

total_ended = len(df[df['state'] == 'ended'])
blocked_count = result['blocked']
pct_of_total = 100 * blocked_count / total_ended

col1, col2 = st.columns(2)
with col1:
    st.metric("Locations potentiellement perdues", blocked_count)
with col2:
    st.metric("% du total des locations", f"{pct_of_total:.2f}%")

st.info(f"""
**Interprétation** : Avec un seuil de **{threshold} minutes** et une portée **{scope}**, 
environ **{blocked_count} locations** ({pct_of_total:.2f}% du total) seraient bloquées, 
représentant une perte de revenu potentielle.
""")

# Section 6 : Recommandations
st.header("Recommandations")

st.markdown(f"""
### Configuration actuelle : Seuil = {threshold} min, Portée = {scope}

- **Cas résolus** : {result['pct_resolved']:.1f}% des cas problématiques
- **Impact** : {result['pct_blocked']:.1f}% des locations consécutives bloquées
- **Perte revenu estimée** : {pct_of_total:.2f}% du total

### Recommandation finale
- **Seuil** : 120 minutes (bon compromis efficacité/impact)
- **Portée** : Connect uniquement (pilote avant déploiement global)
""")