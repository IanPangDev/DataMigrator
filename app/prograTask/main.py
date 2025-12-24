import argparse
from TaskController import TaskController
from TkLoggerView import TkLoggerView


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=int, required=True)
    parser.add_argument("--name", type=str, required=True)
    args = parser.parse_args()

    view = TkLoggerView()
    controller = TaskController(view)

    if args.mode == 0:
        controller.create_task(args.name)
    else:
        controller.delete_task(args.name)

    view.app.mainloop()


if __name__ == "__main__":
    main()