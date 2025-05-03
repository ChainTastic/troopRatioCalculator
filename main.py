from typing import Dict, List, Tuple, Optional

import streamlit as st
from constants import TROOP_TYPES, PET_BUFF_LEVELS, MINISTER_BUFF_VALUE
from models.buffs import BuffConfiguration
from models.troop_count import TroopCount
from models.troop_manager import TroopManager


def main():
    st.set_page_config(page_title="Troop Manager", layout="centered")
    st.title('Troop Formation Builder & Ratio Optimizer')

    # Setup the different sections of the app
    max_march_size = render_march_setup_section()
    buffs, total_buff = render_buffs_section(max_march_size)
    troops, troop_manager = render_troops_input_section(max_march_size, buffs)
    num_marches, optimized_ratio = render_ratio_optimization_section(troops, troop_manager)
    render_march_generation_section(num_marches, troops, troop_manager, buffs)


def render_march_setup_section() -> int:
    """Render the march setup section and return the max march size."""
    st.header("March Setup", divider="blue", help="Setup your Marches and Troops.")
    return st.number_input('Base March Size', min_value=1, value=1000, format="%d")


def render_buffs_section(max_march_size: int) -> Tuple[BuffConfiguration, int]:
    """Render the buffs section and return the buff configuration and total buff value."""
    st.subheader('Buffs')

    # Pet buff
    pet_buff = st.selectbox('Select Snow Ape Pet Buff Level', options=list(PET_BUFF_LEVELS.keys()), index=0)
    pet_buff_value = PET_BUFF_LEVELS[pet_buff]

    # City buff
    city_buff_10 = st.checkbox('Apply 10% City Buff')
    city_buff_20 = st.checkbox('Apply 20% City Buff')

    if city_buff_10 and city_buff_20:
        st.error('You cannot select both 10% and 20% City Buff. Please choose one.')
        city_buff = 0
    elif city_buff_10:
        city_buff = 10
    elif city_buff_20:
        city_buff = 20
    else:
        city_buff = 0

    # Minister buff
    minister_buff_enabled = st.checkbox('Apply Minister of Strategy Buff')
    minister_buff = MINISTER_BUFF_VALUE if minister_buff_enabled else 0

    # Create buff configuration and display summary
    buffs = BuffConfiguration(pet_buff_value, city_buff, minister_buff)

    # Display summary
    st.write('### Buffs Summary')
    st.write(f"Pet Buff: {buffs.pet_buff} troops" if buffs.pet_buff else "No Pet Buff Selected")

    city_buff_text = (
        f"City Buff: {buffs.city_buff}% (Flat Value: {int(max_march_size * buffs.city_buff / 100)} troops)" if buffs.city_buff else "No City Buff Selected")
    st.write(city_buff_text)

    st.write(f"Minister Buff: {buffs.minister_buff} troops" if buffs.minister_buff else "No Minister Buff Selected")
    ## add a  blue divider thin line with thin margin
    st.markdown("""
        <style>
        .divider {
            border: 0;
            height: 1px;
            background-color: #0072B8;
            margin: 1px 0;
        }
        </style>
        <div class="divider"></div>
        """, unsafe_allow_html=True)
    total_buff = buffs.calculate_total_buff(max_march_size)
    st.write("Total Buff: ", pet_buff_value + int(max_march_size * buffs.city_buff / 100) + buffs.minister_buff,
             " troops")

    st.write("Total Buffed March Size: ", total_buff, " troops")

    return buffs, total_buff


def render_troops_input_section(max_march_size: int, buffs: BuffConfiguration) -> Tuple[TroopCount, TroopManager]:
    """Render the troops input section and return the troop count and troop manager."""
    st.subheader('Troops Input')

    # T10 troops
    st.subheader('T10 Troops')
    infantry_t10 = st.number_input("Infantry T10",
                                   value=st.session_state.get("infantry_t10", 0),
                                   min_value=0,
                                   step=1000,
                                   format="%d",
                                   key="infantry_t10")

    lancer_t10 = st.number_input('Lancer T10',
                                 min_value=0,
                                 value=st.session_state.get("lancer_t10", 0),
                                 step=1000,
                                 format="%d",
                                 key="lancer_t10")

    marksman_t10 = st.number_input('Marksman T10',
                                   min_value=0,
                                   value=st.session_state.get("marksman_t10", 0),
                                   step=1000,
                                   format="%d",
                                   key="marksman_t10")

    # T11 troops
    st.subheader('T11 Troops')
    infantry_t11 = st.number_input('Infantry T11', min_value=0, value=0, format="%d")
    lancer_t11 = st.number_input('Lancer T11', min_value=0, value=0, format="%d")
    marksman_t11 = st.number_input('Marksman T11', min_value=0, value=0, format="%d")

    # Create troop count and display summary
    troops = TroopCount(infantry=infantry_t11 + infantry_t10, lancer=lancer_t11 + lancer_t10,
        marksman=marksman_t11 + marksman_t10)

    # Display summary
    troops_dict = troops.to_dict()
    st.subheader("Total Available Troops")
    for troop_type in TROOP_TYPES:
        st.write(f"Total {troop_type.capitalize()}: {troops_dict[troop_type]:,}")

    return troops, TroopManager(max_march_size, buffs)


