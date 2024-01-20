#!/usr/bin/env python3
""" Search for identical file in any of the supplied directories"""
import argparse
import filecmp
import os
import sys
import textwrap
from importlib.metadata import version

import macos_tags


class RawFormatter(argparse.HelpFormatter):
    """Help formatter"""

    def _fill_text(self, text, width, indent):
        """Split the text on newlines and indent each line"""
        return "\n".join(
            [
                textwrap.fill(line, width)
                for line in textwrap.indent(textwrap.dedent(text), indent).splitlines()
            ]
        )


class Check4Duplicates:
    """This class is responsible for searching for identical files
    in any of the supplied directories"""

    def __init__(self):
        self.parser = None
        self.directories = None
        self.reference_file = None
        self.ref_size = 0
        self.ref_sha256 = None
        self.matches = 0
        self.make_cmd_line_parser()
        self.verbose = False

    def make_cmd_line_parser(self):
        """Set up the command line parser"""

        self.parser = argparse.ArgumentParser(
            formatter_class=RawFormatter,
            description=(
                "Search for a identical file in any of the supplied directories\n"
                "    It will exit 0 if no duplicates are found, "
                "1 if duplicates are found and 2 any error found\n"
                "    If the file is a duplicate, the color is set to RED on Darwin"
            ),
        )
        self.parser.add_argument(
            "-d",
            "--directory",
            action="append",
            help="Directory to search (Can be specified multiple times). "
            "If an invalid directory is specified, the program will exit with an error "
            "but the refrence file color will not be changed",
        )
        self.parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=version("dml-check4duplicates"),
            help="Print the version number",
        )
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            default=False,
            help="Display files that are identical",
        )

        self.parser.add_argument("reference_file")

    def parse_args(self):
        """Parse the command line arguments"""
        args = self.parser.parse_args()
        self.directories = args.directory
        self.reference_file = args.reference_file
        self.verbose = args.verbose

    def validate_args(self):
        """Validate the command line arguments"""
        if len(self.directories) == 0:
            self.parser.print_help()
            sys.exit(2)
        if not os.path.isfile(self.reference_file):
            print(f"Reference file {self.reference_file} does not exist")
            sys.exit(2)
        self.ref_size = os.stat(self.reference_file).st_size
        if self.ref_size == 0:
            print(f"Reference file {self.reference_file} is empty")
            sys.exit(2)

    @staticmethod
    def mark_as_duplicate(file):
        """Mark a file as duplicate"""
        tag = macos_tags.Tag(name="Duplicate", color=macos_tags.Color.RED)
        macos_tags.add(tag, file=file)
        sys.exit(1)

    def run(self):
        """Run the program"""
        self.parse_args()
        self.validate_args()
        macos_tags.remove_all(file=self.reference_file)
        self.ref_size = os.stat(self.reference_file).st_size
        # pylint: disable=too-many-nested-blocks
        for directory in self.directories:
            if not os.path.isdir(directory):
                print(f"Directory {directory} does not exist")
                sys.exit(1)
            for root, _, files in os.walk(directory):
                for f in files:
                    file = os.path.join(root, f)
                    file_size = os.stat(file).st_size
                    if file_size == self.ref_size:
                        if filecmp.cmp(self.reference_file, file, shallow=False):
                            tag = macos_tags.Tag(name="Duplicate", color=macos_tags.Color.RED)
                            macos_tags.add(tag, file=self.reference_file)
                            if self.verbose:
                                print(f"File {file} is identical to {self.reference_file}")
                            sys.exit(1)

        tag = macos_tags.Tag(name="Unique", color=macos_tags.Color.GREEN)
        macos_tags.add(tag, file=self.reference_file)
        sys.exit(0)


def main():
    """Main entry point"""
    instance = Check4Duplicates()
    instance.run()


if __name__ == "__main__":
    main()
