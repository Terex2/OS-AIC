import subprocess
import os

class AutoCoder:
    def __init__(self, project_root="/home/ubuntu/open_source_ai_company"):
        self.project_root = project_root

    def execute_command(self, command: str) -> str:
        """ينفذ أوامر النظام في بيئة المشروع"""
        print(f"[AutoCoder] Executing: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                return f"Success: {result.stdout}"
            else:
                return f"Error (code {result.returncode}): {result.stderr}"
        except Exception as e:
            return f"Exception: {str(e)}"

    def write_code_to_file(self, file_path: str, code: str) -> str:
        """يكتب كوداً برمجياً إلى ملف محدد"""
        full_path = os.path.join(self.project_root, file_path)
        print(f"[AutoCoder] Writing code to: {full_path}")
        try:
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(code)
            return f"Successfully written to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def fix_code_with_llm(self, file_path: str, error_message: str, llm_callback):
        """يستخدم LLM لتحليل الخطأ وإصلاح الكود تلقائياً"""
        full_path = os.path.join(self.project_root, file_path)
        with open(full_path, 'r') as f:
            original_code = f.read()
        
        prompt = f"Fix the following code error:\n\nCode:\n{original_code}\n\nError:\n{error_message}\n\nProvide ONLY the fixed code without any explanation."
        fixed_code = llm_callback(prompt)
        
        return self.write_code_to_file(file_path, fixed_code)

if __name__ == "__main__":
    coder = AutoCoder()
    # تجربة تنفيذ أمر بسيط
    print(coder.execute_command("ls -R"))
    # تجربة كتابة ملف جديد
    print(coder.write_code_to_file("agents/test_agent.py", "print('Hello from Auto-Coder')"))
