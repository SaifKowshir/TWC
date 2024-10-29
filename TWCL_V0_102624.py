import streamlit as st
import pandas as pd
from io import BytesIO

# Set the page configuration to wide mode
st.set_page_config(layout="wide")

# Initialize session state for storing calculation results
if 'calculation_results' not in st.session_state:
    st.session_state['calculation_results'] = []

# Define tower data for options and weights (with added tower types and logic)
tower_data = {
    "NS5": {
        "BTB_options": {
            "BASIC TOWER BODY WHEN WITH E3 BODY EXTENSION": 7657.795,
            "BASIC TOWER BODY WHEN WITH E6 to E12 BODY EXTENSIONS": 7318.671,
            "BASIC TOWER BODY WHEN WITH -4M to +2M LEG EXTENSIONS": 7657.795,
            "BASIC TOWER BODY WHEN WITH -5M LEG EXTENSION": 7318.671,  # Correct logic applied here
        },
        "BE_values": {
            "E0": 0.0,
            "E3": 1398.814,
            "E6": 2535.785,
            "E9": 3185.689,
            "E12": 4297.383
        },
        "Leg_values": {
            "+0M": 471.061,
            "-5M": 171.491,
            "-4M": 236.135,
            "-3M": 264.864,
            "-2M": 342.284,
            "-1M": 407.650,
            "+1M": 535.807,
            "+2M": 623.249
        }
    },
    "LA5": {
        "BTB_options": {
            "BASIC TOWER BODY WHEN WITH -4M & -5M LEG EXTENSIONS": 0,
            "BASIC TOWER BODY WHEN WITH BE OR -3M,-2M,-1M,+0M,+1M AND +2M LEG EXTENSIONS": 11390.96,
        },
        "BE_values": {
            "E0": 0.0,
            "E3": {
                "with -4M & -5M leg extensions": 0,
                "with -3M to +2M leg extensions": 2151.75
            },
            "E6": {
                "with -4M & -5M leg extensions": 0,
                "with -3M to +2M leg extensions": 3572.72
            },
            "E9": {
                "with -4M & -5M leg extensions": 0,
                "with -3M to +2M leg extensions": 4694.68
            }
        },
        "Leg_values": {
            "+0M": 574.689,
            "-5M": 187.406,
            "-4M": 266.396,
            "-3M": 335.810,
            "-2M": 416.244,
            "-1M": 514.038,
            "+1M": 669.806,
            "+2M": 765.783
        }
    },
    "MA5": {
        "BTB_options": {
            "BASIC TOWER BODY WHEN WITH -4M & -5M LEG EXTENSIONS": 13726.899,
            "BASIC TOWER BODY WHEN WITH BE OR -3M,-2M,-1M,+0M,+1M AND +2M LEG EXTENSIONS": 13724.584,
        },
        "BE_values": {
            "E0": 0.0,
            "E3": {
                "with -4M & -5M leg extensions": 2228.388,
                "with -3M to +2M leg extensions": 2228.100
            },
            "E6": {
                "with -4M & -5M leg extensions": 3690.482,
                "with -3M to +2M leg extensions": 3688.048
            },
            "E9": {
                "with -4M & -5M leg extensions": 5240.190,
                "with -3M to +2M leg extensions": 5237.598
            }
        },
        "Leg_values": {
            "+0M": 588.899,
            "-5M": 219.517,
            "-4M": 307.324,
            "-3M": 357.019,
            "-2M": 448.234,
            "-1M": 576.856,
            "+1M": 757.754,
            "+2M": 852.382
        }
    },
    "HA5/DE5": {
        "BTB_options": {
            "BASIC TOWER BODY WHEN WITH ALL BODY EXTENSION": 14513.530,
            "BASIC TOWER BODY WHEN WITH -4M & -5M LEG EXTENSIONS": 14515.305,
            "BASIC TOWER BODY WHEN WITH -3M,-2M,-1M,+0M,+1M & +2M LEG EXTENSIONS": 14513.530,
        },
        "BE_values": {
            "E0": 0.0,
            "E3": 2691.752,
            "E6": 4344.253,
            "E9": 5849.610
        },
        "Leg_values": {
            "+0M": 588.899,
            "-5M": 322.898,
            "-4M": 408.242,
            "-3M": 516.451,
            "-2M": 585.859,
            "-1M": 705.206,
            "+1M": 936.229,
            "+2M": 1044.828
        }
    }
}

# Title for the app
st.title("Tower Weight Calculator")

# Sidebar for selection area
with st.sidebar.expander("Tower Selection", expanded=True):
    st.subheader("Tower Selection")

    # Tower Type selection
    tower_type = st.selectbox("Tower Type", tower_data.keys(), key='tower_type')

    # Body Extension selection with default "E0" for all towers
    be_options = list(tower_data[tower_type]['BE_values'].keys())
    selected_be = st.selectbox("Body Extension", be_options, key='body_extension', index=be_options.index("E0"))

    # Leg Extension selection for each leg with default "+0M" for all towers
    leg_extensions = []
    for i in range(1, 5):
        leg_ext = st.selectbox(f"Leg {i} Extension", tower_data[tower_type]['Leg_values'].keys(), key=f'leg_ext_{i}',
                               index=0)  # Default is "+0M"
        leg_extensions.append(leg_ext)

    # Buttons for calculation and removal
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        calculate_btn = st.button("Calculate")
    with col_btn2:
        remove_last_btn = st.button("Remove Last")
    with col_btn3:
        remove_all_btn = st.button("Remove All")


