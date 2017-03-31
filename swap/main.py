#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm


from swap import ui


class Interface(ui.Interface):

    def call(self):
        super().call()
        args = self.getArgs()

        save_file = False
        swap = None
        if args.save:
            save_file = args.save[0]
            save_file = self.f(save_file)

        if args.load:
            swap = ui.load_pickle(args.load[0])

        if args.run:
            swap = self.run_swap(save_file)

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

    def options(self):
        parser = super().options()

        parser.add_argument(
            '--save', nargs=1,
            help='The filename where the SWAP object should be stored')

        parser.add_argument(
            '--load', nargs=1,
            help='Load a pickled SWAP object')

        parser.add_argument(
            '--run', action='store_true',
            help='Run the SWAP algorithm')

        parser.add_argument(
            '--subject', nargs=1,
            help='Generate subject track plot and output to filename S')

        parser.add_argument(
            '--user', nargs=1,
            help='Generate user track plots and output to filename U')

        parser.add_argument(
            '--log', nargs=1,
            help='Write the entire SWAP export to file')

        return parser

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
