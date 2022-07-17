import os
import pytest

from route import *


class TestRoute:

    test_file = "tests/data/route_1.kml"

    def test_route_init(self):
        """
        Test that the route object is initialized with a path to a kml file
        """
        route = Route(self.test_file)
        assert route is not None

    def test_get_total_distance(self, sample_route: Route):
        """
        Test that the total distance of the route is returned and is equal to
        the approx route distance before smoothing
        """
        assert float(sample_route.get_total_distance()) == pytest.approx(
            52.392, 0.1
        )

    def test_smoothen_route(self, sample_route: Route):
        """
        Test that the route is smoothened
        """
        sample_route.smoothen_route()
        assert sample_route.smoothened_line_string is not None

    def test_get_total_distance_after_smoothing(self, sample_route: Route):
        """
        Test that the total distance of the route is returned and is equal to
        the approx route distance after smoothing
        """
        sample_route.smoothen_route()
        assert float(sample_route.get_total_distance()) == pytest.approx(
            12.914, 0.1
        )

    def test_to_file(self, sample_route: Route, tmp_path: str):
        """Test that the smoothened route is written to a kml file"""
        file = tmp_path / "smoothen_route.kml"
        sample_route.smoothen_route()
        sample_route.to_file(file)
        assert os.path.exists(file)

    def test_invalid_file(self):
        """
        Test that an error is raised when an invalid file is passed to the
        route object
        """
        with pytest.raises(ValueError):
            Route("invalid_file.kml")

    def test_invalid_cutoff_distance_to_route_smoothen(
        self, sample_route: Route
    ):
        """
        Test that an error is raised when an invalid cutoff distance is passed
        to the route object
        """
        with pytest.raises(ValueError):
            sample_route.smoothen_route(cutoff_distance=100000)
        with pytest.raises(ValueError):
            sample_route.smoothen_route(cutoff_angle="de")

    def test_invalid_cutoff_angle_to_route_smoothen(self, sample_route: Route):
        """
        Test that an error is raised when an invalid cutoff angle is passed to
        the route object
        """
        with pytest.raises(ValueError):
            sample_route.smoothen_route(cutoff_angle=90)
        with pytest.raises(ValueError):
            sample_route.smoothen_route(cutoff_angle="de")

    def test_invalid_granular_level_to_route_smoothen(
        self, sample_route: Route
    ):
        """
        Test that an error is raised when an invalid granular level is passed
        to the route object
        """
        with pytest.raises(ValueError):
            sample_route.smoothen_route(granular_level=11)
        with pytest.raises(ValueError):
            sample_route.smoothen_route(granular_level="de")

    def test_smoothen_by_distance(self, sample_route: Route):
        """
        Test that the route is smoothened by a given cutoff distance
        """
        distance_before_smoothing = sample_route.get_total_distance()
        sample_route._smoothen_by_distance(cutoff_distance=100)
        distance_after_smoothing = sample_route.get_total_distance()
        assert sample_route.smoothened_line_string is not None
        assert distance_before_smoothing > distance_after_smoothing

    def test_smoothen_by_angle(self, sample_route: Route):
        """
        Test that the route is smoothened by a given a cutoff angle
        """
        distance_before_smoothing = sample_route.get_total_distance()
        sample_route._smoothen_by_angle(cutoff_angle=40)
        distance_after_smoothing = sample_route.get_total_distance()
        assert sample_route.smoothened_line_string is not None
        assert distance_before_smoothing > distance_after_smoothing

    def test_smoothen_by_simplifying(self, sample_route: Route):
        """
        Test that the route is smoothened by a given a granular level
        """
        distance_before_smoothing = sample_route.get_total_distance()
        sample_route._smoothen_by_simplifying(granular_level=4)
        distance_after_smoothing = sample_route.get_total_distance()
        assert sample_route.smoothened_line_string is not None
        assert distance_before_smoothing > distance_after_smoothing

    def test_get_line_string(self, sample_route: Route):
        """
        Test that the smoothened line string line string is returned after the
        route is smoothened otherwise the raw line string is returned
        """
        line_string_before_smoothing = sample_route._Route__get_line_string()
        sample_route.smoothen_route()
        line_string_after_smoothing = sample_route._Route__get_line_string()
        assert line_string_before_smoothing != line_string_after_smoothing

    def test_get_coord_angle(self, sample_route: Route):
        """
        Test that angle between three lines is returned
        """
        coord_angle = sample_route._Route__get_coord_angle(2, 2, 2)
        assert coord_angle == pytest.approx(60, 0.1)

    def test_remove_close_duplicate_coords(self, sample_route: Route):
        """
        Test that close duplicate coordinates are removed
        """
        raw_line_string = sample_route.gdf.geometry.iloc[0]
        sample_route.line_string = raw_line_string

        coord_count_before_removal = len(sample_route.line_string.coords)
        sample_route._Route__remove_close_duplicate_coords()
        coord_count_after_removal = len(sample_route.line_string.coords)

        assert coord_count_before_removal > coord_count_after_removal

    def test_validate_smoothen_input(self, sample_route):
        """
        Test that error is raised when invalid input is passed to
        validate_smoothen_input
        """
        with pytest.raises(ValueError):
            sample_route._Route__validate_smoothen_input(
                granular_level="de", cutoff_distance="de", cutoff_angle="de"
            )

    def test_get_distance_between_coords(self, sample_route):
        """
        Test that the distance between two coordinates is returned
        """
        distance = sample_route._Route__get_distance_between_coords(
            (13.296698, 52.46445, 0), (13.360589, 52.47494, 0)
        )
        assert distance == pytest.approx(4500, 0.1)
