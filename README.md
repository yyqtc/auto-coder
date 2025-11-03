# Python 执行脚本的多种方法

这个示例演示了在 Python 中执行脚本的几种常用方法。

## 方法对比

### 1. subprocess.run() ⭐ 推荐
- **优点**: 安全、灵活、可以捕获输出、跨平台
- **适用场景**: 执行独立的 Python 脚本，需要获取输出结果

```python
import subprocess
result = subprocess.run(['python', 'script.py'], capture_output=True, text=True)
print(result.stdout)
```

### 2. subprocess.Popen()
- **优点**: 适合异步执行、交互式场景
- **适用场景**: 需要长时间运行的脚本、需要实时输出

```python
process = subprocess.Popen(['python', 'script.py'], stdout=subprocess.PIPE)
stdout, stderr = process.communicate()
```

### 3. os.system()
- **优点**: 简单直接
- **缺点**: 安全性差、无法捕获输出、平台相关
- **适用场景**: 简单的系统命令（不推荐用于生产环境）

```python
os.system('python script.py')
```

### 4. 动态导入模块
- **优点**: 可以在当前命名空间中使用脚本中的函数和变量
- **适用场景**: 需要调用脚本中的函数或访问变量

```python
import importlib.util
spec = importlib.util.spec_from_file_location("module", "script.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

### 5. exec()
- **优点**: 可以访问脚本的所有内容
- **缺点**: 安全性极差，容易导致代码注入攻击
- **适用场景**: 信任的代码（一般不推荐）

```python
with open('script.py', 'r') as f:
    code = f.read()
exec(code)
```

## 使用建议

1. **生产环境**: 优先使用 `subprocess.run()` 或 `subprocess.Popen()`
2. **需要调用函数**: 使用动态导入 (`importlib`)
3. **简单测试**: 可以使用 `os.system()`，但不推荐
4. **避免使用**: `exec()` 和 `eval()`，除非完全信任代码来源

## 运行示例

```bash
python example_execute_script.py
```

