import pandas as pd
import json
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel 
true = True
false = False
# Create your views here.
@api_view(['GET', 'POST'])
def api_recommend(request):
    response_dict = {}
    if request.method == 'POST':
        data=request.data
        #print(data["allProducts"])
        #print(data["viewedProductNames"])
        #response_dict = {"allProducts": data["allProducts"]}
        df = pd.json_normalize(data["allProducts"])
        df.insert(loc=0, column='id', value=df.index)
        #print(df)
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(df['description'])
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
        results = {}
        for idx, row in df.iterrows():
            similar_indices = cosine_similarities[idx].argsort()[:-100:-1] 
            similar_items = [(cosine_similarities[idx][i], df['id'][i]) for i in similar_indices] 
            results[row['id']] = similar_items[1:]
            
        def item(id):  
            return df.loc[df['id'] == id]['description'].tolist()[0].split(' - ')[0]
        def get_id_from_product_name(productName):
        	return df[df['productName'] == productName]["id"].values[0]
        def get__id_from_product_name(productName):
	        return df[df.productName == productName]["_id"].values[0]
     
        recommendedProducts = []
        recommendedProductsScore = {}
        for productName in data["viewedProductNames"]:
            #print(productName)
            item_id = get_id_from_product_name(productName)  
            #print(item_id)
            recs = results[item_id][:9]   
            for rec in recs:
                recommendedProducts.append(df[df['description']==item(rec[1])]['productName'].values[0])
                recommendedProductsScore[df[df['description']==item(rec[1])]['productName'].values[0]] = rec[0]
            recommendedProductsSorted = dict( sorted(recommendedProductsScore.items(),
                           key=lambda item: item[1],
                           reverse=True))
            new_df=pd.DataFrame(columns=df.columns)
            for product in recommendedProductsSorted.keys():
                new_df=new_df.append(df[df["productName"]==product],ignore_index=True)
            new_df = new_df[:9]
    #print(new_df)
            response_dict = {"recommendedProducts": new_df.to_json(orient='records')}
            print(new_df.to_json(orient='records'))
    return Response(response_dict, status=status.HTTP_201_CREATED)

