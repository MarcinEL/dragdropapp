import json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
import pickle

# Streamlit app setup
st.title("Gradient Norm Plotter")
st.write("Upload your JSON files to visualize and customize the gradient norm plot.")

# Load saved settings from a file if provided
settings_file = st.sidebar.file_uploader("Load plot settings", type="pkl")
if settings_file is not None:
    try:
        st.session_state['saved_settings'] = pickle.load(settings_file)
        st.success("Settings loaded successfully!")
    except Exception as e:
        st.error(f"Failed to load settings: {e}")

if 'saved_settings' not in st.session_state:
    st.session_state['saved_settings'] = {}

# File uploader
uploaded_files = st.file_uploader("Drag and drop your JSON files here", type="json", accept_multiple_files=True)

if uploaded_files:
    try:
        fig_width = st.sidebar.slider("Figure width", 5, 20, 12)
        fig_height = st.sidebar.slider("Figure height", 5, 20, 6)

        # Font customization options
        st.sidebar.title("Font Customization")
        title_fontsize = st.sidebar.slider("Title font size", 10, 30, 16)
        title_fontstyle = st.sidebar.selectbox("Title font style", ["normal", "italic", "oblique"], index=0)
        label_fontsize = st.sidebar.slider("Axis label font size", 8, 20, 12)
        label_fontstyle = st.sidebar.selectbox("Axis label font style", ["normal", "italic", "oblique"], index=0)
        tick_fontsize = st.sidebar.slider("Tick label font size", 8, 20, 10)

        # Axis range customization
        st.sidebar.title("Axis Range Customization")
        x_min = st.sidebar.number_input("X-axis min", value=None, step=1.0, format="%.2f")
        x_max = st.sidebar.number_input("X-axis max", value=None, step=1.0, format="%.2f")
        y_min = st.sidebar.number_input("Y-axis min", value=None, step=1.0, format="%.2f")
        y_max = st.sidebar.number_input("Y-axis max", value=None, step=1.0, format="%.2f")

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

        # Save settings to a file
        if st.sidebar.button("Save Settings to File"):
            settings_file_buffer = BytesIO()
            pickle.dump(settings, settings_file_buffer)
            settings_file_buffer.seek(0)
            st.download_button(
                label="Download Settings File",
                data=settings_file_buffer,
                file_name="plot_settings.pkl",
                mime="application/octet-stream"
            )

        # Global plot customizations
        grid = st.sidebar.checkbox("Show grid", value=True)
        title = st.sidebar.text_input("Plot title", "Gradient Norm vs Learning Steps")
        x_label = st.sidebar.text_input("X-axis label", "Learning Steps (Iterations)")
        y_label = st.sidebar.text_input("Y-axis label", "Gradient Norm")

        ax.set_title(title, fontsize=title_fontsize, fontstyle=title_fontstyle)
        ax.set_xlabel(x_label, fontsize=label_fontsize, fontstyle=label_fontstyle)
        ax.set_ylabel(y_label, fontsize=label_fontsize, fontstyle=label_fontstyle)
        ax.tick_params(axis='both', labelsize=tick_fontsize)

        # Apply axis limits if specified
        if x_min is not None or x_max is not None:
            ax.set_xlim(left=x_min, right=x_max)
        if y_min is not None or y_max is not None:
            ax.set_ylim(bottom=y_min, top=y_max)

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
