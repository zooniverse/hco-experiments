#!/usr/bin/env python

from swap import Control
import pickle
from pprint import pprint
import matplotlib.pyplot as plt


def main():
    control = Control(.01, .5)
    control.process()

    data = control.getSWAP().export()
    # with open('log', 'w') as file:
    #     yaml.dump(data, file)

    with open('pickle.pkl', 'wb') as file:
        pickle.dump(data, file)


def find_errors():
    with open('pickle.pkl', 'rb') as file:
        data = pickle.load(file)

    interest = []
    for key, value in data['subjects'].items():
        if 1.0 in value['history'] or 0 in value['history']:
            interest.append(value)

    print(len(interest))
    plot_swap_subjects(data,
                       title="Subject Tracks",
                       name="subject_tracks.pdf")

    with open('log', 'w') as file:
        pprint(interest, file)


def plot_swap_subjects(export, title, name):
    """ Plot subject tracks """
    subject_data = export['subjects']
    colourmap = ["#669D31", "#F00200"]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    count = 0
    for subject_id in subject_data.keys():
        if count == 1000:
            break
        #print(count)
        colour = colourmap[subject_data[subject_id]['gold_label']]
        history = subject_data[subject_id]['history']
        #print(history)
        ax.plot([0.01]+history,range(len(history)+1),"-",color=colour,lw=1, alpha=0.1)
        """
        if subjectData[subject_id]["gold_label"] == "1":
            ax.plot([0.01]+history,range(len(history)+1),"-",color=colour,lw=1, alpha=0.5,zorder=1000)
        else:
            ax.plot([0.01]+history,range(len(history)+1),"-",color=colour,lw=1, alpha=0.5)
        """
        count += 1
    plt.xlim(-0.01, 1.01)
    ax.set_yscale("log")
    plt.gca().invert_yaxis()
    plt.xlabel("P(real)")
    plt.ylabel("number of classificaions")
    plt.title(title)
    plt.savefig(name)
    plt.show()


if __name__ == "__main__":
    #main()
    find_errors()
