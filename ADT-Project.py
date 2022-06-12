# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 19:16:36 2022

@author: User
"""
import tkinter as tk
from tkinter import RIGHT, Y, Scrollbar
import spacy
import pandas
import re
import json
from textblob import TextBlob
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch, helpers
import configparser
import csv
import ssl


height = []


# Create the elasticsearch client.
config = configparser.ConfigParser()
config.read('example.ini')

es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password']),
    verify_certs=False
)

print(es.info())


def upload():
    """
       Desc: Function for uploading the user file.( Upload CSV file)
       param: None
    """
    root.filename: object = tk.filedialog.askopenfilename(initialdir="/",
                                                          title="select a file",
                                                          filetypes=(("csv files", "*.csv"),
                                                                     ("all files", "*.*")))
    return root.filename


def fileread():
    """
        Desc: Read Uploaded File
        param: None
    """
    file = pandas.read_csv(root.filename, encoding="latin-1", header=None)
    nlp = spacy.load("en_core_web_sm")
    tweets = []  # tweet list
    # Data cleaning-removing 1st column, empty rows and removing words with @
    #file = file.drop(file[0], axis=1)
    file = file[pandas.notnull(file[5])]
    file.index = range(len(file))
    counter = 0
    for line in file[5]:
        file.loc[counter, 5] = re.sub('@[a-zA-z0-9]*[^\s]', '', line)
        tweets.append(nlp(file.loc[counter, 5]))
        counter += 1
    return tweets


def sentiment():
    """
       Desc: Sentiment Analysis
       param: None
    """
    text_box.delete("1.0", tk.END)
    tweets = fileread()
    text_box.insert(tk.END, "\n\n\nSentimental Analysis\n\n\n")
    counter_positive = 0
    counter_negative = 0
    counter_neutral = 0
    for tweet in tweets:  # Sentimental Analysis logic
        text_box.insert(tk.END, tweet)
        analysis = TextBlob(tweet.text)
        new_obj = json.dumps({"polarity": analysis.sentiment.polarity,
                              "subjectivity": analysis.sentiment.subjectivity})
        text_box.insert(tk.END, new_obj)
        if analysis.sentiment[0] > 0:
            counter_positive += 1
            text_box.insert(tk.END, " [Positive]\n\n")
        elif analysis.sentiment[0] < 0:
            counter_negative += 1
            text_box.insert(tk.END, " [Negative]\n\n")
        else:
            counter_neutral += 1
            text_box.insert(tk.END, " [Neutral]\n\n")

    # Ploting graph for Sentimental Analysis
    global height
    height = [counter_positive, counter_negative, counter_neutral]


def graph_sentiment():
    global height
    labels = 'Positive', 'Negative', 'Neutral'
    colors = ['green', 'red', 'blue']
    plt.pie(height, labels=labels, colors=colors, autopct='%1.1f%%', explode=[0.05, 0.05, 0.05])
    plt.title("This is Sentimental Analysis")
    plt.show()


def upload_file():
    # Create the elasticsearch client.
    config = configparser.ConfigParser()
    config.read('example.ini')

    es = Elasticsearch(
        cloud_id=config['ELASTIC']['cloud_id'],
        http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password']),
        verify_certs=False
    )
    # Open csv file and bulk upload
    with open('Customer_reviews.csv') as f:
        reader = csv.DictReader(f)
        helpers.bulk(es, reader, index='adt-final-form-test')


def fetch_data():
    #searching data in elastic search
    result = es.search(
     index='adt-req-format',
      body = {
            "query": {
                "match": {
                        "Brand": "Amazon"
                    }
            }
        },
      size=30
    )
    print(result['hits']['hits'])


    # conversion to csv from json data received 


    with open('req-format-test.csv', 'w') as f:
        header_present  = False
        for doc in result['hits']['hits']:
            my_dict = doc['_source'] 
            if not header_present:
                w = csv.DictWriter(f, my_dict.keys())
                w.writeheader()
                header_present = True


            w.writerow(my_dict)

    print("Done writting")


def interjections():
    """
        Desc: Find Interjections
        param: None
    """
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, "\n\n\nInterjection!\n\n\n")
    intj_list = []  # interjection list

    tweets = fileread()
    length = len(tweets)
    counter_great = 0
    counter_good = 0
    counter_best = 0
    for column in range(0, length):  # Interjection logic
        temp_list = []
        for token in tweets[column]:
            if token.text == "Great":
                counter_great += 1
            if token.text == "Best":
                counter_best += 1
            if token.text == "Good":
                counter_good += 1
            
        intj_list.append(temp_list)
    
    global height
    # Ploting graph for Interjection
    height = [counter_great, counter_best, counter_good]


def graph_interjections():
    global height
    total_labels_interjection = [1, 2, 3]
    tick_label = ['Great', 'Best', 'Good']
    plt.bar(total_labels_interjection, height, tick_label=tick_label,
            width=0.5, color=['red', 'green'])
    plt.title("This is Interjection ")
    plt.show()


# This is the GUI of the program
root = tk.Tk()
frame = tk.Frame(root, bg='blue')
frame.pack()

btn_file_upload = tk.Button(frame,  # Button for calling upload function
                            text='Select File',
                            bg='dark grey',
                            fg='blue',
                            padx=30,
                            pady=10,
                            command=upload)
btn_file_upload.pack(side=tk.LEFT)

btn_sentimental_analysis = tk.Button(frame,  # Button for calling sentiment function
                                     text="S.A",
                                     bg="dark grey",
                                     fg='blue',
                                     padx=40,
                                     pady=10,
                                     command=sentiment)
btn_sentimental_analysis.pack(side=tk.LEFT)

btn_sentimental_analysis_graph = tk.Button(frame,  # Button for calling sentiment function
                                           text="S.A graph",
                                           bg="dark grey",
                                           fg='blue',
                                           padx=40,
                                           pady=10,
                                           command=graph_sentiment)
btn_sentimental_analysis_graph.pack(side=tk.LEFT)

btn_pos = tk.Button(frame,  # Button for calling pos function
                    text="Upload",
                    bg="dark grey",
                    fg='blue',
                    padx=40,
                    pady=10,
                    command=upload_file)
btn_pos.pack(side=tk.LEFT)

btn_pos_graph = tk.Button(frame,  # Button for calling pos function
                          text="Fetch",
                          bg="dark grey",
                          fg='blue',
                          padx=40,
                          pady=10,
                          command=fetch_data)
btn_pos_graph.pack(side=tk.LEFT)

btn_interjection = tk.Button(frame,  # Button for calling interjection function
                             text="Interjection",
                             bg="dark grey",
                             fg='blue',
                             padx=25,
                             pady=10,
                             command=interjections)
btn_interjection.pack(side=tk.LEFT)

btn_interjection_graph = tk.Button(frame,  # Button for calling interjection function
                                   text="Interjection graph ",
                                   bg="dark grey",
                                   fg='blue',
                                   padx=25,
                                   pady=10,
                                   command=graph_interjections)
btn_interjection_graph.pack(side=tk.LEFT)

scrollbar: Scrollbar = tk.Scrollbar(root)  # Creating a scrollbar
scrollbar.pack(side=RIGHT, fill=Y)
text_box = tk.Text(root, width=150, height=120, bg='lightblue', yscrollcommand=scrollbar.set)
text_box.pack()
scrollbar.config(command=text_box.yview)
root.geometry("500x500")  # Initial size of the gui
root.mainloop()


    
    