def render_ratio_optimization_section(troops: TroopCount, troop_manager: TroopManager) -> Tuple[int, Dict[str, float]]:
    """Render the ratio optimization section and return the number of marches and optimized ratio."""
    st.header("Optimize Ratios", divider="blue")

    formation_ratios = {
        "Bear": {"infantry": 10, "lancer": 30, "marksman": 60},
        "Balanced": {"infantry": 34, "lancer": 33, "marksman": 33},
        "Marksman Rush": {"infantry": 5, "lancer": 15, "marksman": 80},
        "Lancer Charge": {"infantry": 5, "lancer": 85, "marksman": 10},
        "Infantry Wall": {"infantry": 80, "lancer": 10, "marksman": 10},
        "Standard Formation": {"infantry": 45, "lancer": 10, "marksman": 45},
        "Garrison": {"infantry": 50, "lancer": 40, "marksman": 10},
        "Rally": {"infantry": 30, "lancer": 20, "marksman": 50}
    }

    for name, values in formation_ratios.items():
        st.markdown(
            f"- **{name}** → Infantry: {values['infantry']}%, Lancer: {values['lancer']}%, Marksman: {values['marksman']}%")

    ratio_type = st.selectbox("Select Formation Ratio Type", options=list(formation_ratios.keys()))
    num_marches = st.selectbox('Number of Marches', options=[1, 2, 3, 4, 5, 6, 7], index=0)

    optimized_ratio = {}
    if st.button('Optimize Ratios'):
        optimized_ratio = troop_manager.optimize_ratio(num_marches, troops, ratio_type)
        st.session_state['optimized_ratio'] = optimized_ratio

    if 'optimized_ratio' in st.session_state:
        st.write('### Optimized Troop Ratios')
        for troop_type, percent in st.session_state['optimized_ratio'].items():
            st.write(f"{troop_type.capitalize()}: {percent}%")

    return num_marches, optimized_ratio


def render_march_generation_section(num_marches: int, troops: TroopCount, troop_manager: TroopManager,
                                    buffs: BuffConfiguration) -> None:
    """Render the march generation section."""
    st.header("Generate Marches", divider="blue")

    use_same_ratio = st.checkbox("Use same ratio for all marches", value=True)
    effective_march_size = buffs.calculate_total_buff(troop_manager.max_march_size)

    if use_same_ratio:
        ratio = render_global_ratio_input(troops, num_marches, effective_march_size)
        if not st.session_state.get("global_ratio_valid", True):
            return
        ratios = [ratio.copy() for _ in range(num_marches)]
    else:
        ratios = render_individual_ratio_inputs(num_marches, effective_march_size)
        if not st.session_state.get("individual_ratios_valid", True):
            return

    render_march_results_button(num_marches, troops, troop_manager, ratios)

def render_ratio_slider_group(prefix: str, index: Optional[int] = None, default_values: Dict[str, int] = None) -> Dict[str, int]:
    """Render sliders with increment/decrement buttons for Infantry, Lancer, Marksman."""
    troop_types = ['infantry', 'lancer', 'marksman']
    result = {}
    defaults = default_values or {"infantry": 33, "lancer": 33, "marksman": 34}

    for troop in troop_types:
        base_key = f"{prefix}_{troop}_{index}" if index is not None else f"{prefix}_{troop}"
        slider_key = f"{base_key}_slider"
        incr_key = f"{base_key}_incr"
        decr_key = f"{base_key}_decr"

        # Initialize session state once
        if slider_key not in st.session_state:
            st.session_state[slider_key] = defaults[troop]

        # Create layout
        st.markdown(f"**{troop.capitalize()} %**")
        col_slider, col_minus, col_plus = st.columns([6, 1, 1])

        with col_minus:
            if st.button("➖", key=decr_key):
                st.session_state[slider_key] = max(0, st.session_state[slider_key] - 1)

        with col_plus:
            if st.button("➕", key=incr_key):
                st.session_state[slider_key] = min(100, st.session_state[slider_key] + 1)

        with col_slider:
            st.slider(
                "Percentage Value",  # hidden label
                min_value=0,
                max_value=100,
                step=1,
                key=slider_key,
                label_visibility="collapsed"
            )

        result[troop] = st.session_state[slider_key]

    return result

