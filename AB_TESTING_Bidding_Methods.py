#####################################################
# Comparison of Conversion Rates of Bidding Methods with AB Testing
#####################################################

#####################################################
# Business Problem
#####################################################

# Facebook son zamanlarda mevcut "maksimum teklif verme" teklif verme türüne alternatif olarak "ortalama teklif verme" adlı yeni bir teklif türü tanıttı. Müşterilerimizden bombabomba.com, bu yeni özelliği test etmeye karar verdi ve ortalama teklif vermenin maksimum teklif vermeden daha fazla dönüşüm getirip getirmediğini belirlemek için bir A/B testi yapmak istiyor. A/B testi 1 aydır devam ediyor ve şimdi bombabomba.com, bu A/B testinin sonuçlarını analiz etmenizi bekliyor. Bombabomba.com için nihai başarı metriği Satın Alma'dır. Bu nedenle, istatistiksel testler için Satın Alma metriğine odaklanılmalıdır.

#####################################################
# Data Set Story
#####################################################

# Bu veri seti, bir şirketin web sitesi hakkında, görülen ve tıklanan reklam sayısı ile gelir bilgilerini içerir. Kontrol ve Test olmak üzere iki ayrı veri seti bulunmaktadır. Bu veri setleri, ab_testing.xlsx excel dosyasının ayrı sayfalarında bulunmaktadır. Kontrol grubuna Maksimum Teklif Verme uygulanmıştır ve Test grubuna Ortalama Teklif Verme uygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Gösterilen reklama tıklama sayısı
# Purchase: Reklama tıkladıktan sonra satın alınan ürün sayısı
# Earning: Ürün satın alındıktan sonra elde edilen gelir

#####################################################
# Project Tasks
#####################################################

#####################################################
# Task 1: Data Preparation and Analysis
#####################################################

# Step 1: Read the data set consisting of control and test group data named ab_testing_data.xlsx. Assign control and test group data to separate variables.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, ttest_ind
import seaborn as sbn

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

dataframe_control = pd.read_excel("ABTesti-221114-234653/ABTesti/ab_testing.xlsx", sheet_name="Control Group")
dataframe_test = pd.read_excel("ABTesti-221114-234653/ABTesti/ab_testing.xlsx" , sheet_name="Test Group")

df_control = dataframe_control.copy()
df_test = dataframe_test.copy()

# Step 2: Analyze the control and test group data.

def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head())
    print("##################### Tail #####################")
    print(dataframe.tail())
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df_control)
check_df(df_test)


# Step 3: After the analysis process, merge the control and test group data using the concat method.

df_control["group"] = "control"
df_test["group"] = "test"

df = pd.concat([df_control, df_test], axis=0, ignore_index=True)
# ignore_index=True is used for continuing indexing after 40 as 41, and so on.
df.tail()
df.shape

df.groupby("group").agg({"Purchase": "mean"}) # Is there a difference, and is it statistically significant?

df.groupby("group")["Earning"].mean() # There seems to be a difference, but it needs to be statistically proven.

#####################################################
# Task 2: Definition of A/B Test Hypothesis
#####################################################

# Step 1: Define the hypothesis.

# H0: M1 = M2 (There is no difference between the average purchases of the control group and the test group.)
# H1: M1 != M2 (There is a difference between the average purchases of the control group and the test group.)

# H0: M1 = M2 (There is no difference between the average earnings of the control group and the test group.)
# H1: M1 != M2 (There is a difference between the average earnings of the control group and the test group.)

# Step 2: Analyze the purchase (earnings) averages for the control and test groups.
df.groupby("group").agg({"Purchase": "mean"}) # There seems to be a difference, but is it statistically significant?

# Step 2: Analyze the earning averages for the control and test groups.
df.groupby("group")["Earning"].mean() # There seems to be a difference, but is it statistically significant?

#####################################################
# Task 3: Conducting the Hypothesis Test
#####################################################

# Step 1: Before conducting the hypothesis test, check the assumptions. These are Normality Assumption and Homogeneity of Variances.

# Check whether the control and test groups meet the normality assumption separately based on the Purchase variable.
# Normality Assumption:
# H0: The normal distribution assumption is met.
# H1: The normal distribution assumption is not met.
# p < 0.05 H0 REJECTED
# p > 0.05 H0 CANNOT BE REJECTED
# Test whether the normality assumption is satisfied for the control and test groups?
# Interpret the obtained p-values.


### *** Normal Distribution: The mean and median are equal. ***

