import streamlit as st

def generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10,
                   marksman_t10, infantry_percent, lancer_percent, marksman_percent, pet_buff, city_buff, minister_buff):
    if infantry_percent + lancer_percent + marksman_percent != 100:
        raise ValueError("The total percentage must equal 100%.")

    # Apply selected buffs to max march size
    total_buff_percent = city_buff
    effective_march_size = int(max_march_size * (1 + total_buff_percent / 100) + minister_buff + pet_buff)

    total_troops = {
        'infantry': (infantry_t11 or 0) + (infantry_t10 or 0),
        'lancer': (lancer_t11 or 0) + (lancer_t10 or 0),
        'marksman': (marksman_t11 or 0) + (marksman_t10 or 0)
    }

    marches = [{'infantry': 0, 'lancer': 0, 'marksman': 0, 'total': 0} for _ in range(num_marches)]

    for march in marches:
        total_capacity = effective_march_size

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

def buffs_section():
    st.subheader('Buffs')
    pet_buff = st.number_input('Pet Buff (Exact Number)', min_value=0, max_value=50000, value=0, step=100, format="%d")

    city_buff_10 = st.checkbox('Apply 10% City Buff')
    city_buff_20 = st.checkbox('Apply 20% City Buff')
    city_buff = 0
    if city_buff_10 and city_buff_20:
        st.error('You cannot select both 10% and 20% City Buff. Please choose one.')
    elif city_buff_10:
        city_buff = 10
    elif city_buff_20:
        city_buff = 20

    minister_buff_enabled = st.checkbox('Apply Minister of Strategy Buff (2500 Flat Bonus)')
    minister_buff = 2500 if minister_buff_enabled else 0

    return  pet_buff, city_buff, minister_buff

def main():
    st.set_page_config(page_title="Troop Manager", layout="centered")
    st.title('Troop Formation Builder & Ratio Optimizer')

    pet_buff, city_buff, minister_buff = buffs_section()

    st.header("March Setup")
    num_marches = st.selectbox('Number of Marches', options=[1, 2, 3, 4, 5, 6, 7], index=0)
    max_march_size = st.number_input('Max March Size', min_value=1, value=1000, format="%d")

    st.subheader('T11 Troops')
    infantry_t11 = st.number_input('Infantry T11', min_value=0, value=0, format="%d")
    lancer_t11 = st.number_input('Lancer T11', min_value=0, value=0, format="%d")
    marksman_t11 = st.number_input('Marksman T11', min_value=0, value=0, format="%d")

    st.subheader('T10 Troops')
    infantry_t10 = st.number_input('Infantry T10', min_value=0, value=0, format="%d")
    lancer_t10 = st.number_input('Lancer T10', min_value=0, value=0, format="%d")
    marksman_t10 = st.number_input('Marksman T10', min_value=0, value=0, format="%d")

    st.header("Generate Marches")
    infantry_percent = st.number_input('Infantry %', min_value=0.0, max_value=100.0, value=33.33, step=0.01, format="%.2f")
    lancer_percent = st.number_input('Lancer %', min_value=0.0, max_value=100.0, value=33.33, step=0.01, format="%.2f")
    marksman_percent = st.number_input('Marksman %', min_value=0.0, max_value=100.0, value=33.33, step=0.01, format="%.2f")

    if st.button('Generate Marches'):
        try:
            marches = generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11,
                                      infantry_t10, lancer_t10, marksman_t10, infantry_percent, lancer_percent,
                                      marksman_percent, pet_buff, city_buff, minister_buff)
            st.write('### March Formation Results')
            for i, march in enumerate(marches, 1):
                st.write(f"March {i}: Infantry={march['infantry']}, Lancer={march['lancer']}, Marksman={march['marksman']}, Total={march['total']}")
        except ValueError as e:
            st.error(str(e))

    st.header("Optimize Ratios")
    ratio_type = st.selectbox('Select Ratio Type', ['Bear']) # Add more options here

    if st.button('Optimize Ratios'):
        optimized_ratio = optimize_ratio(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11,
                                         infantry_t10, lancer_t10, marksman_t10, ratio_type,
                                         pet_buff, city_buff, minister_buff)
        st.write('### Optimized Troop Ratios')
        for troop_type, percent in optimized_ratio.items():
            st.write(f"{troop_type.capitalize()}: {percent:.2f}%")

def optimize_ratio(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10,
                   marksman_t10, ratio_type, pet_buff, city_buff, minister_buff):

    total_buff_percent = city_buff
    effective_march_size = int(max_march_size * (1 + total_buff_percent / 100) + minister_buff + pet_buff)

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
    max_total_troops = num_marches * effective_march_size

    adjusted_troops = {'infantry': 0, 'lancer': 0, 'marksman': 0}
    remaining_capacity = max_total_troops

    for troop_type in selected_priority:
        if total_troops[troop_type] > 0 and remaining_capacity > 0:
            allocated = min(total_troops[troop_type], remaining_capacity)
            adjusted_troops[troop_type] = allocated
            remaining_capacity -= allocated

    total_allocated = sum(adjusted_troops.values())
    if total_allocated > 0:
        optimized_ratio = {t: round((adjusted_troops[t] / total_allocated * 100), 2) for t in adjusted_troops}
    else:
        optimized_ratio = {t: 0 for t in adjusted_troops}

    return optimized_ratio

if __name__ == '__main__':
    main()
