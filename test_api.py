from main import get_all_users, get_categories, live_ai_analyze, AIAnalyzeRequest, list_feedbacks, get_analytics_summary

print("=== 1. Test Users ===")
users = get_all_users()
print("Loaded users count:", len(users))
for u in users:
    print(f"  - [{u['role']}] {u['name']} ({u['email']})")

print("\n=== 2. Test Categories ===")
cats = get_categories()
print("Loaded categories count:", len(cats))
for c in cats:
    print(f"  - {c['category_code']}: {c['category_name']}")

print("\n=== 3. Test AI Multi-label Analysis ===")
sample = "Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh"
ai_res = live_ai_analyze(AIAnalyzeRequest(title="Góp ý tiết học", content=sample))
print("Sample:", sample)
print("Is Multi-label:", ai_res["is_multi_label"])
for c in ai_res["predicted_categories"]:
    print(f"  * {c['category_name']} (Confidence: {c['confidence_score']}) - Matched: {c['matched_keywords']}")
print("Sentiment:", ai_res["sentiment"])

print("\n=== 4. Test List Feedbacks ===")
fbs = list_feedbacks()
print("Feedbacks count:", len(fbs))
for fb in fbs[:2]:
    print(f"  - #{fb['feedback_id']} [{fb['status']}] {fb['title']}")
    print(f"    Categories: {[c['category_name'] for c in fb['categories']]}")

print("\n=== 5. Test Analytics ===")
summary = get_analytics_summary()
print("Status counts:", summary["status_counts"])
print("Sentiment counts:", summary["sentiment_counts"])
print("AI Accuracy:", summary["ai_accuracy"])

print("\nAll integration tests PASSED!")
