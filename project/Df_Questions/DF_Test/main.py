import pandas as pd

ENQUIRY_COLUMNS = ["enquiry_id", "course_id", "student_name", "email",
                "phone", "quoted_fee", "discount_pct"]


def load_student_enquiries(file_path):
    df = pd.read_csv(file_path, usecols=ENQUIRY_COLUMNS)
    return df[ENQUIRY_COLUMNS]


def clean_enquiry_data(df):
    out = df.dropna(subset=["email"])
    out = out.drop_duplicates(subset="enquiry_id", keep="first")
    return out.reset_index(drop=True)


def merge_with_courses(enquiries_df, ref_file_path):
    courses = pd.read_csv(ref_file_path)
    courses = courses[["course_id", "course_name", "category",
                    "duration_months", "standard_fee"]]
    merged = enquiries_df.merge(courses, on="course_id", how="inner")
    return merged.reset_index(drop=True)


def add_net_quoted_fee(df):
    net = (df["quoted_fee"] * (1 - df["discount_pct"] / 100)).round(2)
    return df.assign(net_quoted_fee=net)


def aggregate_by_course(df):
    out = df.groupby("course_name", as_index=False).agg(
        avg_net_quoted_fee=("net_quoted_fee", "mean"),
        enquiry_count=("net_quoted_fee", "size"),
    )
    return out.reset_index(drop=True)


def finalize_summary(df):
    out = df[["course_name", "avg_net_quoted_fee", "enquiry_count"]].copy()
    out["avg_net_quoted_fee"] = out["avg_net_quoted_fee"].round(2)
    return out.sort_values("course_name").reset_index(drop=True)


if __name__ == "__main__":
    enquiries = load_student_enquiries("data/training_enquiries.csv")
    cleaned = clean_enquiry_data(enquiries)
    merged = merge_with_courses(cleaned, "data/training_courses.csv")
    with_net = add_net_quoted_fee(merged)
    aggregated = aggregate_by_course(with_net)
    print(finalize_summary(aggregated))