import pathlib
from functools import lru_cache

import geopandas as gpd
from mediascope_api.mediavortex import catalogs as cwc

from app_settings import PROJECT_ROOT
from core.utils.tools import FileTools


@lru_cache(maxsize=1)
def load_daytypes():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'tv' / 'daytypes.json'))


@lru_cache(maxsize=1)
def load_kz_channels():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'tv' / 'kz_channels.json'))


@lru_cache(maxsize=1)
def load_nat_tvc_info():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'tv' / 'nat_tvc_info.json'))


@lru_cache(maxsize=1)
def load_reg_tvc_info():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'tv' / 'reg_tvc_info.json'))


@lru_cache(maxsize=1)
def load_drivetimes():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'radio' / 'mapping' / 'drivetimes.json'))


@lru_cache(maxsize=1)
def load_xlsx_formulas():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'xlsx_formulas.json'))


@lru_cache(maxsize=1)
def load_ooh_coefficients():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'ooh_coefficients.json'))


@lru_cache(maxsize=1)
def load_ru_subjects():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'ru_subjects.json'))


@lru_cache(maxsize=1)
def load_radiostations():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'radio' / 'mapping' / 'radiostations.json'))


@lru_cache(maxsize=1)
def load_broadcast():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'radio' / 'mapping' / 'broadcast.json'))


@lru_cache(maxsize=1)
def load_placement():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'radio' / 'mapping' / 'placement.json'))


@lru_cache(maxsize=1)
def load_status():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'radio' / 'mapping' / 'status.json'))


@lru_cache(maxsize=1)
def load_geo_data() -> dict[str, gpd.GeoDataFrame]:
    return _load_geo_data(PROJECT_ROOT / 'assets' / 'ooh' / 'geodata')


def _load_geo_data(directory: pathlib.Path) -> dict[str, gpd.GeoDataFrame]:
    if not directory.is_dir():
        raise FileNotFoundError('Указанная директория не существует')

    geo_data: dict[str, gpd.GeoDataFrame] = {}
    for filepath in directory.rglob('*.geojson'):
        try:
            gdf = gpd.read_file(filepath)
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            if gdf.crs.to_epsg() != 3857:  # type: ignore
                gdf = gdf.to_crs(epsg=3857)
            geo_data[filepath.stem] = gdf
        except Exception as e:
            raise RuntimeError('Не удалось загрузить файл') from e

    return geo_data


@lru_cache(maxsize=1)
def load_advertisers():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'advertisers.json'))


@lru_cache(maxsize=1)
def load_table_advertiser():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'advertiser.json'))


@lru_cache(maxsize=1)
def load_formats():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'formats.json'))


@lru_cache(maxsize=1)
def load_locations():
    locations_dir = PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'locs'
    merged = {}
    for json_file in locations_dir.glob('*.json'):
        key = json_file.stem
        merged[key] = FileTools.load_json(str(json_file))
    return merged


@lru_cache(maxsize=1)
def load_operators():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'operators.json'))


@lru_cache(maxsize=1)
def load_radiostantions():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'radiostantions.json'))


@lru_cache(maxsize=1)
def load_sides():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'sides.json'))


@lru_cache(maxsize=1)
def load_sizes():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'sizes.json'))


@lru_cache(maxsize=1)
def load_mediascope_cats():
    return cwc.MediaVortexCats()


@lru_cache(maxsize=1)
def load_users():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'users.json'))


@lru_cache(maxsize=1)
def load_specific_locs():
    return FileTools.load_json(str(PROJECT_ROOT / 'assets' / 'ooh' / 'mapping' / 'locs' / 'UNION.json'))
