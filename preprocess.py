import numpy as np
import pandas as pd
from pathlib import Path
from pyimzml.ImzMLParser import ImzMLParser


class IMSDataset:
    def __init__(self, fpath, micro_res=0.5, IMS_res=10):
        self.parser = ImzMLParser(fpath)
        self.micro_res = micro_res
        self.IMS_res = IMS_res
        self.IMS_px_in_micro = IMS_res / micro_res
        self.coord_fields = [
            "x",
            "y",
            "micro_x_topleft",
            "micro_y_topleft",
            "micro_px_width",
        ]

    def __iter__(self):
        for idx, (x, y, z) in enumerate(self.parser.coordinates):
            micro_x_topleft = x * 20 - self.IMS_px_in_micro
            micro_y_topleft = y * 20 - self.IMS_px_in_micro
            coords = [x, y, micro_x_topleft, micro_y_topleft, self.IMS_px_in_micro]
            _, intensities = self.parser.getspectrum(idx)
            yield np.concatenate([coords, intensities])

    def to_columnar(self):
        mzs, _ = self.parser.getspectrum(0)
        df = pd.DataFrame(iter(self), dtype="uint32")
        df.columns = np.concatenate((self.coord_fields, np.round(mzs, 4)))
        return df


if __name__ == "__main__":
    fpath = Path.cwd() / "data" / "VAN0001-RK-1-21-IMS.imzML"
    dataset = IMSDataset(fpath)
    df = dataset.to_columnar()
    df.to_csv(f"{fpath.stem}.csv", index=False)
