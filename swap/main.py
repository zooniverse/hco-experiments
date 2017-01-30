import swap
import sys
import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio



# from SNHunters_analysis import get_date_limits_from_manifest
def get_subjects_by_date_limits(db, mjd_limits):

    subjects = []

    cursor = db["gold_standard"].find({"$and": [
        {"min_mjd": {"$gte": mjd_limits[0]}},
        {"max_mjd": {"$lte": mjd_limits[1]}}
    ]
    })

    for doc in cursor:
        for subject in doc["subject_ids"]:
            subjects.append(subject)

    return subjects

def plot_subject_history(db):
    colourmap = {
        "confirmed": "#0014CE",
        "possible": "#FCB606",
                    "good": "#F00200",
                    "attic": "#3D348B",
                    "zoo": "#011627",
                    "garbage": "#669D31"
    }

    # subject_dict = pickle.load(open("subject_dict_swap.pkl","rb"))
    subject_dict = pickle.load(open("subject_dict_robot_human_combo_swap_tes.pkl", "rb"))
    # subjects = sio.loadmat("swap.mat")["subjects"].tolist()[0]
    subjects = sio.loadmat("robot_human_combo_swap_test.mat")["subjects"].tolist()[0]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    count = 0
    good_count = 0
    garbage_count = 0
    for subject_id in subject_dict.keys():
        if count == 100:
            break
        object_id = db["diffID_to_subjectID"].find({"subject_id": {"$eq": subject_id}})[0]["id"]
        l = db["gold_standard"].find({"id": object_id})[0]["list"]
        if l in ["zoo", "possible"]:
            continue
        colour = colourmap[l]
        history = subject_dict[subject_id]
        ax.plot([0.1] + history, range(len(history) + 1), "-", color=colour, lw=1, alpha=0.5)
        # if l == "good" and history[-1] == 1 and good_count < 5:
        """
        if subject_id == 2973946:
            print subject_id, history
            ax.plot([0.1]+history,range(len(history)+1),"k-",lw=1.6, zorder=3000)
            ax.plot([0.1]+history,range(len(history)+1),"-",color=colour,lw=1.5, zorder=3000)
            good_count += 1
        #if l == "garbage" and history[-1] == 0 and garbage_count < 5:
        if subject_id == 2973716:
            print subject_id, history
            ax.plot([0.1]+history,range(len(history)+1),"k-",lw=1.6, zorder=3000)
            ax.plot([0.1]+history,range(len(history)+1),"-",color=colour,lw=1.5, zorder=3000)
            garbage_count += 1
        #if history[-1] >= 0.2 and history[-1] <= 0.6 and len(history) > 20:
        #    print subject_id, history[-1], len(history)
        if subject_id == 2974823:
            ax.plot([0.1]+history,range(len(history)+1),"-",color=colour,lw=1.5, zorder=3000)
        """
        count += 1

    # plt.ylim(ymin=0.9, ymax=50)
    plt.xlim(-0.01, 1.01)
    ax.set_yscale("log")
    plt.gca().invert_yaxis()
    plt.xlabel("P(real)")
    plt.ylabel("number of classificaions")
    plt.show()


def snap_test(db):

    data = sio.loadmat("snapbot_20160725-20160829.mat")

    swap = SWAP(db, np.squeeze(data["subjects"]).tolist(), p0=0.01, epsilon=0.5)
    swap.dt = np.concatenate((np.zeros(swap.M.shape), np.squeeze(data["dt"])))
    swap.dt_prime = np.concatenate((np.zeros(swap.M.shape), np.squeeze(data["dt_prime"])))
    swap.M = np.concatenate((swap.M, data["M"]))
    swap.unique_users = swap.unique_users + np.squeeze(data["unique_users"]).tolist()
    swap.S = np.squeeze(data["S"])

    swap.user_history = pickle.load(open("user_dict_snapbot_20160725-20160829.pkl", "rb"))
    swap.subject_history = pickle.load(open("subject_dict_snapbot_20160725-20160829.pkl", "rb"))

    swap.process()

    swap.save("robot_human_combo_swap_test.mat")


