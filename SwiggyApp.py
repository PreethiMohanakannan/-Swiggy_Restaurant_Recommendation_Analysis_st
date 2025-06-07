###################################################################################
import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Page setup
st.set_page_config(page_title="🍽️ Swiggy Restaurant Recommendation", layout="wide")

# Load Clean Data
cleaned_df = pd.read_csv("Cleaned_Data.csv", index_col=0)

# Load Models & Encoded Data
with open("final_encoded_clusters.pkl", "rb") as f:
    models = pickle.load(f)

# Extract from models
kmeans = models["kmeans"]
encoded_df = models["encoded_data"]  

cluster_labels = models["clusters"]  

# Reattach original columns to encoded_df
encoded_df['name'] = cleaned_df['name'].values
encoded_df['city'] = cleaned_df['city'].values
encoded_df['rating'] = cleaned_df['rating'].values
encoded_df['cost'] = cleaned_df['cost'].values


# Display the updated DataFrame in Streamlit
st.dataframe(encoded_df)

# Styling
st.markdown("<style>body {font-family: 'Segoe UI';}</style>", unsafe_allow_html=True)

# Title & Image
col1, col2, col3 = st.columns(3)
with col2:
    st.image("swigg_image.jpg", width=300)

st.markdown("<h1 style='text-align: center; color: #FF5733;'>🍽️ Swiggy Restaurant Recommendation</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #ccc;' />", unsafe_allow_html=True)

# Sidebar Filters
with st.sidebar:
    
    st.markdown("""
        <div style='
        display: inline-block;
        background-color: #E56B06;
        color: White;
        font-weight: bold;
        font-size: 35px;
        padding: 16px 75px;
        border-radius: 15px;
        font-family: Arial, sans-serif;
        '> SwiggY </div>
    """, unsafe_allow_html=True)
    st.header("🎯 FILTERS")
    available_cities = cleaned_df["city"].dropna().unique()
    available_cuisines = cleaned_df["cuisine"].dropna().unique()
  
    city = st.selectbox("Select City 📍", sorted(available_cities))
    min_rating = st.slider("Minimum Rating:", 1.0, 5.0, 4.0)
    max_cost = st.slider("Maximum Price per Meal (₹):", 100, 1000, 500)
    st.markdown("<label class='custom-cuisine-label'>Pick your Cuisine</label>", unsafe_allow_html=True)
    selected_cuisines = st.multiselect("", options=sorted(available_cuisines), key="Cuisine_selector")
    

# Recommendation Logic
st.subheader("🍴 Recommended Restaurants")

# Apply base filters first
base_filtered = encoded_df[
    (encoded_df["city"] == city) &
    (encoded_df["rating"] >= min_rating) &
    (encoded_df["cost"] <= max_cost)
    ]

# Apply cuisine filter if selected
if selected_cuisines:
    cuisine_pattern = '|'.join(selected_cuisines)
    base_filtered = base_filtered[base_filtered['name'].isin(
        cleaned_df[cleaned_df["cuisine"].str.contains(cuisine_pattern, case=False, na=False)]["name"]
    )]

# Find common cluster in filtered subset and recommend restaurants from same cluster
if not base_filtered.empty:
    
    target_cluster = base_filtered["Cluster"].mode()[0]

    
    recommendations = encoded_df[
        (encoded_df["Cluster"] == target_cluster) &
        (encoded_df["city"] == city) &
        (encoded_df["rating"] >= min_rating) &
        (encoded_df["cost"] <= max_cost) 
    ]

    if not recommendations.empty:
        for _, row in recommendations.head(10).iterrows():
            st.write(f"**🍽️ {row['name']}** - ⭐ {row['rating']} | ₹{row['cost']} | {row['city']}")
            
            # Order Now Button
            if st.button(f"Order Now at {row['name']}", key=row["name"]):
                st.success(f"Redirecting to {row['name']}... (Add actual URL here)")
            
        st.dataframe(recommendations[["name", "city", "rating", "cost"]].head(10))
    else:
        st.warning("❌ No matching restaurants found. Try adjusting your filters!")
else:
    st.info("ℹ️ Please adjust your filters to view recommendations.")

     
###################################################################################
