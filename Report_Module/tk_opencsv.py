import pandas as pd
import os
import re
import numpy as np
import gc

from PIL import Image
import requests
from io import BytesIO

def read_csv(csv_file):
    f_extension = os.path.splitext(os.path.basename(csv_file))[-1]
    if f_extension != ".csv":
        return 1, None

    data = pd.read_csv(csv_file)

    re_compiler = re.compile("^([A-Z] = )")
    target_img_dict = {}
    sample_img_dict = {}

    sample_detail = { "Background" : None
                    , "Product dimension" : None
                    }

    test_criteria = { "Lighting Dimension (mm)" : None
                    , "Lighting Thickness (mm)" : None
                    , "Lighting Inner Diameter" : None
                    , "Lighting Working Distance (mm)" : None
                    , "Lens Working Distance (mm)" : None
                    , "Field of View (mmxmm)" : None
                    ,
                    }
    light_detail = {  "Lighting Model Number" : None
                    , "Lighting Color": None
                    , "Accesories (Polarizer/Diffuser/Extension Cable/Mounting Bracket)" : None
                    , "Lighting Voltage / Current (mA)" : None
                    }

    ctrl_detail = {   "Controller Model" : None
                    , "Controller Mode (Constant / Strobe / Trigger)": None
                    , "Current Multiplyer" : None
                    , "Intensity" : None
                    }

    cam_detail = {    "Camera Model" : None
                    , "Sensor Size": None
                    , "Resolution (pixel)" : None
                    , "Megapixel" : None
                    , "Sensor Type" : None
                    , "Pixel Size (mm)" : None
                    , "Shutter Type" : None
                    , "Mono/Color" : None
                    , "X axis (mm)" : None
                    , "Y axis (mm)" : None
                    }

    lens_detail = {   "Lens model" : None
                    , "Focal length (mm)" : None
                    , "Mount" : None
                    , "Sensor Size (max)": None
                    , "TV distortion (%)" : None
                    , "F.O.V (mm)" : None
                    }

    for col in data.columns:
        kw = str(re.sub(re_compiler, "", col))
        if kw in sample_detail:
            s = str(data[col].values[0])
            if s == 'nan':
                sample_detail[kw] = None
            else:
                sample_detail[kw] = s

        if kw in test_criteria:
            s = str(data[col].values[0])
            if s == 'nan':
                test_criteria[kw] = None
            else:
                test_criteria[kw] = s

        if kw in light_detail:
            s = str(data[col].values[0])
            if s == 'nan':
                light_detail[kw] = None
            else:
                light_detail[kw] = s

        if kw in ctrl_detail:
            s = str(data[col].values[0])
            if s == 'nan':
                ctrl_detail[kw] = None
            else:
                ctrl_detail[kw] = s

        if kw in cam_detail:
            s = str(data[col].values[0])
            if s == 'nan':
                cam_detail[kw] = None
            else:
                cam_detail[kw] = s

        if kw in lens_detail:
            s = str(data[col].values[0])
            if s == 'nan':
                lens_detail[kw] = None
            else:
                lens_detail[kw] = s

        if kw == 'Desire Result Photo':
            url_list = data[col].values[0].splitlines()
            for i, url in enumerate(url_list):
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                np_img = np.array(img)
                target_img_dict[str(i)] = np_img

            del url_list

        if kw == 'Product Photo':
            url_list = data[col].values[0].splitlines()
            for i, url in enumerate(url_list):
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                np_img = np.array(img)
                sample_img_dict[str(i)] = np_img

            del url_list

    del data
    gc.collect()

    return 0, [sample_detail, test_criteria, light_detail, ctrl_detail, cam_detail, lens_detail], [sample_img_dict, target_img_dict]
