# src/emitter.py
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.header = ""
        self.functions = "" # [新增] 存放函式定義
        self.main = ""      # [新增] 存放主程式邏輯
        self.capture_mode = "main" # 當前寫入模式: "main" 或 "functions"

    def setCaptureMode(self, mode):
        """切換寫入模式: 'main' 或 'functions'"""
        self.capture_mode = mode

    def emit(self, code):
        if self.capture_mode == "functions":
            self.functions += code
        else:
            self.main += code

    def emitLine(self, code):
        if self.capture_mode == "functions":
            self.functions += code + '\n'
        else:
            self.main += code + '\n'

    def headerLine(self, code):
        self.header += code + '\n'

    def writeFile(self):
        with open(self.fullPath, 'w') as writeFile:
            # 組合順序: Header -> Functions -> Main
            writeFile.write(self.header)
            writeFile.write("\n// --- Functions ---\n")
            writeFile.write(self.functions)
            writeFile.write("\n// --- Main Program ---\n")
            writeFile.write(self.main)