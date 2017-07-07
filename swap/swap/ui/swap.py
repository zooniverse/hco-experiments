################################################################
"""
    An interface to interact with our utilities from the command line.
    Makes it easier to repeated run SWAP under different conditions.

    UI:
        Container for all the different interfaces

    Interface:
        A construct that manages options and determines the right action

    SWAPInterface:
        An interface for interacting with SWAP

    RocInterface:
        An interface to generate roc curves from multiple SWAP exports
"""

import swap.plots as plots

from swap.utils.scores import ScoreExport
from swap.swap import SWAP
from swap.control import Control
from swap.ui.ui import Interface
from swap.ui.utils import load_pickle, write_log

import os
import csv
import logging

logger = logging.getLogger(__name__)

class SWAPInterface(Interface):
    """
        Customized interface to add SWAP operations
    """

    def init(self):
        """
            Initialize variables
        """
        self.control = None

    @property
    def command(self):
        return 'swap'

    def options(self, parser):

        parser.add_argument(
            '--save', nargs=1,
            metavar='file',
            help='save swap to file')

        parser.add_argument(
            '--save-scores', nargs=1,
            metavar='file',
            help='save swap scores to file')

        parser.add_argument(
            '--load', nargs=1,
            metavar='file',
            help='Load a pickled SWAP object')

        parser.add_argument(
            '--run', action='store_true',
            help='Run the SWAP algorithm')

        parser.add_argument(
            '--train', nargs=1,
            metavar='n',
            help='Run swap with a test/train split. Restricts sample size' +
                 ' of gold labels to \'n\'')

        parser.add_argument(
            '--controversial', nargs=1,
            metavar='n',
            help='Run swap with a test/train split, using the most/least' +
                 'controversial subjects')

        parser.add_argument(
            '--consensus', nargs=1,
            metavar='n',
            help='Run swap with a test/train split, using the most/least' +
                 'consensus subjects')

        parser.add_argument(
            '--subject', nargs=1,
            metavar='file',
            help='Generate subject track plot and output to file')

        # parser.add_argument(
        #     '--utraces', nargs=1,
        #     metavar='file',
        #     help='Generate user track plots and output to file')

        parser.add_argument(
            '--user', nargs=1,
            metavar='file',
            help='Generate plot of user confusion matrices and save to file.'
                 ' Specifying - as filename renders plot in matplotlib viewer.')

        parser.add_argument(
            '--hist', nargs=1,
            metavar='file',
            help='Generate multiclass histogram plot.'
                 ' Specifying - as filename renders plot in matplotlib viewer.')

        parser.add_argument(
            '--log', nargs=1,
            metavar='file',
            help='Write the entire SWAP export to file')

        parser.add_argument(
            '--presrec', nargs=1,
            metavar='file',
            help='Generate Precision-Recall curve (SciKit learn)'
                 ' Specifying - as filename renders plot in matplotlib viewer.')

        # parser.add_argument(
        #     '--extremes', nargs=2,
        #     metavar='controversial consensus',
        #     help='Run swap with a test/train split, using the most' +
        #          'controversial subjects and subjects with most consensus')

        # parser.add_argument(
        #     '--extreme-min', nargs=2,
        #     metavar='controversial consensus',
        #     help='Run swap with a test/train split, using the most' +
        #          'controversial subjects and subjects with most consensus')

        parser.add_argument(
            '--stats', action='store_true',
            help='Display run statistics')

        parser.add_argument(
            '--dist', nargs=2,
            help='Show distribution plot')

        parser.add_argument(
            '--diff', nargs='*',
            help='Visualize performance difference between swap outputs')

        parser.add_argument(
            '--shell', action='store_true',
            help='Drop to shell after other commands have completed.')

        parser.add_argument(
            '--test', action='store_true')

        parser.add_argument(
            '--test-reorder', action='store_true')

        parser.add_argument(
            '--scores-from-csv', nargs=1,
            metavar='file',
            help='Load scores from csv export')

        parser.add_argument(
            '--scores-to-csv', nargs=1,
            metavar='file',
            help='Save score export to csv')

        parser.add_argument(
            '--export-user-scores', nargs=1,
            metavar='file',
            help='Export user scores to csv')

    def call(self, args):
        swap = None
        score_export = None

        if args.load:
            obj = self.load(args.load[0])

            if isinstance(obj, SWAP):
                swap = obj
                score_export = swap.score_export()
            elif isinstance(obj, ScoreExport):
                score_export = obj

        if args.scores_from_csv:
            fname = args.scores_from_csv[0]
            score_export = ScoreExport.from_csv(fname)

        if args.run:
            swap = self.run_swap(args)
            score_export = swap.score_export()

        if swap is not None:

            if args.save:
                manifest = self.manifest(swap, args)
                self.save(swap, self.f(args.save[0]), manifest)

            if args.subject:
                fname = self.f(args.subject[0])
                plots.traces.plot_subjects(swap.history_export(), fname)

            if args.user:
                fname = self.f(args.user[0])
                plots.plot_user_cm(swap, fname)

            if args.utraces:
                fname = self.f(args.user[0])
                plots.traces.plot_user(swap, fname)

            if args.log:
                fname = self.f(args.log[0])
                write_log(swap, fname)

            if args.stats:
                s = swap.stats_str()
                print(s)
                logger.debug(s)

            if args.test:
                from swap.utils.golds import GoldGetter
                gg = GoldGetter()
                logger.debug('applying new gold labels')
                swap.set_gold_labels(gg.golds)
                swap.process_changes()
                logger.debug('done')

            if args.test_reorder:
                self.reorder_classifications(swap)

            if args.export_user_scores:
                fname = self.f(args.export_user_scores[0])
                self.export_user_scores(swap, fname)

        if score_export is not None:
            if args.save_scores:
                fname = self.f(args.save_scores[0])
                self.save(score_export, fname)

            if args.hist:
                fname = self.f(args.hist[0])
                plots.plot_class_histogram(fname, score_export)

            if args.dist:
                data = [s.getScore() for s in swap.subjects]
                plots.plot_pdf(data, self.f(args.dist[0]), swap,
                               cutoff=float(args.dist[1]))

            if args.presrec:
                fname = self.f(args.presrec[0])
                plots.distributions.sklearn_purity_completeness(
                    fname, score_export)

            if args.scores_to_csv:
                self.scores_to_csv(score_export, args.scores_to_csv[0])

        if args.diff:
            self.difference(args)

        if args.shell:
            import code
            code.interact(local=locals())

        return swap

    def run_swap(self, args):
        """
            Have the Control process all classifications
        """
        control = self.getControl()

        # Random test/train split
        if args.train:
            train = int(args.train[0])
            control.gold_getter.random(train)

        if args.controversial:
            size = int(args.controversial[0])
            control.gold_getter.controversial(size)

        if args.consensus:
            size = int(args.consensus[0])
            control.gold_getter.consensus(size)

        # if args.extremes:
        #     controversial = int(args.extremes[0])
        #     consensus = int(args.extremes[1])
        #     control.gold_getter.extremes(controversial, consensus)

        # if args.extreme_min:
        #     controversial = int(args.extreme_min[0])
        #     consensus = int(args.extreme_min[1])
        #     control.gold_getter.extreme_min(controversial, consensus)

        control.run()
        swap = control.getSWAP()

        return swap

    @staticmethod
    def reorder_classifications(swap):
        import random
        import progressbar
        with progressbar.ProgressBar(
                max_value=len(swap.subjects)) as bar:
            n = 0
            for subject in swap.subjects:
                bar.update(n)

                ids = [t.id for t in subject.ledger]
                ids = list(sorted(ids, key=lambda item: random.random()))

                previous = None
                for i, id_ in enumerate(ids):
                    t = subject.ledger.get(id_)
                    t.order = i
                    t.right = None

                    if previous is None:
                        t.left = None
                    else:
                        previous.right = t
                        t.left = previous

                    subject.ledger.update(id_)
                    previous = t

                n += 1
        print(n)

        swap.process_changes()
        return swap

    @staticmethod
    def scores_to_csv(score_export, fname):
        with open(fname, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for score in score_export.scores.values():
                writer.writerow((score.id, score.gold, score.p))

    @staticmethod
    def export_user_scores(swap, fname):
        logger.debug('Exporting user scores to %s', fname)
        with open(fname, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for user in swap.users:
                writer.writerow((user.id, *user.score, len(user.ledger)))
        logger.debug('done')

    # def scores_from_csv(self, fname):
    #     import csv
    #     from swap.utils.scores import Score, ScoreExport
    #     data = {}
    #     with open(fname) as csvfile:
    #         reader = csv.reader(csvfile)
    #         for i, g, p in reader:
    #             i = int(i)
    #             g = int(g)
    #             p = float(p)
    #             data[i] = Score(i, g, p)

    #     return ScoreExport(data, new_golds=False)

    @staticmethod
    def manifest(swap, args):
        def arg_str(args):
            s = ''
            for key, value in args._get_kwargs():
                if key in ['func']:
                    continue
                s += '%13s  %s\n' % (key, value)

            return s

        s = swap.manifest() + '\n'
        s += 'UI Manifest\n'
        s += '===========\n'
        s += 'args:\n%s' % arg_str(args)

        return s

    def save(self, obj, fname, manifest=None):
        if manifest != '' and manifest is not None:
            m_fname = fname.split('.')
            m_fname = m_fname[:-1]
            m_fname[-1] += '-manifest'
            m_fname = '.'.join(m_fname)
            with open(self.f(m_fname), 'w') as file:
                file.write(manifest)

        super().save(obj, fname)

    @staticmethod
    def getControl():
        """
            Returns the Control instance
            Defines a Control instance if it doesn't exist yet
        """
        control = Control()

        return control

    def difference(self, args):
        base = load_pickle(args.diff[0])

        p_args = []
        args_ = args.diff[1: -1]
        args_ = [tuple(args_[i: i + 2]) for i in range(0, len(args_), 2)]
        for label, fname in args_:
            _, extension = os.path.splitext(fname)
            if extension == '.csv':
                scores = ScoreExport.from_csv(fname)
            elif extension == '.pkl':
                scores = load_pickle(fname)

            p_args.append((label, scores))

        fname = self.f(args.diff[-1])

        print(p_args)

        # other = [load_pickle(x) for x in args.diff[1:]]
        plots.performance.p_diff(base, p_args, fname)
