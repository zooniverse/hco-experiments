#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels


def main():
    logging.init(__name__, __file__)

    ui = swap.ui.UI()
    RocInterface(ui)
    BootInterface(ui)
    experiment.Interface(ui)

    ui.run()


if __name__ == "__main__":
    main()
