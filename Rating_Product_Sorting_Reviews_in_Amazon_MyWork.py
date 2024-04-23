
###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# İş Problemi
###################################################

# E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
# Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak, satıcılar için ürünün öne çıkması ve satın
# alanlar için sorunsuz bir alışveriş deneyimi demektir. Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması
# olarak karşımıza çıkmaktadır. Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp
# hem de müşteri kaybına neden olacaktır. Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler
# ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

###################################################
# Veri Seti Hikayesi
###################################################

# Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
# Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı

import pandas as pd
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.set_option("display.width",500)
pd.set_option("display.expand_frame_repr",False)
pd.set_option("display.float_format",lambda x: "%.5f" %x)

###################################################
# GÖREV 1: Average Rating'i Güncel Yorumlara Göre Hesaplayınız ve Var Olan Average Rating ile Kıyaslayınız.
###################################################

# Paylaşılan veri setinde kullanıcılar bir ürüne puanlar vermiş ve yorumlar yapmıştır.
# Bu görevde amacımız verilen puanları tarihe göre ağırlıklandırarak değerlendirmek.
# İlk ortalama puan ile elde edilecek tarihe göre ağırlıklı puanın karşılaştırılması gerekmektedir.

###################################################
# Adım 1: Veri Setini Okutunuz ve Ürünün Ortalama Puanını Hesaplayınız.
###################################################
df = pd.read_csv("Case Study I/RatingProductSortingReviewsinAmazon-221119-111357/Rating Product&SortingReviewsinAmazon/amazon_review.csv")
df.head(10)
df.shape
df = df[["reviewerID","overall","reviewTime","day_diff","helpful_yes","total_vote"]]

# Ürünün Ortalama Puanı
df["overall"].mean()

###################################################
# Adım 2: Tarihe Göre Ağırlıklı Puan Ortalamasını Hesaplayınız.
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

# Adım 3: Ağırlıklandırılmış puanlamada her bir zaman diliminin ortalamasını karşılaştırıp yorumlayınız.
df.loc[df["day_diff"] < df["day_diff"].quantile(0.25),"overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.25)) & (df["day_diff"] < df["day_diff"].quantile(0.5)), "overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.5)) & (df["day_diff"] < df["day_diff"].quantile(0.75)), "overall"].mean()
df.loc[(df["day_diff"] > df["day_diff"].quantile(0.75)), "overall"].mean()


###################################################
# Görev 2: Ürün için Ürün Detay Sayfasında Görüntülenecek 20 Review'i Belirleyiniz.
###################################################

###################################################
# Adım 1. helpful_no Değişkenini Üretiniz
###################################################
# Not:
# total_vote bir yoruma verilen toplam up-down sayısıdır.
# up, helpful demektir.
# veri setinde helpful_no değişkeni yoktur, var olan değişkenler üzerinden üretilmesi gerekmektedir.

df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
df.head(30)

###################################################
# Adım 2. score_pos_neg_diff, score_average_rating ve wilson_lower_bound Skorlarını Hesaplayıp Veriye Ekleyiniz
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
# Yoruma ve sansa yer bırakmadan, güvenebilecegimiz istatistiki bir metrik ile sıralama gercekleştirmek istersek kullanırız.
# İlgili yorumun like-dislike sayıları üzerinden güven aralıgı olusturur.
# Yani bernoulli parametresi p için bir güven aralıgı hesaplar.
# odagı like oranıdır.(up)
# up için bir güven aralıgı hesaplanır.
# Bu aralıgın min degerini kullanarak yani en kotu ihtimali degerlendirerek bir skor olusturur.

# Bernoulli dagılımı kullanılarak bir hesaplama gercekleştirir.
# Bernoilli dagılımı: rastgele bir degişkenin olası iki sonucu oldugunda kullanılan olasılık hesabıdır.

# confidence: şansa bırakmamak adına kabul gören orandır.
def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasındaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

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
# Adım 3. 20 Yorumu Belirleyiniz ve Sonuçları Yorumlayınız.
###################################################
df.sort_values("score_pos_neg_diff", ascending=False).head(20)
df.sort_values("score_average_rating", ascending=False).head(20)
df.sort_values("wilson_lower_bound", ascending=False).head(20)
