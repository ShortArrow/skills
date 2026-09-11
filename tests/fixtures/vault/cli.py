"""List share links from the command line."""
import argparse
import sys

import handler


def main(argv):
    parser = argparse.ArgumentParser(description="List share links")
    parser.add_argument("--user", help="only links owned by this user")
    args = parser.parse_args(argv)
    for token, link in handler.LINKS.items():
        if args.user and link["user"] != args.user:
            continue
        print(token, link["user"], link["path"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
