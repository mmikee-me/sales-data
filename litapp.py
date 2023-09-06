import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the password
password = "salesdata"

# Title for your app
st.title("CSV Data Analysis")

# Add a password input field
entered_password = st.sidebar.text_input("Enter Password:", "", type="password")

# Check if the entered password matches the predefined password
if entered_password == password:
    # Continue with the app if the password is correct
    st.sidebar.success("Password accepted!")

    # Upload CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    # Check if the entered password matches the predefined password
    if uploaded_file is not None:
        # Read the CSV file into a DataFrame with the specified delimiter "|"
        df = pd.read_csv(uploaded_file, delimiter="|")

        # Extract month and year from the 'transaction_date' column
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['transaction_month'] = df['transaction_date'].dt.strftime('%Y-%m')
        df['transaction_year'] = df['transaction_date'].dt.strftime('%Y')

        # Create multiselect widgets for transaction month, year, and location
        all_months = df['transaction_month'].unique()
        all_years = df['transaction_year'].unique()
        all_locations = df['transaction_location'].unique()

        # Get the unique year-month values and sort them in ascending order
        unique_year_months = sorted(all_months)

        # Create a multiselect widget for selecting years
        selected_years = st.sidebar.multiselect("Select Transaction Years", sorted(all_years), default=[])

        # Filter the DataFrame based on the selected years
        filtered_df = df[df['transaction_year'].isin(selected_years)]

        # Update the list of available months based on selected years
        unique_year_months = sorted(filtered_df['transaction_month'].unique())

        # Create a multiselect widget for selecting months
        selected_months = st.sidebar.multiselect("Select Transaction Months", unique_year_months, default=unique_year_months)

        # Create a multiselect widget for selecting locations
        selected_locations = st.sidebar.multiselect("Select Locations", sorted(all_locations), default=[])

        # Add a selection widget for chart type (bar or line)
        chart_type = st.sidebar.selectbox("Select Chart Type", ["Line Chart", "Bar Chart"])

        # Filter the DataFrame based on the selected months, years, and locations
        filtered_df = df[
            (df['transaction_month'].isin(selected_months)) &
            (df['transaction_year'].isin(selected_years)) &
            (df['transaction_location'].isin(selected_locations))
        ]

        # Group by location and calculate totals
        grouped_data = filtered_df.groupby(['transaction_location', 'transaction_month']).agg({
            'total_delivered': 'sum',
            'total_returned': 'sum'
        }).reset_index()

        # Add the "billable" column
        grouped_data['billable'] = grouped_data['total_delivered'] - grouped_data['total_returned']

        # Calculate the total billable amount for the current selection
        total_billable = grouped_data['billable'].sum()

        # Display the total billable amount as a metric
        st.metric("Total Billable Amount", total_billable)

        # Display the slicer options
        #st.subheader("Selected Slicer Options:")
        #st.write(f"Selected Years: {', '.join(selected_years)}")
        #st.write(f"Selected Months: {', '.join(selected_months)}")
        #st.write(f"Selected Locations: {', '.join(selected_locations)}")

        # Display the filtered table
        st.subheader("Monthly Totals per Location")
        st.write(grouped_data)

        # Get a color palette for locations
        location_palette = sns.color_palette("husl", len(grouped_data['transaction_location'].unique()))

        # Create a chart based on the selected type (bar or line)
        plt.figure(figsize=(12, 6))
        for i, location in enumerate(grouped_data['transaction_location'].unique()):
            location_data = grouped_data[grouped_data['transaction_location'] == location]
            x = location_data['transaction_month']
            y = location_data['billable']
            label = location
            
            # Check if data exists for the location before plotting
            if not location_data.empty:
                if chart_type == "Bar Chart":
                    plt.bar(x, y, label=label, color=location_palette[i])
                elif chart_type == "Line Chart":
                    plt.plot(x, y, label=label, marker='o', linestyle='-')

        plt.xlabel('Month')
        plt.ylabel('Billable Amount')
        plt.title(f'Billable Amounts for Selected Locations and Months ({chart_type})')
        plt.xticks(rotation=45, ha="right")
        plt.legend()
        st.pyplot(plt)  # Display the selected chart type in Streamlit

else:
    # Display an error message if the password is incorrect
    st.sidebar.error("Incorrect password! Access denied.")
