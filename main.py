import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import xml.dom.minidom
import string
import os
import re
import glob
import numpy as np

def file2list(path):
    file_f = open(path, 'r')
    file_list = file_f.read().split(',')
    # print(file_list,file=file2)
    file_f.close()
    return(file_list)

def file_process(path,listOFlists):
    print("started processing the file")
    # Processing XML using the library ElementTree
    file = open(path, encoding="utf8").readlines()
    tree = ET.parse(path)
    root = tree.getroot()
    # children = root.getchildren()
    children = list(root)


    id_timestamp_text = {}
    timestamp_text = {}
    lists = []
    for i in range(0,len(listOFlists)):
        lists = lists + listOFlists[i]

    for line in file:
        line = line.strip()
        if line.startswith('<id>'):
            # index = line.
            id = line.split("<id>")[1].split("</id>")[0]
        # if line.startswith('</mediawiki>'):
        #     # index = line.
        #     line = line.replace(line,'')
        #     break

    # for in range(0,len(children)):
    for child in children:
        if "page" in child.tag:
            for elem in child.iter():
                if "timestamp" in elem.tag:
                    li = []
                    timestamp = elem.text
                    timestamp = timestamp.split('T')[0] + " " + timestamp.split('T')[1].split('Z')[0]
                    # print(timestamp)
                elif "text" in elem.tag:
                    text = elem.text
                    if text is not None:
                        for line in text.splitlines():
                            # print(line)
                            line = line.strip()
                            for part in line.split():
                                # Converting to lower case
                                part = part.lower()

                                # This is not used as it would only remove the special character and not the word attached to it
                                # It is not preferred as those words might mean or refer to some original work
                                # part = re.sub(r"[^a-zA-Z0-9]","",part)

                                # Checking the length and removing the stopwords
                                # (?=.* \w) ^ (\w | ')+$
                                if len(part) <= 2 \
                                        or part in lists \
                                        or part.isalnum() == False \
                                        or any(map(str.isdigit, part)) == True \
                                        or part.isascii() == False:
                                    part = part.replace(part, "")
                                if part != "":
                                    li.append(part)
                                #----
                    li = set(li)
                    li = sorted(li)
                    timestamp_text[timestamp] = li
    id_timestamp_text[id] = timestamp_text
    print("Done Marking Text")
    print()
    print()
    return(id_timestamp_text)


def find_typo(id_timestamp_text,dict):
    print("started finding typo")
    id_timestamp_typo = {}
    timestamp_typo = {}
    id_doc = 0
    for id, timestamp_text in id_timestamp_text.items():
        id_doc = id
        print()
        print()
        for ts, text in timestamp_text.items():
            print(ts)
            typo = []
            for i in range(0, len(text)):
                if text[i] not in dict:
                    typo.append(text[i])
                timestamp_typo[ts] = typo
        id_timestamp_typo[id] = timestamp_typo
        # df = pd.DataFrame()
        df = pd.DataFrame.from_dict(id_timestamp_typo)
        # df.to_csv(path+'\df_typo_duration\df.csv')
        print("Done finding typo")
    return(id_timestamp_typo,df,id_doc)


