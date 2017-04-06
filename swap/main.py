#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm


from swap import ui
from swap import Control


class Interface(ui.Interface):
    def __init__(self):
        super().__init__()

        self.control = None

    def options(self):
        parser = super().options()

        swap_parser = self.subparsers.add_parser('swap')
        swap_parser.set_defaults(func=self.command_swap)
        self.the_subparsers['swap'] = swap_parser

        swap_parser.add_argument(
            '--save', nargs=1,
            help='The filename where the SWAP object should be stored')

        swap_parser.add_argument(
            '--load', nargs=1,
            help='Load a pickled SWAP object')

        swap_parser.add_argument(
            '--run', action='store_true',
            help='Run the SWAP algorithm')

        swap_parser.add_argument(
            '--subject', nargs=1,
            help='Generate subject track plot and output to filename S')

        swap_parser.add_argument(
            '--user', nargs=1,
            help='Generate user track plots and output to filename U')

        swap_parser.add_argument(
            '--log', nargs=1,
            help='Write the entire SWAP export to file')

        return parser

    def command_swap(self, args):
        swap = None

        if args.load:
            swap = self.load(args.load[0])

        if args.run:
            swap = self.run_swap()

        if args.save:
            self.save(swap, self.f(args.save[0]))

        if args.subject:
            fname = self.f(args.subject[0])
            ui.plot_subjects(swap, fname)

        if args.user:
            fname = self.f(args.user[0])
            ui.plot_users(swap, fname)

        if args.log:
            fname = self.f(args.output[0])
            ui.write_log(swap, fname)

        return swap

    def _control(self):
        return Control(self.p0, self.epsilon)

    def getControl(self):
        if self.control is None:
            self.control = self._control()

        return self.control

    def run_swap(self, fname):
        control = self.getControl()
        control.process()
        swap = control.getSWAP()

        ui.save_pickle(swap, fname)

        return swap


def main():
    interface = Interface()
    ui.run(interface)


if __name__ == "__main__":
    main()
