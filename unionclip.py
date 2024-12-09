from tqdm import tqdm
import geopandas as gpd
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union, snap

def process_union_clip(roof_structure_path, building_outline_path, output_union_path):
    with tqdm(total=6, desc="Processing Union and Clip", unit="step") as pbar:
        # Langkah 1: Baca file SHP dari roof_structure dan building_outline
        roof_structure = gpd.read_file(roof_structure_path)
        building_outline = gpd.read_file(building_outline_path)
        pbar.update(1)

        # Langkah 2: Memperbaiki geometri dengan buffer untuk geometri yang bermasalah
        def safe_buffer(geom, buffer_distance, boundary_geom):
            """
            Menghasilkan buffer aman yang tidak melebihi boundary_geom.
            """
            if geom and geom.is_valid:
                buffered = geom.buffer(buffer_distance)
                if buffered.is_valid:
                    # Batasi hasil buffer dengan boundary geometry
                    return buffered.intersection(boundary_geom)
            return None

        building_union = unary_union(building_outline.geometry)  # Gabungkan seluruh outline untuk batasan

        roof_structure['geometry'] = roof_structure['geometry'].apply(
            lambda geom: safe_buffer(geom, 0, building_union) if geom else None)
        building_outline['geometry'] = building_outline['geometry'].apply(
            lambda geom: safe_buffer(geom, 0, building_union) if geom else None)
        pbar.update(1)

        # Langkah 3: Menghapus geometri None atau invalid setelah buffering
        roof_structure = roof_structure[roof_structure['geometry'].notnull() & roof_structure.is_valid]
        building_outline = building_outline[building_outline['geometry'].notnull() & building_outline.is_valid]
        pbar.update(1)

        # Langkah 4: Memastikan tidak ada overlap atau perpotongan yang tidak sesuai
        try:
            roof_structure['geometry'] = roof_structure['geometry'].apply(
                lambda geom: snap(geom, building_union, tolerance=0.01))
            building_outline['geometry'] = building_outline['geometry'].apply(
                lambda geom: snap(geom, building_union, tolerance=0.01))
            pbar.update(1)
        except Exception as e:
            print(f"Error during snapping: {e}")
            return

        # Langkah 5: Operasi Clip - memotong data roof_structure dengan building_outline
        try:
            roof_clipped = gpd.clip(roof_structure, building_outline)
            roof_clipped['geometry'] = roof_clipped['geometry'].apply(
                lambda geom: safe_buffer(geom, 0, building_union) if geom else None)
            roof_clipped = roof_clipped[roof_clipped['geometry'].notnull() & roof_clipped.is_valid]
            pbar.update(1)
        except Exception as e:
            print(f"Error during clipping: {e}")
            return

        # Langkah 6: Operasi Union - Menggabungkan hasil clip dengan building_outline
        try:
            result_union = gpd.overlay(building_outline, roof_clipped, how="union")
            pbar.update(1)
        except Exception as e:
            print(f"Error during union operation: {e}")
            return

        # Menyimpan hasil union ke file shapefile baru
        try:
            result_union.to_file(output_union_path, driver="ESRI Shapefile")
            print("Operasi Union dan Clip selesai!")
        except Exception as e:
            print(f"Error saving file: {e}")
