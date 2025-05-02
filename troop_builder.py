import streamlit as st

def generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10,
                   marksman_t10, ratios, pet_buff, city_buff, minister_buff):
    total_buff_percent = city_buff
    effective_march_size = int(max_march_size * (1 + total_buff_percent / 100) + minister_buff + pet_buff)

    total_troops = {
        'infantry': (infantry_t11 or 0) + (infantry_t10 or 0),
        'lancer': (lancer_t11 or 0) + (lancer_t10 or 0),
        'marksman': (marksman_t11 or 0) + (marksman_t10 or 0)
    }

    marches = [{'infantry': 0, 'lancer': 0, 'marksman': 0, 'total': 0} for _ in range(num_marches)]

    for i, march in enumerate(marches):
        r = ratios[i]
        if r['infantry'] + r['lancer'] + r['marksman'] != 100:
            raise ValueError(f"March {i+1} ratios must total 100%.")

        total_capacity = effective_march_size
        infantry_troops = int((r['infantry'] / 100) * total_capacity)
        lancer_troops = int((r['lancer'] / 100) * total_capacity)
        marksman_troops = int((r['marksman'] / 100) * total_capacity)

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
    pet_buff = st.selectbox('Select the level/bonus of your Snow Ape Pet Buff',
                            ("Level 1 - 1500" ,
                             "Level 2 - 3000",
                             "Level 3 - 4500",
                             "Level 4 - 6000",
                             "Level 5 - 7500",
                             "Level 6 - 9000",
                             "Level 7 - 10500",
                             "Level 8 - 12000",
                             "Level 9 - 13500",
                             "Level 10 - 15000"), index=0, )
    pet_buff = int(pet_buff.split('-')[1].strip()) if pet_buff else 0

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
    st.write('### Buffs Summary')
    st.write(f"Pet Buff: {pet_buff}, City Buff: {city_buff}%, Minister Buff: {minister_buff}")
    return  pet_buff, city_buff, minister_buff

def main():
    st.set_page_config(page_title="Troop Manager", layout="centered")
    st.title('Troop Formation Builder & Ratio Optimizer')

    pet_buff, city_buff, minister_buff = buffs_section()

    st.header("March Setup", divider="blue", help="Setup your Marches and Troops.")
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

    st.header("Optimize Ratios", divider="blue", help="Optimize your troop ratios  according to your troops and buffs.")
    ratio_type = st.selectbox('Select Ratio Type', ['Bear'])  # Add more options here

    if st.button('Optimize Ratios'):
        optimized_ratio = optimize_ratio(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11,
                                         infantry_t10, lancer_t10, marksman_t10, ratio_type,
                                         pet_buff, city_buff, minister_buff)
        st.write('### Optimized Troop Ratios')
        for troop_type, percent in optimized_ratio.items():
            st.write(f"{troop_type.capitalize()}: {percent:.2f}%")

    st.header("Generate Marches" , divider="blue", help="Generate your Marches with the selected Troops and Buffs.")
    st.header("March Ratio Selection")
    use_same_ratio = st.checkbox("Use same ratio for all marches", value=True)
    ratios = []

    if use_same_ratio:
        col1, col2, col3 = st.columns(3)
        with col1:
            infantry_percent = st.number_input('Infantry %', min_value=0.0, max_value=100.0, value=33.33, step=0.01,
                                               format="%.2f", key="global_inf")
        with col2:
            lancer_percent = st.number_input('Lancer %', min_value=0.0, max_value=100.0, value=33.33, step=0.01,
                                             format="%.2f", key="global_lan")
        with col3:
            marksman_percent = st.number_input('Marksman %', min_value=0.0, max_value=100.0, value=33.33, step=0.01,
                                               format="%.2f", key="global_mar")
        for _ in range(num_marches):
            ratios.append({
                'infantry': infantry_percent,
                'lancer': lancer_percent,
                'marksman': marksman_percent
            })
    else:
        for i in range(num_marches):
            st.subheader(f"March {i + 1} Ratios")
            col1, col2, col3 = st.columns(3)
            with col1:
                infantry_percent = st.number_input(f'Infantry % (M{i + 1})', min_value=0.0, max_value=100.0,
                                                   value=33.33, step=0.01, format="%.2f", key=f"inf_{i}")
            with col2:
                lancer_percent = st.number_input(f'Lancer % (M{i + 1})', min_value=0.0, max_value=100.0, value=33.33,
                                                 step=0.01, format="%.2f", key=f"lan_{i}")
            with col3:
                marksman_percent = st.number_input(f'Marksman % (M{i + 1})', min_value=0.0, max_value=100.0,
                                                   value=33.33, step=0.01, format="%.2f", key=f"mar_{i}")

            ratios.append({
                'infantry': infantry_percent,
                'lancer': lancer_percent,
                'marksman': marksman_percent
            })

    if st.button('Generate Marches'):
        try:
            marches = generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11,
                                     infantry_t10, lancer_t10, marksman_t10, ratios,
                                     pet_buff, city_buff, minister_buff)
            st.write('### March Formation Results')
            for i, march in enumerate(marches, 1):
                st.write(
                    f"March {i}: Infantry={march['infantry']}, Lancer={march['lancer']}, Marksman={march['marksman']}, Total={march['total']}")
        except ValueError as e:
            st.error(str(e))

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
