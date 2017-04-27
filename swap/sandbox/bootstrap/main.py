#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels
from bootstrap import *

from swap import ui
import swap.plots as plots

import copy

gold_1 = [3328040, 3313220, 2977121, 2943566, 3317607]
gold_0 = [3624432, 3469678, 3287492, 3627326, 3724438]

p0 = 0.12
epsilon = 0.5


class Interface(ui.Interface):

    def __init__(self):
        super().__init__()
        self.p0 = p0
        self.epsilon = epsilon

        self.last_load = None

    def options(self):
        parser = super().options()

        boot_parser = self.subparsers.add_parser('boot')
        boot_parser.set_defaults(func=self.command_boot)
        self.the_subparsers['boot'] = boot_parser

        # boot_parser.add_argument(
        #     '--threshold', nargs=2,
        #     help='Print the number of subjects above or below the threshold')

        boot_parser.add_argument(
            '--iterate', nargs=3,
            help='Iterate SWAP N times with the ' +
                 'specified (low, high) thresholds')

        boot_parser.add_argument(
            '--thresholds', '-t', nargs=3)

        boot_parser.add_argument(
            '--traces', nargs=1,
            metavar='file',
            help='Generate trace plot of bootstrap iterations')

        boot_parser.add_argument(
            '--load', nargs=1,
            metavar='file',
            help='load a pickled bootstrap from file')

        boot_parser.add_argument(
            '--save', nargs=1,
            metavar='file',
            help='load a pickled bootstrap from file')

        boot_parser.add_argument(
            '--histogram', nargs=1,
            metavar='file',
            help='Draw a histogram of bootstrap data')

        boot_parser.add_argument(
            '--cm', nargs=3)

        boot_parser.add_argument(
            '--utraces', nargs='*')

        roc_parser = self.the_subparsers['roc']
        roc_parser.add_argument(
            '-b', '--bootstrap', nargs='*', action='append',
            help='Generate ROC curve from this file, bootstrap specific')

        return parser

    def command_boot(self, args):

        if args.load:
            bootstrap = self.load(args.load[0])
        else:
            bootstrap = None

        if args.iterate:
            bootstrap = self.iterate(args)

        if args.traces and bootstrap:
            fname = self.f(args.traces[0])
            self.plot_bootstrap(bootstrap, fname)

        if args.cm and bootstrap:
            if len(args.cm) < 2:
                raise ValueError('Must specify at least one swap level')
            self.confusion_matrix_err(bootstrap, args)

        if args.utraces and bootstrap:
            if len(args.cm) < 2:
                raise ValueError('Must specify at least one swap level')
            self.user_traces(bootstrap, args)

        if args.save:
            fname = self.f(args.save[0])
            self.save(bootstrap, fname)

    def save(self, obj, fname):
        if isinstance(obj, Bootstrap):
            with open(self.f('manifest'), 'w') as file:
                file.write(obj.manifest())

        super().save(obj, fname)

    def load(self, fname):
        if self.last_load is not None and \
                self.last_load[0] == fname:
            return self.last_load[1]
        else:
            self.last_load = None

            obj = super().load(fname)
            self.last_load = (fname, obj)

            return obj

    def mod_f(self, fname, append):
        append = str(append)

        f = fname[:]
        i = f.find('.')
        f = f[:i] + '-%s' % append + f[i:]

        return self.f(f)

    def threshold(self, data, threshold):
        min = float(threshold[0])
        max = float(threshold[1])
        high = 0
        low = 0
        other = 0

        for subject, item in data['subjects'].items():
            if item['score'] < min:
                low += 1
            elif item['score'] > max:
                high += 1
            else:
                other += 1

        print('high: %d, low: %d, other: %d' % (high, low, other))

    def iterate(self, args):
        if args.save:
            fname = args.save[0]
        else:
            fname = None

        n = int(args.iterate[0])
        low = float(args.iterate[1])
        high = float(args.iterate[2])

        thresholds = {}
        if args.thresholds:
            i = int(args.thresholds[0]) - 1
            low = float(args.thresholds[1])
            high = float(args.thresholds[2])
            thresholds[i] = (low, high)

        bootstrap = Bootstrap(low, high, self.p0, self.epsilon)

        for i in range(n):
            if i in thresholds:
                bootstrap.setThreshold(*thresholds[i])

            swap = bootstrap.step()
            if fname:
                self.save(swap,
                          self.mod_f(fname, 'swap-%d' % i))

            img = self.f('iterate-%d.png' % i)
            plots.traces.plot_subjects(swap, img)

        # if fname:
        #     self.save(bootstrap, fname)

        return bootstrap

    def confusion_matrix_err(self, bootstrap, args):
        level = int(args.cm[0]) - 1
        swap_name = args.cm[1]
        fname = self.f(args.cm[2])

        swap = self.load(swap_name)
        bswap = bootstrap.getMetric(level).getSWAP()

        data = []
        for id_ in swap.users.getAgentIds():

            a_user = swap.users.getAgent(id_)
            b_user = bswap.users.getAgent(id_)

            error = [0, 0]
            for i in [0, 1]:
                a = a_user.getScore(i)
                b = b_user.getScore(i)
                error[i] = a - b / a

            data.append((*error, 10))

        plots.plot_confusion_matrix(data, "Test", None)

    def user_traces(self, bootstrap, args):
        pass

    def plot_bootstrap(self, bootstrap, fname):
        plot_data = []
        for subject, value in bootstrap.export().items():
            if subject in bootstrap.silver:
                c = bootstrap.silver[subject]
            else:
                c = 2

            history = value['history']
            plot_data.append((c, history))

        plots.traces.plot_tracks(plot_data, "Bootstrap Traces",
                                 fname, scale='linear')

    def collect_roc(self, args):
        it = super().collect_roc(args)
        it.__class__ = Roc_Iterator

        if args.bootstrap:
            for label, fname, *steps in args.bootstrap:
                print(fname)
                steps = [int(i) - 1 for i in steps]
                it.addBootObject(label, fname, self.load, steps)

        return it


class Roc_Iterator(ui.Roc_Iterator):

    def addBootObject(self, label, fname, load, iterations=None):
        if iterations:
            self.items.append((label, fname, load, iterations))

    def next(self):
        self.__bounds()

        item = self.items[self.i]
        if len(item) < 4:
            return super().next()
        elif len(item[3]) == 0:
            self.i += 1
            return self.next()
        else:
            print(item)
            label, fname, load = item[:3]
            i = item[3].pop(0)
            label = '%s-%d' % (label, i + 1)

            obj = load(fname)

            return (label, obj.roc_export(i))


def main():
    interface = Interface()
    ui.run(interface)


if __name__ == "__main__":
    main()
