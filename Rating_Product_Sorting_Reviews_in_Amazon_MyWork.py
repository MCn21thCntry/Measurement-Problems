###################################################
# PROJECT: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# Business Problem
###################################################

# One of the most important problems in e-commerce is accurately calculating the ratings given to products after purchase.
# Solving this problem means providing more customer satisfaction for the e-commerce site, highlighting the product for sellers,
# and ensuring a seamless shopping experience for buyers. Another problem is sorting the reviews given to products correctly.
# Since misleading reviews can directly affect the product's sales, it can lead to both financial loss and customer loss. 
# Solving these two fundamental problems will increase sales for e-commerce sites and sellers, while customers will complete their
# purchase journey smoothly.

###################################################
# Data Set Story
###################################################

# This data set containing Amazon product data includes product categories and various metadata.
# It includes user ratings and reviews for the product that received the most reviews in the Electronics category.

# Variables:
# reviewerID: User ID
# asin: Product ID
# reviewerName: User Name
# helpful: Helpful review rating
# reviewText: Review
# overall: Product rating
# summary: Review summary
# unixReviewTime: Review time
# reviewTime: Review time Raw
# day_diff: Number of days elapsed since the review
# helpful_yes: Number of times the review was found helpful
# total_vote: Number of votes given to the review

import pandas as pd
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.set_option("display.width",500)
pd.set_option("display.expand_frame_repr",False)
pd.set_option("display.float_format",lambda x: "%.5f" %x)

Below is the translation of the provided code snippet into English:

###################################################
# TASK 1: Calculate Average Rating Based on Recent Reviews and Compare with Existing Average Rating
###################################################

# Users in the shared data set have given ratings and reviews to a product.
# The goal in this task is to evaluate the given ratings by weighting them based on the date.
# It is necessary to compare the initial average rating with the weighted rating based on the date.

###################################################
# Step 1: Read the Data Set and Calculate the Average Rating of the Product
###################################################

df = pd.read_csv("Case Study I/RatingProductSortingReviewsinAmazon-221119-111357/Rating Product&SortingReviewsinAmazon/amazon_review.csv")
df.head(10)
df.shape
df = df[["reviewerID","overall","reviewTime","day_diff","helpful_yes","total_vote"]]

# Product's Average Rating
df["overall"].mean()

###################################################
# Step 2: Calculate the Time-Weighted Average Rating
###################################################
df.describe().T
df.info()
df["reviewTime"] = pd.to_datetime(df["reviewTime"])
df.info()

df.loc[df["day_diff"] < df["day_diff"].quantile(0.25),"overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.25)) & (df["day_diff"] <= df["day_diff"].quantile(0.5)), "overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.5)) & (df["day_diff"] <= df["day_diff"].quantile(0.75)), "overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.75)), "overall"].mean()

def time_weighted_overall(dataframe, w1=40, w2=26, w3=14, w4=10):
    return dataframe.loc[df["day_diff"] <= dataframe["day_diff"].quantile(0.25), "overall"].mean() * w1/100 + \
        dataframe.loc[(df["day_diff"] > dataframe["day_diff"].quantile(0.25)) & (
                dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.5)), "overall"].mean() * w2/100 + \
        dataframe.loc[(df["day_diff"] > dataframe["day_diff"].quantile(0.5)) & (
                dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.75)), "overall"].mean() * w3/100 + \
        dataframe.loc[(df["day_diff"] > dataframe["day_diff"].quantile(0.75)), "overall"].mean() * w4/100

df["time_based_weighted_overall"] = time_weighted_overall(df)

# Step 3: Compare and Interpret the Average Ratings for Each Time Interval in the Weighted Rating
df.loc[df["day_diff"] < df["day_diff"].quantile(0.25),"overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.25)) & (df["day_diff"] < df["day_diff"].quantile(0.5)), "overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.5)) & (df["day_diff"] < df["day_diff"].quantile(0.75)), "overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.75)), "overall"].mean()


###################################################
# Task 2: Determine the 20 Reviews to be Displayed on the Product Detail Page
###################################################

###################################################
# Step 1. Generate the helpful_no Variable
###################################################
# Note:
# total_vote is the total up-down count given to a review.
# up represents helpful.
# There is no helpful_no variable in the dataset; it needs to be generated from existing variables.

df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
df.head(30)

###################################################
# Step 2. Calculate and Add the score_pos_neg_diff, score_average_rating, and wilson_lower_bound Scores to the Data
###################################################

#### score_pos_neg_diff
def score_pos_neg_diff(up, down):
    return up - down

df["score_pos_neg_diff"] = df.apply(lambda x: score_pos_neg_diff(x["helpful_yes"], x["helpful_no"]),axis=1)
df.sort_values("score_pos_neg_diff",ascending=False).head(10)

#### score_average_rating
def score_average_rating(up, down):
    if up + down == 0:
        return 0
    return up / (up+down)

df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]),axis=1)
df.sort_values("score_average_rating",ascending=False).head(10)

#### Wilson Lower Bound:
# If we want to rank using a statistical metric we can trust without leaving room for comments and chance.
# It creates a confidence interval based on the like-dislike counts of the relevant comment.
# It calculates a confidence interval for the Bernoulli parameter p.
# The focus is on the like rate (up).
# A confidence interval is calculated for up.
# By using the minimum value of this interval, it evaluates the worst-case scenario to create a score.

# It performs a calculation using the Bernoulli distribution.
# Bern

Bernoulli distribution: A probability calculation used when a random variable has two possible outcomes.

Confidence: The accepted rate to avoid leaving it to chance.


def wilson_lower_bound(up, down, confidence=0.95):
    """
    Calculate Wilson Lower Bound Score

    - The lower bound of the confidence interval to be calculated for the Bernoulli parameter p is considered as the WLB score.
    - Used for ranking products based on the calculated score.
    - Note:
    If the scores are between 1-5, they are marked as negative for 1-3 and positive for 4-5, and can be adjusted to fit Bernoulli distribution. This brings some problems along with it. Therefore, it is necessary to do Bayesian average rating.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"],x["helpful_no"]), axis=1)
df.sort_values("wilson_lower_bound",ascending=False).head(10)

##################################################
# Step 3. Identify 20 Comments and Interpret the Results.
###################################################
df.sort_values("score_pos_neg_diff", ascending=False).head(20)
df.sort_values("score_average_rating", ascending=False).head(20)
df.sort_values("wilson_lower_bound", ascending=False).head(20)


