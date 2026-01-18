import arcade
from src.f1_data import load_session, get_race_telemetry, get_circuit_rotation, FPS

class WidgetOrchestrator:
    def __init__(self, year):
        self.year = year
        self.current_round = 1
        self.session = None
        self.race_telemetry = None
        self.example_lap = None # Add this
        self.frame_index = 0
        self.paused = False
        self.widgets = []

    def load_next_round(self):
        print(f"Loading {self.year} Round {self.current_round}...")
        try:
            self.session = load_session(self.year, self.current_round, 'R')
            self.session.load(laps=True, telemetry=True, weather=True) # Explicitly load weather data
            self.race_telemetry = get_race_telemetry(self.session, 'R')
            
            # --- CRITICAL: Get track layout for the TrackWidget ---
            fastest_lap = self.session.laps.pick_fastest()
            if fastest_lap is not None:
                self.example_lap = fastest_lap.get_telemetry()
            # ------------------------------------------------------

            self.frame_index = 0
            
            for w in self.widgets:
                w.on_session_change(self.session, self.race_telemetry)
                
            self.current_round += 1
        except Exception as e:
            print(f"Error loading round {self.current_round}: {e}")
            self.current_round = 1 
            # Avoid infinite recursion if the whole year fails
            # self.load_next_round()

    def update(self, delta_time):
        if self.paused or not self.race_telemetry:
            return

        self.frame_index += delta_time * FPS
        
        # Check if race finished
        if self.frame_index >= len(self.race_telemetry['frames']):
            self.load_next_round()