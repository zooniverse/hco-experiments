#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm


from swap import ui


def main():
    interface = ui.SWAPInterface()
    ui.run(interface)


if __name__ == "__main__":
    main()
