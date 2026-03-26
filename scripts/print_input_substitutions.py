import pathlib

from loguru import logger

import ebm


def main() -> None:
    ebm_data = pathlib.Path(ebm.__file__).parent / 'data'
    logger.info('Using {data_dir}', data_dir=ebm_data)
    logger.complete()

    for c in ebm_data.glob('*.csv'):
        s = f'.. |{c.stem}_ref| replace:: :ref:`{c.name} 🧾<{c.stem} csv>`'
        print(s)
        print()


if __name__ == '__main__':
    main()
