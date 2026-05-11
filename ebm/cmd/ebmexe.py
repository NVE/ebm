"""Starting point for the ebm project script defined in pyproject.toml."""

import os
import sys

from ebm.__version__ import version


def main() -> None:
    """
    Start ebm __main__ without a return value.

    Also sets DISABLE_PANDERA_IMPORT_WARNING to True so that pandera does not throw deprecation warning.

    Print version when the command line argument --version is passed

    Returns
    -------
    None

    """
    if '--version' in sys.argv:
        print(f'ebm {version}')
        sys.exit(0)
    os.environ['DISABLE_PANDERA_IMPORT_WARNING'] = 'True'
    from ebm.__main__ import main as ebm_main # noqa: PLC0415,I001
    ebm_main()


if __name__ == '__main__':
    main()