## for Purchase:
test_stat, pvalue = shapiro(df.loc[df["group"] == "control", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.5891
# H0 cannot be rejected. The values of the control group satisfy the normal distribution assumption.
test_stat, pvalue = shapiro(df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.1541
# H0 cannot be rejected. The values of the test group satisfy the normal distribution assumption.

## for Earning:
test_stat, pvalue = shapiro(df.loc[df["group"]=="test", "Earning"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value = 0.6163, H0 CANNOT BE REJECTED
test_stat, pvalue = shapiro(df.loc[df["group"]=="control", "Earning"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p - value = 0.5306, H0 CANNOT BE REJECTED, Let's move on to Homogeneity of Variances


#####################################################
# Let's visualize to observe Normal Distribution:

# Normal Distribution: The mean and median are equal.

# Histogram is used to visualize the distributions of numerical variables.
# The defined plot shows the histogram and density of the variable.
# If we only want to see the histogram, we just need to set the kde parameter to False.

def create_displot(dataframe, col):
    sbn.displot(data=dataframe, x=col, kde=True)
    plt.show()

create_displot(df_control, "Purchase")
create_displot(df_control, "Earning")

df_control["Purchase"].mean()
df_control["Earning"].mean()
###################################################

test_stat, pvalue = shapiro(df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# To observe the distribution of both: Purchase
for group in list(df["group"].unique()):
    pvalue = shapiro(df.loc[df["group"] == group, "Purchase"])[1] # the value at index 1 of shapiro
    print(group,'p-value = %.4f' % pvalue)

# To observe the distribution of both: Earning
for group_E in list(df["group"].unique()):
    pvalue = shapiro(df.loc[df["group"]==group_E, "Earning"])[1]
    print(group, "p-value = %.4f" %pvalue)

# Homogeneity of Variances:

# It expresses that the variances of the groups are similar to each other.

# H0: Variances are homogeneous.
# H1: Variances are not homogeneous.
# p < 0.05 H0 REJECTED
# p > 0.05 H0 CANNOT BE REJECTED
# Test the homogeneity of variances for the Purchase variable for the control and test groups.
# According to the test result, is the normality assumption satisfied? Interpret the obtained p-value values.

# for Purchase:
test_stat, pvalue = levene(df.loc[df["group"] == "control", "Purchase"],
                           df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.1083
# H0 cannot be rejected. The values of the control and test groups satisfy the assumption of variance homogeneity.
# Variances are Homogeneous.

# for Earnings:
test_stat, pvalue = levene(df.loc[df["group"]=="control","Earning"],
                           df.loc[df["group"]=="test","Earning"])
print("Test Stat = %.4f, p-value = %.4f" %(test_stat, pvalue))
# p-value = 0.5540
# H0 CANNOT BE REJECTED, Variances are homogeneous. Let's move on to the parametric t-test.


# Step 2: Select the appropriate test according to the results of the Normality Assumption and Variance Homogeneity

# Since the assumptions are met, an independent two-sample t-test (parametric test) is performed.
# H0: M1 = M2 (There is no statistically significant difference between the control group and the test group purchase (for the second case --> return) averages.)
# H1: M1 != M2 (There is a statistically significant difference between the control group and the test group purchase (for the second case --> return) averages.)
# p<0.05 HO REJECTED, p>0.05 HO CANNOT BE REJECTED

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True) # If variance homogeneity was not provided, equal_var = False would make it perform the Welch test.
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.3493, H0 CANNOT BE REJECTED, there is no statistically significant difference between the purchase averages of both groups.
# The observed difference is due to chance, it is not reliable.

# for Earning:
test_stat, pvalue = ttest_ind(df.loc[df["group"]=="control","Earning"],
                              df.loc[df["group"]=="test","Earning"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value = 0.0000, H0 REJECTED, THE INCOME DIFFERENCE BETWEEN THEM IS STATISTICALLY SIGNIFICANT.
# It is not by chance.


# Step 3: Interpret the obtained p-value considering the test results and advise the customer accordingly.
# Purchase p-value=0.3493
# H0 cannot be rejected. There is no statistically significant difference between the purchase averages of the control and test groups.
# There will be no significant difference in using the old method or the new method since the new method did not provide confidence in increasing sales.

# Earning p-value = 0.0000,
# H0 REJECTED, THE INCOME DIFFERENCE BETWEEN THEM IS STATISTICALLY SIGNIFICANT.
# Therefore, using the new method will provide more profit as it is more reliable.
