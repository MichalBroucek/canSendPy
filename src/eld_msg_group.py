class ELD_msg_group:
    """
    ELD message group - holds values for one stage of ELD message simulation
      - description of simulation stage
      - vehicle speed
      - vehicle distance
      - engine speed r.p.m.
      - engine hours
      - VIN code
      - duration of this stage [s]
    """

    def __init__(self, description="", speed=0, distance=0, engine_speed=0, engine_hours=0, vin=None, duration=0):
        self.description = description
        self.vehicle_speed = speed
        self.vehicle_distance = distance
        self.engine_speed = engine_speed
        self.engine_hours = engine_hours
        self.vin_code = vin
        self.duration = duration

    def print(self):
        print("Simulation step: {0}\nspeed={1};distance={2};engine_rpm={3};engine_hours={4};vin={5}\nduration={6}"
              .format(self.description, self.vehicle_speed, self.vehicle_distance, self.engine_speed, self.engine_hours,
                      self.vin_code, self.duration))
