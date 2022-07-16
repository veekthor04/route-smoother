import geopandas as gpd

from fiona.drvsupport import supported_drivers
from shapely.geometry import LineString, shape
from pyproj import Geod
from math import acos, degrees


supported_drivers["KML"] = "rw"
supported_drivers["LIBKML"] = "rw"


class Route:
    """
    A route object is kml file with a single line string which can be
    smoothened by several methods.
    """

    def __init__(self, path: str) -> None:
        """Initialize the route object with a path to a kml file

        Parameters
        ----------
        path : str
            the path to the kml file

        Examples
        ----------
        create a route object from a kml file.
            >>> route = Route("path/to/file.kml")

        get the total distance of the route.
            >>> route.get_total_distance()
            23.304

        smoothen the route.
            >>> route.smoothen_route()

        write the smoothened route to a kml file.
            >>> route.to_file("path/to/file.kml")
        """

        self.path = path
        self.gdf: gpd.GeoDataFrame = gpd.read_file(path, driver="KML")
        self.line_string: LineString = self.gdf.geometry.iloc[0]
        self.__remove_close_duplicate_coords()
        self.geod = Geod(ellps="WGS84")
        self.smoothened_line_string = None

    def get_total_distance(self) -> str:
        """Returns the total distance of smoothen (if available) or raw route

        Returns
        -------
        str
            The total distance of the route in kilometers
        """

        line_string = self.__get_line_string()
        return f"{self.geod.geometry_length(line_string)/1000:.3f}"

    def _smoothen_by_simplifying(self, granular_level: float) -> None:
        """Smoothen the line string by a given granular level"""

        tolerance = granular_level * 0.00003
        print("tolerance", tolerance)
        self.smoothened_line_string = self.__get_line_string().simplify(
            tolerance,
        )

    def _smoothen_by_distance(self, cutoff_distance: int):
        """Smoothen the line string by a given cutoff distance"""

        line_coords = list(shape(self.__get_line_string()).coords)
        filtered_coords = []

        for i, line_coord in enumerate(line_coords):
            if i == 0 or i == len(line_coords) - 1:
                filtered_coords.append(line_coord)
                continue
            current_line_string = LineString([filtered_coords[-1], line_coord])
            current_distance = self.geod.geometry_length(current_line_string)

            if current_distance < cutoff_distance:
                filtered_coords.append(line_coord)

        self.smoothened_line_string = LineString(filtered_coords)

    def _smoothen_by_angle(self, cutoff_angle: int) -> None:
        """Smoothen the line string by a given cutoff angle"""

        line_coords = list(shape(self.__get_line_string()).coords)
        filtered_coords = []

        geod = self.geod
        for i, line_coord in enumerate(line_coords):
            if i == 0 or i == len(line_coords) - 1:
                filtered_coords.append(line_coord)
                continue

            previous_to_current_line_string = LineString(
                [filtered_coords[-1], line_coord]
            )
            previous_to_current_distance = geod.geometry_length(
                previous_to_current_line_string
            )

            current_to_next_line_string = LineString(
                [line_coord, line_coords[i + 1]]
            )
            current_to_next_distance = geod.geometry_length(
                current_to_next_line_string
            )

            previous_to_next_line_string = LineString(
                [filtered_coords[-1], line_coords[i + 1]]
            )
            previous_to_next_distance = geod.geometry_length(
                previous_to_next_line_string
            )

            if (
                self.__get_point_angle(
                    previous_to_current_distance,
                    previous_to_next_distance,
                    current_to_next_distance,
                )
                < cutoff_angle
            ):
                continue
            filtered_coords.append(line_coord)

        self.smoothened_line_string = LineString(filtered_coords)

    @staticmethod
    def __get_point_angle(A: float, B: float, C: float) -> float:
        """
        Calculates the angle between three points A, B, C in degrees. The
        returned angle is the angle between the line AB and the line BC
        """
        try:
            return degrees(acos((A * A + C * C - B * B) / (2 * A * C)))
        except (ValueError, ZeroDivisionError):
            return 0

    def __get_line_string(self) -> LineString:
        """
        Returns the smoothen line string (if exists)  of raw line string
        of the route
        """
        if self.smoothened_line_string:
            return self.smoothened_line_string
        return self.line_string

    def __remove_close_duplicate_coords(self):
        """Remove similar coordinates that are too close to each other"""
        line_coords = list(shape(self.line_string).coords)

        filtered_coords = []
        for i, line_coord in enumerate(line_coords):
            if i == 0:
                filtered_coords.append(line_coord)
                continue
            if line_coord != filtered_coords[-1]:
                filtered_coords.append(line_coord)

        self.line_string = LineString(filtered_coords)

    def to_file(self, path: str = None):
        """Write the smoothen route to a file

        Parameters
        ----------
        path : str, optional
            The path to the file. If not provided, the path of the original file
        """
        if not path:
            path = self.path
        self.gdf.geometry.iloc[0] = self.__get_line_string()
        self.gdf.to_file(path, driver="KML")

    def smoothen_route(
        self,
        granular_level: int = 5,
        cutoff_angle: int = 45,
        cutoff_distance: int = 500,
    ) -> None:
        """Smoothen the route by a given granular level, cutoff angle and
        cutoff distance

        Parameters
        ----------
        granular_level : int, optional
            Determines the granularity of the simplification, by default 5
        cutoff_angle : int, optional
            The cutoff angle in degrees which defines the minimum allowed
            angle between a middle coordinate and the neighboring coordinates
            , by default 45
        cutoff_distance : int, optional
            The cutoff distance in meters which defines the maximum allowed
            distance between two points, by default 500
        """

        self.__validate_smoothen_input(
            granular_level, cutoff_angle, cutoff_distance
        )
        self._smoothen_by_distance(cutoff_distance)
        self._smoothen_by_angle(cutoff_angle)
        self._smoothen_by_simplifying(granular_level)

    def __validate_smoothen_input(
        self, granular_level, cutoff_angle, cutoff_distance
    ) -> None:
        """Validate the input for smoothen_route"""
        if granular_level < 0 or granular_level > 10:
            raise ValueError("Granular level must be between 0 and 10")

        if not isinstance(granular_level, int):
            raise ValueError("Granular level must be an integer")

        if cutoff_angle < 0 or cutoff_angle > 60:
            raise ValueError("Cutoff angle must be between 0 and 60")

        if not isinstance(cutoff_angle, int):
            raise ValueError("Cutoff angle must be an integer")

        if cutoff_distance < 0 or cutoff_distance > 1000:
            raise ValueError("Cutoff distance must be between 0 and 10000")

        if not isinstance(cutoff_distance, int):
            raise ValueError("Cutoff distance must be an integer")


# route = Route("task_2_sensor.kml")

# print(route.get_total_distance())

# route.smoothen_route(
#     granular_level=5,
#     cutoff_angle=45,
#     cutoff_distance=500,
# )

# print(route.get_total_distance())

# route.to_file("task_2_sensor_smoothened.kml")
