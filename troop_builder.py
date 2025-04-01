import streamlit as st

def generate_march(num_marches, max_march_size, infantry_t11, lancer_t11, marksman_t11, infantry_t10, lancer_t10, marksman_t10, infantry_min, lancer_max, marksman_max, infantry_max, lancer_min, marksman_min):
    total_troops = {
        'infantry': (infantry_t11 or 0) + (infantry_t10 or 0),
        'lancer': (lancer_t11 or 0) + (lancer_t10 or 0),
        'marksman': (marksman_t11 or 0) + (marksman_t10 or 0)
    }

    marches = [{'infantry': 0, 'lancer': 0, 'marksman': 0, 'total': 0} for _ in range(num_marches)]

    # Allocate Infantry Min
    infantry_min_troops = int((infantry_min / 100) * max_march_size)
    infantry_max_troops = int((infantry_max / 100) * max_march_size)
    for march in marches:
        allocate = min(infantry_min_troops, total_troops['infantry'])
        march['infantry'] += allocate
        march['total'] += allocate
        total_troops['infantry'] -= allocate

    # Allocate Lancer Max and Min
    lancer_max_troops = int((lancer_max / 100) * max_march_size)
    lancer_min_troops = int((lancer_min / 100) * max_march_size)
    for march in marches:
        allocate = min(lancer_max_troops, total_troops['lancer'])
        march['lancer'] += allocate
        march['total'] += allocate
        total_troops['lancer'] -= allocate

    # Allocate Marksman Max and Min
    marksman_max_troops = int((marksman_max / 100) * max_march_size)
    marksman_min_troops = int((marksman_min / 100) * max_march_size)
    for march in marches:
        allocate = min(marksman_max_troops, total_troops['marksman'])
        march['marksman'] += allocate
        march['total'] += allocate
        total_troops['marksman'] -= allocate

    return marches

def main():
    st.set_page_config(page_title="Troop Formation Builder", layout="centered", initial_sidebar_state="collapsed")
    st.title('Troop Formation Builder')

    num_marches = st.selectbox('Number of Marches', options=[1, 2, 3, 4, 5, 6, 7], index=0)
    max_march_size = st.number_input('Max March Size', min_value=1, value=1000, format="%d")

    st.subheader('T11 Troops')
    infantry_t11 = st.number_input('Infantry T11', min_value=0, value=None, format="%d", placeholder='Enter number of troops')
    lancer_t11 = st.number_input('Lancer T11', min_value=0, value=None, format="%d", placeholder='Enter number of troops')
    marksman_t11 = st.number_input('Marksman T11', min_value=0, value=None, format="%d", placeholder='Enter number of troops')

    st.subheader('T10 Troops')
    infantry_t10 = st.number_input('Infantry T10', min_value=0, value=None, format="%d", placeholder='Enter number of troops')
    lancer_t10 = st.number_input('Lancer T10', min_value=0, value=None, format="%d", placeholder='Enter number of troops')
    marksman_t10 = st.number_input('Marksman T10', min_value=0, value=None, format="%d", placeholder='Enter number of troops')

    st.subheader('Percentage Constraints')
    infantry_min = st.number_input('Minimum Infantry %', min_value=0, max_value=100, value=0, step=1, format="%d")
    infantry_max = st.number_input('Maximum Infantry %', min_value=0, max_value=100, value=100, step=1, format="%d")
    lancer_min = st.number_input('Minimum Lancer %', min_value=0, max_value=100, value=0, step=1, format="%d")
    lancer_max = st.number_input('Maximum Lancer %', min_value=0, max_value=100, value=100, step=1, format="%d")
    marksman_min = st.number_input('Minimum Marksman %', min_value=0, max_value=100, value=0, step=1, format="%d")
    marksman_max = st.number_input('Maximum Marksman %', min_value=0, max_value=100, value=100, step=1, format="%d")

    if st.button('Generate Marches'):
        try:
            marches = generate_march(
                int(num_marches), max_march_size,
                infantry_t11, lancer_t11, marksman_t11,
                infantry_t10, lancer_t10, marksman_t10,
                infantry_min, lancer_max, marksman_max,
                infantry_max, lancer_min, marksman_min
            )
            st.write('### March Formation Results')
            for i, march in enumerate(marches, 1):
                formatted_infantry = f"{march['infantry']:,}"
                formatted_lancer = f"{march['lancer']:,}"
                formatted_marksman = f"{march['marksman']:,}"
                formatted_total = f"{march['total']:,}"
                st.write(f"March {i}: Infantry={formatted_infantry}, Lancer={formatted_lancer}, Marksman={formatted_marksman}, Total={formatted_total}")
        except ValueError:
            st.error("Please enter valid numbers in all fields.")

if __name__ == '__main__':
    main()