def render_global_ratio_input(troops: TroopCount, num_marches: int, effective_march_size: int) -> Optional[Dict[str, int]]:
    """Render global sliders + buttons using the shared slider group."""
    st.subheader("Global Troop Ratio for All Marches")
    st.markdown("_Bear example: 10% Infantry / 30% Lancer / 60% Marksman_")

    ratio = render_ratio_slider_group("global", default_values={"infantry": 33, "lancer": 33, "marksman": 34})
    total = sum(ratio.values())
    st.markdown(f"**Total: {total}%**")

    st.session_state["global_ratio_valid"] = (total == 100)
    if not st.session_state["global_ratio_valid"]:
        st.warning("Total must equal 100% to apply this ratio.")
        return None

    display_global_requirements(troops, ratio, num_marches, effective_march_size)
    return ratio


def display_global_requirements(troops: TroopCount, ratio: Dict[str, float], num_marches: int,
                                effective_march_size: int) -> None:
    """Display the troop requirements for the selected global ratio."""
    troops_dict = troops.to_dict()

    infantry_needs = int((ratio['infantry'] / 100) * effective_march_size * num_marches)
    lancer_needs = int((ratio['lancer'] / 100) * effective_march_size * num_marches)
    marksman_needs = int((ratio['marksman'] / 100) * effective_march_size * num_marches)

    st.markdown(
        f"**Infantry:** {troops_dict['infantry']:,} _(Needs: {infantry_needs:,})_ | " + f"**Lancer:** {troops_dict['lancer']:,} _(Needs: {lancer_needs:,})_ | " + f"**Marksman:** {troops_dict['marksman']:,} _(Needs: {marksman_needs:,})_")


def render_individual_ratio_inputs(num_marches: int, effective_march_size: int) -> List[Dict[str, int]]:
    """Render sliders + buttons for individual ratios using shared helper."""
    ratios = []
    valid = True

    for i in range(num_marches):
        st.subheader(f"March {i + 1} Ratios")
        ratio = render_ratio_slider_group("march", index=i, default_values={"infantry": 33, "lancer": 33, "marksman": 34})
        total = sum(ratio.values())
        st.markdown(f"**Total: {total}%**")

        if total != 100:
            valid = False
            st.warning("Total must equal 100% to generate this march.")
        else:
            ratios.append(ratio)
            display_individual_requirements(ratio, effective_march_size)

    st.session_state["individual_ratios_valid"] = valid
    return ratios


def display_individual_requirements(ratio: Dict[str, float], effective_march_size: int) -> None:
    """Display the requirements for an individual march."""
    inf_amt = int((ratio['infantry'] / 100) * effective_march_size)
    lan_amt = int((ratio['lancer'] / 100) * effective_march_size)
    mar_amt = int((ratio['marksman'] / 100) * effective_march_size)

    st.markdown(f"_Needs: Infantry={inf_amt:,}, Lancer={lan_amt:,}, Marksman={mar_amt:,}_")


def render_march_results_button(num_marches: int, troops: TroopCount, troop_manager: TroopManager,
                                ratios: List[Dict[str, float]]) -> None:
    """Render the button to generate march results and display them when clicked."""
    if st.button('Generate Marches'):
        try:
            marches = troop_manager.generate_marches(num_marches, troops, ratios)
            st.write('### March Formation Results')

            for i, march in enumerate(marches, 1):
                st.write(f"March {i}: Infantry = {march['infantry']}, "
                         f"Lancer = {march['lancer']}, "
                         f"Marksman = {march['marksman']}, "
                         f"Total = {march['total']}")
        except ValueError as e:
            st.error(str(e))


if __name__ == "__main__":
    main()