def cal_duration(df, id_doc):
    print("started calculating duration")
    # Removing the rows with empty lists
    df = df[df[id_doc] != '[]']

    # Reseting the index after dropping rows with empty lists
    # df.reset_index(drop=True, inplace=True)
    df = df.reset_index()

    df.rename(columns={'index': 'ts'}, inplace=True)
    df[['date', 'time']] = df['ts'].str.split(" ", expand=True, )
    df = df.drop(['ts', 'time'], axis=1)

    # convert ts column to datatype datetime
    df['date'] = pd.to_datetime(df['date'])

    # df_typo_duration = pd.DataFrame(columns=['word', 'duration'])

    word_list = []

    for i in range(1, len(df.index)):
        # l1 = df.loc[i, '40552645']
        # l1 = str(l1)
        # l1 = l1.split("[")[1].split("]")[0].replace("'", '').split(",")
        l1 = str(df.loc[i, id_doc]).split("[")[1].split("]")[0].replace("'", '').split(",")
        for j in range(0, len(l1)):
            word = l1[j]
            word_list.append(word)

    word_list = list(set(word_list))

    df_typo_duration = pd.DataFrame(columns=['word', 'duration','sd','ed'])

    for i in range(0, len(word_list)):
        word = word_list[i]
        dates_present = []
        dates_absent = []
        end_date = 0
        for i in range(1, len(df.index)):
            if df.loc[i, id_doc] != '[]':
                l1 = df.loc[i, id_doc]
                l1 = str(l1).split("[")[1].split("]")[0].replace("'", '').split(",")
                # l1 = l1.split("[")[1].split("]")[0].replace("'", '').split(",")
                if word in l1:
                    d = df.loc[i, 'date']
                    dates_present.append(d.strftime('%Y/%m/%d'))
                elif word not in l1:
                    d = df.loc[i, 'date']
                    dates_absent.append(d.strftime('%Y/%m/%d'))

        dates_present.sort()
        dates_absent.sort()
        # input_date is the date the word was last present
        input_date = dates_present[-1]

        date_found = False
        if dates_absent == []:
            end_date = datetime.today().strftime('%Y/%m/%d')
        else:
            for date in range(0, len(dates_absent)):
                if dates_absent[date] > input_date:
                    end_date = dates_absent[date]
                    date_found = True
                    break
        if date_found == False:
            end_date = datetime.today().strftime('%Y/%m/%d')
            # print("ed: " + str(end_date))
        str_sd = dates_present[0]
        str_ed = end_date

        # convert string to date object
        sd = datetime.strptime(str_sd, "%Y/%m/%d")
        ed = datetime.strptime(str_ed, "%Y/%m/%d")

        # difference between dates in timedelta
        delta = ed - sd
        duration = delta.days
        # df_typo_duration = df_typo_duration.append({'word': word, 'duration': duration, 'sd': sd, 'ed': ed},ignore_index=True)
        new_row = pd.DataFrame({'word': word, 'duration': duration, 'sd': sd, 'ed': ed}, index=[0])
        df_typo_duration = pd.concat([df_typo_duration, new_row], axis=0, ignore_index=True)

    # print(df_typo_duration)
    print("Done finding duration")
    df_typo_duration.to_csv(path + '/Outputs/df_typo_duration/file'+id_doc+'.csv')
    return df_typo_duration


if __name__ == '__main__':
    # path = "C:\Users\n10856188\Downloads\703\703\"
    # repr(path)
    path = os. getcwd()
    # print(path)


    summary_df = pd.DataFrame(columns=['id', 'min', 'max', 'avg'])

    # file_path = "/Users/devikanair/Desktop/IFN703/samples/sample4.xml"
    # file1 = open("/Users/devikanair/Desktop/IFN703/Programs/Draft_1/Dict2.txt", "a")
    # file2 = open("/Users/devikanair/Desktop/IFN703/Programs/Draft_1/Typo2.txt", "a")

    # Importing lists
    # Roman numerals
    RomanNumList = file2list(path+'/Data/common-english-words.txt')
    Dictionary = file2list(path+'/Data/words.txt')
    # Combining all the lists to be checked
    listOFlists = []
    listOFlists.append(RomanNumList)

    for file in glob.glob(path+'/Samples/*.xml'):
        print(file)
        id_timestamp_text = file_process(file, listOFlists)
        id_timestamp_typo, df, id_doc = find_typo(id_timestamp_text, Dictionary)
        df_typo_duration = cal_duration(df, id_doc)

        df_typo_duration['word'].replace('', np.nan, inplace=True)
        df_typo_duration.dropna(subset=["word"], inplace=True)

        new_row = pd.DataFrame({'id': id_doc, 'min': df_typo_duration['duration'].min(), 'max': df_typo_duration['duration'].max(),
             'avg': df_typo_duration['duration'].mean()}, index=[0])
        summary_df = pd.concat([summary_df, new_row], axis=0, ignore_index=True)
        summary_df.to_csv(path+'/Outputs/summary.csv')

    # print(summary_df)


