from tqdm import tqdm
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
import numpy as np
import geopandas as gpd

def process_aspect(ohm_path, building_outline_path, output_path):
    # Fungsi untuk menghitung aspect dengan rentang 0 hingga 360
    def calculate_aspect(dem):
        dx, dy = np.gradient(dem)
        aspect = np.arctan2(dy, -dx) * (180 / np.pi)  # Pembalikan dx dan dy
        aspect = (aspect + 360) % 360  # Memastikan rentang 0 hingga 360
        return aspect

    # Mulai progres bar
    total_steps = 5  # Jumlah tahapan utama dalam proses
    with tqdm(total=total_steps, desc="Processing Aspect", unit="step") as pbar:
        
        # Baca file OHM
        with rasterio.open(ohm_path) as src:
            ohm_data = src.read(1, resampling=Resampling.bilinear)
            profile = src.profile
            transform = src.transform
        pbar.update(1)  # Update progres bar

        # Hitung aspect dari data OHM
        aspect_data = calculate_aspect(ohm_data)
        pbar.update(1)  # Update progres bar

        # Baca outline gedung
        building_outline = gpd.read_file(building_outline_path)
        building_outline = building_outline.to_crs(profile["crs"])
        pbar.update(1)  # Update progres bar

        # Buat mask untuk area outline gedung
        mask = geometry_mask([geom for geom in building_outline.geometry], 
                             transform=transform, 
                             invert=True,
                             out_shape=aspect_data.shape)
        pbar.update(1)  # Update progres bar

        # Terapkan mask dan simpan hasil aspect yang sudah dipotong
        aspect_clipped = np.where(mask, aspect_data, np.nan)
        profile.update(dtype=rasterio.float32, count=1, nodata=np.nan)

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(aspect_clipped, 1)
        pbar.update(1)  # Update progres bar terakhir