def load_saved_SWAP(db, file, gold_updates):
    data = sio.loadmat(file)
    swap = SWAP(db, np.squeeze(data["subjects"]).tolist(), p0=0.1, epsilon=0.5)
    swap.dt = np.concatenate((np.zeros(swap.M.shape), np.squeeze(data["dt"])))
    swap.dt_prime = np.concatenate((np.zeros(swap.M.shape), np.squeeze(data["dt_prime"])))
    swap.M = np.concatenate((swap.M, data["M"]))
    swap.unique_users = swap.unique_users + np.squeeze(data["unique_users"]).tolist()
    swap.S = np.squeeze(data["S"])

    swap.user_history = pickle.load(open("user_dict_" + file.strip(".mat") + ".pkl", "rb"))
    swap.subject_history = pickle.load(open("subject_dict_" + file.strip(".mat") + ".pkl", "rb"))
    swap.setGoldUpdates(gold_updates)
    return swap


def swap_forward_test(db):

    # load in new subjects
    mjd_limits = get_date_limits_from_manifest("../data/20160905.txt")
    min_mjd = mjd_limits[0]
    mjd_limits = get_date_limits_from_manifest("../data/20161128.txt")
    max_mjd = mjd_limits[1]
    mjd_limits = (min_mjd, max_mjd)
    print mjd_limits

    subjects = get_subjects_by_date_limits(db, mjd_limits)
    print len(subjects)
    # load the saved SWAP run on data between 20160725 and 20160829 with updates to M turned off
    file = "swap_20160725-20160829.mat"
    swap = load_saved_SWAP(db, file, "off")
    print len(swap.subjects)
    swap.subjects += subjects
    print len(swap.subjects)
    print swap.S.shape
    swap.S = np.concatenate((swap.S, np.ones((np.shape(subjects))) * swap.p0))
    print swap.S.shape
    swap.epsilon = 0.1

    swap.process()

    swap.save("swap_epsilon-0.1_20160905-20161128.mat")


def plot_S_surface():

    M_real = np.arange(0, 1, 0.01)
    M_bogus = np.arange(0, 1, 0.01)
    print M_bogus.shape
    S = np.ones((100, 100)) * 0.5

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    for i, m in enumerate(M_real):
        for j, n in enumerate(M_bogus):
            S[i, j] = S[i, j] * M_real[i] / (S[i, j] * M_real[i] + (1 - M_bogus[j]) * (1 - S[i, j]))
    ax1.imshow(S)
    plt.gca().invert_yaxis()
    S = np.ones((100, 100)) * 0.5
    for i, m in enumerate(M_real):
        for j, n in enumerate(M_bogus):
            S[i, j] = S[i, j] * (1 - M_real[i]) / (S[i, j] *
                                                   (1 - M_real[i]) + (M_bogus[j]) * (1 - S[i, j]))
    cax = ax2.imshow(S)
    plt.gca().invert_yaxis()
    cbar = fig.colorbar(cax)
    plt.show()

def main():
    client = MongoClient()
    db = client.SNHunters

    subjects = db.classifications.distinct("subject_id")

    swap = SWAP(db, subjects, p0=0.1, epsilon=0.5)

    swap.process()


