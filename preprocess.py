import numpy as np
import pandas as pd
from pathlib import Path
from pyimzml.ImzMLParser import ImzMLParser
import zarr


class IMSDataset:
    def __init__(self, fpath, micro_res=0.5, IMS_res=10):
        self.parser = ImzMLParser(fpath)
        self.micro_res = micro_res
        self.IMS_res = IMS_res
        self.IMS_px_in_micro = IMS_res / micro_res

    def __get_min_max_coords(self):
        coords = np.array(self.parser.coordinates)
        x_min, y_min, _ = np.min(coords, axis=0)
        x_max, y_max, _ = np.max(coords, axis=0)
        return x_min, y_min, x_max, y_max

    def to_columnar(self, mz_precision=4, dtype="uint32"):
        mzs, _ = self.parser.getspectrum(0)
        coords = np.array(dataset.parser.coordinates)
        x, y, _ = coords.T

        coords_df = pd.DataFrame(
            {
                "x": x,
                "y": y,
                "micro_x_topleft": x * self.IMS_px_in_micro - self.IMS_px_in_micro,
                "micro_y_topleft": y * self.IMS_px_in_micro - self.IMS_px_in_micro,
                "micro_px_width": np.repeat(self.IMS_px_in_micro, len(coords)),
            },
            dtype=dtype,
        )

        intensities = np.zeros((len(coords_df), len(mzs)))
        for i in range(len(coords)):
            _, coord_intensities = self.parser.getspectrum(i)
            intensities[i, :] = coord_intensities

        intensities = pd.DataFrame(
            intensities, columns=np.round(mzs, mz_precision).astype(str), dtype=dtype
        )

        return coords_df.join(intensities)

    def to_array(self):
        x_min, y_min, x_max, y_max = self.__get_min_max_coords()
        mz_lengths = self.parser.mzLengths
        if not (mz_lengths.count(mz_lengths[0]) == len(mz_lengths)):
            raise ValueError("The number of m/z is not the same at each coordinate.")

        arr = np.zeros((x_max - x_min + 1, y_max - y_min + 1, mz_lengths[0]))

        for idx, (x, y, _) in enumerate(self.parser.coordinates):
            _, intensities = self.parser.getspectrum(idx)
            arr[x - x_min, y - y_min, :] = intensities

        return arr

    def write_zarr(self, path, dtype="i4"):
        arr = self.to_array()
        z_arr = zarr.open(path, mode="w", shape=arr.shape, compressor=None, dtype=dtype)
        z_arr[:, :, :] = arr
        

if __name__ == "__main__":
    fpath = Path.cwd() / "data" / "VAN0001-RK-1-21-IMS.imzML"
    print("Parsing imzML...")
    dataset = IMSDataset(fpath)
    
    print("Creating columnar...")
    df = dataset.to_columnar()
    df.to_csv(f"{fpath.stem}.csv", index=False)
    
    print("Creating zarr array...")
    dataset.write_zarr(f"{fpath.stem}.zarr")
