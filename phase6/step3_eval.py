import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

# ==========================================
# 1. 定义测试集（黄金测试集 Golden Dataset）
# 真实企业里这可能有几百条，这里只写 3 条
# ==========================================
TEST_DATASET = [
    {"input": "1+1等于几？", "expected": "2"},
    {"input": "中国的首都是哪里？", "expected": "北京"},
    {"input": "请把'apple'翻译成中文。", "expected": "苹果"},
]


# ==========================================
# 2. 定义评估器（Evaluator）
# 这里用最简单的“包含匹配”规则，真实项目可以用 LLM 当裁判
# ==========================================
def evaluate_answer(actual: str, expected: str) -> bool:
    # 只要模型回答里包含期望答案，就算对
    return expected in actual


# ==========================================
# 3. 跑评估流程
# ==========================================
def run_eval():
    print("===== 开始自动化评估 =====")
    passed = 0
    total = len(TEST_DATASET)

    for i, case in enumerate(TEST_DATASET, 1):
        print(f"\n[Test {i}] 输入: {case['input']}")

        # 调模型
        res = llm.invoke([HumanMessage(content=case["input"])])
        actual = res.content
        print(f"  模型输出: {actual}")
        print(f"  期望输出: {case['expected']}")

        # 打分
        is_correct = evaluate_answer(actual, case["expected"])

        if is_correct:
            passed += 1
            print("  评估结果: ✅ PASS")
        else:
            print("  评估结果: ❌ FAIL")

    # 总结
    print("\n===== 评估总结 =====")
    print(f"通过率: {passed}/{total} ({(passed / total) * 100:.1f}%)")
    print(f"准确率: {passed / total:.2f}")


if __name__ == "__main__":
    run_eval()