def old_main():
    # plot_S_surface()
    # swap = MATSWAP("../hco-experiments/SNHunters_classification_dump_20170109.mat")
    # swap.process()
    # swap.save("matswaptest.mat")
    data = sio.loadmat("matswaptest.mat")
    user_dict = pickle.load(open("user_dict_swaptes.pkl", "rb"))
    m = len(data["unique_users"])
    print m
    order = np.random.permutation(m)

    counter = 0
    max = 0
    # Loop over all users in random order
    for i in order:
        try:
            u = data["unique_users"][i]
            # update max number of classifications of any user
            if len(user_dict[u][1]) + len(user_dict[u][0]) > max:
                max = len(user_dict[u][1]) + len(user_dict[u][0])
            #    continue
            if u[:6] == "robot_":
                print u, "%.3f %.3f" % (user_dict[u][1][-1], user_dict[u][0][-1])
                plt.plot(user_dict[u][1][-1], user_dict[u][0][-1], "o",
                         color="#FFBA08", alpha=0.5)
            else:
                plt.plot(user_dict[u][1][-1], user_dict[u][0][-1], "o",
                         ms=(len(user_dict[u][1]) + len(user_dict[u][0])) / 2000.0,
                         color="#3F88C5", alpha=0.5)
                # plt.plot(user_dict[u][1][-1],user_dict[u][0][-1], "o", \
                #         color="#3F88C5", alpha=0.5)
            counter += 1
        except (KeyError, IndexError):
            continue
    print max
    plt.text(0.03, 0.03, "Obtuse")
    plt.text(0.75, 0.03, "Optimistic")
    plt.text(0.03, 0.95, "Pessimistic")
    plt.text(0.8, 0.95, "Astute")
    plt.plot([0.5, 0.5], [0, 1], "k--", lw=1)
    plt.plot([0, 1], [0.5, 0.5], "k--", lw=1)
    plt.plot([0, 1], [1, 0], "k-", lw=1)
    plt.xlabel("P(\'real\'|real)")
    plt.ylabel("P(\'bogus\'|bogus)")
    plt.axes().set_aspect('equal')
    plt.show()
    exit()
    client = MongoClient()
    db = client.SNHunters
    # swap_forward_test(db)
    # mjd_limits = get_date_limits_from_manifest("../data/20160712.txt")
    # mjd_limits = get_date_limits_from_manifest("../data/20160725.txt")
    # min_mjd = mjd_limits[0]
    # mjd_limits = get_date_limits_from_manifest("../data/20160718.txt")
    # mjd_limits = get_date_limits_from_manifest("../data/20160829.txt")
    # max_mjd = mjd_limits[1]
    # mjd_limits = (min_mjd, max_mjd)
    # print mjd_limits

    # subjects = get_subjects_by_date_limits(db, mjd_limits)
    # data = sio.loadmat("")
    # plot_subject_history(db)
    # snap_test(db)
    # exit()
    # swap = SWAP(db, subjects, p0=0.1, epsilon=0.5)
    # snap = SNAP(db, subjects, p0=0.01, epsilon=0.5, n=100)

    # swap.process()
    # snap.process()

    # swap.save("swap_20160712-20160718.mat")
    # snap.save("snapbot_20160725-20160829.mat")

    # snap_test(db)
    # user_dict = pickle.load(open("user_dict_swap_20160725-20160829.pkl","rb"))
    # user_dict = pickle.load(open("user_dict_snapbot_20160725-20160829.pkl","rb"))
    user_dict = pickle.load(open("user_dict_robot_human_combo_swap_tes.pkl", "rb"))

    # user_dict = pickle.load(open("user_dict_swap_20160725-20160829_13-18.pkl","rb"))
    # user_dict = pickle.load(open("user_dict_swap_20160725-20160829_19.pkl","rb"))
    # user_dict = pickle.load(open("user_dict_swap_20160725-20160829_20.pkl","rb"))
    # user_dict = pickle.load(open("user_dict_swap_20160725-20160829_21-22.pkl","rb"))
    # print user_dict
    # exit()
    # user_dict = pickle.load(open("snap_20160712_user_dict.pkl","rb"))
    # data = sio.loadmat("swap_20160725-20160829.mat")
    # data = sio.loadmat("snapbot_20160725-20160829.mat")
    data = sio.loadmat("robot_human_combo_swap_test.mat")
    # data = sio.loadmat("swap_20160725-20160829_13-18.mat")
    # data = sio.loadmat("swap_20160725-20160829_19.mat")
    # data = sio.loadmat("swap_20160725-20160829_20.mat")
    # data = sio.loadmat("swap_20160725-20160829_21-22.mat")
    """
    u = "nilium"
    plt.plot(range(len(user_dict[u][0])),user_dict[u][0],"b-",label="bogus")
    plt.plot(range(len(user_dict[u][1])), user_dict[u][1],"r-",label="real")
    plt.ylim(0,1)
    plt.xlabel("number classifications")
    plt.ylabel("M")
    plt.legend()
    plt.show()
    exit()
    """
    """
    for i,user in enumerate(data["unique_users"]):
        #if i > 1000:
        #    break
        #if str(user.strip()) == "sean63":
        #print user, data["dt_prime"][i], data["dt"][i]
        try:
            u = str(user.rstrip())
            #if len(user_dict[u][0]) < 5000 and len(user_dict[u][1]) < 5000:
                #print u, len(user_dict[u][0]), len(user_dict[u][1])
                #continue

            if i == 0:
                plt.plot(range(len(user_dict[u][0])),user_dict[u][0],"r-",label="bogus")
                plt.plot(range(len(user_dict[u][1])), user_dict[u][1],"b-",label="real")
            else:
                plt.plot(range(len(user_dict[u][0])),user_dict[u][0],"r-")
                plt.plot(range(len(user_dict[u][1])), user_dict[u][1],"b-")
        except KeyError:
            #print user
            continue
    plt.legend()
    plt.show()
    """

    m = len(data["unique_users"])
    print m
    order = np.random.permutation(m)

    counter = 0
    max = 0
    for i in order:
        # if counter == 100:
        #    break
        try:
            u = str(data["unique_users"][i].rstrip())
            # print u
            if len(user_dict[u][1]) + len(user_dict[u][0]) > max:
                max = len(user_dict[u][1]) + len(user_dict[u][0])
            #    continue
            if u[:6] == "robot_":
                print u, "%.3f %.3f" % (user_dict[u][1][-1], user_dict[u][0][-1])
                plt.plot(user_dict[u][1][-1], user_dict[u][0][-1], "o",
                         color="#FFBA08", alpha=0.5)
            else:
                plt.plot(user_dict[u][1][-1], user_dict[u][0][-1], "o",
                         ms=(len(user_dict[u][1]) + len(user_dict[u][0])) / 150.0,
                         color="#3F88C5", alpha=0.5)
                # plt.plot(user_dict[u][1][-1],user_dict[u][0][-1], "o", \
                #         color="#3F88C5", alpha=0.5)
            counter += 1
        except (KeyError, IndexError):
            continue
    print max
    plt.text(0.03, 0.03, "Obtuse")
    plt.text(0.75, 0.03, "Optimistic")
    plt.text(0.03, 0.95, "Pessimistic")
    plt.text(0.8, 0.95, "Astute")
    plt.plot([0.5, 0.5], [0, 1], "k--", lw=1)
    plt.plot([0, 1], [0.5, 0.5], "k--", lw=1)
    plt.plot([0, 1], [1, 0], "k-", lw=1)
    plt.xlabel("P(\'real\'|real)")
    plt.ylabel("P(\'bogus\'|bogus)")
    plt.axes().set_aspect('equal')
    plt.show()
    # plt.savefig("user_performance.pdf",bbox_inches="tight")

    print

    # for key in user_dict.keys():
    #    print key, len(user_dict[key][0]),len(user_dict[key][1])

    # data = sio.loadmat("swap.mat")
    # M = data["M"]
    # unique_users = data["unique_users"]
    # for i, user in enumerate(unique_users):
    # print user
    #    if "Carrie" in str(user):
    #        print M[i,:]

    # exit()
    """
    print unique_users[np.where(data["M"]==1)[0]]
    print np.shape(data["dt"])
    print M[np.where(data["M"]==1)[0],:]
    print data["dt"][np.where(data["M"]==1)[0],:]
    """
    # S = np.squeeze(data["S"])
    # bins = np.arange(0,1.04,0.04)
    # plt.hist(swap.S, bins=bins)
    # plt.show()
    """
    data = sio.loadmat("snap.mat")
    S = np.squeeze(data["S"])
    subjects = np.squeeze(data["subjects"]).tolist()
    M = data["M"]
    #print M
    #print np.where(M>1)
    #print data["dt"][np.where(M>1)]
    #print data["dt_prime"][np.where(M>1)]
    #for i in range(M.shape[0]):
    #    print M[i,:], data["dt"][i,:], data["dt_prime"][i,:]

    """
    # S = swap.S
    # subjects = swap.subjects
    # print np.where(swap.M==1)

    """




    """

if __name__ == "__main__":
    main()