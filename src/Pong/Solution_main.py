"""Backwards-compatible entry point for the refactored Pong game."""

from game import PongGame


def main():
    PongGame().run()


if __name__ == "__main__":
    main()
