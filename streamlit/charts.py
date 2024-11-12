# pylint: skip-file
"""Script that create the charts for the Streamlit application."""
import altair as alt
import streamlit as st
import pandas as pd
import database as db
import data_processing as dp


def create_multiselect(unique_trucks: list) -> list:
    """Create a multi-select widget for truck IDs."""
    return st.multiselect(
        "Select Truck IDs to Display:",
        options=unique_trucks,
        default=unique_trucks
    )


def create_bar_chart_total_transactions(truck_data: pd.DataFrame) -> None:
    """Create and display a bar chart using the provided truck data."""
    bar_chart = alt.Chart(truck_data).mark_bar(color='#FF5733').encode(
        x=alt.X('truck_id:O', title='Truck ID', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('count:Q', title='Total Transactions'),
        tooltip=[
            alt.Tooltip('truck_id:O', title='Truck ID'),
            alt.Tooltip('count:Q', title='Total Transactions')
        ]
    ).properties(
        title='Transactions per Truck',
        width='container',
        height=600
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=30,
        anchor='start'
    )

    st.altair_chart(bar_chart, use_container_width=True)


def bar_transactions_per_truck() -> None:
    """Creates a bar chart showing total transactions per truck with filtering options."""
    all_data = db.fetch_transaction_data()
    unique_trucks = dp.get_unique_trucks(all_data)

    selected_trucks = create_multiselect(unique_trucks)

    if selected_trucks:
        transaction_data = db.fetch_transaction_data(
            selected_trucks)
        truck_data = dp.prepare_truck_data(transaction_data)
        create_bar_chart_total_transactions(truck_data)
    else:
        st.warning("Please select at least one truck to display.")


def get_x_encoding(view: str) -> alt.X:
    """Return the appropriate x encoding based on the selected view."""
    if view == 'Hour':
        return alt.X('time_period:O', title='Time (Hour)', axis=alt.Axis(labelAngle=0))
    return alt.X('time_period:T', title='Time (Day)')


def create_line_chart(transactions_per_time_period: pd.DataFrame, view: str) -> alt.Chart:
    """Create and return the Altair line chart based on the processed data."""
    line_chart = alt.Chart(
        transactions_per_time_period).mark_line(
            point=True, color='black').encode(
        x=get_x_encoding(view),
        y=alt.Y('count:Q', title='Total Transactions'),
    ).properties(
        title=f'Transactions per {view}',
        width='container',
        height=515
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=30,
        anchor='start'
    )

    return line_chart


def line_transactions(transaction_data: pd.DataFrame) -> None:
    """Creates a line chart showing total transactions based on selected granularity."""
    view = st.selectbox('Select Time Granularity:', ['Hour', 'Day'])

    transaction_data = dp.preprocess_transaction_data_line(
        transaction_data, view)

    transactions_per_time_period = transaction_data.groupby(
        'time_period').size().reset_index(name='count')

    line_chart = create_line_chart(transactions_per_time_period, view)
    st.altair_chart(line_chart, use_container_width=True)


def create_color_scale(transaction_counts: pd.DataFrame) -> alt.Scale:
    """Create a color scale for the pie chart based on transaction payment_method_ids."""
    return alt.Scale(
        domain=transaction_counts['payment_method_id'].tolist(),
        range=['#78c679', '#fec44f']
    )


def create_pie_chart(transaction_counts: pd.DataFrame, color_scale: alt.Scale) -> alt.Chart:
    """Create a pie chart using the provided transaction counts and color scale."""
    pie_chart = alt.Chart(transaction_counts).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="payment_method_id", type="nominal",
                        scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip('payment_method_type:N', title='Payment Method Type'),
            alt.Tooltip('count:Q', title='Count'),
            alt.Tooltip('percentage:Q', format=".1f", title='Percentage')
        ]
    ).properties(
        title="Total Transactions per Payment Method",
        width='container',
        height=500
    ).configure_title(
        fontSize=25,
        anchor='middle'
    )
    return pie_chart


def pie_transactions_per_payment_method_id() -> None:
    """Creates a pie chart showing total transactions per payment_method_id using Altair."""
    transaction_data = db.fetch_transaction_data_pie_chart()
    transaction_counts = dp.calculate_transaction_counts_pie(transaction_data)
    color_scale = create_color_scale(transaction_counts)
    pie_chart = create_pie_chart(transaction_counts, color_scale)
    st.altair_chart(pie_chart, use_container_width=True)


def create_bar_chart_total_or_average(truck_data: pd.DataFrame, view: str) -> alt.Chart:
    """Create a bar chart for the provided truck data."""
    bar_chart = alt.Chart(truck_data).mark_bar().encode(
        x=alt.X('truck_id:O', title='Truck ID', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('total:Q', title='Earnings'),
        tooltip=['truck_id:O', 'total:Q']
    ).properties(
        title=view,
        width="container",
        height=500
    ).configure_title(
        fontSize=30
    )
    return bar_chart


def bar_total_or_average_per_truck(transaction_data: pd.DataFrame) -> None:
    """Creates a bar chart showing either total or average earnings per truck."""
    view_option = st.selectbox(
        "Select filter", ("Total Earnings", "Average Earnings"))

    truck_data = dp.calculate_earnings_per_truck(transaction_data, view_option)
    view = f"{view_option} per Truck"

    bar_chart = create_bar_chart_total_or_average(truck_data, view)
    st.altair_chart(bar_chart, use_container_width=True)


def color_status(val: str) -> str:
    """Sets the color for the card reader table."""
    if val == '✓':
        return 'color: green;'
    return 'color: red;'


def display_truck_card_reader_table() -> None:
    """Displays a table showing each truck's name along with its card reader status."""
    truck_data = db.fetch_truck_card_reader_data()

    truck_data['has_card_reader'] = truck_data['has_card_reader'].map(
        {True: '✓', False: '✗'})

    styled_table = truck_data.style.applymap(
        color_status, subset=['has_card_reader'])

    st.dataframe(styled_table, hide_index=True, use_container_width=True)
