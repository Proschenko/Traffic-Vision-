from typing import Any, Type


def asdict(cls: Type) -> dict[str, Any]:
    return {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}

class DetectorArgs:
    iou = 0.4
    conf = 0.5
    persist = True
    imgsz = 640
    verbose = False
    tracker = "botsort.yaml"

class Detector:
    model_path = "runs/detect/train8/weights/best.pt"
    args = asdict(DetectorArgs)

class Doors:
    names = ("women", "men", "kid")
    path = "doors_corners.txt"

class Drawer:
    resize = False
    boxes = True
    doors = True
    lines = False
    points = True

class Framer:
    size = 640
    height1 = 300
    height2 = 150
    start2 = 900
    border = 20

class Master:
    show_video = True
    save_path = None

class RedisArgs:
    host = 'localhost'
    port = 6379
    decode_responses = True

class Redis:
    args = asdict(RedisArgs)


url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
url_small = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/102'
