import streamlit as st

def generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10,
                   marksman_t10, infantry_percent, lancer_percent, marksman_percent):
    if infantry_percent + lancer_percent + marksman_percent != 100:
        raise ValueError("The total percentage must equal 100%.")

    total_troops = {
        'infantry': (infantry_t11 or 0) + (infantry_t10 or 0),
        'lancer': (lancer_t11 or 0) + (lancer_t10 or 0),
        'marksman': (marksman_t11 or 0) + (marksman_t10 or 0)
    }

    marches = [{'infantry': 0, 'lancer': 0, 'marksman': 0, 'total': 0} for _ in range(num_marches)]

    for march in marches:
        total_capacity = max_march_size

        infantry_troops = int((infantry_percent / 100) * total_capacity)
        lancer_troops = int((lancer_percent / 100) * total_capacity)
        marksman_troops = int((marksman_percent / 100) * total_capacity)

        march['infantry'] = min(infantry_troops, total_troops['infantry'])
        march['lancer'] = min(lancer_troops, total_troops['lancer'])
        march['marksman'] = min(marksman_troops, total_troops['marksman'])

        march['total'] = march['infantry'] + march['lancer'] + march['marksman']

        total_troops['infantry'] -= march['infantry']
        total_troops['lancer'] -= march['lancer']
        total_troops['marksman'] -= march['marksman']

    return marches

def optimize_ratio(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10,
                   marksman_t10, ratio_type):
    total_troops = {
        'infantry': (infantry_t11 or 0) + (infantry_t10 or 0),
        'lancer': (lancer_t11 or 0) + (lancer_t10 or 0),
        'marksman': (marksman_t11 or 0) + (marksman_t10 or 0)
    }

    ratios = {
        'Bear': ['marksman', 'lancer', 'infantry'],
        'Balanced': ['infantry', 'lancer', 'marksman'],
        'Infantry Focus': ['infantry', 'lancer', 'marksman']
    }

    selected_priority = ratios.get(ratio_type, ratios['Balanced'])
    max_total_troops = num_marches * max_march_size

    adjusted_troops = {'infantry': 0, 'lancer': 0, 'marksman': 0}
    remaining_capacity = max_total_troops

    for troop_type in selected_priority:
        if total_troops[troop_type] > 0 and remaining_capacity > 0:
            allocated = min(total_troops[troop_type], remaining_capacity)
            adjusted_troops[troop_type] = allocated
            remaining_capacity -= allocated

    if remaining_capacity > 0:
        total_available = sum(total_troops[t] for t in selected_priority)
        if total_available > 0:
            for troop_type in selected_priority:
                if total_troops[troop_type] > 0:
                    extra_allocation = min(int((total_troops[troop_type] / total_available) * remaining_capacity), total_troops[troop_type])
                    adjusted_troops[troop_type] += extra_allocation
                    remaining_capacity -= extra_allocation

    total_allocated = sum(adjusted_troops.values())
    if total_allocated > 0:
        optimized_ratio = {t: round((adjusted_troops[t] / total_allocated * 100), 2) for t in adjusted_troops}
    else:
        optimized_ratio = {t: 0 for t in adjusted_troops}

    return optimized_ratio

def generate_marches_page():
    st.title('Troop Formation Builder')

    num_marches = st.selectbox('Number of Marches', options=[1, 2, 3, 4, 5, 6, 7], index=0)
    max_march_size = st.number_input('Max March Size', min_value=1, value=1000, format="%d")

    st.subheader('T11 Troops')
    infantry_t11 = st.number_input('Infantry T11', min_value=0, value=None, format="%d")
    lancer_t11 = st.number_input('Lancer T11', min_value=0, value=None, format="%d")
    marksman_t11 = st.number_input('Marksman T11', min_value=0, value=None, format="%d")

    st.subheader('T10 Troops')
    infantry_t10 = st.number_input('Infantry T10', min_value=0, value=None, format="%d")
    lancer_t10 = st.number_input('Lancer T10', min_value=0, value=None, format="%d")
    marksman_t10 = st.number_input('Marksman T10', min_value=0, value=None, format="%d")

    st.subheader('Troop Percentage Allocation')
    infantry_percent = st.number_input('Infantry %', min_value=0.0, max_value=100.0, value=33.33, step=0.01, format="%.2f")
    lancer_percent = st.number_input('Lancer %', min_value=0.0, max_value=100.0, value=33.33, step=0.01, format="%.2f")
    marksman_percent = st.number_input('Marksman %', min_value=0.0, max_value=100.0, value=33.33, step=0.01, format="%.2f")

    if st.button('Generate Marches'):
        try:
            marches = generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10, marksman_t10, infantry_percent, lancer_percent, marksman_percent)
            st.write('### March Formation Results')
            for i, march in enumerate(marches, 1):
                st.write(f"March {i}: Infantry={march['infantry']}, Lancer={march['lancer']}, Marksman={march['marksman']}, Total={march['total']}")
        except ValueError as e:
            st.error(str(e))

def optimize_ratios_page():
    st.title('Troop Ratio Optimizer')

    num_marches = st.selectbox('Number of Marches', options=[1, 2, 3, 4, 5, 6, 7], index=0)
    max_march_size = st.number_input('Max March Size', min_value=1, value=1000, format="%d")

    st.subheader('T11 Troops')
    infantry_t11 = st.number_input('Infantry T11', min_value=0, value=None, format="%d")
    lancer_t11 = st.number_input('Lancer T11', min_value=0, value=None, format="%d")
    marksman_t11 = st.number_input('Marksman T11', min_value=0, value=None, format="%d")

    st.subheader('T10 Troops')
    infantry_t10 = st.number_input('Infantry T10', min_value=0, value=None, format="%d")
    lancer_t10 = st.number_input('Lancer T10', min_value=0, value=None, format="%d")
    marksman_t10 = st.number_input('Marksman T10', min_value=0, value=None, format="%d")

    ratio_type = st.selectbox('Select Ratio Type', ['Bear',]) #TODO add more options

    if st.button('Optimize Ratios'):
        optimized_ratio = optimize_ratio(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10, marksman_t10, ratio_type)
        st.write('### Optimized Troop Ratios')
        for troop_type, percent in optimized_ratio.items():
            st.write(f"{troop_type.capitalize()}: {percent:.2f}%")

def main():
    st.set_page_config(page_title="Troop Management", layout="centered")
    page = st.sidebar.radio("Select a Page", ["Generate Marches", "Optimize Ratios"])

    if page == "Generate Marches":
        generate_marches_page()
    else:
        optimize_ratios_page()

if __name__ == '__main__':
    main()
