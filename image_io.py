def load_image(path):
    """Load an image as a numpy array, using OpenCV when available."""
    try:
        import cv2

        image = cv2.imread(path)
        if image is not None:
            return image
    except ImportError:
        pass

    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("读取本地图片需要安装 opencv-python 或 pillow") from exc

    return Image.open(path).convert("RGB")