# Function to calculate tower weight
def calculate_tower_weight():
    data = tower_data[tower_type]

    # Retrieve BE weight based on tower type and leg extensions
    BE_weight = data['BE_values'].get(selected_be, 0)

    # Handle LA5 and MA5 towers where BE is a dictionary
    if isinstance(data['BE_values'][selected_be], dict):
        be_options = data["BE_values"][selected_be]
        if leg_extensions[0] in ["-4M", "-5M"]:
            BE_weight = be_options["with -4M & -5M leg extensions"]
        else:
            BE_weight = be_options["with -3M to +2M leg extensions"]

    # Automatically select BTB based on BE and leg extensions
    if tower_type == "NS5":
        if any(ext == "-5M" for ext in leg_extensions):
            BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH -5M LEG EXTENSION"]
        elif selected_be == "E3":
            BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH E3 BODY EXTENSION"]
        elif selected_be in ["E6", "E9", "E12"]:
            BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH E6 to E12 BODY EXTENSIONS"]
        else:
            BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH -4M to +2M LEG EXTENSIONS"]
    else:
        if tower_type == "HA5/DE5":
            if "-4M" in leg_extensions or "-5M" in leg_extensions:
                BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH -4M & -5M LEG EXTENSIONS"]
            else:
                BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH -3M,-2M,-1M,+0M,+1M & +2M LEG EXTENSIONS"]
        else:
            if "-4M" in leg_extensions or "-5M" in leg_extensions:
                BTB_weight = data["BTB_options"]["BASIC TOWER BODY WHEN WITH -4M & -5M LEG EXTENSIONS"]
            else:
                BTB_weight = data["BTB_options"][
                    "BASIC TOWER BODY WHEN WITH BE OR -3M,-2M,-1M,+0M,+1M AND +2M LEG EXTENSIONS"]

    BB_BE_weight = BTB_weight + BE_weight

    # Retrieve leg weights for each leg
    leg_weights = [data['Leg_values'][leg_ext] for leg_ext in leg_extensions]
    ALL_Legs = sum(leg_weights)

    # Calculate total weight
    total_weight = BB_BE_weight + ALL_Legs

    # Create a result dictionary
    result = {
        'SNO': len(st.session_state['calculation_results']) + 1,
        'Tower Type': tower_type,
        'Body Extension': selected_be,
        'Leg Extensions': f"{leg_extensions[0]}, {leg_extensions[1]}, {leg_extensions[2]}, {leg_extensions[3]}",
        'Leg A': f"{leg_weights[0]:,.2f}",
        'Leg B': f"{leg_weights[1]:,.2f}",
        'Leg C': f"{leg_weights[2]:,.2f}",
        'Leg D': f"{leg_weights[3]:,.2f}",
        'BTB Weight': f"{BTB_weight:,.2f}",
        'BE Weight': f"{BE_weight:,.2f}",
        'BB+BE Weight': f"{BB_BE_weight:,.2f}",
        'ALL Legs': f"{ALL_Legs:,.2f}",
        'Total Weight': f"{total_weight:,.2f}"
    }

    return result


# Handle button actions
if calculate_btn:
    result = calculate_tower_weight()
    st.session_state['calculation_results'].append(result)

if remove_last_btn:
    if st.session_state['calculation_results']:
        st.session_state['calculation_results'].pop()
        st.success("Last calculation removed.")
    else:
        st.warning("No calculations to remove.")

if remove_all_btn:
    st.session_state['calculation_results'].clear()
    st.success("All calculations removed.")

# Results Table
st.subheader("Results Table")

if st.session_state['calculation_results']:
    df = pd.DataFrame(st.session_state['calculation_results'])

    # Remove index by resetting the index
    df = df.reset_index(drop=True)

    # Convert Total Weight to float for proper summation and formatting
    df['Total Weight'] = df['Total Weight'].replace({',': ''}, regex=True).astype(float)

    # Total weight calculation
    total_weight_sum = df["Total Weight"].sum()

    # Ensure Total Weight column is formatted to two decimal places
    df['Total Weight'] = df['Total Weight'].map('{:,.2f}'.format)

    # Styling: Last three columns with specific colors
    def style_columns(row):
        styles = [''] * len(row)  # Default styles for all columns
        styles[-1] = 'font-weight: bold; color: red'  # Tower Weight in bold red
        styles[-2] = 'color: blue'  # ALL Legs in blue
        styles[-3] = 'color: blue'  # BB+BE Weight in blue
        styles[-4] = 'color: Purple'  # ALL Body Extension Color
        styles[-5] = 'color: Green'  # BTB Weight column color

        return styles

    # Applying the styling logic to the DataFrame
    df_styled = df.style.apply(style_columns, axis=1)

    # Centering all columns except SNO and Tower Type
    df_styled = df_styled.set_properties(subset=df.columns.difference(['SNO', 'Tower Type']),
                                         **{'text-align': 'center'})

    st.table(df_styled)

    # Adding the total weight row at the end
    st.write(f"**Grand_Total (Ton): {total_weight_sum/1000:,.2f}**")

    # Export to Excel button (Excel index starts from 1)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        label="Export to Excel",
        data=buffer.getvalue(),
        file_name="tower_weight_calculations.xlsx",
        mime="application/vnd.ms-excel"
    )
