"""Safe, deterministic decimal arithmetic checks for authored exercises."""
import ast
from decimal import Decimal, InvalidOperation

OPS = {ast.Add:lambda a,b:a+b, ast.Sub:lambda a,b:a-b,
       ast.Mult:lambda a,b:a*b, ast.Div:lambda a,b:a/b}

def evaluate(expression):
    def walk(node):
        if isinstance(node,ast.Expression): return walk(node.body)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            return Decimal(str(node.value))
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=walk(node.operand)
            return value if isinstance(node.op,ast.UAdd) else -value
        if isinstance(node,ast.BinOp) and type(node.op) in OPS:
            left,right=walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Div) and right==0: raise ValueError("Division by zero")
            return OPS[type(node.op)](left,right)
        raise ValueError("Unsupported arithmetic expression")
    try: return walk(ast.parse(expression,mode="eval"))
    except (SyntaxError,ArithmeticError,InvalidOperation) as exc:
        raise ValueError("Invalid arithmetic expression") from exc

def audit(project):
    questions={k:v for chapter in project["chapters"] for k,v in chapter["answers"].items()}
    checks=project.get("math_checks",[])
    if not isinstance(checks,list): raise ValueError("math_checks must be a list")
    seen=set()
    for case in checks:
        key=case["problem_id"]
        if key in seen or key not in questions: raise ValueError("Duplicate or unknown math check ID")
        seen.add(key)
        computed=evaluate(case["expression"])
        if computed != Decimal(str(case["expected"])):
            raise ValueError("Arithmetic verification failed for "+key)
        if questions[key].strip()!=str(case["answer_text"]):
            raise ValueError("Answer mapping changed for "+key)
    return {"checked":len(checks),"total":len(questions),"unchecked":len(questions)-len(checks)}
