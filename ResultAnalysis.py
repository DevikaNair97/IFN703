import pandas as pd
from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import glob
import os
import numpy as np


def data_prep(df):
    df = df.dropna().reset_index(drop=True)
    df["sd"] = pd.to_datetime(df["sd"])
    df["ed"] = pd.to_datetime(df["ed"])
    df['word'] = df['word'].str.strip()
    df["Word_Length"] = df["word"].str.len()
    df.drop(df.index[df['Word_Length'] > 10], inplace=True)
    df['duration'] = (df['ed'] - df['sd']) / np.timedelta64(1, 'Y')
    return (df)

###
# Plot to Study the duration of each Typo (per Article)
###
def plot_lifespan(df,ysize,xsize):

    plt.rcParams["figure.figsize"] = (ysize,xsize)

    word_set = set(word.strip() for words in df['word'] for word in words.split(","))
    df_words = {p: i for i, p in enumerate(sorted(word_set))}
    # print(persons)
    for d_word in df_words:
        periods = []
        for words, start, end in zip(df['word'], df['sd'], df['ed']):
            if d_word in set(word.strip() for word in words.split(",")):
                periods.append((start, end - start))
        plt.broken_barh(periods, (df_words[d_word] - 0.45, 0.9),
                        facecolors=plt.cm.twilight_shifted(df_words[d_word] / len(df_words)))

    plt.yticks(range(len(df_words)), df_words)
    plt.title('Typos and their Lifespan')
    plt.xlabel('Year')
    plt.ylabel('Typos')
    plt.savefig(newpath + "/Plot1.png")
    plt.show()

###
# Plot to study the Distribution of Birth/Death of typo across Years (per Article)
###
def plot_freq_dist(df, col, Birth_Death,ysize,xsize):
    df = df
    xlabel = Birth_Death + " - Year"
    title = 'Frequency Distribution of ' + Birth_Death + ' of Typos'
    PlotName = "/Plot" + Birth_Death + ".png"

    plt.rcParams["figure.figsize"] = [ysize,xsize]
    plt.rcParams["figure.autolayout"] = True

    fig, ax = plt.subplots()
    df[col].value_counts().plot(ax=ax, kind='line', xlabel=xlabel, ylabel='Frequency', title=title)

    plt.savefig(newpath + PlotName)
    plt.show()

if __name__ == '__main__':

    df_together = pd.DataFrame(columns=['word', 'duration','sd','ed'])
    typo_no = {}

    path = os.getcwd()
    path = path + "/Outputs/"
    for file in glob.glob(path + 'df_typo_duration/*.csv'):
        name = file.replace(path,"").replace(".csv","")
        # print(name)

        df = pd.read_csv(file)

        newpath = path + "Results/" + name
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        df = data_prep(df)

        # ---------------------------------------------------------------------------------------------------------------------
        plot_lifespan(df, 10, 20)
        # ---------------------------------------------------------------------------------------------------------------------
        plot_freq_dist(df, 'sd', 'Birth', 7.5, 3.5)
        # ---------------------------------------------------------------------------------------------------------------------
        plot_freq_dist(df, 'ed', 'Death', 7.5, 3.5)
        # ---------------------------------------------------------------------------------------------------------------------

        df_together = pd.concat([df_together, df])
        typo_no[i] = len(df)
        i = i + 1

    plot_freq_dist(df_together, 'sd', 'Concatenated_Birth', 20, 5)
    plot_freq_dist(df_together, 'ed', 'Concatenated_Death', 20, 5)

    df_typo_no = pd.DataFrame(typo_no, index=[0]).T

    # Plotting Number of Typos per Articles
    plt.rcParams["figure.figsize"] = [7.5, 3.5]
    plt.rcParams["figure.autolayout"] = True
    fig, ax = plt.subplots()
    df_typo_no[0].plot(ax=ax, kind='line', xlabel="Article", ylabel='Frequency', title="Number of Typos per Articles")
    plt.savefig(path + "typo_no.png")
    plt.show()

