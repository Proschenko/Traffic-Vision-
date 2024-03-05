import cv2
import random
import enum
import numpy


class People:
    def __init__(self, class_person, coordinates, conf) -> None:

        self.model_class: str = class_person  # если циферками класс задается то можно в случае чего преобразовывать в строку
        self.confidence: float = conf

        #Корды не нормализованы
        self.center_x: int = None
        self.center_y: int = None

        self._set_coordinates(coordinates)

    def _set_coordinates(self, coordinates):
        """
        Ставим новые координаты
        """
        self.center_x = coordinates[0]
        self.center_y = coordinates[1]

    # Смотрим насколько близко находится к двери
    def check_how_close_to_door(self):
        door_centers = [Doors.kid_center_door.value, Doors.women_center_door.value, Doors.men_center_door.value]
        #door_centers = [Doors.women_center_door.value]

        for door_center in door_centers:
            print("People", self.center_x, self.center_y, "Doors", door_center[0], door_center[1])
            distance_to_door = numpy.sqrt((self.center_x - door_center[0]) ** 2 + (self.center_y - door_center[1]) ** 2)
            distance_to_door = Tracking().get_normalized_coordinates((distance_to_door,0))[0]
            print(distance_to_door)
            if distance_to_door < 50:
                self.print_person()
                return
        # print("Not close enough")

    # Обновление структуры, новые координаты, новая уверенность в себе(в точности предсказания), сразу проверяем насколько близко к двери
    def update(self, coordinates, conf):
        self.confidence = conf
        self._set_coordinates(coordinates)
        self.check_how_close_to_door()

    # Выводит всю инфу
    def print_person(self):
        print("Class:", self.model_class)
        print("Confidence:", self.confidence)
        norm_x, norm_y =  Tracking().get_normalized_coordinates((self.center_x, self.center_y))
        print("X:", self.center_x, "Нормализованый:", norm_x)
        print("Y:", self.center_y, "Нормализованый:", norm_y)


class Doors(enum.Enum):
    women_center_door = (0.14453125, 0.244140625)
    men_center_door = (0.19375, 0.2109375)
    kid_center_door = (0.440625, 0.13046875000000002)


class Tracking:
    def __init__(self) -> None:
        self.image_width = 1920
        self.image_height = 1080

    #Для динамического определения разрешения убрал декоратор @staticmethod, теперь обращение по объекту, т.е. Tracking().get_normalized_coordinates()
    def get_normalized_coordinates(self, center):
        """
        Преобразует нормализованные координаты центра в абсолютные координаты для разрешения изображения.
        """
        absolute_x = int(center[0] * self.image_width)
        absolute_y = int(center[1] * self.image_height)
        return absolute_x, absolute_y

    def process_video_with_tracking(self, model, input_video_path, show_video=True, save_video=False,
                                    output_video_path="output_video.mp4"):
        # Open the input video file
        cap = cv2.VideoCapture(input_video_path)

        if not cap.isOpened():
            raise Exception("Error: Could not open video file.")

        # Get inaput video frame rate and dimensions
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        #Ставим актуальное разрешение
        self.image_width = frame_width
        self.image_height = frame_height
        
        # Define the output video writer
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = model.track(frame, iou=0.4, conf=0.5, persist=True, imgsz=608, verbose=False,
                                  tracker="botsort.yaml")

            self._tracking(results)

            if results[0].boxes.id != None:  # this will ensure that id is not None -> exist tracks
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)

                for box, id in zip(boxes, ids):
                    # Generate a random color for each object based on its ID
                    random.seed(int(id))
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                    cv2.putText(
                        frame,
                        f"Id {id}",
                        (box[0], box[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2,
                    )

            if save_video:
                out.write(frame)

            if show_video:
                frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
                cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Release the input video capture and output video writer
        cap.release()
        if save_video:
            out.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

    def _tracking(self, results):
        people_objects = self._process_tracking_results(results)

        for person in people_objects:
            person.check_how_close_to_door()

    @staticmethod
    def _process_tracking_results(tracking_results):
        """
        Process tracking results to compute the class, confidence score, and center of each bounding box.

        Parameters:
        - tracking_results: List of tracking results, where each result contains information about tracked objects.

        Returns:
        - List of People objects, where each object represents a person with their class, confidence score, and center coordinates.
        """
        result_objects = []

        for result in tracking_results:
            if result.boxes.id is not None:  # Check if there is a valid ID
                box = result.boxes.xyxy.cpu().numpy().astype(int)[0]
                center_x = (box[2] + box[0]) // 2
                center_y = (box[1] + box[3]) // 2
                confs = result[0].boxes.conf.tolist()
                class_object = result[0].boxes.cls.tolist()
                # print(int(class_object[0]), (center_x, center_y), confs[0])
                # Create a People object and append it to the list
                person = People(int(class_object[0]), (center_x, center_y), confs[0])
                result_objects.append(person)

        return result_objects


if __name__ == "__main__":
    a = People("kid", (0.44, 0.13), 0.952134)
    a.check_how_close_to_door()
