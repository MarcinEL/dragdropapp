import json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
import pickle

# Streamlit app setup
st.title("Tensorboard json Plotter")
st.write("Upload your JSON files to visualize and customize the gradient norm plot.")

# Load saved settings if available
if 'saved_settings' not in st.session_state:
    st.session_state['saved_settings'] = {}

# File uploader
uploaded_files = st.file_uploader("Drag and drop your JSON files here", type="json", accept_multiple_files=True)

if uploaded_files:
    try:
        fig_width = st.sidebar.slider("Figure width", 5, 20, 12)
        fig_height = st.sidebar.slider("Figure height", 5, 20, 6)

        # Plot setup
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        settings = {}  # To save settings for this session

        for uploaded_file in uploaded_files:
            # Load each uploaded JSON file
            data = json.load(uploaded_file)

            # Convert the JSON data to a DataFrame
            df = pd.DataFrame(data, columns=["timestamp", "iteration", "gradient_norm"])

            # Sidebar options for each file
            st.sidebar.title(f"Customization for {uploaded_file.name}")
            default_settings = st.session_state['saved_settings'].get(uploaded_file.name, {})
            color = st.sidebar.color_picker(f"Select line color for {uploaded_file.name}", default_settings.get('color', "#00f900"))
            line_style = st.sidebar.selectbox(f"Select line style for {uploaded_file.name}", ["-", "--", "-.", ":"], index=["-", "--", "-.", ":"].index(default_settings.get('line_style', "-")), key=f"line_style_{uploaded_file.name}")
            line_width = st.sidebar.slider(f"Select line width for {uploaded_file.name}", 0.5, 5.0, default_settings.get('line_width', 1.5), key=f"line_width_{uploaded_file.name}")
            label = st.sidebar.text_input(f"Legend label for {uploaded_file.name}", default_settings.get('label', uploaded_file.name))

            # Save settings for the current file
            settings[uploaded_file.name] = {
                'color': color,
                'line_style': line_style,
                'line_width': line_width,
                'label': label
            }

            # Plot the gradient norm against learning steps (iterations)
            ax.plot(df['iteration'], df['gradient_norm'], label=label, color=color, linestyle=line_style, linewidth=line_width)

        # Save settings to session state
        if st.sidebar.button("Save Settings"):
            st.session_state['saved_settings'] = settings
            st.success("Settings saved successfully!")

        # Global plot customizations
        grid = st.sidebar.checkbox("Show grid", value=True)
        title = st.sidebar.text_input("Plot title", "Gradient Norm vs Learning Steps")
        x_label = st.sidebar.text_input("X-axis label", "Learning Steps (Iterations)")
        y_label = st.sidebar.text_input("Y-axis label", "Gradient Norm")

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend()
        if grid:
            ax.grid(True)

        # Display the plot in the Streamlit app
        st.pyplot(fig)

        # Button to download the plot as SVG or PDF
        buffer = BytesIO()
        format = st.sidebar.selectbox("Download format", ["SVG", "PDF"], index=0)
        fig.savefig(buffer, format=format.lower())
        buffer.seek(0)
        st.download_button(
            label=f"Download Plot as {format}",
            data=buffer,
            file_name=f"gradient_norm_plot.{format.lower()}",
            mime=f"application/{format.lower()}"
        )
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
