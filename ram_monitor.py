import psutil


class RAMMonitor:

    def __init__(self):
        self.ram_before = 0
        self.ram_peak = 0
        self.ram_after = 0

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_ram_used_mb(self):
        memory = psutil.virtual_memory()

        return memory.used / (1024 * 1024)

    def start_monitoring(self):
        self.ram_before = self.get_ram_usage()
        self.ram_peak = self.ram_before

    def update_peak(self):
        current_ram = self.get_ram_usage()

        if current_ram > self.ram_peak:
            self.ram_peak = current_ram

        return current_ram

    def stop_monitoring(self):
        self.ram_after = self.get_ram_usage()

    def get_ram_before(self):
        return self.ram_before

    def get_ram_peak(self):
        return self.ram_peak

    def get_ram_after(self):
        return self.ram_after

    def get_ram_change(self):
        return self.ram_after - self.ram_before