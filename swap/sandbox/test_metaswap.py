## Test meta data splits
from swap.control import Control, MetaDataControl
from swap.mongo import Query
import matplotlib.pyplot as plt

def plot_swap_users(swappy,title,name):
    """ Plot User Skill """
    # Loop over all users
    user_data = swappy.exportUserData()
    # all users
    unique_users = user_data.keys()
    # max classifications
    max_class = 0
    # number of user processed
    counter = 0
    for user in unique_users:
        n_class_user = len(user_data[user]['gold_labels'])
        max_class = max(max_class, n_class_user)
        plt.plot(user_data[user]['score_1_history'][-1],
                 user_data[user]['score_0_history'][-1], "o",
                 ms=(n_class_user)/500,
                 color="#3F88C5", alpha=0.5)
        counter += 1

    plt.text(0.03, 0.03, "Obtuse")
    plt.text(0.75, 0.03, "Optimistic")
    plt.text(0.03, 0.95, "Pessimistic")
    plt.text(0.8, 0.95, "Astute")
    plt.plot([0.5, 0.5], [0,1], "k--", lw=1)
    plt.plot([0, 1], [0.5, 0.5], "k--", lw=1)
    plt.plot([0, 1], [1, 0], "k-", lw=1)
    plt.xlabel("P(\'real\'|real)")
    plt.ylabel("P(\'bogus\'|bogus)")
    plt.axes().set_aspect('equal')
    plt.title(title)
    plt.savefig(name)
    plt.show()


def plot_swap_subjects(swappy,title,name):
    """ Plot subject tracks """
    subject_data = swappy.exportSubjectData()
    colourmap = ["#669D31","#F00200"]
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


if __name__ == '__main__':
    # magnitude ranges
    control1 = MetaDataControl(0.01, 0.5, 'mag', 13, 18)
    control1.process()
    plot_swap_subjects(control1.getSWAP(),
                       title="Subject Tracks - 13-18 Mag",
                       name="subject_tracks_13_18.pdf")
    plot_swap_users(control1.getSWAP(),
                    title="User Profiles - 13-18 Mag",
                    name="User_profiles_13_18.pdf")

    control2 = MetaDataControl(0.01, 0.5, 'mag', 18, 19)
    control2.process()
    plot_swap_subjects(control2.getSWAP(),
                       title="Subject Tracks - 18-19 Mag",
                       name="subject_tracks_18_19.pdf")
    plot_swap_users(control2.getSWAP(),
                    title="User Profiles - 18-19 Mag",
                    name="User_profiles_18_19.pdf")

    control3 = MetaDataControl(0.01, 0.5, 'mag', 19, 20)
    control3.process()
    plot_swap_subjects(control3.getSWAP(),
                       title="Subject Tracks - 19-20 Mag",
                       name="subject_tracks_19_20.pdf")
    plot_swap_users(control3.getSWAP(),
                    title="User Profiles - 19-20 Mag",
                    name="User_profiles_19_20.pdf")

    control4 = MetaDataControl(0.01, 0.5, 'mag', 20, 23)
    control4.process()
    plot_swap_subjects(control4.getSWAP(),
                       title="Subject Tracks - 20-23 Mag",
                       name="subject_tracks_20_23.pdf")
    plot_swap_users(control4.getSWAP(),
                    title="User Profiles - 20-23 Mag",
                    name="User_profiles_20_23.pdf")

    # Reverse SWAP
#    control2 = MetaDataControl(0.01, 0.5, 'mag', 18, 19)
#    control2.process()
#    plot_swap_subjects(control2.getSWAP(),
#                       title="Subject Tracks - 18-19 Mag",
#                       name="subject_tracks_revSWAP_18_19.pdf")
#    plot_swap_users(control2.getSWAP(),
#                    title="User Profiles - 18-19 Mag",
#                    name="User_profiles_revSWAP_18_19.pdf")
