import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="EduPro Instructor Analytics",
    layout="wide"
)

st.title("EduPro Instructor Performance & Course Quality Dashboard")

@st.cache_data
def load_data():
    teachers = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Teachers")
    courses = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Courses")
    transactions = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Transactions")
    df = transactions.merge(teachers, on="TeacherID", how="left")
    df = df.merge(courses, on="CourseID", how="left")
    return df

df = load_data()

st.sidebar.header(" Filters")

expertise_filter = st.sidebar.multiselect(
    "Select Expertise",
    options=df["Expertise"].unique(),
    default=df["Expertise"].unique()
)

category_filter = st.sidebar.multiselect(
    "Select Course Category",
    options=df["CourseCategory"].unique(),
    default=df["CourseCategory"].unique()
)

rating_range = st.sidebar.slider(
    "Instructor Rating Range",
    0.0, 5.0, (2.5, 5.0)
)

filtered_df = df[
    (df["Expertise"].isin(expertise_filter)) &
    (df["CourseCategory"].isin(category_filter)) &
    (df["TeacherRating"].between(rating_range[0], rating_range[1]))
]

st.subheader(" Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Teacher Rating", round(filtered_df["TeacherRating"].mean(), 2))
col2.metric("Avg Course Rating", round(filtered_df["CourseRating"].mean(), 2))
col3.metric("Total Instructors", filtered_df["TeacherID"].nunique())
col4.metric("Total Enrollments", filtered_df.shape[0])

st.subheader(" Instructor Performance Leaderboard")

leaderboard = (
    filtered_df.groupby("TeacherName")["TeacherRating"]
    .mean()
    .sort_values(ascending=False)
)

st.dataframe(leaderboard.reset_index())

st.subheader(" Experience vs Instructor Rating")

fig1, ax1 = plt.subplots()
sns.scatterplot(
    x="YearsOfExperience",
    y="TeacherRating",
    data=filtered_df,
    ax=ax1
)
ax1.set_title("Experience vs Instructor Rating")
st.pyplot(fig1)

st.subheader(" Instructor Rating vs Course Rating")

fig2, ax2 = plt.subplots()
sns.regplot(
    x="TeacherRating",
    y="CourseRating",
    data=filtered_df,
    ax=ax2
)
ax2.set_title("Instructor Rating vs Course Rating")
st.pyplot(fig2)

st.subheader(" Course Quality Heatmap")

heatmap_data = filtered_df.pivot_table(
    values="CourseRating",
    index="CourseCategory",
    columns="CourseLevel",
    aggfunc="mean"
)

fig3, ax3 = plt.subplots()
sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", ax=ax3)
ax3.set_title("Average Course Rating by Category & Level")
st.pyplot(fig3)

st.subheader(" Expertise-wise Performance")

fig4, ax4 = plt.subplots()
sns.barplot(
    x="Expertise",
    y="CourseRating",
    data=filtered_df,
    ax=ax4
)
ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45)
ax4.set_title("Expertise vs Course Rating")
st.pyplot(fig4)

st.subheader(" Enrollment Impact by Instructor Rating")

filtered_df["InstructorTier"] = pd.cut(
    filtered_df["TeacherRating"],
    bins=[0, 3, 4, 5],
    labels=["Low", "Mid", "High"]
)

enrollment = filtered_df.groupby("InstructorTier")["TransactionID"].count()

fig5, ax5 = plt.subplots()
enrollment.plot(kind="bar", ax=ax5)
ax5.set_title("Enrollments by Instructor Rating Tier")
st.pyplot(fig5)
