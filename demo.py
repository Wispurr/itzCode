import os
import sys
from src.lexer import Lexer
from src.parser import Parser
from src.emitter import Emitter

def compile_file(filename):
    """
    讀取 examples/{filename}，編譯並輸出到 results/{filename}.cpp
    """
    input_path = f"./examples/{filename}"
    
    # 建立 results 資料夾 (如果不存在)
    output_dir = "./results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 決定輸出檔名: hello.itz -> results/hello.cpp
    base_name = os.path.splitext(filename)[0]
    output_path = f"{output_dir}/{base_name}.cpp"

    print(f"Compiling: {filename} -> {output_path}")

    # 1. 讀取檔案
    try:
        with open(input_path, "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        return False

    # 2. 初始化編譯器模組
    # 注意：這裡將 output_path 傳入 Emitter，而不是寫死的 "output.c"
    lexer = Lexer(source_code)
    emitter = Emitter(output_path)
    parser = Parser(lexer, emitter)

    # 3. 執行編譯
    try:
        parser.program()
        emitter.writeFile()
        print("  [Success]")
        return True
    except Exception as e:
        print(f"  [Error]: {e}")
        return False

def run_all_demos():
    """
    批次編譯 ./examples 資料夾下所有的 .itz 檔案
    """
    print("=== Batch Compiling All Examples ===")
    if not os.path.exists("./examples"):
        print("Error: ./examples directory not found.")
        return

    files = [f for f in os.listdir("./examples") if f.endswith(".itz")]
    if not files:
        print("No .itz files found in ./examples")
        return

    success_count = 0
    for file in files:
        if compile_file(file):
            success_count += 1
    
    print("-" * 30)
    print(f"Batch completed: {success_count}/{len(files)} files compiled successfully.")

def main():
    print("--- itzCode Tiny Compiler Driver ---")

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Compile one file:  python demo.py <filename.itz>")
        print("  Compile all files: python demo.py --all")
        return

    arg = sys.argv[1]

    if arg == "--all":
        run_all_demos()
    else:
        # 編譯單一檔案
        compile_file(arg)

if __name__ == "__main__":
    main()