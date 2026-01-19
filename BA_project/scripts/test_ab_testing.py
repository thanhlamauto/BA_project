#!/usr/bin/env python3
"""
Test A/B Testing Variant Assignment
Verifies that variant assignment produces proper 50/50 split
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ab_testing import assign_variant


def test_variant_assignment():
    """Test that variant assignment produces 50/50 split"""
    print("=" * 60)
    print("Testing A/B Variant Assignment")
    print("=" * 60)
    
    # Generate 1000 random user IDs
    import random
    import time
    
    user_ids = []
    for i in range(1000):
        timestamp = int(time.time() * 1000) + i
        random_num = random.randint(1000, 9999)
        user_id = f"user_{timestamp}_{random_num}"
        user_ids.append(user_id)
    
    # Assign variants
    assignments = {}
    for user_id in user_ids:
        variant = assign_variant(user_id)
        assignments[user_id] = variant
    
    # Count variants
    control_count = sum(1 for v in assignments.values() if v == 'control')
    treatment_count = sum(1 for v in assignments.values() if v == 'treatment')
    
    control_pct = (control_count / len(user_ids)) * 100
    treatment_pct = (treatment_count / len(user_ids)) * 100
    
    print(f"\n📊 Results (n={len(user_ids)}):")
    print(f"  Control:   {control_count:4d} users ({control_pct:5.2f}%)")
    print(f"  Treatment: {treatment_count:4d} users ({treatment_pct:5.2f}%)")
    
    # Check if distribution is within acceptable range (45-55%)
    print(f"\n🎯 Expected: 50% ± 5% (45-55% range)")
    
    if 45 <= control_pct <= 55 and 45 <= treatment_pct <= 55:
        print("✅ PASS: Variant distribution is balanced!")
        return True
    else:
        print("❌ FAIL: Variant distribution is imbalanced!")
        print("   Check assign_variant() logic in utils/ab_testing.py")
        return False


def test_consistency():
    """Test that same user always gets same variant"""
    print("\n" + "=" * 60)
    print("Testing Consistency (Sticky Sessions)")
    print("=" * 60)
    
    test_users = ["alice", "bob", "charlie", "user123", "test_user"]
    
    print("\n🔄 Testing same user gets same variant:")
    all_consistent = True
    
    for user_id in test_users:
        # Assign variant 10 times
        variants = [assign_variant(user_id) for _ in range(10)]
        
        # Check if all assignments are identical
        unique_variants = set(variants)
        is_consistent = len(unique_variants) == 1
        
        status = "✅" if is_consistent else "❌"
        print(f"  {status} {user_id:15s} → {variants[0]:10s} (checked 10x)")
        
        if not is_consistent:
            all_consistent = False
            print(f"      WARNING: Got different variants: {unique_variants}")
    
    if all_consistent:
        print("\n✅ PASS: All users get consistent variants!")
        return True
    else:
        print("\n❌ FAIL: Inconsistent variant assignment detected!")
        return False


def show_sample_assignments():
    """Show sample assignments for different user patterns"""
    import time
    import random
    
    print("\n" + "=" * 60)
    print("Sample Assignments by User Pattern")
    print("=" * 60)
    
    patterns = {
        "Sequential": [f"user{i}" for i in range(1, 11)],
        "Timestamps": [f"user_{int(time.time())}_{i}" for i in range(10)],
        "Random": [f"user_{random.randint(1000, 9999)}" for _ in range(10)],
        "Names": ["alice", "bob", "charlie", "david", "emma", 
                  "frank", "grace", "henry", "ivy", "jack"]
    }
    
    for pattern_name, users in patterns.items():
        control = sum(1 for u in users if assign_variant(u) == 'control')
        treatment = len(users) - control
        
        print(f"\n{pattern_name} Users (n={len(users)}):")
        print(f"  Control: {control}, Treatment: {treatment} ({treatment/len(users)*100:.0f}% treatment)")
        
        # Show first 3 assignments
        for user in users[:3]:
            variant = assign_variant(user)
            emoji = "🔵" if variant == "control" else "🟢"
            print(f"    {emoji} {user:20s} → {variant}")


def main():
    """Run all tests"""
    print("\n🧪 A/B Testing Verification Script\n")
    
    results = []
    
    # Test 1: Distribution
    results.append(("Variant Distribution (50/50)", test_variant_assignment()))
    
    # Test 2: Consistency  
    results.append(("Consistency (Sticky Sessions)", test_consistency()))
    
    # Show samples
    show_sample_assignments()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n{'='*60}")
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("="*60)
        print("\n🎉 A/B testing logic is working correctly!")
        print("\n💡 Tips for using A/B testing:")
        print("  1. Click 'Random' button in login modal to generate unique users")
        print("  2. Each unique user_id gets consistent variant assignment")
        print("  3. Population should split ~50/50 across many users")
        print("  4. Check dashboard to see real-time variant distribution")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total} passed)")
        print("="*60)
        print("\n⚠️  A/B testing logic needs attention!")
        print("   Check utils/ab_testing.py for issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
