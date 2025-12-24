# import pytest
# from rest_framework import serializers
# from parking_point_edit_location.api.validators import (
#     validate_location_structure,
#     validate_no_existing_proposal,
#     validate_distance,
#     validate_user_not_voted,
#     validate_proposal_exists,
#     validate_has_edit_location_proposal,
# )
# from parking_point_edit_location.models import (
#     ParkingPointEditLocationVote,
# )
#
#
# # ============================================================
# #  Helpers
# # ============================================================
#
# class DummySerializer(serializers.Serializer):
#     location = serializers.JSONField(required=False)
#
#     def validate(self, attrs):
#         return attrs
#
#
# # ============================================================
# #  validate_location_structure
# # ============================================================
#
# def test_validate_location_structure_valid():
#     class TestSerializer(DummySerializer):
#         @validate_location_structure()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={"location": {"lat": 52.1, "lng": 21.0}}
#     )
#
#     assert serializer.is_valid(), serializer.errors
#
#
# @pytest.mark.parametrize(
#     "location",
#     [
#         None,
#         {},
#         {"lat": 10},
#         {"lng": 10},
#         {"lat": "abc", "lng": 10},
#         {"lat": 1000, "lng": 10},
#         {"lat": 10, "lng": 1000},
#     ],
# )
# def test_validate_location_structure_invalid(location):
#     class TestSerializer(DummySerializer):
#         @validate_location_structure()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(data={"location": location})
#     assert not serializer.is_valid()
#     assert "location" in serializer.errors
#
#
# # ============================================================
# #  validate_no_existing_proposal
# # ============================================================
#
# @pytest.mark.django_db
# def test_validate_no_existing_proposal_ok(parking_point):
#     parking_point.has_edit_location_proposal = False
#     parking_point.save()
#
#     class TestSerializer(DummySerializer):
#         @validate_no_existing_proposal()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={"parking_point": parking_point},
#     )
#
#     assert serializer.is_valid(), serializer.errors
#
#
# @pytest.mark.django_db
# def test_validate_no_existing_proposal_blocks(parking_point):
#     parking_point.has_edit_location_proposal = True
#     parking_point.save()
#
#     class TestSerializer(DummySerializer):
#         @validate_no_existing_proposal()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={"parking_point": parking_point},
#     )
#
#     assert not serializer.is_valid()
#     assert "parking_point" in serializer.errors
#
#
# # ============================================================
# #  validate_distance
# # ============================================================
#
# @pytest.mark.django_db
# def test_validate_distance_ok(parking_point):
#     parking_point.location = {"lat": 52.0, "lng": 21.0}
#     parking_point.save()
#
#     class TestSerializer(DummySerializer):
#         @validate_distance(min_distance=20, max_distance=100)
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={"location": {"lat": 52.0003, "lng": 21.0}},  # ~33m
#         context={"parking_point": parking_point},
#     )
#
#     assert serializer.is_valid(), serializer.errors
#
#
# @pytest.mark.django_db
# def test_validate_distance_too_close(parking_point):
#     parking_point.location = {"lat": 52.0, "lng": 21.0}
#     parking_point.save()
#
#     class TestSerializer(DummySerializer):
#         @validate_distance()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={"location": {"lat": 52.00005, "lng": 21.0}},  # ~5m
#         context={"parking_point": parking_point},
#     )
#
#     assert not serializer.is_valid()
#     assert "zbyt blisko" in serializer.errors["location"][0]
#
#
# @pytest.mark.django_db
# def test_validate_distance_too_far(parking_point):
#     parking_point.location = {"lat": 52.0, "lng": 21.0}
#     parking_point.save()
#
#     class TestSerializer(DummySerializer):
#         @validate_distance()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={"location": {"lat": 52.002, "lng": 21.0}},  # ~220m
#         context={"parking_point": parking_point},
#     )
#
#     assert not serializer.is_valid()
#     assert "zbyt daleko" in serializer.errors["location"][0]
#
#
# # ============================================================
# #  validate_user_not_voted
# # ============================================================
#
# @pytest.mark.django_db
# def test_validate_user_not_voted_ok(user_factory, edit_location, api_rf):
#     user = user_factory()
#     request = api_rf.post("/")
#     request.user = user
#
#     class TestSerializer(serializers.Serializer):
#         @validate_user_not_voted()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={
#             "request": request,
#             "proposal": edit_location,
#             "method": "POST",
#         },
#     )
#
#     assert serializer.is_valid(), serializer.errors
#
#
# @pytest.mark.django_db
# def test_validate_user_not_voted_blocks_second_vote(
#     user_factory, edit_location, api_rf
# ):
#     user = user_factory()
#
#     ParkingPointEditLocationVote.objects.create(
#         user=user,
#         parking_point_edit_location=edit_location,
#         is_like=True,
#     )
#
#     request = api_rf.post("/")
#     request.user = user
#
#     class TestSerializer(serializers.Serializer):
#         @validate_user_not_voted()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={
#             "request": request,
#             "proposal": edit_location,
#             "method": "POST",
#         },
#     )
#
#     assert not serializer.is_valid()
#
#
# # ============================================================
# #  validate_proposal_exists
# # ============================================================
#
# @pytest.mark.django_db
# def test_validate_proposal_exists_ok(edit_location):
#     class TestSerializer(serializers.Serializer):
#         @validate_proposal_exists()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={"proposal": edit_location},
#     )
#
#     assert serializer.is_valid()
#
#
# @pytest.mark.django_db
# def test_validate_proposal_exists_removed(edit_location):
#     edit_location.delete()
#
#     class TestSerializer(serializers.Serializer):
#         @validate_proposal_exists()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={"proposal": edit_location},
#     )
#
#     assert not serializer.is_valid()
#
#
# # ============================================================
# #  validate_has_edit_location_proposal
# # ============================================================
#
# @pytest.mark.django_db
# def test_validate_has_edit_location_proposal_ok(edit_location):
#     edit_location.parking_point.has_edit_location_proposal = True
#     edit_location.parking_point.save()
#
#     class TestSerializer(serializers.Serializer):
#         @validate_has_edit_location_proposal()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={"proposal": edit_location},
#     )
#
#     assert serializer.is_valid()
#
#
# @pytest.mark.django_db
# def test_validate_has_edit_location_proposal_inactive(edit_location):
#     edit_location.parking_point.has_edit_location_proposal = False
#     edit_location.parking_point.save()
#
#     class TestSerializer(serializers.Serializer):
#         @validate_has_edit_location_proposal()
#         def validate(self, attrs):
#             return attrs
#
#     serializer = TestSerializer(
#         data={},
#         context={"proposal": edit_location},
#     )
#
#     assert not serializer.is_valid()
