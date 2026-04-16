import json
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from maxcut_ecommerce.baseline import brute_force_max_cut
from maxcut_ecommerce.instance import EcommerceInstance, Relation, load_instance


class BaselineTests(unittest.TestCase):
    def test_bruteforce_finds_optimum_for_small_graph(self):
        instance = EcommerceInstance(
            products=("A", "B", "C"),
            relations=(
                Relation("A", "B", 1.0, ""),
                Relation("A", "C", 2.0, ""),
                Relation("B", "C", 3.0, ""),
            ),
        )

        best_weight, side_a, side_b = brute_force_max_cut(instance)

        self.assertEqual(best_weight, 5.0)
        self.assertEqual(side_a | side_b, set(instance.products))
        self.assertEqual(side_a & side_b, set())

        recomputed = 0.0
        for relation in instance.relations:
            if (relation.product_a in side_a) != (relation.product_b in side_a):
                recomputed += relation.weight
        self.assertEqual(recomputed, best_weight)

    def test_load_instance_raises_value_error_for_unknown_product(self):
        invalid = {
            "products": ["A", "B"],
            "relations": [
                {"product_a": "A", "product_b": "X", "weight": 1.0}
            ],
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            tmp.write(json.dumps(invalid))
            tmp_path = tmp.name

        try:
            with self.assertRaises(ValueError):
                load_instance(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
