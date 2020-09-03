"""
Ego-vehicle is performing a right turn at an intersection, yielding to crossing traffic.
Based on 2019 Carla Challenge Traffic Scenario 09.
"""
param map = localPath('../../carla/OpenDrive/Town05.xodr')  # or other CARLA map that definitely works
param carla_map = 'Town05'
model scenic.domains.driving.model

DELAY_TIME_1 = 1 # the delay time for ego
DELAY_TIME_2 = 40 # the delay time for the slow car
FOLLOWING_DISTANCE = 13 # normally 10, 40 when DELAY_TIME is 25, 50 to prevent collisions

DISTANCE_TO_INTERSECTION1 = Uniform(10, 15) * -1
DISTANCE_TO_INTERSECTION2 = Uniform(15, 20) * -1
SAFETY_DISTANCE = 20
BRAKE_INTENSITY = 1.0


behavior CrossingCarBehavior(trajectory):
	do FollowTrajectoryBehavior(trajectory = trajectory)
	terminate

behavior EgoBehavior(trajectory):
	print("position: ", self.position)
	try :
		do FollowTrajectoryBehavior(trajectory=trajectory)
	interrupt when distanceToAnyObjs(self, SAFETY_DISTANCE):
		print("distance breached")
		take SetBrakeAction(BRAKE_INTENSITY)


spawnAreas = []
fourWayIntersection = filter(lambda i: i.is4Way, network.intersections)
intersec = Uniform(*fourWayIntersection)

startLane = Uniform(*intersec.incomingLanes)
straight_maneuvers = filter(lambda i: i.type == ManeuverType.STRAIGHT, startLane.maneuvers)
straight_maneuver = Uniform(*straight_maneuvers)
straight_trajectory = [straight_maneuver.startLane, straight_maneuver.connectingLane, straight_maneuver.endLane]

conflicting_rightTurn_maneuvers = filter(lambda i: i.type == ManeuverType.RIGHT_TURN, straight_maneuver.conflictingManeuvers)
ego_rightTurn_maneuver = Uniform(*conflicting_rightTurn_maneuvers)
ego_startLane = ego_rightTurn_maneuver.startLane
ego_trajectory = [ego_rightTurn_maneuver.startLane, ego_rightTurn_maneuver.connectingLane, \
								ego_rightTurn_maneuver.endLane]

spwPt = startLane.centerline[-1]
csm_spwPt = ego_startLane.centerline[-1]

# crossing_car = Car following roadDirection from spwPt for DISTANCE_TO_INTERSECTION1,
# 				with behavior CrossingCarBehavior(trajectory = straight_trajectory)

# ego = Car following roadDirection from csm_spwPt for DISTANCE_TO_INTERSECTION2,
# 				with behavior EgoBehavior(ego_trajectory)

# position:  (-58.42084503173828 @ 116.73458862304688)
# controller acts out (27.202537536621094 @ 122.28080749511719)


spwPt = Point at -94.67450714111328 @ -84.45836639404297
ego_lane = network.laneAt(spwPt)
maneuvers =  filter(lambda i: i.type == ManeuverType.RIGHT_TURN, ego_lane.maneuvers)
rightTurn_maneuver = Uniform(*maneuvers)
traj = [rightTurn_maneuver.startLane, rightTurn_maneuver.connectingLane, rightTurn_maneuver.endLane]
print("endLane's intersection", traj[-1].maneuvers)

ego = Car at spwPt,
		with behavior EgoBehavior(traj)

