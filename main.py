import os
import time
import shutil
from aspect import process_aspect
from raster2shp import process_raster
from unionclip import process_union_clip

ohm_path = './input/OHM_FT_Fix.tif'
bo_path = './input/BO_FT.shp'
last_output = './output/roof_structure.shp'

#temp
temp = './temp'
o_path = os.path.join(temp, './aspect.tif')
o_shp = os.path.join(temp,'./output.shp')

def create_temp_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder temporary '{folder_path}' berhasil dibuat.")

def clear_temp_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder temporary '{folder_path}' berhasil dihapus.")

def main():
    create_temp_folder(temp)
    try:
        start = time.time()
        process_aspect(ohm_path, bo_path, o_path)
        print(f"Pembuatan Aspect selesai dalam {time.time() - start:.2f} detik")

        start = time.time()
        process_raster(o_path, o_shp, 4)
        print(f"Pembuatan shp dari Aspect selesai dalam {time.time() - start:.2f} detik")

        start = time.time()
        process_union_clip(o_shp, bo_path, last_output)
        print(f"Perapihan geometry selesai dalam {time.time() - start:.2f} detik")

    finally:
        clear_temp_folder(temp)
if __name__ == "__main__":
    main()