#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olanbombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.


#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleri ab_testing.xlsx excel’inin ayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBidding uygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç

#####################################################
# Proje Görevleri
#####################################################

#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.

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

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

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

# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df_control["group"] = "control"
df_test["group"] = "test"

df = pd.concat([df_control, df_test], axis=0, ignore_index=True)
# ignore_index=True ilk 40 tan sonra 41 diye devam etmesi içindir.
df.tail()
df.shape

df.groupby("group").agg({"Purchase": "mean"}) # fark var gibi fakat istatistiksel olarak anlamlı bir fark mı?

df.groupby("group")["Earning"].mean() # fark var gibi fakat ist. olarak kanıtlanmalı

#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.

# H0 : M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark yoktur.)
# H1 : M1!= M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark vardır.)

# H0 : M1 = M2 (Kontrol grubu ve test grubu gelir ortalamaları arasında fark yoktur.)
# H1 : M1!= M2 (Kontrol grubu ve test grubu gelir ortalamaları arasında fark vardır.)

# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz.
df.groupby("group").agg({"Purchase": "mean"}) # fark var gibi fakat istatistiksel olarak anlamlı bir fark mı?

# Adım 2: Kontrol ve test grubu için earning(kazanç) ortalamalarını analiz ediniz.
df.groupby("group")["Earning"].mean() # fark var gibi fakat istatistiksel olarak anlamlı bir fark mı?

#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz
# Normallik Varsayımı :
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır
# p < 0.05 H0 RED
# p > 0.05 H0 REDDEDİLEMEZ
# Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu ?
# Elde edilen p-valuedeğerlerini yorumlayınız.


### *** Normal Dağılım: Ortalama ve medyan birbirine eşittir. ***

## for Purchase:
test_stat, pvalue = shapiro(df.loc[df["group"] == "control", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.5891
# HO reddedilemez. Control grubunun değerleri normal dağılım varsayımını sağlamaktadır.
test_stat, pvalue = shapiro(df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.1541
# HO reddedilemez. Control grubunun değerleri normal dağılım varsayımını sağlamaktadır.

## for Earning:
test_stat, pvalue = shapiro(df.loc[df["group"]=="test", "Earning"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value = 0.6163, HO REDDEDİLEMEZ
test_stat, pvalue = shapiro(df.loc[df["group"]=="control", "Earning"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p - value = 0.5306, HO REDDEDİLEMEZ, Varyans homojenliğine gidelim


#####################################################
# Normal Dagılımı gözlemlemek adına görselleştirelim:

# Normal Dağılım: Ortalama ve medyan birbirine eşittir.

# Histogram, nümerik değişkenlerin dağılımlarını görselleştirmede kullanılır.
# Tanımlanan grafik değişkenin histogram ve yoğunluğunu gösterir.
# Sadece histogramı görmek istersek kde parametresini False yapmamız yeterlidir.

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

# Her ikisinin de dagılımını gözlemlemek adına: Purchase
for group in list(df["group"].unique()):
    pvalue = shapiro(df.loc[df["group"] == group, "Purchase"])[1] #shapironun 1. indexteki degeri
    print(group,'p-value = %.4f' % pvalue)

# Her ikisinin de dagılımını gözlemlemek adına: Earning
for group_E in list(df["group"].unique()):
    pvalue = shapiro(df.loc[df["group"]==group_E, "Earning"])[1]
    print(group, "p-value = %.4f" %pvalue)

# Varyans Homojenliği :

# grupların varyanslarının birbirine benzer olduğunu ifade eder.

# H0: Varyanslar homojendir.
# H1: Varyanslar homojen Değildir.
# p < 0.05 H0 RED
# p > 0.05 H0 REDDEDİLEMEZ
# Kontrol ve test grubu için varyans homojenliğinin sağlanıp sağlanmadığını Purchase değişkeni üzerinden test ediniz.
# Test sonucuna göre normallik varsayımı sağlanıyor mu? Elde edilen p-value değerlerini yorumlayınız.

# for Purchase:
test_stat, pvalue = levene(df.loc[df["group"] == "control", "Purchase"],
                           df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.1083
# HO reddedilemez. Control ve Test grubunun değerleri varyans homejenliği varsayımını sağlamaktadır.
# Varyanslar Homojendir.

# for Earnings:
test_stat, pvalue = levene(df.loc[df["group"]=="control","Earning"],
                           df.loc[df["group"]=="test","Earning"])
print("Test Stat = %.4f, p-value = %.4f" %(test_stat, pvalue))
# p-value = 0.5540
# HO REDDEDİLEMEZ, Varyanlar homojendir. Hadi parametrik olan t teste


# Adım 2: Normallik Varsayımı ve VaryansHomojenliği sonuçlarına göre uygun testi seçiniz

# Varsayımlar sağlandığı için bağımsız iki örneklem t testi (parametrik test) yapılmaktadır.
# H0: M1 = M2 (Kontrol grubu ve test grubu satın alma(2. durum için --> getirisi) ortalamaları arasında ist. ol.anl.fark yoktur.)
# H1: M1 != M2 (Kontrol grubu ve test grubu satın alma(2. durum için --> getirisi) ortalamaları arasında ist. ol.anl.fark vardır)
# p<0.05 HO RED , p>0.05 HO REDDEDİLEMEZ

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True) # Varyans homojemligi saglanmıyor olsaydı equal_var = False Weltch testini yapmasını saglardı.
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.3493, H0 REDDEDİLEMEZ, her iki grup arasında istatistiksel olarak anlamlı bir fark yoktur.
# Gözüken fark şans eseri olmuştur, güvenilirliği yoktur.

# for Earning:
test_stat, pvalue = ttest_ind(df.loc[df["group"]=="control","Earning"],
                              df.loc[df["group"]=="test","Earning"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value = 0.0000, H0 RED, ARALARINDAKİ GELİR FARKI İSTATİSTİKSEL OLARAK ANLAMLI.
# Şans eseri olarak ortaya çıkmamıştır.


# Adım 3: Test sonucunda elde edilen p_valuedeğerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

# Purchase p-value=0.3493
# HO reddedilemez. Kontrol ve test grubu satın alma ortalamaları arasında istatistiksel olarak anlamlı farklılık yoktur.

# Earning p-value = 0.0000,
# H0 RED, ARALARINDAKİ GELİR FARKI İSTATİSTİKSEL OLARAK ANLAMLI.

##############################################################
# GÖREV 4 : Sonuçların Analizi
##############################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.
	# shapiro'yu Normallik Dağılımı olup olmadığını görmek için
	# levene'i Varyans Homojenliği'nin olup olmadığını görmek için
	# ve t test'i sonucu elde edebilmek için kullandım.

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.
	# Satış sayılarında; yeni elde edilen yöntem satı sayılarını arttırıp arttırmayacağı konusunda güven vermediği için
	# eski yöntemin veya yeni yöntemin kullanılmasında pek fark olmayacaktır.
	# Fakat yeni yöntemin gelir konusunda daha güvenilir olduğunu gözlemledik
	# bu yüzden yeni yöntemin kullanılması daha fazla kazanç sağlayacaktır.
