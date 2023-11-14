# Multiuse libraries
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords

# ML libraries
import pickle
import tensorflow as tf
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences

# Visualization libraries
from wordcloud import WordCloud
from collections import Counter
import base64
from io import BytesIO

# Youtube API Libraries
from googleapiclient.discovery import build
import googleapiclient.discovery
import googleapiclient.errors
import os
import requests


# model = tf.saved_model.load('C:\\Users\\Lenovo\\Downloads\\Flask-Web-App-Tutorial\\website\\LSTM_GL_1L\LSTM_GL_1L')

model = tf.keras.models.load_model('model_1.h5')
with open('tokenizer.pkl', 'rb') as handle:
    tokenizer = pickle.load(handle)

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

nltk.download('stopwords')
stopwords_list = stopwords.words('english')

def preprocess_text(sen):
    sen = sen.lower()
    # Remove html tags
    sentence = remove_tags(sen)
    # Remove punctuations and numbers
    sentence = re.sub('[^a-zA-Z]', ' ', sentence)
    # Single character removal
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)  # When we remove apostrophe from the word "Mark's", the apostrophe is replaced by an empty space. Hence, we are left with single character "s" that we are removing here.
    # Remove multiple spaces
    sentence = re.sub(r'\s+', ' ', sentence)  # Next, we remove all the single characters and replace it by a space which creates multiple spaces in our text. Finally, we remove the multiple spaces from our text as well.
    # Remove Stopwords
    pattern = re.compile(r'\b(' + r'|'.join(stopwords_list) + r')\b\s*')
    sentence = pattern.sub('', sentence)
    return sentence

def simple_prediction(text):
    text = preprocess_text(text)
    text = tokenizer.texts_to_sequences([text])
    text = pad_sequences(text, padding='post', truncating='post', maxlen=25)
    if tf.squeeze(tf.round(model(text))) == 0:
        preds = "Negative"
    elif tf.squeeze(tf.round(model(text))) == 1:
        preds = "Positive"
    return preds

def custom_prediction(data, x_data, type=0):
    x = []
    sentences = data[x_data].to_list()
    for sen in sentences:
        x.append(preprocess_text(sen))
    x = tokenizer.texts_to_sequences(x)
    x = pad_sequences(x, padding="post", truncating="post", maxlen = 25)
    model_preds = model.predict(x)
    data['Predictions'] = model_preds
    if type == 0:
        data['Predictions'] = round(data['Predictions'])
        data['Predictions'] = data['Predictions'].replace(1, 'Positive')
        data['Predictions'] = data['Predictions'].replace(0, 'Negative')
    return data

def word_cloud(df, column):
    tokens = [token for sentence in df[column].apply(preprocess_text) for token in sentence.split()]
    wc = WordCloud(background_color='white', width=480, height=360).generate_from_frequencies(dict(Counter(tokens)))
    wc_img = wc.to_image()
    with BytesIO() as buffer:
        wc_img.save(buffer, 'png')
        image_data = base64.b64encode(buffer.getvalue()).decode()
    return image_data

def word_table(df, column):
    tokens = [token for sentence in df[column].apply(preprocess_text) for token in sentence.split()]
    token_dict = dict(Counter(tokens))
    sorted_dict = sorted(token_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_df = pd.DataFrame(sorted_dict, columns=['Word', 'Frequency Count'])
    return sorted_df

def yt_videos(terms, order='relevance'):
    api_key = 'AIzaSyC6SvVnvBR8RpMmzw6RpqYn1IUzGUCVfN0'
    search_terms = terms
    max_results = 5
    url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&key={}&maxResults={}&order={}'.format(search_terms, api_key, max_results, order)
    response = requests.get(url)
    results = response.json()

    # Extract the video IDs
    video_ids = []
    for item in results['items']:
        video_ids.append(item['id']['videoId'])

    videos_df = pd.DataFrame()

    for video_id in video_ids:
        url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={}&key={}'.format(video_id, api_key)
        response = requests.get(url)
        results = response.json()

        published_date = results['items'][0]['snippet']['publishedAt']
        title = results['items'][0]['snippet']['title']

        # Concatenate the temporary dataframe to the videos dataframe
        video_temp_df = pd.DataFrame({'Video_ID': video_id, 'Date': published_date[:10], 'Title': title}, index=[0])
        videos_df = pd.concat([videos_df, video_temp_df], ignore_index=True)

    return videos_df

def yt_comments(df, order):
    comments_df = pd.DataFrame()
    api_key = 'AIzaSyC6SvVnvBR8RpMmzw6RpqYn1IUzGUCVfN0'
    video_id_list = df['Video_ID']
    video_title_list = df['Title']
    for video_id, video_title in zip(video_id_list, video_title_list):
        url1 = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={}&key={}&order={}'.format(video_id, api_key, order)
        response1 = requests.get(url1)
        results1 = response1.json()

        for item in results1['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            updated_date = item['snippet']['topLevelComment']['snippet']['updatedAt']
            # Create a temporary dataframe
            comment_temp_df = pd.DataFrame({'Date': updated_date[:10], 'Video_Title': video_title, 'Comment': comment}, index=[0])

            # Concatenate the temporary dataframe to the comments dataframe
            comments_df = pd.concat([comments_df, comment_temp_df], ignore_index=True)
    return comments_df