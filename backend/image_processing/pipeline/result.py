def build_result(
    image_path: str,
    width: int,
    height: int,
    colors: int,
    dmc_list: list
):
    return {
        "image": image_path,
        "width": width,
        "height": height,
        "colors": colors,
        "dmc_threads": dmc_list
    }
