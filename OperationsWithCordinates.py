import numpy as np


class OperationsWithCoordinates():
    @staticmethod
    def boxes_center(corners: np.ndarray[float, float]) -> np.ndarray[float, float]:
        """
        Находит центры прямоугольников, которые заданны двумя углами.

        :param corners: Массив координат размера (n, 4) формата xyxy
        :type corners: np.ndarray[float, float]
        :return: Массив координат размера (n, 2) формата xy
        :rtype: np.ndarray[float, float]
        """
        return np.mean(corners.reshape((-1, 2, 2)), 1)

    # @staticmethod
    # def xxx(coordinate):
    #     mean_x = (coordinate[0] + coordinate[2]) / 2
    #     mean_y = (coordinate[1] + coordinate[3]) / 2
    #     return mean_x, mean_y
